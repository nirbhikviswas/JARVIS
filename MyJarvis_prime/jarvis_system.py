import screen_brightness_control as sbc
import pyautogui
from AppOpener import open as open_app
import subprocess

def execute_sys_command(command):
    command = command.lower()

    if "brightness" in command:
        try:
            if "up" in command: 
                sbc.set_brightness(min(sbc.get_brightness()[0]+20, 100))
                return "Brightness Up"
            elif "down" in command: 
                sbc.set_brightness(max(sbc.get_brightness()[0]-20, 0))
                return "Brightness Down"
        except: pass

    if "volume" in command:
        if "up" in command: pyautogui.press("volumeup", presses=5)
        elif "down" in command: pyautogui.press("volumedown", presses=5)
        elif "mute" in command: pyautogui.press("volumemute")
        return "Volume Adjusted"

    if "keyboard" in command:
        subprocess.Popen("osk")
        return "Keyboard On"

    if "open" in command:
        app = command.replace("open", "").strip()
        try:
            open_app(app, match_closest=True)
            return f"Opening {app}"
        except: return "App not found"
        
    if "screenshot" in command:
        return "ACTION_SCREENSHOT"

    return None