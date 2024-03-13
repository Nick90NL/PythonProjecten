import os
from pynput.mouse import Listener as MouseListener
from pynput.keyboard import Listener as KeyboardListener, Key

# Globale variabelen
current_directory = os.getcwd()
shift_pressed = False
pause_script = False
keyboard_listener = None
log_file_path = ""
recording_started = False

def recording_stopped():
    return os.path.exists(log_file_path) and os.stat(log_file_path).st_size == 0

def write_to_log(content):
    if not pause_script:
        with open(log_file_path, 'a') as output_file:
            output_file.write(content + "\n")

def on_move(x, y):
    write_to_log(f"pyautogui.moveTo({x}, {y})")

def on_click(x, y, button, pressed):
    if pressed:
        write_to_log(f"pyautogui.mouseDown(button='{button.name}')")
    else:
        write_to_log(f"pyautogui.mouseUp(button='{button.name}')")

def on_key_press(key):
    global shift_pressed, pause_script
    
    if key in [Key.shift, Key.shift_l, Key.shift_r]:
        shift_pressed = True
        
    if key == Key.enter and shift_pressed and not recording_started:
        return True

    if key == Key.space and shift_pressed:
        pause_script = not pause_script
        return
    
    if key == Key.esc and shift_pressed:
        stop_recording()
        return True

    if not pause_script:
        if hasattr(key, 'name'):
            if shift_pressed and (key == Key.space or key == Key.esc or key == Key.enter):
                return
            write_to_log(f"pyautogui.press('{key.name}')")
        else:
            write_to_log(f"pyautogui.press('{key.char}')")

def on_key_release(key):
    global shift_pressed
  
    if key in [Key.shift, Key.shift_l, Key.shift_r]:
        shift_pressed = False

def stop_recording():
    global keyboard_listener
    if keyboard_listener:
        keyboard_listener.stop()

def start_recording(log_file_name=None):
    global keyboard_listener, log_file_path
    
    log_file_path = os.path.join(current_directory, log_file_name)
    try:
        with open(log_file_path, 'w') as test_file:
            test_file.write("")

    except Exception as e:
        print(f"Error bij het initialiseren van de log file: {e}")
    mouse_listener = MouseListener(on_move=on_move, on_click=on_click)
    mouse_listener.start()

    keyboard_listener = KeyboardListener(on_press=on_key_press, on_release=on_key_release)
    keyboard_listener.start()

def set_recording_started(value):
    global recording_started
    recording_started = value

def is_recording_started():
    return recording_started


def toggle_pause_script():
    global pause_script
    pause_script = not pause_script
