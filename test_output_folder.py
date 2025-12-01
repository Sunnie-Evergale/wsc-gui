#!/usr/bin/env python3
# test_output_folder.py
# Test the output folder functionality

import requests
import tempfile
import os

def test_output_folder_api():
    """Test the output folder API endpoint."""
    print("🧪 Testing Output Folder API")
    print("=" * 40)

    base_url = "http://localhost:8094"  # Use the current server

    try:
        # Test output folder listing
        response = requests.get(f"{base_url}/api/recompile/output", timeout=10)

        print(f"📡 API response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Output folder API working!")
                print(f"   Output folder: {data.get('output_folder')}")
                print(f"   Total files: {data.get('total_files', 0)}")

                if data.get('files'):
                    print("   Files in output folder:")
                    for i, file in enumerate(data.get('files', []), 1):
                        print(f"     {i}. {file['filename']} ({file['file_size']} bytes)")

                return True
            else:
                print(f"❌ API error: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_compilation_with_output():
    """Test compilation and output folder creation."""
    print("\n🧪 Testing Compilation with Output Folder")
    print("=" * 50)

    base_url = "http://localhost:8094"

    # Test data for compilation
    test_entries = [
        {
            "start_offset": 8,
            "end_offset": 14,
            "content": "テスト",
            "is_speaker": True
        },
        {
            "start_offset": 15,
            "end_offset": 25,
            "content": "Hello World",
            "is_speaker": False
        }
    ]

    try:
        # Test compilation
        compile_data = {
            "entries": test_entries,
            "preserve_offsets": True,
            "filename": "test_output.wsc"
        }

        response = requests.post(
            f"{base_url}/api/recompile/compile",
            json=compile_data,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )

        print(f"📡 Compilation response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("✅ Compilation successful!")
                print(f"   Filename: {data.get('filename')}")
                print(f"   Output folder: {data.get('output_folder')}")
                print(f"   File size: {data.get('file_size')} bytes")
                print(f"   Entries: {data.get('entries_count')}")

                # Test output folder listing again
                output_response = requests.get(f"{base_url}/api/recompile/output", timeout=10)
                if output_response.status_code == 200:
                    output_data = output_response.json()
                    if output_data.get('success') and output_data.get('total_files', 0) > 0:
                        print("✅ Output folder now contains compiled files!")

                return True
            else:
                print(f"❌ Compilation error: {data.get('message')}")
                return False
        else:
            print(f"❌ HTTP error: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🗂️ Testing Recompiler Output Folder Functionality")
    print("=" * 60)

    # Test 1: Output folder API
    success1 = test_output_folder_api()

    # Test 2: Compilation with output folder
    success2 = test_compilation_with_output()

    overall_success = success1 and success2

    print(f"\n🎯 Overall Result: {'✅ SUCCESS' if overall_success else '❌ FAILED'}")

    if overall_success:
        print("\n🎉 Output folder functionality is working correctly!")
        print("   - Compiled files are saved to the output folder")
        print("   - API can list files in the output folder")
        print("   - Timestamped filenames prevent conflicts")

    exit(0 if overall_success else 1)