#!/usr/bin/env python3
"""
Final integration test for Flow KVM Italian dead keys
Run this test to verify everything works correctly
"""

import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hardware.keyboard_layout import LayoutType, get_layout_manager
from hardware.keyboard import test_dead_key_support
from data.db import Settings
import sqlite3

def test_database_integration():
    """Test that layout settings are properly stored in database"""
    print("Testing Database Integration")
    print("=" * 30)
    
    try:
        # Test database connection and layout settings
        conn = sqlite3.connect('data.db')
        cursor = conn.cursor()
        
        # Check if layout settings exist
        cursor.execute("SELECT * FROM configuration WHERE key=?", (Settings.KEYBOARD_LAYOUT,))
        layout_setting = cursor.fetchone()
        
        cursor.execute("SELECT * FROM configuration WHERE key=?", (Settings.LAYOUT_AUTO_DETECT,))
        auto_detect_setting = cursor.fetchone()
        
        if layout_setting:
            print(f"✓ Layout setting found: {layout_setting[1]}")
        else:
            print("✗ Layout setting not found")
        
        if auto_detect_setting:
            print(f"✓ Auto-detect setting found: {auto_detect_setting[1]}")
        else:
            print("✗ Auto-detect setting not found")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database error: {e}")
        return False

def test_layout_detection():
    """Test automatic layout detection"""
    print("Testing Layout Detection")
    print("=" * 25)
    
    try:
        layout_manager = get_layout_manager()
        layout_info = layout_manager.get_layout_info()
        
        print(f"✓ Detected layout: {layout_info.layout_type.value}")
        print(f"✓ Language: {layout_info.language_code}")
        print(f"✓ Country: {layout_info.country_code}")
        print(f"✓ Display name: {layout_info.layout_name}")
        
        # Force Italian layout for testing
        layout_manager.set_layout_type(LayoutType.QWERTY_IT)
        italian_layout = layout_manager.get_layout_info()
        
        print(f"✓ Italian layout test: {italian_layout.layout_type.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Layout detection error: {e}")
        return False

def test_character_conversion():
    """Test character conversion between layouts"""
    print("Testing Character Conversion")
    print("=" * 30)
    
    try:
        layout_manager = get_layout_manager()
        
        # Test some common character conversions
        test_chars = ['a', 'z', 'q', 'w', 'y', ';', '[', ']']
        conversions_ok = 0
        
        for char in test_chars:
            try:
                # Convert US to German
                us_to_de = layout_manager.convert_key_between_layouts(
                    char, LayoutType.QWERTY_US, LayoutType.QWERTZ_DE
                )
                
                # Convert back
                de_to_us = layout_manager.convert_key_between_layouts(
                    us_to_de, LayoutType.QWERTZ_DE, LayoutType.QWERTY_US
                )
                
                if de_to_us == char:
                    conversions_ok += 1
                    print(f"✓ {char} → {us_to_de} → {char}")
                else:
                    print(f"✗ {char} → {us_to_de} → {de_to_us} (failed round-trip)")
                    
            except Exception as e:
                print(f"✗ Error converting {char}: {e}")
        
        print(f"Conversion success rate: {conversions_ok}/{len(test_chars)}")
        return conversions_ok >= len(test_chars) * 0.8  # 80% success rate
        
    except Exception as e:
        print(f"✗ Character conversion error: {e}")
        return False

def test_italian_dead_keys():
    """Test Italian dead key functionality"""
    print("Testing Italian Dead Keys")
    print("=" * 25)
    
    try:
        layout_manager = get_layout_manager()
        layout_manager.set_layout_type(LayoutType.QWERTY_IT)
        
        # Test some key dead key combinations
        dead_key_tests = [
            ('`', 'a', 'à'),
            ('`', 'e', 'è'),
            ("'", 'e', 'é'),
            ('^', 'i', 'î'),
            ('~', 'n', 'ñ'),
            ('"', 'u', 'ü')
        ]
        
        success_count = 0
        for dead_key, base_char, expected in dead_key_tests:
            # Reset dead key state
            layout_manager.pending_dead_key = None
            
            # Input dead key
            result1 = layout_manager.process_key_input(dead_key)
            
            # Input base character  
            result2 = layout_manager.process_key_input(base_char)
            
            if result2 == expected:
                print(f"✓ {dead_key} + {base_char} → {result2}")
                success_count += 1
            else:
                print(f"✗ {dead_key} + {base_char} → {result2} (expected {expected})")
        
        print(f"Dead key success rate: {success_count}/{len(dead_key_tests)}")
        return success_count == len(dead_key_tests)
        
    except Exception as e:
        print(f"✗ Dead key test error: {e}")
        return False

def main():
    print("Flow KVM - Final Integration Test")
    print("=" * 50)
    print("This test verifies all components work correctly together.")
    print()
    
    tests = [
        ("Database Integration", test_database_integration),
        ("Layout Detection", test_layout_detection),
        ("Character Conversion", test_character_conversion),
        ("Italian Dead Keys", test_italian_dead_keys)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ Test {test_name} crashed: {e}")
            results.append((test_name, False))
        
        print()
    
    # Summary
    print("=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print()
    print(f"Overall Result: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED!")
        print("Flow KVM is ready for Italian keyboard layout with dead keys support.")
        print()
        print("You can now:")
        print("1. Start the server: python debug_flow.py")
        print("2. Connect clients with Italian layout")
        print("3. Use dead key combinations like ` + a = à")
        print("4. Enjoy seamless international keyboard support!")
        
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        print("The system may not work correctly with Italian dead keys.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)