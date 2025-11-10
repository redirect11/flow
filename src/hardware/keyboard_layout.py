"""
Keyboard layout detection and management for cross-platform KVM software.
Handles different keyboard layouts and provides mapping between physical keys
and their representations across different systems.
"""

import sys
import platform
from typing import Dict, Optional, Tuple, Any, List
from dataclasses import dataclass
from enum import Enum
import locale

try:
    from pynput.keyboard import Key
except ImportError:
    Key = None

import src.info.computerinfo as ci


class LayoutType(Enum):
    """Common keyboard layout types"""
    QWERTY_US = "qwerty_us"
    QWERTY_UK = "qwerty_uk"
    QWERTY_IT = "qwerty_it"
    AZERTY_FR = "azerty_fr"
    QWERTZ_DE = "qwertz_de"
    QWERTZ_CH = "qwertz_ch"
    DVORAK = "dvorak"
    COLEMAK = "colemak"
    UNKNOWN = "unknown"


@dataclass
class DeadKeySequence:
    """Represents a dead key + character sequence"""
    dead_key: str       # The dead key character (`, ', ^, ~, ")
    base_char: str      # The base character (a, e, i, o, u, etc.)
    result_char: str    # The resulting accented character (à, é, î, õ, ü, etc.)


@dataclass
class KeyInfo:
    """Information about a key press including physical and logical representation"""
    physical_code: int  # Scancode or keycode (hardware independent)
    logical_char: str   # Character produced by the key in current layout
    key_name: str      # Name of the physical key (e.g., 'KEY_A', 'KEY_SEMICOLON')
    modifiers: int     # Modifier state (Shift, Ctrl, Alt, etc.)


@dataclass
class LayoutInfo:
    """Information about the current keyboard layout"""
    layout_type: LayoutType
    language_code: str  # ISO language code (e.g., 'en', 'fr', 'de')
    country_code: str   # ISO country code (e.g., 'US', 'FR', 'DE')
    layout_name: str    # Full layout name


class KeyboardLayoutManager:
    """
    Manages keyboard layout detection and key mapping across different layouts.
    Provides unified interface for handling keyboard events regardless of layout.
    """
    
    def __init__(self):
        self.current_layout: Optional[LayoutInfo] = None
        self.layout_maps = self._initialize_layout_maps()
        self.physical_key_names = self._initialize_physical_keys()
        self.dead_key_combinations = self._initialize_dead_key_combinations()
        self.pending_dead_key: Optional[str] = None  # Track pending dead key
        self._detect_current_layout()
    
    def _initialize_dead_key_combinations(self) -> Dict[LayoutType, List[DeadKeySequence]]:
        """Initialize dead key combinations for different layouts"""
        return {
            LayoutType.QWERTY_IT: [
                # Grave accent (`)
                DeadKeySequence('`', 'a', 'à'), DeadKeySequence('`', 'e', 'è'),
                DeadKeySequence('`', 'i', 'ì'), DeadKeySequence('`', 'o', 'ò'),
                DeadKeySequence('`', 'u', 'ù'),
                DeadKeySequence('`', 'A', 'À'), DeadKeySequence('`', 'E', 'È'),
                DeadKeySequence('`', 'I', 'Ì'), DeadKeySequence('`', 'O', 'Ò'),
                DeadKeySequence('`', 'U', 'Ù'),
                
                # Acute accent (')
                DeadKeySequence("'", 'a', 'á'), DeadKeySequence("'", 'e', 'é'),
                DeadKeySequence("'", 'i', 'í'), DeadKeySequence("'", 'o', 'ó'),
                DeadKeySequence("'", 'u', 'ú'),
                DeadKeySequence("'", 'A', 'Á'), DeadKeySequence("'", 'E', 'É'),
                DeadKeySequence("'", 'I', 'Í'), DeadKeySequence("'", 'O', 'Ó'),
                DeadKeySequence("'", 'U', 'Ú'),
                
                # Circumflex (^)
                DeadKeySequence('^', 'a', 'â'), DeadKeySequence('^', 'e', 'ê'),
                DeadKeySequence('^', 'i', 'î'), DeadKeySequence('^', 'o', 'ô'),
                DeadKeySequence('^', 'u', 'û'),
                DeadKeySequence('^', 'A', 'Â'), DeadKeySequence('^', 'E', 'Ê'),
                DeadKeySequence('^', 'I', 'Î'), DeadKeySequence('^', 'O', 'Ô'),
                DeadKeySequence('^', 'U', 'Û'),
                
                # Tilde (~)
                DeadKeySequence('~', 'a', 'ã'), DeadKeySequence('~', 'n', 'ñ'),
                DeadKeySequence('~', 'o', 'õ'),
                DeadKeySequence('~', 'A', 'Ã'), DeadKeySequence('~', 'N', 'Ñ'),
                DeadKeySequence('~', 'O', 'Õ'),
                
                # Diaeresis/Umlaut (")
                DeadKeySequence('"', 'a', 'ä'), DeadKeySequence('"', 'e', 'ë'),
                DeadKeySequence('"', 'i', 'ï'), DeadKeySequence('"', 'o', 'ö'),
                DeadKeySequence('"', 'u', 'ü'),
                DeadKeySequence('"', 'A', 'Ä'), DeadKeySequence('"', 'E', 'Ë'),
                DeadKeySequence('"', 'I', 'Ï'), DeadKeySequence('"', 'O', 'Ö'),
                DeadKeySequence('"', 'U', 'Ü'),
            ],
            # Add other layouts here as needed
            LayoutType.AZERTY_FR: [
                # French dead keys...
                DeadKeySequence('^', 'a', 'â'), DeadKeySequence('^', 'e', 'ê'),
                DeadKeySequence('^', 'i', 'î'), DeadKeySequence('^', 'o', 'ô'),
                DeadKeySequence('^', 'u', 'û'),
            ]
        }
    
    def _initialize_layout_maps(self) -> Dict[LayoutType, Dict[str, str]]:
        """Initialize mapping tables for different keyboard layouts"""
        return {
            LayoutType.QWERTY_US: {
                # Mapping from physical key name to character for US QWERTY
                'KEY_Q': 'q', 'KEY_W': 'w', 'KEY_E': 'e', 'KEY_R': 'r', 'KEY_T': 't',
                'KEY_Y': 'y', 'KEY_U': 'u', 'KEY_I': 'i', 'KEY_O': 'o', 'KEY_P': 'p',
                'KEY_A': 'a', 'KEY_S': 's', 'KEY_D': 'd', 'KEY_F': 'f', 'KEY_G': 'g',
                'KEY_H': 'h', 'KEY_J': 'j', 'KEY_K': 'k', 'KEY_L': 'l',
                'KEY_Z': 'z', 'KEY_X': 'x', 'KEY_C': 'c', 'KEY_V': 'v', 'KEY_B': 'b',
                'KEY_N': 'n', 'KEY_M': 'm',
                'KEY_SEMICOLON': ';', 'KEY_APOSTROPHE': "'", 'KEY_COMMA': ',',
                'KEY_PERIOD': '.', 'KEY_SLASH': '/', 'KEY_BACKSLASH': '\\',
                'KEY_LEFTBRACE': '[', 'KEY_RIGHTBRACE': ']', 'KEY_GRAVE': '`',
                'KEY_MINUS': '-', 'KEY_EQUAL': '=',
                # Numbers
                'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
                'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
            },
            LayoutType.AZERTY_FR: {
                # Mapping for French AZERTY layout
                'KEY_Q': 'a', 'KEY_W': 'z', 'KEY_E': 'e', 'KEY_R': 'r', 'KEY_T': 't',
                'KEY_Y': 'y', 'KEY_U': 'u', 'KEY_I': 'i', 'KEY_O': 'o', 'KEY_P': 'p',
                'KEY_A': 'q', 'KEY_S': 's', 'KEY_D': 'd', 'KEY_F': 'f', 'KEY_G': 'g',
                'KEY_H': 'h', 'KEY_J': 'j', 'KEY_K': 'k', 'KEY_L': 'l',
                'KEY_Z': 'w', 'KEY_X': 'x', 'KEY_C': 'c', 'KEY_V': 'v', 'KEY_B': 'b',
                'KEY_N': 'n', 'KEY_M': ',',
                'KEY_SEMICOLON': 'm', 'KEY_APOSTROPHE': 'ù', 'KEY_COMMA': ';',
                'KEY_PERIOD': ':', 'KEY_SLASH': '!', 'KEY_BACKSLASH': '*',
                'KEY_LEFTBRACE': '^', 'KEY_RIGHTBRACE': '$', 'KEY_GRAVE': '²',
                'KEY_MINUS': ')', 'KEY_EQUAL': '=',
                # Numbers produce symbols on AZERTY
                'KEY_1': '&', 'KEY_2': 'é', 'KEY_3': '"', 'KEY_4': "'", 'KEY_5': '(',
                'KEY_6': '-', 'KEY_7': 'è', 'KEY_8': '_', 'KEY_9': 'ç', 'KEY_0': 'à',
            },
            LayoutType.QWERTY_IT: {
                # Mapping for Italian QWERTY layout with dead keys support
                'KEY_Q': 'q', 'KEY_W': 'w', 'KEY_E': 'e', 'KEY_R': 'r', 'KEY_T': 't',
                'KEY_Y': 'y', 'KEY_U': 'u', 'KEY_I': 'i', 'KEY_O': 'o', 'KEY_P': 'p',
                'KEY_A': 'a', 'KEY_S': 's', 'KEY_D': 'd', 'KEY_F': 'f', 'KEY_G': 'g',
                'KEY_H': 'h', 'KEY_J': 'j', 'KEY_K': 'k', 'KEY_L': 'l',
                'KEY_Z': 'z', 'KEY_X': 'x', 'KEY_C': 'c', 'KEY_V': 'v', 'KEY_B': 'b',
                'KEY_N': 'n', 'KEY_M': 'm',
                # Italian specific mappings
                'KEY_SEMICOLON': 'ò', 'KEY_APOSTROPHE': 'à', 'KEY_COMMA': ',',
                'KEY_PERIOD': '.', 'KEY_SLASH': '-', 'KEY_BACKSLASH': '\\',
                'KEY_LEFTBRACE': 'è', 'KEY_RIGHTBRACE': '+', 'KEY_GRAVE': '\\',
                'KEY_MINUS': "'", 'KEY_EQUAL': 'ì',
                # Numbers on Italian layout
                'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
                'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
                # Dead keys for Italian international
                'KEY_DEAD_GRAVE': '`',      # Dead grave accent
                'KEY_DEAD_ACUTE': "'",     # Dead acute accent  
                'KEY_DEAD_CIRCUMFLEX': '^', # Dead circumflex
                'KEY_DEAD_TILDE': '~',     # Dead tilde
                'KEY_DEAD_DIAERESIS': '"', # Dead diaeresis (umlaut)
            },
            LayoutType.QWERTZ_DE: {
                # Mapping for German QWERTZ layout
                'KEY_Q': 'q', 'KEY_W': 'w', 'KEY_E': 'e', 'KEY_R': 'r', 'KEY_T': 't',
                'KEY_Y': 'z', 'KEY_U': 'u', 'KEY_I': 'i', 'KEY_O': 'o', 'KEY_P': 'p',
                'KEY_A': 'a', 'KEY_S': 's', 'KEY_D': 'd', 'KEY_F': 'f', 'KEY_G': 'g',
                'KEY_H': 'h', 'KEY_J': 'j', 'KEY_K': 'k', 'KEY_L': 'l',
                'KEY_Z': 'y', 'KEY_X': 'x', 'KEY_C': 'c', 'KEY_V': 'v', 'KEY_B': 'b',
                'KEY_N': 'n', 'KEY_M': 'm',
                'KEY_SEMICOLON': 'ö', 'KEY_APOSTROPHE': 'ä', 'KEY_COMMA': ',',
                'KEY_PERIOD': '.', 'KEY_SLASH': '-', 'KEY_BACKSLASH': '#',
                'KEY_LEFTBRACE': 'ü', 'KEY_RIGHTBRACE': '+', 'KEY_GRAVE': '^',
                'KEY_MINUS': 'ß', 'KEY_EQUAL': '´',
                # Numbers
                'KEY_1': '1', 'KEY_2': '2', 'KEY_3': '3', 'KEY_4': '4', 'KEY_5': '5',
                'KEY_6': '6', 'KEY_7': '7', 'KEY_8': '8', 'KEY_9': '9', 'KEY_0': '0',
            }
        }
    
    def _initialize_physical_keys(self) -> Dict[int, str]:
        """Initialize mapping from hardware scancodes to physical key names"""
        # This is a simplified mapping - in reality, this would be more comprehensive
        # and potentially different per platform
        return {
            # Letter keys (approximate scancodes - these vary by platform)
            30: 'KEY_A', 48: 'KEY_B', 46: 'KEY_C', 32: 'KEY_D', 18: 'KEY_E',
            33: 'KEY_F', 34: 'KEY_G', 35: 'KEY_H', 23: 'KEY_I', 36: 'KEY_J',
            37: 'KEY_K', 38: 'KEY_L', 50: 'KEY_M', 49: 'KEY_N', 24: 'KEY_O',
            25: 'KEY_P', 16: 'KEY_Q', 19: 'KEY_R', 31: 'KEY_S', 20: 'KEY_T',
            22: 'KEY_U', 47: 'KEY_V', 17: 'KEY_W', 45: 'KEY_X', 21: 'KEY_Y',
            44: 'KEY_Z',
            # Number keys
            2: 'KEY_1', 3: 'KEY_2', 4: 'KEY_3', 5: 'KEY_4', 6: 'KEY_5',
            7: 'KEY_6', 8: 'KEY_7', 9: 'KEY_8', 10: 'KEY_9', 11: 'KEY_0',
            # Symbol keys
            39: 'KEY_SEMICOLON', 40: 'KEY_APOSTROPHE', 51: 'KEY_COMMA',
            52: 'KEY_PERIOD', 53: 'KEY_SLASH', 43: 'KEY_BACKSLASH',
            26: 'KEY_LEFTBRACE', 27: 'KEY_RIGHTBRACE', 41: 'KEY_GRAVE',
            12: 'KEY_MINUS', 13: 'KEY_EQUAL',
        }
    
    def _detect_current_layout(self) -> None:
        """Detect the current keyboard layout of the system"""
        try:
            if ci.platform == ci.WINDOWS:
                self.current_layout = self._detect_windows_layout()
            elif ci.platform == ci.MACOS:
                self.current_layout = self._detect_macos_layout()
            elif ci.platform == ci.LINUX:
                self.current_layout = self._detect_linux_layout()
            else:
                self.current_layout = LayoutInfo(
                    LayoutType.UNKNOWN, "en", "US", "Unknown"
                )
        except Exception:
            # Fallback to US QWERTY if detection fails
            self.current_layout = LayoutInfo(
                LayoutType.QWERTY_US, "en", "US", "US QWERTY (fallback)"
            )
    
    def _detect_windows_layout(self) -> LayoutInfo:
        """Detect keyboard layout on Windows"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Get the current keyboard layout
            user32 = ctypes.windll.user32
            kernel32 = ctypes.windll.kernel32
            
            # Get the current thread's keyboard layout
            hkl = user32.GetKeyboardLayout(0)
            
            # Extract language ID from keyboard layout handle
            language_id = hkl & 0xFFFF
            
            # Map common language IDs to layouts
            layout_map = {
                0x0409: (LayoutType.QWERTY_US, "en", "US", "US English"),
                0x0809: (LayoutType.QWERTY_UK, "en", "GB", "UK English"),
                0x040C: (LayoutType.AZERTY_FR, "fr", "FR", "French"),
                0x0407: (LayoutType.QWERTZ_DE, "de", "DE", "German"),
                0x0807: (LayoutType.QWERTZ_CH, "de", "CH", "Swiss German"),
                0x0410: (LayoutType.QWERTY_IT, "it", "IT", "Italian"),
            }
            
            if language_id in layout_map:
                layout_type, lang, country, name = layout_map[language_id]
                return LayoutInfo(layout_type, lang, country, name)
            else:
                return LayoutInfo(LayoutType.UNKNOWN, "en", "US", f"Unknown (0x{language_id:04X})")
                
        except Exception:
            return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US QWERTY (Windows fallback)")
    
    def _detect_macos_layout(self) -> LayoutInfo:
        """Detect keyboard layout on macOS"""
        try:
            import subprocess
            
            # Get current keyboard layout using defaults command
            result = subprocess.run([
                'defaults', 'read', 
                'com.apple.HIToolbox', 'AppleSelectedInputSources'
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                output = result.stdout
                # Parse the output to extract layout information
                # This is simplified - real implementation would parse the plist properly
                if 'US' in output:
                    return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US English")
                elif 'French' in output:
                    return LayoutInfo(LayoutType.AZERTY_FR, "fr", "FR", "French")
                elif 'German' in output:
                    return LayoutInfo(LayoutType.QWERTZ_DE, "de", "DE", "German")
            
            return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US QWERTY (macOS fallback)")
            
        except Exception:
            return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US QWERTY (macOS fallback)")
    
    def _detect_linux_layout(self) -> LayoutInfo:
        """Detect keyboard layout on Linux"""
        try:
            import subprocess
            
            # Try to get layout from setxkbmap
            result = subprocess.run(['setxkbmap', '-query'], 
                                   capture_output=True, text=True)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                layout = None
                variant = None
                
                for line in lines:
                    if line.startswith('layout:'):
                        layout = line.split(':')[1].strip()
                    elif line.startswith('variant:'):
                        variant = line.split(':')[1].strip()
                
                # Map common layouts
                if layout == 'us':
                    return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US English")
                elif layout == 'fr':
                    return LayoutInfo(LayoutType.AZERTY_FR, "fr", "FR", "French")
                elif layout == 'de':
                    return LayoutInfo(LayoutType.QWERTZ_DE, "de", "DE", "German")
                elif layout == 'gb':
                    return LayoutInfo(LayoutType.QWERTY_UK, "en", "GB", "UK English")
            
            return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US QWERTY (Linux fallback)")
            
        except Exception:
            return LayoutInfo(LayoutType.QWERTY_US, "en", "US", "US QWERTY (Linux fallback)")
    
    def process_key_input(self, char: str, layout_type: LayoutType = None) -> str:
        """
        Process a character input, handling dead key sequences.
        Returns the final character to output.
        """
        if layout_type is None:
            layout_type = self.current_layout.layout_type
        
        # Check if current input is a dead key
        if self.is_dead_key(char, layout_type):
            # Store the dead key and wait for next character
            self.pending_dead_key = char
            return ""  # Don't output anything yet
        
        # If we have a pending dead key, try to combine
        if self.pending_dead_key:
            result = self.resolve_dead_key_sequence(self.pending_dead_key, char, layout_type)
            self.pending_dead_key = None  # Clear pending dead key
            return result
        
        # Normal character
        return char
    
    def clear_dead_key_state(self):
        """Clear any pending dead key state"""
        self.pending_dead_key = None
    
    def resolve_dead_key_sequence(self, dead_key: str, base_char: str, layout_type: LayoutType = None) -> str:
        """Resolve a dead key + base character combination to the accented character"""
        if layout_type is None:
            layout_type = self.current_layout.layout_type
        
        combinations = self.dead_key_combinations.get(layout_type, [])
        
        for combination in combinations:
            if combination.dead_key == dead_key and combination.base_char == base_char:
                return combination.result_char
        
        # If no combination found, return the base character
        return base_char
    
    def is_dead_key(self, char: str, layout_type: LayoutType = None) -> bool:
        """Check if a character is a dead key for the given layout"""
        if layout_type is None:
            layout_type = self.current_layout.layout_type
        
        dead_keys = {'`', "'", '^', '~', '"'}  # Common dead keys
        return char in dead_keys
    
    def get_layout_info(self) -> LayoutInfo:
        """Get current layout information"""
        return self.current_layout
    
    def set_layout_type(self, layout_type):
        """Manually set the layout type (useful for testing)"""
        if isinstance(layout_type, str):
            layout_type = LayoutType(layout_type)
        
        # Create a new layout info with the specified type
        self.current_layout = LayoutInfo(
            layout_type=layout_type,
            language_code=self._get_language_code_for_layout(layout_type),
            country_code=self._get_country_code_for_layout(layout_type),
            layout_name=self._get_display_name_for_layout(layout_type)
        )
        
        print(f"Layout manually set to: {layout_type.value}")
    
    def _get_language_code_for_layout(self, layout_type):
        """Get appropriate language code for layout type"""
        layout_map = {
            LayoutType.QWERTY_US: 'en',
            LayoutType.QWERTY_UK: 'en',
            LayoutType.QWERTY_IT: 'it',
            LayoutType.AZERTY_FR: 'fr',
            LayoutType.QWERTZ_DE: 'de',
            LayoutType.QWERTZ_CH: 'de',
            LayoutType.DVORAK: 'en',
            LayoutType.COLEMAK: 'en'
        }
        return layout_map.get(layout_type, 'en')
    
    def _get_country_code_for_layout(self, layout_type):
        """Get appropriate country code for layout type"""
        country_map = {
            LayoutType.QWERTY_US: 'US',
            LayoutType.QWERTY_UK: 'UK',
            LayoutType.QWERTY_IT: 'IT',
            LayoutType.AZERTY_FR: 'FR',
            LayoutType.QWERTZ_DE: 'DE',
            LayoutType.QWERTZ_CH: 'CH',
            LayoutType.DVORAK: 'US',
            LayoutType.COLEMAK: 'US'
        }
        return country_map.get(layout_type, 'US')
    
    def _get_display_name_for_layout(self, layout_type):
        """Get display name for layout type"""
        name_map = {
            LayoutType.QWERTY_US: 'US QWERTY',
            LayoutType.QWERTY_UK: 'UK QWERTY',
            LayoutType.QWERTY_IT: 'Italian QWERTY',
            LayoutType.AZERTY_FR: 'French AZERTY',
            LayoutType.QWERTZ_DE: 'German QWERTZ',
            LayoutType.QWERTZ_CH: 'Swiss QWERTZ',
            LayoutType.DVORAK: 'Dvorak',
            LayoutType.COLEMAK: 'Colemak'
        }
        return name_map.get(layout_type, 'Unknown Layout')
    
    def physical_key_to_char(self, physical_code: int, layout_type: LayoutType = None) -> str:
        """Convert physical key code to character for specified layout"""
        if layout_type is None:
            layout_type = self.current_layout.layout_type
        
        # Get physical key name from scancode
        key_name = self.physical_key_names.get(physical_code)
        if not key_name:
            return ""
        
        # Get character for this physical key in the specified layout
        layout_map = self.layout_maps.get(layout_type, {})
        return layout_map.get(key_name, "")
    
    def char_to_physical_key(self, char: str, layout_type: LayoutType = None) -> Optional[int]:
        """Convert character to physical key code for specified layout"""
        if layout_type is None:
            layout_type = self.current_layout.layout_type
        
        layout_map = self.layout_maps.get(layout_type, {})
        
        # Find the physical key that produces this character
        for key_name, key_char in layout_map.items():
            if key_char == char.lower():
                # Find scancode for this key name
                for scancode, name in self.physical_key_names.items():
                    if name == key_name:
                        return scancode
        return None
    
    def convert_key_between_layouts(self, char: str, from_layout: LayoutType, 
                                  to_layout: LayoutType) -> str:
        """Convert a character from one layout to another using physical key mapping"""
        # Find physical key that produces this character in source layout
        physical_code = self.char_to_physical_key(char, from_layout)
        if physical_code is None:
            return char  # Return original if not found
        
        # Get character that this physical key produces in target layout
        target_char = self.physical_key_to_char(physical_code, to_layout)
        return target_char if target_char else char
    
    def create_key_info(self, pynput_key, physical_code: int = None) -> KeyInfo:
        """Create KeyInfo from pynput key event"""
        if hasattr(pynput_key, 'char') and pynput_key.char is not None:
            # Character key
            logical_char = pynput_key.char
            key_name = f"KEY_{pynput_key.char.upper()}" if pynput_key.char.isalpha() else "KEY_UNKNOWN"
        else:
            # Special key
            logical_char = ""
            key_name = str(pynput_key)
        
        return KeyInfo(
            physical_code=physical_code or 0,
            logical_char=logical_char,
            key_name=key_name,
            modifiers=0  # TODO: Extract modifier state
        )


# Global instance
_layout_manager = None

def get_layout_manager() -> KeyboardLayoutManager:
    """Get the global keyboard layout manager instance"""
    global _layout_manager
    if _layout_manager is None:
        _layout_manager = KeyboardLayoutManager()
    return _layout_manager