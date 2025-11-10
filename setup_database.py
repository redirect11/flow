#!/usr/bin/env python3
"""
Setup script to create database with proper schema
"""

import sys
import os
import sqlite3

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data.db import Settings, upgrade_database

def create_database():
    """Create the database with proper schema"""
    print("Creating Flow KVM database...")
    
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()
    
    # Create configuration table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuration (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')
    
    # Insert default values
    defaults = [
        (Settings.IP, ''),
        (Settings.PASS, ''),
        (Settings.PC, '1'),
        (Settings.ENCRYPTION, '1'),
        (Settings.KEYBOARD_LAYOUT, 'auto'),
        (Settings.LAYOUT_AUTO_DETECT, '1')
    ]
    
    cursor.executemany('INSERT OR IGNORE INTO configuration (key, value) VALUES (?, ?)', defaults)
    
    conn.commit()
    conn.close()
    
    print("✓ Database created successfully")
    
    # Run upgrade to ensure all new fields are present
    upgrade_database()
    print("✓ Database upgraded to latest schema")

if __name__ == "__main__":
    create_database()