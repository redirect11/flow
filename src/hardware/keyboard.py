"""
Constants for string to pynput Key conversion +
keyboard functions with layout-aware support
"""

from pynput.keyboard import Key, Listener as KeyboardListener, Controller as KeyboardController

import src.info.computerinfo as ci
from .keyboard_layout import get_layout_manager, KeyInfo, LayoutType

kbuttons = {
    'Key.alt': Key.alt,
    'Key.alt_l': Key.alt_l,
    'Key.alt_r': Key.alt_r,
    'Key.alt_gr': Key.alt_gr,
    'Key.backspace': Key.backspace,
    'Key.caps_lock': Key.caps_lock,
    'Key.cmd': Key.cmd,
    'Key.cmd_l': Key.cmd_l,
    'Key.cmd_r': Key.cmd_r,
    'Key.ctrl': Key.ctrl,
    'Key.ctrl_l': Key.ctrl_l,
    'Key.ctrl_r': Key.ctrl_r,
    'Key.delete': Key.delete,
    'Key.down': Key.down,
    'Key.end': Key.end,
    'Key.enter': Key.enter,
    'Key.esc': Key.esc,
    'Key.f1': Key.f1,
    'Key.f2': Key.f2,
    'Key.f3': Key.f3,
    'Key.f4': Key.f4,
    'Key.f5': Key.f5,
    'Key.f6': Key.f6,
    'Key.f7': Key.f7,
    'Key.f8': Key.f8,
    'Key.f9': Key.f9,
    'Key.f10': Key.f10,
    'Key.f11': Key.f11,
    'Key.f12': Key.f12,
    'Key.f13': Key.f13,
    'Key.f14': Key.f14,
    'Key.f15': Key.f15,
    'Key.f16': Key.f16,
    'Key.f17': Key.f17,
    'Key.f18': Key.f18,
    'Key.f19': Key.f19,
    'Key.f20': Key.f20,
    'Key.home': Key.home,
    'Key.left': Key.left,
    'Key.page_down': Key.page_down,
    'Key.page_up': Key.page_up,
    'Key.right': Key.right,
    'Key.shift': Key.shift,
    'Key.shift_l': Key.shift_l,
    'Key.shift_r': Key.shift_r,
    'Key.space': Key.space,
    'Key.tab': Key.tab,
    'Key.up': Key.up,
    'Key.media_play_pause': Key.media_play_pause,
    'Key.media_volume_mute': Key.media_volume_mute,
    'Key.media_volume_down': Key.media_volume_down,
    'Key.media_volume_up': Key.media_volume_up,
    'Key.media_previous': Key.media_previous,
    'Key.media_next': Key.media_next,
}

if ci.platform != ci.MACOS:
    kbuttons['key.insert'] = Key.insert
    kbuttons['Key.menu'] = Key.menu
    kbuttons['Key.num_lock'] = Key.num_lock
    kbuttons['key.print_screen'] = Key.print_screen
    kbuttons['key.scroll_lock'] = Key.scroll_lock


def key_from_str(key):
    """
    Legacy function for backward compatibility.
    Converts string representation to pynput Key.
    """
    if key.startswith("Key."):
        return kbuttons[key]
    else:
        return key[1:-1][0]


def create_layout_aware_key_data(pynput_key, physical_code=None):
    """
    Create layout-aware key data from pynput key event.
    Returns a dictionary containing both physical and logical key information.
    """
    layout_manager = get_layout_manager()
    key_info = layout_manager.create_key_info(pynput_key, physical_code)
    
    # For special keys, use the existing mapping
    if hasattr(pynput_key, 'name'):
        key_type = 'special'
        key_data = {
            'type': key_type,
            'key_name': f"Key.{pynput_key.name}",
            'physical_code': physical_code or 0,
            'layout_type': layout_manager.current_layout.layout_type.value
        }
    else:
        # For character keys, include layout information
        key_type = 'character'
        key_data = {
            'type': key_type,
            'physical_code': physical_code or 0,
            'logical_char': key_info.logical_char,
            'key_name': key_info.key_name,
            'layout_type': layout_manager.current_layout.layout_type.value,
            'language_code': layout_manager.current_layout.language_code,
            'country_code': layout_manager.current_layout.country_code
        }
    
    return key_data


def key_from_layout_aware_data(key_data, target_layout_type=None):
    """
    Convert layout-aware key data back to pynput Key or character.
    Handles layout conversion if target layout is different from source.
    """
    layout_manager = get_layout_manager()
    
    if key_data['type'] == 'special':
        # Special keys are layout-independent
        key_name = key_data['key_name']
        if key_name in kbuttons:
            return kbuttons[key_name]
        else:
            return None
    
    elif key_data['type'] == 'character':
        source_layout = LayoutType(key_data['layout_type'])
        target_layout = target_layout_type or layout_manager.current_layout.layout_type
        
        if source_layout == target_layout:
            # Same layout, use original character
            return key_data['logical_char']
        else:
            # Different layouts, convert using physical key mapping
            converted_char = layout_manager.convert_key_between_layouts(
                key_data['logical_char'], 
                source_layout, 
                target_layout
            )
            return converted_char
    
    return None


def get_current_layout_info():
    """Get information about the current keyboard layout"""
    layout_manager = get_layout_manager()
    return layout_manager.get_layout_info()


def set_target_layout(layout_type):
    """Set the target layout type for key conversion"""
    # This could be stored in a global variable or configuration
    # For now, it's just a placeholder for future implementation
    pass
