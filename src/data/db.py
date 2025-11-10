"""
Sqlite3 database used to store Settings options and machine locations.
"""
import sqlite3
import os

from src.files import DATABASE


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
    Creates settings and screens table.
    """
    sql_exec(
        f'''CREATE TABLE settings (
                {Settings.IP} text,
                {Settings.PASS} text,
                {Settings.PC} integer,
                {Settings.ENCRYPTION} integer,
                {Settings.KEYBOARD_LAYOUT} text,
                {Settings.LAYOUT_AUTO_DETECT} integer
        )'''
    )

    sql_exec("INSERT INTO settings VALUES (?, ?, ?, ?, ?, ?)",
             (
                 DEFAULTS[Settings.IP],
                 DEFAULTS[Settings.PASS],
                 DEFAULTS[Settings.PC],
                 DEFAULTS[Settings.ENCRYPTION],
                 DEFAULTS[Settings.KEYBOARD_LAYOUT],
                 DEFAULTS[Settings.LAYOUT_AUTO_DETECT],
             )
             )

    sql_exec(
        f'''CREATE TABLE screens (
                address text,
                top text,
                right text,
                bottom text,
                left text
        )'''
    )

    add_screen({Screens.LEFT: None, Screens.TOP: None, Screens.RIGHT: None, Screens.BOTTOM: None}, 'main')


def get_data(elem):
    """
    Gets given element from settings table.
    """
    return sql_exec(f"SELECT {elem} FROM settings")[0][0]


def set_data(elem, data):
    """
    Sets given element from settings table.
    """
    sql_exec(f"UPDATE settings SET {elem}=?", (data,))


def get_all_data():
    """
    Gets all data from settings table.
    """
    data = sql_exec("SELECT * from settings")[0]

    out = DEFAULTS.copy()
    for i, key in enumerate(out):
        out[key] = data[i]

    return out


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
    Upgrades existing database to include new keyboard layout columns.
    """
    try:
        # Check if keyboard layout columns exist
        sql_exec(f"SELECT {Settings.KEYBOARD_LAYOUT} FROM settings LIMIT 1")
        sql_exec(f"SELECT {Settings.LAYOUT_AUTO_DETECT} FROM settings LIMIT 1")
    except sqlite3.OperationalError:
        # Columns don't exist, add them
        try:
            sql_exec(f"ALTER TABLE settings ADD COLUMN {Settings.KEYBOARD_LAYOUT} text DEFAULT '{DEFAULTS[Settings.KEYBOARD_LAYOUT]}'")
        except sqlite3.OperationalError:
            pass  # Column might already exist
        
        try:
            sql_exec(f"ALTER TABLE settings ADD COLUMN {Settings.LAYOUT_AUTO_DETECT} integer DEFAULT {DEFAULTS[Settings.LAYOUT_AUTO_DETECT]}")
        except sqlite3.OperationalError:
            pass  # Column might already exist


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
    create()
else:
    # Database exists, check if it needs upgrading
    upgrade_database()
