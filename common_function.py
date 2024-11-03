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
import pyttsx3
import winreg
from moviepy.video.fx.all import resize, crop, mirror_x, speedx
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, afx, vfx, CompositeVideoClip, ImageClip, ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip
from pydub import AudioSegment
import requests
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
import subprocess
import ffmpeg
import pickle
import uuid
import wmi
import platform
from tkinter import messagebox, filedialog
import customtkinter as ctk
import ctypes
import httplib2
from googleapiclient.discovery import build
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
import keyboard
import pyperclip

def get_disk_serial():
    c = wmi.WMI()
    for disk in c.Win32_DiskDrive():
        for partition in disk.associators("Win32_DiskDriveToDiskPartition"):
            for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
                if logical_disk.DeviceID == "C:" or logical_disk.DeviceID == "c:":
                    return disk.SerialNumber

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

current_dir = get_current_dir()
sys.path.append(current_dir)
secret_path = os.path.join(current_dir, 'oauth', 'secret.json')
chromedriver_path = os.path.join(current_dir, 'import\\chromedriver.exe')
config_path = os.path.join(current_dir, 'config.pkl')
download_info_path = os.path.join(current_dir, 'download_info.pkl')
youtube_config_path = os.path.join(current_dir, 'youtube_config.pkl')
icon_path = os.path.join(current_dir, 'import' , 'icon.png')
ico_path = os.path.join(current_dir, 'import' , 'icon.ico')
local_storage_path = os.path.join(current_dir, 'local_storage.pkl')
facebook_cookies_path = os.path.join(current_dir, 'facebook_cookies.pkl')
tiktok_cookies_path = os.path.join(current_dir, 'tiktok_cookies.pkl')
youtube_cookies_path = os.path.join(current_dir, 'youtube_cookies.pkl')
youtube_config_path = os.path.join(current_dir, 'youtube_config.pkl')
tiktok_config_path = os.path.join(current_dir, 'tiktok_config.pkl')
facebook_config_path = os.path.join(current_dir, 'facebook_config.pkl')
profile_folder = get_chrome_profile_folder()
pre_time_download = 0
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

def load_download_info():
    download_info = {
         "downloaded_urls": []
      }
    if os.path.exists(download_info_path):
        download_if = get_json_data(download_info_path)
    else:
        download_if = download_info
    save_to_pickle_file(download_if, download_info_path)
    return download_if

def save_download_info(data):
    save_to_pickle_file(data, download_info_path)

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
        # if show:
        #     driver.maximize_window()
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
    
def get_driver_with_profile(target_gmail, show=True):
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
    
    profile_name = get_profile_name_by_gmail()
    if profile_name:
        profile_path = os.path.join(profile_folder, profile_name)
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
        # driver.maximize_window()
        return driver
    else:
        print(f'Không tìm thấy profile cho tài khoản google {target_gmail}')
        print("--> Hãy dùng cookies để đăng nhập !")
        return None

def get_element_by_text(driver, text, tag_name='*', timeout=10):
    try:
        # Tìm element chứa text thuộc thẻ xác định
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.XPATH, f'//{tag_name}[contains(text(), "{text}")]'))
        )
        return element
    except:
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
       
def convert_date_format_yyyymmdd_to_mmddyyyy(date_str, vi_date=False):
    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        if vi_date:
            formatted_date = date_obj.strftime("%d/%m/%Y")
        else:
            formatted_date = date_obj.strftime("%m/%d/%Y")
        return formatted_date
    except:
        print(f"Định dạng ngày {date_str} không đúng yy-mm-dd")

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

def get_pushlish_time_hh_mm(publish_time="", facebook_time=False):
    try:
        hh, mm = map(int, publish_time.split(':'))
        if hh >= 0 and hh < 24 and mm >= 0 and mm < 60:
            if mm >= 45:
                mm = 45
            elif mm >= 30:
                mm = 30
            elif mm >= 15:
                mm = 15
            else:
                mm = 0
            if facebook_time:
                if hh > 12:
                    hh = hh - 12
                    get_time = f"{hh}:{mm}:PM"
                else:
                    get_time = f"{hh}:{mm}:AM"
            else:
                get_time = f"{hh}:{mm}"
            return get_time
        else:
            print("Định dạng giờ phải là hh:mm (ví dụ: 08:30,20:00)")
    except:
        print("Định dạng giờ phải là hh:mm (ví dụ: 08:30,20:00)")
    return None

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
 
def get_file_path(file_name=None):
    """Lấy đường dẫn tới tệp config trong cùng thư mục với file thực thi (exe)"""
    if getattr(sys, "frozen", False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(__file__))
    file_parent_path = application_path
    os.makedirs(file_parent_path, exist_ok=True)
    if file_name:
        return os.path.join(file_parent_path, file_name)
    else:
        return file_parent_path

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
    
def convert_sang_tieng_viet_khong_dau(input_str):
    convert_text = unidecode(input_str)
    return re.sub(r'[\\/*?:"<>|]', "", convert_text)

def remove_file(file_path):
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
    except:
        pass

def get_json_data(file_name=""):
    try:
        if file_name.endswith('.json'):
            if os.path.exists(file_name):
                with open(file_name, "r", encoding="utf-8") as file:
                    portalocker.lock(file, portalocker.LOCK_SH)
                    p = json.load(file)
                    portalocker.unlock(file)
        else:
            p = get_pickle_data(file_name)
    except:
        getlog()
        p = {}
    return p

def save_to_json_file(data, filename):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            portalocker.lock(f, portalocker.LOCK_EX)
            json.dump(data, f, indent=3)
            portalocker.unlock(f)
    except Exception as e:
        print(f"ERROR: can not save data to {filename}: {e}")
        getlog()

def get_pickle_data(file_path):
    if os.path.exists(file_path):
        try:
            with open(file_path, "rb") as file:
                portalocker.lock(file, portalocker.LOCK_SH)
                data = pickle.load(file)
                portalocker.unlock(file)
                return data
        except:
            getlog()
    return None

def save_to_pickle_file(data, file_path):
    try:
        with open(file_path, "wb") as file:
            portalocker.lock(file, portalocker.LOCK_EX)
            pickle.dump(data, file)
            portalocker.unlock(file)
    except:
        getlog()

def convert_json_to_pickle(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.json'):
            json_file_path = os.path.join(directory, filename)
            pkl_file_path = os.path.join(directory, filename[:-5] + '.pkl')  # Thay đổi đuôi file từ .json sang .pkl
            data = get_json_data(json_file_path)
            if data:
                save_to_pickle_file(data, pkl_file_path)
                remove_file(json_file_path)
convert_json_to_pickle(current_dir)

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

def get_json_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        data = None
        print("Failed to fetch the secret file.")
    return data

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

def check_folder(folder, is_create=False):
    try:
        if not os.path.exists(folder):
            if is_create:
                os.makedirs(folder, exist_ok=True)
            else:
                print(f'Thư mục {folder} không tồn tại.')
                return False
        return True
    except:
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
        download_info = get_json_data(download_info_path)
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
            if video_url not in download_info['downloaded_urls']:
                download_info['downloaded_urls'].append(video_url)
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

def download_video_by_url(url, download_folder=None, file_path=None, sleep_time=5, return_file_path=False):
    t = time()
    if not url:
        return False
    try:
        if file_path:
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': file_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
        else:
            if not download_folder:
                return False
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
        if t1 < sleep_time:
            sleep(sleep_time-t1)
        print(f'Tải thành công video: {file_path}')
        if return_file_path:
            return file_path
        else:
            return True
    except:
        return None
    
def get_info_by_url(url, download_folder=None, is_download=False):
    if not url:
        return None
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,
            'allsubtitles': True,
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'addmetadata': False,
            'nocheckcertificate': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_video = ydl.extract_info(url, download=False)
            if is_download:
                ydl.download(url)
                video_path = f"{info_video['title']}.mp4"
                video_path = os.path.join(download_folder, video_path)
                sleep(1)
                return video_path
            else:
                return info_video
    except:
        getlog()
        return None

def rename_files_by_index(folder_path, base_name="", extension=None, start_index=1):
    if not extension:
        extension = '.mp4'
    try:
        start_index = int(start_index)
    except:
        start_index = 1
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
            from imageio import imwrite
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

def check_folder(folder):
    if not folder:
        print("Hãy chọn thư mục lưu video.")
        return False
    if not os.path.isdir(folder):
        print(f"Thư mục {folder} không tồn tại.")
        return False
    return True

def get_random_audio_path(new_audio_folder):
    audios = get_file_in_folder_by_type(new_audio_folder, file_type=".mp3", is_sort=False)
    if not audios:
        return None
    return os.path.join(new_audio_folder, random.choice(audios))
    
def get_file_in_folder_by_type(folder, file_type=".mp4", is_sort=True, noti=True):
    try:
        if not os.path.exists(folder):
            if noti:
                print(f"Thư mục {folder} không tồn tại !!!")
            return None
        list_files = os.listdir(folder)
        list_files = [k for k in list_files if k.endswith(file_type)]      
        if len(list_files) == 0:
            if noti:
                print(f"Không tìm thấy file {file_type} trong thư mục {folder} !!!")
            return None
        if is_sort:
            list_files = natsorted(list_files)
        return list_files
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

def choose_file():
    file_path = filedialog.askopenfilename( title="Select a file", filetypes=(("All files", "*.*"),) )
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

def run_command_ffmpeg(command):
    try:
        subprocess.run(command, check=True, text=True, encoding='utf-8', errors='ignore')
        return True
    except:
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
            if not run_command_with_progress(command, duration):
                cut_video_by_moviepy(input_video_path, segment_file_path, start, end)

            if get_audio:
                download_folder = os.path.join(output_folder, "extracted_audio")
                os.makedirs(download_folder, exist_ok=True)
                extract_audio_ffmpeg(video_path=segment_file_path, download_folder=download_folder)
            if is_connect:
                combine_videos.append(segment_file_path)


        if is_connect != 'no' and len(combine_videos) > 1:
            try:
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
            except:
                merge_videos_use_moviepy(videos_list=combine_videos, file_path=output_file_path, is_delete=is_delete, fps=int(video_info['fps']))
        cat = time() - ti
        print(f'---> Thời gian cắt video {input_video_path} là {int(cat)}s')
        return True, None
    except:
        return cut_video_by_timeline_use_moviepy(input_video_path, segments, is_connect, is_delete=is_delete)

        
def cut_video_by_moviepy(input_video_path, output_file_path, start, end):
    try:
        clip = VideoFileClip(input_video_path)
        sub_clip = clip.subclip(start, end)
        sub_clip.write_videofile(output_file_path, codec='libx264')
        sub_clip.close()
        clip.close()
    except:
        print(f"!!! Cắt video {input_video_path} thất bại !!!")

def cut_video_by_timeline_use_moviepy(input_video_path, segments, is_connect, is_delete=False):
    try:
        output_folder, file_name = get_output_folder(input_video_path, output_folder_name='cut_video')
        clips = []
        i = 0
        video = VideoFileClip(input_video_path)
        duration = video.duration
        try:
            segments = segments.split(',')
        except:
            print("Định dạng thời gian cắt là start-end với start,end là hh:mm:ss hoặc mm:ss hoặc ss")
            return None, "Có lỗi khi cắt video"
        for segment in segments:
            segment = segment.strip()
            start, end = segment.split('-')
            list_start = start.split(':')
            cnt = len(list_start)
            if cnt == 3:
                start = int(list_start[0]) * 3600 + int(list_start[1]) * 60 + int(list_start[2])
            elif cnt == 2:
                start = int(list_start[0]) * 60 + int(list_start[1])
            elif cnt == 1:
                start = int(list_start[0])
            else:
                message = "Định dạng thời gian cắt ở đầu video không đúng. Định dạng đúng là hh:mm:ss-hh:mm:ss hoặc mm:ss-mm:ss hoặc ss-ss"
                return False, message

            # Chuyển đổi thời gian kết thúc
            list_end = end.split(':')
            cnt = len(list_end)
            if cnt == 3:
                end = int(list_end[0]) * 3600 + int(list_end[1]) * 60 + int(list_end[2])
            elif cnt == 2:
                end = int(list_end[0]) * 60 + int(list_end[1])
            elif cnt == 1:
                end = int(list_end[0])
            else:
                message = "Định dạng thời gian cắt ở đầu video không đúng. Định dạng đúng là hh:mm:ss-hh:mm:ss hoặc mm:ss-mm:ss hoặc ss-ss"
                return False, message
            if end > duration:
                end = duration
            clip = video.subclip(start, end)
            if is_connect:
                clips.append(clip)
                sleep(1)
            else:
                i += 1
                file_path = f"{output_folder}\\{file_name}"
                clip.write_videofile(file_path, codec='libx264')
                clip.close()
                sleep(1)
        if is_connect and len(clips) > 0:
            final_clip = concatenate_videoclips(clips, method="compose")
            file_path = f"{output_folder}\\{file_name.split('.mp4')[0]}_1.mp4"
            final_clip.write_videofile(file_path, codec='libx264')
            final_clip.close()
            for clip in clips:
                clip.close()
        video.close()
        return True, None
    except Exception as e:
        if video:
            video.close()
        getlog()
        return False, "Có lỗi trong quá trình cắt video."


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
        merge_videos_use_moviepy(videos_folder, file_path, is_delete, fps=max_fps)
        noi = time() - ti
        print(f'Tổng thời gian nối là {noi}')

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

def merge_videos_use_moviepy(videos_folder, file_path=None, is_delete=False, is_move=True, videos_list=None, fps=30):
    try:
        if videos_list:
            edit_videos = videos_list
        else:
            edit_videos = get_file_in_folder_by_type(videos_folder)
            if not edit_videos:
                return
            if len(edit_videos) <= 1:
                warning_message("Phải có ít nhất 2 video trong videos folder")
                return
        output_folder = f'{videos_folder}\\merge_videos'
        os.makedirs(output_folder, exist_ok=True)
        clips = []
        remove_videos = []
        for i, video_file in enumerate(edit_videos):
            video_path = f'{videos_folder}\\{video_file}'
            remove_videos.append(video_path)
            clip = VideoFileClip(video_path)
            clips.append(clip)
        if len(clips) > 0:
            final_clip = concatenate_videoclips(clips, method="compose")
            if not file_path:
                file_path = f"{output_folder}\\combine_video.mp4"
            final_clip.write_videofile(file_path, codec='libx264', fps=fps)
            final_clip.close()
            for clip in clips:
                clip.close()
            for clip in clips:
                clip.close()
        for video_path in remove_videos:
            remove_or_move_file(video_path, is_delete=is_delete, is_move=is_move)
    except:
        print(f"Có lỗi khi nối video !!!")


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


def get_index_of_temp_file (input_path):
    return int(input_path.split('temp')[-1].split('.mp4')[0])
    
def strip_first_and_end_video(clip, first_cut, end_cut):
    try:
        first_cut = int(first_cut)
    except:
        first_cut = 0
    try:
        end_cut = int(end_cut)
    except:
        end_cut = 0

    if first_cut < 0:
        first_cut = 0
    if end_cut < 0 or end_cut >= clip.duration:
        warning_message("Thời gian cắt video không hợp lệ.")
        return None
    return clip.subclip(first_cut, clip.duration - end_cut)

def zoom_and_crop(clip, zoom_factor, vertical_position='center', horizontal_position='center'):
    resized_clip = clip.resize(zoom_factor)
    new_width, new_height = resized_clip.size
    y1, y2 = 0, new_height
    x1, x2 = 0, new_width
    if vertical_position == 'center':
        y1 = (new_height - clip.h) // 2
        y2 = y1 + clip.h
    elif vertical_position == 'top':
        y1 = 0
        y2 = clip.h
    elif vertical_position == 'bottom':
        y1 = new_height - clip.h
        y2 = new_height
    if horizontal_position == 'center':
        x1 = (new_width - clip.w) // 2
        x2 = x1 + clip.w
    elif horizontal_position == 'left':
        x1 = 0
        x2 = clip.w
    elif horizontal_position == 'right':
        x1 = new_width - clip.w
        x2 = new_width
    cropped_clip = resized_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    return cropped_clip

def apply_zoom(clip, zoom_factor, vertical_position, horizontal_position):
    if not zoom_factor:
        return clip
    zoom_factor = float(zoom_factor)
    if zoom_factor < 0 or zoom_factor > 3:
        warning_message('Tỷ lệ zoom không hợp lệ.')
        return None
    return zoom_and_crop(clip, zoom_factor, vertical_position, horizontal_position)

def zoom_video_random_intervals(clip, max_zoom_size, vertical_position='center', horizontal_position='center', is_random_zoom="3-5"):
    try:
        min_time_to_change_zoom, max_time_to_change_zoom = is_random_zoom.split('-')
        min_time_to_change_zoom = int(float(min_time_to_change_zoom.strip()))
        max_time_to_change_zoom = int(float(max_time_to_change_zoom.strip()))
    except:
        print("Thời gian zoom ngẫu nhiên không phù hợp !!!")
        return None
    try:
        max_zoom_size = float(max_zoom_size)
    except:
        print("Tỷ lệ zoom không đúng định dạng số !!!")
        return None
    if max_time_to_change_zoom > clip.duration:
        max_time_to_change_zoom = clip.duration
    start_times = []
    current_time = 0
    while current_time < clip.duration:
        start_times.append(current_time)
        current_time += random.uniform(min_time_to_change_zoom, max_time_to_change_zoom)
    if start_times[-1] < clip.duration:
        start_times.append(clip.duration)
    zoom_factors = []
    last_zoom_factor = None
    for _ in range(len(start_times) - 1):
        while True:
            new_zoom = round(random.uniform(1.01, max_zoom_size), 2)
            if new_zoom != last_zoom_factor:
                zoom_factors.append(new_zoom)
                last_zoom_factor = new_zoom
                break
    zoomed_clips = []
    try:
        for i, start_time in enumerate(start_times[:-1]):
            end_time = start_times[i + 1]
            sub_clip = clip.subclip(start_time, end_time)
            zoomed_clip = apply_zoom(sub_clip, zoom_factors[i], vertical_position, horizontal_position)
            zoomed_clips.append(zoomed_clip)
    
        final_zoom_clip = concatenate_videoclips(zoomed_clips, method="compose")
        return final_zoom_clip
    except Exception as e:
        getlog()
        return None

def speed_up_clip(clip, speed):
    speed = float(speed)
    if speed < 0 or speed > 3:
        warning_message('invalid speed up')
        return None
    sped_up_clip = clip.fx(speedx, factor=speed)
    return sped_up_clip

def get_clip_ratio(clip, tolerance=0.02):  #Kiểm tra video thuộc tỷ lệ 16:9 hay 9:16
    clip_width, clip_height = clip.size
    ratio = clip_width / clip_height
    if abs(ratio - (16/9)) < tolerance:  # Kiểm tra xem tỷ lệ gần bằng 16:9
        return (16,9)
    elif abs(ratio - (9/16)) < tolerance:  # Kiểm tra xem tỷ lệ gần bằng 9:16
        return (9,16)
    else:
        return None
    
def resize_clip(clip, re_size=0.999):
    try:
        target_ratio = get_clip_ratio(clip)
        clip_width, clip_height = clip.size
        if target_ratio:
            target_width, target_height = target_ratio
            if clip_width / clip_height != target_width / target_height:
                clip_width = clip_height * target_width / target_height
            
            width = int(clip_width * re_size)
            height = int(clip_height * re_size)
            try:
                clip = resize(clip, newsize=(width, height))
            except:
                ratio = clip_width/clip_height
                new_height = 720/ratio
                clip = resize(clip, newsize=(720, new_height))
        else:
            ratio = clip_width/clip_height
            new_height = 720/ratio
            clip = resize(clip, newsize=(720, new_height))
        return clip
    except:
        getlog()
        return None

def flip_clip(clip):
    # Áp dụng hiệu ứng đối xứng (flip) theo chiều ngang
    flipped_clip = mirror_x(clip)
    return flipped_clip

def increase_video_quality(input_path, output_path): #Tăng chất lượng video
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'unsharp=luma_msize_x=7:luma_msize_y=7:luma_amount=1.5,'
                    'eq=contrast=1.2:saturation=1.2',  # Tăng cường độ sắc nét và điều chỉnh độ tương phản
            '-c:a', 'copy', '-y',  # Sao chép âm thanh gốc
            output_path 
        ]
        subprocess.run(ffmpeg_command, check=True)
        print(f"Xử lý tăng độ phân giải thành công: \n{output_path}")
        return True
    except:
        print(f"Có lỗi trong quá trình tăng chất lượng video: \n{input_path}")
        return False
    
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

def add_image_watermark_into_video(clip, top_bot_overlay_height='2,2', left_right_overlay_width='2,2', watermark=None, vertical_watermark_position=0, horizontal_watermark_position=0, watermark_scale='1,1'):
    w, h = clip.size
    try:
        if not top_bot_overlay_height:
            top_bot_overlay_height = '2,2'
        top_overlay_height, bot_overlay_height = top_bot_overlay_height.split(',')
        if not top_overlay_height or int(top_overlay_height) < 0 or int(top_overlay_height) >= h:
            top_overlay_height = 2
        else:
            top_overlay_height = int(top_overlay_height)
        if not bot_overlay_height or int(bot_overlay_height) < 0 or int(bot_overlay_height) >= (h-top_overlay_height):
            bot_overlay_height = 2
        else:
            bot_overlay_height = int(bot_overlay_height)
    except:
        print("kích thước lớp phủ trên và dưới đã nhập không hợp lệ, lấy kích thước lớp phủ mặc định là 2")
        bot_overlay_height = top_overlay_height = 2

    try:
        if not left_right_overlay_width:
            left_right_overlay_width = '2,2'
        left_overlay_width, right_overlay_width = left_right_overlay_width.split(',')
        if not left_overlay_width or int(left_overlay_width) < 0 or int(left_overlay_width) >= w:
            left_overlay_width = 2
        else:
            left_overlay_width = int(left_overlay_width)
        if not right_overlay_width or int(right_overlay_width) < 0 or int(right_overlay_width) >= (w - left_overlay_width):
            right_overlay_width = 2
        else:
            right_overlay_width = int(right_overlay_width)
    except:
        print("kích thước lớp phủ trái và phải đã nhập không hợp lệ, lấy kích thước lớp phủ mặc định là 2")
        left_overlay_width = right_overlay_width = 2

    try:
        width, height = clip.size
        top_image = ColorClip(size=(width, top_overlay_height), color=(0, 0, 0)).set_position(('center', 0)).set_duration(clip.duration)
        bottom_image = ColorClip(size=(width, bot_overlay_height), color=(0, 0, 0)).set_position(('center', height - bot_overlay_height)).set_duration(clip.duration)
        left_image = ColorClip(size=(left_overlay_width, height), color=(0, 0, 0)).set_position((0, 'center')).set_duration(clip.duration)
        right_image = ColorClip(size=(right_overlay_width, height), color=(0, 0, 0)).set_position((width - right_overlay_width, 'center')).set_duration(clip.duration)

        if watermark:
            try:
                scale_w, scale_h = [float(s) for s in watermark_scale.split(',')]
            except:
                scale_w = scale_h = 1.0
            watermark_image = ImageClip(watermark).set_duration(clip.duration)
            watermark_width, watermark_height = watermark_image.size
            scaled_width = int(watermark_width * scale_w)
            scaled_height = int(watermark_height * scale_h)

            watermark_image = watermark_image.resize((scaled_width, scaled_height))
            if horizontal_watermark_position == 'center':
                horizontal_watermark_position = (width - scaled_width) / 2
            elif horizontal_watermark_position == 'left':
                horizontal_watermark_position = 0
            elif horizontal_watermark_position == 'right':
                horizontal_watermark_position = width - scaled_width
            else:
                try:
                    horizontal_watermark_position = int(float(horizontal_watermark_position) * width / 100)
                except ValueError:
                    horizontal_watermark_position = (width - scaled_width) / 2

            if vertical_watermark_position == 'center':
                vertical_watermark_position = (height - scaled_height) / 2
            elif vertical_watermark_position == 'top':
                vertical_watermark_position = 0
            elif vertical_watermark_position == 'bottom':
                vertical_watermark_position = height - scaled_height
            else:
                try:
                    vertical_watermark_position = int(float(vertical_watermark_position) * height / 100)
                except ValueError:
                    vertical_watermark_position = (height - scaled_height) / 2

            watermark_image = watermark_image.set_position((horizontal_watermark_position, vertical_watermark_position))
            final_clip = CompositeVideoClip([clip, top_image, bottom_image, left_image, right_image, watermark_image])
        else:
            final_clip = CompositeVideoClip([clip, top_image, bottom_image, left_image, right_image])
        return final_clip

    except Exception as e:
        print(f"Lỗi khi thêm watermark: {e}")
        return None

def convert_video_169_to_916(input_video_path, zoom_size=None, resolution="1080x1920", is_delete=False, is_move=True):
    try:
        output_folder, file_name = get_output_folder(input_video_path, output_folder_name='converted_videos')
        output_file_path = os.path.join(output_folder, file_name)
        video = VideoFileClip(input_video_path)
        width, height = video.size
        if not zoom_size:
            zoom_size = 0.9
        else:
            zoom_size = float(zoom_size)
        target_width, target_height = list(map(int, resolution.split('x')))
        video_display_height = target_height * zoom_size
        zoom = video_display_height / height
        zoomed_video = video.resize(newsize=(int(width * zoom), int(height * zoom)))
        zoomed_width, zoomed_height = zoomed_video.size
        background = ColorClip(size=(target_width, target_height), color=(0, 0, 0), duration=video.duration)
        x_pos = (target_width - zoomed_width) / 2
        y_pos = (target_height - zoomed_height) / 2
        final_video = CompositeVideoClip([background, zoomed_video.set_position((x_pos, y_pos))], size=(target_width, target_height))
        final_video.write_videofile(output_file_path, codec='libx264', audio_codec='aac')
        final_video.close()
        zoomed_video.close()
        video.close()
        remove_or_move_file(input_video_path, is_delete=is_delete, is_move=is_move)
        return True
    except Exception as e:
        getlog()
        return False
    
def convert_video_916_to_169(input_video_path, resolution="1920x1080", is_delete=False, is_move=True):
    try:
        if not resolution:
            resolution = '1920x1080'
        resolution = resolution.split('x')
        output_folder, file_name = get_output_folder(input_video_path, output_folder_name='converted_videos')
        output_file_path = os.path.join(output_folder, file_name)
        video = VideoFileClip(input_video_path)
        input_width, input_height = video.size
        new_height = input_width * 9 / 16
        if new_height <= input_height:
            y1 = (input_height - new_height) / 2
            y2 = y1 + new_height
            cropped_video = video.crop(x1=0, x2=input_width, y1=y1, y2=y2)
        else:
            new_width = input_height * 16 / 9
            black_bar = ColorClip(size=(int(new_width), input_height), color=(0, 0, 0))
            video = video.set_position(("center", "center"))
            cropped_video = CompositeVideoClip([black_bar, video]).set_duration(video.duration)
        resized_video = cropped_video.resize(newsize=(resolution[0], resolution[1]))
        resized_video.write_videofile(output_file_path, codec='libx264', audio_codec='aac')
        resized_video.close()
        video.close()
        sleep(1)
        remove_or_move_file(input_video_path, is_delete=is_delete, is_move=is_move)
        return True
    except:
        getlog()
        return False

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

def remove_audio_from_clip(clip):
    return clip.without_audio()

def set_audio_for_clip(clip, background_music, background_music_volume="10"):
    try:
        volume = float(background_music_volume)/100
        background_music = AudioFileClip(background_music)
        background_music = background_music.volumex(volume)
        background_music = afx.audio_loop(background_music, duration=clip.duration)
        current_audio = clip.audio
        if current_audio is None:
            clip = clip.set_audio(background_music)
        else:
            combined_audio = CompositeAudioClip([current_audio, background_music])
            clip = clip.set_audio(combined_audio)
        return clip
    except:
        print("Có lỗi ghi ghép audio vào video")

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
            sample_rate = 44100 if original_sample_rate == 48000 else 48000
            original_bitrate = streams_info.get("bit_rate", "192k")
            bitrate = "256k" if original_bitrate == "192000" else "192k"
            channels = 1 if streams_info.get("channels") == 2 else 2
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
            ffmpeg_cmd_adjust += ["-c:a", "libmp3lame", output_audio_path]
            if run_command_ffmpeg(ffmpeg_cmd_adjust):
                print(f"Chỉnh sửa thông tin audio thành công: {output_audio_path}")
            else:
                print(f"Lỗi khi thay đổi thông tin audio !!!")
            os.remove(temp_audio_path)
    except:
        print("Có lỗi trong quá trình chỉnh sửa audio !!!")

def extract_audio_ffmpeg(audio_path=None, video_path=None, video_url=None, video_folder=None, segments=None, download_folder=None, fast=True):
    try:
        if not segments:
            segments = "0-999999999999"
        try:
            segments = segments.split(',')
        except:
            print("Định dạng thời gian cắt là start-end với start,end là hh:mm:ss hoặc mm:ss hoặc ss")
            return
        cnt_cut = 0
        for segment in segments:
            cnt_cut += 1
            segment = segment.strip()
            start, end = segment.split('-')
            start = convert_time_to_seconds(start)
            if start is None:
                return
            end = convert_time_to_seconds(end)
            if end is None:
                return
            target_paths = []
            if video_url:
                video_path = download_video_by_url(video_url, download_folder, return_file_path=True)
                target_path = video_path
            elif audio_path:
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

            for target_path in target_paths:
                video_clip = None
                if '.mp3' in target_path:
                    audio_clip = AudioFileClip(target_path)
                else:
                    video_clip = VideoFileClip(target_path)
                    audio_clip = video_clip.audio
                duration = audio_clip.duration
                if end > duration:
                    end = duration
                file_name = os.path.basename(target_path)
                if len(segments) == 1:
                    audio_name = file_name.split('.')[0]
                else:
                    audio_name = f"{file_name.split('.')[0]}_{cnt_cut}"
                output_audio_path = f'{download_folder}/{audio_name}.mp3'
                if os.path.exists(output_audio_path):
                    output_audio_path = f'{download_folder}/{audio_name}_{cnt_cut}.mp3'
                print(f"  --> Bắt đầu trích xuất audio từ file {target_path}")
                try:
                    if fast:
                        ffmpeg_cmd = [
                            "ffmpeg", "-y",
                            '-progress', 'pipe:1',
                            "-i", target_path, "-ss", str(start), "-to", str(end),
                            "-filter:a", f"atempo=1",
                            "-loglevel", "quiet",
                            output_audio_path
                        ]
                        run_command_with_progress(ffmpeg_cmd, duration)
                    else:
                        if start > 0 or end != duration:
                            audio_clip = audio_clip.subclip(start, end)
                        audio_clip.write_audiofile(output_audio_path, codec='mp3')
                except:
                    output_audio_path = f'{download_folder}/audio.mp3'
                    audio_clip.write_audiofile(output_audio_path, codec='mp3')
                    
                if audio_clip:
                    audio_clip.close()
                if video_clip:
                    video_clip.close()
                print(f"  --> Trích xuất thành công audio từ video {target_path}")
        if video_url:
            remove_file(video_path)
    except:
        print("Có lỗi trong quá trình trích xuất audio !!!")






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
            "auto_upload_youtube": False,
            "auto_upload_facebook": False,
            "auto_upload_tiktok": False,
            "time_check_auto_upload": "0",
            "time_check_status_video": "0",

            "current_youtube_account": "",
            "current_tiktok_account": "",
            "current_facebook_account": "",
            "current_channel": "",
            "current_page": "",
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
            "pitch_factor": "1.05",
            "cut_silence": False,
            "aecho": "100",

            "audio_edit_path": "", 
            "speed_talk": "1", 
            "convert_multiple_record": False, 
            "video_get_audio_path": "", 
            "video_get_audio_url": "", 

            "supported_languages": {
                "en-us": "English (United States)",
                "vi": "Vietnamese"
            }
        }
        save_to_pickle_file(config, config_path)
    return config

youtube_category = {
    "Film & Animation": "1",
    "Autos & Vehicles": "2",
    "Music": "10",
    "Pets & Animals": "15",
    "Sports": "17",
    "Short Movies": "18",
    "Travel & Events": "19",
    "Gaming": "20",
    "Videoblogging": "21",
    "People & Blogs": "22",
    "Comedy": "23",
    "Entertainment": "24",
    "News & Politics": "25",
    "Howto & Style": "26",
    "Education": "27",
    "Science & Technology": "28",
    "Nonprofits & Activism": "29",
    "Movies": "30",
    "Anime/Animation": "31",
    "Action/Adventure": "32",
    "Classics": "33",
    "Documentary": "35",
    "Drama": "36",
    "Family": "37",
    "Foreign": "38",
    "Horror": "39",
    "Sci-Fi/Fantasy": "40",
    "Thriller": "41",
    "Shorts": "42",
    "Shows": "43",
    "Trailers": "44"
}

youtube_config = {
   "registered_account":['dxthien2@gmail.com'],
   "current_youtube_account": "",
   "current_channel": "",
   "download_folder": "",
   "download_url": "",
   "filter_by_like": "0",
   "filter_by_views": "0",
   "use_cookies": True,
   "show_browser": False,
   "template": {}
   }

tiktok_config = {
   "registered_account": [],
   "output_folder": "",
   "show_browser": True,
   "download_url": "",
   "download_folder": "",
   "is_move": False,
   "is_delete_after_upload": False,
   "filter_by_like": "0",
   "filter_by_views": "0",
   "template": {}
}

facebook_config = {
   "show_browser": False,
   "download_url": "",
   "download_folder": "",
   "filter_by_views": "0",
   "filter_by_like": "0",
   "registered_account": [],
   "template": {}
}


def load_youtube_config():
    if os.path.exists(youtube_config_path):
        config = get_json_data(youtube_config_path)
    else:
        config = youtube_config
    save_to_pickle_file(config, youtube_config_path)
    return config

def load_tiktok_config():
    if os.path.exists(tiktok_config_path):
        config = get_json_data(tiktok_config_path)
    else:
        config = tiktok_config
    save_to_pickle_file(config, tiktok_config_path)
    return config

def load_facebook_config():
    if os.path.exists(facebook_config_path):
        config = get_json_data(facebook_config_path)
    else:
        config = facebook_config
    save_to_pickle_file(config, facebook_config_path)
    return config
