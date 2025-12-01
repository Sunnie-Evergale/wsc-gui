# recompiler.py
# WSC Recompiler - Convert decompiled text back to WSC binary format

import re
import struct
from pathlib import Path
from typing import List, Tuple, Optional

# Import patterns and utilities from decompiler
from decompiler import (
    re_japanese_name,
    SPEAKER_BYTE,
    decode_try,
    sanitize
)


class WSCEntry:
    """Represents a single WSC entry with its metadata."""

    def __init__(self, start_offset: int, end_offset: int, content: str, is_speaker: bool = False):
        self.start_offset = start_offset
        self.end_offset = end_offset
        self.content = content
        self.is_speaker = is_speaker
        self.binary_data = None
        self.warnings = []
        self.errors = []
        self.original_length = end_offset - start_offset

    def __repr__(self):
        return f"WSCEntry({self.start_offset:08X}:{self.end_offset:08X}, speaker={self.is_speaker}, content='{self.content}')"


class ValidationResult:
    """Result of WSC content validation."""

    def __init__(self):
        self.is_valid = False
        self.errors = []
        self.warnings = []
        self.suggestions = []
        self.needs_recalculation = False

    def add_error(self, error: str):
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False

    def add_warning(self, warning: str):
        """Add a warning message."""
        self.warnings.append(warning)

    def add_suggestion(self, suggestion: str):
        """Add a repair suggestion."""
        self.suggestions.append(suggestion)


def parse_github_format(text: str) -> Tuple[List[WSCEntry], ValidationResult]:
    """
    Parse GitHub-style WSC format into WSCEntry objects.

    Format:
    <start_offset:end_offset>
    content
    <next_start_offset:next_end_offset>
    next_content
    """
    entries = []
    result = ValidationResult()

    lines = text.strip().split('\n')
    i = 0

    while i < len(lines):
        line = lines[i].strip()

        # Skip empty lines
        if not line:
            i += 1
            continue

        # Parse offset line
        if line.startswith('<') and ':' in line and line.endswith('>'):
            try:
                # Extract start and end offsets
                offset_content = line[1:-1]  # Remove < and >
                start_hex, end_hex = offset_content.split(':')

                start_offset = int(start_hex, 16)
                end_offset = int(end_hex, 16)

                # Get content (next line, or empty if end of file)
                content = ""
                if i + 1 < len(lines):
                    content = lines[i + 1].strip()

                # Detect if this is a speaker name (starts with .)
                is_speaker = content.startswith('.') and len(content) > 1

                # Remove speaker dot for processing
                clean_content = content[1:] if is_speaker else content

                # Restore literal \n to actual newlines
                clean_content = clean_content.replace('\\n', '\n')

                entry = WSCEntry(start_offset, end_offset, clean_content, is_speaker)
                entries.append(entry)

                i += 2  # Skip content line

            except ValueError as e:
                result.add_error(f"Invalid offset format on line {i+1}: {line}")
                result.add_suggestion("Ensure format is <XXXXXXXX:XXXXXXXX>")
                i += 1
        else:
            # Invalid format line
            result.add_error(f"Expected offset format on line {i+1}, got: {line[:50]}...")
            i += 1

    # Validate the parsed entries
    if entries:
        result.is_valid = len(result.errors) == 0

        # Check for offset ordering
        for i in range(1, len(entries)):
            if entries[i].start_offset <= entries[i-1].start_offset:
                result.add_warning(f"Offset ordering issue: entry {i} starts before entry {i-1}")
                result.needs_recalculation = True

    else:
        result.add_error("No valid WSC entries found")
        result.add_suggestion("Ensure file contains <start:end> offset lines followed by content")

    return entries, result


def content_to_binary(content: str, is_speaker: bool = False) -> bytes:
    """
    Convert text content back to WSC binary format.
    """
    if is_speaker:
        # This was originally marked as speaker by decompiler, so convert back with double 0x0F
        if content.strip():  # Not empty
            try:
                encoded = content.strip().encode('cp932')
                return b'\x0F\x0F' + encoded + b'\x00'
            except UnicodeEncodeError:
                # Fallback encoding - handle problematic content
                try:
                    # Try different encodings
                    for encoding in ['cp932', 'shift_jis', 'latin-1']:
                        try:
                            encoded = content.strip().encode(encoding)
                            return b'\x0F\x0F' + encoded + b'\x00'
                        except:
                            continue
                    # Last resort - replace problematic characters
                    encoded = content.strip().encode('latin-1', errors='replace')
                    return b'\x0F\x0F' + encoded + b'\x00'
                except Exception:
                    # Ultimate fallback - empty content
                    return b'\x00'
        else:
            # Empty speaker - just return null terminator
            return b'\x00'
    else:
        # Regular content (resources, audio, commands, narration)
        # For narration that starts with 0x0F, we need to detect it
        if content.strip():
            # Check if this looks like narration (Japanese text without obvious resource pattern)
            has_japanese = bool(re_japanese_name.search(content))
            has_resource_pattern = bool(re.match(r'^(DAY|BG|ST|HOS|SE|BGM|%).*', content))

            # If it has Japanese characters but doesn't look like a resource/command, treat as narration
            if has_japanese and not has_resource_pattern:
                # This is likely narration that originally had single 0x0F
                try:
                    encoded = content.encode('cp932')
                    return b'\x0F' + encoded + b'\x00'
                except UnicodeEncodeError:
                    # Fallback encoding for problematic content
                    try:
                        for encoding in ['cp932', 'shift_jis', 'latin-1']:
                            try:
                                encoded = content.encode(encoding)
                                return b'\x0F' + encoded + b'\x00'
                            except:
                                continue
                        encoded = content.encode('latin-1', errors='replace')
                        return b'\x0F' + encoded + b'\x00'
                    except Exception:
                        return b'\x00'
            else:
                # Regular content (resources, audio, commands)
                try:
                    return content.encode('cp932') + b'\x00'
                except UnicodeEncodeError:
                    # Fallback encoding for problematic content
                    try:
                        for encoding in ['cp932', 'shift_jis', 'latin-1']:
                            try:
                                encoded = content.encode(encoding)
                                return encoded + b'\x00'
                            except:
                                continue
                        encoded = content.encode('latin-1', errors='replace')
                        return encoded + b'\x00'
                    except Exception:
                        return b'\x00'
        else:
            # Empty content
            return b'\x00'


def calculate_new_offsets(entries: List[WSCEntry]) -> None:
    """
    Recalculate offsets for all entries based on their binary data.
    """
    current_offset = 0

    for entry in entries:
        # Generate binary data
        entry.binary_data = content_to_binary(entry.content, entry.is_speaker)

        # Update offsets
        entry.start_offset = current_offset
        entry.end_offset = current_offset + len(entry.binary_data) - 1  # -1 because we want inclusive end

        # Move to next position
        current_offset += len(entry.binary_data)


def preserve_original_offsets(entries: List[WSCEntry]) -> bool:
    """
    Try to preserve original offsets. Returns True if successful, False if recalculation needed.
    """
    for entry in entries:
        # Generate binary data
        entry.binary_data = content_to_binary(entry.content, entry.is_speaker)

        # Check if length matches original
        expected_length = entry.original_length + 1  # +1 for null terminator
        actual_length = len(entry.binary_data)

        if actual_length != expected_length:
            return False  # Need recalculation

    return True  # All entries match original lengths


def reconstruct_wsc_binary(entries: List[WSCEntry], preserve_offsets: bool = True) -> bytes:
    """
    Reconstruct complete WSC binary file from entries.
    """
    if preserve_offsets:
        # Try to preserve original offsets
        if not preserve_original_offsets(entries):
            # Fall back to recalculation
            calculate_new_offsets(entries)
    else:
        # Always recalculate
        calculate_new_offsets(entries)

    # Combine all binary data
    result = b''
    for entry in entries:
        result += entry.binary_data

    return result


def validate_wsc_entries(entries: List[WSCEntry]) -> ValidationResult:
    """
    Validate WSC entries for potential issues.
    """
    result = ValidationResult()

    for i, entry in enumerate(entries):
        # Check content for encoding issues
        try:
            entry.content.encode('cp932')
        except UnicodeEncodeError:
            result.add_warning(f"Entry {i+1} contains characters not compatible with CP932")
            result.add_suggestion(f"Consider modifying entry {i+1}: {entry.content[:50]}...")

        # Check speaker name format
        if entry.is_speaker:
            if not re_japanese_name.match(entry.content.strip()) or len(entry.content.strip()) > 8:
                result.add_warning(f"Entry {i+1} speaker name format may be unusual: {entry.content}")
                result.add_suggestion("Speaker names should be 1-8 Japanese characters")

        # Check for empty content
        if not entry.content.strip():
            result.add_warning(f"Entry {i+1} has empty content")

    # Check for potential conflicts
    for i in range(1, len(entries)):
        if entries[i].start_offset <= entries[i-1].end_offset:
            result.add_error(f"Offset conflict between entries {i} and {i+1}")
            result.needs_recalculation = True

    result.is_valid = len(result.errors) == 0
    return result


def recompile_wsc_file(input_txt_path: str, output_wsc_path: str,
                      preserve_offsets: bool = True) -> Tuple[bool, ValidationResult]:
    """
    Recompile a WSC file from decompiled text.

    Args:
        input_txt_path: Path to the decompiled .txt file
        output_wsc_path: Path for the output .WSC file
        preserve_offsets: Whether to try preserving original offsets

    Returns:
        Tuple of (success, ValidationResult)
    """
    # Read input file
    try:
        with open(input_txt_path, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except Exception as e:
        result = ValidationResult()
        result.add_error(f"Failed to read input file: {e}")
        return False, result

    # Parse GitHub format
    entries, parse_result = parse_github_format(text_content)

    if not parse_result.is_valid:
        return False, parse_result

    # Validate entries
    validation_result = validate_wsc_entries(entries)
    if not validation_result.is_valid:
        return False, validation_result

    # Combine results
    final_result = ValidationResult()
    final_result.errors.extend(parse_result.errors)
    final_result.warnings.extend(parse_result.warnings)
    final_result.warnings.extend(validation_result.warnings)
    final_result.suggestions.extend(parse_result.suggestions)
    final_result.suggestions.extend(validation_result.suggestions)
    final_result.needs_recalculation = validation_result.needs_recalculation

    # Reconstruct binary
    try:
        binary_data = reconstruct_wsc_binary(entries, preserve_offsets)

        # Write output file
        output_path = Path(output_wsc_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_wsc_path, 'wb') as f:
            f.write(binary_data)

        final_result.is_valid = True

        # Add success info
        final_result.add_suggestion(f"Successfully recompiled {len(entries)} entries")
        if preserve_offsets and not preserve_original_offsets(entries):
            final_result.add_warning("Offsets were recalculated due to content changes")

        return True, final_result

    except Exception as e:
        final_result.add_error(f"Failed to reconstruct WSC binary: {e}")
        return False, final_result


def suggest_repair(error_type: str, content: str = "") -> str:
    """
    Generate automated repair suggestions for common issues.
    """
    repairs = {
        'invalid_encoding': f"Convert '{content}' to CP932 compatible text",
        'missing_offset': "Generate new offset structure using the recompiler",
        'speaker_format': f"Convert '{content}' to proper .Name format or remove speaker prefix",
        'offset_conflict': "Enable offset recalculation in recompiler options",
        'empty_content': "Add meaningful content or remove this entry",
        'invalid_format': "Ensure proper <start:end> offset format on each entry"
    }

    return repairs.get(error_type, "Manual review required - check entry format and content")