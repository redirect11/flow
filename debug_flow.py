#!/usr/bin/env python3
"""
Flow KVM Debug Launcher - Enhanced debugging for server startup issues
"""

import sys
import os
import traceback
import threading
import time

# Add src directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(script_dir, 'src'))

def test_server_components():
    """Test individual server components to identify the issue"""
    print("\n🔍 Testing Server Components:")
    print("=" * 50)
    
    # Test 1: Import core modules
    try:
        print("1. Testing core imports...")
        import src.info.computerinfo as computerinfo
        import src.network.sockets as socket
        from src.data.db import Settings, get_data
        print("   ✓ Core modules imported successfully")
    except Exception as e:
        print(f"   ✗ Core import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 2: Test UI components
    try:
        print("2. Testing UI components...")
        from src.ui.components import app
        print("   ✓ QApplication created")
    except Exception as e:
        print(f"   ✗ UI component failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 3: Test server class
    try:
        print("3. Testing server class...")
        from src.comms.server import Server
        print("   ✓ Server class imported")
    except Exception as e:
        print(f"   ✗ Server import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 4: Test client class  
    try:
        print("4. Testing client class...")
        from src.comms.client import Client
        print("   ✓ Client class imported")
    except Exception as e:
        print(f"   ✗ Client import failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 5: Test network components
    try:
        print("5. Testing network components...")
        from src.network.sockets import set_encryption_key
        print("   ✓ Network components working")
    except Exception as e:
        print(f"   ✗ Network component failed: {e}")
        traceback.print_exc()
        return False
    
    # Test 6: Test transfer components
    try:
        print("6. Testing transfer components...")
        from src.comms.transfer import SharedDevices, ControlledDevices
        print("   ✓ Transfer components working")
    except Exception as e:
        print(f"   ✗ Transfer component failed: {e}")
        traceback.print_exc()
        return False
    
    return True

def test_server_creation():
    """Test actual server creation"""
    print("\n🖥️ Testing Server Creation:")
    print("=" * 50)
    
    try:
        from src.comms.server import Server
        from src.data.db import Settings, get_data
        
        print("1. Attempting to create server instance...")
        
        # Clear any existing machines
        Server.machines.clear()
        server = Server()
        
        print("   ✓ Server instance created")
        
        # Test server start (briefly)
        print("2. Testing server start...")
        server.start()
        
        # Wait a moment to see if it starts
        time.sleep(2)
        
        if server.isRunning():
            print("   ✓ Server started successfully")
            server.stop()
            server.wait(1000)  # Wait up to 1 second for clean shutdown
            print("   ✓ Server stopped cleanly")
            return True
        else:
            print("   ✗ Server failed to start")
            return False
            
    except Exception as e:
        print(f"   ✗ Server creation/start failed: {e}")
        traceback.print_exc()
        return False

def test_tray_icon():
    """Test tray icon creation"""
    print("\n🔔 Testing Tray Icon:")
    print("=" * 50)
    
    try:
        from src.ui.components import tray_icon
        print("1. Tray icon imported...")
        
        # Test showing tray icon
        tray_icon.show()
        print("   ✓ Tray icon show() called")
        
        # Check if it's visible
        time.sleep(1)
        print("   ✓ Tray icon should be visible")
        
        return True
    except Exception as e:
        print(f"   ✗ Tray icon failed: {e}")
        traceback.print_exc()
        return False

def debug_main():
    """Debug version of the main function"""
    print("Flow KVM - Debug Mode")
    print("=" * 50)
    
    # Test components step by step
    if not test_server_components():
        print("\n❌ Component test failed - stopping")
        return False
    
    if not test_server_creation():
        print("\n❌ Server creation failed - stopping")
        return False
    
    if not test_tray_icon():
        print("\n❌ Tray icon failed - stopping")
        return False
    
    print("\n✅ All tests passed - attempting full startup...")
    
    try:
        # Import the main application
        print("\n🚀 Starting full Flow KVM application...")
        
        # Set up main app components step by step
        from src.ui.components import app, settings, tray_icon, blocker
        from src.comms.server import Server
        from src.comms.client import Client
        from src.data.db import Settings, get_data, get_all_data
        import src.network.sockets as socket
        
        print("1. ✓ All components imported")
        
        # Create a simple main class for debugging
        class DebugMain:
            def __init__(self):
                print("2. Setting up event handlers...")
                
                # Set up event handlers
                settings.onSave(self.save)
                tray_icon.onSettings(self.open_settings)
                tray_icon.onExit(self.exit_flow)
                
                print("3. ✓ Event handlers set")
                
                # Show tray icon
                print("4. Showing tray icon...")
                tray_icon.show()
                
                print("5. ✓ Tray icon shown")
                
                # Initialize server/client
                print("6. Initializing server/client...")
                self.serverclient = None
                typ = get_data(Settings.PC)
                
                print(f"7. Mode: {'Server' if typ == Settings.SERVER else 'Client'}")
                
                self.init_serverclient(typ)
                
                print("8. ✓ Server/client initialized")
                
                # Start the Qt event loop
                print("9. Starting Qt application...")
                print("\n🎉 Flow KVM started successfully!")
                print("Check your system tray for the Flow icon.")
                print("Right-click the icon to access settings.")
                print("\nPress Ctrl+C to stop...\n")
                
                sys.exit(app.exec_())
            
            def init_serverclient(self, typ):
                if typ == Settings.CLIENT:
                    print("   Creating client...")
                    self.serverclient = Client()
                else:
                    print("   Creating server...")
                    Server.machines.clear()
                    self.serverclient = Server()
                    
                print("   Setting up encryption...")
                if get_data(Settings.ENCRYPTION) == Settings.ENCRYPTION_ON:
                    socket.key = socket.set_encryption_key(get_data(Settings.PASS))
                else:
                    socket.key = socket.set_encryption_key("")
                
                print("   Starting server/client thread...")
                self.serverclient.start()
                print("   ✓ Server/client started")
            
            def save(self):
                print("Save called")
                settings.update()
                settings.hide()
                
            def open_settings(self):
                print("Settings opened")
                settings.show()
            
            def exit_flow(self):
                print("Exit called")
                if self.serverclient is not None:
                    self.serverclient.stop()
                    self.serverclient.wait()
                tray_icon.hide()
                app.quit()
        
        # Start the debug main
        debug_main = DebugMain()
        
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        return True
    except Exception as e:
        print(f"\n❌ Startup failed: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        success = debug_main()
        if not success:
            input("\nPress Enter to exit...")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nShutting down...")
        sys.exit(0)