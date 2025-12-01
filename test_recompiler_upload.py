#!/usr/bin/env python3
# test_recompiler_upload.py
# Test the recompiler upload functionality

import requests
import tempfile
import os

def create_test_txt_file():
    """Create a test decompiled WSC file."""
    content = """<00000000:00000007>
DAY0904

<00000008:0000000E>
.夜久

<0000000F:0000001E>
こんにちは世界

<0000001F:00000029>
SE_104.ogg

<0000002A:0000002E>
%K%P
"""
    return content

def test_recompiler_upload():
    """Test the recompiler upload functionality."""
    print("🧪 Testing Recompiler Upload Functionality")
    print("=" * 50)

    base_url = "http://localhost:8104"

    try:
        # Create test file content
        test_content = create_test_txt_file()

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_content)
            temp_file_path = f.name

        print(f"📄 Created test file: {temp_file_path}")

        try:
            # Test file upload
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = requests.post(f"{base_url}/api/recompile/upload", files=files, timeout=10)

            print(f"📡 Upload response status: {response.status_code}")

            if response.status_code == 200:
                data = response.json()
                if data.get('success'):
                    print("✅ Upload successful!")
                    print(f"   Filename: {data.get('filename')}")
                    print(f"   Entries parsed: {len(data.get('entries', []))}")
                    print(f"   Parse valid: {data.get('parse_result', {}).get('valid', False)}")
                    print(f"   Validation valid: {data.get('validation_result', {}).get('valid', False)}")
                    return True
                else:
                    print(f"❌ Upload failed: {data.get('message')}")
                    return False
            else:
                print(f"❌ HTTP error: {response.status_code}")
                return False

        finally:
            # Cleanup
            try:
                os.unlink(temp_file_path)
                print(f"🧹 Cleaned up test file")
            except:
                pass

    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_recompiler_upload()
    exit(0 if success else 1)