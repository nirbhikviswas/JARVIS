import tkinter as tk
from tkinter import messagebox
import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.cfg")
CORE_SCRIPT = os.path.join(BASE_DIR, "jarvis_core.py")
PID_FILE = os.path.join(BASE_DIR, "jarvis.pid")

def save_setting(key, value):
    settings = {}
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    k, v = line.strip().split("=", 1)
                    settings[k] = v
    settings[key] = value
    with open(SETTINGS_FILE, "w") as f:
        for k, v in settings.items():
            f.write(f"{k}={v}\n")

def start_system():
    if os.path.exists(PID_FILE):
        messagebox.showinfo("System", "Already Online")
        return
    # Launch HUD script independently
    proc = subprocess.Popen(["python", CORE_SCRIPT], cwd=BASE_DIR)
    with open(PID_FILE, "w") as f:
        f.write(str(proc.pid))
    lbl_status.config(text="Status: ONLINE", fg="green")

def stop_system():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            pid = f.read().strip()
        os.system(f"taskkill /F /PID {pid}")
        os.remove(PID_FILE)
        lbl_status.config(text="Status: OFFLINE", fg="red")

root = tk.Tk()
root.title("JARVIS COMMAND")
root.geometry("300x400")
root.configure(bg="#111")

tk.Label(root, text="JARVIS CONTROLLER", bg="#111", fg="#0ff", font=("Impact", 16)).pack(pady=20)
lbl_status = tk.Label(root, text="Status: OFFLINE", bg="#111", fg="red")
lbl_status.pack()

tk.Button(root, text="ENGAGE HUD", bg="#060", fg="white", font=("Arial", 12), command=start_system).pack(pady=10, fill="x", padx=20)
tk.Button(root, text="TERMINATE", bg="#900", fg="white", font=("Arial", 12), command=stop_system).pack(pady=5, fill="x", padx=20)

tk.Label(root, text="LANGUAGE", bg="#111", fg="#888").pack(pady=15)
f_lang = tk.Frame(root, bg="#111")
f_lang.pack()

def set_l(l): save_setting("LANGUAGE", l)
tk.Button(f_lang, text="ENG", command=lambda: set_l("en-US")).pack(side=tk.LEFT, padx=5)
tk.Button(f_lang, text="HIN", command=lambda: set_l("hi-IN")).pack(side=tk.LEFT, padx=5)
tk.Button(f_lang, text="BEN", command=lambda: set_l("bn-IN")).pack(side=tk.LEFT, padx=5)

root.mainloop()