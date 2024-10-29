import os
import sys
import json
import wmi
import requests
import base64
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import re
import shutil
import random
from natsort import natsorted
from datetime import datetime, timedelta, time as dtime
from time import sleep, time
import threading
import traceback
import pyttsx3
import winreg
from moviepy.video.fx.all import resize, crop, mirror_x, speedx
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, afx, CompositeVideoClip, ImageClip, ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip
from imageio import imwrite
from pydub import AudioSegment
from unidecode import unidecode
import yt_dlp
import portalocker
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium_stealth import stealth
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import subprocess
import pickle
import wmi
import platform
from tkinter import messagebox, filedialog
import customtkinter as ctk
import ctypes
import tempfile
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow

is_dev_enviroment = True
def get_current_dir():
    """Lấy thư mục đang chạy tệp thực thi"""
    global is_dev_enviroment
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
        is_dev_enviroment = False
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        is_dev_enviroment = True
    return current_dir
current_dir = get_current_dir()
sys.path.append(current_dir)

def detect_debugger():
    if is_dev_enviroment:
        print("Không thể khởi động chương trình ở môi trường phát triển !!!")
        sys.exit(1)
    if sys.gettrace():
        print("Debugger detected! Exiting...")
        sys.exit(1)
    debugger_modules = ['pdb', 'pydevd', 'pydev']
    for module in debugger_modules:
        if module in sys.modules:
            print(f"Debugger module detected: {module}. Exiting...")
            sys.exit(1)
    for frame in sys._current_frames().values():
        if frame.f_lineno in range(1, 100):  # Kiểm tra các dòng có thể chứa breakpoint
            print("Breakpoint detected in current frame! Exiting...")
            sys.exit(1)
def detect_virtual_machine():
    c = wmi.WMI()
    for system in c.Win32_ComputerSystem():
        if "Virtual" in system.Manufacturer or "VMware" in system.Manufacturer:
            print("Virtual machine detected! Exiting...")
            sys.exit(1)

def getlog(lock=None):
    try:
        print(traceback.print_exc())
        if lock:
            lock["log"].acquire()
            with open("log.txt", "a", encoding='utf-8') as logf:
                logf.write(str(datetime.now()))
                traceback.print_exc(file=logf)
            lock["log"].release()
        else:
            with open("log.txt", "a", encoding='utf-8') as logf:
                logf.write(str(datetime.now()))
                traceback.print_exc(file=logf)
    except:
        pass

def get_disk_serial():
    c = wmi.WMI()
    for disk in c.Win32_DiskDrive():
        for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                if logical_disk.DeviceID == "C:" or logical_disk.DeviceID == "c:":
                    return disk.SerialNumber

def load_private_key():
    with open("import\\private_key.pem", "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,  # Mật khẩu của khóa bí mật
            backend=default_backend()
        )
    return private_key

def sign_data(data, private_key):
    signature = private_key.sign(
        data,
        padding.PKCS1v15(),
        hashes.SHA256()
    )
    return base64.b64encode(signature).decode('utf-8')

def read_file(file_path):
    with open(file_path, 'rb') as f:
        return f.read()
    
def send_file_to_server(file_data, signature, serial):
    url = "http://127.0.0.1:5000/api/verify_start"
    payload = {
        "file_content": base64.b64encode(file_data).decode('utf-8'),
        "signature": signature,
        "serial": serial
    }
    response = requests.post(url, json=payload)
    return response
def run_py_files(py_files):
    for filename, file_content_base64 in py_files.items():
        file_content = base64.b64decode(file_content_base64).decode('utf-8')
        exec(file_content, globals())
def main():
    # detect_debugger()
    # detect_virtual_machine()
    file_path = os.path.join(current_dir, 'start.py')
    file_data = read_file(file_path)
    private_key = load_private_key()
    signature = sign_data(file_data, private_key)

    serial = get_disk_serial().strip()
    response = send_file_to_server(file_data, signature, serial)

    if response.status_code == 200:
        pyc_files = response.json().get('pyc_files')
        try:
            run_py_files(pyc_files)
        except:
            pass

    else:
        print(f"Server returned error: {response.status_code}")

if __name__ == '__main__':
    main()
