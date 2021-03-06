import os
import logging
import cv2 as cv
import matplotlib.pyplot as plt
import numpy as np

# Takes a desktop image to find the tasksbar inside bottom split


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
def check_icon(desktop, icon_path, threshold=.4 , debug=0):
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
        print(icon)
        try:
            print(f'Attempting to read image from PATH={icon_path+icon}')
            logging.info(f'Attempting to read image from PATH={icon_path+icon}')
            ic_img = cv.imread(f"{icon_path}{icon}", cv.IMREAD_GRAYSCALE)
            kp_ic, des_ic = sift.detectAndCompute(ic_img, None)

            # BF Matcher
            bf = cv.BFMatcher()
            matches = bf.knnMatch(des_dt, des_ic, k=2)
            #Ratio Test
            good = []
            try:
                for m, n in matches:
                    if m.distance < threshold * n.distance:
                        good.append([m])
            except ValueError:
                pass

            #Homography
            min_match_count = 5
            if len(good)>min_match_count:
                src_pts = np.float32([ kp_dt[m.trainIdx].pt for m in good ]).reshape(-1,1,2)
                dst_pts = np.float32([ kp_ic[m.queryIdx].pt for m in good ]).reshape(-1,1,2)

                M, mask = cv.findHomography(src_pts, dst_pts, cv.RANSAC, 5.0)
                matchesMask = mask.ravel().tolist()

                h,w = dt_img.shape
                pts = np.float32([ [0,0],[0,h-1],[w-1,h-1],[w-1,0] ]).reshape(-1,1,2)
                dst = cv.perspectiveTransform(pts, M)

                dt_img = cv.polylines(dt_img,[np.int32(dst)],True,255,3,cv.LINE_AA)
            else:
                logging.info("Not enough matches are found")
                matchesMask = None

            draw_params = dict(matchColor=(0,255,0), singlePointColor=None, matchesMask=matchesMask, flags=2)

            if debug:
                img_test = cv.drawMatchesKnn(dt_img, kp_dt, ic_img, kp_ic, good, None, **draw_params)
                plt.imshow(img_test), plt.show()
                plt.imsave(f'debug_{icon}', img_test, dpi=350)
            res.append((len(good), icon))
        except AttributeError:
            logging.warning('Failed to read image from PATH={icon_path}')
    return res


