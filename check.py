import os
import logging
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

# Takes a desktop image to find the tasksbar inside bottom split
from joblib.numpy_pickle_utils import xrange


def check_desktop(desktop, template, confidence=.75, split=4, debug=0):
    try:
        logging.info(f'Atempting to read image from PATH={desktop}.')
        dt_img = cv.imread(desktop, 0)
        h, w = dt_img.shape
    except AttributeError:
        logging.warning(f'Failed to read image from PATH={desktop}.')
        logging.debug('Failure when trying to instantiate dt_img.')
        return None
    dt_img = dt_img[(split - 1) * int(h / split):h, 0:w]

    if debug:
        try:
            logging.info(f'Attempting to read image from PATH={desktop}.')
            dt_res = cv.imread(desktop)
            ch, cw, cc = dt_res.shape
        except AttributeError:
            logging.warning(f'Failed to read image from PATH={desktop}.')
            logging.debug('Failure when trying to instantiate dt_res.')
            return None
        dt_res = dt_res[(split - 1) * int(ch / split):ch, 0:cw]

    try:
        logging.info(f'Attempting to read image from PATH={template}.')
        src_img = cv.imread(template, 0)
        sw, sh = src_img.shape
    except AttributeError:
        logging.warning(f'Failed to read image from PATH={template}.')
        logging.debug('Failure when trying to instantiate src_img.')
        return None

    res = cv.matchTemplate(dt_img, src_img, cv.TM_CCOEFF_NORMED)
    threshold = confidence
    pts = np.where(res >= threshold)

    rect = None
    for pt in zip(*pts):
        rect = (pt[::-1], (pt[1] + sh, pt[0] + sw))
        if debug:
            cv.rectangle(dt_res, rect[0], rect[1], (0, 255, 0), 2)

    if debug:
        cv.imshow("Debug Result", dt_res)
        cv.waitKey(0)

    return rect

# Creates an edge from the icon using OpenCV canny() then tries to match
# at multiple scales on the desktop
# Returns amount of matches over a threshold
def check_icon(desktop, icon_path, threshold=.35, debug=0):
    logging.info(f'Starting check_icon with desktop_path={desktop}, icon_path={icon_path}, threshold={threshold}')
    sift = cv.SIFT_create()
    try:
        logging.info(f'Attempting to read image from PATH={desktop}')
        dt_img = cv.imread(desktop, cv.IMREAD_GRAYSCALE)
    except AttributeError:
        logging.warning('Failed to read image from PATH={desktop}.')
    kp_dt, des_dt = sift.detectAndCompute(dt_img, None)

    res = []
    for icon in os.listdir(icon_path):
        try:
            logging.info(f'Attempting to read image from PATH={icon_path}')
            ic_img = cv.imread(f"icons/{icon}", cv.IMREAD_GRAYSCALE)
            kp_ic, des_ic = sift.detectAndCompute(ic_img, None)

            # FLANN Matcher
            flann_index_kdtree = 0
            index_params = dict(algorithm=flann_index_kdtree, trees = 5)
            search_params = dict(check=50)
            flann = cv.FlannBasedMatcher(index_params, search_params)
            matches = flann.knnMatch(des_dt, des_ic, k=2)

            # BF Matcher
            # bf = cv.BFMatcher()
            # matches = bf.knnMatch(des_dt, des_ic, k=2)

            #Mask Matches
            matchesMask = [[0,0] for i in xrange(len(matches))]
            #Ratio Test
            for i,(m,n) in enumerate(matches):
                if m.distance < threshold*n.distance:
                    matchesMask[i]=[1,0]

            draw_params = dict(matchColor=(0,255,0), singlePointColor=(255,0,0), matchesMask=matchesMask, flags=0)
            good = []
            for m, n in matches:
                if m.distance < threshold * n.distance:
                    good.append([m])
            if debug:
                img_test = cv.drawMatchesKnn(dt_img, kp_dt, ic_img, kp_ic, matches, None, **draw_params)
                plt.imshow(img_test), plt.show()
                plt.imsave(f'debug_{icon}', img_test, dpi=350)
            res.append((len(good), icon))
        except AttributeError:
            logging.warning('Failed to read image from PATH={icon_path}')
    return res


