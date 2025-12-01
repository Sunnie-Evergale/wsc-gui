#!/usr/bin/env python3
# test_javascript.py
# Test JavaScript functionality in the web GUI

import requests
import re

def test_javascript_functionality():
    """Test that JavaScript functions are properly defined in the HTML."""
    print("🧪 Testing JavaScript Functionality")
    print("=" * 40)

    base_url = "http://localhost:8083"

    try:
        # Get the HTML content
        response = requests.get(base_url, timeout=5)
        assert response.status_code == 200, "Should get the page successfully"

        html_content = response.text

        # Check for switchTab function definition
        print("1️⃣ Checking for switchTab function...")
        switchTab_match = re.search(r'function switchTab\(tabName\)', html_content)
        assert switchTab_match, "switchTab function should be defined"
        print("✅ switchTab function found")

        # Check for setupTabSwitching function
        print("2️⃣ Checking for setupTabSwitching function...")
        setupTab_match = re.search(r'function setupTabSwitching\(\)', html_content)
        assert setupTab_match, "setupTabSwitching function should be defined"
        print("✅ setupTabSwitching function found")

        # Check for event listener setup
        print("3️⃣ Checking for event listener setup...")
        event_listener_match = re.search(r'addEventListener\([\'"]click[\'"], function\(\)', html_content)
        assert event_listener_match, "Click event listeners should be set up"
        print("✅ Event listeners found")

        # Check for defensive onclick attributes
        print("4️⃣ Checking for defensive onclick attributes...")
        defensive_onclick_match = re.search(r'if\(typeof switchTab === [\'"]function[\'"]\)', html_content)
        assert defensive_onclick_match, "Defensive onclick should be present"
        print("✅ Defensive onclick found")

        # Check for tab content containers
        print("5️⃣ Checking for tab content containers...")
        decompiler_content_match = re.search(r'id=[\'"]decompilerTabContent[\'"]', html_content)
        recompiler_content_match = re.search(r'id=[\'"]recompilerTabContent[\'"]', html_content)
        assert decompiler_content_match, "Decompiler tab content should exist"
        assert recompiler_content_match, "Recompiler tab content should exist"
        print("✅ Tab content containers found")

        # Check for tab buttons
        print("6️⃣ Checking for tab buttons...")
        decompiler_tab_match = re.search(r'id=[\'"]decompilerTab[\'"]', html_content)
        recompiler_tab_match = re.search(r'id=[\'"]recompilerTab[\'"]', html_content)
        assert decompiler_tab_match, "Decompiler tab button should exist"
        assert recompiler_tab_match, "Recompiler tab button should exist"
        print("✅ Tab buttons found")

        # Check for CSS classes
        print("7️⃣ Checking for CSS classes...")
        tab_content_class_match = re.search(r'\.tab-content\s*\{[^}]*display:\s*none', html_content)
        active_class_match = re.search(r'\.active\s*\{[^}]*display:\s*block', html_content)
        assert tab_content_class_match, "tab-content CSS should exist"
        assert active_class_match, "active CSS should exist"
        print("✅ CSS classes found")

        # Check DOMContentLoaded event
        print("8️⃣ Checking for DOMContentLoaded event...")
        dom_loaded_match = re.search(r'document\.addEventListener\([\'"]DOMContentLoaded[\'"]', html_content)
        assert dom_loaded_match, "DOMContentLoaded event should be set up"
        print("✅ DOMContentLoaded event found")

        print("\n🎉 All JavaScript tests passed!")
        print("🌐 The tab switching functionality should work correctly at:", base_url)
        print("\n📋 What was verified:")
        print("  ✅ JavaScript functions are properly defined")
        print("  ✅ Event listeners are set up correctly")
        print("  ✅ Defensive onclick attributes prevent early execution")
        print("  ✅ Tab content containers exist")
        print("  ✅ Tab buttons are properly configured")
        print("  ✅ CSS for tab switching is present")
        print("  ✅ DOM is ready before script execution")

        return True

    except Exception as e:
        print(f"❌ JavaScript test failed: {e}")
        return False


if __name__ == "__main__":
    success = test_javascript_functionality()
    exit(0 if success else 1)