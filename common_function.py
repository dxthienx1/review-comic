import json
import sys
import os
import re
import shutil
import random
from natsort import natsorted
from datetime import datetime, timedelta, timezone, time as dtime
from time import sleep, time
from tzlocal import get_localzone
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import pyttsx3
import winreg
from moviepy.video.fx.all import resize, crop, mirror_x
from moviepy.video.fx.speedx import speedx
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, afx, vfx, CompositeVideoClip, ImageClip, ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip
from pytube import YouTube
from translate import Translator
import requests
from pydub import AudioSegment
from unidecode import unidecode
import yt_dlp
import portalocker
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
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

profile_folder = get_chrome_profile_folder()
current_dir = get_current_dir()
sys.path.append(current_dir)
config_path = os.path.join(current_dir, 'config.json')
chromedriver_path = os.path.join(current_dir, 'import\\chromedriver.exe')
secret_path = os.path.join(current_dir, 'oauth', 'secret.json')
download_info_path = os.path.join(current_dir, 'download_info.json')
youtube_config_path = os.path.join(current_dir, 'youtube_config.json')
# download_folder = f'{current_dir}\\download_folder'
# os.makedirs(download_folder, exist_ok=True)
test_folder = f'{current_dir}\\test'
local_storage_path = os.path.join(current_dir, 'local_storage.json')
facebook_cookies_path = os.path.join(current_dir, 'facebook_cookies.json')
tiktok_cookies_path = os.path.join(current_dir, 'tiktok_cookies.pkl')
youtube_cookies_path = os.path.join(current_dir, 'youtube_cookies.pkl')
youtube_config_path = os.path.join(current_dir, 'youtube_config.json')
tiktok_config_path = os.path.join(current_dir, 'tiktok_config.json')
facebook_config_path = os.path.join(current_dir, 'facebook_config.json')
pre_time_download = 0

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
    save_to_json_file(download_if, download_info_path)
    return download_if

def save_download_info(data):
    save_to_json_file(data, download_info_path)

def get_driver(show=True):
    try:
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        if not show:
            options.add_argument('--headless')  # Chạy ở chế độ không giao diện
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36")
        options.add_argument("--log-level=3")  # Suppress most logs
        options.add_argument("--disable-logging")  # Disable logging
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)
        driver = webdriver.Chrome(service=service, options=options)
        if show:
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
    
def get_driver_with_profile(target_gmail, show=True):
    try:
        os.system("taskkill /F /IM chrome.exe /T")
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
        print(profile_path)
        options = webdriver.ChromeOptions()
        options.add_argument(f"user-data-dir={profile_folder}")
        options.add_argument(f"profile-directory={profile_name}")
        if not show:
            options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        driver = webdriver.Chrome(options=options)
        return driver
    else:
        print(f'Không tìm thấy profile cho tài khoản google {target_gmail}')
        print("--> Hãy dùng cookies để đăng nhập !")
        return None

def get_element_by_xpath(driver, xpath, key=None, index=0, multiple_ele=False):
    kq = []
    cnt=0
    while(len(kq)==0):
        cnt+=1
        elements = driver.find_elements(By.XPATH, xpath)
        if multiple_ele:
            return elements
        if key:
            key = key.lower()
            for ele in elements:
                if key in ele.accessible_name.lower() or key in ele.text.lower() or key in ele.tag_name.lower() or key in ele.aria_role.lower():
                    kq.append(ele)
                    break
            if len(kq) > 0:
                return kq[0]
            else:
                return None
        else:
            if len(elements) > 0:
                ele = elements[index]
                return ele
        sleep(1)
        cnt += 1
        if cnt > 3:
            # print(f"Không tìm thấy: {key}: {xpath}")
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
    # Kiểm tra định dạng ngày bằng biểu thức chính quy
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not date_pattern.match(date_str):
        return False, "Định dạng ngày phải là yyyy-mm-dd"
    if daydelta:
        try:
            # Chuyển đổi từ chuỗi ngày sang đối tượng datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Định dạng ngày phải là yyyy-mm-dd"

        # Lấy ngày hiện tại
        current_date = datetime.now()
        
        # Kiểm tra khoảng cách giữa ngày nhập vào và ngày hiện tại
        if date_obj > current_date + timedelta(days=daydelta-1):
            return False, f"Date is more than {daydelta} days in the future"
    return True, "Valid date"

def convert_time_to_UTC(year, month, day, hour, minute, second=0, iso8601=True):
    local_tz = get_localzone()
    local_time = datetime(year, month, day, hour, minute, second, tzinfo=local_tz)
    utc_time = local_time.astimezone(timezone.utc)
    # Định dạng thời gian theo ISO 8601
    if iso8601:
        iso8601_time = utc_time.strftime('%Y-%m-%dT%H:%M:%SZ')
        return iso8601_time
    return utc_time

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

def convert_date_yyyymmdd_to_youtybe_date(date_yyyymmdd, is_english=True):
    try:
        year, month, day = date_yyyymmdd.split('-')
        month = int(month.strip())
        if is_english:
            convert_month = {
                '1':"Jan",
                '2':"Feb",
                '3':"Mar",
                '4':"Apr",
                '5':"May",
                '6':"Jun",
                '7':"Jul",
                '8':"Aug",
                '9':"Sep",
                '10':"Oct",
                '11':"Nov",
                '12':"Dec",
            }
            date = f'{convert_month[str(month)]} {date}, {year}'
        else:
            date = f'{day.strip()} thg {month}, {year.strip()}'
        return date
    except:
        return None

def add_days(datetime, days):
    return datetime + timedelta(days=days)
    
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

def translate_now(translator, original):
    if original:
        original = original.strip().lower()
        if "_" in original:
            original = original.replace("_", " ")
        if "-" in original:
            original = original.replace("-", " ")
        try:
            translation = translator.translate(original)
            translation = re.sub(r"\(.*?\)", "", translation)
            return translation
        except Exception as e:
            print(f"An error occurred during translation: {e}")
            return None
    else:
        return None
    
def convert_sang_tieng_viet_khong_dau(input_str):
    convert_text = unidecode(input_str)
    return re.sub(r'[\\/*?:"<>|]', "", convert_text)

def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)



def get_json_data(file_name):
    if os.path.exists(file_name):
        try:
            with open(file_name, "r", encoding="utf-8") as file:
                portalocker.lock(file, portalocker.LOCK_SH)  # Khóa chia sẻ (shared lock) để đọc
                p = json.load(file)
                portalocker.unlock(file)  # Giải phóng khóa
        except:
            getlog()
            p = {}
    else:
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

def get_audio_clip_from_video(video_path=None, is_get_video=False):
    try:
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        if is_get_video:
            output_folder, output_video_path, file_name = get_output_folder(video_path, output_folder_name='output_audio')
            video_clip_without_audio = video_clip.without_audio()
            video_clip_without_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
            video_clip_without_audio.close()
        video_clip.close()
        return audio_clip
    except:
        getlog()
        return None

def get_output_folder(input_video_path, output_folder_name='output_folder'):
    folder_input = os.path.dirname(input_video_path)
    file_name = os.path.basename(input_video_path)
    output_folder = f'{folder_input}/{output_folder_name}'
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = f'{output_folder}/{file_name}'
    return output_folder, output_file_path, file_name

def download_video_by_url(url, download_folder=None, file_path=None, sleep_time=3, return_file_path=False):
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
        sleep(5)
    if get_file_path:
        return None
    else:
        return False
    
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

def download_video_no_watermark_from_tiktok(video_url, download_folder=None):
        url = "https://tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com/index"
        headers = {
            "x-rapidapi-key": "e1456d8b1dmsh0410da9e2ed2388p1991fdjsnf2f2ca37b287",
            "x-rapidapi-host": "tiktok-downloader-download-tiktok-videos-without-watermark.p.rapidapi.com"
        }
        querystring = {"url":video_url}
        try:
            response = requests.get(url, headers=headers, params=querystring)
            result = response.json()
            video_urls = result.get('video', [])
            if len(video_urls) > 0:
                new_video_url = video_urls[0]
            description = result.get('description', [])
            if description:
                video_name = description[0].split('#')[0].strip()
            video_path = f'{download_folder}\\{video_name}.mp4'
            if new_video_url:
                r = requests.get(new_video_url)
                with open(video_path, 'wb') as f:
                    f.write(r.content)
            return True
        except:
            getlog()
            return False

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

def remove_or_move_after_upload(input_video_path, is_delete=False, is_move=True, finish_folder_name='upload_finished'):
    try:
        if is_delete:
            os.remove(input_video_path)
            print(f'Đã xóa file {input_video_path}')
        elif is_move:
            videos_folder = os.path.dirname(input_video_path)
            finish_folder = os.path.join(videos_folder, f'{finish_folder_name}')
            os.makedirs(finish_folder, exist_ok=True)
            base_name = os.path.basename(input_video_path)
            move_file_path = os.path.join(finish_folder, base_name)
            shutil.move(input_video_path, move_file_path)
            print(f'Đã di chuyển file {input_video_path} đến thư mục {finish_folder}')
    except:
        print(f"Không thể xóa hoặc di chuyển file {input_video_path}")
        
def remove_or_move_file(input_video_path, is_delete=False, is_move=True):
    try:
        if is_delete:
            os.remove(input_video_path)
            print(f'Đã xóa file {input_video_path}')
        elif is_move:
            output_folder, output_file_path, file_name = get_output_folder(input_video_path)
            finish_folder = os.path.join(output_folder, 'Finished Edit')
            os.makedirs(finish_folder, exist_ok=True)
            move_file_path = os.path.join(finish_folder, file_name)
            shutil.move(input_video_path, move_file_path)
            print(f'Đã di chuyển file đến {move_file_path}')
    except:
        if is_delete:
            print(f"Xóa không thành công file: {input_video_path}")
        else:
            print(f"Di chuyển không thành công file: {input_video_path}")

def check_datetime_input(date_str, time_str):
    input_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    current_time_plus_30 = datetime.now() + timedelta(minutes=30)
    if input_time <= current_time_plus_30:
        print(f'Thời gian muốn đăng vào là {time_str} ngày {date_str} không hợp lệ --> Phải đăng sau 30 phút so với thời điểm hiện tại. Lưu ý phút hợp lệ là 00, 15, 30, 45')
        return False
    return True

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
            sleep(0.2)

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
    output_folder = os.path.join(videos_folder, 'images')
    os.makedirs(output_folder, exist_ok=True)
    cnt = 0
    for i, video_file in enumerate(videos):
        video_path = os.path.join(videos_folder, video_file)
        video_name = os.path.splitext(video_file)[0] #lấy tên
        image_path = os.path.join(output_folder, f'{video_name}.png')
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
        cnt += 1
    if cnt > 0:
        print(f'Đã trích xuất thành công {cnt} ảnh.')
        print(f'Thư mục chứa ảnh là {output_folder}.')

# def check_time_for_auto_upload(time_check_string):
#     try:
#         target_hour, target_minute = time_check_string.split(':')
#         now = datetime.now()
#         target_time = now.replace(hour=int(target_hour.strip()), minute=int(target_minute.strip()), second=0, microsecond=0)
        
#         # Nếu thời gian mục tiêu đã qua trong ngày, chuyển sang ngày hôm sau
#         if target_time < now :
#             target_time += timedelta(days=1)
        
#         time_to_wait = (target_time - now).total_seconds()
        
#         if time_to_wait <= 0:
#             return True, None
#         return False, time_to_wait
#     except:
#         return False, None

def get_time_check_cycle(time_check_string):
    try:
        time_check = int(time_check_string)
    except:
        time_check = 0
    return time_check * 60

def check_folder(folder):
    if not folder:
        print("Hãy chọn thư mục lưu video.")
        return False
    if not os.path.exists(folder):
        print(f"Thư mục {folder} không tồn tại.")
        return False
    return True

def get_list_video_in_folder(folder):
    all_file = os.listdir(folder)
    videos = [k for k in all_file if k.endswith('.mp4')]
    return videos