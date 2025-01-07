import json
import sys
import os
import re
import shutil
import random
from natsort import natsorted
from datetime import datetime, timedelta, timezone, time as dtime
from time import sleep, time
import threading
import traceback
import winreg
import requests
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
import subprocess
import ffmpeg
import pickle
import platform
from tkinter import messagebox, filedialog
import customtkinter as ctk
import ctypes
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import keyboard
import pyperclip
import whisper
import torch
import gc
from imageio import imwrite
from moviepy.editor import VideoFileClip, AudioFileClip, vfx
from pydub import AudioSegment
import math
from TTS.api import TTS
from PyQt5.QtWidgets import QApplication, QWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QGuiApplication

print(f'is_cuda_available: {torch.cuda.is_available()}')
device = "cpu"
# device = "cuda" if torch.cuda.is_available() else "cpu"

# def get_disk_serial():
#     c = wmi.WMI()
#     for disk in c.Win32_DiskDrive():
#         for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
#             for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
#                 if logical_disk.DeviceID == "C:" or logical_disk.DeviceID == "c:":
#                     return disk.SerialNumber

def get_chrome_profile_folder():
    if platform.system() == "Windows":
        profile_folder = os.path.join(os.environ['LOCALAPPDATA'], "Google", "Chrome", "User Data")
    elif platform.system() == "Darwin":
        profile_folder = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "Google", "Chrome")
    elif platform.system() == "Linux":
        profile_folder = os.path.join(os.path.expanduser("~"), ".config", "google-chrome")
    else:
        raise Exception("Hệ điều hành không được hỗ trợ.")
    return profile_folder

is_dev_enviroment = True
def get_current_dir():
    """Lấy thư mục đang chạy tệp thực thi"""
    if getattr(sys, 'frozen', False):
        current_dir = os.path.dirname(sys.executable)
        is_dev_enviroment = False
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        is_dev_enviroment = True
    return current_dir

current_dir = get_current_dir()
sys.path.append(current_dir)

chromedriver_path = os.path.join(current_dir, 'import\\chromedriver.exe')
config_path = os.path.join(current_dir, 'config.json')
config_xtts_path = os.path.join(current_dir, 'models', 'main', 'config.json')
last_config_xtts_path = os.path.join(current_dir, 'models', 'last_version', 'config.json')
last_model_path = os.path.join(current_dir, 'models', 'last_version', 'vietnamese', 'model.json')
ref_audio_folder = os.path.join(current_dir, 'models', 'ref_data')

icon_path = os.path.join(current_dir, 'import' , 'icon.png')
ico_path = os.path.join(current_dir, 'import' , 'icon.ico')

profile_folder = get_chrome_profile_folder()

padx = 5
pady = 2
height_element = 40
width_window = 500
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
left = 0.3
right = 0.7
LEFT = 'left'
RIGHT = 'right'
CENTER = 'center'

max_lenth_text = 300

def load_ffmpeg():
    def get_ffmpeg_dir():
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(__file__)
        ffmpeg_dir = os.path.join(base_dir, "ffmpeg", "bin")
        return ffmpeg_dir
    def is_ffmpeg_available():
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            return True
        except FileNotFoundError:
            return False
    if not is_ffmpeg_available():
        ffmpeg_dir = get_ffmpeg_dir()
        os.environ["PATH"] += os.pathsep + ffmpeg_dir
load_ffmpeg()

def get_driver(show=True):
    try:
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        if not show:
            options.add_argument('--headless')
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36")
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        stealth(driver,
                languages=["en-US", "en"],
                vendor="Google Inc.",
                platform="Win32",
                webgl_vendor="Intel Inc.",
                renderer="Intel Iris OpenGL Engine",
                fix_hairline=True
                )
        sleep(1)
        return driver
    except:
        getlog()
        print("Lỗi trong quá trình khởi tạo chromedriver.")
        return None
    
def get_driver_with_profile(target_gmail='default', show=True):
    try:
        os.system("taskkill /F /IM chrome.exe /T >nul 2>&1")
    except:
        pass
    sleep(1)
    def get_profile_name_by_gmail():
        def check_gmail_in_profile(profile_path):
            preferences_file = os.path.join(profile_path, "Preferences")
            
            if os.path.exists(preferences_file):
                with open(preferences_file, 'r', encoding='utf-8') as f:
                    try:
                        preferences = json.load(f)
                        if 'profile' in preferences:
                            for account in preferences['account_info']:
                                if 'email' in account and account['email'] == target_gmail:
                                    return True
                    except json.JSONDecodeError:
                        print(f"Không thể đọc file Preferences trong profile {profile_path}.")
            return False
        
        profiles = [name for name in os.listdir(profile_folder) if os.path.isdir(os.path.join(profile_folder, name)) and name.startswith("Profile")]
        if "Default" in os.listdir(profile_folder):
            profiles.append("Default")

        for profile_name in profiles:
            profile_path = os.path.join(profile_folder, profile_name)
            if os.path.exists(profile_path):
                if check_gmail_in_profile(profile_path):
                    return profile_name
        return None
    
    if target_gmail == 'default':
        profile_name = "Default"
    else:
        profile_name = get_profile_name_by_gmail()
    if profile_name:
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={profile_folder}")
        options.add_argument(f"profile-directory={profile_name}")
        if not show:
            options.add_argument("--headless")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(options=options)
        driver.maximize_window()
        return driver
    else:
        print(f'Không tìm thấy profile cho tài khoản google {target_gmail}')
        print("--> Hãy dùng cookies để đăng nhập !")
        return None

def scroll_into_view(driver, element):
    driver.execute_script("arguments[0].scrollIntoView(true);", element)
    sleep(0.2)
    
def get_element_by_text(driver, text, tag_name='*', timeout=10, multiple=False, not_contain_attribute=None):
    try:
        xpath = f'//{tag_name}[contains(text(), "{text}")]'
        if not_contain_attribute:
            xpath = f'//{tag_name}[contains(text(), "{text}") and not(@{not_contain_attribute})]'
        if multiple:
            elements = WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            return elements
        else:
            element = WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.XPATH, xpath))
            )
            return element
    except Exception as e:
        getlog()
        return None

def get_element_by_xpath(driver, xpath, key=None, index=0, multiple_ele=False, timeout=10):
    try:
        if multiple_ele:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_all_elements_located((By.XPATH, xpath))
            )
            return driver.find_elements(By.XPATH, xpath)

        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, xpath))
        )
        elements = driver.find_elements(By.XPATH, xpath)
        if key:
            key = key.lower()
            for ele in elements:
                if key in ele.accessible_name.lower() or key in ele.text.lower() or key in ele.tag_name.lower() or key in ele.aria_role.lower():
                    return ele
            return None
        if len(elements) > 0:
            return elements[index] 
    except:
        return None

def get_xpath(maintag, class_name=None, attribute=None, attribute_value=None, contain=False):
    if contain:
        if class_name:
            class_list = class_name.split()
            class_condition = " and ".join([f"contains(@class, '{cls}')" for cls in class_list])
        if attribute and attribute_value:
            xpath = f"//{maintag}[{class_condition} and @{attribute}=\"{attribute_value}\"]"
        else:
            xpath = f"//{maintag}[{class_condition}]"
    else:
        if attribute and attribute_value:
            xpath = f"//{maintag}[@class=\"{class_name}\" and @{attribute}=\"{attribute_value}\"]"
        else:
            xpath = f"//{maintag}[@class=\"{class_name}\"]"
    return xpath

def get_xpath_by_multi_attribute(maintag, attributes): #attributes = ['name="postSchedule"', ...]
    if len(attributes) > 1:
        attribute = " and @".join(attributes)
    else:
        attribute = attributes[0]
    attribute = f"@{attribute}"
    xpath = f"//{maintag}[{attribute}]"
    return xpath

def find_parent_element(element, level=1, tag_name=None, attribute=None, value=None):
    xpath = f"./ancestor::*[{level}]"
    if tag_name:
        xpath = f"./ancestor::{tag_name}[{level}]"
    if attribute and value:
        xpath += f"[contains(@{attribute}, '{value}')]"
    try:
        parent_element = get_element_by_xpath(element, xpath)
        return parent_element
    except:
        getlog()
        return None 
    
def find_child_element(element, level=1, tag_name=None, attribute=None, value=None):
    xpath = f"./descendant::*[{level}]"
    if tag_name:
        xpath = f"./descendant::{tag_name}[{level}]"
    if attribute and value:
        xpath += f"[contains(@{attribute}, '{value}')]"
    try:
        child_element = get_element_by_xpath(element, xpath)
        return child_element
    except:
        getlog()
        return None

def is_date_greater_than_current_day(date_str, day_delta=0):
    try:
        input_date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        print(f"Định dạng ngày {date_str} không hợp lệ ...")
        return False
    current_date = datetime.now().date()
    target_date = current_date + timedelta(days=day_delta)
    return input_date > target_date

def is_format_date_yyyymmdd(date_str, daydelta=None):
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not date_pattern.match(date_str):
        return False, "Định dạng ngày phải là yyyy-mm-dd"
    if daydelta:
        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Định dạng ngày phải là yyyy-mm-dd"
        current_date = datetime.now()
        if date_obj > current_date + timedelta(days=daydelta-1):
            return False, f"Date is more than {daydelta} days in the future"
    return True, "Valid date"

def convert_datetime_to_string(date):
    try:
        return date.strftime('%Y-%m-%d')
    except ValueError:
        print(f"ngày {date} không hợp lệ")
        return None
    
def convert_date_string_to_datetime(date_str):
    if not date_str:
        print("Ngày đầu vào không hợp lệ.")
        return None
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except:
        print(f"Định dạng ngày {date_str} phải là yyyy-mm-dd")
        return None
    
def add_date_into_string(date_str, day_gap):
    date  = convert_date_string_to_datetime(date_str)
    if date:
        date += timedelta(days=day_gap)
        return date.strftime("%Y-%m-%d")
    return None

def convert_time_to_seconds(time_str):
    try:
        list_time = time_str.split(':')
        cnt = len(list_time)
        if cnt == 3:
            return float(list_time[0]) * 3600 + float(list_time[1]) * 60 + float(list_time[2])
        elif cnt == 2:
            return float(list_time[0]) * 60 + float(list_time[1])
        elif cnt == 1:
            return float(list_time[0])
        else:
            print("Định dạng thời gian không hợp lệ")
            return None
    except:
        print("Định dạng thời gian không hợp lệ")
        return None

def set_autostart():
    try:
        # Lấy đường dẫn tới file app.py
        script_path = os.path.abspath(sys.argv[0])
        key = winreg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key_path = "VocabularyReminder"
        with winreg.OpenKey(
            key, key_value, 0, winreg.KEY_SET_VALUE
        ) as registry_key:
            winreg.SetValueEx(registry_key, key_path, 0, winreg.REG_SZ, script_path)
    except Exception as e:
        print(f"Could not set autostart: {e}")
# Hàm để xóa ứng dụng khỏi danh sách khởi động cùng Windows
def unset_autostart():
    try:
        key = winreg.HKEY_CURRENT_USER
        key_value = "Software\\Microsoft\\Windows\\CurrentVersion\\Run"
        key_path = "VocabularyReminder"
        with winreg.OpenKey(
            key, key_value, 0, winreg.KEY_SET_VALUE
        ) as registry_key:
            winreg.DeleteValue(registry_key, key_path)
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Could not unset autostart: {e}")

def remove_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

def get_json_data(file_path=""):
    try:
        if os.path.exists(file_path):
            if file_path.endswith('.json'):
                with open(file_path, "r", encoding="utf-8") as file:
                    portalocker.lock(file, portalocker.LOCK_SH)
                    p = json.load(file)
                    portalocker.unlock(file)
            elif file_path.endswith('.pkl'):
                with open(file_path, "rb") as file:
                    portalocker.lock(file, portalocker.LOCK_SH)
                    p = pickle.load(file)
                    portalocker.unlock(file)
            elif file_path.endswith('.txt'):
                with open(file_path, "r", encoding="utf-8") as file:
                    p = file.readlines()
        return p
    except:
        getlog()
        return None

def save_to_json_file(data, file_path):
    try:
        if file_path.endswith('.json'):
            with open(file_path, "w", encoding="utf-8") as file:
                portalocker.lock(file, portalocker.LOCK_EX)
                json.dump(data, file, indent=3)
                portalocker.unlock(file)
        else:
            with open(file_path, "wb") as file:
                portalocker.lock(file, portalocker.LOCK_EX)
                pickle.dump(data, file)
                portalocker.unlock(file)
    except:
        getlog()


def get_txt_data(file_path):
    if not os.path.isfile(file_path):
        return None
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    return content

def save_list_to_txt(data_list, file_path):
    with open(file_path, "w", encoding="utf-8") as file:
        for item in data_list:
            file.write(f"{item}\n")

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

def get_float_data(float_string):
    try:
        value = float(float_string)
        return value
    except:
        return None

def check_folder(folder, is_create=False, noti=True):
    try:
        if not os.path.exists(folder):
            if is_create:
                os.makedirs(folder, exist_ok=True)
            else:
                if noti:
                    print(f'Thư mục {folder} không tồn tại.')
                return False
        return True
    except:
        if noti:
            print(f'{folder} không phải là đường dẫn thư mục hợp lệ !!!')
        return False
    
def get_output_folder(input_video_path, output_folder_name='output_folder'):
    folder_input, file_name = get_current_folder_and_basename(input_video_path)
    output_folder = f'{folder_input}/{output_folder_name}'
    os.makedirs(output_folder, exist_ok=True)
    return output_folder, file_name

def get_current_folder_and_basename(input_video_path):
    folder_input = os.path.dirname(input_video_path)
    file_name = os.path.basename(input_video_path)
    return folder_input, file_name #file_name bao gồm phần mở rộng

def download_video_by_bravedown(video_urls, download_folder=None, root_web="https://bravedown.com/ixigua-video-downloader"):
    try:
        driver = get_driver(show=True)
        def choose_downlaod_folder():
            if download_folder:
                driver.get("chrome://settings/downloads")
                pyperclip.copy(download_folder)
                sleep(1)
                press_TAB_key(driver, 2)
                sleep(0.5)
                press_SPACE_key(driver, 1)
                sleep(0.5)
                press_key_on_window('tab', 4)
                press_key_on_window('space', 1)
                keyboard.send('ctrl+v')
                press_key_on_window('enter', 4)
                sleep(1)
            sleep(1)
        choose_downlaod_folder()
        def verify_human(video_url):
            ele = get_element_by_text(driver, "Please verify you are human!")
            if ele:
                sleep(3)
                press_TAB_key(driver)
                press_SPACE_key(driver)
                sleep(3)
                input_url(video_url)
        def input_url(video_url):
            xpath = get_xpath_by_multi_attribute('input', ['id="input"'])
            ele = get_element_by_xpath(driver, xpath)
            ele.clear()
            ele.send_keys(video_url)
            sleep(1)
            press_ENTER_key(driver, 1)
            sleep(2)
 
        def get_max_resolution_video():
            try:
                xpath = get_xpath('i', 'fas fa-volume-up')
                ele = get_element_by_xpath(driver, xpath, index=-1)
                return ele
            except:
                return None
        cnt=0
        download_from, root_web = get_download_flatform(video_urls[0])
        driver.get(root_web)
        sleep(5)
        for video_url in video_urls.copy():
            if cnt==0:
                verify_human(video_url)
            else:
                driver.get(root_web)
                sleep(2)
            input_url(video_url)
            ele = get_max_resolution_video()
            if not ele:
                continue
            parent = find_parent_element(ele, 1, 'a')
            url_data = parent.get_attribute("data-linkdown")
            driver.get(url_data)
            sleep(2)
            cnt += 1
            video_urls.remove(video_url)
            sleep(2)
            print(f'Tải thành công video: {video_url}')
        if cnt > 0:
            print(f'  --> Đã tải được {cnt} video.')
            return True
        else:
            return False
    except:
        getlog()
        print("Có lỗi khi tải video từ web !!!")
        return False
    finally:
        if driver:
            driver.quit()

def get_download_flatform(video_url):
    if "//www.douyin.com/" in video_url:
        download_flatform = "douyin"
        root_web = "https://bravedown.com/douyin-video-downloader"
    elif "//www.youtube.com/" in video_url or "youtu.be/" in video_url:
        download_flatform = "youtube"
        root_web = "https://bravedown.com/youtube-video-downloader"
    elif "//www.facebook.com/" in video_url:
        download_flatform = "facebook"
        root_web = "https://bravedown.com/facebook-video-downloader"
    elif "//www.instagram.com/" in video_url:
        download_flatform = "instagram"
        root_web = "https://bravedown.com/instagram-video-downloader"
    elif "//www.twitter.com/" in video_url or "//twitter.com/" in video_url:
        download_flatform = "twitter"
        root_web = "https://bravedown.com/twitter-video-downloader"
    elif "//www.tiktok.com/" in video_url:
        download_flatform = "tiktok"
        root_web = "https://bravedown.com/tiktok-downloader"
    elif "//www.vimeo.com/" in video_url:
        download_flatform = "vimeo"
        root_web = "https://bravedown.com/vimeo-downloader"
    elif "//www.reddit.com/" in video_url:
        download_flatform = "reddit"
        root_web = "https://bravedown.com/reddit-downloader"
    elif "//www.dailymotion.com/" in video_url:
        download_flatform = "dailymotion"
        root_web = "https://bravedown.com/dailymotion-video-downloader"
    elif "//www.vk.com/" in video_url:
        download_flatform = "vk"
        root_web = "https://bravedown.com/vk-video-downloader"
    elif "//www.bilibili.com/" in video_url:
        download_flatform = "bilibili"
        root_web = "https://bravedown.com/bilibili-downloader"
    elif "//www.snapchat.com/" in video_url:
        download_flatform = "snapchat"
        root_web = "https://bravedown.com/snapchat-video-downloader"
    elif "baidu.com/" in video_url:
        download_flatform = "baidu"
        root_web = "https://bravedown.com/baidu-video-downloader"
    elif "www.threads.net/" in video_url:
        download_flatform = "threads"
        root_web = "https://bravedown.com/threads-downloader"
    elif "kuaishou.com/" in video_url:
        download_flatform = "kuaishou"
        root_web = "https://bravedown.com/kuaishou-video-downloader"
    else:
        download_flatform = "ixigua"
        root_web = "https://bravedown.com/ixigua-video-downloader"
    return download_flatform, root_web

def download_video_by_url(url, download_folder=None, file_path=None, return_file_path=False):
    t = time()
    if not url:
        return False
    if not download_folder:
        return False
    try:
        if not file_path:
            def get_file_path(file_name):
                chars = ["/", "\\", ":", "|", "?", "*", "<", ">", "\"", "."]
                for char in chars:
                    if char in file_name:
                        file_name = file_name.replace(char, "")
                    if len(file_name) > 100:
                        file_name = file_name[:100]
                file_path = os.path.join(download_folder, f"{file_name}.mp4")
                return file_path
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': f'{download_folder}/%(title)s.%(ext)s'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=False)
                title = info_dict.get('title', 'video')
                if title == 'video':
                    cnt = 1
                    while True:
                        file_path = os.path.join(download_folder, f"{title}_{cnt}.mp4")
                        if os.path.exists(file_path):
                            cnt += 1
                        else:
                            break
                else:
                    file_path = get_file_path(title)
                    cnt = 0
                    while True:
                        if os.path.exists(file_path):
                            cnt += 1
                            file_path = f"{file_path.split('.mp4')[0]}_{cnt}.mp4"
                        else:
                            break
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': file_path,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
        t1 = time() - t
        if t1 < 5:
            sleep(5-t1)
        print(f'Tải thành công video: {file_path}')
        if return_file_path:
            return file_path
        else:
            return True
    except:
        return None

def rename_files_by_index(folder_path, base_name="", extension="", start_index=1):
    try:
        start_index = int(start_index)
    except:
        start_index = 1
    if extension == "":
        files = [folder for folder in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, folder))]
    else:
        files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.endswith(extension)]
    files = natsorted(files)
    for index, file_name in enumerate(files, start=start_index):
        old_file_path = os.path.join(folder_path, file_name)
        if '<index>' in base_name:
            name = base_name.replace('<index>', str(index))
            new_file_name = f'{name}{extension}'
        else:
            print("Không có chuỗi <index> trong tên chung nên số thứ tự sẽ được đặt ở cuối tên file.")
            new_file_name = f"{base_name}{index}{extension}"
        new_file_path = os.path.join(folder_path, new_file_name)
        try:
            os.rename(old_file_path, new_file_path)
            print(f"Đã đổi tên {old_file_path} thành {new_file_path}")
        except:
            print(f"Đổi tên file {old_file_path} không thành công")

def remove_char_in_file_name(folder_path, chars_want_to_remove, extension=None):
    if not extension:
        extension = '.mp4'
    try:
        chars = chars_want_to_remove.split(',')
        if len(chars) == 0:
            return
        files = [file for file in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, file)) and file.endswith(extension)]
        files = natsorted(files)
        for i, file_name in enumerate(files):
            base_name = file_name.split(extension)[0]
            for char in chars:
                if char in base_name:
                    base_name = base_name.replace(char, "")
            old_file_path = os.path.join(folder_path, file_name)
            new_file_name = f"{base_name}{extension}"
            new_file_path = os.path.join(folder_path, new_file_name)
            try:
                os.rename(old_file_path, new_file_path)
                print(f"Đã đổi tên {old_file_path} thành {new_file_path}")
            except:
                print(f"Đổi tên file {old_file_path} không thành công")
    except:
        pass

def remove_or_move_file(input_video_path, is_delete=False, is_move=True, finish_folder_name='finished folder'):
    try:
        if is_delete:
            os.remove(input_video_path)
        elif is_move:
            videos_folder = os.path.dirname(input_video_path)
            finish_folder = os.path.join(videos_folder, f'{finish_folder_name}')
            os.makedirs(finish_folder, exist_ok=True)
            base_name = os.path.basename(input_video_path)
            move_file_path = os.path.join(finish_folder, base_name)
            shutil.move(input_video_path, move_file_path)
    except:
        print(f"Không thể xóa hoặc di chuyển file {input_video_path}")
        

def check_datetime_input(date_str, time_str):
    try:
        input_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
        current_time_plus_30 = datetime.now() + timedelta(minutes=30)
        if input_time <= current_time_plus_30:
            print(f'Thời gian muốn đăng vào là {time_str} ngày {date_str} không hợp lệ --> Phải đăng sau 30 phút so với thời điểm hiện tại.')
            return False
        return True
    except:
        print("Định dạng giờ không đúng hh:mm")
        return False

def get_upload_date(upload_date, next_day=False):
    current_date = datetime.now().date()
    if isinstance(upload_date, str):
        try:
            upload_date = convert_date_string_to_datetime(upload_date)
        except:
            upload_date = current_date
    try:
        if upload_date <= current_date:
            upload_date = current_date
    except:
        upload_date = current_date
    if next_day and upload_date == current_date:
        upload_date = upload_date + timedelta(days=1)
    return upload_date

def get_day_gap(day_gap):
    if not day_gap:
        day_gap = "1"
    try:
        day_gap = int(day_gap.strip())
    except:
        day_gap = 1
    return day_gap

def get_number_of_days(number_of_days):
    if not number_of_days:
        number_of_days = "10"
    try:
        number_of_days = int(number_of_days.strip())
    except:
        number_of_days = 1
    return number_of_days

def convert_boolean_to_Yes_No(value):
    if value:
        return 'Yes'
    else:
        return 'No'

def press_esc_key(cnt=1, driver=None):
    if driver:
        for i in range(cnt):
            actions = ActionChains(driver)
            actions.send_keys(Keys.ESCAPE).perform()
            sleep(0.3)

def press_TAB_key(driver, cnt=1):
    try:
        for i in range(cnt):
            actions = ActionChains(driver)
            actions.send_keys(Keys.TAB).perform()
            sleep(0.3)
    except:
        print("Không thể bấm nút TAB")

def press_SPACE_key(driver, cnt=1):
    try:
        for i in range(cnt):
            actions = ActionChains(driver)
            actions.send_keys(Keys.SPACE).perform()
            sleep(0.3)
    except:
        print("Không thể bấm nút SPACE")

def press_ENTER_key(driver, cnt=1):
    try:
        for i in range(cnt):
            actions = ActionChains(driver)
            actions.send_keys(Keys.ENTER).perform()
            sleep(0.3)
    except:
        print("Không thể bấm nút ENTER")

def press_key_on_window(key, cnt=1):
    """Bấm một phím trên Windows nhiều lần với khoảng nghỉ giữa các lần bấm."""
    try:
        for _ in range(cnt):
            keyboard.send(key)
            sleep(0.3)
    except:
        print(f"Không thể bấm nút {key.upper()}")

def get_views_text(views_ele):
    match = re.search(r'(\d+(?:\.\d+)?)([KMB]?)', views_ele)
    if match:
        number = float(match.group(1))
        unit = match.group(2)
        return f'{number}{unit}'
    return None

def get_view_count(view_count=""):
    if view_count:
        try:
            view_count = view_count.split('views')[0].strip()
            if 'B' in view_count:
                view_count = float(view_count.replace('B', '')) * 1000000000
            elif 'M' in view_count:
                view_count = float(view_count.replace('M', '')) * 1000000
            elif 'K' in view_count:
                view_count = float(view_count.replace('K', '')) * 1000
            else:
                view_count = int(float(view_count))
        except:
                getlog()
                view_count = 0
    else:
        view_count = 0
    return view_count

def get_image_from_video(videos_folder, position=None):
    try:
        if position:
            time_position = convert_time_to_seconds(position)
        else:
            print("Hãy chọn thời điểm trích xuất ảnh từ video.")
            return
    except:
        print("Định dạng thời điểm trích xuất ảnh không hợp lệ.")
        return
    videos = os.listdir(videos_folder)
    videos = [k for k in videos if k.endswith('.mp4')]      
    if len(videos) == 0:
        print(f"Không tìm thấy video trong thư mục {videos_folder}")
        return
    try:
        output_folder = os.path.join(videos_folder, 'images')
        os.makedirs(output_folder, exist_ok=True)
        for i, video_file in enumerate(videos):
            video_path = os.path.join(videos_folder, video_file)
            video_name = os.path.splitext(video_file)[0]
            image_path = os.path.join(output_folder, f'{video_name}.png')
            if os.path.exists(image_path):
                continue
            video = VideoFileClip(video_path)
            if ':' in position:
                extraction_time = time_position
            else:
                extraction_time = video.duration - time_position
            if extraction_time < 0 or extraction_time > video.duration:
                print(f'Thời điểm trích xuất ảnh vượt quá thời lượng của video {video_file}. Lấy thời điểm trích xuất ở cuối video')
                extraction_time = video.duration
            frame = video.get_frame(extraction_time)
            imwrite(image_path, frame)
            video.close()
    except:
        print("Có lỗi trong quá trình trích xuất ảnh từ video !!!")

def get_time_check_cycle(time_check_string):
    try:
        time_check = int(float(time_check_string))
    except:
        time_check = 0
    return time_check * 60

def get_random_audio_path(new_audio_folder):
    audios = get_file_in_folder_by_type(new_audio_folder, file_type=".mp3", is_sort=False)
    if not audios:
        return None
    return os.path.join(new_audio_folder, random.choice(audios))
    
def get_file_in_folder_by_type(folder, file_type=".mp4", start_with=None, is_sort=True, noti=True):
    try:
        if not os.path.exists(folder):
            if noti:
                print(f"Thư mục {folder} không tồn tại !!!")
            return None
        list_items = os.listdir(folder)
        if "." not in file_type:
            list_dirs = [d for d in list_items if os.path.isdir(os.path.join(folder, d)) and d.startswith(file_type)]
            if len(list_dirs) == 0:
                if noti:
                    print(f"Không tìm thấy thư mục bắt đầu với '{start_with}' trong {folder} !!!")
                return None
            return natsorted(list_dirs) if is_sort else list_dirs
        else:
            if start_with:
                list_files = [f for f in list_items if f.endswith(file_type) and f.startswith(start_with)]
            else:
                list_files = [f for f in list_items if f.endswith(file_type)]
            if len(list_files) == 0:
                if noti:
                    print(f"Không tìm thấy file {file_type} trong thư mục {folder} !!!")
                return None
            return natsorted(list_files) if is_sort else list_files
    except:
        return None

def move_file_from_folder_to_folder(folder1, folder2):
    try:
        for filename in os.listdir(folder1):
            folder1_file = os.path.join(folder1, filename)
            folder2_file = os.path.join(folder2, filename)
            if os.path.isfile(folder1_file):
                shutil.move(folder1_file, folder2_file)
    except:
        pass
        

#--------------------------CTK----------------------------

def choose_folder():
    folder_path = filedialog.askdirectory()
    return folder_path

def choose_file(file_type = "*"):
    file_path = filedialog.askopenfilename( title="Select a file", filetypes=(("All files", f"*.{file_type}"),) )
    return file_path

def message_aks(message):
    messagebox.askquestion(title="Question", message=message)
def warning_message(message):
    messagebox.showinfo(title="WARNING", message=message)
def notification(parent=None, message=""):
    try:
        if parent:
            parent.after(0, lambda: messagebox.showinfo(title="Notification", message=message))
        else:
            messagebox.showinfo(title="Notification", message=message)
    except:
        pass

def error_message(message):
    messagebox.showinfo(title="ERROR", message=message)

def clear_widgets(root):
    for widget in root.winfo_children():
        widget.pack_forget()

def create_button_icon(frame = None, command=None, image=None, side=None, width=60):
    button = ctk.CTkButton( master=frame, text="", command=command, image=image, width=width)
    if side:
        button.pack(side=side, padx=0, pady=0)
    else:    
        button.pack(padx=0, pady=0)
    return button

def create_button(frame = None, text="", command=None, width=width_window, compound="left", anchor="center", image=None, side=None, pady=pady, padx=padx):
    button = ctk.CTkButton(master=frame, text=text, command=command, image=image, width=width, height= height_element, compound=compound, anchor=anchor, )
    if side:
        button.pack(side=side, pady=pady, padx=padx)
    else:    
        button.pack(pady=pady, padx=padx)
    return button

def create_label(frame=None, text="", compound="center", anchor="w", width=width_window, height=height_element, wraplength=None, side=None):
    if not width:
        width = width
    wraplength = width - 20
    label = ctk.CTkLabel(master=frame, text=text, width=width, height= height_element, wraplength=wraplength, anchor=anchor, compound=compound)
    if side:
        label.pack(side=side, pady=pady, padx=padx)
    else:
        label.pack(pady=pady, padx=padx)
    return label

def create_frame(frame, fill='x', side=None):
    frame = ctk.CTkFrame(master=frame, height=height_element*0.9)
    frame.pack(padx=padx, pady=pady, fill=fill, side=side)
    return frame

def create_text_input(frame, width=width_window, placeholder=None, side="right", default="", is_password=False):
    if not width:
        width = width
    if is_password:
        text_input = ctk.CTkEntry(master=frame, width=width, height=height_element*0.8, placeholder_text=placeholder, textvariable=default, show="*")
    else:
        text_input = ctk.CTkEntry(master=frame, width=width, height=height_element*0.8, placeholder_text=placeholder, textvariable=default)
    text_input.pack(pady=pady, padx=padx, side=side)
    return text_input

def create_combobox(frame, values=None, variable=None, side=RIGHT, width=width_window, height=height_element):
    val=None
    if variable:
        val = ctk.StringVar(value=str(variable))

    combobox = ctk.CTkComboBox(master=frame, values=values, variable=val, width=width, height=height)
    combobox.pack(side=side, padx=padx, pady=pady)
    return combobox

def create_frame_label_and_progress_bar(frame, label_text="", width=width_window, left=left, right=right):
    label = create_label(frame=frame, text=label_text, side=LEFT, width=width*left, compound=LEFT)
    processbar = create_progress_bar(frame=frame, width=width*right, side=RIGHT)
    return frame, processbar

def create_progress_bar(frame=None, width=width_window):
    processbar = ctk.CTkProgressBar(master=frame, width=width)
    processbar.pack(padx=padx, pady=pady)
    return processbar

def create_frame_label_input_input(root, label_text="", place_holder1=None, place_holder2=None, width=width_window, left=0.25, mid=0.56, right=0.19):
    frame = create_frame(root)
    label = create_label(frame=frame, text=label_text, side=LEFT, width=width*left, compound=LEFT, anchor='w')
    entry1 = create_text_input(frame=frame, width=width*mid, placeholder=place_holder1, side=RIGHT)
    entry2 = create_text_input(frame=frame, width=width*right, placeholder=place_holder2)
    return entry1, entry2

def create_frame_label_and_input(root, label_text="", place_holder=None, width=width_window, left=left, right=right, is_password=False):
    frame = create_frame(root)
    label = create_label(frame=frame, text=label_text, side=LEFT, width=width*left, compound=LEFT, anchor='w')
    entry = create_text_input(frame=frame, width=width*right, placeholder=place_holder, is_password=is_password)

    return entry

def create_frame_button_input_input(root,text, width=width_window, place_holder1=None, place_holder2=None, command=None, left=0.25, mid=0.56, right=0.19):
    frame = create_frame(root)
    button = create_button(frame=frame, text=text, width=width*left, side=LEFT, command=command)
    entry1 = create_text_input(frame, width=width*mid, placeholder=place_holder1, side=RIGHT)
    entry2 = create_text_input(frame, width=width*right, placeholder=place_holder2)
    return entry1, entry2

def create_frame_button_and_input(root, text, width=width_window, place_holder=None, command=None, left=left, right=right):
    frame = create_frame(root)
    button = create_button(frame=frame, text=text, width=width*left, side=LEFT, command=command)
    entry = create_text_input(frame, width=width*right, placeholder=place_holder)
    return entry

def create_frame_button_and_combobox(root, text, command=None, width=width_window, values=None, variable=None, left=left, right=right):
    frame = create_frame(root)
    button = create_button(frame=frame, text=text, width=width*left, side=LEFT, command=command)
    combobox = create_combobox(frame, width=width*right, side=RIGHT, values=values, variable=variable)
    return combobox

def create_frame_button_and_button(root, text1, text2, command1=None, command2=None, width=width_window, left=left, right=right):
    frame = create_frame(root)
    button1 = create_button(frame=frame, text=text1, width=width*left , side=LEFT, command=command1)
    button2 = create_button(frame=frame, text=text2, width=width*right -15, side=RIGHT, command=command2)
    return button1, button2

#----------------------edit video/ audio--------------------------------

def run_command_ffmpeg(command, hide=True):
    try:
        if hide:
            subprocess.run(command, check=True, text=True, encoding='utf-8', stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            subprocess.run(command, check=True, text=True, encoding='utf-8', stdout=subprocess.DEVNULL)
        return True
    except:
        getlog()
        return False

def run_command_with_progress(command, duration):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        encoding='utf-8',
    )

    current_time = 0.0
    check=False
    for line in process.stdout:
        if 'out_time_ms=' in line:
            match = re.search(r'out_time_ms=(\d+)', line)
            if match:
                out_time_ms = int(match.group(1))
                current_time = out_time_ms / 1000000.0
                percent_complete = (current_time / duration) * 100
                sys.stdout.write(f'\rĐã xử lý: {percent_complete:.2f}%')
                sys.stdout.flush()
                check = True
    process.wait()
    return check

def get_video_info(input_file):
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,duration',
            '-of', 'json',
            input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        video_info = info['streams'][0]
        width = video_info['width']
        height = video_info['height']
        duration = video_info['duration']
        r_frame_rate = video_info.get('r_frame_rate', '0/1')
        numerator, denominator = map(int, r_frame_rate.split('/'))
        fps = numerator / denominator if denominator != 0 else 0
        return {
            'width': width,
            'height': height,
            'fps': fps,
            'duration': duration
        }
    except:
        try:
            clip = VideoFileClip(input_file)
            video_info = {}
            width, height = clip.size
            duration = clip.duration
            fps = clip.fps
            clip.close()
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'duration': duration
            }
        except:
            return None

def get_audio_info(audio_path):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", audio_path]
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    info = json.loads(result.stdout)
    streams_info = info.get("streams", [])
    if not streams_info:
        print(f"Lỗi: Không thể tìm thấy thông tin của audio {audio_path}")
        return None
    streams_info = streams_info[0]
    return streams_info

def get_image_info(image_path):
    try:
        with Image.open(image_path) as img:
            width, height = img.size
            return width, height
    except Exception as e:
        print(f"Không thể lấy thông tin ảnh từ {image_path}: {e}")
        return {'width': 0, 'height': 0}
    
def cut_video_by_timeline_use_ffmpeg(input_video_path, segments, is_connect='no', is_delete=False, fast_cut=True, get_audio=False):
    ti = time()
    if fast_cut:
        print("..........................")
        print("Bắt đầu cắt nhanh video...")
    else:
        print("Bắt đầu cắt video...")
    try:
        output_folder, file_name = get_output_folder(input_video_path, output_folder_name='cut_video')
        output_file_path = os.path.join(output_folder, file_name)
        temp_list_file = os.path.join(output_folder, "temp_list.txt")
        remove_file(temp_list_file)
        combine_videos = []
        video_info = get_video_info(input_video_path)
        if not video_info:
            return None, f"Không lấy được thông tin video {input_video_path}"
        duration = float(video_info['duration'])
        end = "0"
        try:
            segments = segments.split(',')
        except:
            print("Định dạng thời gian cắt là start-end với start,end là hh:mm:ss hoặc mm:ss hoặc ss")
            return None, "Có lỗi khi cắt video"
        for i, segment in enumerate(segments, start=0):
            segment = segment.strip()
            if i==0 and '-' not in segment:
                start, end = "0", segment
            elif '-' not in segment:
                start = str(end)
                end = segment
            else:
                start, end = segment.split('-')
            start = convert_time_to_seconds(start)
            end = convert_time_to_seconds(end)
            if start is None or end is None:
                print("Thời gian cắt không hợp lệ.")
                return
            if end > duration:
                end = duration
            base_name = file_name.split('.mp4')[0]
            index = 1
            if len(segments) == 1:
                segment_file_path = os.path.join(output_folder, file_name)
                if os.path.exists(segment_file_path):
                    segment_file_path = os.path.join(output_folder, f"{base_name}_{index}.mp4")
            else:
                segment_file_path = os.path.join(output_folder, f"{base_name}_{index}.mp4")
            while True:
                if os.path.exists(segment_file_path):
                    index +=1
                    segment_file_path = os.path.join(output_folder, f"{base_name}_{index}.mp4")
                else:
                    break

            if fast_cut:
                command = [
                    'ffmpeg', '-progress', 'pipe:1', '-accurate_seek', '-ss', str(start), '-i', input_video_path,
                    '-to', str(end - start), '-c:v', 'copy', '-c:a', 'copy', '-fps_mode', 'cfr',
                    '-y', segment_file_path, '-loglevel', 'quiet'
                ]
            else:
                command = [
                    'ffmpeg', '-progress', 'pipe:1', '-i', input_video_path, '-ss', str(start), '-to', str(end), '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', '-b:a', '192k', '-y', segment_file_path, '-loglevel', 'quiet'
                ]
            run_command_with_progress(command, duration)

            if get_audio:
                download_folder = os.path.join(output_folder, "extracted_audio")
                os.makedirs(download_folder, exist_ok=True)
                extract_audio_ffmpeg(video_path=segment_file_path, download_folder=download_folder)
            if is_connect:
                combine_videos.append(segment_file_path)


        if is_connect != 'no' and len(combine_videos) > 1:
            with open(temp_list_file, 'w', encoding= 'utf-8') as f:
                for video in combine_videos:
                    f.write(f"file '{video}'\n")
            command = connect_video(temp_list_file, output_file_path, fast_connect=is_connect == 'fast connect')
            run_command_ffmpeg(command)
            try:
                for video in combine_videos:
                    remove_file(video)
                remove_file(temp_list_file)
            except:
                pass
        cat = time() - ti
        print(f'---> Thời gian cắt video {input_video_path} là {int(cat)}s')
        return True, None
    except:
        return False, "Có lỗi trong quá trình cắt video!!!"



def merge_videos_use_ffmpeg(videos_folder, file_name=None, is_delete=False, videos_path=None, fast_combine=True):
    ti = time()
    if fast_combine:
        print("..........................")
        print("Bắt đầu nối nhanh video...")
    else:
        print("Bắt đầu nối video...")

    temp_file_path = os.path.join(videos_folder, "temp.txt")
    max_fps = 24
    if not videos_path:
        videos = get_file_in_folder_by_type(videos_folder)
        if not videos:
            return
        if len(videos) <= 1:
            return False, "Phải có ít nhất 2 video trong videos folder"
        videos_path = []
        with open(temp_file_path, 'w') as f:
            for video in videos:
                if video.endswith('.mp4'):
                    video_path = os.path.join(videos_folder, video)
                    video_info = get_video_info(video_path)
                    if not video_info:
                        warning_message(f"Dừng gộp video vì không lấy được thông tin từ video {video_path}")
                        return
                    fps = video_info['fps']
                    if fps > max_fps:
                        max_fps = fps
                    f.write(f"file '{video_path}'\n")
                    videos_path.append(video_path)
    else:
        with open(temp_file_path, 'w') as f:
            for video_path in videos_path:
                video_info = get_video_info(video_path)
                if not video_info:
                    warning_message(f"Dừng gộp video vì không lấy được thông tin từ video {video_path}")
                    return
                fps = video_info['fps']
                if fps > max_fps:
                    max_fps = fps
                if video_path.endswith('.mp4'):
                    f.write(f"file '{video_path}'\n")
        
    output_folder = f"{videos_folder}\\merge_videos"
    os.makedirs(output_folder, exist_ok=True)
    if file_name:
        file_path = f"{output_folder}\\{file_name}.mp4"
    else:
        file_path = f"{output_folder}\\merge_video.mp4"
    command = connect_video(temp_file_path, file_path, fast_connect=fast_combine, max_fps=max_fps)
    try:
        run_command_ffmpeg(command)
        try:
            remove_file(temp_file_path)
            if is_delete:
                for video_path in videos_path:
                    remove_file(video_path)
        except:
            pass
        noi = time() - ti
        print(f'Tổng thời gian nối là {noi}')
        return True, f"Gộp video thành công vào file {file_path}"
    except:
        return False, "Có lỗi trong quá trình gộp video"

def merge_audio_use_ffmpeg(videos_folder, file_name=None, fast_combine=True):
    if fast_combine:
        print("..........................")
        print("Bắt đầu nối nhanh audio...")
    else:
        print("Bắt đầu nối audio...")

    temp_file_path = os.path.join(videos_folder, "temp.txt")
    audios = get_file_in_folder_by_type(videos_folder, file_type=".mp3")
    if not audios:
        return
    if len(audios) <= 1:
        return False, "Phải có ít nhất 2 video trong videos folder"
    with open(temp_file_path, 'w') as f:
        for audio in audios:
            if audio.endswith('.mp3'):
                audio_path = os.path.join(videos_folder, audio)
                f.write(f"file '{audio_path}'\n")
    output_folder = f"{videos_folder}\\merge_audios"
    os.makedirs(output_folder, exist_ok=True)
    if file_name:
        file_path = f"{output_folder}\\{file_name}.mp3"
    else:
        file_path = f"{output_folder}\\merge_audio.mp3"
    command = connect_audio(temp_file_path, file_path, fast_connect=fast_combine)
    try:
        if run_command_ffmpeg(command):
            try:
                remove_file(temp_file_path)
            except:
                pass
            return True, f"Gộp audio thành công vào file {file_path}"
    except:
        getlog()
    return False, "Có lỗi khi gộp audio"


def connect_video(temp_file_path, output_file_path, fast_connect=True, max_fps=None):
    if fast_connect:
        print("---> đang nối nhanh video...")
        command = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, 
            '-vf', 'fps=30', '-c:v', 'libx264', '-crf', '23', '-preset', 'veryfast', 
            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-y', output_file_path, '-loglevel', 'quiet'
        ]
    else:
        print("---> đang nối video...")
        if max_fps:
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c:v', 'libx264', '-c:a', 'aac', '-r', f'{max_fps}', '-y', output_file_path, '-loglevel', 'quiet'
            ]
        else:
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c:v', 'libx264', '-c:a', 'aac', '-y', output_file_path, '-loglevel', 'quiet'
            ]
    return command

def connect_audio(temp_file_path, output_file_path, fast_connect=True):
    if fast_connect:
        print("---> đang nối nhanh audio...")
        command = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, 
            '-c:a', 'libmp3lame', '-b:a', '192k', '-y', output_file_path, '-loglevel', 'quiet'
        ]
    else:
        print("---> đang nối audio...")
        command = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, 
            '-c:a', 'libmp3lame', '-b:a', '192k', '-y', output_file_path, '-loglevel', 'quiet'
        ]
    return command
    
def add_watermark_by_ffmpeg(video_width, video_height, horizontal_watermark_position, vertical_watermark_position):
    try:
        if horizontal_watermark_position == 'center':
            horizontal_watermark_position = 50
        elif horizontal_watermark_position == 'left':
            horizontal_watermark_position = 0
        elif horizontal_watermark_position == 'right':
            horizontal_watermark_position = 100
        else:
            try:
                horizontal_watermark_position = float(horizontal_watermark_position)
                if horizontal_watermark_position > 100:
                    horizontal_watermark_position = 100
                elif horizontal_watermark_position < 0:
                    horizontal_watermark_position = 0
            except:
                horizontal_watermark_position = 50
        if vertical_watermark_position == 'center':
            vertical_watermark_position = 50
        elif vertical_watermark_position == 'top':
            vertical_watermark_position = 0
        elif vertical_watermark_position == 'bottom':
            vertical_watermark_position = 100
        else:
            try:
                vertical_watermark_position = float(vertical_watermark_position)
                if vertical_watermark_position > 100:
                    vertical_watermark_position = 100
                elif vertical_watermark_position < 0:
                    vertical_watermark_position = 0
            except:
                vertical_watermark_position = 50
        watermark_x = int(video_width * horizontal_watermark_position / 100)
        watermark_y = int(video_height * vertical_watermark_position / 100)
        return watermark_x, watermark_y
    except:
        return None, None


def get_and_adjust_resolution_from_clip(clip, scale_factor=0.997):
    width = int(clip.size[0] * scale_factor)
    height = int(clip.size[1] * scale_factor)
    resized_video = clip.resize((width, height))
    return resized_video

def check_vietnamese_characters(filename):
    vietnamese_pattern = re.compile(
        r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        r'ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]'
    )
    return bool(vietnamese_pattern.search(filename))

def edit_audio_ffmpeg(input_audio_folder, start_cut="0", end_cut="0", pitch_factor=None, speed=None, cut_silence=False, aecho=None, flanger='8', chorus='0.05'):
    try:
        speed = get_float_data(speed)
        if not speed:
            speed = 1
        if aecho:
            aecho = get_float_data(aecho)
            if not aecho:
                print("Thời gian thiết lập tạo tiếng vang cho audio không hợp lệ --> Không áp dụng tạo tiếng vang")
        pitch_factor = get_float_data(pitch_factor)
        if not pitch_factor:
            print("Cao độ không hợp lệ --> Đặt về 1")
            pitch_factor = 1.0
        try:
            start_cut = float(start_cut)
            end_cut = float(end_cut)
        except:
            print("Giá trị của start_cut và end_cut không hợp lệ. Đặt về 0.")
            start_cut = end_cut = 0

        import tempfile
        audios = get_file_in_folder_by_type(input_audio_folder, ".mp3")
        if not audios:
            return
        for audio in audios:
            input_audio_path = os.path.join(input_audio_folder, audio)
            audio_info = get_audio_info(input_audio_path)
            if not audio_info:
                return
            duration = float(audio_info.get("duration", 0))
            if start_cut + end_cut >= duration:
                print("Thời gian cắt không hợp lệ. Đảm bảo rằng start_cut và end_cut không lớn hơn thời gian của audio.")
                return
            cut_duration = duration - start_cut - end_cut
            with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as temp_audio_file:
                temp_audio_path = temp_audio_file.name
            ffmpeg_cmd_cut = [
                "ffmpeg", "-y",
                '-loglevel', 'quiet',
                "-ss", str(start_cut),
                "-i", input_audio_path,
                "-t", str(cut_duration),
                "-c:a", "copy",
                temp_audio_path
            ]
            if not run_command_ffmpeg(ffmpeg_cmd_cut):
                print(f"Lỗi khi xử lý audio {input_audio_path}!")
                return
            streams_info = get_audio_info(temp_audio_path)
            if not streams_info:
                return
            output_audio_folder, file_name = get_output_folder(input_audio_path, output_folder_name="edited_audios")
            output_audio_path = os.path.join(output_audio_folder, file_name)
            metadata = {"artist": "None", "album": "None", "title": "None", "encoder": "FFmpeg 6.0"}
            original_sample_rate = int(streams_info.get("sample_rate", 0))
            sample_rate = 24000  # Đảm bảo tần số lấy mẫu là 24 kHz cho huấn luyện
            original_bitrate = streams_info.get("bit_rate", "192k")
            bitrate = "256k" if original_bitrate == "192000" else "192k"
            channels = 1  # Chuyển thành mono (1 kênh)
            volume = "4dB"
            eq_adjust = "equalizer=f=120:width_type=h:width=300:g=7, equalizer=f=1000:width_type=h:width=300:g=-1"
            ffmpeg_cmd_adjust = ["ffmpeg", '-loglevel', 'quiet', "-y", "-i", temp_audio_path]
            for key, value in metadata.items():
                ffmpeg_cmd_adjust += ["-metadata", f"{key}={value}"]
            ffmpeg_cmd_adjust += ["-ar", str(sample_rate), "-b:a", bitrate, "-ac", str(channels)]
            filters = [f"volume={volume}", eq_adjust]
            if speed != 1.0:
                filters.append(f"atempo={speed}")
            if cut_silence:
                filters.append("silenceremove=start_periods=1:start_silence=0.1:start_threshold=-50dB")
            # Áp dụng hiệu ứng tùy chọn
            if pitch_factor != 1.0:
                filters.append(f"rubberband=pitch={pitch_factor}")
            if flanger:
                filters.append(f"flanger=delay={flanger}:depth=3:regen=-9:width=77:speed=0.7")
            if aecho:
                filters.append(f"aecho=0.8:0.9:{aecho}:0.2")
            if chorus:
                filters.append(f"chorus=0.8:0.9:50:{chorus}:{chorus}:3")

            if filters:
                ffmpeg_cmd_adjust += ["-af", ",".join(filters)]
            # Đảm bảo xuất audio với định dạng chuẩn cho huấn luyện
            ffmpeg_cmd_adjust += ["-sample_fmt", "s16", "-c:a", "pcm_s16le", output_audio_path]
            if run_command_ffmpeg(ffmpeg_cmd_adjust):
                print(f"Chỉnh sửa thông tin audio thành công: {output_audio_path}")
            else:
                print(f"Lỗi khi thay đổi thông tin audio !!!")
            os.remove(temp_audio_path)
    except:
        print("Có lỗi trong quá trình chỉnh sửa audio !!!")


def extract_audio_ffmpeg(audio_path=None, video_path=None, video_url=None, video_folder=None, segments=None, download_folder=None, file_type='wav', speed='1.0'):
    try:
        if not segments:
            segments = "0-999999999999"
        try:
            segments = segments.split(',')
        except:
            print("Định dạng thời gian cắt là start-end với start,end là hh:mm:ss hoặc mm:ss hoặc ss")
            return
        try:
            speed = float(speed)
        except:
            speed = 1.0

        if video_url:
            video_path = download_video_by_url(video_url, download_folder, return_file_path=True)

        for segment in segments:
            segment = segment.strip()
            start, end = segment.split('-')
            start = convert_time_to_seconds(start)
            if start is None:
                return
            end = convert_time_to_seconds(end)
            if end is None:
                return
            target_paths = []
            if audio_path:
                target_path = audio_path
            elif video_path:
                target_path = video_path
            elif video_folder:
                videos =  get_file_in_folder_by_type(video_folder, ".mp4")   
                if not videos:
                    return
                for video in videos:
                    video_path = os.path.join(video_folder, video)
                    target_paths.append(video_path)
            else:
                warning_message("Vui lòng chọn nguồn để edit video")
                return
            if video_url or audio_path or video_path:
                target_paths.append(target_path)

            output_folder = os.path.join(os.path.dirname(target_path), 'extract_audios')
            os.makedirs(output_folder, exist_ok=True)
            for target_path in target_paths:
                video_clip = None
                if '.wav' in target_path or '.mp3' in target_path:
                    audio_clip = AudioFileClip(target_path)
                else:
                    video_clip = VideoFileClip(target_path)
                    audio_clip = video_clip.audio
                duration = audio_clip.duration
                if end > duration:
                    end = duration
                file_name = os.path.basename(target_path)
                audio_name = file_name.split('.')[0]
                cnt_cut = 1
                while True:
                    output_audio_path = f'{output_folder}/{audio_name}_{cnt_cut}.{file_type}'
                    if os.path.exists(output_audio_path):
                        cnt_cut += 1
                    else:
                        break
                try:
                    ffmpeg_cmd = [ "ffmpeg", "-y", "-i", target_path, "-ss", str(start), "-to", str(end), "-ac", "1", "-ar", "24000", "-filter:a", f"atempo={speed}", "-sample_fmt", "s16", output_audio_path ]
                    run_command_ffmpeg(ffmpeg_cmd)
                except:
                    getlog()
                    print(f'Có lỗi trong khi trích xuất audio')
                    
                if audio_clip:
                    audio_clip.close()
                if video_clip:
                    video_clip.close()
                print(f"  --> Trích xuất thành công audio từ video {target_path}")
        if video_url:
            remove_file(video_path)
    except:
        getlog()
        print("Có lỗi trong quá trình trích xuất audio !!!")


def text_to_audio_with_xtts(xtts, text, output_path, language="vi", speed_talk="1.0", speaker_id=None):
    try:
        if not text:
            return False
        if not xtts:
            return False
        try:
            speed_talk = float(speed_talk)
        except:
            speed_talk = 1.0
        speaker_wav_path = get_speaker_wav_path(language)
        text = cleaner_text(text)
        xtts.tts_to_file(text=text, speaker_wav=speaker_wav_path, language=language, speed=speed_talk, speaker=speaker_id, file_path=output_path)
        return True
    except:
        getlog()
        return False

def get_speaker_wav_path(language):
    if language == 'vi':
        speaker_wav_path = os.path.join(ref_audio_folder, 'vi.wav')
    elif language == 'en':
        speaker_wav_path = os.path.join(ref_audio_folder, 'en.wav')
    elif language == 'zh':
        speaker_wav_path = os.path.join(ref_audio_folder, 'zh.wav')
    else:
        print(f'Không tìm thấy file audio chuẩn cho ngôn ngữ {language}')
        return None
    return speaker_wav_path



def merge_images(image_paths, output_path, direction='vertical'):
    images = [Image.open(img_path) for img_path in image_paths]
    if direction == 'vertical':
        total_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)
        merged_image = Image.new('RGB', (total_width, total_height))
        y_offset = 0
        for img in images:
            merged_image.paste(img, (0, y_offset))
            y_offset += img.height  # Di chuyển vị trí dọc theo chiều cao của ảnh hiện tại
    elif direction == 'horizontal':
        total_width = sum(img.width for img in images)
        total_height = max(img.height for img in images)
        merged_image = Image.new('RGB', (total_width, total_height))
        x_offset = 0
        for img in images:
            merged_image.paste(img, (x_offset, 0))
            x_offset += img.width  # Di chuyển vị trí ngang theo chiều rộng của ảnh hiện tại
    merged_image.save(output_path)
    print(f"Đã lưu ảnh gộp tại: {output_path}")
    return output_path

def add_subtitle_into_video(video_path, subtitle_file, lang='vi', pitch=1.0, speed=1.0, speed_talk="1.0"):
    try:
        current_folder, file_name = get_current_folder_and_basename(video_path)
        output_video_folder = os.path.join(current_folder, 'output_videos')
        temp_audio_folder = os.path.join(current_folder, 'temp_audios')
        temp_audios = []
        output_video_path = os.path.join(output_video_folder, file_name)
        os.makedirs(output_video_folder, exist_ok=True)
        os.makedirs(temp_audio_folder, exist_ok=True)
        file_list_path = os.path.join(current_folder, "filelist.txt")
        with open(file_list_path, "w") as f:
            with open(subtitle_file, "r", encoding="utf-8") as infile:
                lines = infile.readlines()
                idx, cnt = 0, 0
                while idx < len(lines):
                    if lines[idx].strip().isdigit():
                        idx += 1
                    if '-->' in lines[idx]:
                        start_time_str, end_time_str = lines[idx].strip().split('-->')
                        start_time = convert_time_to_seconds(start_time_str.strip()) or 0
                        end_time = convert_time_to_seconds(end_time_str.strip()) or 0
                        if end_time > start_time:
                            idx += 1
                            content = lines[idx].strip()
                            cnt += 1
                            temp_audio_path = os.path.join(temp_audio_folder, f'{cnt}.wav')
                            text_to_audio_with_xtts(content, temp_audio_path, lang, speed_talk=speed_talk)
                            f.write(f"file '{temp_audio_path}'\n")
                            temp_audios.append(temp_audio_path)
                    idx += 1

        concatenated_audio = os.path.join(current_folder, 'final_audio.wav')
        subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'filelist.txt', '-c', 'copy', concatenated_audio])
        if pitch != 1.0 or speed != 1.0:
            adjusted_audio = os.path.join(current_folder, 'adjusted_audio.wav')
            audio_filters = []
            if speed != 1.0:
                audio_filters.append(f"atempo={speed}")
            if pitch != 1.0:
                audio_filters.append(f"rubberband=pitch={pitch}")
            subprocess.run(['ffmpeg', '-y', '-i', concatenated_audio, '-filter:a', ",".join(audio_filters), adjusted_audio])
            concatenated_audio = adjusted_audio

        video_duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', video_path]))
        audio_duration = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', concatenated_audio]))
        adjusted_video = None
        final_adjusted_audio = None
        if speed != 1.0 or audio_duration > video_duration:
            speed_factor = video_duration / audio_duration
            adjusted_video = os.path.join(current_folder, 'adjusted_video.mp4')
            subprocess.run(['ffmpeg', '-y', '-i', video_path, '-filter:v', f"setpts={1/speed_factor}*PTS", adjusted_video])
            video_path = adjusted_video
        else:
            speed_factor = audio_duration / video_duration
            final_adjusted_audio = os.path.join(current_folder, 'final_adjusted_audio.wav')
            subprocess.run(['ffmpeg', '-y', '-i', concatenated_audio, '-filter:a', f"atempo={speed_factor}", final_adjusted_audio])
            concatenated_audio = final_adjusted_audio
        subprocess.run([
            'ffmpeg', '-y', '-i', video_path, '-i', concatenated_audio,
            '-c:v', 'copy', '-map', '0:v:0', '-map', '1:a:0', '-shortest', output_video_path
        ])
        
        remove_file(file_list_path)
        if adjusted_video:
            remove_file(adjusted_video)
        if final_adjusted_audio:
            remove_file(final_adjusted_audio)
        for temp_audio in temp_audios:
            remove_file(temp_audio)
        print(f" --> Thêm phụ đề và chuyển thanh giọng nói thành công --> {output_video_path}")
    except:
        print("Có lỗi khi thêm phụ đề và chuyển thành giọng nói !!!")


def take_screenshot(name="1"):
    is_first = True
    def snip_screen():
        # Khởi tạo cửa sổ chụp ảnh
        app = QApplication(sys.argv)
        start_x = start_y = 0
        end_x = end_y = 0
        snipping = False

        def mousePressEvent(event):
            nonlocal start_x, start_y, snipping
            if event.button() == Qt.LeftButton:
                start_x = event.x()
                start_y = event.y()
                snipping = True

        def mouseMoveEvent(event):
            nonlocal end_x, end_y, snipping
            if snipping:
                end_x = event.x()
                end_y = event.y()
                window.update()

        def mouseReleaseEvent(event):
            nonlocal snipping, is_first
            if event.button() == Qt.LeftButton:
                snipping = False
                window.close()  # Đóng cửa sổ sau khi thả chuột

                # Tạo vùng chọn và chụp ảnh chỉ khi có vùng chọn hợp lệ
                if start_x != end_x and start_y != end_y:
                    x1 = min(start_x, end_x)
                    y1 = min(start_y, end_y)
                    x2 = max(start_x, end_x)
                    y2 = max(start_y, end_y)
                    screenshot = QGuiApplication.primaryScreen().grabWindow(0, x1, y1, x2 - x1, y2 - y1)
                    if is_first:
                        is_first = False
                        return
                    # Tìm tên file có sẵn để lưu ảnh
                    filename = get_next_filename(name)
                    screenshot.save(filename, "png")
                    print(f"Đã lưu ảnh dưới tên: {filename}")
                else:
                    print("Không có vùng chọn hợp lệ, không lưu ảnh.")

        def get_next_filename(name=name):
            file_name = None
            try:
                file_name = int(name)
            except:
                pass
            if file_name:
                while os.path.exists(f"{file_name}.png"):
                    file_name += 1
            else:
                file_name = name
            return f"{file_name}.png"

        def paintEvent(event):
            nonlocal start_x, start_y, end_x, end_y, snipping
            if snipping:
                rect = QRect(start_x, start_y, end_x - start_x, end_y - start_y)
                painter = QPainter(window)
                pen = QPen(Qt.red, 2)
                painter.setPen(pen)
                painter.drawRect(rect)

        # Tạo cửa sổ để vẽ và chụp màn hình
        window = QWidget()
        window.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        window.setWindowOpacity(0.3)
        window.setCursor(Qt.CrossCursor)
        window.setGeometry(QGuiApplication.primaryScreen().geometry())
        window.setStyleSheet("background-color: black;")
        window.showFullScreen()

        # Gán các sự kiện chuột cho cửa sổ
        window.mousePressEvent = mousePressEvent
        window.mouseMoveEvent = mouseMoveEvent
        window.mouseReleaseEvent = mouseReleaseEvent
        window.paintEvent = paintEvent

        # Chạy vòng lặp sự kiện
        app.exec_()

    print("Chế độ chụp ảnh đã mở. Nhấn Ctrl + M để bắt đầu. Nhấn Ctrl + Q để thoát")
    while True:
        if keyboard.is_pressed('ctrl+m'):
            snip_screen()
            while keyboard.is_pressed('ctrl+m'):  # Chờ nhả phím Ctrl + M
                pass
        if keyboard.is_pressed('ctrl+q'):
            print("Thoát chức năng chụp ảnh màn hình")
            keyboard.unhook_all()
            break



#-----------------commond-------------------------------

def load_config():
    if os.path.exists(config_path):
        config = get_json_data(config_path)
    else:
        config = {
            "download_folder":"",
            "auto_start": False,
            "is_delete_video": False,
            "is_move": False,
            "show_browser": False,
            "time_check_auto_upload": "0",
            "time_check_status_video": "0",
            "download_by_video_url": "",

            "file_name": "",
            "start_index": "1",
            "videos_edit_folder": "",
            "first_cut": "0",
            "end_cut": "0",
            "is_delete_original_audio": False,
            "background_music_path": "",
            "background_music_volume": "",
            "speed_up": "1.05",
            "max_zoom_size": "1.1",
            "is_random_zoom": False,
            "vertical_position": 'center',
            "horizontal_position": 'center',
            "flip_video": False,
            "water_path": "",
            "watermark_scale": "1,1",
            "vertical_watermark_position": "50",
            "horizontal_watermark_position": "50",
            "top_bot_overlay": "0,0",
            "left_right_overlay": "0,0",

            "audios_edit_folder": "",
            "audio_speed": "1", 
            "pitch_factor": "1",
            "cut_silence": False,
            "aecho": "100",

            "audio_edit_path": "", 
            "speed_talk": "1.0", 
            "convert_multiple_record": False, 
            "video_get_audio_path": "", 
            "video_get_audio_url": "",

            "language_tts": "vi",
            "speed_talk": "vi",
        }
        save_to_json_file(config, config_path)
    return config

supported_languages = {
      "cn": "Chinese",
      "en1": "English",
      "en2": "English",
      "vi": "Vietnamese"
}

special_word = {
    "/": " ",
    ";": ". ",
    "-": " ",
    "_": " ",
    ":": ", ",
    " ?": "?",
    " !": "!",
    "?.": "?",
    "!.": "!",
    "..": ".",
    "\"": "",
    "'": "",
    "#": " ",
    "   ": " ",
    "  ": " ",
    "~": " đến ",
    "$": " đô",
    "vnđ": "đồng",
    "%": " phần trăm",
    "&": " và ",
    "=": "bằng",
    ">": "lớn hơn",
    "<": "bé hơn",
}

viet_tat = {
    "IP" : "ai pi",
    "IT" : "ai ti",
    "AI" : "ây ai",
    "API" : "ây pi ai",
    "GPT" : "gi pi ti",
    " 1 " : " một ",
    " 2 " : " hai ",
    " 3 " : " ba ",
    " 4 " : " bốn ",
    " 5 " : " năm ",
    " 6 " : " sáu ",
    " 7 " : " bảy ",
    " 8 " : " tám ",
    " 9 " : " chín ",
    " 10 " : " mười ",
    " 11 " : " mười một ",
    " 12 " : " mười hai ",
    " 13 " : " mười ba ",
    " 14 " : " mười bốn ",
    " 15 " : " mười lăm ",
    " 16 " : " mười sáu ",
    " 17 " : " mười bảy ",
    " 18 " : " mười tám ",
    " 19 " : " mười chín ",
    " 20 " : " hai mươi ",
    " 30 " : " ba mươi ",
    " 40 " : " bốn mươi ",
    " 50 " : " năm mươi ",
    " 60 " : " sáu mươi ",
    " 70 " : " bảy mươi ",
    " 80 " : " tám mươi ",
    " 90 " : " chín mươi ",
    " 100 " : " một trăm ",
}

loi_chinh_ta = {
    "kickboxing": "kít bốc xing",
    "skill": "sờ kiu",
    "pro": "pờ rồ",
    "alo": "a lô",
    "out": "au",
    "solo": "sô lô",
    "damge": "đăm",
    "studio": "sờ tiu đi ô",
    "ferari": "phe ra ri",
    "over": "ao vờ",
    "thinking": "thing king",
    "trùm hợp": "trùng hợp",
    "hoàng thành": "hoàn thành",
    "đùa dưỡn": "đùa giỡn",
    "xác hại": "sát hại",
    "xác thủ": "sát thủ",
    "xinh con": "sinh con",
    "danh con": "ranh con",
    "trẻ danh": "trẻ ranh",
    "nhóc danh": "nhóc ranh",
    "sinh đẹp": "xinh đẹp",
    "nữ từ": "nữ tử",
    "sắc khí": "sát khí",
    "sui xẻo": "xui xẻo",
    "chậm dãi": "chậm rãi",
    "bồn trồn": "bồn chồn",
    "lan lóc": "lăn lóc",
    "cuốt": "cút",
    "cười chử": "cười trừ",
    "lầm bẩm": "lẩm bẩm",
    "tróng váng": "choáng váng",
    "sát chết": "xác chết",
    "giò xét": "dò xét",
    "âm dưng": "âm dương",
    "cao mày": "cau mày",
    "chấn an": "trấn an",
    "sừng sốt": "sửng sốt",
    "rỗ rành": "dỗ dành",
    "huyền đệ": "huynh đệ",
    "sữa sờ": "sững sờ",
    "xứng sờ": "sững sờ",
    "run dẩy": "run rẩy",
    "trào hỏi": "chào hỏi",
    "huyên đệ": "huynh đệ",
    "sứng sờ": "sững sờ",
    "lia liện": "lia lịa",
    "rác rười": "rác rưởi",
    "thiếu ra": "thiếu gia",
    "mủ khơi": "mù khơi",
    "sa tít": "xa tít",
    "viền vông": "viễn vông",
    "trân ái": "chân ái",
    "cho đùa": "trò đùa",
    "rồn dập": "dồn dập",
    "sữ người": "sững người",
    "xữ người": "sững người",
    "chừng mắt": "trừng mắt",
    "ẩm ý": "ầm ỷ",
    "dỗ rảnh": "dỗ dành",
    "chế diễu": "chế giễu",
    "bàm lấy": "bám lấy",
    "rũ rỗ": "dụ giỗ",
    "xỉ nhục": "sỉ nhục",
    "song lên": "xông lên",
    "đuổi ý": "đổi ý",
    "y tứ": "ý tứ",
    "to mò": "tò mò",
    "khách giáo": "khách sáo",
    "băng cua": "bâng quơ",
    "chi kỷ": "tri kỷ",
    "cười khỉ": "cười khẩy",
    "nguyền dùa": "nguyền rủa",
    "chế riễu": "chế giễu",
    "miểm mai": "mỉa mai",
    "binh vực": "bênh vực",
    "xáo dỗng": "xáo rỗng",
    "âm ức": "ấm ức",
    "xót ra": "xót xa",
    "vút ve": "vuốt ve",
    "khắc nào": "khác nào",
    "ly xì": "lì xì",
    "li xì": "lì xì",
    "sốt sáng": "sốt sắng",
    "cầm muốn": "câm mồm",
    "ma cả dòng": "ma cà rồng",
    "học tỳ": "học tỷ",
    "quyệt": "quỵt",
    "chừng mắt": "trừng mắt",
    "sắp mặt": "sắc mặt",
    "lước xéo": "liếc xéo",
    "rụi mắt": "dụi mắt",
    "chú đáo": "chu đáo",
    "thân thức": "thần thức",
    "tự chọc": "tự trọng",
    "lên lút": "lén lút",
    "nhẹ nhóm": "nhẹ nhõm",
    "đụng chúng": "đụng trúng",
    "câu mày": "cau mày",
    "thàn thở.": "than thở.",
    "đứng phát dậy": "đứng phắt dậy",
    "nóng gian": "nóng ran",
    "may dám": "mày dám",
    "ái trả": "ái chà",
    "nghe thầy": "nghe thấy",
    "dài nhân": "giai nhân",
    "ngược lép": "ngực lép",
    "trai dự": "chai rượu",
    "nửa họ": "nợ họ",
    "cựa đầu": "gật đầu",
    "giờ khóc giờ cười": "giở khóc giở cười",
    "gió sư": "giáo sư",
    "thiện trí": "thiện chí",
    "can tin": "căn tin",
    "can tín": "căn tin",
    "học để": "học đệ",
    "nhực": "nhược",
    "chút giận": "trút giận",
    "thẳng nhiên": "thản nhiên",
    "châm mắt": "trơ mắt",
    "buồn mã": "buồn bã",
    "senh": "xen",
    "ngẹn": "nghẹn",
    "lức anh": "liếc anh",
    "nghiến rằng": "nghiến răng",
    "dỗ rảnh": "dỗ dành",
    "tọa nguyện": "toại nguyện",
    "sang ngã": "sa ngã",
    "mắng nhất": "mắng nhiếc",
    "tiên đồn": "tin đồn",
    "tụt rốc": "tụt dốc",
    "ngừng mặt": "ngẩng mặt",
    "quên biết": "quen biết",
    "cân bản": "căn bản",
    "nhớ mày": "nhíu mày",
    "ấm ẩm": "ngấm ngầm",
    "ngốc ngách": "ngốc nghếch",
    "lé lên": "lóe lên",
    "tót": "toát",
    "cương chiều": "cưng chiều",
    "ngần ra": "ngẩn ra",
    "cao giáo": "cao ráo",
    "ra tộc": "gia tộc",
    "dở trò": "giở trò",
    "yêu tú": "ưu tú",
    "ra thế": "gia thế",
    "thì gia thế": "thì ra thế",
    "thành gia thế": "thành ra thế",
    "hồn hền": "hổn hển",
    "tái nhật": "tái nhợt",
    "sót ra": "xót xa",
    "giáng vẻ": "dáng vẻ",
    "thanh chốt": "then chốt",
    "kếp trước": "kiếp trước",
    "thật thứ": "tha thứ",
    "gây tẩm": "ghê tởm",
    "chọng sinh": "trọng sinh",
    "ái nái": "áy náy",
    "ái náy": "áy náy",
    "sưng mù": "sương mù",
    "cười lệnh": "cười lạnh",
    "đói là": "đói lã",
    "liên gọi": "liền gọi",
    "mô thuẫn": "mâu thuẫn",
    "cười khỏi": "cười khẩy",
    "ký túc giá": "ký túc xá",
    "ký túc xa": "ký túc xá",
    "vóng vẻ": "vắng vẻ",
    "đáy ngộ": "đãi ngộ",
    "hử lệnh": "hừ lạnh",
    "ba lồ": "ba lô",
    "dẫn dỗi": "giận dỗi",
    "bị ốn": "bị ốm",
    "ưu ám": "u ám",
    "chầm tính": "trầm tính",
    "ốt ức": "uất ức",
    "học tì": "học tỷ",
    "hừa lạnh": "hừ lạnh",
    "nguy ngoai": "nguôi ngoai",
    "phần nửa": "phân nửa",
    "chiều trụng": "chiều chuộng",
    "chàn da": "tràn ra",
    "răng lên": "dâng lên",
    "rời lại": "giờ lại",
    "hán ta": "hắn ta",
    "hàn ta": "hắn ta",
    "hủng hồ": "huống hồ",
    "rung nạp": "dung nạp",
    "sua tay": "xua tay",
    "chầm mặt": "trầm mặt",
    "chân nhà": "trần nhà",
    "mô giấc": "một giấc",
    "hội trần": "hội chuẩn",
    "trên ngành": "chuyên ngành",
    "học mụy": "học muội",
    "sen vào": "xen vào",
    "dùng bỏ": "ruồng bỏ",
    "giáng vẻ": "dáng vẻ",
    "vu khổng": "vu khống",
    "huy chưng": "huy chương",
    "dạy rỗ": "dạy giỗ",
    "chầm ngâm": "trầm ngâm",
    "hứ lạnh": "hừ lạnh",
    "cướng rắn": "cứng rắn",
    "chàng pháo": "tràn pháo",
    "bà lô": "ba lô",
    "cần nhớ": "cần nhờ",
    "tùn tìm": "tủm tỉm",
    "bị đặt": "bịa đặt",
    "độc điện": "độc địa",
    "tránh ghét": "chán ghét",
    "mắc cấp": "max cấp",
    "cao rọng": "cao giọng",
    "tin nghĩa": "tình nghĩa",
    "luống cuốn": "luống cuống",
    "mê mụi": "mê nuội",
    "cố hiểu": "cố hữu",
    "thầm rùa": "thầm rủa",
    "bành bao": "bảnh bao",
    "tủn tìm": "tủm tỉm",
    "xài bước": "xải bước",
    "cứ ngửi": "cứng người",
    "được đối": "tuyệt đối",
    "chầm chầm": "chằm chằm",
    "đáy hổ": "đáy hồ",
    "bộ dạo": "bộ dạng",
    "nghe song": "nghe xong",
    "lục ra": "lục gia",
    "ăn phận": "an phận",
    "trí tôn": "chí tôn",
    "chiếc dương": "chiếc rương",
    "cái dương": "cái rương",
    "dọa đầu": "dạo đầu",
    "chuyển cành": "chuyển cảnh",
    "phần nộ": "phẫn nộ",
    "đạp vang": "đạp văng",
    "hắn tam": "hắn ta",
    "gãý": "gãy",
    "ổ ạt": "ồ ạt",
    "xong lên": "xông lên",
    "sợ ý": "sơ ý",
    "sắt lạnh": "sắc lạnh",
    "sáng lạm": "sáng lạn",
    "chú tức": "chu tước",
    "chư mộ": "chiêu mộ",
    "tử thư": "tiểu thư",
    "giới chứng": "dưới trướng",
    "vụi vã": "vội vã",
    "cố động": "cô đọng",
    "song xuôi": "xong xuôi",
    "song sau": "xong sau",
    "song đi": "xong đi",
    "trưởng lực": "chưởng lực",
    "trưởng thẳng": "chưởng thẳng",
    "trường mạnh": "chưởng mạnh",
    "chứa thẳng": "chiếu thẳng",
    "quá nhật": "quán nhật",
    "trường thẳng": "chưởng thẳng",
    "cúc máy": "cúp máy",
    "nghiến giăng": "nghiến răng",
    "trưng mắt": "trừng mắt",
    "lầm bầm": "lẩm bẩm",
    "tri tiêu": "chi tiêu",
    "khoe miệng": "khóe miệng",
    "bú phim": "bú phêm",
    "chàn đầy": "tràn đầy",
    "qua tặng": "quà tặng",
    "ngạo nghĩa": "ngạo nghễ",
    "thân hào": "thần hào",
    "cao ốm": "cáo ốm",
    "chút được": "trút được",
    "tue tue": "toe toét",
    "thị xát": "thị sát",
    "đấu trưởng": "đấu trường",
    "lạnh lung": "lạnh lùng",
    "thiên thít": "thin thít",
    "lác đầu": "lắc đầu",
    "giấc lời": "dứt lời",
    "sức khoát": "dứt khoát",
    "nhò nhò": "nho nhỏ",
    "xảy bước": "xải bước",
    "nhà sửa": "nhà xưởng",
    "lòng văn": "long vân",
    "ra cố": "gia cố",
    "chật nhớ": "chợt nhớ",
    "xôi nổi": "sôi nổi",
    "liều cỏ": "lều cỏ",
    "tân qua": "tân quan",
    "ráng vẻ": "dáng vẻ",
    "giữa trừng": "giữa chừng",
    "gián đốc": "giám đốc",
    "trả hỏi": "chào hỏi",
    "su nịnh": "xu nịnh",
    "gượm": "gượng",
    "nhớn mày": "nhướng mày",
    "dâu tóc": "râu tóc",
    "ngởng đầu": "ngẩng đầu",
    "vụi vàng": "vội vàng",
    "đáng bằng": "đóng băng",
    "rứt lời": "dứt lời",
    "chất lặng": "chết lặng",
    "thâm nghĩ": "thầm nghĩ",
    "xa thải": "sa thải",
    "út ức": "uất ức",
    "lan chuyển": "lan truyền",
    "mời trào": "mời chào",
    "lan sóng": "làn sóng",
    "trân thành": "chân thành",
    "ra nhập": "gia nhập",
    "tập kỹ": "tạp kỹ",
    "sẽ số": "dãy số",
    "trật nghĩ": "chợt nghĩ",
    "trần trừ": "chần chừ",
    "dững lại": "sững lại",
    "hàng giòng": "hàng rong",
    "ngương ác": "ngơ ngác",
    "đùi việc": "đuổi việc",
    "trâm trâm": "chăm chăm",
    "lão ra": "lão gia",
    "lòng lực": "long lực",
    "thủ lão": "thụ lão",
    "truyền hóa": "chuyển hóa",
    "nhạt nhạt": "nhàn nhạt",
    "chuỗi lủi": "trụi lủi",
    "bao trùng": "bao trùm",
    "căn cỗi": "cằn cỗi",
    "ung tùng": "um tùm",
    "bất chật": "bất chợt",
    "trợ tập": "triệu tập",
    "cuộc sáng": "cột sáng",
    "kỹ sĩ": "kỵ sĩ",
    "mùi sạc": "mùi sặc",
    "sặc thuốc dùng": "sặc thuốc súng",
    "tôn tép": "tôm tép",
    "lợi lục": "lợi lộc",
    "chấp tay": "chắp tay",
    "vừa rứt": "vừa dứt",
    "lá trắng": "lá chắn",
    "chiêu tức": "chiêu thức",
    "trịt tiêu": "triệt tiêu",
    "trột dạ": "chột dạ",
    "lớn dọng": "lớn giọng",
    "hùng hãn": "hung hãn",
    "lòng khí": "long khí",
    "giành dỗi": "rảnh rỗi",
    "kỳ sĩ": "kỵ sĩ",
    "giực": "dực",
    "trò hỏi": "chào hỏi",
    "ngương tụ": "ngưng tụ",
    "chữ lượng": "trữ lượng",
    "dao gam": "dao găm",
    "dung động": "rung động",
    "nhái mắt": "nháy mắt",
    "tơ giấy": "tờ giấy",
    "dên dỉ": "rên rỉ",
    "tử bi": "từ bi",
    "ráng xuống": "giáng xuống",
    "xâm xét": "sấm sét",
    "rọng": "giọng",
    "nhiều đây": "nhiêu đây",
    "khi thức": "khí tức",
    "trói lọt": "chói lọi",
    "su tan": "xua tan",
    "liên thấy": "liền thấy",
    "liên biến": "liền biến",
    "liên cung kính": "liền cung kính",
    "liên cười": "liền cười",
    "từ phủ": "tử phủ",
    "nhìn gia": "nhìn ra",
    "trường giáo": "chưởng giáo",
    "chậm chế": "chậm trễ",
    "đà kích": "đả kích",
    "cợt đầu": "gật đầu",
    "mất máy": "mắp máy",
    "khi huyết": "khí huyết",
    "chuyển tống": "truyền tống",
    "động tác mở": "động tác mời",
    "vạn rạm": "vạn dặm",
    "trậm giãi": "chậm rãi",
    "luông khí": "luồng khí",
    "ấm ấm": "ầm ầm",
    "lué": "lóe",
    "liên xuất hiện": "liền xuất hiện",
    "khí thức": "khí tức",
    "uy nhiêm": "uy nghiêm",
    "không chung": "không trung",
    "hiện nhiên": "hiển nhiên",
    "tuần cha": "tuần tra",
    "tôn tì": "tôn ti",
    "cùng bạo": "cuồng bạo",
    "trông đối": "chống đối",
    "dòng dòng": "ròng ròng",
    "kim đàn": "kim đan",
    "bể hạ": "bệ hạ",
    "uy nhiễm": "uy nghiêm",
    "khi nhờn": "khinh nhờn",
    "cô ý": "cố ý",
    "rào động": "dao động",
    "xin thà": "xin tha",
    "khó thà": "khó tha",
    "quỷ lạy": "quỳ lạy",
    "cùng kính": "cung kính",
    "ảo ảo": "ào ào",
    "chỉ hoãn": "trì hoãn",
    "cư chú": "cư trú",
    "trưởng giáo": "chưởng giáo",
    "như nếu": "nhưng nếu",
    "tró ngợp": "choáng ngợp",
    "cao mảnh": "cau mày",
    "quenh": "quen",
    "sững sở": "sững sờ",
    "trật": "chợt",
    "nhìn xa qua": "nhìn sơ qua",
    "chảy dài": "trải dài",
    "cử dương": "cửu dương",
    "trắn ngang": "chắn ngang",
    "trót vót": "chót vót",
    "vạn rặm": "vạn dặm",
    "tức đất": "tấc đất",
    "thân sấm": "thần sấm",
    "khoa chặt": "khóa chặt",
    "sau gái": "sau gáy",
    "vẫn vẹo": "vặn vẹo",
    "hướng thú": "hứng thú",
    "đăng hoành": "đằng hoành",
    "cỡ sao": "cớ sao",
    "nhíu mẩy": "nhíu mày",
    "quân việt": "quân phiệt",
    "chung khủng bố": "trùm khủng bố",
    "onza": "oan gia",
    "đô là": "đô la",
    "chọn tội": "trọng tội",
    "ngu cương": "ngô cương",
    "tv": "ti vi",
    "hòa lực": "hỏa lực",
    "ủng phí": "uổng phí",
    "trong trước mắt": "trong chớp mắt",
    "nguy trang": "ngụy trang",
    "it": "IT",
    "chầm mặc": "trầm mặt",
    "vừa vẫn": "vừa vặn",
    "nhất khóe miệng": "nhếch khóe miệng",
    "nhất miệng": "nhếch miệng",
    "tiểu da": "tiểu gia",
    "tiểu ra": "tiểu gia",
    "dẫn giữ": "giận dữ",
    "chú ẩn": "trú ẩn",
    "cút máy": "cúp máy",
    "châu bò": "trâu bò",
    "bình vương": "binh vương",
    "hồ to": "hô to",
    "ngẳng đầu": "ngẩng đầu",
    "cho chơi": "trò chơi",
    "ông phóng": "ống phóng",
    "suốt ruột": "sốt ruột",
    "ổn ảo": "ồn ào",
    "không trùng": "không trung",
    "chưa kỳ": "chưa kịp",
    "khiếp sự": "khiếp sợ",
    "sắc hồ": "xác khô",
    "co súng": "cò súng",
    "đinh cuồng": "điên cuồng",
    "tường lĩnh": "tướng lĩnh",
    "đánh đau tháng đó": "đánh đâu thắng đó",
    "mầu chốt": "mấu chốt",
    "hương phấn": "hưng phấn",
    "dâu dia": "râu ria",
    "dơ súng": "giơ súng",
    "bắt giác": "bất giác",
    "dâu rậm": "râu rậm",
    "kêu ngạo": "kiêu ngạo",
    "sư mụi": "sư muội",
    "bầu vực": "bờ vực",
    "ra nghiệp": "gia nghiệp",
    "loạn tgiọng": "loạn choạng",
    "tgiọng": "trọng",
    "ỏn tù": "oẻn tù",
    "lùng cây": "lùm cây",
    "núp lùng": "núp lùm",
    "hà thủ âu": "hà thủ ô",
    "thủ yêu": "thụ yêu",
    "con trồn": "con chồn",
    "một lùn": "một luồng",
    "chấp mắt": "chớp mắt",
    "sơ sải": "sơ xài",
    "xảo quỵt": "xảo quyệt",
    "dỡ thủ đoạn": "giỡ thủ đoạn",
    "võ cây": "vỏ cây",
    "dĩa cây": "rễ cây",
    "tạ khí": "tà khí",
    "trực hồi": "triệu hồi",
    "giang bộc": "ràng buộc",
    "nút chừng": "nuốt chửng",
    "xiết chặt": "siết chặt",
    "vùng tay": "vung tay",
    "hết lớn": "hét lớn",
    "tích chữ": "tích trữ",
    "rung nham": "dung nham",
    "trùng kín": "trùm kín",
    "e rè": "e dè",
    "quỳ dạp": "quỳ rạp",
    "giữ tượng": "dữ tợn",
    "dơ bàn chân": "giơ bàn chân",
    "thoả mãn": "thỏa mãn",
    "rút lời": "dứt lời",
    "sông thẳng": "xông thẳng",
    "hóa thành cho": "hóa thành tro",
    "hàn hé": "hắn hé",
    "phẳng phất": "phảng phất",
    "ta khí": "tà khí",
    "rồi rào": "dồi dào",
    "lướt mắt": "liếc mắt",
    "xuân sao": "xôn xao",
    "chơi má": "trời má",
    "có đuôi chó": "cỏ đuôi chó",
    "miếu miệng": "mếu miệng",
    "ca cực": "cá cược",
    "dám định": "giám định",
    "sợ hái": "sợ hãi",
    "hạo nam nhi": "hảo nam nhi",
    "vặt áo": "vạt áo",
    "sảo trá": "xảo trá",
    "xem trút": "xem chút",
    "ruồn dẩy": "run rẩy",
    "thật hay đủ": "thật hay đùa",
    "đan rới": "đan giới",
    "ráng rỡ": "rạng rỡ",
    "miêu máu": "mếu máo",
    "gặm mặt": "gằm mặt",
    "taý": "tay",
    "tức khác": "tức khắc",
    "át sẽ": "ắt sẽ",
    "đơn thúc": "đơn thuốc",
    "có thủ tất báo": "có thù tất báo",
    "bỏ xót": "bỏ sót",
    "trục sức": "trục xuất",
    "khoái trí": "khoái chí",
    "rang cánh": "dang cánh",
    "phú chốc": "phút chốc",
    "sáng trói": "sáng chói",
    "trứ": "chứ",
    "mùm": "mồm",
    "sành chính": "sảnh chính",
    "gia trủ": "gia chủ",
    "tiểu từ": "tiểu tử",
    "ly lẽ": "lý lẽ",
    "phối đổ": "phối đồ",
    "cam phẫn": "căm phẫn",
    "kinh tầm": "kinh tởm",
    "cho cười": "trò cười",
    "trẻ chung": "trẻ trung",
    "ngaý": "ngay",
    "vờ kịch": "vở kịch",
    "ở sành": "ở sảnh",
    "lơ lả": "lơ là",
    "ôn chặt": "ôm chặt",
    "cầy xấy": "cầy sấy",
    "hác tà": "hắc tà",
    "nhược bang": "nhược băng",
    "la hết": "la hét",
    "trong thấy": "trông thấy",
    "cây rau": "cây dao",
    "cua cậu": "cu cậu",
    "đường rau": "đường dao",
    "giựt lửa": "rực lửa",
    "giận dò": "dặn dò",
    "ném thử": "nếm thử",
    "rổ trò": "giở trò",
    "chén giết": "chém giết",
    "nhìn hán": "nhìn hắn",
    "cú cậu": "cu cậu",
    "tích tác": "tích tắc",
    "cái nổi": "cái nồi",
    "hoác mồm": "ngoác mồm",
    "độ ma": "đậu má",
    "đờ mơ": "đờ mờ",
    "tổ chuyển": "tổ truyền",
    "lùng miếng": "lùm mía",
    "nha cương": "nha cưng",
    "phát xốt": "phát sốt",
    "chữ vật": "trữ vật",
    "chú mày": "chúng mày",
    "sữa rừng sâu": "giữa rừng sâu",
    "chữ đồ": "trữ đồ",
    "hồ hồi": "hồ hỡi",
    "nhỏ rãi": "nhỏ dãi",
    "cao có": "cau có",
    "nhét miệng": "nhếch miệng",
    "chưa thức": "chiêu thức",
    "chơi sỏ": "chơi xỏ",
    "mù hồi": "mồ hôi",
    "mù hôi": "mồ hôi",
    "ngầm gừ": "gầm gừ",
    "thi chiến": "thi triển",
    "phùng phùng": "phừng phừng",
    "chưng ra": "trưng ra",
    "nhằm hiểm": "nham hiểm",
    "nhắc bổng": "nhấc bổng",
    "kêu gạo": "kêu gào",
    "móc móc": "ngoắc ngoắc",
    "sạc sụa": "sặc sụa",
    "gạo thét": "gào thét",
    "thẻ lưỡi": "thè lưỡi",
    "trợn cháo": "trợn tráo",
    "tới nguyệt": "tuế nguyệt",
    "chán trường": "chán chường",
    "thi chiển": "thi triển",
    "vò vè": "vo ve",
    "xót lại": "sót lại",
    "gây guộc": "gầy guộc",
    "răng bẫy": "giăng bẫy",
    "tính kê": "tính kế",
    "rang tay": "giang tay",
    "rông dài": "dông dài",
    "chắn nản": "chán nản",
    "ân ký": "ấn ký",
    "trinh lệch": "chênh lệch",
    "chương khí": "chướng khí",
    "chắn ghét": "chán ghét",
    "phân yêu": "phân ưu",
    "ngu dần": "ngu xuẩn",
    "tư diệt": "tiêu diệt",
    "nguồn loài": "muôn loài",
    "chính mùi": "chín mùi",
    "nhách miệng": "nhếch miệng",
    "mau chó": "máu chó",
    "ngu rốt": "ngu dốt",
    "may mắn thầy": "may mắn thay",
    "trịu hồi": "triệu hồi",
    "chứa dọa": "chiếu rọi",
    "lùn kiếm khí": "luồng kiếm khí",
    "rồn lại": "dồn lại",
    "rồn nén": "dồn nén",
    "run rảy": "run rẩy",
    "găng gượng": "gắng gượng",
    "dữ rồi": "dữ dội",
    "rước khỏi": "dứt khỏi",
    "nước nảy": "nứt nẻ",
    "xương hùng": "xưng hùng",
    "thân sắc": "thân xác",
    "rậm chân": "dậm chân",
    "lùng tà khí": "luồng tà khí",
    "đệch miệng": "đệch mịa",
    "lòng môn": "long môn",
    "trúc lát": "chốc lát",
    "con rán": "con dán",
    "mặt mây": "mặt mày",
    "hình hải": "hình hài",
    "gõi chết": "cõi chết",
    "nhẹ rộng": "nhẹ giọng",
    "mừng dỡ": "mừng rỡ",
    "miếu máu": "mếu máo",
    "tử lầu": "tửu lầu",
    "chiều mến": "triều mến",
    "trong tróng": "chong chóng",
    "ho hát": "ho hắt",
    "chầm lặng": "trầm lặng",
    "đổ ăn": "đồ ăn",
    "mè nhau": "mè nheo",
    "về đường": "vệ đường",
    "xữa người": "sững người",
    "liên nhĩ": "liền nghĩ",
    "méo máu": "mếu máo",
    "trống cầm": "chống cằm",
    "trong quan": "trông quen",
    "chầm lặng": "trầm lặng",
    "nhìn tay": "nhểnh tai",
    "tụng ba": "tụm ba",
    "thứ gia": "thiếu gia",
    "sùa đuổi": "xua đuổi",
    "gần rộng": "gằn giọng",
    "rắn vải": "dáng vẻ",
    "cầm nến": "câm nín",
    "vuốt cầm": "vuốt cằm",
    "đánh cực": "đánh cược",
    "vinh váo": "vênh váo",
    "cực xem": "cược xem",
    "đan rực": "đan dược",
    "tư tỉnh": "tươi tỉnh",
    "khói trí": "khoái trí",
    "ván cực": "ván cược",
    "huỳnh phẩm": "huyền phẩm",
    "lạng người": "lặng người",
    "cá cực": "cá cược",
    "êch": "ếch",
    "xôn sao": "xôn xao",
    "nhà hoàng": "nha hoàng",
    "cái hụt": "cái hộp",
    "đuôi cho": "đuôi chó",
    "chiếc hụt": "chiếc hộp",
    "trong hụt": "trong hộp",
    "lên rộng": "lên giọng",
    "nghiệm đàn": "nghiệm đan",
    "lỗ bịch": "lố bịch",
    "hoái ngoác": "ngoái ngoác",
    "để phòng": "đề phòng",
    "hộp cổ": "hộp gỗ",
    "nhếu mày": "nhíu mày",
    "ngóc miệng": "ngoác miệng",
    "nhà đầu": "nha đầu",
    "chầm tư": "trầm tư",
    "diễu cờ": "giễu cợt",
    "chân chu": "trơn tru",
    "phầy tay": "phẩy tay",
    "cận bã": "cặn bã",
    "điều cực": "điều cược",
    "nhách môi": "nhếch môi",
    "ngương thần": "ngưng thần",
    "lên cầm": "lên cằm",
    "xôi sục": "sôi sục",
    "mà đem": "màn đêm",
    "ra chủ": "gia chủ",
    "vút về": "vuốt ve",
    "bộ dâu": "bộ râu",
    "trí cực": "chí cực",
    "phân khích": "phấn khích",
    "thiền đan": "thiên đan",
    "đà thông": "đả thông",
    "trang khuyết": "trăng khuyết",
    "tĩnh lạng": "tĩnh lặng",
    "vơn mình": "vươn mình",
    "tròn váng": "choáng váng",
    "ngả người": "ngã người",
    "thu dọa": "thu dọn",
    "lẻ lưỡi": "lè lưỡi",
    "lan đùng": "lăn đùng",
    "có đọc": "có độc",
    "dơ một": "giơ một",
    "chống cầm": "chống cằm",
    "thằng thực": "thẳng thực",
    "dơ tay": "giơ tay",
    "quy tủ": "quy tụ",
    "ngay người": "ngây người",
    "đang dược": "đan dược",
    "kính cần": "kính cẩn",
    "dắn chắc": "rắn chắc",
    "điều khác": "điêu khắc",
    "gẹo": "ghẹo",
    "tục trưởng": "tộc trưởng",
    "cầm quốc": "cầm cuốc",
    "phiền rối": "phiền rồi",
    "nghiêm trình": "nghiêm chỉnh",
    "ganh đùa": "ganh đua",
    "người trị tốt": "người chị tốt",
    "chi khí": "chí khí",
    "không mang nguy hiểm": "không màng nguy hiểm",
    "bội chạy": "vội chạy",
    "tiên xin": "tiên sinh",
    "chua sót": "chua xót",
    "lại xe": "lái xe",
    "thức dận": "tức giận",
    "cạp đào": "cặp đào",
    "biết chức": "biết trước",
    "ngư ngác": "ngơ ngác",
    "không mảng": "không màng",
    "dê xồn": "dê xồm",
    "sự hãi": "sợ hãi",
    "khách tiếng": "khét tiếng",
    "quấy dối": "quấy rối",
    "quỷ xuống": "quỳ xuống",
    "hỏa lớn": "hỏi lớn",
    "chờ mình": "trở mình",
    "chông chừng": "trông chừng",
    "chủ sở": "trụ sở",
    "râm rớm": "rơm rớm",
    "cha nam": "tra nam",
    "liếm cầu": "liếm cẩu",
    "tiền hóa": "tiến hóa",
    "vãi trưởng": "vãi chưởng",
    "cài quái": "cái quái",
    "dì cơ": "gì cơ",
    "lên may": "lên mây",
    "đang rìu": "đang dìu",
    "trung quyền": "trung nguyên",
    "thân giáo": "thần giáo",
    "tróng mặt": "chóng mặt",
    "khuya khuất": "khuya khoắc",
    "kê đáng": "cay đắng",
    "chạm chán": "chạm trán",
    "phục hương": "phục hưng",
    "chịu trùng": "chịu chung",
    "phắn đoán": "phán đoán",
    "lấý": "lấy",
    "run dày": "run rẩy",
    "dài ngoàn": "dài ngoằn",
    "súc tua": "xúc tua",
    "nhắt gan": "nhát gan",
    "bị gái": "bị gãy",
    "hoàng sợ": "hoảng sợ",
    "tổ chứng": "tổ trứng",
    "rồn rập": "dồn dập",
    "lồng cồn": "lồm cồm",
    "mũi rùi": "mũi dùi",
    "vò thẳng": "vọt thẳng",
    "tặc từ": "tặc tử",
    "tuông lấy": "túm lấy",
    "chọc thương": "trọng thương",
    "bào vệ": "bảo vệ",
    "rút lùi": "rút lui",
    "hừ lệnh": "hừ lạnh",
    "động quang": "độn quang",
    "đỏ giựt": "đỏ rực",
    "đau khí": "đao khí",
    "mũi đau": "mũi đao",
    "tan tật": "tàn tật",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "a thất lục": "a thập lục",
    "tông thư hàng": "tống thư hằng",
    "mục kiếm": "mộc kiếm",
    "sợ hải": "sợ hãi",
    "xợ hãi": "sợ hãi",
    "lùn ma khí": "luồng ma khí",
    "cười chừ": "cười trừ",
    "không quả": "không quản",
    "chứ đã": "trước đã",
    "dên lên": "rên lên",
    "tỏ vẽ": "tỏ vẻ",
    "rõ rạc": "dõng dạc",
    "sư mụy": "sư muội",
    "trưởng môn": "chưởng môn",
    "võ đàng": "võ đang",
    "bộ vốt": "bộ vuốt",
    "lên cẳm": "lên cằm",
    "hết lên": "hét lên",
    "hòa ra": "hóa ra",
    "oan ủng": "oan uổng",
    "dạo dực": "rạo rực",
    "rời sắc": "dời xác",
    "ta ma": "tà ma",
    "khô quát": "khô quắt",
    "cao mây": "cau mày",
    "nhân nhó": "nhăn nhó",
    "lục điện": "lục địa",
    "tạm môn": "tà môn",
    "trợt nhận": "chợt nhận",
    "quá lớn": "quát lớn",
    "nhất bỏng": "nhấc bổng",
    "phụ triện": "phù triện",
    "sơ lên": "giơ lên",
    "họ gieo": "hò reo",
    "xoái khí": "soái khí",
    "dơ bàn tay": "giơ bàn tay",
    "lùn linh": "luồng linh",
    "nhắc miệng": "nhếch miệng",
    "lời vừa giúp": "lời vừa dứt",
    "vô tức": "vô thức",
    "ngợ ngùng": "ngại ngùng",
    "sờ soãn": "sờ soạn",
    "e thẹt": "e thẹn",
    "chiếc giương": "chiếc rương",
    "bồ nước": "bồn nước",
    "thu tính": "thú tính",
    "run giảy": "run rẩy",
    "nhục trí": "nhụt chí",
    "chầm ngơm": "trầm ngâm",
    "dùng mình": "rùng mình",
    "hốt hỏa": "hốt hoảng",
    "công hiến": "cống hiến",
    "hồ hoán": "hô hoán",
    "ngay thấy": "nghe thấy",
    "long lan": "long lanh",
    "bộ chuyện": "bộ truyện",
    "bản bạc": "bàn bạc",
    "xói ca": "soái ca",
    "rắn vảy": "dáng vẻ",
    "kiểu thiên": "cửu thiên",
    "tức sận": "tức giận",
    ".0": "0",
    ".1": "1",
    ".2": "2",
    ".3": "3",
    ".4": "4",
    ".5": "5",
    ".6": "6",
    ".7": "7",
    ".8": "8",
    ".9": "9",
    "tri tử": "chi tử",
    "tri nữ": "chi nữ",
    "lập trí": "lập chí",
    "hoài báo": "hoài bão",
    "triệt đề": "triệt để",
    "qua khứ": "quá khứ",
    "quyền tiểu thuyết": "quyển tiểu thuyết",
    "tử hôn": "từ hôn",
    "chúc cơ": "trúc cơ",
    "trúc cơ kỷ": "trúc cơ kỳ",
    "nghẹt mặt": "nghệch mặt",
    "rứt câu": "dứt câu",
    "dây dừa": "dây dưa",
    "rút suy nghĩ": "dứt suy nghĩ",
    "sờ càm": "sờ cằm",
    "cười kinh": "cười khinh",
    "dây chức": "giây trước",
    "dây sau": "giây sau",
    "hoa nhảy": "hoa nhài",
    "cước trâu": "cức trâu",
    "lở lời": "lỡ lời",
    "hai đấy": "hay đấy",
    "mô típ": "mô tuýp",
    "cho chết": "chó chết",
    "phạm chủ": "phạm trù",
    "chuyển công": "truyền công",
    "xưng hút": "xưng húp",
    "trổm trễ": "chổm chệ",
    "chứ bát giới": "trư bát giới",
    "mùa hôi": "mồ hôi",
    "hé toáng": "hét toáng",
    "sắc ướp": "xác ướp",
    "mụi mụi": "muội muội",
    "nhất mép": "nhếch mép",
    "dương dương": "rưng rưng",
    "huynh mụi": "huynh muội",
    "lạm xác": "lạm sát",
    "khải ráp": "khải giáp",
    "long lành": "long lanh",
    "đấm máu": "đẫm máu",
    "dun dễ": "run rẩy",
    "của hán": "của hắn",
    "bình phòng": "bình phong",
    "cho cốt": "tro cốt",
    "xỉ khói": "xì khói",
    "mụi từ": "muội tử",
    "lấp lá": "lấp la",
    "hàng ngội": "hàng nguội",
    "lửa hói": "lừa hói",
    "nhân lại": "nhăn lại",
    "hơi thởi": "hơi thở",
    "quảnn": "quản",
    "lanhh": "lanh",
    "thắnh": "thánh",
    "gải": "gãi",
    "sư tồn": "sư tôn",
    "thưởng cổ": "thượng cổ",
    "thay nghiên": "thanh niên",
    "mùng": "mồm",
    "duy cho cùng": "suy cho cùng",
    "trượt trông": "chợt trông",
    "nghẹt ra": "nghệch ra",
    "sận": "giận",
    "nhét mép": "nhếch mép",
    "thả nhiên": "thản nhiên",
    "miến răng": "nghiến răng",
    "đống sang": "đốm sáng",
    "trưởng về": "chưởng về",
    "cường hắn": "cường hãn",
    "dơ hai tay": "giơ hai tay",
    "cầu dẫn": "câu dẫn",
    "giấc câu": "dứt câu",
    "dưng dưng": "rưng rưng",
    "cao gắt": "cáu gắt",
    "tay trời": "tày trời",
    "cung bái": "cúng bái",
    "bản tán": "bàn tán",
    "nhân tử": "nhân từ",
    "điện long": "địa long",
    "chở mình": "trở mình",
    "ngừng đầu": "ngẩng đầu",
    "trao đảo": "chao đảo",
    "khi chất": "khí chất",
    "luông sức mạnh": "luồng sức mạnh",
    "hết toán": "hét toán",
    "bồ lô bồ là": "bô lô bô la",
    "ngày thắng": "ngày tháng",
    "dè luyện": "rèn luyện",
    "hương thịnh": "hưng thịnh",
    "sừng sừng": "sừng sững",
    "trắng lệ": "tráng lệ",
    "đúng đáng": "đúng đắn",
    "ngàn rậm": "ngàn dặm",
    "dưa cao": "giơ cao",
    "ba ngày ban mặt": "ban ngày ban mặt",
    "cậu tặc": "cẩu tặc",
    "xe áo": "xé áo",
    "ngaynh": "nghênh",
    "rồi khỏi": "rời khỏi",
    "cửu truyền": "cửu chuyển",
    "đồ địa": "đồ đệ",
    "quân thử": "quân tử",
    "chọt vàng": "chọt vào",
    "thở vào": "thở phào",
    "ủng công": "uổng công",
    "trong coi": "trông coi",
    "áo troàng": "áo choàng",
    "nhúng nhảy": "nhún nhảy",
    "kinh tổm": "kinh tởm",
    "chiếm cứu": "chiếm cứ",
    "ngay đón": "nghênh đón",
    "ấp á ấp úm": "ấp a ấp úng",
    "há hóc": "há hốc",
    "chơn trượt": "trơn trượt",
    "gì sát": "dí sát",
    "ôm trầm": "ôm chầm",
    "dơ lên": "giơ lên",
    "vèo má": "véo má",
    "lùng linh khí": "luồng linh khí",
    "thẩm nghĩ": "thầm nghĩ",
    "cững ép": "cưỡng ép",
    "diễp": "diệp",
    "tay dơ": "tay giơ",
    "nghỉ thầm": "nghĩ thầm",
    "mưa màng": "mơ màng",
    "nước mắt trải": "nước mắt chảy",
    "dưa điện thoại": "giơ điện thoại",
    "tố rác": "tố giác",
    "tué": "tóe",
    "tay nghe": "tai nghe",
    "méttt": "mét",
    "nhảy cẫn": "nhảy cẫng",
    "vừa rước": "vừa dứt",
    "chầm xuống": "trầm xuống",
    "rơ ra": "giơ ra",
    "gây dối": "gây rối",
    "tên sinh": "tiên sinh",
    "hưng thú": "hứng thú",
    "đồng sự trưởng": "đổng sự trưởng",
    "chêu đùa": "trêu đùa",
    "giữ rắc": "dìu dắt",
    "chiếu dọi": "chiếu rọi",
    "tạo gia": "tạo ra",
    "trói mắt": "chói mắt",
    "đổ rồn": "đổ dồn",
    "phân thưởng": "phần thưởng",
    "sửng sững": "sừng sững",
    "chỉnh chu": "chỉn chu",
    "sởi lời": "xởi lởi",
    "quỳ công ty": "quý công ty",
    "bồn tiểu thư": "bổn tiểu thư",
    "trói trang": "chói chang",
    "chắn ản": "chán nản",
    "buồn dầu": "buồn rầu",
    "chùng với": "trùng với",
    "danh ma": "ranh ma",
    "đại hắn": "đại hán",
    "ca lớn nuốt": "cá lớn nuốt",
    "ca bé": "cá bé",
    "nhật nhạt": "nhợt nhạt",
    "thang bằng": "thăng bằng",
    "máu chóng": "mau chóng",
    "quốc chim": "cuốc chim",
    "danh giới": "ranh giới",
    "sẵn rò": "dặn dò",
    "đói dét": "đói rét",
    "tủng lung": "tùm lum",
    "cú à": "cô ả",
    "chữ chứng": "triệu chứng",
    "hương thú": "hứng thú",
    "cái cậy": "cái kệ",
    "nhẹ dọng": "nhẹ giọng",
    "nghiêm dọng": "nghiêm giọng",
    "thích thu": "thích thú",
    "giít": "rít",
    "lỏng đất": "lòng đất",
    "giận dỏ": "dặn dò",
    "chúng độc": "trúng độc",
    "răn ác": "gian ác",
    "mủm": "mồm",
    "rệ đi": "dậy đi",
    "rức khoát": "dứt khoát",
    "kết sắt": "két sắt",
    "ung tùm": "um tùm",
    "chút lát": "chốc lát",
    "vỏ giống": "vỏ rỗng",
    "cầm nín": "câm nín",
    "nhất bỗng": "nhấc bỗng",
    "vỏ giỗng": "vỏ rỗng",
    "ngơ mặt da": "ngơ mặt ra",
    "miễn cười": "mỉm cười",
    "lô là": "lâu la",
    "bía lùi": "mía lùi",
    "ngây chiến": "nghênh chiến",
    "nhến chặt": "nghiến chặt",
    "ra tóc": "gia tốc",
    "đắt ý": "đắc ý",
    "sợ rủi": "sợ rồi",
    "lùng năng lượng": "luồng năng lượng",
    "rè biểu": "dè biểu",
    "chung nó": "chúng nó",
    "kinh tờm": "kinh tởm",
    "vẫn khớp": "vặn khớp",
    "hạt sống": "hạt giống",
    "hay to": "hét to",
    "đầy dẫy": "đầy rẫy",
    "nhụm": "nhuộm",
    "vỉnh mép": "vểnh mép",
    "mang tay": "mang tai",
    "học máu": "hộc máu",
    "dọi sáng": "rọi sáng",
    "xích chặt": "siết chặt",
    "mồm hết": "mồm hét",
    "bay bỏng": "bay bổng",
    "ngứng đầu": "ngẩng đầu",
    "bảo trâu": "bảo châu",
    "nhàn chán": "nhàm chán",
    "siềng xích": "xiềng xích",
    "vãi cả trường": "vãi cả chưởng",
    "mặt may": "mặt mày",
    "xỉ cả khói": "xì cả khói",
    "vực thảm": "vực thẳm",
    "được cãi": "được cái",
    "con quả đen": "con quạ đen",
    "tôi sầm": "tối sầm",
    "giữ hôn lễ": "dự hôn lễ",
    "đều càng": "đểu cán",
    "xét đánh": "sét đánh",
    "báo thủ": "báo thù",
    "trường mắt": "trừng mắt",
    "xuất sinh": "súc sinh",
    "đến mạng": "đền mạng",
    "đen kịch": "đen kịt",
    "á đủ": "á đù",
    "liên trưởng": "liền chưởng",
    "trí bảo": "chí bảo",
    "liên chảm": "liên trảm",
    "tẩy tùy": "tẩy tủy",
    "rang rộng": "giang rộng",
    "đừng hồng": "đừng hòng",
    "năm đấm": "nắm đấm",
    "hung tận": "hung tợn",
    "chư thức": "chiêu thức",
    "cắn nút": "cắn nuốt",
    "sám xịt": "xám xịt",
    "đần ẩn": "đần đần",
    "dỉ ra": "rỉ ra",
    "lường mắt": "lườm mắt",
    "đỏ âu": "đỏ au",
    "thanh trâu": "thanh châu",
    "co dúng": "co rúm",
    "liên liếc nhìn": "liền liếc nhìn",
    "chắc địch": "chắc nịch",
    "quý xuống": "quỳ xuống",
    "trổng cắp mông": "chổng cặp mông",
    "tổ trảng": "tổ chảng",
    "tím dịm": "tím rịm",
    "tru toàn": "chu toàn",
    "so dự": "do dự",
    "rồn lên não": "dồn lên não",
    "gây rợn": "ghê rợn",
    "diệt chuyển": "dịch chuyển",
    "rơ hai tay": "giơ hai tay",
    "chức chán": "trước trán",
    "à ta": "ả ta",
    "phất phơi": "phất phơ",
    "vẽ mặt": "vẻ mặt",
    "phu quần": "phu quân",
    "cục cước": "cục cứt",
    "lau đến": "lao đến",
    "giữ câu": "dứt câu",
    "tất hải": "tất thẩy",
    "gạng giọng": "gặng giọng",
    "chứng mắt": "trừng mắt",
    "sung kích": "xung kích",
    "cùng bảo": "cuồng bạo",
    "lên thất thành": "lên thất thanh",
    "trẻ làm đôi": "chẻ làm đôi",
    "thở rốc": "thở dốc",
    "liền trưởng": "liền chưởng",
    "tiếng sáng": "tia sáng",
    "ngươi áo": "người áo",
    "nhanh như trước": "nhanh như chớp",
    "chung chú": "chăm chú",
    "là ngươi của": "là người của",
    "cử huyền": "cửu huyền",
    "bắt chì": "bất tri",
    "gượng ạo": "gượng gạo",
    "mỉn cười": "mỉm cười",
    "lau dày": "lau giày",
    "nhớng mày": "nhướng mày",
    "cứng hãn": "cường hãn",
    "giảng rỡ": "rạng rỡ",
    "hậu rệ": "hậu duệ",
    "quấy dày": "quấy rầy",
    "thức thởi": "thức thời",
    "nâng cầm": "nâng cằm",
    "lân lượt": "lần lượt",
    "ngẩn mặt": "ngẩng mặt",
    "dật mình": "giật mình",
    "bộ ráng": "bộ dáng",
    "đan rược": "đan dược",
    "nặng chĩu": "nặng trĩu",
    "xứng sở": "sững sờ",
    "loạn trọng": "loạn choạng",
    "vụy vã": "vội vã",
    "thong rong": "thong dong",
    "mệt mỏi nhì": "mệt mỏi nhỉ",
    "cây cú": "cay cú",
    "cây thiệt": "cay thiệt",
    "ra ra": "gia gia",
    "hục gấm": "hộp gấm",
    "ngàn giảm": "ngàn dặm",
    "ngẫu nghĩ": "ngẫm nghĩ",
    "nhân mặt": "nhăn mặt",
    "bất chi bất giác": "bất tri bất giác",
    "động lại": "đọng lại",
    "nhanh chí": "nhanh trí",
    "cho chót": "cho trót",
    "quề rốn": "quề dốn",
    "cải lại": "cãi lại",
    "tan sương": "tan xương",
    "trẻ làm hai": "chẻ làm hai",
    "gặn rộng": "gặng giọng",
    "ngay xong": "nghe xong",
    "dìu rắt": "dìu dắt",
    "sẵn dữ": "giận dữ",
    "nhan mặt": "nhăn mặt",
    "ủ ám": "u ám",
    "trổng mông": "chổng mông",
    "cục cướt": "cục cứt",
    "thần trưởng": "thần chưởng",
    "dữ rội": "dữ dội",
    "tung tuế": "tung tóe",
    "lào đảo": "lảo đảo",
    "chồng mông": "chổng mông",
    "nhọn hoát": "nhọn hoắc",
    "cao cấu": "cào cấu",
    "răng tơ": "giăng tơ",
    "tuẹt rời": "toẹt dời",
    "nuốt ức": "nuốt ực",
    "đăn hồi": "đàn hồi",
    "rán đầy": "dán đầy",
    "phù trú": "phù chú",
    "đôi mảy": "đôi mày",
    "mủ hôi": "mồ hôi",
    "tiếng thất thành": "tiếng thất thanh",
    "nõ nả": "nõn nà",
    "bỗng trốc": "bỗng chốc",
    "cây châm cải tóc": "cây trâm cài tóc",
    "ưu tối": "u tối",
    "lấp lanh": "lấp lánh",
    "sứng sở": "sững sờ",
    "vuốt dâu": "vuốt râu",
    "trang sáng": "trăng sáng",
    "mỉnh cười": "mỉm cười",
    "do động": "dao động",
    "thử lỗi": "thứ lỗi",
    "trúc lấy": "chuốc lấy",
    "cáo gắt": "cáu gắt",
    "siêu phạm": "siêu phàm",
    "vút cầm": "vuốt cằm",
    "tông ngôn": "tông môn",
    "bài kiến": "bái kiến",
    "miếng lụi": "mía lụi",
    "ngậm vào mù": "ngậm vào mồm",
    "trống hông": "chống hông",
    "đốt khí cụ": "đúc khí cụ",
    "cạnh giới": "cảnh giới",
    "nam xưa": "năm xưa",
    "kinh bỉ": "khinh bỉ",
    "trông đỡ": "chống đỡ",
    "trên chán": "trên trán",
    "trống đỡ": "chống đỡ",
    "cái sắc": "cái xác",
    "rơ lên": "giơ lên",
    "chó ngáp phải rồi": "chó ngáp phải ruồi",
    "yêu ái": "ưu ái",
    "giọng giặc": "dõng dạc",
    "đá lông nhao": "đá lông nheo",
    "cáo tử": "cáo từ",
    "rạt sang": "dạt sang",
    "trừa đường": "chừa đường",
    "khi thế": "khí thế",
    "gạng hỏi": "gặng hỏi",
    "dẫn dữ": "giận dữ",
    "đít nổi": "đít nồi",
    "cho mày": "chau mày",
    "ngây ngang": "nghênh ngang",
    "nhe giang": "nhe răng",
    "điểm tĩnh": "điềm tĩnh",
    "nghiến giang": "nghiến răng",
    "đắc trí": "đắc chí",
    "sáng dựng": "sáng rực",
    "hua tay": "khua tay",
    "trưởng một phát": "chưởng một phát",
    "an chọn": "ăn trọn",
    "dang rộng": "giang rộng",
    "bảo phát": "bạo phát",
    "gì ra": "rỉ ra",
    "vàm vỡ": "vạm vỡ",
    "sẵn giữ": "giận dữ",
    "chợt vật": "chật vật",
    "xữ rội": "dữ dội",
    "dao long": "giao long",
    "một trường": "một chưởng",
    "hát lớn": "hét lớn",
    "nguyên dận": "nguôi giận",
    "trưởng vừa rồi": "chưởng vừa rồi",
    "khiến trách": "khiển trách",
    "vút sâu": "vuốt râu",
    "chiếu dõi": "chiếu rọi",
    "sải dọng": "sải rộng",
    "loạn troạng": "loạn choạng",
    "phiên trợ": "phiên chợ",
    "ngồi sổm": "ngồi xổm",
    "cà ca": "ca ca",
    "trống tay": "chống tay",
    "thầm mĩ": "thầm nghĩ",
    "lừa mắt": "lườm mắt",
    "nám đấm": "nắm đấm",
    "ngứng mặt": "ngẩng mặt",
    "cả nằm trên": "cá nằm trên",
    "bam chặt": "băm chặt",
    "xin ta ừ": "xin ta ư",
    "khing": "khinh",
    "vuốt ve cầm": "vuốt ve cằm",
    "dỷ ra": "rỉ ra",
    "lồng ngược": "lồng ngực",
    "không chế": "khống chế",
    "quy xuống": "quỳ xuống",
    "nứt nảy": "nứt nẻ",
    "tiên lôi xách": "tia lôi sét",
    "một trưởng": "một chưởng",
    "dặn giò": "dặn dò",
    "trưởng một phát": "chưởng một phát",
    "luồngg": "luồng",
    "tiêu lôi xét": "tia lôi sét",
    "nhíu mảy": "nhíu mày",
    "màn trắng": "màn chắn",
    "màn trắn": "màn chắn",
    "rước lời": "dứt lời",
    "trắngg": "trắng",
    "lai động": "lay động",
    "lỗ hồng": "lỗ hổng",
    "vung vứt": "vuông vứt",
    "nhân dân tể": "nhân dân tệ",
    "lung cuống": "luống cuống",
    "nu triều": "nuông chiều",
    "không lửa": "không lừa",
    "sợi dâu": "sợi râu",
    "kinh tồng": "kinh tởm",
    "dã dụa": "giẫy dụa",
    "trợt nhớ": "chợt nhớ",
    "phẻ tay": "phẩy tay",
    "vẩy sâu": "vẩy râu",
    "phản háng": "phản kháng",
    "chùn chìa khóa": "chùm chìa khóa",
    "trắng bịch": "trắng bệch",
    "con dối": "con rối",
    "chiêu đùa": "trêu đùa",
    "ngừng ngơ": "ngẩn ngơ",
    "cường cáp": "cứng cáp",
    "chiêu con": "trêu con",
    "ông chóng": "ông cháu",
    "gập gềnh": "gập ghềnh",
    "ống ánh": "óng ánh",
    "sát vàng": "dát vàng",
    "trợt lóe": "chợt lóe",
    "trắng bệnh": "trắng bệch",
    "lôn tiếng": "lớn tiếng",
    "sơ ký": "sờ kỹ",
    "dạng săn hô": "rạng san hô",
    "dãng dỡ": "rạng rỡ",
    "súc tu": "xúc tu",
    "ngọc chai": "ngọc trai",
    "chẳng đầy": "tràn đầy",
    "cho tàn": "tro tàn",
    "lan sương mù": "làn sương mù",
    "trợt ngây": "chợt ngây",
    "hoàng tuyển": "hoàng tuyền",
    "ẩn trưa": "ẩn chứa",
    "cảnh dưới": "cảnh giới",
    "buột miệng": "buộc miệng",
    "tưởng trừng": "tưởng chừng",
    "súp tu": "xúc tu",
    "lưng chồng": "lưng tròng",
    "trợt mềm": "chợt mềm",
    "mềm nhũng": "mềm nhũn",
    "khống chết": "không chết",
    "trượt lóe": "chợt lóe",
    "ánh sẽ": "anh xé",
    "trải rường": "trải giường",
    "từng dài": "từng dải",
    "sẵn dò": "dặn dò",
    "nhất định dãy": "nhất định sẽ",
    "ẩm ẩm ẩm": "ầm ầm ầm",
    "dung chuyển": "rung chuyển",
    "đục ngâu": "đục ngầu",
    "ồ ồ ồ": "ù ù ù",
    "lạnh búa": "lạnh buốc",
    "chảy rường": "trải giường",
    "găng tắc": "gang tấc",
    "mê nuội": "mê muội",
    "ủng ủc": "ùng ục",
    "ừc": "ực",
    "trong trèo": "trong trẻo",
    "tốt cùng": "tột cùng",
    "giận tóc": "rợn tóc",
    "tóc gái": "tóc gáy",
    "dãy ruộng": "giãy dụa",
    "lây chuyển": "lay chuyển",
    "nhuống": "nhuốm",
    "chở tay": "trở tay",
    "the the": "the thé",
    "trao ra": "trào ra",
    "buông lòng": "buông lỏng",
    "dãy dụ": "giãy dụa",
    "mối bỏ bề": "muối bỏ bể",
    "ngồi vịt": "ngồi phịch",
    "run dậy": "run rẩy",
    "luận lờ": "lượn lờ",
    "thiền cận": "thiển cận",
    "thủy tình": "thủy tinh",
    "sát sống": "xác sống",
    "bóng giáng": "bóng dáng",
    "ngưa ngác": "ngơ ngác",
    "nước toác": "nứt toác",
    "khe nước": "khe nứt",
    "nước chừng": "nuốt chửng",
    "sẽ rụ": "giãy dụa",
    "giỡng": "giỡn",
    "dãy dụ": "giãy dụa",
    "ngương hác": "ngơ ngác",
    "săn hô": "san hô",
    "rác rác rác": "rắc rắc rắc",
    "quả chứng": "quả trứng",
    "tiêm mờ mịt": "tia mờ mịt",
    "ngọc chai": "ngọc trai",
    "chứng cút": "trứng cút",
    "kề rau": "kề dao",
    "một phên": "một phen",
    "quả chứng": "quả trứng",
    "nhà nhạt": "nhàn nhạt",
    "áo tràng": "áo choàng",
    "thị thầm": "thì thầm",
    "hiêu vũ": "khiêu vũ",
    "thủy chiều": "thủy triều",
    "huyết xâm": "huyết sâm",
    "thân dược": "thần dược",
    "quỷ quai": "quỷ quái",
    "cứng như sát": "cứng như sắt",
    "đau thương bất nhập": "đao thương bất nhập",
    "mây mông": "mênh mông",
    "huyết xáo": "huýt sáo",
    "rãng rỡ": "rạng rỡ",
    "ghu chết": "hù chết",
    "nhạt được": "nhặt được",
    "hoàn hoãn": "ngoan ngoãn",
    "bò bọc": "bao bọc",
    "tuổi tắc": "tuổi tác",
    "nguyền rủ": "nguyền rủa",
    "hú hú hú": "hu hu hu",
    "chưa rứt": "chưa dứt",
    "bị chặt": "bịt chặt",
    "chạm trung chuyển": "trạm trung chuyển",
    "trạm trung truyền": "trạm trung chuyển",
    "tourvít": "tua vít",
    "thương ngài": "thưa ngài",
    "sắp tiền": "sấp tiền",
    "giày cộp": "dày cộp",
    "vali": "va li",
    "kinh chiếu yêu": "kính chiếu yêu",
    "ẩn dấu": "ẩn giấu",
    "nhễ nhạy": "nhễ nhại",
    "móc phí": "móc ví",
    "đừng giờ cho": "đừng giở trò",
    "cười trói": "cởi trói",
    "dày cao gót": "giày cao gót",
    "lột cộp": "lộp cộp",
    "bù nháo": "bùn nhão",
    "súc tú": "xúc tu",
    "chẳng đầy": "tràn đầy",
    "chầm trầm": "chằm chằm",
    "chọc lốc": "trọc lóc",
    "tâm hơi": "tăm hơi",
    "sắc dối": "rắc rối",
    "chúc lấy": "chuốc lấy",
    "rụ rỗ": "dụ dỗ",
    "cám rỗ": "cám dỗ",
    "nhít người": "nhích người",
    "gạm": "gặm",
    "ủ rú": "ủ rủ",
    "hà hê": "hả hê",
    "vừa vạn": "vừa vặn",
    "rủaa": "rủa",
    "ệnhnhnh": "ệnh",
    "ệnhnh": "ệnh",
    "uốngg": "uống",
    "ẫngg": "ẫng",
    "vòn vẹn": "vỏn vẹn",
    "bộ rác": "bộ giáp",
    "chưa hôm sau": "trưa hôm sau",
    "lộn thụng": "lộm thộm",
    "dối ghen": "rối ren",
    "tri viện": "chi viện",
    "xuyết chút": "suýt chút",
    "nuê": "nuôi",
    "gợt đầu": "gật đầu",
    "khai khẽ": "khe khẽ",
    "lấp đẩy": "lấp đầy",
    "chiêu yêu": "chiếu yêu",
    "vạn dạm": "vạn dặm",
    "ru ngoạn": "du ngoạn",
    "hung mảnh": "hung mãnh",
    "trồng lên nhau": "chồng lên nhau",
    "đăng đăng": "đang đang",
    "vật đầu": "gật đầu",
    "cất đổ": "cất đồ",
    "mini": "mi ni",
    "trói tai": "chói tai",
    "trói tay": "chói tai",
    "dung lên": "rung lên",
    "rãi núi": "dãy núi",
    "rõ rét": "dò xét",
    "cổ học": "cổ họng",
    "ôn đầu": "ôm đầu",
    "bỏ dậy": "bò dậy",
    "trích tiệt": "chết tiệt",
    "tue tóet": "toe toét",
    "gõng kính": "gọng kính",
    "yêu ất": "yếu ớt",
    "lù nhiệt": "luồng nhiệt",
    "bịt tay": "bịt tai",
    "nhé mắt": "nháy mắt",
    "lầu mờ": "lờ mờ",
    "thịt vũng": "thịt vụn",
    "chầm đục": "trầm đục",
    "mý mắt": "mí mắt",
    "chầm thấp": "trầm thấp",
    "lạng lẽ": "lặng lẽ",
    "rò xét": "dò xét",
    "hình nộn": "hình nộm",
    "đông loạt": "đồng loạt",
    "lenh canh": "len ken",
    "cam rỗ": "cám giỗ",
    "rông dạ": "rơm rạ",
    "bịn tay": "vịn tay",
    "đàm nhận": "đảm nhận",
    "nghỉ người": "nghỉ ngơi",
    "chầm ấm": "trầm ấm",
    "giao động": "dao động",
    "ít hầu": "yết hầu",
    "ăn vật": "ăn vặt",
    "trợt hiểu": "chợt hiểu",
    "mềm nhuốn": "mềm nhũn",
    "trắng bề": "trắng bệt",
    "phết xẹo": "vết sẹo",
    "giữ tợn": "dữ tợn",
    "phiên đá": "viên đá",
    "nước nở": "nức nở",
    "cầm miệng": "câm miệng",
    "kỳ thơi": "kịp thời",
    "sông lên": "xông lên",
    "trinh lịch": "chênh lệch",
    "cú đầm": "cú đấm",
    "ngụ máu": "ngụm máu",
    "hẳn ý": "hàn ý",
    "trần chuồng": "trần truồng",
    "rơm dạng": "rơm rạ",
    "nhạc chung": "nhạc chuông",
    "ngoài chứ": "ngoài trừ",
    "sai đắm": "say đắm",
    "rác ngộ": "giác ngộ",
    "quyển vờ": "quyển vở",
    "chử tà": "trừ tà",
    "lức nở": "nức nở",
    "cúi trào": "cúi chào",
    "chố mắt": "trố mắt",
    "thủ lao": "thù lao",
    "dơ ngón": "giơ ngón",
    "không xót": "không sót",
    "đồ kỵ": "đố kỵ",
    "đẹp chai": "đẹp trai",
    "sáng sửa": "sáng sủa",
    "da dì": "ra gì",
    "nảy nọ": "này nọ",
    "chai xinh": "trai xinh",
    "vóng vải": "vắng vẻ",
    "cười giăng": "cười gian",
    "tắt nghiệp": "tác nghiệp",
    "ràng giải": "giảng giải",
    "chế tắc": "chế tác",
    "lau về": "lao về",
    "đấu kỵ": "đố kỵ",
    "rằng co": "giằng co",
    "điên cùng": "điên cuồng",
    "iphone": "ai phôn",
    "video": "vi đê ô",
    "youtube": "diu túp",
    "edit": "e đít",
    "viral": "vai rồ",
    "add": "át",
    "tiếc núi": "tiếc nuối",
    "bồn pháp sư": "bổn pháp sư",
    "mạo mụi": "mạo muội",
    "sát xuất": "xác xuất",
    "dụng chứng": "rụng trứng",
    "bớt quá": "bất quá",
    "nằm dạp": "nằm rạp",
    "lồng cồm": "lồm cồm",
    "ký tức": "khí tức",
    "khác chế": "khắc chế",
    "thoang cái": "thoáng cái",
    "chầm giọng": "trầm giọng",
    "haha": "ha ha",
    "trên lời": "chen lời",
    "dĩ năng": "dị năng",
    "giắt người": "dắt người",
    "dễ cây": "rễ cây",
    "châu bỏ": "trâu bò",
    "phi đau": "phi đao",
    "nhét lên": "nhếch lên",
    "xít chặt": "siết chặt",
    "hác ráp": "hắc giáp",
    "gào giống": "gào rống",
    "chàn ra": "tràn ra",
    "khâu chung": "không trung",
    "người gá": "người gã",
    "chêu người": "trêu ngươi",
    "sâu xí": "xấu xí",
    "ẩm một tiếng": "ầm một tiếng",
    "sương khốt": "xương cốt",
    "bất hóa": "bất quá",
    "vút xuống": "vứt xuống",
    "giống ít hết": "giống y hệt",
    "ok": "ô kê",
    "zombie": "giom bi",
    "topping": "top ping",
    "full": "phun",
    "độc nhãn lòng": "độc nhãn long",
    "viên trâu": "viên châu",
    "đỏ trói": "đỏ chói",
    "lặng lặng": "lẳng lặng",
    "hạt trâu": "hạt châu",
    "shipper": "síp pơ",
    "thương ài": "thưa ngài",
    "venh": "vênh",
    "lỗ tay": "lỗ tai",
    "sao trổi": "sao chổi",
    "cam tức": "căm tức",
    "bi phẫn hết": "bi phẫn hét",
    "virus": "vi rút",
    "app": "áp",
    "điều luyện": "điêu luyện",
    "đầy áp": "đầy ắp",
    "phản nàn": "phàn nàn",
    "vương vai": "vươn vai",
    "thổ điện": "thổ địa",
    "cốt điện": "cột điện",
    "mải nhìn": "mãi nhìn",
    "ship ": "síp ",
    "ông lấy bụng": "ôm lấy bụng",
    "trang sĩ": "tráng sĩ",
    "đồng su": "đồng xu",
    "kêu là oai oai": "kêu la oai oái",
    "bảy tắc": "bảy tấc",
    "soi đo": "so đo",
    "tự riễu": "tự giễu",
    "hán thấy": "hắn thấy",
    "diếng": "giếng",
    "à à à": "a a a",
    "bồn cung": "bổn cung",
    "đau ván": "đo ván",
    "mầy mò": "mày mò",
    "mỹ ăn liền": "mỳ ăn liền",
    "chứng gà": "trứng gà",
    "sông khói": "xông khói",
    "một tiếng ẩm": "một tiếng ầm",
    "ngót ngót": "ngoắc ngoắc",
    "sách cái": "xách cái",
    "chứng này": "trứng này",
    "dơ ra": "giơ ra",
    "vàng ống": "vàng óng",
    "cư rao": "cứ giao",
    "đất đỏ": "đắt đỏ",
    "người thấy mùi": "ngửi thấy mùi",
    "dữ người": "sững người",
    "dẫn rõ": "dặn dò",
    "mối thủ": "mối thù",
    "dạp chiếu": "rạp chiếu",
    "bản công": "bản cung",
    "nhất nách": "nhức nách",
    "mặt dây": "mặt dày",
    "nhảy trồm": "nhảy chồm",
    "nguyệt quê": "nguyệt quế",
    "trợ hoán": "triệu hoán",
    "lăn khói": "làn khói",
    "xấu múi": "6 múi",
    "vào ngược": "vào ngực",
    "rồn ép": "dồn ép",
    "rượu kế": "diệu kế",
    "dân dị": "rên rỉ",
    "phi phó": "phì phò",
    "veo má": "véo má",
    "rắn vẻ": "dáng vẻ",
    "giót": "rót",
    "chầm trồ": "trầm trồ",
    "thường nóng": "thưởng nóng",
    "đên cuồng": "điên cuồng",
    "ngấu miến": "ngấu nghiến",
    "liên tranh thủ": "liền tranh thủ",
    "nhắc lên": "nhấc lên",
    "rội thẳng": "dội thẳng",
    "trả nước": "trà nước",
    "giật thoát": "giật thót",
    "ninja": "ninh gia",
    "mất đã": "mất đà",
    "bỏng giát": "bỏng rát",
    "rắt xuống": "dắt xuống",
    "sẽ chau": "sẽ cho",
    "rất theo": "dắt theo",
    "thiếu da": "thiếu gia",
    "nhỏ rộng": "nhỏ giọng",
    "cung nganh": "cung nghênh",
    "chỉ huy xứ": "chỉ huy sứ",
    "xanh cả giái": "xanh cả dái",
    "sẽ đên": "sẽ đến",
    "tỏ về": "tỏ vẻ",
    "đầu cắt môi": "đầu cắt moi",
    "văng lệnh": "vâng lệnh",
    "rắc mặt": "sắc mặt",
    "dàng đường": "giảng đường",
    "thể cô": "thầy cô",
    "lạnh rộng": "lạnh giọng",
    "rừng tay": "dừng tay",
    "trường hộc": "trường học",
    "một đau": "một đao",
    "ruôn giọng": "run giọng",
    "hãy thà": "hãy tha",
    "rầm mưa": "dầm mưa",
    "rút đau": "rút đao",
    "bào ứng": "báo ứng",
    "bà gia": "bà già",
    "tranh lệch": "chênh lệch",
    "dưới chứng": "dưới trướng",
    "dén": "rén",
    "bùng máu": "búng máu",
    "khi kình": "khí kình",
    "từ ra": "tứ gia",
    "lễ gia": "lẽ ra",
    "trầm mặc": "trầm mặt",
    "rối cuộc": "rốt cuộc",
    "đang quỷ": "đang quỳ",
    "gian luyện": "rèn luyện",
    "biến cô": "biến cố",
    "ba nội": "bà nội",
    "giả vâng": "dạ vâng",
    "trưởng từ": "trưởng tử",
    "âm chầm": "âm trầm",
    "rút đào": "rút đao",
    "cha ra": "tra ra",
    "to tắt": "to tát",
    "nhờ và": "nhờ vả",
    "nóng này": "nóng nảy",
    "đầu chuông": "đổ chuông",
    "tư sinh": "tiên sinh",
    "vội dơ": "vội giơ",
    "trả trách": "chả trách",
    "khoản vai": "khoản vay",
    "vai nóng": "vay nóng",
    "sàng khoái": "sảng khoái",
    "tôi vai": "tôi vay",
    "sang sớm": "sáng sớm",
    "mỉn cưới": "mỉm cười",
    "đình ước": "đính ước",
    "tháp hương": "thắp hương",
    "trướng mắt": "chướng mắt",
    "dẫn xôi": "giận sôi",
    "nhập hộc": "nhập học",
    "bệnh thân kinh": "bệnh thần kinh",
    "vung trưởng": "vung chưởng",
    "trắn nản": "chán nản",
    "mà kệ": "mặc kệ",
    "lộn sộn": "lộn xộn",
    "hãng nói": "hẵng nói",
    "thành rao": "thành giao",
    "khi tức": "khí tức",
    "chêu chọc": "trêu chọc",
    "khách xào": "khách sáo",
    "cứng còi": "cứng cỏi",
    "xầm mặt": "sầm mặt",
    "võ già": "võ giả",
    "xắc mặt": "sắc mặt",
    "thiêu ra": "thiếu gia",
    "sưng hô": "xưng hô",
    "ruôn giẩy": "run rẩy",
    "đội trường": "đội trưởng",
    "chén trả": "chén trà",
    "run rộng": "run giọng",
    "cất chó": "cứt chó",
    "dơ chân": "giơ chân",
    "nhắc hắn lên": "nhấc hắn lên",
    "lên bản": "lên bàn",
    "ôm song": "om sòm",
    "lửng lẫy": "lừng lẫy",
    "ảo rác": "ảo giác",
    "thử kế": "thừa kế",
    "mau tróng": "mau chóng",
    "ai ra": "ai gia",
    "thèm thùng": "thèm thuồng",
    "chó gáy": "chó ghẻ",
    "trự hồi": "triệu hồi",
    "ai dồ": "ai giô",
    "bắt chói": "bắt trói",
    "bẩn thiều": "bẩn thiểu",
    "ăn chai": "ăn chay",
    "dấu dưới": "giấu dưới",
    "hết vào": "hét vào",
    "chào ngai": "chào ngài",
    "nay thì": "này thì",
    "phở lát": "phờ lát",
    "biên thái": "biến thái",
    "quần dịp": "quần sịp",
    "dài ngoang": "dài ngoằng",
    "iq": "ai kiêu",
    "thiêu nữ": "thiếu nữ",
    "trung tin nhắn": "chuông tin nhắn",
    "email": "y meo",
    "lẩm bầm": "lẩm bẩm",
    "game": "ghem",
    "ceo": "xi e ô",
    "cuốc máy": "cúp máy",
    "dây chán": "dây trán",
    "cộng quản lý": "cục quản lý",
    "tức dẫn": "tức giận",
    "trộn đồ ăn": "trộm đồ ăn",
    "truyền phát nhanh": "chuyển phát nhanh",
    "himalaya": "hi ma lay a",
    "kinh hạc": "kinh ngạc",
    "chào phúng": "trào phúng",
    "nói phép": "nói phét",
    "lan lộn": "lăn lộn",
    "manga": "man ga",
    "dài luyện": "rèn luyện",
    "chơi đãi": "chiêu đãi",
    "ái trà": "ái chà",
    "thiêu hào": "tiêu hao",
    "đầu chọc": "đầu trọc",
    "sen mồm": "xen mồm",
    "bay cho": "bày trò",
    "hỗ sược": "hỗn xược",
    "đi hộc": "đi học",
    "tiệc dựa": "tiệc rượu",
    "phòng ấn": "phong ấn",
    "sửa cả gai ốc": "sởn cả gai ốc",
    "xong tới": "xông tới",
    "tung trưởng": "tung chưởng",
    "sờ dĩ": "sở dĩ",
    "như người": "như ngươi",
    "nên tiếp": "liên tiếp",
    "báo được thủ": "báo được thù",
    "mâu chốt": "mấu chốt",
    "làm ngờ": "làm ngơ",
    "chê người": "trên người",
    "chừng trị": "trừng trị",
    "mau gà": "mào gà",
    "nhơ xuống": "nhớ xuống",
    "say khiến": "sai khiến",
    "vái lại": "bái lạy",
    "roi ra": "roi da",
    "thất lưng": "thắt lưng",
    "để nấy": "đến đấy",
    "dạ chết": "dọa chết",
    "quyền bí kĩ": "quyển bí kĩ",
    "cực một lần": "cược một lần",
    "cầm mồm": "câm mồm",
    "sexy": "séc xy",
    "album": "an bum",
    "icon": "ai kình",
    "online": "on lai",
    "offline": "ọp lai",
    "carbon": "các bon",
    "giải hoàng": "dài ngoằng",
    "hỏng rôi": "hỏng rồi",
    "bất chắc": "bất trắc",
    "mở mạn": "mở màn",
    "thân bí": "thần bí",
    "bồng bình": "bồng bềnh",
    "vẫn may": "vận may",
    "trọt trúng": "chọt trúng",
    "chỗ đong": "chỗ đau",
    "khôn kiếp": "khốn kiếp",
    "chat": "chát",
    "tiên bối": "tiền bối",
    "chấp vá": "chắp vá",
    "luôn phiên": "luân phiên",
    "phiền tói": "phiền toái",
    "sóng xoài": "sỏng soài",
    "đông ngẹt": "đông nghẹt",
    "phòng viết": "phòng víp",
    "rường bệnh": "giường bệnh",
    "ngói đầu": "ngoi đầu",
    "nào ngơ": "nào ngờ",
    "nghiêu ngao": "nghêu ngao",
    "xong vào": "xông vào",
    "camera": "ca me ra",
    "sai vật": "sai vặt",
    "do phó": "giao phó",
    "tăng vật": "tang vật",
    "tố chức": "tố chất",
    "dối loạn": "rối loạn",
    "ai rè": "ai dè",
    "yếu siều": "ỉu xìu",
    "đánh ngứt": "đánh ngất",
    "tiểu hiểu": "tiểu hữu",
    "đảng chí": "đảng trí",
    "ngữ kiếm": "ngự kiếm",
    "chọn đời": "trọn đời",
    "từ đầu trí cuối": "từ đầu chí cuối",
    "dãy mạnh": "giãy mạnh",
    "pháp khi": "pháp khí",
    "ngon ngẻ": "ngon nghẻ",
    "bẻn": "bèn",
    "minh mông": "mênh mông",
    "tha bỏng": "tha bổng",
    "cuồng đau": "cuồng đao",
    "đảnh lòng": "đành lòng",
    "kiểu non": "cừu non",
    "đổ kiếp": "độ kiếp",
    "nghiên răng": "nghiến răng",
    "canh két": "ken két",
    "dơ cao": "giơ cao",
    "hồng hộp": "hồng hộc",
    "tươi giói": "tươi rói",
    "dân dạy": "răn dạy",
    "mất mái": "mấp máy",
    "ấp tới": "ập tới",
    "mũi nhảy": "mũi nhạy",
    "thưởng thức": "thường thức",
    "màn xương": "màn sương",
    "trộp": "chộp",
    "một chảo": "một trảo",
    "đong gói": "đóng gói",
    "chức đã": "trước đã",
    "taxi": "tắc xi",
    "tiếng giống": "tiếng rống",
    "nhức ốc": "nhức óc",
    "rượt thủy": "dược thủy",
    "đợi thò": "đợi thỏ",
    "làm gọi": "làm gỏi",
    "át phải": "ắt phải",
    "à đù": "á đù",
    "vẽ mời": "vé mời",
    "mạng sông": "mạng sống",
    "quay hóa": "quay ngoắc",
    "phân mềm": "phần mềm",
    "trúc cờ": "trúc cơ",
    "đệt mỡ": "đệt mợ",
    "hàn nhớ": "hắn nhớ",
    "trôn sâu": "chôn sâu",
    "hỏi rò": "hỏi dò",
    "lặng lãng": "lẳng lặng",
    "nhuốn vai": "nhún vai",
    "chăm chằm": "chằm chằm",
    "ngỗng nghĩ": "ngẫm nghĩ",
    "salon": "sa lông",
    "lệnh lùng": "lạnh lùng",
    "dống lên": "rống lên",
    "nói bữa": "nói bừa",
    "giờ cao": "giơ cao",
    "ba khí": "bá khí",
    "cơ thầy": "cơ thể",
    "áp đào": "áp đảo",
    "dận dữ": "giận dữ",
    "hán giận": "hắn giận",
    "ra chiêu chức": "ra chiêu trước",
    "kinh kỵ": "kiên kỵ",
    "bấu phiếu": "bấu víu",
    "thủ chảo": "thủ trảo",
    "chảo ảnh": "trảo ảnh",
    "quạp xuống": "quặp xuống",
    "chiêu chức": "chiêu thức",
    "làm đào": "làm đao",
    "ảnh đào": "ánh đao",
    "đào thế": "đao thế",
    "chảo công": "trảo công",
    "đào chém": "đao chém",
    "nát bương": "nát bươm",
    "đánh giạp": "đánh rạp",
    "đồ ra dụng": "đồ gia dụng",
    "một đào": "một đao",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ffff": "ffff",
    "ột ột": "ọt ọt",
    "ít cốc": "ích cốc",
    "à thập": "a thập",
    "chúng chưa": "trúng chiêu",
    "ác sú hoàn": "ác xú hoàn",
    "cửa đấy": "cơ đấy",
    "trự nhã nhã": "triệu nhã nhã",
    "chịu nhã nhã": "triệu nhã nhã",
    "à cộng": "a còng",
    "a thất lực": "a thập lục",
    "bắc hà ta nhân": "bắc hà tán nhân",
    "bắt hà ta nhân": "bắc hà tán nhân",
    "bác hà tá nhân": "bắc hà tán nhân",
    "thưa hàng": "thư hằng",
    "tổng thư hàng": "tống thư hằng",
    "tống thư hàng": "tống thư hằng",
    "cướp máy": "cúp máy",
    "bắn chúng": "bắn trúng",
    "bác hà": "bắc hà",
    "trân quân": "chân quân",
    "giã tượng vương": "dã tượng vương",
    "bảng long": "bàng long",
    "như ma vương": "ngưu ma vương",
    "bằng lòng": "bàng long",
    "lý ra": "lý gia",
    "đánh chúng": "đánh trúng",
    "nhị đạp": "nhị đà",
    "chủ tới": "chủ tớ",
    "nhất phạm": "nhất phàm",
    "tiếp mai": "tuyết mai",
    "cậu yêu": "cẩu yêu",
    "tụ trường": "tụ trưởng",
    "bạn yêu vương": "bản yêu vương",
    "bất cảnh": "bắc cảnh",
    "bắc như": "bắc nhi",
    "tam ra": "tam gia",
    "chấn bác vương": "trấn bắc vương",
    "bác vương": "bắc vương",
    "tần ra": "tần gia",
    "xử ra": "sử gia",
    "bác lương": "bắc lương",
    "bố đi": "bố y",
    "bác cảnh": "bắc cảnh",
    "bác nhi": "bắc nhi",
    "tứ ra": "tứ gia",
    "nhị da": "nhị gia",
    "nhị ra": "nhị gia",
    "lương da": "lương gia",
    "bác nghi": "bắc nhi",
    "ninh bắt": "ninh bắc",
    "ninh bắp": "ninh bắc",
    "nhị ra": "nhị gia",
    "tiểu bác": "tiểu bắc",
    "ninh ra": "ninh gia",
    "tô ra": "tô gia",
    "cắt đầu mò": "cắt đầu moi",
    "chấn bắc vương": "trấn bắc vương",
    "ba vương": "bá vương",
    "khả lòng vệ": "khả long vệ",
    "dơ vòng tay": "giơ vòng tay",
    "ninh bác": "ninh bắc",
    "giỏi làm sao": "giỏi lắm sao",
    "trưng trung nguyên": "trương trung nguyên",
    "chương trung nguyên": "trương trung nguyên",
    "bác hổ": "bắc hổ",
    "vượt qua giới hạn": "vượt quá giới hạn",
    "bác vương": "bắc vương",
    "lương ra": "lương gia",
    "đực": "được",
    "hù hù": "hu hu",
    "cựu linh": "cự linh",
    "ngoạ tào": "ngọa tào",
    "cười ra": "cười gian",
    "nhưng không nhầm": "nhớ không nhầm",
    "nang": "nàng",
    "na cha": "na tra",
    "cướp chứng": "cướp trứng",
    "trong chứng": "trong trứng",
    "trên dầu": "chiên dầu",
    "kỳ bằng": "kim bằng",
    "giới nhân gian": "dưới nhân gian",
    "giới trần": "dưới trần",
    "một tâm": "một tấm",
    "gửi lên": "cưỡi lên",
    "dựa vào đầu": "dựa vào đâu",
    "hàng nga": "hằng nga",
    "rất lời": "dứt lời",
    "đồ an": "đồ án",
    "tiết điểm": "tiếp điểm",
    "ẩm,": "ầm,",
    "cột đầu": "cụt đầu",
    "dĩ cây": "rễ cây",
    "chuyên đến": "truyền đến",
    "bất quả": "bất quá",
    "lám đấm": "lắm đấm",
    "ráp đen": "giáp đen",
    "tế bảo": "tế bào",
    "để bảo": "tế bào",
    "trôi ra": "trồi ra",
    "thức độ": "tốc độ",
    "là hàn": "la hàn",
    "tô huỳnh": "tô huyền",
    "rút ta": "giúp ta",
    "đấm da": "đấm ra",
    "đừng hòa": "đừng mà",
    "trận đánh": "chặn đánh",
    "giang hô": "răng hô",
    "giống lớn": "rống lớn",
    "bước qua": "bất quá",
    "thôi quá": "thối quá",
    "thi chiều": "thi triều",
    "xích lại": "siết lại",
    "trừ ta": "trừ tà",
    "takai": "ta cai",
    "asakura": "a sa ku ra",
    "remio": "rê mi ô",
    "tỉnh giai": "tịnh giai",
    "truyền thành": "chuyển thành",
    "lão chủ": "lão trụ",
    "giá lô": "gia lô",
    "max": "mắt",
    "hi ge": "hi gie",
    "gỗ muôn": "gỗ mun",
    "chừ ta": "trừ tà",
    "chứ ta": "trừ tà",
    "chờ đãi": "chiêu đãi",
    "ramen": "ra men",
    "suga": "su ga",
    "chian": "chi an",
    "asada": "a sa đa",
    "arakawa": "a ra ca qua",
    "xuất ra": "xuất gia",
    "hibiya": "hi bi da",
    "chủ trì": "trụ trì",
    "jemio": "gie mi ô",
    "hize": "hi gie",
}

# def cleaner_text(text, is_loi_chinh_ta=True):
#     for word, replacement in viet_tat.items():
#         text = text.replace(word, replacement)
#     text = text.lower()
#     for word, replacement in special_word.items():
#         text = text.replace(word, replacement)
#     if is_loi_chinh_ta:
#         for wrong, correct in loi_chinh_ta.items():
#             text = text.replace(wrong, correct)
#     return text

def cleaner_text(text, is_loi_chinh_ta=True):
    for word, replacement in viet_tat.items():
        text = text.replace(word, replacement)
    text = text.lower()
    for word, replacement in special_word.items():
        text = text.replace(word, replacement)
    if is_loi_chinh_ta:
        for wrong, correct in loi_chinh_ta.items():
            text = re.sub(rf'\b{re.escape(wrong)}(\W?)', rf'{correct}\1', text)
    return text.strip()


# # -------Sửa chính tả trong file txt và xuất ra file txt khác-------
# cnt = 1
# old_txt = "E:\\Python\\developping\\review comic\\test\\1.txt"

# fol = os.path.dirname(old_txt)
# file_name = os.path.basename(old_txt).split('.')[0]
# new_txt = os.path.join(fol, f'{file_name}_1.txt')
# with open(old_txt, 'r', encoding='utf-8') as fff:
#     lines = fff.readlines()
# with open(new_txt, 'w', encoding='utf-8') as ggg:
#     for line in lines:
#         if line and not line.strip().isdigit():
#             line = cleaner_text(line.strip())
#             ggg.write(f'{cnt}\n{line}\n')
#             cnt += 1












#--------------tổng hợp các file sub và audio-----------------------------
def get_text_and_audio_in_folder(folder, txt_total='total.txt', audio_total_folder='total'):
    os.makedirs(audio_total_folder, exist_ok=True)
    txt_files = get_file_in_folder_by_type(folder, '.txt')
    unique_lines = set()  # Dùng set để lưu các dòng đã ghi (tìm kiếm nhanh hơn)
    index = 0
    
    try:
        with open(txt_total, mode='w', encoding='utf-8') as total:  # Ghi đè file tổng
            for txt_f in txt_files:
                txt_path = os.path.join(folder, txt_f)
                file_name = os.path.splitext(txt_f)[0]
                audio_folder = os.path.join(folder, file_name)
                audios = get_file_in_folder_by_type(audio_folder, '.wav')
                try:
                    with open(txt_path, mode='r', encoding='utf-8') as fff:
                        lines = fff.readlines()
                    i_au = 0
                    for line in lines:
                        line_content = line.strip()
                        # Kiểm tra nếu không phải số
                        if not line_content.isdigit():
                            if i_au >= len(audios):  # Kiểm tra số lượng audio
                                print(f"Warning: Không đủ file audio cho file {txt_f}")
                                break
                            
                            if line_content not in unique_lines and len(line_content) < max_lenth_text:
                                index += 1
                                processed_text = cleaner_text(line_content)
                                total.write(f'{index}\n{processed_text}\n')
                                unique_lines.add(line_content)  # Thêm vào set để tránh trùng lặp
                                audio_path = os.path.join(audio_folder, audios[i_au])
                                new_au_path = os.path.join(audio_total_folder, f'{index}.wav')
                                shutil.copy(audio_path, new_au_path)
                            i_au += 1
                except Exception as e:
                    print(f"Lỗi khi xử lý file {txt_f}: {e}")
    except Exception as e:
        print(f"Lỗi khi ghi file tổng {txt_total}: {e}")
# folder = "E:\\Python\\developping\\review comic\\test\\extract_audios"
# total_txt = os.path.join(folder, 'total.txt')
# audio_total_folder = os.path.join(folder, 'total_audios')   
# get_text_and_audio_in_folder(folder, total_txt, audio_total_folder)








#---------kiểm tra và xử lý file metadata để đúng chuẩn training XTTS-v2 ---------------------------
def add_voice_to_csv(input_file, voice_tag="vi_female"):
    import csv
    cur_dir = os.path.dirname(input_file)
    name = os.path.basename(input_file)
    output_dir = os.path.join(cur_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    wavs_dir = os.path.join(output_dir, 'wavs')
    os.makedirs(wavs_dir, exist_ok=True)
    output_file = os.path.join(output_dir, name)
    index = 0
    try:
        # Đọc nội dung file CSV
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            rows = [row for row in reader]
        
        # Thêm voice tag vào cuối mỗi dòng
        updated_rows = []
        for i, row in enumerate(rows):
            if i == 0:  # Header đã sửa ở bước trên
                row = ["audio_file", "text", "speaker_name"]
                updated_rows.append(row)
            else:
                text = row[1]
                if len(text) >= max_lenth_text or len(text) < 20:
                    continue
                else:
                    audio_path = os.path.join(cur_dir, row[0])
                    if not os.path.exists(audio_path):
                        continue
                    index += 1
                    new_path = os.path.join(wavs_dir, f'{index}.wav')
                    shutil.copy(audio_path, new_path)
                    row[0] = f'wavs/{index}.wav'
                updated_rows.append([row[0], row[1], voice_tag])
        
        # Ghi nội dung mới vào file đầu ra
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            writer.writerows(updated_rows)
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# # Sử dụng hàm
# input_csv = "E:\\Python\\developping\\review comic\\dataset\\vietnam\\train.csv"
# add_voice_to_csv(input_csv)












# #------------Thay đổi tốc độ audio hàng loạt---------
# def adjust_audio_speed(input_folder, output_folder, speed=0.97):
#     try:
#         # Tạo thư mục đầu ra nếu chưa tồn tại
#         os.makedirs(output_folder, exist_ok=True)
        
#         # Duyệt qua tất cả các file trong thư mục
#         for file_name in os.listdir(input_folder):
#             if file_name.endswith(".wav"):
#                 input_path = os.path.join(input_folder, file_name)
#                 output_path = os.path.join(output_folder, file_name)
                
#                 # Command để giảm tốc độ phát bằng ffmpeg
#                 ffmpeg_command = [
#                     'ffmpeg', '-i', input_path, '-filter:a', f"atempo={speed}",
#                     '-vn', output_path, '-y', '-loglevel', 'quiet'
#                 ]
                
#                 # Thực thi command
#                 subprocess.run(ffmpeg_command)
#                 print(f"Đã xử lý: {file_name}")
                
#     except Exception as e:
#         print(f"Có lỗi xảy ra: {e}")

# input_folder = "E:\\Python\\developping\\review comic\\dataset\\vietnam\\wavs"  # Thư mục chứa file .wav gốc
# output_folder = "E:\\Python\\developping\\review comic\\dataset\\vietnam\\out"  # Thư mục lưu file .wav đã giảm tốc độ
# os.makedirs(output_folder, exist_ok=True)
# adjust_audio_speed(input_folder, output_folder)