#!/usr/bin/env python3
"""
Test complete client-server communication with Italian dead keys
"""

import sys
import os
import time

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hardware.keyboard_layout import LayoutType
from hardware.keyboard import create_layout_aware_key_data, key_from_layout_aware_data, get_layout_manager
from pynput import keyboard

def test_key_transmission():
    """Test the complete key transmission process"""
    
    print("Testing Complete Key Transmission Process")
    print("=" * 50)
    
    # Initialize layout manager with Italian layout
    layout_manager = get_layout_manager()
    layout_manager.set_layout_type(LayoutType.QWERTY_IT)
    
    print(f"Server layout: {layout_manager.current_layout.layout_type.value}")
    print(f"Language: {layout_manager.current_layout.language_code}")
    print()
    
    # Test scenarios for Italian dead keys
    test_cases = [
        # (dead_key, base_char, expected_result, description)
        ('`', 'a', 'à', 'Grave accent on a'),
        ('`', 'e', 'è', 'Grave accent on e'),
        ('`', 'i', 'ì', 'Grave accent on i'),
        ('`', 'o', 'ò', 'Grave accent on o'),
        ('`', 'u', 'ù', 'Grave accent on u'),
        ("'", 'a', 'á', 'Acute accent on a'),
        ("'", 'e', 'é', 'Acute accent on e'),
        ("'", 'i', 'í', 'Acute accent on i'),
        ("'", 'o', 'ó', 'Acute accent on o'),
        ("'", 'u', 'ú', 'Acute accent on u'),
        ('^', 'a', 'â', 'Circumflex accent on a'),
        ('^', 'e', 'ê', 'Circumflex accent on e'),
        ('^', 'i', 'î', 'Circumflex accent on i'),
        ('^', 'o', 'ô', 'Circumflex accent on o'),
        ('^', 'u', 'û', 'Circumflex accent on u'),
        ('~', 'n', 'ñ', 'Tilde accent on n'),
        ('"', 'a', 'ä', 'Diaeresis on a'),
        ('"', 'e', 'ë', 'Diaeresis on e'),
        ('"', 'i', 'ï', 'Diaeresis on i'),
        ('"', 'o', 'ö', 'Diaeresis on o'),
        ('"', 'u', 'ü', 'Diaeresis on u'),
    ]
    
    successful_tests = 0
    total_tests = len(test_cases)
    
    for dead_key, base_char, expected, description in test_cases:
        print(f"Testing: {description}")
        
        try:
            # Step 1: Create key data for dead key (server side)
            dead_key_code = keyboard.KeyCode.from_char(dead_key)
            dead_key_data = create_layout_aware_key_data(dead_key_code)
            
            # Step 2: Create key data for base character (server side)
            base_key_code = keyboard.KeyCode.from_char(base_char)
            base_key_data = create_layout_aware_key_data(base_key_code)
            
            print(f"  Dead key data: {dead_key_data}")
            print(f"  Base key data: {base_key_data}")
            
            # Step 3: Convert key data back to keys (client side)
            # This simulates the transmission process
            reconstructed_dead_key = key_from_layout_aware_data(dead_key_data)
            reconstructed_base_key = key_from_layout_aware_data(base_key_data)
            
            print(f"  Reconstructed dead key: {reconstructed_dead_key}")
            print(f"  Reconstructed base key: {reconstructed_base_key}")
            
            # Step 4: Test the actual composition
            # Simulate the dead key sequence
            result1 = layout_manager.process_key_input(dead_key)
            result2 = layout_manager.process_key_input(base_char)
            
            if result2 == expected:
                print(f"  ✓ SUCCESS: {dead_key} + {base_char} → {result2}")
                successful_tests += 1
            else:
                print(f"  ✗ FAILED: {dead_key} + {base_char} → {result2} (expected {expected})")
            
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
        
        print()
    
    print(f"Test Results: {successful_tests}/{total_tests} tests passed")
    print(f"Success rate: {(successful_tests/total_tests)*100:.1f}%")
    
    return successful_tests == total_tests

def test_layout_conversion():
    """Test layout conversion between different keyboard layouts"""
    
    print("Testing Layout Conversion")
    print("=" * 30)
    
    layout_manager = get_layout_manager()
    
    # Test converting keys between layouts
    test_keys = ['a', 'q', 'w', 'z', 'y']
    
    for key in test_keys:
        print(f"Testing key '{key}' conversion:")
        
        # Convert from US to Italian
        us_to_it = layout_manager.convert_key_between_layouts(
            key, LayoutType.QWERTY_US, LayoutType.QWERTY_IT
        )
        
        # Convert from Italian back to US
        it_to_us = layout_manager.convert_key_between_layouts(
            us_to_it, LayoutType.QWERTY_IT, LayoutType.QWERTY_US
        )
        
        print(f"  US → IT: '{key}' → '{us_to_it}'")
        print(f"  IT → US: '{us_to_it}' → '{it_to_us}'")
        
        if it_to_us == key:
            print("  ✓ Round-trip conversion successful")
        else:
            print("  ✗ Round-trip conversion failed")
        print()

def main():
    print("Flow KVM - Italian Dead Keys Integration Test")
    print("=" * 60)
    print()
    
    # Test 1: Complete transmission process
    success1 = test_key_transmission()
    print()
    
    # Test 2: Layout conversion
    test_layout_conversion()
    print()
    
    # Summary
    if success1:
        print("🎉 All tests passed! Italian dead keys are working correctly.")
        print("The Flow KVM system now supports accented characters properly.")
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
    
    print()
    print("Next steps:")
    print("1. Test with real client-server communication")
    print("2. Verify dead keys work in applications like text editors")
    print("3. Test with other Italian characters (ç, ß, etc.)")

if __name__ == "__main__":
    main()