import time
import cv2
import numpy as np
import imutils
from mss import mss
import pytesseract
from PIL import ImageGrab
import win32gui
import re

template = cv2.imread("template2.png")
template = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
template = cv2.Canny(template, 50, 200)
(h, w) = template.shape[:2]
cv2.imshow('TEMPLATE_edge', template)

start_time = time.time()
mon = {'top': 0, 'left': 0, 'width': 2560, 'height': 1440}
with mss() as sct:
    while True:
        last_time = time.time()
        img = sct.grab(mon)
        img = np.array(img)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        edged = cv2.Canny(gray, 20, 200)

        found = None

        sp = np.linspace(0.2, 1, 50)
        for scale in sp[::-1]:

            resized = imutils.resize(gray, width=int(gray.shape[1] * scale))
            r = gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < h or resized.shape[1] < w:
                break

            edged = cv2.Canny(resized, 50, 30)
            result = cv2.matchTemplate(edged, template, cv2.TM_CCOEFF)

            (_, maxVal, _, maxLoc) = cv2.minMaxLoc(result)
                # cv2.rectangle(img_rgb, pt, (pt[0] + w, pt[1] + h), (0, 0, 255), 2)
            print(maxVal)
            clone = np.dstack([edged, edged, edged])
            cv2.rectangle(clone, (maxLoc[0], maxLoc[1]), (maxLoc[0] + w, maxLoc[1] + h), (0, 255, 0), 2)
            cv2.imshow('visualize', clone)
            cv2.waitKey(0)

            if found is None or maxVal > found[0]:
                found = (maxVal, maxLoc, r)

        if found is None:
            print('NOT FOUND! The loop took: {0}'.format(time.time() - last_time))
            continue

        (con, maxLoc, r) = found
        print("CONFIDENCE", con)
        (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
        (endX, endY) = (int((maxLoc[0] + w) * r), int((maxLoc[1] + h) * r))

        cv2.rectangle(img, (startX, startY), (endX, endY), (180, 105, 255), 2)

        print('FOUND! The loop took: {0}'.format(time.time() - last_time))
        cv2.imshow('test', np.array(img))

        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
