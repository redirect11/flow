"""
File containing static methods used to obtain machine information.
"""

from sys import platform
import subprocess
import re

from src.files import WINRES, MACRES, LINRES

WINDOWS = 'win32'
LINUX = 'linux'
MACOS = 'darwin'


def supported():
    """
    Returns True if computer is supported.
    """
    return platform == WINDOWS or platform == LINUX or platform == MACOS


def get_screeninfo():
    """
    Returns screen resolution of computer.
    """
    if platform == WINDOWS:
        output = subprocess.check_output(f'"{WINRES}"', shell=True)
        resolution = re.findall("[0-9]+", output.decode(errors="ignore"))
        resolutions = [(resolution[i], resolution[i + 1]) for i in range(0, len(resolution) - 1, 2)]

    elif platform == LINUX:
        output = subprocess.check_output(LINRES, shell=True)
        resolution = re.findall("[0-9]+x[0-9]+", output.decode(errors="ignore"))
        resolutions = [tuple(res.split("x")) for res in resolution]

    elif platform == MACOS:
        output = subprocess.check_output(MACRES, shell=True)
        resolution = [float(r) for r in output.decode(errors="ignore").split("\n")[:-1]]
        resolutions = [resolution]

    else:
        return None

    return int(resolutions[0][0]), int(resolutions[0][1])  # main screen only


def get_ip():
    """
    Returns local IP of computer with improved detection.
    """
    import socket
    
    # Method 1: Try to get IP by connecting to a remote address (most reliable)
    try:
        # Connect to Google DNS to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            local_ip = s.getsockname()[0]
            # Verify it's a valid private IP
            if local_ip.startswith(('192.168.', '10.', '172.')):
                return local_ip
    except Exception:
        pass
    
    # Method 2: Platform-specific commands as fallback
    try:
        if platform == WINDOWS:
            # Try improved Windows method
            output = subprocess.check_output('ipconfig', shell=True).decode(errors="ignore")
            lines = output.split('\n')
            
            # Look for IPv4 addresses in active adapters
            for i, line in enumerate(lines):
                if 'IPv4 Address' in line and ': ' in line:
                    ip = line.split(': ')[-1].strip()
                    # Check if it's a private IP
                    if ip.startswith(('192.168.', '10.', '172.')) and not ip.endswith('1'):
                        return ip
            
            # Fallback: look for any IPv4 address
            import re
            ip_pattern = r'\b(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\b'
            matches = re.findall(ip_pattern, output)
            if matches:
                return matches[0]

        elif platform == LINUX:
            # Try multiple Linux commands
            commands = ['ip addr', 'hostname -I', 'ifconfig']
            for cmd in commands:
                try:
                    output = subprocess.check_output(cmd.split(), shell=True).decode(errors="ignore")
                    import re
                    ip_pattern = r'\b(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\b'
                    matches = re.findall(ip_pattern, output)
                    if matches:
                        return matches[0]
                except:
                    continue
        
        elif platform == MACOS:
            # Try multiple macOS methods
            commands = ['ifconfig', 'ipconfig getifaddr en0', 'ipconfig getifaddr en1']
            for cmd in commands:
                try:
                    output = subprocess.check_output(cmd.split(), shell=True).decode(errors="ignore")
                    import re
                    ip_pattern = r'\b(?:192\.168\.|10\.|172\.(?:1[6-9]|2[0-9]|3[01])\.)\d{1,3}\.\d{1,3}\b'
                    matches = re.findall(ip_pattern, output)
                    if matches:
                        return matches[0]
                except:
                    continue

    except Exception:
        pass
    
    # Method 3: Use socket.gethostbyname as last resort
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        if not local_ip.startswith('127.'):
            return local_ip
    except Exception:
        pass
    
    # Method 4: Try to enumerate network interfaces (requires additional module)
    try:
        import netifaces
        interfaces = netifaces.interfaces()
        for interface in interfaces:
            addrs = netifaces.ifaddresses(interface)
            if netifaces.AF_INET in addrs:
                for addr_info in addrs[netifaces.AF_INET]:
                    ip = addr_info.get('addr')
                    if ip and ip.startswith(('192.168.', '10.', '172.')) and not ip.endswith('.1'):
                        return ip
    except ImportError:
        pass
    except Exception:
        pass
    
    return 'Not Found'
