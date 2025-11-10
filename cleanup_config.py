#!/usr/bin/env python3
"""
Flow KVM Configuration Cleanup Script
Removes all configuration files, databases, and temporary files.
"""

import os
import sys
import shutil
import tempfile
import glob
from pathlib import Path

def get_database_path():
    """Get the database file path based on platform"""
    if sys.platform == 'win32':
        return os.path.join(os.getenv('APPDATA'), 'flow.db')
    else:
        return 'flow.db'

def get_temp_directories():
    """Get temporary directories that might contain Flow files"""
    temp_dirs = []
    
    # System temp directory
    temp_dir = tempfile.gettempdir()
    flow_temp = os.path.join(temp_dir, "flow")
    if os.path.exists(flow_temp):
        temp_dirs.append(flow_temp)
    
    # Windows specific temp locations
    if sys.platform == 'win32':
        # Local AppData temp
        local_appdata = os.getenv('LOCALAPPDATA')
        if local_appdata:
            flow_local = os.path.join(local_appdata, 'flow')
            if os.path.exists(flow_local):
                temp_dirs.append(flow_local)
    
    return temp_dirs

def cleanup_config_files():
    """Remove all Flow KVM configuration and temporary files"""
    
    files_removed = []
    dirs_removed = []
    errors = []
    
    print("Flow KVM Configuration Cleanup")
    print("=" * 40)
    
    # 1. Remove main database file
    db_path = get_database_path()
    print(f"\n1. Checking main database: {db_path}")
    
    if os.path.exists(db_path):
        try:
            os.remove(db_path)
            files_removed.append(db_path)
            print(f"   ✓ Removed: {db_path}")
        except Exception as e:
            errors.append(f"Failed to remove {db_path}: {e}")
            print(f"   ✗ Failed to remove: {e}")
    else:
        print(f"   - Not found: {db_path}")
    
    # 2. Remove local database file (if exists in project directory)
    local_db = os.path.join(os.getcwd(), 'flow.db')
    print(f"\n2. Checking local database: {local_db}")
    
    if os.path.exists(local_db):
        try:
            os.remove(local_db)
            files_removed.append(local_db)
            print(f"   ✓ Removed: {local_db}")
        except Exception as e:
            errors.append(f"Failed to remove {local_db}: {e}")
            print(f"   ✗ Failed to remove: {e}")
    else:
        print(f"   - Not found: {local_db}")
    
    # 3. Remove temporary directories
    temp_dirs = get_temp_directories()
    print(f"\n3. Checking temporary directories:")
    
    if not temp_dirs:
        print("   - No temporary directories found")
    
    for temp_dir in temp_dirs:
        print(f"   Checking: {temp_dir}")
        if os.path.exists(temp_dir):
            try:
                shutil.rmtree(temp_dir)
                dirs_removed.append(temp_dir)
                print(f"   ✓ Removed directory: {temp_dir}")
            except Exception as e:
                errors.append(f"Failed to remove directory {temp_dir}: {e}")
                print(f"   ✗ Failed to remove directory: {e}")
        else:
            print(f"   - Directory not found")
    
    # 4. Look for any other Flow-related files in temp
    print(f"\n4. Checking for other Flow files in temp:")
    temp_dir = tempfile.gettempdir()
    flow_files = glob.glob(os.path.join(temp_dir, "*flow*"))
    
    if not flow_files:
        print("   - No additional Flow files found in temp")
    
    for file_path in flow_files:
        print(f"   Found: {file_path}")
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                files_removed.append(file_path)
                print(f"   ✓ Removed file: {file_path}")
            elif os.path.isdir(file_path):
                shutil.rmtree(file_path)
                dirs_removed.append(file_path)
                print(f"   ✓ Removed directory: {file_path}")
        except Exception as e:
            errors.append(f"Failed to remove {file_path}: {e}")
            print(f"   ✗ Failed to remove: {e}")
    
    # 5. Windows Registry cleanup (optional)
    if sys.platform == 'win32':
        print(f"\n5. Windows Registry (manual cleanup needed):")
        print("   Flow KVM may have created registry entries.")
        print("   Check HKCU\\Software for any Flow entries if needed.")
    
    # 6. Check for process locks
    print(f"\n6. Checking for running Flow processes:")
    try:
        import psutil
        flow_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = ' '.join(proc.info['cmdline'] or [])
                if 'flow' in cmdline.lower() or 'flow.py' in cmdline.lower():
                    flow_processes.append(f"PID {proc.info['pid']}: {proc.info['name']}")
            except:
                pass
        
        if flow_processes:
            print("   ⚠️  Found running Flow processes:")
            for proc in flow_processes:
                print(f"      {proc}")
            print("   Please stop these processes before cleanup.")
        else:
            print("   ✓ No running Flow processes found")
            
    except ImportError:
        print("   - Could not check for running processes (psutil not available)")
    
    # Summary
    print("\n" + "=" * 40)
    print("CLEANUP SUMMARY:")
    print("=" * 40)
    
    if files_removed:
        print(f"\n✓ Files removed ({len(files_removed)}):")
        for file_path in files_removed:
            print(f"  - {file_path}")
    
    if dirs_removed:
        print(f"\n✓ Directories removed ({len(dirs_removed)}):")
        for dir_path in dirs_removed:
            print(f"  - {dir_path}")
    
    if errors:
        print(f"\n✗ Errors ({len(errors)}):")
        for error in errors:
            print(f"  - {error}")
    
    if not files_removed and not dirs_removed and not errors:
        print("\n✓ No configuration files found - system is already clean!")
    
    print(f"\nCleanup completed!")
    
    # Ask if user wants to restart with fresh config
    if files_removed or dirs_removed:
        print(f"\nTo verify cleanup worked:")
        print(f"1. Restart Flow KVM: python launch_flow.py")
        print(f"2. New database will be created with default settings")
        print(f"3. Configure as server or client from scratch")

def main():
    """Main cleanup function"""
    
    print("This will remove ALL Flow KVM configuration and data files.")
    print("This includes:")
    print("- Database with all settings and screen configurations")
    print("- Temporary files")
    print("- Cached data")
    print()
    
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        cleanup_config_files()
    else:
        print("Cleanup cancelled.")

if __name__ == "__main__":
    main()