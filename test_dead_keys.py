#!/usr/bin/env python3
"""
Test script for Italian dead keys functionality
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from hardware.keyboard import test_dead_key_support, get_layout_manager
from hardware.keyboard_layout import LayoutType

def main():
    print("Testing Italian Dead Keys Support")
    print("=" * 40)
    
    # Get layout manager
    layout_manager = get_layout_manager()
    
    # Force Italian layout for testing
    layout_manager.set_layout_type(LayoutType.QWERTY_IT)
    
    print(f"Current layout: {layout_manager.current_layout.layout_type.value}")
    print(f"Language: {layout_manager.current_layout.language_code}")
    print(f"Country: {layout_manager.current_layout.country_code}")
    print()
    
    # Test dead key functionality
    test_dead_key_support()
    
    print("\n" + "=" * 40)
    print("Manual testing:")
    print("Try typing these sequences:")
    print("  ` + a = à")
    print("  ' + e = é")
    print("  ^ + i = î")
    print("  ~ + n = ñ")
    print("  ¨ + u = ü")
    
    # Manual test interface
    print("\nEnter dead key combinations (or 'quit' to exit):")
    while True:
        try:
            user_input = input("Enter character: ").strip()
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            
            if user_input:
                result = layout_manager.process_key_input(user_input)
                if result and result != user_input:
                    print(f"Result: {result}")
                else:
                    print(f"No composition for: {user_input}")
        
        except KeyboardInterrupt:
            break
    
    print("Test completed.")

if __name__ == "__main__":
    main()