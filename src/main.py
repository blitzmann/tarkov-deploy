import time
import cv2
import numpy as np
import imutils
from mss import mss
import pytesseract
from PIL import ImageGrab
import win32gui
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


while True:
    # win32gui.SetForegroundWindow(hwnd)
    bbox = win32gui.GetWindowRect(hwnd)
    img = ImageGrab.grab(bbox)
    after_grab = time.time()

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
                playsound('audio.wav')
            cv2.imshow('test', np.array(im))
            break;
        time.sleep(5)

    # Press "q" to quit
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    # One screenshot per second
    time.sleep(.5)

