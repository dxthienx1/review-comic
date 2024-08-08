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
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from common_function_CTK import warning_message
from selenium_stealth import stealth
import subprocess
is_dev_enviroment = True
def get_current_dir():
    """Lấy thư mục đang chạy tệp thực thi"""
    if getattr(sys, 'frozen', False):
        # Đang chạy từ tệp thực thi đóng gói
        current_dir = os.path.dirname(sys.executable)
        is_dev_enviroment = False
    else:
        # Đang chạy trong môi trường phát triển
        current_dir = os.path.dirname(os.path.abspath(__file__))
        is_dev_enviroment = True
    return current_dir
current_dir = get_current_dir()
# current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(current_dir)
icon_path = os.path.join(current_dir, 'icon.png')
config_path = os.path.join(current_dir, 'config.json')
chromedriver_path = os.path.join(current_dir, 'import\\chromedriver.exe')
secret_path = os.path.join(current_dir, 'secret.json')
download_info_path = os.path.join(current_dir, 'download_info.json')
youtube_config_path = os.path.join(current_dir, 'youtube_config.json')
download_folder = f'{current_dir}\\download_folder'
os.makedirs(download_folder, exist_ok=True)
test_folder = f'{current_dir}\\test'
local_storage_path = os.path.join(current_dir, 'local_storage.json')
cookies_path = os.path.join(current_dir, 'cookies.json')
cookies_tiktok_path = os.path.join(current_dir, 'cookies_tiktok.pkl')
# cookies_youtube_path = os.path.join(current_dir, 'cookies_youtube.pkl')
youtube_config_path = os.path.join(current_dir, 'youtube_config.json')
tiktok_config_path = os.path.join(current_dir, 'tiktok_config.json')
facebook_config_path = os.path.join(current_dir, 'facebook_config.json')
pre_time_download = 0



def get_driver(show=True):
    try:
        print(chromedriver_path)
        service = Service(chromedriver_path)
        options = webdriver.ChromeOptions()
        if not show:
            options.add_argument('--headless')  # Chạy ở chế độ không giao diện
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
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
        return driver
    except:
        getlog()
        warning_message("Lỗi trong quá trình khởi tạo chromedriver.")
        return None


def convert_date_format_yyyymmdd_to_mmddyyyy(date_str):
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%m/%d/%Y")
    return formatted_date

def is_format_date_yyyymmdd(date_str, daydelta=None):
    # Kiểm tra định dạng ngày bằng biểu thức chính quy
    date_pattern = re.compile(r"^\d{4}-\d{2}-\d{2}$")
    if not date_pattern.match(date_str):
        return False, "Invalid date format"
    if daydelta:
        try:
            # Chuyển đổi từ chuỗi ngày sang đối tượng datetime
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            return False, "Invalid date format"

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

def add_days(datetime, days):
    return datetime + timedelta(days=days)

def convert_date_string_to_datetime(date_str):
    """Chuyển đổi chuỗi ngày sang đối tượng datetime.date."""
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        warning_message("Format date must be yyyy-mm-dd")
        getlog()
        return None
def get_time_remaining_until_quota_reset():
    # Giờ PST (Pacific Standard Time) có UTC offset là -8 giờ
    pst_timezone = timezone(timedelta(hours=-8))
    # Lấy thời gian hiện tại theo giờ UTC
    now_utc = datetime.now(timezone.utc)
    # Chuyển đổi thời gian hiện tại sang giờ PST
    now_pst = now_utc.astimezone(pst_timezone)
    # Lấy thời điểm reset hạn mức (00:00 giờ PST hôm sau)
    reset_time_pst = now_pst.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    # Tính toán thời gian còn lại đến khi reset
    time_remaining = reset_time_pst - now_pst
    total_seconds = time_remaining.total_seconds()
    return total_seconds
 
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
# Hàm để thêm ứng dụng vào danh sách khởi động cùng Windows
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
            portalocker.lock(f, portalocker.LOCK_EX)  # Khóa độc quyền (exclusive lock) để ghi
            json.dump(data, f, indent=3)
            portalocker.unlock(f)  # Giải phóng khóa
    except Exception as e:
        print(f"ERROR: can not save data to {filename}: {e}")
        getlog()
    
def get_txt_data(file_path, utf8=False):
    if not os.path.isfile(file_path):
        return None
    encoding = "utf-8" if utf8 else None
    with open(file_path, "r", encoding=encoding) as file:
        content = file.read()
    return content

def get_json_data_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
    else:
        data = None
        print("Failed to fetch the secret file.")
    return data

# Ghi lỗi vào file log.txt
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
        # Tạo video mới không có phần audio và lưu lại
        if is_get_video:
            output_folder, output_video_path, file_name, finish_folder = get_output_folder(video_path)
            video_clip_without_audio = video_clip.without_audio()
            video_clip_without_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
            video_clip_without_audio.close()
        video_clip.close()
        return audio_clip
    except:
        getlog()
        return None

def get_output_folder(input_video_path):
    folder_input = os.path.dirname(input_video_path)
    file_name = os.path.basename(input_video_path)
    output_folder = f'{folder_input}/output_folder'
    os.makedirs(output_folder, exist_ok=True)
    finish_folder = f'{folder_input}/finish_folder'
    os.makedirs(finish_folder, exist_ok=True)
    output_file_path = f'{output_folder}/{file_name}'
    return output_folder, output_file_path, file_name, finish_folder

#Áp dụng cho tất cả url
def download_video_by_url(url, download_folder=None, file_path=None, sleep_time=1):
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
                chars = ["/", "\\", ":", "|", "?", "*", "<", ">", "\""]
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
            ydl_opts = {
                'quiet': True,
                'no_warnings': True,
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'outtmpl': file_path,
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download(url)
        sleep(sleep_time)
        return True
    except:
        getlog()
    return False
    
def get_info_by_url(url, download_folder=None, is_download=False):
    if not url:
        return None
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,  # Cho phép viết phụ đề
            'allsubtitles': True,  # Tải tất cả các phụ đề có sẵn
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

#chỉ tiktok
def download_video_no_watermask_from_tiktok(video_url, download_folder=None):
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

def download_videos_form_playhh3dhay_by_txt_file(id_file_txt, download_folder=download_folder):
    def download_video_by_url(url, output_path):
        try:
            headers = {
                'Referer': 'https://playhh3dhay.xyz',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print(f"Video downloaded successfully to {output_path}")
                return True
            else:
                print(f"Failed to download video. Status code: {response.status_code}")
                return False
        except:
            return False
        
    file_data = get_txt_data(id_file_txt)
    if file_data is None:
        print(f"File {id_file_txt} không tồn tại.")
        return
    lines = file_data.splitlines()
    index = 1938
    temp_list_file = f"{download_folder}\\temp_list.txt"
    remove_file(temp_list_file)
    for line in lines:
        no_video_downloaded = False
        line = line.split(',')
        if len(line) == 1:
            server, video_id, end_url = 's1', line[0], '1080p/1080p_003.html'
        elif len(line) == 2:
            server, video_id, end_url = line[0], line[1], '1080p/1080p_003.html'
        else:
            server, video_id, end_url = line[0], line[1], line[2] #dạng s1,81ff33517ddda537c8858780626cfc12,1080p/1080p_003.html
        resolution = end_url.split('_')[0]
        exp = end_url.split('_')[1].split('.')[-1]
        print("-----------------------------------------")
        print(f"Bắt đầu tải tập phim với id {video_id} - Độ phân giải {resolution}")
        output_folder = os.path.join(download_folder, video_id)
        os.makedirs(output_folder, exist_ok=True)
        for j in range(1, 2000):
            if no_video_downloaded:
                break
            if j < 1000:
                j_str = f"{j:03}"
            else:
                j_str = f"{j:04}"
            for i in range(1, 6):
                video_url = f"https://{server}.playhh3dhay{i}.com/cdn/down/{video_id}/Video/{resolution}_{j_str}.{exp}"
                segment_path = os.path.join(output_folder, f"video_{index}.mp4")
                
                if download_video_by_url(video_url, segment_path):
                    no_video_downloaded = False  # Đặt lại cờ vì đã tải được video
                    index += 1
                    break
            else:
                no_video_downloaded = True

def get_xpath(maintag, class_name=None, attribute=None, attribute_value=None):
    if attribute and attribute_value:
        xpath = f"//{maintag}[@class=\"{class_name}\" and @{attribute}=\"{attribute_value}\"]"
    else:
        xpath = f"//{maintag}[@class=\"{class_name}\"]"
    return xpath
def get_xpath_by_multi_attribute(maintag, attributes):
    if len(attributes) > 1:
        attribute = " and @".join(attributes)
    else:
        attribute = attributes[0]
    attribute = f"@{attribute}"
    xpath = f"//{maintag}[{attribute}]"
    return xpath

def rename_files_by_index(folder_path, base_name, extension=None, start_index=1):
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
        new_file_name = f"{base_name}{index}{extension}"
        new_file_path = os.path.join(folder_path, new_file_name)
        try:
            os.rename(old_file_path, new_file_path)
            print(f"Đã đổi tên {old_file_path} thành {new_file_path}")
        except:
            print(f"Đổi tên file {old_file_path} không thành công")

