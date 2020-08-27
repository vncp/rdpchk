#!/usr/bin/env python3
import os
import sys
import subprocess
import requests
import json
import socket
import urllib3

from uuid import getnode as get_mac
from jinja2 import FileSystemLoader, Environment

urllib3.disable_warnings(urllib3.exceptions.SecurityWarning)

api_url = 'https://imm.engr.unr.edu/ipxe/api/host/'
certs = ("/etc/ssl/private/util.cert.pem","/etc/ssl/private/util.key.pem")

def get_hosts():

  params = {'hostname__istartswith': 'ecc', 'limit':1000 }
  r = requests.get(api_url, cert = certs, params = params)

  resp_json = r.json()

  return resp_json

