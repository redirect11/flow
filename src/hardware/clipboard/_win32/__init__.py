import subprocess
import win32clipboard

from src.files import FILE2CLIP_WIN


class WindowsClipboard:
    """
    Windows Clipboard api
    """

    @staticmethod
    def set_files(files: list):
        """
        Sets given file paths to the clipboard.
        """
        if len(files) != 0:
            subprocess.Popen([FILE2CLIP_WIN] + files)

    @staticmethod
    def data():
        """
        Returns clipboard data with proper error handling.
        """
        try:
            win32clipboard.OpenClipboard()
            try:
                try:
                    data = win32clipboard.GetClipboardData()
                except TypeError:
                    try:
                        data = win32clipboard.GetClipboardData(win32clipboard.CF_HDROP)
                    except:
                        data = 'unknown format'
            except Exception:
                # Clipboard access error, return None
                data = None
            finally:
                win32clipboard.CloseClipboard()
        except Exception:
            # Cannot open clipboard (access denied, etc.)
            data = None
        
        return data

    @staticmethod
    def set_text(data: str):
        """
        Sets plain text to the clipboard with proper Unicode handling.
        """
        try:
            # Ensure data is properly encoded as UTF-8 string
            if isinstance(data, bytes):
                try:
                    data = data.decode('utf-8')
                except UnicodeDecodeError:
                    try:
                        data = data.decode('latin1')
                    except UnicodeDecodeError:
                        data = data.decode('utf-8', errors='replace')
            
            # Ensure it's a string
            if not isinstance(data, str):
                data = str(data)
            
            # Try to set clipboard with Unicode support
            win32clipboard.OpenClipboard()
            try:
                win32clipboard.EmptyClipboard()
                
                # Try to set as Unicode text first (Windows CF_UNICODETEXT)
                try:
                    win32clipboard.SetClipboardData(win32clipboard.CF_UNICODETEXT, data)
                except Exception:
                    # Fallback to regular text, but encode properly
                    try:
                        # Convert to Windows-1252 (extended ASCII) as fallback
                        encoded_data = data.encode('windows-1252', errors='replace').decode('windows-1252')
                        win32clipboard.SetClipboardText(encoded_data)
                    except Exception:
                        # Last fallback: ASCII with replacement characters
                        ascii_data = data.encode('ascii', errors='replace').decode('ascii')
                        win32clipboard.SetClipboardText(ascii_data)
                        
            finally:
                win32clipboard.CloseClipboard()
                
        except Exception as e:
            # If all fails, log the error but don't crash
            print(f"Clipboard set_text error: {e}")
            # Try to close clipboard if it was opened
            try:
                win32clipboard.CloseClipboard()
            except:
                pass
