#!/usr/bin/env python3
# test_js_syntax.py
# Test JavaScript syntax in the generated HTML

import requests
import re
import subprocess
import tempfile

def test_javascript_syntax():
    """Test JavaScript syntax in the web GUI HTML."""
    print("🧪 Testing JavaScript Syntax")
    print("=" * 40)

    base_url = "http://localhost:8088"

    try:
        # Get the HTML content
        response = requests.get(base_url, timeout=10)
        assert response.status_code == 200, "Should get the page successfully"

        html_content = response.text

        # Extract JavaScript code from HTML
        script_match = re.search(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        assert script_match, "Should find script tag"

        js_code = script_match.group(1)

        # Remove the HTML structure part and keep only JavaScript
        js_start = js_code.find('let selectedFiles')
        if js_start != -1:
            js_code = js_code[js_start:]

        # Write JavaScript to a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.js', delete=False) as f:
            f.write(js_code)
            temp_js_file = f.name

        try:
            # Test with Node.js if available
            result = subprocess.run(['node', '--check', temp_js_file],
                                    capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ JavaScript syntax is valid (Node.js check)")
            else:
                print("❌ JavaScript syntax error (Node.js check):")
                print(result.stderr)
                return False
        except FileNotFoundError:
            print("⚠️ Node.js not available, skipping syntax check")

        # Basic syntax checks
        print("1️⃣ Checking for common syntax issues...")

        # Check for unmatched braces
        open_braces = js_code.count('{')
        close_braces = js_code.count('}')
        if open_braces != close_braces:
            print(f"❌ Brace mismatch: {open_braces} open, {close_braces} close")
            return False
        else:
            print(f"✅ Braces balanced: {open_braces}")

        # Check for unmatched parentheses
        open_parens = js_code.count('(')
        close_parens = js_code.count(')')
        if open_parens != close_parens:
            print(f"❌ Parentheses mismatch: {open_parens} open, {close_parens} close")
            return False
        else:
            print(f"✅ Parentheses balanced: {open_parens}")

        # Check for multiline template literal issues
        lines = js_code.split('\n')
        in_template = False
        multiline_found = False

        for i, line in enumerate(lines):
            if '`' in line:
                backtick_count = line.count('`')
                if backtick_count == 1:
                    if in_template:
                        # This might be a closing backtick
                        if line.strip().endswith('`'):
                            in_template = False
                    else:
                        # This might be an opening backtick
                        if not line.strip().endswith('`'):
                            in_template = True
                        elif not line.strip().startswith('`'):
                            # Single line template
                            pass
                elif backtick_count > 1:
                    # Multiple backticks on one line - check if they span
                    if '`' not in line.replace('`', ''):
                        # All backticks are literal characters, not template delimiters
                        pass
                    else:
                        # Template delimiter - check if content spans
                        if not line.strip().startswith('`') or not line.strip().endswith('`'):
                            in_template = not in_template
            elif in_template and not line.strip().startswith('`'):
                multiline_found = True
                print(f"❌ Multiline template found at line {i+1}: {repr(line[:50])}")
                break

        if multiline_found:
            print("❌ Found multiline template literal - this can cause syntax errors")
            print("Template literals should be single-line or use \\n for newlines")
            return False
        else:
            print("✅ No problematic multiline template literals found")

        # Check for function definitions
        function_count = len(re.findall(r'function\s+\w+\s*\(', js_code))
        arrow_function_count = len(re.findall(r'=\s*\([^)]*\)\s*=>', js_code))
        print(f"✅ Found {function_count} named functions and {arrow_function_count} arrow functions")

        # Check for event listeners
        event_listener_count = len(re.findall(r'addEventListener\s*\(', js_code))
        print(f"✅ Found {event_listener_count} event listeners")

        print("\n🎉 JavaScript syntax validation passed!")
        print("🌐 The web GUI should work without JavaScript errors at:", base_url)

        # Cleanup
        try:
            import os
            os.unlink(temp_js_file)
        except:
            pass

        return True

    except Exception as e:
        print(f"❌ JavaScript syntax test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_javascript_syntax()
    exit(0 if success else 1)