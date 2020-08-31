import cv2 as cv
import numpy as np
import logging
import os

# The path where the icons are at
icon_path = "icons/"
result_path = "icons_resized/"
icon_icon_path = "shortcut icon.PNG"

ic_img = cv.imread(icon_icon_path)
ic = cv.resize(ic_img, (16, 16))
ic = cv.flip(ic, 1)
ic = cv.rotate(ic, cv.ROTATE_90_COUNTERCLOCKWISE)
for icon in os.listdir(icon_path):
    img = cv.imread(icon_path+icon)
    res = cv.resize(img, (64, 64))
    #for x in range(16):
    #    for y in range(16):
    #        res[48+y, x] = ic[x, y]
    for x in range(64):
        for y in range(64):
            if res[y, x][0] == 0 and res[y, x][1] == 0 and res[y, x][2] == 0:
                res[y, x] = (125, 125, 125)
    cv.imwrite(result_path+icon, res)