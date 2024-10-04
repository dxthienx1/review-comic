from common_function import os, datetime, save_to_json_file, get_json_data, get_json_data_from_url, sys, dtime, config_path, youtube_config_path, facebook_config_path, tiktok_config_path, download_info_path

def load_config():
    if os.path.exists(config_path):
        config = get_json_data(config_path)
    else:
        config = {
            "download_folder":"",
            "output_folder":"",
            "from_language": "en-us",
            "to_language": "vi",
            "auto_start": False,
            "is_delete_video": False,
            "is_move": False,
            "show_browser": False,

            "current_youtube_account": "",
            "current_tiktok_account": "",
            "current_facebook_account": "",
            "current_channel": "",
            "current_page": "",
            "download_by_video_url": "",

            "file_name": "",
            "start_index": "",
            "videos_edit_folder": "",
            "quantity_split": "1",
            "first_cut": "1",
            "end_cut": "2",
            "is_delete_original_audio": False,
            "background_music_path": "",
            "background_music_volume": "",
            "speed_up": "1.05",
            "max_zoom_size": "1.05",
            "is_random_zoom": False,
            "vertical_position": 'center',
            "horizontal_position": 'center',
            "flip_video": False,
            "water_path": "",
            "watermark_scale": "1,1",
            "vertical_watermark_position": "50",
            "horizontal_watermark_position": "50",
            "watermark_scale": "1,1",
            "top_bot_overlay": "2,2",
            "left_right_overlay": "2,2",

            "audio_speed": "", 
            "reversed_audio": False, 
            "audio_edit_path": "", 
            "video_get_audio_path": "", 
            "video_get_audio_url": "", 
            "speed_talk": "1", 
            "convert_multiple_record": False, 

            "supported_languages": {
                "en-us": "English (United States)",
                "vi": "Vietnamese"
            }
        }
        save_to_json_file(config, config_path)
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
   "download_by_channel_id": "",
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
   "download_by_channel_url": "",
   "download_folder": "",
   "is_move": False,
   "is_delete_after_upload": False,
   "filter_by_like": "0",
   "filter_by_views": "0",
   "template": {}
}

facebook_config = {
   "show_browser": False,
   "download_folder": "",
   "registered_account": [],
   "template": {}
}


def load_youtube_config():
    if os.path.exists(youtube_config_path):
        config = get_json_data(youtube_config_path)
    else:
        config = youtube_config
    save_to_json_file(config, youtube_config_path)
    return config

def load_tiktok_config():
    if os.path.exists(tiktok_config_path):
        config = get_json_data(tiktok_config_path)
    else:
        config = tiktok_config
    save_to_json_file(config, tiktok_config_path)
    return config

def load_facebook_config():
    if os.path.exists(facebook_config_path):
        config = get_json_data(facebook_config_path)
    else:
        config = facebook_config
    save_to_json_file(config, facebook_config_path)
    return config

