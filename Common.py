from common_function import os, datetime, save_to_json_file, get_json_data, get_json_data_from_url, sys, dtime
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(current_dir)
config_path = f'{current_dir}\\config.json'
secret_url = 'https://firebasestorage.googleapis.com/v0/b/supper-app-4f2ce.appspot.com/o/secret.json?alt=media&token=4747a38a-2220-4977-8383-95f8a89ce2cb'

def load_config():
    if os.path.exists(config_path):
        config = get_json_data(config_path)
    else:
        config = {
            "registered_gmails":["dxthienx2@gmail.com", "dxthienx10@gmail.com", "tranhangbk.001@gmail.com", "tranghangbk.002@gmail.com"],
            "registered_channel":["UCw84Zm5eXZHTMONt_OiqRXA", "UCxBuEz6aETSTRB55MoV9pKA", "UChWQUjInuNW5rVWvVlN-mJg", "UC9D6E5sCF2wGx1ApLEnr5XQ", "UCgxzKC2hwgkod7Xb2Lpb5uA"],
            "auto_channel_id":"",
            "download_folder":"",
            "output_folder":"",
            "from_language": "en-us",
            "to_language": "vi",
            "auto_start": False,

            "current_gmail": "dxthienx2@gmail.com",
            "current_tiktok_account": "dxthienx2@gmail.com",
            "current_facebook_account": "dxthienx2@gmail.com",
            "current_channel": "",
            "current_channel_id": "",

            "download_by_video_url": "",
            "download_by_channel_id": "",
            "download_by_channel_url": "",
            "filter_by_like": 100000,
            "filter_by_views": 5000000,

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
            "min_time_to_change_zoom": "3", 
            "max_time_to_change_zoom": "7", 
            "top_image_path": "",
            "bot_image_path": "",
            "top_height": "10", 
            "bot_height": "10", 
            "water_path": "",
            "vertical_watermask_position": "50",
            "horizontal_watermask_position": "50",

            "first_cut_audio": "", 
            "end_cut_audio": "", 
            "audio_speed": "", 
            "reversed_audio": False, 
            "audio_edit_path": "", 
            "video_get_audio_path": "", 
            "video_get_audio_url": "", 

            "supported_languages": {
                "ar": "Arabic",
                "bn": "Bengali",
                "zh-cn": "Chinese (Simplified, China)",
                "zh-tw": "Chinese (Traditional, Taiwan)",
                "cs": "Czech",
                "da": "Danish",
                "nl": "Dutch",
                "en-us": "English (United States)",
                "en-uk": "English (United Kingdom)",
                "fi": "Finnish",
                "fr": "French",
                "de": "German",
                "el": "Greek",
                "he": "Hebrew",
                "hi": "Hindi",
                "hu": "Hungarian",
                "id": "Indonesian",
                "it": "Italian",
                "ja": "Japanese",
                "ko": "Korean",
                "ms": "Malay",
                "no": "Norwegian",
                "fa": "Persian",
                "pl": "Polish",
                "pt": "Portuguese",
                "ro": "Romanian",
                "ru": "Russian",
                "sr": "Serbian",
                "sk": "Slovak",
                "sl": "Slovenian",
                "es": "Spanish",
                "sv": "Swedish",
                "th": "Thai",
                "tr": "Turkish",
                "uk": "Ukrainian",
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



