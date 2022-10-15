import pyautogui
import pytesseract
import cv2
import os
from PIL import ImageGrab
import socket
import time

# Path of tesseract executable
pytesseract.pytesseract.tesseract_cmd ='/opt/homebrew/Cellar/tesseract/5.2.0/bin/tesseract'

PORT = 5000
HOST = '192.168.64.1'

VERBOSE_MODE = True
SAVE_SCREENSHOTS = True 
SAVE_OCR_DATA = True

#### server setup
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST, PORT))

def send(message):
    message = message.strip() + '\n'
    s.send(message.encode())

### global variables
specified_area = None
previous_command = None

# helper variables
SIZES = {
    "small": [50,50],
    "medium": [150,150],
    "large": [300, 300],
}

### built in functions
def osr_screen():
    img = ImageGrab.grab() 

    if SAVE_SCREENSHOTS:
        # generate unique filename
        filename = f"screenshots/{int(time.time())}.png"
        img.save(filename)

    ocr_data = pytesseract.image_to_data(img, lang='eng', output_type='dict', config='--psm 11')

    if SAVE_OCR_DATA:
        # generate unique filename
        filename = f"ocr_data/{int(time.time())}.txt"
        with open(filename, "w") as f:
            f.write(str(ocr_data))

    return ocr_data

def verbose(text):
    if VERBOSE_MODE:
        print(text)
        send(text)

def is_inside_specified_area(position):
    x = position[0]
    y = position[1]
    if specified_area:
        verbose(f"Checking if {position} is inside {specified_area}")
        if x < specified_area["left"] or x > specified_area["right"] or y < specified_area["top"] or y > specified_area["bottom"]:
            return False
    return True

def find_on_screen(phrase):
    ocr_data = osr_screen()
    if previous_command == "right_click":
        verbose("Previous command was right click, only looking below and to the right of the cursor")
        verbose(f"Cursor position: {pyautogui.position()}")

    phrase_length = len(phrase.split(" "))

    for idx, val in enumerate(ocr_data["text"]):
        if idx == len(ocr_data["text"]) - phrase_length:
            return False # phrase not found
            break

        # get phrase length in ocr_data
        ocr_data_text = ocr_data["text"][idx:idx + phrase_length]
        # strip spaces, join list to string
        ocr_data_text = " ".join(ocr_data_text).strip()

        divisor = 2 # for retina display

        if phrase in ocr_data_text:
            position = [int(ocr_data["left"][idx]), int(ocr_data["top"][idx])]
            position[0] = position[0]//divisor # x
            position[1] = position[1]//divisor # y

            if not is_inside_specified_area(position):
                continue

            if previous_command == "right_click":
                # only look below and to the right
                cursor_position = pyautogui.position()
                if position[1] < cursor_position[1] or position[0] < cursor_position[0]:
                    continue

            size = [int(ocr_data["width"][idx]), int(ocr_data["height"][idx])]
            size[0] = size[0]//divisor
            size[1] = size[1]//divisor
            middle_x = position[0] + size[0]//2
            middle_y = position[1] + size[1]//2
            verbose(f"Found {phrase} at {position} with size {size}")
            return [middle_x, middle_y]
            break

    return False # phrase not found


def click(phrase):
    position = find_on_screen(phrase)
    if position:
            pyautogui.click(position[0], position[1])
            verbose(f"Clicked {phrase} at {position}")
    else:
            verbose(f"Could not find {phrase}")

def specify_area(area):
    global specified_area

    # rectangle with left, right, top, bottom
    if area == "top":
        specified_area = {
            "left": 0,
            "right": pyautogui.size()[0],
            "top": 0,
            "bottom": pyautogui.size()[1]//2 # half of screen
        }
    elif area == "bottom":
        specified_area = {
            "left": 0,
            "right": pyautogui.size()[0],
            "top": pyautogui.size()[1]//2,
            "bottom": pyautogui.size()[1]
        }
    elif area == "left":
        specified_area = {
            "left": 0,
            "right": pyautogui.size()[0]//2,
            "top": 0,
            "bottom": pyautogui.size()[1]
        }
    elif area == "right":
        specified_area = {
            "left": pyautogui.size()[0]//2,
            "right": pyautogui.size()[0],
            "top": 0,
            "bottom": pyautogui.size()[1]
        }
    else:
        verbose("Invalid area")

def insert_text(phrase):
    pyautogui.write(phrase)

def press(key):
    allowed_keys = ['enter', 'up', 'down', 'left', 'right', 'space', 'tab', 'backspace', 'esc'] 
    if key in allowed_keys:
        pyautogui.press(key)
    else:
        verbose("Invalid key")

def find(phrase):
    pyautogui.hotkey('command', 'f')
    pyautogui.write(phrase)

def right_click(phrase):
    if phrase:
         position = find_on_screen(phrase)
         if position:
             pyautogui.click(position[0], position[1], button='right')
             verbose(f"Right clicked {phrase} at {position}")
         else:
             verbose(f"Could not find {phrase}")
    else:
        pyautogui.click(button='right')

def open_app(app):
    pyautogui.hotkey('command', 'space')
    time.sleep(0.5)
    insert_text(app)
    time.sleep(0.5)
    press('enter')

# add built in commands
commands = {
    "click": click,
    "in": specify_area,
    "type": insert_text,
    "press": press,
    "find": find,
    "right_click": right_click,
    "open": open_app,
}

history = []
while True:
    # reset specified area
    if previous_command != "in":
      specified_area = None

    # ask for command
    print("Asking for command")
    send("command")

    data = s.recv(1024)
    if not data:
        break
    data = data.decode()
    print(f"Received: {data}")

    command = ""
    phrase = ""
    words = data.split(" ")
    for word in words:
        if word in commands:
            if command != "":
                arg = phrase.strip()
                history.append(command + "(" + arg + ")")
                print(f"Executing: {command}({arg})")
                commands[command](arg)
                previous_command = command
            command = word
            phrase = ""
        else:
            phrase += word + " "
    if command != "":
        arg = phrase.strip()
        history.append(command + "(" + arg + ")")
        print(f"Executing: {command}({arg})")
        commands[command](arg)
        previous_command = command


s.close()
