from pynput import keyboard
from pynput.keyboard import Key, Controller
import configparser

class Hotkeys():
    def __init__(self):
        config=configparser.ConfigParser()
        config.read('cfg/config.ini')
        self.first_hotkey = config['HOTKEYS']['first_hotkey']
        self.second_hotkey = config['HOTKEYS']['second_hotkey']
        self.hotkey = None
        self.listener = None


    def _start(self) -> None:
        self.listener.start()

    def _join(self) -> None:
        self.listener.join()



   