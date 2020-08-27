#!/usr/bin/env python3
import argparse
import time
import subprocess
import ipxe
import multiprocessing as mp
import cv2 as cv
import numpy as np
import logging


username = "ecc-admin"
password = "M!ntychic13"

taskbar_path = "/opt/rdpchk/source_taskbar.png"
priv_path = "/opt/rdpchk/source_privacy.png"

logging.basicConfig(filename='rdpck.log',level=logging.DEBUG)

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
'''
def check_icon(desktop, icon_path, threshold=.4, debug=0):
    logging.info(f'Starting check_icon with desktop_path={desktop}, icon_path={icon_path}, threshold={threshold}')
    sift = cv.SIFT_create()
    try:
        logging.info(f'Attempting to read image from PATH={desktop}')
        dt_img = cv.imread(desktop, cv.IMREAD_GRAYSCALE)
    except AttributeError:
        logging.warning('Failed to read image from PATH={desktop}.')
    kp_dt, des_dt = sift.detectAndCompute(dt_img, None)
    for icon in os.listdir(icon_path):
        try:
            logging.info(f'Attempting to read image from PATH={icon_path}')
            ic_img = cv.imread("taskbar.png", cv.IMREAD_GRAYSCALE)
            kp_ic, des_ic = sift.detectAndCompute(ic_img, None)
            bf = cv.BFMatcher()
            matches = bf.knnMatch(des_dt, des_ic, k=2)
            good = []
            for m, n in matches:
                if m.distance < threshold * n.distance:
                    good.append([m])
            #img_test = cv.drawMatchesKnn(dt_img, kp_dt, ic_img, kp_ic, good, None, flags=cv.DRAW_MATCHES_FLAGS_NOT_DRAW_SINGLE_POINTS)
    #return len(good)
'''


def run_freerdp(hostname):
  command = ['xfreerdp', '-compression', '/cert-ignore', f'/v:{hostname}', f'/u:{hostname}\{username}',f'/p:{password}', '/app:C:\Windows\System32\notepad.exe']
  subprocess.run(command)

def run_scrot(hostname):
  path = f'/tmp/rdpchk/{hostname}'
  command = ['mkdir', '-p', path]
  subprocess.run(command)
  full_path = f'{path}/test.png'
  command=['scrot', full_path]
  subprocess.run(command)
  return full_path 

def main():
  #parser = argparse.ArgumentParser(description="Connect and take screenshots")
  #parser.add_argument('hostname', type=str)
  #args = parser.parse_args()
  hosts = ipxe.get_hosts()
  # Writes if it found a matching taskbar
  for h in hosts['objects']:
    #Gets prior screenshot to see if a connection failed
    command = ['scrot', '/opt/rdpchk/source_connection.png']
    subprocess.run(command)
    hostname = h['hostname']
    print(hostname)
    ip = h.get('ip', None)
    command = ['xfreerdp', '/f', '/cert-ignore', f'/v:{hostname}', f'/u:{hostname}\{username}',f'/p:{password}']
    rdp_proc=subprocess.Popen(command)
    time.sleep(20)
    status = open("rdp_status.txt", "a")
    scrot_path = run_scrot(hostname)
    res = check_desktop(scrot_path, taskbar_path) 
    if res is None:
        res0 = check_desktop(scrot_path, priv_path, confidence=.8, split=1)
        if res0 is None:
            status.write(f'0: {scrot_path} failed to find taskbar\n')
            print(f'{scrot_path} did not find taskbar!')
            logging.info(f'{scrot_path} did not find taskbar')
        else:
            status.write(f'2: {scrot_path} found privacy prompt.\n')
            print(f'{scrot_path} found privacy prompt!')
            logging.info(f'{scrot_path} found privacy prompt')
    else:
         status.write(f'1: {scrot_path} found taskbar\n')
         print(f'{scrot_path} found taskbar.')
         logging.info(f'{scrot_path} found taskbar.')
    rdp_proc.terminate()
    status.close()



if __name__ == "__main__":
  main()
