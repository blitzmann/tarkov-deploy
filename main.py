import time
import cv2
import numpy as np
from PIL import ImageGrab
import win32gui
import win32con
import win32api
import win32com, win32com.client
import re
from playsound import playsound
import jstyleson as json
from os import path
import sys
from collections import deque

import pytesseract
from pytesseract import TesseractNotFoundError

q = deque(maxlen=100)
root = None

if hasattr(sys, '_MEIPASS'):
    root = sys._MEIPASS
base = getattr(sys.modules['__main__'], "__file__", sys.executable) if hasattr(sys, 'frozen') else __file__
root = path.dirname(path.realpath(path.abspath(base)))

path_to_audio = path.abspath(path.join(root, 'assets', 'audio.wav'))

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
        cfg["auto_accept"]["bounding_box"]["left"],
        cfg["auto_accept"]["bounding_box"]["right"],
        cfg["auto_accept"]["bounding_box"]["top"],
        cfg["auto_accept"]["bounding_box"]["bottom"])
    text = convert_image_to_text(img)
    matches = re.finditer(r"(.+) wants to invite you", text, re.IGNORECASE | re.MULTILINE)

    for matchNum, match in enumerate(matches, start=1):
        person = match.groups()
        person = person[0]
        print("Invite from `{}`".format(person))
        allowed = [x.lower() for x in cfg["auto_accept"]["allowed_names"]]
        if len(allowed) == 0 or person.lower() in allowed:
            print("Invite allowed!".format(person))
            try:
                # Tarkov doesn't accept inputs unless it's in the foreground
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                # https://stackoverflow.com/a/46092
                win32gui.ShowWindow(hwnd, 9)
                win32gui.SetForegroundWindow(hwnd)
                win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x59, 0)
                time.sleep(0.5)
                win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x59, 0)
            except Exception as ex:
                print("Failed to bring window to foreground, err: {}".format(ex))

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

loading_symbols = ['|', '/', '-', '\\']

def runningMeanFast(x, N):
    return np.convolve(x, np.ones((N,))/N)[(N-1):]

try:
    i = 0
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
        limiter = 0.5  # min seconds to wait between loops
        while True:
            start_time = time.time()
            # auto-accept invites
            if cfg["auto_accept"]["enabled"]:
                auto_accept_invite(hwnd)

            # deployment warning
            if cfg["deploy_warning"]["enabled"]:
                deployment_warning(hwnd)

            # One screenshot per second
            elapsed = time.time() - start_time
            q.append(elapsed)
            print('Waiting {0} Avg loop time: {1:.3f}s'.format(loading_symbols[i % 4], sum(q) / len(q)), end="\r")
            i+=1
            remaining = limiter - elapsed
            if remaining > 0:
                time.sleep(remaining)

except TesseractNotFoundError:
    print(
        "tesseract is not installed or it's not in your PATH. Please find the Windows "
        "binaries for download here: https://github.com/UB-Mannheim/tesseract/wiki")
    input()
    sys.exit(1)