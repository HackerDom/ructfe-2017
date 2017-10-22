#!/usr/bin/python3
import os
import sys

from webserver.webserver import start_web_server

sys.path.append(os.getcwd())
start_web_server()
