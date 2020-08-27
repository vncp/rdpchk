#Creates a copy image which crops the source image using numpy
#Vincent Pham

import cv2 as cv
import numpy as np


#Takes image from source and crops # pixel height
def crop_image(source, height):
    img = cv.imread(source)
    h, w, c = img.shape
    img = img[h-height:h, 0:w]
    cv.imwrite('/opt/rdpchk/source_taskbar.png', img, [cv.IMWRITE_JPEG_QUALITY, 100])

source_path = "/opt/rdpchk/source_connection.png"
crop_image(source_path, 40)
