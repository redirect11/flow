import time

from src.hardware.keyboard import (KeyboardController, KeyboardListener, key_from_str,
                                  create_layout_aware_key_data, key_from_layout_aware_data,
                                  get_current_layout_info)
from src.hardware.mouse import LockedMouse, MouseController, MouseListener, mbuttons


class SharedDevices:
    """
    A class used to send mouse and keyboard data
    to the given client.

    UDP communication
    """

    def __init__(self, machine):
        # current machine being controlled. Send events to this machine
        self.machine = machine
        # current machine's udp socket
        self.socket = machine.udp_conn
        # devices which callback the events
        self.lmouse = self.mouse = self.keyboard = None

    def __on_move(self, x, y):
        """
        On move event. Sends 'mov <mouse_position>' to client
        """
        self.machine.mouse_position = (self.machine.mouse_position[0] + x, self.machine.mouse_position[1] + y)
        self.socket.true_sendto(
            "mov " + str(self.machine.mouse_position[0]) + " " + str(self.machine.mouse_position[1]),
            self.machine.address)

    def __on_mouse_click(self, x, y, button, pressed):
        """
        On mouse click event. Sends 'prsm <button>' to client
        """
        self.socket.true_sendto(("prsm", pressed, str(button)[7:]), self.machine.address, special=True)

    def __on_mouse_scroll(self, x, y, dx, dy):
        """
        On scroll event. Sends 'scrl <dx dy>' to client
        """
        self.socket.true_sendto("scrl " + str(dx) + " " + str(dy), self.machine.address)

    def __on_keyboard_press(self, key):
        """
        On key press event. Sends layout-aware key data to client
        """
        key_data = create_layout_aware_key_data(key)
        self.socket.true_sendto(("prsk", True, key_data), self.machine.address, special=True)

    def __on_keyboard_release(self, key):
        """
        On key release event. Sends layout-aware key data to client
        """
        key_data = create_layout_aware_key_data(key)
        self.socket.true_sendto(("prsk", False, key_data), self.machine.address, special=True)

    def share(self):
        """
        Starts mouse and keyboard event capture.
        Sends layout information to client.
        """
        # Send current layout information to client
        layout_info = get_current_layout_info()
        layout_data = {
            'layout_type': layout_info.layout_type.value,
            'language_code': layout_info.language_code,
            'country_code': layout_info.country_code,
            'layout_name': layout_info.layout_name
        }
        self.socket.true_sendto(("layout_info", layout_data), self.machine.address, special=True)
        
        # Start input capture
        self.lmouse = LockedMouse(on_move=self.__on_move)
        self.mouse = MouseListener(on_click=self.__on_mouse_click, on_scroll=self.__on_mouse_scroll)
        self.keyboard = KeyboardListener(on_press=self.__on_keyboard_press, on_release=self.__on_keyboard_release,
                                         suppress=True)
        self.lmouse.start()
        self.mouse.start()
        self.keyboard.start()

    def pause(self):
        if self.mouse is not None:
            for device in (self.mouse, self.lmouse, self.keyboard):
                device.stop()
            self.lmouse.wait()

    def stop(self):
        self.pause()
        self.socket.true_sendto("stp X X", self.machine.address)


class ControlledDevices:
    """
    A class used to receive mouse and keyboard data
    and physically apply them.

    UDP communication
    """

    def __init__(self, client):
        # current controlled client
        self.client = client

        # devices controllers
        self.keyboard = KeyboardController()
        self.mouse = MouseController()

        # layout information from server
        self.server_layout_info = None
        
        self._on = True

    def get_controlled(self):
        """
        Implements events received from server
        """
        while self._on:

            try:
                data = self.client.udp_sock.true_recvfrom(1024)[0]
            except OSError:  # when the udp socket is temporarly closed
                time.sleep(1)
                continue

            if type(data) == str:
                data = data.split(" ")

            cmd_type = data[0]
            
            # Only extract action if we have enough elements
            if len(data) >= 3:
                action = (data[1], data[2])
            elif len(data) >= 2:
                action = (data[1],)
            else:
                action = ()

            if cmd_type == "mov":
                x_pos, y_pos = action
                self.mouse.position = (int(float(x_pos)), int(float(y_pos)))

            elif cmd_type == "prsk":
                # data = True/False, key_data (dict):
                pressed, key_data = action
                try:
                    # Handle both old string format and new layout-aware format
                    if isinstance(key_data, str):
                        # Legacy format - use old conversion method
                        key_to_press = key_from_str(key_data)
                    else:
                        # New layout-aware format
                        key_to_press = key_from_layout_aware_data(key_data)
                    
                    if key_to_press is not None:
                        if pressed:
                            self.keyboard.press(key_to_press)
                        else:
                            self.keyboard.release(key_to_press)
                except (KeyError, TypeError, AttributeError):
                    # Skip key if conversion fails
                    pass

            elif cmd_type == "prsm":
                # data = True/False, button:
                pressed, str_button = action
                if pressed:
                    self.mouse.press(mbuttons[str_button])
                else:
                    self.mouse.release(mbuttons[str_button])

            elif cmd_type == "scrl":
                # data = dx, dy
                dx, dy = action
                self.mouse.scroll(int(dx), int(dy))

            elif cmd_type == "stp":
                # data = 'X', 'X'
                pass
            
            elif cmd_type == "layout_info":
                # Receive server layout information
                self.server_layout_info = action[0] if len(action) > 0 else None

    def stop(self):
        self._on = False
