# Flow KVM - Keyboard Layout Improvements

## Overview

This document describes the significant improvements made to the Flow KVM software to address keyboard layout compatibility issues between client and server machines with different keyboard layouts.

## Problem Addressed

The original Flow KVM software had a critical limitation: it couldn't correctly handle keyboard input when the server and client machines used different keyboard layouts (e.g., QWERTY vs AZERTY vs QWERTZ). This made the software unusable in multilingual environments.

### Original Issues:
- Characters would appear incorrectly when typing (e.g., 'A' on server would produce 'Q' on AZERTY client)
- No layout detection or conversion mechanisms
- Simplistic string-based key transmission that assumed identical layouts
- Special characters (@, #, [], {}, etc.) appeared in wrong positions

## New Architecture

### 1. Keyboard Layout Detection (`src/hardware/keyboard_layout.py`)

**Automatic Detection:**
- **Windows**: Uses Windows API to detect current keyboard layout via language ID
- **macOS**: Queries system preferences using `defaults` command
- **Linux**: Uses `setxkbmap -query` to determine current layout

**Supported Layouts:**
- QWERTY (US, UK)
- AZERTY (French)
- QWERTZ (German, Swiss)
- Dvorak
- Colemak
- Extensible for additional layouts

### 2. Physical Key Mapping

**Key Features:**
- Maps physical key positions (scancodes) to logical characters
- Layout-independent key identification
- Conversion between layouts using physical key positions
- Handles both character keys and special keys (Ctrl, Alt, etc.)

### 3. Enhanced Protocol

**New Key Data Format:**
```python
{
    'type': 'character',  # or 'special'
    'physical_code': 30,  # Hardware scancode
    'logical_char': 'a',  # Character in current layout
    'key_name': 'KEY_A', # Physical key identifier
    'layout_type': 'qwerty_us',
    'language_code': 'en',
    'country_code': 'US'
}
```

**Layout Information Exchange:**
- Server sends layout information when connection is established
- Client can adjust key interpretation based on server layout
- Backward compatibility with old string-based format

### 4. User Interface Enhancements

**New Settings Section:**
- Auto-detect keyboard layout (default)
- Manual layout selection override
- Real-time layout detection display
- Visual feedback for layout matching/mismatching

## Implementation Details

### Key Files Modified:

1. **`src/hardware/keyboard_layout.py`** (NEW)
   - Core layout detection and conversion logic
   - Cross-platform layout detection
   - Layout mapping tables
   - Key conversion functions

2. **`src/hardware/keyboard.py`**
   - Enhanced with layout-aware functions
   - Backward compatibility maintained
   - New key data creation and parsing

3. **`src/comms/transfer.py`**
   - Updated to send layout-aware key data
   - Layout information exchange on connection
   - Graceful handling of both old and new formats

4. **`src/ui/qtsettings.py`**
   - New keyboard layout configuration section
   - Auto-detect vs manual selection
   - Real-time layout status display

5. **`src/data/db.py`**
   - New database settings for layout preferences
   - Auto-detect and manual layout storage

### Key Functions:

- `get_layout_manager()`: Get global layout manager instance
- `create_layout_aware_key_data()`: Create new key data format
- `key_from_layout_aware_data()`: Convert key data back to pynput format
- `convert_key_between_layouts()`: Convert characters between layouts

## Usage

### For Users:

1. **Automatic Mode (Default):**
   - Layout is automatically detected on both server and client
   - Keys are converted based on physical positions
   - Works seamlessly across different layouts

2. **Manual Override:**
   - Access Settings → Keyboard Layout section
   - Disable "Auto-detect keyboard layout"
   - Select your specific layout from dropdown
   - Useful for special cases or detection failures

### For Developers:

1. **Adding New Layouts:**
   ```python
   # In keyboard_layout.py, add to _initialize_layout_maps()
   LayoutType.NEW_LAYOUT: {
       'KEY_Q': 'mapped_char',
       'KEY_W': 'mapped_char',
       # ... mapping for all keys
   }
   ```

2. **Layout Detection for New Platforms:**
   ```python
   # Add platform-specific detection in KeyboardLayoutManager
   def _detect_new_platform_layout(self) -> LayoutInfo:
       # Platform-specific detection logic
       return LayoutInfo(layout_type, lang, country, name)
   ```

## Testing

Run the comprehensive test suite:

```bash
python test_keyboard_layout.py
```

**Tests Include:**
- Layout detection on current system
- Character conversion between layouts
- New key data format validation
- Physical key mapping verification
- Backward compatibility checks

## Backward Compatibility

The implementation maintains full backward compatibility:
- Old clients can connect to new servers
- New clients can connect to old servers
- Graceful fallback to string-based format when needed

## Performance Considerations

- Layout detection is performed once at startup
- Key conversion uses lookup tables (O(1) operations)
- Minimal network overhead for layout information exchange
- No impact on mouse or other input handling

## Future Enhancements

### Potential Improvements:
1. **Dynamic Layout Switching**: Detect layout changes during runtime
2. **Custom Layout Creation**: Allow users to define custom mappings
3. **Layout Learning**: Automatically learn mappings from user behavior
4. **Mobile Layout Support**: Support for mobile device virtual keyboards
5. **Gaming Optimizations**: Special handling for gaming scenarios

### Advanced Features:
- Dead key support for accented characters
- IME (Input Method Editor) support for Asian languages
- Compose key sequences
- Platform-specific special keys (Windows key, Cmd key variations)

## Migration Guide

### From Original Version:

1. **No Action Required**: The system automatically detects and handles layouts
2. **Optional Configuration**: Use new settings for manual override if needed
3. **Testing**: Verify keyboard input works correctly across your devices

### Troubleshooting:

1. **Wrong Characters Appearing:**
   - Check Settings → Keyboard Layout
   - Try manual layout selection
   - Verify detected layout matches your keyboard

2. **Layout Not Detected:**
   - Use manual selection
   - Check system language/keyboard settings
   - Report unsupported layout for future addition

3. **Performance Issues:**
   - Layout detection happens once at startup
   - Key conversion is very fast (lookup table)
   - Check network connectivity for layout info exchange

## Contributing

### Adding New Keyboard Layouts:

1. Research the layout's character mapping
2. Add layout type to `LayoutType` enum
3. Add mapping table in `_initialize_layout_maps()`
4. Add detection logic for the layout's regions
5. Test thoroughly with native speakers
6. Update documentation

### Reporting Issues:

Include the following information:
- Operating system and version
- Keyboard layout being used
- Detected vs expected layout
- Specific keys that don't work correctly
- Flow version information

---

This improvement significantly enhances Flow KVM's usability in international and multilingual environments, making it a truly universal KVM solution.