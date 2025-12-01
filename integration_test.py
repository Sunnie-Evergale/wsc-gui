#!/usr/bin/env python3
# integration_test.py
# Integration test for the complete WSC decompiler/recompiler system

import requests
import json
import tempfile
import os
from pathlib import Path

def test_web_server_integration():
    """Test integration with the web server."""
    print("🌐 Testing Web Server Integration")
    print("=" * 40)

    base_url = "http://localhost:8082"

    try:
        # Test 1: Check if server is running
        print("1️⃣ Testing server connectivity...")
        response = requests.get(base_url, timeout=5)
        assert response.status_code == 200, "Server should respond with 200"
        print("✅ Server is running")

        # Test 2: Test directory browsing API
        print("2️⃣ Testing directory browsing API...")
        response = requests.get(f"{base_url}/api/browse?path=/tmp", timeout=5)
        assert response.status_code == 200, "Directory browsing should work"
        data = response.json()
        assert data.get('success'), "Directory API should return success"
        print("✅ Directory browsing API working")

        # Test 3: Test recompiler upload with sample data
        print("3️⃣ Testing recompiler upload API...")

        # Create sample decompiled text
        sample_text = """<00000000:00000007>
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

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(sample_text)
            temp_file_path = f.name

        try:
            # Upload file
            with open(temp_file_path, 'rb') as f:
                files = {'file': ('test.txt', f, 'text/plain')}
                response = requests.post(f"{base_url}/api/recompile/upload", files=files, timeout=10)

            assert response.status_code == 200, "Upload should succeed"
            data = response.json()
            assert data.get('success'), "Upload should return success"
            assert len(data.get('entries', [])) > 0, "Should parse entries"

            print(f"✅ Recompiler upload working - parsed {len(data['entries'])} entries")

            # Test 4: Test validation API
            print("4️⃣ Testing validation API...")

            validation_data = {
                'content': sample_text,
                'entries': data['entries']
            }

            response = requests.post(
                f"{base_url}/api/recompile/validate",
                json=validation_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            assert response.status_code == 200, "Validation should succeed"
            validation_result = response.json()
            assert validation_result.get('success'), "Validation should return success"

            print("✅ Validation API working")

            # Test 5: Test compilation API
            print("5️⃣ Testing compilation API...")

            compile_data = {
                'entries': data['entries'],
                'preserve_offsets': False,
                'filename': 'test_output.wsc'
            }

            response = requests.post(
                f"{base_url}/api/recompile/compile",
                json=compile_data,
                headers={'Content-Type': 'application/json'},
                timeout=10
            )

            assert response.status_code == 200, "Compilation should succeed"
            compile_result = response.json()
            assert compile_result.get('success'), "Compilation should return success"
            assert compile_result.get('file_size', 0) > 0, "Should create file with content"

            print(f"✅ Compilation API working - created {compile_result['file_size']} byte file")

        finally:
            # Cleanup
            try:
                os.unlink(temp_file_path)
            except:
                pass

        # Test 6: Test recompiler page loads
        print("6️⃣ Testing recompiler interface...")
        response = requests.get(base_url, timeout=5)
        html_content = response.text
        assert "Recompiler" in html_content, "Recompiler should be in the page"
        assert "✏️ Recompiler" in html_content, "Recompiler tab should be present"
        print("✅ Recompiler interface accessible")

        print("\n🎉 All integration tests passed!")
        print(f"🌐 Web GUI is fully functional at: {base_url}")
        print("\nFeatures available:")
        print("  ✅ WSC Decompilation (original functionality)")
        print("  ✅ WSC Recompilation (new functionality)")
        print("  ✅ Interactive text editor")
        print("  ✅ Real-time validation")
        print("  ✅ Directory browsing")
        print("  ✅ File upload/download")

        return True

    except requests.exceptions.ConnectionError:
        print("❌ Connection error - server may not be running")
        print("   Start the server with: python3 web_gui.py --port 8082")
        return False
    except Exception as e:
        print(f"❌ Integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_web_server_integration()
    exit(0 if success else 1)