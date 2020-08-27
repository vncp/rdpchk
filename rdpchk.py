#!/usr/bin/env python3
import argparse
import time
import subprocess
import ipxe
import multiprocessing as mp
import cv2 as cv
import numpy as np
import logging
from check import *


username = "ecc-admin"
password = "M!ntychic13"

taskbar_path = "/opt/rdpchk/src/source_taskbar.png"
priv_path = "/opt/rdpchk/src/source_privacy.png"

logging.basicConfig(filename='rdpck.log',level=logging.DEBUG)



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
