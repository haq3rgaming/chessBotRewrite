import sys, traceback, serial.tools.list_ports
import PySimpleGUI as sg

from robot import Robot

import platform, ctypes
if int(platform.release()) >= 8: ctypes.windll.shcore.SetProcessDpiAwareness(True)
screenSize = sg.Window.get_screen_size()

sg.theme("DarkAmber")
sg.set_options(font=("Consolas", 16))
guiSizeCoeficient = 2

baudrate = 115200
port = [port.device for port in serial.tools.list_ports.comports() if port.description.startswith("USB-SERIAL")][0]

layout = [
    [sg.Text("Chess Bot")],
]

def main():
    window = sg.Window("Chess Bot", layout, size=(screenSize[0]//guiSizeCoeficient, screenSize[1]//guiSizeCoeficient), resizable=False, enable_close_attempted_event=True)
    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, sg.WIN_CLOSE_ATTEMPTED_EVENT, "exit"): break
    window.close()

if __name__ == "__main__":
    print("Starting...")
    try: main()
    except Exception:
        print(traceback.format_exc())
    print("Closing...")