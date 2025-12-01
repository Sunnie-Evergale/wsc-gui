#!/usr/bin/env python3
# comprehensive_test.py
# Comprehensive test suite for WSC decompiler

import os
import sys
import tempfile
from pathlib import Path
from decompiler import decompile_wsc_file


def create_test_wsc_with_all_features():
    """Create a comprehensive test WSC file with all required features."""
    test_data = bytearray()

    # Resource IDs (should be kept)
    test_data.extend(b"DAY0904\x00")           # Day resource
    test_data.extend(b"BG108_02\x00")           # Background image
    test_data.extend(b"ST13A05S\x00")           # Character sprite
    test_data.extend(b"HOS_1318\x00")           # Hospital sprite

    # Audio files (should be kept)
    test_data.extend(b"SE_104.ogg\x00")         # Sound effect
    test_data.extend(b"BGM_06\x00")             # Background music

    # Engine commands (should be kept)
    test_data.extend(b"%K%P\x00")               # Wait for key press
    test_data.extend(b"%N\x00")                 # New page

    # Speaker names with 0x0F prefix (should get .Name format)
    test_data.extend(b"\x0F\x0F")              # Double 0x0F prefix
    test_data.extend(b"\x96\xe9\x8b\x56\x00")   # 夜久 (Yoru Hisashi) in CP932

    test_data.extend(b"\x0F\x0F\x0F")          # Triple 0x0F prefix
    test_data.extend(b"\x94\xfc\x97\x51\x00")   # 美里 (Misato) in CP932

    # Narration lines with 0x0F prefix (should lose prefix, no dot)
    test_data.extend(b"\x0F")
    # こんにちは世界 (Hello world) in CP932
    test_data.extend(b"\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd\x90\xa2\x8a\xc5\x00")

    test_data.extend(b"\x0F")
    # 今日は良い天気ですね (Today is good weather) in CP932
    test_data.extend(b"\x8d\xa1\x93\xfa\x82\xcd\x97\xc7\x82\xa2\x93\x47\x8b\xc2\x82\xc5\x82\xb7\x82\xcb\x00")

    # More complex Japanese text with punctuation
    test_data.extend(b"\x0F")
    # さようなら、世界… (Goodbye, world...) in CP932
    test_data.extend(b"\x8d\xb3\x82\xe6\x82\xa4\x82\xc8\x82\xe7\x81\x42\x90\xa2\x8a\xc5\x81\x46\x00")

    # Mixed content - should still be recognized as meaningful
    test_data.extend(b"\x0F")
    # プレイヤーの名前は何ですか？ (What is your name?) in CP932 - simplified version
    test_data.extend(b"\x83\x76\x83\x8c\x83\x43\x83\x84\x81\x5b\x82\xcc\x96\xbc\x91\x4f\x82\xcd\x89\xbd\x82\xc5\x82\xb7\x82\xa9\x81\x48\x00")

    # Garbage tokens (should be filtered out)
    test_data.extend(b"I\x00")                 # Single character
    test_data.extend(b"t\x00")                 # Single character
    test_data.extend(b"F\x00")                 # Single character
    test_data.extend(b"\x01\x02\x03\x00")       # Random bytes

    # More resource IDs
    test_data.extend(b"DAY1005\x00")            # Another day
    test_data.extend(b"BG202_01\x00")           # Another background

    return bytes(test_data)


def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🧪 Running Comprehensive WSC Decompiler Test Suite")
    print("=" * 60)

    # Create test file
    test_data = create_test_wsc_with_all_features()
    with tempfile.NamedTemporaryFile(suffix='.wsc', delete=False) as f:
        f.write(test_data)
        input_file = f.name

    # Create output file path
    with tempfile.NamedTemporaryFile(suffix='.txt', delete=False) as f:
        output_file = f.name

    try:
        print(f"📁 Test input file: {input_file}")
        print(f"📁 Test output file: {output_file}")
        print(f"📊 Input size: {len(test_data)} bytes")
        print()

        # Run decompiler
        print("🔧 Running decompiler...")
        decompile_wsc_file(input_file, output_file)
        print("✅ Decompilation completed successfully!")

        # Read and analyze output
        with open(output_file, 'r', encoding='utf-8') as f:
            output_content = f.read()

        print(f"📄 Output size: {len(output_content)} characters")
        print()

        # Parse output into records
        lines = output_content.strip().split('\n')
        records = []
        i = 0
        while i < len(lines):
            if lines[i].startswith('<') and ':' in lines[i]:
                offset_line = lines[i]
                if i + 1 < len(lines):
                    content = lines[i + 1]
                    records.append((offset_line, content))
                    i += 2
                else:
                    i += 1
            else:
                i += 1

        print(f"📋 Found {len(records)} records extracted")
        print()

        # Test each requirement
        print("🔍 Testing Requirements:")
        print("-" * 40)

        # Test 1: Resource IDs kept
        resource_found = any('DAY' in content for _, content in records)
        print(f"✅ Resource IDs preserved: {'YES' if resource_found else 'NO'}")
        if resource_found:
            for offset, content in records:
                if any(resource in content for resource in ['DAY', 'BG', 'ST', 'HOS']):
                    print(f"   {offset}: {content}")

        print()

        # Test 2: Audio files kept
        audio_found = any('SE_' in content or 'BGM_' in content for _, content in records)
        print(f"✅ Audio file names preserved: {'YES' if audio_found else 'NO'}")
        if audio_found:
            for offset, content in records:
                if 'SE_' in content or 'BGM_' in content:
                    print(f"   {offset}: {content}")

        print()

        # Test 3: Engine commands kept
        engine_cmd_found = any('%' in content for _, content in records)
        print(f"✅ Engine commands preserved: {'YES' if engine_cmd_found else 'NO'}")
        if engine_cmd_found:
            for offset, content in records:
                if '%' in content:
                    print(f"   {offset}: {content}")

        print()

        # Test 4: Speaker names with . prefix
        speaker_names = [content for _, content in records if content.startswith('.')]
        print(f"✅ Speaker names with '.' prefix: {len(speaker_names)} found")
        for offset, content in records:
            if content.startswith('.'):
                print(f"   {offset}: {content}")

        print()

        # Test 5: Narration without . prefix
        japanese_narration = [content for _, content in records
                             if not content.startswith('.') and
                             any('\u3040' <= ch <= '\u309F' or '\u30A0' <= ch <= '\u30FF' or '\u4E00' <= ch <= '\u9FFF'
                                 for ch in content)]
        print(f"✅ Japanese narration (no dot): {len(japanese_narration)} found")
        for offset, content in records:
            if content in japanese_narration:
                print(f"   {offset}: {content}")

        print()

        # Test 6: Hex offset format
        offset_format_correct = all(offset_line.startswith('<') and ':' in offset_line and '>' in offset_line
                                  for offset_line, _ in records)
        print(f"✅ Hex offset format <XXXXXXXX:XXXXXXXX>: {'YES' if offset_format_correct else 'NO'}")

        print()

        # Test 7: Garbage filtering (should be filtered out)
        garbage_found = any(content in ['I', 't', 'F'] or len(content.strip()) < 2
                          for _, content in records if not content.startswith('.') and '%' not in content)
        print(f"✅ Garbage tokens filtered: {'YES' if not garbage_found else 'NO'}")

        print()
        print("=" * 60)

        # Show full output
        print("📄 Complete Decompiled Output:")
        print("-" * 40)
        print(output_content)
        print("-" * 40)

        # Overall result
        all_tests_passed = all([
            resource_found,
            audio_found,
            engine_cmd_found,
            len(speaker_names) > 0,
            len(japanese_narration) > 0,
            offset_format_correct,
            not garbage_found
        ])

        print()
        if all_tests_passed:
            print("🎉 ALL TESTS PASSED! The WSC decompiler is working correctly.")
            return True
        else:
            print("❌ Some tests failed. Please check the output above.")
            return False

    finally:
        # Cleanup
        try:
            os.unlink(input_file)
            os.unlink(output_file)
        except:
            pass


def main():
    """Main entry point."""
    try:
        success = run_comprehensive_test()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())