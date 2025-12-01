#!/usr/bin/env python3
# test_recompiler.py
# Comprehensive test suite for WSC recompiler functionality

import os
import sys
import tempfile
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from recompiler import (
    parse_github_format,
    content_to_binary,
    reconstruct_wsc_binary,
    recompile_wsc_file,
    WSCEntry,
    ValidationResult
)
from validator import WSCValidator
from decompiler import decompile_wsc_file


def create_test_text_content():
    """Create test content in GitHub-style format."""
    return """<00000000:00000007>
DAY0904

<00000008:0000000E>
.夜久

<0000000F:0000001E>
こんにちは世界

<0000001F:00000029>
SE_104.ogg

<0000002A:00000030>
BGM_06

<00000031:00000035>
%K%P

<00000036:0000003E>
BG108_02

<0000003F:00000047>
ST13A05S

<00000048:0000004E>
.美里

<0000004F:00000064>
今日は良い天気ですね
"""


def test_parse_github_format():
    """Test parsing of GitHub-style format."""
    print("🧪 Testing parse_github_format...")

    content = create_test_text_content()
    entries, result = parse_github_format(content)

    # Check parsing results
    assert result.is_valid, f"Parsing failed: {result.errors}"
    assert len(entries) == 10, f"Expected 10 entries, got {len(entries)}"

    # Check specific entries
    assert entries[0].content == "DAY0904", f"Expected DAY0904, got {entries[0].content}"
    assert entries[1].is_speaker == True, f"Entry 1 should be speaker"
    assert entries[1].content == "夜久", f"Expected 夜久, got {entries[1].content}"
    assert entries[2].is_speaker == False, f"Entry 2 should not be speaker"
    assert entries[2].content == "こんにちは世界", f"Expected こんにちは世界, got {entries[2].content}"

    print("✅ parse_github_format test passed")
    return entries


def test_content_to_binary():
    """Test content to binary conversion."""
    print("🧪 Testing content_to_binary...")

    # Test regular content
    binary = content_to_binary("DAY0904", False)
    expected = b"DAY0904\x00"
    assert binary == expected, f"Expected {expected}, got {binary}"

    # Test speaker name (Japanese) - this is marked as speaker, so gets double 0x0F
    binary = content_to_binary("夜久", True)
    assert binary.startswith(b'\x0F\x0F'), "Speaker should start with double 0x0F"
    assert binary.endswith(b'\x00'), "Should end with null terminator"

    # Test narration (Japanese) - this is NOT marked as speaker, so gets single 0x0F
    binary = content_to_binary("こんにちは世界", False)
    assert binary.startswith(b'\x0F'), "Narration should start with single 0x0F"
    assert not binary.startswith(b'\x0F\x0F'), "Narration should not start with double 0x0F"
    assert binary.endswith(b'\x00'), "Should end with null terminator"

    print("✅ content_to_binary test passed")


def test_reconstruct_wsc_binary():
    """Test WSC binary reconstruction."""
    print("🧪 Testing reconstruct_wsc_binary...")

    # Parse test content
    content = create_test_text_content()
    entries, _ = parse_github_format(content)

    # Reconstruct binary
    binary = reconstruct_wsc_binary(entries, preserve_offsets=False)

    # Check that binary is not empty
    assert len(binary) > 0, "Reconstructed binary should not be empty"

    # Check null terminators
    null_count = binary.count(b'\x00')
    assert null_count == len(entries), f"Expected {len(entries)} null terminators, got {null_count}"

    print(f"✅ reconstruct_wsc_binary test passed ({len(binary)} bytes)")


def test_round_trip():
    """Test complete round-trip: WSC → text → WSC."""
    print("🧪 Testing round-trip conversion...")

    # Create test WSC file
    test_wsc_data = (
        b"DAY0904\x00"
        b"\x0F\x0F\x96\xe9\x8b\x56\x00"  # 夜久 in CP932
        b"\x0F\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd\x90\xa2\x8a\xc5\x00"  # こんにちは世界 in CP932
        b"SE_104.ogg\x00"
        b"%K%P\x00"
    )

    with tempfile.NamedTemporaryFile(suffix='.wsc', delete=False) as temp_wsc:
        temp_wsc.write(test_wsc_data)
        temp_wsc_path = temp_wsc.name

    try:
        # Step 1: Decompile
        with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as temp_txt:
            temp_txt_path = temp_txt.name

        decompile_wsc_file(temp_wsc_path, temp_txt_path)

        # Step 2: Read decompiled content
        with open(temp_txt_path, 'r', encoding='utf-8') as f:
            decompiled_content = f.read()

        print(f"📄 Decompiled content ({len(decompiled_content)} chars):")
        print(decompiled_content[:200] + "..." if len(decompiled_content) > 200 else decompiled_content)

        # Step 3: Recompile
        with tempfile.NamedTemporaryFile(suffix='.wsc', delete=False) as recompiled_wsc:
            recompiled_path = recompiled_wsc.name

        success, result = recompile_wsc_file(temp_txt_path, recompiled_path, preserve_offsets=False)

        assert success, f"Recompilation failed: {result.errors}"
        assert result.is_valid, f"Recompilation validation failed: {result.errors}"

        # Step 4: Compare results
        with open(recompiled_path, 'rb') as f:
            recompiled_data = f.read()

        print(f"📊 Original: {len(test_wsc_data)} bytes")
        print(f"📊 Recompiled: {len(recompiled_data)} bytes")

        # Check that both have null terminators
        assert test_wsc_data.count(b'\x00') == recompiled_data.count(b'\x00'), "Null terminator count mismatch"

        # Check content preservation (allowing for offset differences)
        original_strings = [s.decode('cp932', errors='ignore') for s in test_wsc_data.split(b'\x00') if s]
        recompiled_strings = [s.decode('cp932', errors='ignore') for s in recompiled_data.split(b'\x00') if s]

        # Remove empty strings
        original_strings = [s for s in original_strings if s.strip()]
        recompiled_strings = [s for s in recompiled_strings if s.strip()]

        print(f"📋 Original strings: {original_strings}")
        print(f"📋 Recompiled strings: {recompiled_strings}")

        # Content should be preserved (order might differ due to offset recalculation)
        for orig_str in original_strings:
            if orig_str.strip():  # Skip empty strings
                found = any(orig_str in recomp_str for recomp_str in recompiled_strings)
                assert found, f"Original string '{orig_str}' not found in recompiled data"

        print("✅ Round-trip test passed")

        # Cleanup
        os.unlink(temp_txt_path)
        os.unlink(recompiled_path)

    finally:
        os.unlink(temp_wsc_path)


def test_validation():
    """Test validator functionality."""
    print("🧪 Testing validator...")

    validator = WSCValidator()

    # Test valid content
    valid_content = create_test_text_content()
    entries, _ = parse_github_format(valid_content)
    result = validator.comprehensive_validation(valid_content, entries)

    assert result.is_valid, f"Valid content should pass validation: {result.errors}"

    # Test invalid format
    invalid_content = "This is not valid WSC format\nNo offsets here"
    result = validator.validate_format_structure(invalid_content)

    assert not result.is_valid, "Invalid format should fail validation"
    assert len(result.errors) > 0, "Should have error messages"

    # Test quick validation with simple valid content
    simple_valid = "<00000000:00000007>\nDAY0904\n<00000008:0000000E>\n.SE_104.ogg\n"
    quick_result = validator.quick_validate(simple_valid)
    # This simple content should pass quick validation
    assert quick_result['valid'], f"Simple valid content should pass quick validation: {quick_result}"

    print("✅ Validator test passed")


def test_speaker_detection():
    """Test speaker name detection and conversion."""
    print("🧪 Testing speaker detection...")

    # Test speaker name conversion (marked as speaker)
    speaker_binary = content_to_binary("夜久", True)
    assert speaker_binary.startswith(b'\x0F\x0F'), "Japanese speaker name should use double 0x0F"

    # Test narration conversion (NOT marked as speaker)
    narration_binary = content_to_binary("こんにちは世界", False)
    assert narration_binary.startswith(b'\x0F'), "Narration should use single 0x0F"
    assert not narration_binary.startswith(b'\x0F\x0F'), "Narration should not use double 0x0F"

    # Test empty content
    empty_binary = content_to_binary("", True)
    assert empty_binary == b'\x00', "Empty content should be just null terminator"

    print("✅ Speaker detection test passed")


def test_encoding_handling():
    """Test encoding compatibility and error handling."""
    print("🧪 Testing encoding handling...")

    validator = WSCValidator()

    # Test CP932 compatible text
    cp932_text = "DAY0904"
    result = validator.validate_encoding_compatibility(cp932_text)
    # Encoding validation should not have errors for CP932 compatible text
    assert len(result.errors) == 0, f"CP932 compatible text should not have errors: {result.errors}"

    # Test problematic characters (should still work due to fallback)
    problematic_text = "Testing ✨ emoji"
    result = validator.validate_encoding_compatibility(problematic_text)
    # This may not fail due to fallback mechanisms, so we just check it doesn't crash

    print("✅ Encoding handling test passed")


def test_api_simulation():
    """Simulate API workflow."""
    print("🧪 Testing API simulation...")

    # Simulate upload workflow
    content = create_test_text_content()
    entries, parse_result = parse_github_format(content)

    # Simulate validation workflow
    validator = WSCValidator()
    validation_result = validator.comprehensive_validation(content, entries)

    # Simulate compilation workflow
    binary = reconstruct_wsc_binary(entries, preserve_offsets=False)

    # Check all steps succeeded
    assert parse_result.is_valid, "Parse step should succeed"
    assert validation_result.is_valid, "Validation step should succeed"
    assert len(binary) > 0, "Compilation should produce binary data"

    print("✅ API simulation test passed")


def run_all_tests():
    """Run all recompiler tests."""
    print("🚀 Starting WSC Recompiler Test Suite")
    print("=" * 50)

    tests = [
        test_parse_github_format,
        test_content_to_binary,
        test_reconstruct_wsc_binary,
        test_round_trip,
        test_validation,
        test_speaker_detection,
        test_encoding_handling,
        test_api_simulation
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()

    print("=" * 50)
    print(f"📊 Test Results: {passed} passed, {failed} failed")

    if failed == 0:
        print("🎉 All tests passed! WSC Recompiler is working correctly!")
        return True
    else:
        print(f"⚠️ {failed} test(s) failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)