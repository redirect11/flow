#!/usr/bin/env python3
"""
Flow KVM Launcher with enhanced error handling and debugging.
"""

import sys
import os
import traceback

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'src'))

def check_dependencies():
    """Check if all required dependencies are available"""
    missing_deps = []
    
    try:
        import PyQt5
        print("✓ PyQt5 available")
    except ImportError:
        missing_deps.append("PyQt5")
    
    try:
        import pynput
        print("✓ pynput available")
    except ImportError:
        missing_deps.append("pynput")
    
    try:
        import numpy
        print("✓ numpy available")
    except ImportError:
        missing_deps.append("numpy")
    
    try:
        import win32clipboard
        print("✓ pywin32 available")
    except ImportError:
        missing_deps.append("pywin32")
    
    if missing_deps:
        print(f"\n❌ Missing dependencies: {', '.join(missing_deps)}")
        print("Install them with: pip install " + " ".join(missing_deps))
        return False
    
    print("\n✅ All dependencies available")
    return True

def test_layout_system():
    """Test the keyboard layout system"""
    try:
        from hardware.keyboard_layout import get_layout_manager
        layout_manager = get_layout_manager()
        layout_info = layout_manager.get_layout_info()
        print(f"✓ Layout system working: {layout_info.layout_name}")
        return True
    except Exception as e:
        print(f"❌ Layout system error: {e}")
        traceback.print_exc()
        return False

def test_database():
    """Test database connectivity"""
    try:
        from data.db import Settings, get_data, set_data
        # Try to read a setting
        pc_setting = get_data(Settings.PC)
        print(f"✓ Database working: PC setting = {pc_setting}")
        
        # Test new layout settings
        layout_setting = get_data(Settings.KEYBOARD_LAYOUT)
        auto_detect = get_data(Settings.LAYOUT_AUTO_DETECT)
        print(f"✓ Layout settings: layout={layout_setting}, auto_detect={auto_detect}")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        traceback.print_exc()
        return False

def main():
    """Main launcher function"""
    print("Flow KVM - Enhanced Launcher")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        input("\nPress Enter to exit...")
        return False
    
    # Test layout system
    if not test_layout_system():
        input("\nPress Enter to exit...")
        return False
    
    # Test database
    if not test_database():
        input("\nPress Enter to exit...")
        return False
    
    print("\n🚀 Starting Flow KVM...")
    
    try:
        # Import and start the main application
        from src import __main__
        print("✅ Flow KVM started successfully!")
        return True
        
    except KeyboardInterrupt:
        print("\n⚠️  Flow KVM interrupted by user")
        return True
        
    except Exception as e:
        print(f"\n❌ Flow KVM startup error: {e}")
        print("\nFull traceback:")
        traceback.print_exc()
        input("\nPress Enter to exit...")
        return False

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)