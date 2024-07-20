import json
import sys
import os
import re
import shutil
import random
import csv
from natsort import natsorted
from datetime import datetime, timedelta, timezone, time as dtime
from time import sleep, time
from tzlocal import get_localzone
import subprocess
import hashlib
import ctypes
import threading
import traceback
import pyttsx3
from moviepy.video.fx.all import resize, crop, mirror_x
from moviepy.video.fx.speedx import speedx
from moviepy.editor import VideoFileClip, AudioFileClip, concatenate_videoclips, afx, vfx, TextClip, CompositeVideoClip, ImageClip, ColorClip
from moviepy.audio.AudioClip import CompositeAudioClip
from pytube import YouTube
from translate import Translator
import requests
import speech_recognition as sr
from pydub import AudioSegment
from unidecode import unidecode
from tkinter import messagebox, filedialog
import customtkinter as ctk
import yt_dlp
import portalocker

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
from selenium_stealth import stealth
from selenium.webdriver.common.by import By

current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(current_dir)
icon_path = os.path.join(current_dir, 'icon.png')
youtube_info_path = os.path.join(current_dir, 'youtube_info.json')
config_path = os.path.join(current_dir, 'config.json')
output_folder = f'{current_dir}\\output_folder'
secret_path = os.path.join(current_dir, 'secret.json')
download_info_path = os.path.join(current_dir, 'download_info.json')
templates_path = os.path.join(current_dir, 'templates.json')
download_folder = f"{current_dir}\\downloads"
test_folder = f'{current_dir}\\test'
finish_folder = f"{current_dir}\\finish"

if not os.path.exists(download_folder):
    os.makedirs(download_folder)
if not os.path.exists(finish_folder):
    os.makedirs(finish_folder)

padx = 5
pady = 2
font_size = 14
height_element = 40
user32 = ctypes.windll.user32
screen_width = user32.GetSystemMetrics(0)
screen_height = user32.GetSystemMetrics(1)
LEFT = 'left'
left = 1/4
right = 3/4
RIGHT = 'right'
CENTER = 'center'

ffmpeg_dir = os.path.join(os.path.dirname(__file__), "ffmpeg", "bin")
# Cập nhật đường dẫn PATH trong mã Python
os.environ["PATH"] += os.pathsep + ffmpeg_dir
# Đảm bảo rằng pydub có thể tìm thấy ffmpeg
AudioSegment.converter = os.path.join(ffmpeg_dir, "ffmpeg.exe")


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

def convert_sang_tieng_viet_khong_dau(input_str):
    convert_text = unidecode(input_str)
    return re.sub(r'[\\/*?:"<>|]', "", convert_text)


def message_box(title, message):
    messagebox.askquestion(title=title, message=message)
def notification(message):
    messagebox.askquestion(title="Notification", message=message)
def warning_message(message):
    messagebox.askquestion(title="WARNING", message=message)
def error_message(message):
    messagebox.askquestion(title="ERROR", message=message)

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
    
def get_txt_data(file_path, utf8 = False):
    if os.path.isfile(file_path):
        if utf8:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
        else:
            with open(file_path, "r") as file:
                content = file.read()
        return content
    else:
        return None

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


def get_video_duration(video_path):
    try:
        clip = VideoFileClip(video_path)
        duration = clip.duration  # Lấy độ dài video (đơn vị giây)
        clip.close()
        return duration
    except Exception as e:
        print(f"Error getting video duration: {e}")
        return None

def get_file_name_from_path(video_path, suffix=True):
    try:
        file_name = os.path.basename(video_path)
        if not suffix:
            file_name = file_name.split('.')[0]
        return file_name
    except:
        getlog()
        return None

def strip_first_and_end_video(clip, first_cut, end_cut):
    first_cut = int(first_cut)
    end_cut = int(end_cut)
    if first_cut < 0:
        first_cut = 0
    if end_cut < 0 or end_cut >= clip.duration:
        warning_message("Invalid end_cut")
        return None
    return clip.subclip(first_cut, clip.duration - end_cut)

def zoom_and_crop(clip, zoom_factor, vertical_position='center', horizontal_position='center'):
    resized_clip = clip.resize(zoom_factor)
    new_width, new_height = resized_clip.size
    y1, y2 = 0, new_height
    x1, x2 = 0, new_width
    
    # Tính toán vị trí cắt theo chiều dọc
    if vertical_position == 'center':
        y1 = (new_height - clip.h) // 2
        y2 = y1 + clip.h
    elif vertical_position == 'top':
        y1 = 0
        y2 = clip.h
    elif vertical_position == 'bot':
        y1 = new_height - clip.h
        y2 = new_height

    # Tính toán vị trí cắt theo chiều ngang
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
        warning_message('invalid zoom size')
        return None
    return zoom_and_crop(clip, zoom_factor, vertical_position, horizontal_position)

def zoom_video_random_intervals(clip, max_zoom_size, min_time_to_change_zoom=3, max_time_to_change_zoom=5, vertical_position='center', horizontal_position='center'):
    if not min_time_to_change_zoom or min_time_to_change_zoom < 3:
        min_time_to_change_zoom = 3
    if not max_time_to_change_zoom or max_time_to_change_zoom < 5:
        max_time_to_change_zoom = 5

    max_zoom_size = float(max_zoom_size)
    min_time_to_change_zoom = int(min_time_to_change_zoom)
    max_time_to_change_zoom = int(max_time_to_change_zoom)
    if max_time_to_change_zoom > clip.duration:
        max_time_to_change_zoom = clip.duration
    
    start_times = []
    current_time = 0

    while current_time < clip.duration:
        start_times.append(current_time)
        current_time += random.uniform(min_time_to_change_zoom, max_time_to_change_zoom)

    if start_times[-1] < clip.duration:
        start_times.append(clip.duration)

    zoom_factors = [round(random.uniform(1.1, max_zoom_size), 2) for _ in range(len(start_times) - 1)]
    
    zoomed_clips = []
    try:
        for i, start_time in enumerate(start_times[:-1]):
            end_time = start_times[i + 1]
            sub_clip = clip.subclip(start_time, end_time)
            zoomed_clip = apply_zoom(sub_clip, zoom_factors[i], vertical_position, horizontal_position)
            zoomed_clips.append(zoomed_clip)
    
        final_zoom_clip = concatenate_videoclips(zoomed_clips, method="compose")
        return final_zoom_clip
    except:
        getlog()

def speed_up_clip(clip, speed):
    speed = float(speed)
    if speed < 0 or speed > 3:
        warning_message('invalid speed up')
        return None
    sped_up_clip = clip.fx(speedx, factor=speed)
    return sped_up_clip

def detect_video_ratio(clip, tolerance=0.02):
    clip_width, clip_height = clip.size
    ratio = clip_width / clip_height
    
    if abs(ratio - (16/9)) < tolerance:  # Kiểm tra xem tỷ lệ gần bằng 16:9
        return (16,9)
    elif abs(ratio - (9/16)) < tolerance:  # Kiểm tra xem tỷ lệ gần bằng 9:16
        return (9,16)
    else:
        return False
def resize_clip(clip):
    target_ratio = detect_video_ratio(clip)
    target_width, target_height = target_ratio
    clip_width, clip_height = clip.size
    if clip_width / clip_height != target_width / target_height:
        target_clip_width = clip_height * target_width / target_height
        resized_clip = resize(clip, newsize=(target_clip_width, clip_height))
        return resized_clip
    return clip

def flip_clip(clip):
    # Áp dụng hiệu ứng đối xứng (flip) theo chiều ngang
    flipped_clip = mirror_x(clip)
    return flipped_clip

def add_image_watermask_into_video(clip, top_overlay_height="10", bot_overlay_height="10", watermask = None, vertical_watermask_position=50, horizontal_watermask_position=50):
    if not top_overlay_height or int (top_overlay_height) < 0:
        top_overlay_height = 2
    else:
        top_overlay_height = int(top_overlay_height)
    if not bot_overlay_height or int (bot_overlay_height) < 0:
        bot_overlay_height = 2
    else:
        bot_overlay_height = int(bot_overlay_height)
    
    try:
        width, height = clip.size
        top_image = ColorClip(size=(width, top_overlay_height), color=(0, 0, 0)).set_position(('center', 0)).set_duration(clip.duration)
        bottom_image = ColorClip(size=(width, bot_overlay_height), color=(0, 0, 0)).set_position(('center', height - bot_overlay_height)).set_duration(clip.duration)
    
        if watermask:
            if horizontal_watermask_position:
                try:
                    horizontal_watermask_position = int(horizontal_watermask_position) * width/100
                except:
                    getlog()
                    horizontal_watermask_position = 'center'
            else:
                horizontal_watermask_position = 'center'
            if vertical_watermask_position:
                try:
                    vertical_watermask_position = int(vertical_watermask_position) * height/100
                except:
                    getlog()
                    vertical_watermask_position = 'center'
            else:
                vertical_watermask_position = 'center'
            watermask_image = (ImageClip(watermask).set_position((horizontal_watermask_position, vertical_watermask_position)).set_duration(clip.duration))
            final_clip = CompositeVideoClip([clip, top_image, bottom_image, watermask_image])
        else:
            final_clip = CompositeVideoClip([clip, top_image, bottom_image])
        return final_clip
    except:
        getlog()
        return None
    
def edit_audio(audio_path=None, video_path=None, video_url=None, reversed_audio=False, speed="1", first_cut_audio="0", end_cut_audio="0"):
    speed = float(speed)
    first_cut_audio = int(first_cut_audio)
    end_cut_audio = int(end_cut_audio)
    if audio_path:
        output_folder, output_audio_path, file_name = get_output_folder(audio_path)
        audio_clip = AudioFileClip(audio_path)
    elif video_path:
        output_folder, output_audio_path, file_name = get_output_folder(video_path)
        audio_clip = get_audio_clip_from_video(video_path)
    elif video_url:
        video_path = download_video_by_url(video_url)
        output_folder, output_audio_path, file_name = get_output_folder(video_path)
        audio_clip = get_audio_clip_from_video(video_path)
    else:
        warning_message("Vui lòng chọn nguồn để edit video")
        return
    
    try:
        if int(end_cut_audio) > 0 or int(first_cut_audio) > 0:
            audio_clip = audio_clip.subclip(first_cut_audio, audio_clip.duration - end_cut_audio)
        # Đảo ngược âm thanh
        if reversed_audio:
            audio_clip = audio_clip.fx(vfx.time_mirror)
        # Thay đổi tốc độ âm thanh
        if float(speed) != 1:
            audio_clip = audio_clip.fx(speedx, speed)

        audio_name = file_name.split('.')[0]
        output_audio_path = f'{output_folder}\\{audio_name}.mp3'
        audio_clip.write_audiofile(output_audio_path, codec='mp3')
        audio_clip.close()
    except Exception as e:
        getlog()

def get_audio_clip_from_video(video_path=None, is_get_video=False):
    try:
        output_folder, output_video_path, file_name = get_output_folder(video_path)
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
        # Tạo video mới không có phần audio và lưu lại
        if is_get_video:
            video_clip_without_audio = video_clip.without_audio()
            video_clip_without_audio.write_videofile(output_video_path, codec='libx264', audio_codec='aac')
            video_clip_without_audio.close()
        audio_clip.close()
        video_clip.close()
        return audio_clip
    except:
        getlog()

def remove_audio_from_clip(clip):
    return clip.without_audio()
def set_audio_for_clip(clip, background_music, background_music_volume="10"):
    volume = float(background_music_volume)/100
    background_music = AudioFileClip(background_music)
    background_music = background_music.volumex(volume)
    background_music = afx.audio_loop(background_music, duration=clip.duration)
    current_audio = clip.audio
    if current_audio is None:
        clip = clip.set_audio(background_music)
    else:
        # Kết hợp giọng thuyết minh và nhạc nền
        combined_audio = CompositeAudioClip([current_audio, background_music])
        clip = clip.set_audio(combined_audio)
    return clip

def get_output_folder(input_video_path):
    folder_input = os.path.dirname(input_video_path)
    file_name = os.path.basename(input_video_path)
    output_folder = f'{folder_input}\\output_folder'
    os.makedirs(output_folder, exist_ok=True)
    output_file_path = f'{output_folder}\\{file_name}'
    return output_folder, output_file_path, file_name

#Áp dụng cho tất cả url
def download_video_by_url(url, download_folder=output_folder):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            # 'writesubtitles': True,  # Cho phép viết phụ đề
            # 'allsubtitles': True,  # Tải tất cả các phụ đề có sẵn
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'addmetadata': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download(url)
            sleep(1)
    except:
        getlog()

def get_info_by_url(url):
    try:
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'writesubtitles': True,  # Cho phép viết phụ đề
            'allsubtitles': True,  # Tải tất cả các phụ đề có sẵn
            'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
            'outtmpl': f'{download_folder}/%(title)s.%(ext)s',
            'addmetadata': False,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_video = ydl.extract_info(url, download=False)
            # automatic_captions = info_dict.get('automatic_captions', [])
            # if automatic_captions:
            #     if lang in automatic_captions:
            #         all = automatic_captions[lang]
            #         for pd in all:
            #             if pd['ext'] == 'srt':
            #                 return {'srt':pd['url']}
            #             if pd['ext'] == 'vtt':
            #                 return {'vtt':pd['url']}
            #             if pd['ext'] == 'ttml':
            #                 return {'ttml':pd['url']}

            return info_video
    except:
        getlog()

#chỉ tiktok
def download_video_no_watermask_from_tiktok(video_url, download_folder=output_folder):
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
        except:
            getlog()






# video_url = 'https://www.youtube.com/watch?v=quSPOIgsPno'
# info_dict = download_video_by_url(video_url, is_download=False)
# print("Video information:")
# print(info_dict)

# # Lấy danh sách các phụ đề
# subtitles = info_dict.get('subtitles', {}).keys()
# # In ra các ngôn ngữ phụ đề có sẵn
# print("Available subtitles languages:")
# for lang in subtitles:
#     print(lang)
# # Nếu muốn lấy phụ đề tiếng Anh (ví dụ)
# if 'en' in subtitles:
#     subtitle_info = info_dict['subtitles']['en']
#     subtitle_url = subtitle_info['url']
    
#     # Tải nội dung phụ đề
#     with yt_dlp.YoutubeDL(ydl_opts) as ydl:
#         subtitle_content = ydl.urlopen(subtitle_url).read().decode('utf-8')
#         # In nội dung phụ đề
#         print("Subtitle content:")
#         print(subtitle_content)

