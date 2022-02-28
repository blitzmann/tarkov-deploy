import time
import cv2
import numpy as np
import imutils
from mss import mss
import pytesseract
from PIL import ImageGrab
import win32gui
import win32con
import win32api
import re
from playsound import playsound


toplist, winlist = [], []

def enum_cb(hwnd, results):
    winlist.append((hwnd, win32gui.GetWindowText(hwnd)))

win32gui.EnumWindows(enum_cb, toplist)

tarkov = [(hwnd, title) for hwnd, title in winlist if 'escapefromtarkov' in title.lower()]
# just grab the hwnd for first window matching firefox
tarkov = tarkov[0]
hwnd = tarkov[0]

names = [
    "AndBobsUrUncle",
    "Lt_Lippski"
]

while True:
    # win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)

    #auto-accept invites
    game_width = bbox[2] - bbox[0]
    game_height = bbox[3] - bbox[1]
    x_gutters = int(game_width * .35)
    top_gutter = int(game_height * .42)
    bottom_gutter = int(game_height * .42)
    win32gui.SetForegroundWindow(hwnd)
    new_box = (
        bbox[0] + x_gutters,
        bbox[1] + top_gutter,
        bbox[0] + x_gutters + (game_width - (x_gutters * 2)),
        bbox[3] - bottom_gutter
    )

    img = ImageGrab.grab(new_box)
    after_grab = time.time()
    # cv2.imshow('screen', np.array(img))
    # cv2.waitKey(0)
    im = np.asarray(img)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(im).lower()

    matches = re.finditer(r"(.+) wants to invite you", text, re.IGNORECASE | re.MULTILINE)
    for matchNum, match in enumerate(matches, start=1):
        person = match.groups()
        if person.lower() in (x.lower() for x in names):
            win32api.SendMessage(hwnd, win32con.WM_KEYDOWN, 0x59, 0)
            sleep(0.5)
            win32api.SendMessage(hwnd, win32con.WM_KEYUP, 0x59, 0)
        pass
        # check for

    # deployment sound

    game_width = bbox[2] - bbox[0]
    game_height = bbox[3] - bbox[1]
    x_gutters = int(game_width * .41)
    top_gutter = int(game_height * .45)
    bottom_gutter = int(game_height * .20)

    new_box = (
        bbox[0] + x_gutters,
        bbox[1] + top_gutter,
        bbox[0] + x_gutters + (game_width - (x_gutters * 2)),
        bbox[3] - bottom_gutter
    )

    img = ImageGrab.grab(new_box)
    after_grab = time.time()
    # cv2.imshow('screen', np.array(img))
    # cv2.waitKey(0)
    im = np.asarray(img)
    im = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)

    text = pytesseract.image_to_string(im).lower()

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
                playsound('./assets/audio.wav')
            cv2.imshow('test', np.array(im))
            break;
        time.sleep(5)

    # Press "q" to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    # One screenshot per second
    elapsed = time.time() - after_grab
    print('Took: {0}'.format(elapsed))

