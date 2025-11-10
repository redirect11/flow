#!/usr/bin/env python3
"""
Test script for the improved keyboard layout system in Flow KVM.
Tests layout detection, key mapping, and conversion between layouts.
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hardware.keyboard_layout import (
    get_layout_manager, LayoutType, KeyInfo, LayoutInfo
)
from hardware.keyboard import (
    create_layout_aware_key_data, key_from_layout_aware_data, 
    get_current_layout_info
)

def test_layout_detection():
    """Test automatic layout detection"""
    print("=== Testing Layout Detection ===")
    
    try:
        layout_manager = get_layout_manager()
        layout_info = layout_manager.get_layout_info()
        
        print(f"Detected Layout: {layout_info.layout_name}")
        print(f"Layout Type: {layout_info.layout_type.value}")
        print(f"Language: {layout_info.language_code}")
        print(f"Country: {layout_info.country_code}")
        print("✓ Layout detection successful")
    except Exception as e:
        print(f"✗ Layout detection failed: {e}")
    
    print()

def test_layout_conversion():
    """Test conversion between different layouts"""
    print("=== Testing Layout Conversion ===")
    
    layout_manager = get_layout_manager()
    
    # Test cases: character in source layout -> expected in target layout
    test_cases = [
        # QWERTY -> AZERTY
        ('a', LayoutType.QWERTY_US, LayoutType.AZERTY_FR, 'q'),  # A key -> Q
        ('q', LayoutType.QWERTY_US, LayoutType.AZERTY_FR, 'a'),  # Q key -> A
        (';', LayoutType.QWERTY_US, LayoutType.AZERTY_FR, 'm'),  # ; key -> M
        
        # QWERTY -> QWERTZ
        ('y', LayoutType.QWERTY_US, LayoutType.QWERTZ_DE, 'z'),  # Y key -> Z
        ('z', LayoutType.QWERTY_US, LayoutType.QWERTZ_DE, 'y'),  # Z key -> Y
        
        # AZERTY -> QWERTZ
        ('a', LayoutType.AZERTY_FR, LayoutType.QWERTZ_DE, 'q'),  # A key (Q phys) -> Q
    ]
    
    print("Testing character conversion between layouts:")
    passed = 0
    total = len(test_cases)
    
    for char, from_layout, to_layout, expected in test_cases:
        try:
            result = layout_manager.convert_key_between_layouts(char, from_layout, to_layout)
            status = "✓" if result == expected else "✗"
            print(f"{status} '{char}' ({from_layout.value}) -> '{result}' ({to_layout.value}) [expected: '{expected}']")
            if result == expected:
                passed += 1
        except Exception as e:
            print(f"✗ Error converting '{char}': {e}")
    
    print(f"\nConversion Tests: {passed}/{total} passed")
    print()

def test_key_data_format():
    """Test the new key data format"""
    print("=== Testing Key Data Format ===")
    
    # Create mock key events
    class MockKey:
        def __init__(self, char=None, name=None):
            if char:
                self.char = char
            if name:
                self.name = name
    
    # Test character key
    char_key = MockKey(char='a')
    try:
        key_data = create_layout_aware_key_data(char_key, physical_code=30)
        print(f"Character key data: {key_data}")
        print("✓ Character key data creation successful")
        
        # Test conversion back
        converted_key = key_from_layout_aware_data(key_data)
        print(f"Converted back to: '{converted_key}'")
        print("✓ Character key conversion successful")
    except Exception as e:
        print(f"✗ Character key test failed: {e}")
    
    # Test special key
    try:
        special_key = MockKey(name='ctrl')
        key_data = create_layout_aware_key_data(special_key, physical_code=29)
        print(f"Special key data: {key_data}")
        print("✓ Special key data creation successful")
        
        # Test conversion back
        converted_key = key_from_layout_aware_data(key_data)
        print(f"Converted back to: {converted_key}")
        print("✓ Special key conversion successful")
    except Exception as e:
        print(f"✗ Special key test failed: {e}")
    
    print()

def test_physical_key_mapping():
    """Test physical key to character mapping"""
    print("=== Testing Physical Key Mapping ===")
    
    layout_manager = get_layout_manager()
    
    # Test some common scancodes
    test_scancodes = [
        (30, 'KEY_A'),  # A key
        (16, 'KEY_Q'),  # Q key  
        (44, 'KEY_Z'),  # Z key
        (39, 'KEY_SEMICOLON'),  # ; key
    ]
    
    print("Testing scancode to character mapping:")
    for scancode, key_name in test_scancodes:
        try:
            # Test in different layouts
            us_char = layout_manager.physical_key_to_char(scancode, LayoutType.QWERTY_US)
            fr_char = layout_manager.physical_key_to_char(scancode, LayoutType.AZERTY_FR)
            de_char = layout_manager.physical_key_to_char(scancode, LayoutType.QWERTZ_DE)
            
            print(f"Scancode {scancode} ({key_name}):")
            print(f"  US QWERTY: '{us_char}'")
            print(f"  FR AZERTY: '{fr_char}'") 
            print(f"  DE QWERTZ: '{de_char}'")
        except Exception as e:
            print(f"✗ Error mapping scancode {scancode}: {e}")
    
    print()

def test_layout_compatibility():
    """Test backward compatibility with old system"""
    print("=== Testing Backward Compatibility ===")
    
    # Test if the system can handle old-style key strings
    from hardware.keyboard import key_from_str
    
    old_style_keys = [
        "Key.ctrl",
        "Key.shift", 
        "Key.enter",
        "'a'",
        "'1'",
        "';'"
    ]
    
    print("Testing old-style key conversion:")
    for key_str in old_style_keys:
        try:
            result = key_from_str(key_str)
            print(f"✓ '{key_str}' -> {result}")
        except Exception as e:
            print(f"✗ Error converting '{key_str}': {e}")
    
    print()

def main():
    """Run all tests"""
    print("Flow KVM - Keyboard Layout System Test")
    print("=" * 50)
    print()
    
    test_layout_detection()
    test_layout_conversion() 
    test_key_data_format()
    test_physical_key_mapping()
    test_layout_compatibility()
    
    print("=" * 50)
    print("Test completed. Check results above.")

if __name__ == "__main__":
    main()