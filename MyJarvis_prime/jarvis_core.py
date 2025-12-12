import customtkinter as ctk
import tkinter as tk
import threading
import speech_recognition as sr
import edge_tts
import asyncio
import pygame
import os
import math
import pyautogui
from jarvis_brain import think, analyze_image
from jarvis_system import execute_sys_command

ctk.set_appearance_mode("Dark")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_FILE = os.path.join(BASE_DIR, "Media", "speech.mp3")
SCREENSHOT_FILE = os.path.join(BASE_DIR, "Media", "vision.png")
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.cfg")
pygame.mixer.init()

def get_setting(key):
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            for line in f:
                if line.startswith(key):
                    return line.split("=")[1].strip()
    return "en-US"

class JarvisHUD(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("JARVIS HUD")
        self.geometry("600x120")
        self.overrideredirect(True)
        self.attributes('-topmost', True)
        self.attributes('-alpha', 0.90)
        self.configure(fg_color="#000000")
        
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        self.geometry(f"600x120+{(sw-600)//2}+{sh-150}")

        self.canvas = tk.Canvas(self, width=600, height=80, bg="black", highlightthickness=0)
        self.canvas.pack(pady=5)
        self.lbl = ctk.CTkLabel(self, text="ONLINE", font=("Consolas", 12), text_color="#00FF00")
        self.lbl.pack()

        self.is_listening = False
        self.is_speaking = False
        self.pulse = 0
        self.stop_audio = False
        
        self.animate()
        threading.Thread(target=self.listener, daemon=True).start()

    def animate(self):
        self.canvas.delete("all")
        cx, cy = 300, 40
        color = "#222"
        if self.is_listening: color = "#FF0000"
        if self.is_speaking: color = "#00FFFF"
        
        self.pulse += 0.2
        r = 20 + (math.sin(self.pulse) * 5)
        
        self.canvas.create_oval(cx-r, cy-r, cx+r, cy+r, fill=color, outline="")
        
        # Sci-Fi Ring
        self.canvas.create_arc(cx-35, cy-35, cx+35, cy+35, start=self.pulse*10, extent=60, outline=color, width=2)
        self.canvas.create_arc(cx-35, cy-35, cx+35, cy+35, start=(self.pulse*10)+180, extent=60, outline=color, width=2)
        
        self.after(40, self.animate)

    def speak(self, text):
        self.stop_audio = False
        self.is_speaking = True
        self.lbl.configure(text=text.upper(), text_color="#00FFFF")
        
        lang = get_setting("LANGUAGE")
        voice = "en-US-ChristopherNeural"
        if lang == "hi-IN": voice = "hi-IN-MadhurNeural"
        if lang == "bn-IN": voice = "bn-IN-BashkarNeural"

        async def gen():
            comm = edge_tts.Communicate(text, voice)
            await comm.save(AUDIO_FILE)

        try:
            asyncio.run(gen())
            pygame.mixer.music.load(AUDIO_FILE)
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if self.stop_audio:
                    pygame.mixer.music.stop()
                    break
                self.update()
            pygame.mixer.music.unload()
        except: pass
        
        self.is_speaking = False
        self.lbl.configure(text="STANDBY", text_color="gray")

    def listener(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source, duration=1)
            r.dynamic_energy_threshold = False
            
            while True:
                try:
                    audio = r.listen(source, phrase_time_limit=3)
                    try: 
                        trigger = r.recognize_google(audio).lower()
                    except: 
                        trigger = ""

                    if "jarvis" in trigger:
                        if self.is_speaking:
                            self.stop_audio = True
                            self.speak("Stopped.")
                            continue

                        self.speak("Yes?")
                        self.is_listening = True
                        
                        full = ""
                        active = True
                        while active:
                            try:
                                aud = r.listen(source, phrase_time_limit=5)
                                lang_code = get_setting("LANGUAGE")
                                txt = r.recognize_google(aud, language=lang_code).lower()
                                self.lbl.configure(text=f">> {txt}", text_color="orange")
                                full += " " + txt
                                if "over" in txt: active = False
                            except: pass
                        
                        self.is_listening = False
                        cmd = full.replace("jarvis", "").replace("over", "").strip()
                        
                        sys_res = execute_sys_command(cmd)
                        if sys_res == "ACTION_SCREENSHOT":
                            self.speak("Scanning...")
                            pyautogui.screenshot(SCREENSHOT_FILE)
                            res = analyze_image(SCREENSHOT_FILE)
                            self.speak(res)
                        elif sys_res:
                            self.speak(sys_res)
                        elif "shutdown" in cmd:
                            self.speak("Goodbye.")
                            os._exit(0)
                        else:
                            reply = think(cmd)
                            self.speak(reply)
                except: pass

if __name__ == "__main__":
    app = JarvisHUD()
    app.mainloop()