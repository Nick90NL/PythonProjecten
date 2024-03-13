import tkinter as tk
from tkinter import simpledialog, messagebox
import pyautogui_rec
import os

def create_gui():
    root = tk.Tk()
    root.title("PyAutoGUI Recorder")
    root.minsize(400, 300)
    recording_status = tk.StringVar(root, value="Klaar om op te nemen")
    recording_status_label = tk.Label(root, textvariable=recording_status)
    recording_status_label.pack(pady=20)

    def update_status():
        if pyautogui_rec.recording_stopped():
            recording_status.set("Opname gestopt")
            record_button.config(state=tk.NORMAL)
        root.after(1000, update_status)

    def start_recording_thread():
        if not pyautogui_rec.is_recording_started():
            log_file_name = simpledialog.askstring("Input", "Geef uw opname een naam:")
            if not log_file_name:
                return

            if not log_file_name.endswith(".txt"):
                log_file_name += ".txt"

            if os.path.exists(log_file_name):
                log_file_name = ask_overwrite(log_file_name)

            pyautogui_rec.set_recording_started(True)
            recording_status.set(f"Opname start over 5 seconden...")
            root.after(1000, lambda: countdown(log_file_name, 4))
    
    def countdown(log_file_name, time_left):
        if time_left > 0:
            recording_status.set(f"Opname start over {time_left} seconden...")
            root.after(1000, lambda: countdown(log_file_name, time_left-1))
        else:
            recording_status.set("Opname gestart!")
            pyautogui_rec.start_recording(log_file_name)

    def pause_recording():
        if pyautogui_rec.is_recording_started():
            pyautogui_rec.pause_script = not pyautogui_rec.pause_script
            if pyautogui_rec.pause_script:
                recording_status.set("Opname gepauzeerd")
            else:
                recording_status.set("Opname hervat")

    def stop_recording():
        if pyautogui_rec.is_recording_started():
            pyautogui_rec.stop_recording()
            recording_status.set("Opname gestopt")

    def ask_overwrite(filename):
        answer = messagebox.askyesno("Bestand bestaat al", f"Het bestand {filename} bestaat al. Wilt u het overschrijven?")
        if answer:
            return filename
        else:
            return None

    record_button = tk.Button(root, text="Start Opname", command=start_recording_thread)
    record_button.pack(pady=20)

    start_label = tk.Label(root, text="SHIFT + ENTER om opname te starten")
    start_label.pack()

    pause_button = tk.Button(root, text="Pauze/Hervat", command=pause_recording)
    pause_button.pack(pady=20)

    pause_label = tk.Label(root, text="SHIFT + SPACE om opname te pauzeren/hervatten")
    pause_label.pack()

    stop_button = tk.Button(root, text="Stop Opname", command=stop_recording)
    stop_button.pack(pady=20)

    stop_label = tk.Label(root, text="SHIFT + ESC om opname te stoppen")
    stop_label.pack()

    update_status() 
    root.mainloop()

# Call the function to display the GUI
create_gui()
