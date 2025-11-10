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
        Sets plain text to the clipboard.
        """
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(data)
        win32clipboard.CloseClipboard()
