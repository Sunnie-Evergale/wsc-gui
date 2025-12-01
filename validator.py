# validator.py
# WSC content validation and error detection system

import re
from typing import List, Dict, Any, Tuple
from recompiler import WSCEntry, ValidationResult, suggest_repair


class WSCValidator:
    """Comprehensive WSC content validator."""

    def __init__(self):
        self.encoding_patterns = {
            'cp932': r'[\x00-\x7F\x81-\x9F\xE0-\xEF\xFA-\xFC]',
            'ascii': r'[\x00-\x7F]',
            'japanese': r'[\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]'
        }

        self.wsc_patterns = {
            'resource_id': re.compile(r'^(DAY|BG|ST|HOS)_[0-9A-Za-z_]+$', re.I),
            'audio_file': re.compile(r'^(SE|BGM)_[0-9A-Za-z_.-]+$', re.I),
            'engine_command': re.compile(r'^%[A-Za-z0-9_]+%?$'),
            'speaker_name': re.compile(r'^[\u3040-\u30FF\u4E00-\u9FFF]{1,8}$'),
            'offset_line': re.compile(r'^<([0-9A-Fa-f]{8}):([0-9A-Fa-f]{8})>$')
        }

    def validate_format_structure(self, text: str) -> ValidationResult:
        """Validate the overall GitHub-style format structure."""
        result = ValidationResult()

        lines = text.strip().split('\n')
        i = 0
        entry_count = 0

        while i < len(lines):
            line = lines[i].strip()

            if not line:
                i += 1
                continue

            # Check for offset line
            if not self.wsc_patterns['offset_line'].match(line):
                result.add_error(f"Line {i+1}: Invalid offset format '{line[:30]}...'")
                result.add_suggestion("Use format <XXXXXXXX:XXXXXXXX>")
                i += 1
                continue

            # Check for content line
            if i + 1 >= len(lines):
                result.add_error(f"Line {i+1}: Missing content for offset {line}")
                result.add_suggestion("Add content line after each offset")
                break

            content = lines[i + 1].strip()
            entry_count += 1
            i += 2

        if entry_count == 0:
            result.add_error("No valid WSC entries found")
            result.add_suggestion("Ensure file contains proper offset and content lines")

        result.is_valid = len(result.errors) == 0
        return result

    def validate_encoding_compatibility(self, content: str) -> ValidationResult:
        """Check if content can be encoded to CP932."""
        result = ValidationResult()

        try:
            content.encode('cp932')
        except UnicodeEncodeError as e:
            result.add_error(f"Encoding error: {e}")
            result.add_suggestion("Replace problematic characters with CP932-compatible alternatives")

        return result

    def validate_speaker_detection(self, content: str, is_speaker: bool) -> ValidationResult:
        """Validate speaker name detection and format."""
        result = ValidationResult()

        if is_speaker:
            clean_name = content.strip()

            if not clean_name:
                result.add_warning("Empty speaker name detected")
                result.add_suggestion("Provide a valid speaker name or remove speaker prefix")

            elif not self.wsc_patterns['speaker_name'].match(clean_name):
                result.add_warning(f"Unusual speaker name format: '{clean_name}'")
                result.add_suggestion("Speaker names should be 1-8 Japanese characters")

                # Check if it might be narration instead
                if len(clean_name) > 8 or re.search(r'[^\u3040-\u309F\u30A0-\u30FF\u4E00-\u9FFF]', clean_name):
                    result.add_suggestion("Consider removing speaker prefix (.) if this is narration")

        return result

    def validate_content_categories(self, content: str) -> ValidationResult:
        """Validate content against known WSC categories."""
        result = ValidationResult()

        # Check for known patterns
        if self.wsc_patterns['resource_id'].match(content):
            # Resource ID - check format
            pass

        elif self.wsc_patterns['audio_file'].match(content):
            # Audio file - check format
            if not content.lower().endswith(('.ogg', '.wav', '.mp3')) and not content.startswith('BGM_'):
                result.add_warning(f"Audio file may have unusual extension: {content}")

        elif self.wsc_patterns['engine_command'].match(content):
            # Engine command - check format
            pass

        elif content.startswith('.') and len(content) > 1:
            # Speaker name - handled by validate_speaker_detection
            pass

        elif content:
            # Regular content - check if it might be Japanese text
            if re.search(self.encoding_patterns['japanese'], content):
                # Japanese text - this is fine
                pass
            else:
                # Non-Japanese, non-standard content
                if len(content) < 3:
                    result.add_warning(f"Short content may be filtered: '{content}'")
                    result.add_suggestion("Consider removing or expanding this content")

        return result

    def validate_offset_consistency(self, entries: List[WSCEntry]) -> ValidationResult:
        """Validate offset consistency and detect conflicts."""
        result = ValidationResult()

        if not entries:
            result.add_error("No entries to validate")
            return result

        # Check for proper ordering
        for i in range(1, len(entries)):
            if entries[i].start_offset <= entries[i-1].start_offset:
                result.add_error(f"Offset ordering issue: entry {i+1} ({entries[i].start_offset:08X}) starts before entry {i} ({entries[i-1].start_offset:08X})")
                result.add_suggestion("Enable offset recalculation or fix offset values")

            if entries[i].start_offset <= entries[i-1].end_offset:
                result.add_error(f"Offset overlap: entry {i} overlaps with entry {i+1}")
                result.add_suggestion("Recalculate all offsets to resolve conflicts")

        # Check for gaps
        for i in range(1, len(entries)):
            gap = entries[i].start_offset - entries[i-1].end_offset - 1
            if gap > 0:
                result.add_warning(f"Gap detected: {gap} bytes between entries {i} and {i+1}")
                if gap > 100:
                    result.add_suggestion("Large gap may indicate missing data")

        result.is_valid = len(result.errors) == 0
        return result

    def validate_binary_consistency(self, entries: List[WSCEntry]) -> ValidationResult:
        """Validate that entries match their declared lengths."""
        result = ValidationResult()

        for i, entry in enumerate(entries):
            if entry.binary_data is None:
                # Generate binary data for validation
                from recompiler import content_to_binary
                entry.binary_data = content_to_binary(entry.content, entry.is_speaker)

            actual_length = len(entry.binary_data)
            expected_length = entry.original_length + 1  # +1 for null terminator

            if actual_length != expected_length:
                result.add_warning(f"Entry {i+1}: Length changed from {expected_length} to {actual_length} bytes")
                result.add_suggestion(f"Content: '{entry.content[:30]}...' - Consider enabling offset recalculation")
                result.needs_recalculation = True

        result.is_valid = len(result.errors) == 0
        return result

    def comprehensive_validation(self, text: str, entries: List[WSCEntry] = None) -> ValidationResult:
        """Perform comprehensive validation of WSC content."""
        final_result = ValidationResult()

        # Format structure validation
        format_result = self.validate_format_structure(text)
        final_result.errors.extend(format_result.errors)
        final_result.warnings.extend(format_result.warnings)

        if entries:
            # Individual entry validation
            for i, entry in enumerate(entries):
                # Encoding compatibility
                encoding_result = self.validate_encoding_compatibility(entry.content)
                if encoding_result.errors:
                    final_result.errors.extend([f"Entry {i+1}: {err}" for err in encoding_result.errors])
                if encoding_result.warnings:
                    final_result.warnings.extend([f"Entry {i+1}: {warn}" for warn in encoding_result.warnings])

                # Speaker detection
                speaker_result = self.validate_speaker_detection(entry.content, entry.is_speaker)
                if speaker_result.errors:
                    final_result.errors.extend([f"Entry {i+1}: {err}" for err in speaker_result.errors])
                if speaker_result.warnings:
                    final_result.warnings.extend([f"Entry {i+1}: {warn}" for warn in speaker_result.warnings])

                # Content categories
                content_result = self.validate_content_categories(entry.content)
                if content_result.errors:
                    final_result.errors.extend([f"Entry {i+1}: {err}" for err in content_result.errors])
                if content_result.warnings:
                    final_result.warnings.extend([f"Entry {i+1}: {warn}" for warn in content_result.warnings])

            # Offset consistency
            offset_result = self.validate_offset_consistency(entries)
            final_result.errors.extend(offset_result.errors)
            final_result.warnings.extend(offset_result.warnings)
            if offset_result.needs_recalculation:
                final_result.needs_recalculation = True

            # Binary consistency
            binary_result = self.validate_binary_consistency(entries)
            final_result.warnings.extend(binary_result.warnings)
            if binary_result.needs_recalculation:
                final_result.needs_recalculation = True

        final_result.is_valid = len(final_result.errors) == 0
        return final_result

    def generate_repair_suggestions(self, validation_result: ValidationResult) -> List[Dict[str, Any]]:
        """Generate structured repair suggestions from validation result."""
        suggestions = []

        for error in validation_result.errors:
            suggestions.append({
                'type': 'error',
                'message': error,
                'repair': suggest_repair('invalid_format'),
                'auto_fixable': False
            })

        for warning in validation_result.warnings:
            suggestions.append({
                'type': 'warning',
                'message': warning,
                'repair': suggest_repair('invalid_format', warning),
                'auto_fixable': False
            })

        for suggestion in validation_result.suggestions:
            suggestions.append({
                'type': 'suggestion',
                'message': suggestion,
                'repair': suggestion,
                'auto_fixable': False
            })

        return suggestions

    def quick_validate(self, text: str) -> Dict[str, Any]:
        """Quick validation for real-time editor feedback."""
        result = {
            'valid': True,
            'errors': [],
            'warnings': [],
            'line_issues': []
        }

        lines = text.split('\n')

        for i, line in enumerate(lines):
            line_stripped = line.strip()

            if not line_stripped:
                continue

            # Check offset line
            if i % 2 == 0:  # Even lines should be offsets
                if not self.wsc_patterns['offset_line'].match(line_stripped):
                    result['valid'] = False
                    result['errors'].append({
                        'line': i + 1,
                        'message': f"Invalid offset format: {line_stripped[:30]}...",
                        'suggestion': "Use format <XXXXXXXX:XXXXXXXX>"
                    })

        # Quick content validation
        if result['valid'] and lines:
            # Check if we have content lines
            content_lines = [lines[i].strip() for i in range(1, len(lines), 2)]
            for i, content in enumerate(content_lines):
                if content:
                    try:
                        content.encode('cp932')
                    except UnicodeEncodeError:
                        result['warnings'].append({
                            'line': (i + 1) * 2,
                            'message': f"Encoding issues in: {content[:20]}...",
                            'suggestion': "Replace with CP932-compatible text"
                        })

        return result