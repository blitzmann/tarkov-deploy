import time
import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import win32con
import win32api
import re
from playsound import playsound
import json
from os import path
import sys

import pytesseract
from pytesseract import TesseractNotFoundError

path_to_audio = path.abspath(path.join(path.dirname(__file__), 'assets', 'audio.wav'))

with open("config.json", "r") as file:
    cfg = json.load(file)

def capture_sub_window_percentage(hwnd, x_left, x_right, y_top, y_bottom):
    bbox = win32gui.GetWindowRect(hwnd)

    game_width = bbox[2] - bbox[0]
    game_height = bbox[3] - bbox[1]

    left_gutter = int(game_width * x_left)
    right_gutter = int(game_width * x_right)
    top_gutter = int(game_height * y_top)
    bottom_gutter = int(game_height * y_bottom)

    # win32gui.SetForegroundWindow(hwnd)
    new_box = (
        bbox[0] + left_gutter,
        bbox[1] + top_gutter,
        bbox[2] - right_gutter,
        bbox[3] - bottom_gutter
    )

    img = ImageGrab.grab(new_box)
    return img

def convert_image_to_text(img):
    im = np.asarray(img)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(im).lower()
    return text

def auto_accept_invite(hwnd):
    img = capture_sub_window_percentage(
        hwnd,
        cfg["auto_invite"]["bounding_box"]["left"],
        cfg["auto_invite"]["bounding_box"]["right"],
        cfg["auto_invite"]["bounding_box"]["top"],
        cfg["auto_invite"]["bounding_box"]["bottom"])
    text = convert_image_to_text(img)
    matches = re.finditer(r"(\n+) wants to invite you", text, re.IGNORECASE | re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):
        person = match.groups()
        print("Invite from `{}`".format(person))
        allowed = [x.lower() for x in cfg["auto_invite"]["allowed_names"]]
        if len(allowed) == 0 or person.lower() in allowed:
            print("Invite allowed!".format(person))
            # Tarkov doesn't accept inputs unless it's in the foreground
            win32gui.SetForegroundWindow(hwnd)
            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x59, 0)
            time.sleep(0.5)
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x59, 0)

def deployment_warning(hwnd):
    img = capture_sub_window_percentage(
        hwnd,
        cfg["deploy_warning"]["bounding_box"]["left"],
        cfg["deploy_warning"]["bounding_box"]["right"],
        cfg["deploy_warning"]["bounding_box"]["top"],
        cfg["deploy_warning"]["bounding_box"]["bottom"])
    text = convert_image_to_text(img)
    after_grab = time.time()
    if "get ready" in text or "deploying in" in text:
        print("found deployment text")
        text = text[text.find('deploying in:'):]
        text = "".join(text.split())
        matches = re.finditer(r"(\d+):(\d+).(\d+)", text)

        for matchNum, match in enumerate(matches, start=1):
            min, sec, frac = match.groups()
            print(min, sec, frac)
            wholeSec = float('{}.{}'.format(sec, frac))
            elapsed = time.time() - after_grab
            print('Took: {0}'.format(elapsed))
            newSec = wholeSec - elapsed
            print('Current spot {}'.format(newSec))
            sleep = newSec - int(newSec)
            print('Sleep {}'.format(sleep))
            time.sleep(sleep)

            for x in range(int(newSec)):
                playsound(path_to_audio)
            break
        time.sleep(5)

try:
    while True:

        toplist, winlist = [], []

        def enum_cb(hwnd, results):
            winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

        win32gui.EnumWindows(enum_cb, toplist)
        tarkov = [(hwnd, title) for hwnd, title in winlist if cfg["window_name"].lower() in title.lower()]
        if len(tarkov) == 0:
            print("Cannot find {} window.".format(cfg["window_name"]))
            time.sleep(5)
            continue

        tarkov = tarkov[0]
        hwnd = tarkov[0]

        while True:
            start_time = time.time()
            # auto-accept invites
            if cfg["auto_invite"]["enabled"]:
                auto_accept_invite(hwnd)

            # deployment warning
            if cfg["deploy_warning"]["enabled"]:
                deployment_warning(hwnd)

            # One screenshot per second
            elapsed = time.time() - start_time
            print('Took: {0}'.format(elapsed))
except TesseractNotFoundError:
    print(
        "tesseract is not installed or it's not in your PATH. Please find the Windows "
        "binaries for download here: https://github.com/UB-Mannheim/tesseract/wiki")
    input()
    sys.exit(1)