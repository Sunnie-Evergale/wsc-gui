#!/usr/bin/env python3
# test_decompiler.py
# Test script for the decompiler without tkinterdnd2

import os
import sys
from pathlib import Path
from decompiler import decompile_wsc_file

def create_test_wsc():
    """Create a test WSC file with sample data."""
    # Create test data similar to actual WSC format
    test_data = bytearray()

    # Add some sample data with null terminators
    # Resource ID
    test_data.extend(b"DAY0904\x00")

    # Speaker name with 0x0F prefix (2 bytes)
    test_data.extend(b"\x0F\x0F")
    # Japanese name encoded in CP932 (夜久)
    test_data.extend(b"\x96\xe9\x8b\x56\x00")

    # Narration with 0x0F prefix
    test_data.extend(b"\x0F")
    # Japanese text encoded in CP932 (こんにちは世界)
    test_data.extend(b"\x82\xb1\x82\xf1\x82\xc9\x82\xbf\x82\xcd\x90\xa2\x8a\xc5\x00")

    # Audio file name
    test_data.extend(b"SE_104.ogg\x00")

    # BGM name
    test_data.extend(b"BGM_06\x00")

    # Engine command
    test_data.extend(b"%K%P\x00")

    # Background image
    test_data.extend(b"BG108_02\x00")

    # Character sprite
    test_data.extend(b"ST13A05S\x00")

    # Another speaker
    test_data.extend(b"\x0F\x0F")
    # Japanese name (美里)
    test_data.extend(b"\x94\xfc\x97\x51\x00")

    # More dialogue
    test_data.extend(b"\x0F")
    # Japanese text (今日は良い天気ですね)
    test_data.extend(b"\x8d\xa1\x93\xfa\x82\xcd\x97\xc7\x82\xa2\x93\x47\x8b\xc2\x82\xc5\x82\xb7\x82\xcb\x00")

    return bytes(test_data)

def test_decompiler():
    """Test the decompiler with a sample WSC file."""
    print("Testing WSC Decompiler...")

    # Create test directory
    test_dir = Path("test_files")
    test_dir.mkdir(exist_ok=True)

    # Create test WSC file
    test_wsc_path = test_dir / "test.wsc"
    test_data = create_test_wsc()
    test_wsc_path.write_bytes(test_data)

    print(f"Created test WSC file: {test_wsc_path}")
    print(f"Test file size: {len(test_data)} bytes")

    # Test decompilation
    output_path = test_dir / "test_output.txt"
    try:
        decompile_wsc_file(str(test_wsc_path), str(output_path))
        print(f"Successfully decompiled to: {output_path}")

        # Show the output
        if output_path.exists():
            print("\nDecompiled content:")
            print("=" * 40)
            print(output_path.read_text(encoding='utf-8'))
            print("=" * 40)

        return True

    except Exception as e:
        print(f"Error during decompilation: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_decompiler()
    if success:
        print("\n✅ Decompiler test passed!")
    else:
        print("\n❌ Decompiler test failed!")
        sys.exit(1)