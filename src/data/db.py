"""
NEW DATABASE MODULE - Sqlite3 database used to store Settings options and machine locations.
"""
import sqlite3
import os

from src.files import DATABASE

print(f"=== NEW DB MODULE LOADED - DATABASE PATH: {DATABASE} ===")


class Settings:
    """
    Setting constants
    """
    PC = 'pc'
    PASS = 'password'
    IP = 'IP'
    ENCRYPTION = 'encryption'
    KEYBOARD_LAYOUT = 'keyboard_layout'
    LAYOUT_AUTO_DETECT = 'layout_auto_detect'

    SERVER = 1
    CLIENT = 0
    ENCRYPTION_ON = 1
    ENCRYPTION_OFF = 0
    LAYOUT_AUTO_ON = 1
    LAYOUT_AUTO_OFF = 0


class Screens:
    """
    Screen constants
    """
    TOP = 0
    BOTTOM = 3
    RIGHT = 1
    LEFT = 2

    @staticmethod
    def oppo(side):
        """
        Opposite side. ex: TOP -> BOTTOM, BOTTOM -> TOP
        f(x) = -x + 3
        """
        return -side + 3


# default settings
DEFAULTS = {
    Settings.IP: "",
    Settings.PASS: "",
    Settings.PC: Settings.SERVER,
    Settings.ENCRYPTION: Settings.ENCRYPTION_OFF,
    Settings.KEYBOARD_LAYOUT: "qwerty_us",
    Settings.LAYOUT_AUTO_DETECT: Settings.LAYOUT_AUTO_ON
}


def sql_exec(*args, **kwargs):
    """
    Excecutes sqlite command.
    """
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()

    c.execute(*args, **kwargs)
    returned_data = c.fetchall()

    conn.commit()
    conn.close()
    return returned_data


def create():
    """
    Creates CONFIGURATION and screens table with modern schema.
    """
    print("=== CREATING NEW DATABASE WITH CONFIGURATION TABLE ===")
    
    # Create configuration table (modern key-value schema)
    sql_exec('''
        CREATE TABLE configuration (
            key TEXT PRIMARY KEY,
            value TEXT
        )
    ''')

    # Insert default configuration values
    for setting_key, default_value in DEFAULTS.items():
        sql_exec("INSERT INTO configuration (key, value) VALUES (?, ?)", 
                (setting_key, str(default_value)))

    sql_exec(
        '''CREATE TABLE screens (
                address text,
                top text,
                right text,
                bottom text,
                left text
        )'''
    )

    add_screen({Screens.LEFT: None, Screens.TOP: None, Screens.RIGHT: None, Screens.BOTTOM: None}, 'main')
    print("=== CONFIGURATION TABLE DATABASE CREATED ===")


def table_exists(table_name):
    """
    Check if a table exists in the database
    """
    result = sql_exec(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return len(result) > 0


def get_data(elem):
    """
    Gets given element from configuration table (preferred) or settings table (legacy).
    """
    if table_exists('configuration'):
        # Use modern configuration table
        result = sql_exec("SELECT value FROM configuration WHERE key=?", (elem,))
        if result:
            value = result[0][0]
            # Convert string values back to appropriate types for legacy compatibility
            if elem in [Settings.PC, Settings.ENCRYPTION, Settings.LAYOUT_AUTO_DETECT]:
                try:
                    return int(value)
                except (ValueError, TypeError):
                    return DEFAULTS.get(elem, 0)
            return value
        else:
            return DEFAULTS.get(elem)
    else:
        # Fall back to legacy settings table
        try:
            return sql_exec(f"SELECT {elem} FROM settings")[0][0]
        except (sqlite3.OperationalError, IndexError):
            return DEFAULTS.get(elem)


def set_data(elem, data):
    """
    Sets given element in configuration table (preferred) or settings table (legacy).
    """
    if table_exists('configuration'):
        # Use modern configuration table
        sql_exec("INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)", (elem, str(data)))
    else:
        # Fall back to legacy settings table
        try:
            sql_exec(f"UPDATE settings SET {elem}=?", (data,))
        except sqlite3.OperationalError:
            # If settings table doesn't exist or column doesn't exist, upgrade the database
            upgrade_database()
            sql_exec("INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)", (elem, str(data)))


def get_all_data():
    """
    Gets all data from configuration table (preferred) or settings table (legacy).
    """
    if table_exists('configuration'):
        # Use modern configuration table
        config_data = sql_exec("SELECT key, value FROM configuration")
        out = DEFAULTS.copy()
        
        for key, value in config_data:
            if key in out:
                # Convert string values back to appropriate types
                if key in [Settings.PC, Settings.ENCRYPTION, Settings.LAYOUT_AUTO_DETECT]:
                    try:
                        out[key] = int(value)
                    except (ValueError, TypeError):
                        out[key] = DEFAULTS[key]
                else:
                    out[key] = value
        
        return out
    else:
        # Fall back to legacy settings table
        try:
            data = sql_exec("SELECT * from settings")[0]
            out = DEFAULTS.copy()
            for i, key in enumerate(out):
                if i < len(data):
                    out[key] = data[i]
            return out
        except (sqlite3.OperationalError, IndexError):
            return DEFAULTS.copy()


def get_screen(name):
    """
    Gets screen from screens table.
    """
    try:
        screen = sql_exec(f"SELECT * FROM screens WHERE address=?", (name,))[0]
    except IndexError:
        return
    return screen


def get_attachments(name):
    """
    Gets attachments of given screen name.
    Adds screen with given name if not found.
    """
    screen = get_screen(name)
    if screen is None:
        attachments = {Screens.TOP: None, Screens.RIGHT: None, Screens.LEFT: None, Screens.BOTTOM: None}
        add_screen(attachments, name)
        # settings.update_view()
    else:
        attachments = {
            Screens.TOP: screen[1],
            Screens.RIGHT: screen[2],
            Screens.BOTTOM: screen[3],
            Screens.LEFT: screen[4]
        }
    return attachments


def get_screens():
    """
    Gets all screens from screens table.
    """
    screens = sql_exec("SELECT * from screens")
    return screens


def add_screen(attachments, name):
    """
    Adds screen to screens table.
    """
    sql_exec(
        "INSERT INTO screens VALUES (?, ?, ?, ?, ?)",
        (
            name,
            attachments[Screens.TOP],
            attachments[Screens.RIGHT],
            attachments[Screens.BOTTOM],
            attachments[Screens.LEFT]
        )
    )


def update_screen(attachments, address):
    """
    Updates screen from screens table.
    """
    sql_exec(
        "UPDATE screens SET top=?, right=?, bottom=?, left=? WHERE address=?",
        (
            attachments[Screens.TOP],
            attachments[Screens.RIGHT],
            attachments[Screens.BOTTOM],
            attachments[Screens.LEFT],
            address
        )
    )


def upgrade_database():
    """
    Upgrades existing database from legacy settings table to modern configuration table.
    """
    if table_exists('settings') and not table_exists('configuration'):
        print("Upgrading database schema from 'settings' to 'configuration' table...")
        
        # Create new configuration table
        sql_exec('''
            CREATE TABLE configuration (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        # Migrate data from settings table
        try:
            # Try to get data from settings table
            settings_data = sql_exec("SELECT * FROM settings")
            if settings_data:
                row = settings_data[0]
                
                # Map columns to keys based on table schema
                # The order should match the original CREATE TABLE statement:
                # IP, password, pc, encryption, keyboard_layout, layout_auto_detect
                column_mapping = [
                    Settings.IP,
                    Settings.PASS, 
                    Settings.PC,
                    Settings.ENCRYPTION,
                    Settings.KEYBOARD_LAYOUT,
                    Settings.LAYOUT_AUTO_DETECT
                ]
                
                # Migrate each column to configuration table
                for i, setting_key in enumerate(column_mapping):
                    if i < len(row) and row[i] is not None:
                        value = str(row[i])
                    else:
                        value = str(DEFAULTS[setting_key])
                    
                    sql_exec("INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)", 
                            (setting_key, value))
                
                print("✓ Successfully migrated settings to configuration table")
            else:
                # Settings table is empty, use defaults
                for key, value in DEFAULTS.items():
                    sql_exec("INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)", 
                            (key, str(value)))
                
        except (sqlite3.OperationalError, IndexError) as e:
            print(f"Warning: Could not migrate settings table: {e}")
            # If migration fails, create with defaults
            for key, value in DEFAULTS.items():
                sql_exec("INSERT OR REPLACE INTO configuration (key, value) VALUES (?, ?)", 
                        (key, str(value)))
    
    elif table_exists('settings') and table_exists('configuration'):
        # Both tables exist, ensure configuration has all required keys
        for key, default_value in DEFAULTS.items():
            result = sql_exec("SELECT value FROM configuration WHERE key=?", (key,))
            if not result:
                sql_exec("INSERT INTO configuration (key, value) VALUES (?, ?)", 
                        (key, str(default_value)))
    
    elif not table_exists('configuration'):
        # No configuration table exists, create it with defaults
        sql_exec('''
            CREATE TABLE configuration (
                key TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        
        for key, value in DEFAULTS.items():
            sql_exec("INSERT INTO configuration (key, value) VALUES (?, ?)", 
                    (key, str(value)))


def remove_screen(address):
    """
    Removes screen from screens table.
    """
    sql_exec(
        "DELETE from screens WHERE address=?",
        (
            address,
        )
    )


if not os.path.isfile(DATABASE):
    print(f"Database file {DATABASE} does not exist, calling create()...")
    create()
    print("create() function completed")
else:
    print(f"Database file {DATABASE} already exists, calling upgrade_database()...")
    # Database exists, check if it needs upgrading
    upgrade_database()
    print("upgrade_database() completed")