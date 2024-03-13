import pyautogui
from pynput.keyboard import Listener, Key
import os

# Globale variabelen voor het beheren van de pauze en stop functionaliteit
pause_execution = False
stop_execution = False
shift_key_pressed = False

# Verminder de standaard pyautogui pauze
pyautogui.PAUSE = 0.02

def execute_log(log_lines):
    global pause_execution, stop_execution
    for line in log_lines:
        while pause_execution:  # Wacht in een loop zolang de uitvoering is gepauzeerd
            if stop_execution:
                return
            pass

        line = line.strip()
        if line.startswith("pyautogui.moveTo"):
            x, y = map(int, line.split("(")[1].split(")")[0].split(", "))
            pyautogui.moveTo(x, y, duration=0.1)  # Voeg een korte duur toe voor een vloeiende beweging
        elif line.startswith("pyautogui.PAUSE"):
            pause_time = float(line.split("=")[1])
            pyautogui.PAUSE = pause_time
        elif line.startswith("pyautogui.mouseDown"):
            button = line.split("button=")[1].split("'")[1]
            pyautogui.mouseDown(button=button)
        elif line.startswith("pyautogui.mouseUp"):
            button = line.split("button=")[1].split("'")[1]
            pyautogui.mouseUp(button=button)
        elif line.startswith("pyautogui.press"):
            try:
                # Extract key using string manipulation
                press = line.split("'")[1]
                pyautogui.press(press, interval=0.1)  # Voeg vertraging van 0.1 seconden toe
            except IndexError:
                print(f"Error parsing line: {line}")

        if stop_execution:  # Als de "esc" toets is ingedrukt, stop de uitvoering
            return

def list_txt_files_in_directory():
    return [file for file in os.listdir() if file.endswith('.txt')]

def on_key_press(key):
    global pause_execution, stop_execution, shift_key_pressed

    if key == Key.shift:  # Detecteer de Shifttoets
        shift_key_pressed = True

    # Als de Shifttoets is ingedrukt EN de spatiebalk wordt ingedrukt
    if shift_key_pressed and key == Key.space:
        pause_execution = not pause_execution  # Wissel tussen pauzeren en hervatten
        if pause_execution:
            print("De opname is gepauzeerd")
        else:
            print("De opname is hervat")

def on_key_release(key):
    global shift_key_pressed

    if key == Key.shift:
        shift_key_pressed = False

def execute_from_file(filename, repetitions):
    while repetitions != 0:  # blijf lopen totdat repetitions 0 is
        with open(filename, 'r') as file:
            log_lines = file.readlines()
        execute_log(log_lines)
        if repetitions > 0:  # verlaag repetitions tenzij het al -1 is (wat betekent oneindig)
            repetitions -= 1

# Start de toetsenbord-luisteraar
with Listener(on_press=on_key_press, on_release=on_key_release) as listener:
    
    # Lijst alle .txt bestanden in de huidige directory
    txt_files = list_txt_files_in_directory()
    print("Beschikbare opnames:")
    for index, txt_file in enumerate(txt_files, 1):
        print(f"{index}. {txt_file[:-4]}")

    # Laat de gebruiker een bestand kiezen
    while True:
        try:
            chosen_index = int(input("Kies uit de lijst het getal dat u wilt afspelen: "))
            if 1 <= chosen_index <= len(txt_files):
                chosen_file = txt_files[chosen_index - 1]
                break
            else:
                print("Geen geldige invoer, geef een getal in die voorkomt in de lijst.")
        except ValueError:
            print("Geen geldige invoer, geef een getal in die voorkomt in de lijst.")
    
    repetitions = int(input("Hoe vaak wilt u de opname herhalen? (0 voor oneindig): \n"))
    if repetitions == 0:
        repetitions = -1  # stel in op -1 voor oneindig
    print("Opname wordt nu afgespeeld!")
    print("Als u de opname wilt pauzeren druk dan op de SHIFT-toets samen met de SPATIE-toets")
    print("Als u de opname wilt afsluiten druk dan op de SHIFT-toets samen met de ESC-toets")

    execute_from_file(chosen_file, repetitions)
