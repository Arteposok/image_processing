import os
import keyboard

def save():
    os.system("git add .")
    os.system("git commit -m 'm'")
    os.system("git push -u origin main")

keyboard.add_hotkey("ctrl+s", save)

while True:
    pass