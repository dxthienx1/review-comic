import threading
import tkinter.font as tkfont
from PIL import Image, ImageDraw
import pystray
import winreg
from pystray import MenuItem as item
from common_function import *
from tiktok_management import TikTokManager
from youtube import YouTubeManager
from Common import *

class MainApp:
    def __init__(self):
        try:
            self.font_size = 15
            self.root = ctk.CTk()
            self.root.title("Super App")
            self.font_label = ctk.CTkFont(family="Arial", size=self.font_size)
            self.font_button = ctk.CTkFont( family="Arial", size=self.font_size, weight="bold")
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.config = load_config()
            if not self.config['output_folder']:
                self.config['output_folder'] = output_folder
            self.youtube = {}
            self.tiktok = {}
            self.facebook = {}
            self.windows = {}
            self.titles = {}
            self.load_secret_info()

            self.engine = pyttsx3.init()
            self.voices = []
            self.all_voice_index = {}

            remove_file("log.txt")
            self.config_path = get_file_path("config.json")
            #kiem tra quota
            time_remaining = get_time_remaining_until_quota_reset()
            print(f"thời gian reset quota là {time_remaining/3600} giờ")
            self.next_time_check_quocta = time() + time_remaining

            self.translator=None
            self.languages = self.config["supported_languages"]
            self.convert_multiple_record = False
            self.load_translate()

            self.text_show_width = 350
            self.is_start_app = True
            self.is_setting = False
            self.is_edit_video_window = False
            self.is_edit_audio_window = False
            self.is_youtube_window = False
            self.is_tiktok_window = False
            self.is_facebook_window = False
            self.is_editing_video = False
            self.thread = None
            self.thread_main = None
            self.icon = None
            self.is_auto_upload = False

            self.next_time_check_quocta = 0
            
            # self.start_main_check_thread()
            self.setting_window_size()
            self.create_icon()
            self.get_start_window()

            if self.config["auto_start"]:
                self.set_autostart()
            else:
                self.unset_autostart()
        except:
            getlog()

    def start_main_check_thread(self):
            self.thread_main = threading.Thread(target=self.main_check_thread)
            self.thread_main.daemon = True  # Để thread kết thúc khi chương trình chính kết thúc
            self.thread_main.start()

    def main_check_thread(self):
        while True:
            try:
                self.check_quota_reset()
                self.auto_upload_every_day()
                
                print("main_check_thread đang chạy...")
                sleep(300)
            except:
                getlog()

    def get_templates(self, channel_id):
        self.templates = get_json_data(templates_path)
        if not self.templates:
            self.templates = {}
        if channel_id and channel_id not in self.templates:
            self.templates[channel_id] = {}
    def save_template(self):
        save_to_json_file(self.templates, templates_path)

    def auto_upload_every_day(self):
        
        if self.is_auto_upload:
            for channel_id in self.config['auto_channel_id']: #những channel muốn chạy auto
                self.get_templates(channel_id)
                if channel_id in self.templates.keys: 
                    gmail = self.templates[channel_id].get('gmail', None)
                    if not gmail:
                        continue 
                    oauth_path = f'app.py-{gmail}-{channel_id}.json'
                    if os.path.isfile(oauth_path):
                        recent_upload_date_str = self.templates[channel_id].get('start_date')
                        recent_upload_date = None
                        if recent_upload_date_str:
                            recent_upload_date = datetime.strptime(recent_upload_date_str, '%Y-%m-%d')
                        current_time = datetime.now()
                        auto_upload_time_str = self.templates[channel_id]['auto_upload_time']
                        auto_upload_time = convert_date_string_to_datetime(auto_upload_time_str)
                        if current_time >= auto_upload_time:
                            if recent_upload_date:
                                next_upload_date = recent_upload_date + timedelta(days=1)
                            else:
                                next_upload_date = current_time.date() + timedelta(days=1)
                            # Cập nhật lại ngày đăng tiếp theo trong thông tin YouTube
                            self.templates[channel_id]['start_date'] = next_upload_date.strftime('%Y-%m-%d')
                            self.save_template()
                            self.youtube[gmail] = YouTubeManager(self.config, self.secret_info, gmail, channel_id)
                            self.youtube[gmail].schedule_videos()
                            sleep(30)
           
            
    def check_quota_reset(self):
        if time() - self.next_time_check_quocta >= 0:
            for gmail in self.config['registered_gmails']:
                if self.youtube:
                    if gmail in self.youtube:
                        self.youtube[gmail].is_quotaExceeded = False
                        self.config[gmail]['cnt_request_upload'] = 0
            self.save_config()

    def load_secret_info(self):
        secret_data = get_json_data(secret_path)
        self.secret_info={}
        for gmail in self.config['registered_gmails']:
            oauth = secret_data[gmail]['oauth']
            api = secret_data[gmail]['api']
            oauth_path = f'{current_dir}\\oauth\\{gmail}.json'
            save_to_json_file(oauth, oauth_path)
            self.secret_info[gmail] = {}
            self.secret_info[gmail]["oauth_path"] = oauth_path
            self.secret_info[gmail]["api"] = api

    def get_start_window(self):
        if not self.is_start_app:
            self.reset()
            self.is_start_app = True
            self.setting_window_size()
        self.is_start_app = False
        self.show_window()
        self.input_gmail = self.create_settings_input("Choose Gmail Account", "current_gmail" ,values=self.config['registered_gmails'], left=0.4, right=0.6)
        self.input_current_channel = self.create_settings_input("Choose Channel Id", "current_channel" ,values=self.config['registered_channel'], left=0.4, right=0.6)
        self.create_button(text="Open YouTube Management", command=self.open_youtube_window)
        self.create_button(text="Open Tiktok Management", command=self.open_tiktok_window)
        self.create_button(text="Open Facebook Management", command=self.open_facebook_window)
        self.create_button(text="Text To MP3", command=self.open_text_to_mp3_window)
        self.create_button(text="Edit Videos 16:9", command=self.open_edit_video_window)
        self.create_button(text="Edit Videos 9:16", command=self.open_edit_video_window)
        self.create_button(text="Download And Edit Audio", command=self.open_edit_audio_window)
        self.create_button(text="Common Settings", command=self.open_common_settings)
    
    def open_youtube_window(self):
        gmail = self.input_gmail.get()
        channel_id = self.input_current_channel.get()
        if gmail not in self.config['registered_gmails']:
            self.config['registered_gmails'].append(gmail)
        if channel_id not in self.config['registered_channel'].keys():
            self.config['registered_channel'].append(channel_id)
        self.config['current_gmail'] = gmail
        self.config['current_channel'] = channel_id
        self.save_config()
        if gmail not in self.config['registered_gmails']:
            message_box("Warning", "Your account does not have access!")
            return
        self.reset()
        self.youtube[gmail] = YouTubeManager(self.config, self.secret_info, gmail, channel_id)
        self.youtube[gmail].get_start_youtube()
        

    def open_tiktok_window(self):
        gmail = self.input_gmail.get()
        if gmail not in self.config['registered_gmails']:
            self.config['registered_gmails'].append(gmail)
        self.config['current_gmail'] = gmail
        self.save_config()
        if gmail not in self.config['registered_gmails']:
            message_box("Warning", "Your account does not have access!")
            return
        self.reset()
        self.setting_window_size()
        self.tiktok[gmail] = TikTokManager(self.config, gmail)
        self.tiktok[gmail].get_start_tiktok()

    def open_facebook_window(self):
        pass

#---------------------------------------------------------------------edit audio
    def open_edit_audio_window(self):
        self.reset()
        self.is_edit_audio_window = True
        self.setting_window_size()
        self.show_window()
        self.first_cut_audio_var = self.create_settings_input("First Cut", "first_cut_audio", values=["5", "10", "15"])
        self.end_cut_audio_var = self.create_settings_input("End Cut", "end_cut_audio", values=["5", "10", "15"])
        self.audio_speed_var = self.create_settings_input("Audio Speed", "audio_speed", values=["0.8", "0.9", "1", "1.1", "1.2"])
        self.reversed_audio_var = self.create_settings_input("Reversed Audio", "reversed_audio", values=["Yes", "No"])
        self.video_get_audio_url = self.create_frame_label_and_input(label_text="Get Audio From Video URL", left=0.4, right=0.6)
        self.audio_edit_path = self.create_frame_button_and_input(text="Edit Audio From MP3 File", command= self.choose_audio_edit_file, left=0.4, right=0.6)
        self.video_get_audio_path = self.create_frame_button_and_input(text="Get Audio From Video", command= self.choose_video_get_audio_path, left=0.4, right=0.6)
        self.create_button(text="Start Edit Audio", command=self.create_thread_edit_audio)

    def choose_audio_edit_file(self):
        audio_edit_path = filedialog.askopenfilename()
        if audio_edit_path:
            self.audio_edit_path.delete(0, ctk.END)
            self.audio_edit_path.insert(0, audio_edit_path)
        else:
            warning_message("Please choose the mp3 file")

    def choose_video_get_audio_path(self):
        video_get_audio_path = filedialog.askopenfilename()
        if video_get_audio_path:
            self.video_get_audio_path.delete(0, ctk.END)
            self.video_get_audio_path.insert(0, video_get_audio_path)
        else:
            warning_message("Please choose the mp3 file")

    def create_thread_edit_audio(self):
        thread_edit_audio = threading.Thread(target=self.start_edit_audio)
        thread_edit_audio.daemon = True
        thread_edit_audio.start()

    def start_edit_audio(self):
        audio_edit_path = self.audio_edit_path.get()
        video_get_audio_path = self.video_get_audio_path.get()
        video_get_audio_url = self.video_get_audio_url.get()
        if not audio_edit_path and not video_get_audio_path and not video_get_audio_url:
            warning_message("Please select only one source to edit audio")
            return
        if (audio_edit_path and video_get_audio_path) or (audio_edit_path and video_get_audio_url) or (video_get_audio_path and video_get_audio_url):
            warning_message("Choose only one source to edit audio")
            return
        def save_edit_audio_setting():
            self.config['first_cut_audio'] = self.first_cut_var.get()
            self.config['end_cut_audio'] = self.end_cut_var.get()
            self.config['audio_speed'] = self.speed_up_var.get()
            self.config['reversed_audio'] = self.reversed_audio_var.get()
            self.config['audio_edit_path'] = audio_edit_path
            self.config['video_get_audio_path'] = video_get_audio_path
            self.config['video_get_audio_url'] = video_get_audio_url
        save_edit_audio_setting()
        
        self.save_config()
        edit_audio(audio_path=self.config['audio_edit_path'], video_path=self.config['video_get_audio_path'], video_url=self.config['video_get_audio_url'], speed=self.config['speed'], first_cut_audio=self.config['first_cut_audio'], end_cut_audio=self.config['end_cut_audio'], reversed_audio=self.config['reversed_audio'])

#---------------------------------------------------------------------edit video 9:16
    def open_edit_video_window(self):
        self.reset()
        self.is_edit_video_window = True
        self.setting_window_size()
        self.show_window()
        self.file_name_var, self.start_index_var = self.create_frame_label_input_input("Batch file naming by index", place_holder1="Input file name containing the string <index>", place_holder2="start index")
        self.quantity_split_var = self.create_settings_input("Quantity split", "quantity_split", values=["1", "2", "3", "4", "5"])
        self.first_cut_var = self.create_settings_input("First Cut", "first_cut", values=["3", "4", "5"])
        self.end_cut_var = self.create_settings_input("End Cut", "end_cut", values=["3", "4", "5"])
        self.flip_video_var = self.create_settings_input("Flip Video", "flip_video", values=["Yes", "No"])
        self.speed_up_var = self.create_settings_input("Speed Up", "speed_up", values=["0.8", "0.9", "1", "1.1", "1.2"])
        self.max_zoom_size_var = self.create_settings_input("Max Zoom size", "max_zoom_size", values=["1", "1.1", "1.2", "1.3", "1.4"])
        self.is_random_zoom_var = self.create_settings_input("Is Random Zoom", "is_random_zoom", values=["Yes", "No"])
        self.min_time_to_change_zoom_var = self.create_settings_input("Min Time To Change Zoom", "min_time_to_change_zoom", values=["3", "4", "5"])
        self.max_time_to_change_zoom_var = self.create_settings_input("Max Time To Change Zoom", "max_time_to_change_zoom", values=["5", "10", "15"])
        self.vertical_position_var = self.create_settings_input("Vertical Display", "vertical_position", values=["top", "center", "bottum"])
        self.horizontal_position_var = self.create_settings_input("Horizontal Display", "horizontal_position", values=["left", "center", "right"])
        self.top_height_var = self.create_settings_input("Top Overlay Height", "top_height", values=["100", "150", "200"])
        self.bot_height_var = self.create_settings_input("Bot Overlay Height", "bot_height", values=["100", "150", "200"])
        self.is_delete_original_audio_var = self.create_settings_input("Is Delete Original Audio", "is_delete_original_audio", values=["Yes", "No"])
        self.background_music_path, self.background_music_volume_var = self.create_frame_button_input_input(text="Choose background music", command= self.choose_background_music, place_holder1="background music path", place_holder2="Volume")
        self.water_path_var = self.create_frame_button_and_input("Choose WaterMask Image", command= self.choose_water_mask_image, left=0.4, right=0.6)
        self.vertical_watermask_position_var = self.create_settings_input("Vertical Watermask Position", "vertical_watermask_position", values=["top", "center", "bottum"])
        self.horizontal_watermask_position_var = self.create_settings_input("Horizontal Watermask Position", "horizontal_watermask_position", values=["left", "center", "right"])
        self.videos_folder_handle_path = self.create_frame_button_and_input(text="Choose videos Edit folder", command= self.choose_videos_edit_folder, left=0.4, right=0.6)
        self.background_music_path.insert(0, self.config['background_music_path'])
        self.background_music_volume_var.insert(0, self.config['background_music_volume'])
        self.water_path_var.insert(0, self.config['water_path'])
        self.videos_folder_handle_path.insert(0, self.config['videos_edit_folder'])
        self.create_button(text="Start Edit Videos", command=self.create_thread_edit_video)

    def create_thread_edit_video(self):
        self.list_edit_finished = []
        thread_edit_video = threading.Thread(target=self.start_edit_video)
        thread_edit_video.daemon = True
        thread_edit_video.start()

    def start_edit_video(self):
        def save_edit_setting():
            # self.config['file_name'] = self.file_name_var.get()
            # self.config['start_index'] = self.start_index_var.get()
            self.config['videos_edit_folder'] = self.videos_folder_handle_path.get()
            self.config['is_delete_original_audio'] = self.is_delete_original_audio_var.get() == "Yes"
            self.config['background_music_path'] = self.background_music_path.get()
            self.config['background_music_volume'] = self.background_music_volume_var.get()
            self.config['quantity_split'] = self.quantity_split_var.get()
            self.config['first_cut'] = self.first_cut_var.get()
            self.config['end_cut'] = self.end_cut_var.get()
            self.config['flip_video'] = self.flip_video_var.get() == "Yes"
            self.config['speed_up'] = self.speed_up_var.get()
            self.config['max_zoom_size'] = self.max_zoom_size_var.get()
            self.config['vertical_position'] = self.vertical_position_var.get()
            self.config['horizontal_position'] = self.horizontal_position_var.get()
            self.config['min_time_to_change_zoom'] = self.min_time_to_change_zoom_var.get()
            self.config['max_time_to_change_zoom'] = self.max_time_to_change_zoom_var.get()
            self.config['water_path'] = self.water_path_var.get()
            self.config['vertical_watermask_position'] = self.vertical_watermask_position_var.get()
            self.config['horizontal_watermask_position'] = self.horizontal_watermask_position_var.get()
            self.config['top_height'] = self.top_height_var.get()
            self.config['bot_height'] = self.bot_height_var.get()
        save_edit_setting()
        video_folder = self.config['videos_edit_folder']
        if not video_folder:
            warning_message("Please choose the videos edit folder")
            return
        if float(self.config['max_zoom_size']) < 1.05:
            self.config['max_zoom_size'] = "1.05"
        if float(self.config['max_zoom_size']) > 1.5:
            warning_message("The maximum value of max_zoom_size is 1.5")
            return

        self.save_config()
        edit_videos = os.listdir(video_folder)
        self.batch_file_name = self.file_name_var.get()
        if self.batch_file_name and "<index>" not in self.batch_file_name:
            warning_message("Please enter a file name containing the string \"<index>\"")
            return
        if self.start_index_var.get():
            try:
                index = int(self.start_index_var.get()) -1 or 0
            except:
                getlog()
                index = 0
        else:
            index = 0
        
        for i, video_file in enumerate(edit_videos):
            if '.mp4' not in video_file:
                continue
            index += 1
            video_path = f'{video_folder}\\{video_file}'
            is_edit_ok = self.edit_video(video_path, index)
            if is_edit_ok:
                print(f"Edited finish video {video_file}")
        cnt = len(self.list_edit_finished)
        if cnt > 0:
            notification(f"Successfully edited {cnt} files: {self.list_edit_finished}")

    def edit_video(self, input_video_path, index):
        self.hide_window()
        try:
            if int(self.config['quantity_split']) > 1:
                quantity_split = int(self.config['quantity_split'])
            else:
                quantity_split = 1

            output_directory = f'{os.path.dirname(input_video_path)}\\output_folder'
            os.makedirs(output_directory, exist_ok=True)
            if not self.batch_file_name:
                file_name = get_file_name_from_path(input_video_path, suffix=False)
                file_name = convert_sang_tieng_viet_khong_dau(file_name)
            else:
                file_name = self.batch_file_name.replace("<index>", str(index))
            
            input_clip = VideoFileClip(input_video_path)
            resized_clip = resize_clip(input_clip)
            if self.config['flip_video']:
                f_clip = flip_clip(resized_clip)
            else:
                f_clip = resized_clip
            clip_duration = f_clip.duration
            video_clip = strip_first_and_end_video(f_clip, first_cut=self.config['first_cut'], end_cut=self.config['end_cut'])
            if not video_clip:
                return
            if self.config['is_delete_original_audio']:
                video_clip = remove_audio_from_clip(video_clip)
            if os.path.isfile(self.config['background_music_path']):
                add_audio_clip = set_audio_for_clip(video_clip, self.config['background_music_path'], self.config['background_music_volume'])
            else:
                add_audio_clip = video_clip
            speed_clip = speed_up_clip(add_audio_clip, speed=self.config['speed_up'])
            if self.config['is_random_zoom']:
                zoom_clip = zoom_video_random_intervals(clip=speed_clip, max_zoom_size=self.config['max_zoom_size'], min_time_to_change_zoom=self.config['min_time_to_change_zoom'], max_time_to_change_zoom=self.config['max_time_to_change_zoom'], vertical_position=self.config['vertical_position'], horizontal_position=self.config['horizontal_position'])
            else:
                zoom_clip = apply_zoom(clip=speed_clip, zoom_factor=self.config['max_zoom_size'], vertical_position=self.config['vertical_position'], horizontal_position=self.config['horizontal_position'])
            clip_duration = zoom_clip.duration
            
            one_clip_duration = clip_duration / quantity_split

            for i in range(quantity_split):
                if i == 0:
                    start_time = 0
                else:
                    start_time = i * one_clip_duration - 3
                end_time = min((i + 1) * one_clip_duration, clip_duration)
                one_clip = zoom_clip.subclip(start_time, end_time)
                final_clip = add_image_watermask_into_video(one_clip, top_overlay_height=self.config['top_height'], bot_overlay_height=self.config['bot_height'], watermask=self.config['water_path'], vertical_watermask_position=self.config['vertical_watermask_position'], horizontal_watermask_position=self.config['horizontal_watermask_position'])
                if final_clip:
                    if self.batch_file_name:
                        output_file = os.path.join(output_directory, f"{file_name}.mp4")
                    else:
                        output_file = os.path.join(output_directory, f"{file_name}_{i + 1}.mp4")

                    final_clip.write_videofile(output_file, codec='libx264', fps=24)
                    self.list_edit_finished.append(input_video_path)
                    final_clip.close()
                else:
                    return False
            input_clip.close()
            sleep(1)
            try:
                shutil.move(input_video_path, f'{finish_folder}\\{file_name}.mp4')
            except:
                getlog()
            return True
        except Exception as e:
            getlog()
            return False


#---------------------------------------------------------------------edit video 16:9
    # def open_edit_video_window(self):
    #     self.reset()
    #     self.is_edit_video_window = True
    #     self.setting_window_size()
    #     self.show_window()
    #     self.quantity_split_var = self.create_settings_input("Quantity split", "quantity_split", values=["1", "2", "3", "4", "5"])
    #     self.first_cut_var = self.create_settings_input("First Cut", "first_cut", values=["3", "4", "5"])
    #     self.end_cut_var = self.create_settings_input("End Cut", "end_cut", values=["3", "4", "5"])
    #     self.flip_video_var = self.create_settings_input("Flip Video", "flip_video", values=["Yes", "No"])
    #     self.speed_up_var = self.create_settings_input("Speed Up", "speed_up", values=["0.8", "0.9", "1", "1.1", "1.2"])
    #     self.is_random_zoom_var = self.create_settings_input("Is Random Zoom", "is_random_zoom", values=["Yes", "No"])
    #     self.max_zoom_size_var = self.create_settings_input("Max Zoom size", "max_zoom_size", values=["1.05", "1.1", "1.15", "1.2"])
    #     self.vertical_position_var = self.create_settings_input("Vertical Display", "vertical_position", values=["top", "center", "bottum"])
    #     self.horizontal_position_var = self.create_settings_input("Horizontal Display", "horizontal_position", values=["left", "center", "right"])
    #     self.min_time_to_change_zoom_var = self.create_settings_input("Min Time To Change Zoom", "min_time_to_change_zoom", values=["3", "4", "5"])
    #     self.max_time_to_change_zoom_var = self.create_settings_input("Max Time To Change Zoom", "max_time_to_change_zoom", values=["5", "10", "15"])
    #     self.background_music_path = self.create_frame_button_and_input(text="Choose background music", command= self.choose_background_music, left=0.4, right=0.6)
    #     self.background_music_volume_var = self.create_settings_input("Background music volume", "background_music_volume", values=["5", "10", "15"])
    #     self.videos_folder_handle_path = self.create_frame_button_and_input(text="Choose videos Edit folder", command= self.choose_videos_edit_folder, left=0.4, right=0.6)
    #     self.background_music_path.insert(0, self.config['background_music_path'])
    #     self.videos_folder_handle_path.insert(0, self.config['videos_edit_folder'])
    #     self.create_button(text="Start Edit Videos", command=self.create_thread_edit_video)

    def choose_background_music(self):
        background_music_path = filedialog.askopenfilename()
        self.background_music_path.delete(0, ctk.END)
        self.background_music_path.insert(0, background_music_path)

    def choose_videos_edit_folder(self):
        videos_edit_folder = filedialog.askdirectory()
        self.videos_folder_handle_path.delete(0, ctk.END)
        self.videos_folder_handle_path.insert(0, videos_edit_folder)

    def choose_water_mask_image(self):
        water_mask_image = filedialog.askopenfilename()
        self.water_path_var.delete(0, ctk.END)
        self.water_path_var.insert(0, water_mask_image)

    # def create_thread_edit_video(self):
    #     self.list_edit_finished = []
    #     thread_edit_video = threading.Thread(target=self.start_edit_video)
    #     thread_edit_video.daemon = True
    #     thread_edit_video.start()

    # def start_edit_video(self):
    #     def save_edit_setting():
    #         self.config['videos_edit_folder'] = self.videos_folder_handle_path.get()
    #         self.config['background_music_path'] = self.background_music_path.get()
    #         self.config['background_music_volume'] = self.background_music_volume_var.get()
    #         self.config['quantity_split'] = self.quantity_split_var.get()
    #         self.config['first_cut'] = self.first_cut_var.get()
    #         self.config['end_cut'] = self.end_cut_var.get()
    #         self.config['flip_video'] = self.flip_video_var.get() == "Yes"
    #         self.config['speed_up'] = self.speed_up_var.get()
    #         self.config['is_random_zoom'] = self.is_random_zoom_var.get() == "Yes"
    #         self.config['max_zoom_size'] = self.max_zoom_size_var.get()
    #         self.config['vertical_position'] = self.vertical_position_var.get()
    #         self.config['horizontal_position'] = self.horizontal_position_var.get()
    #         self.config['min_time_to_change_zoom'] = self.min_time_to_change_zoom_var.get()
    #         self.config['max_time_to_change_zoom'] = self.max_time_to_change_zoom_var.get()
    #     save_edit_setting()
    #     video_folder = self.config['videos_edit_folder']
    #     if not video_folder:
    #         warning_message("Please choose the videos edit folder")
    #         return
    #     if float(self.config['max_zoom_size']) < 1.1:
    #         self.config['max_zoom_size'] = "1.1"
    #     if float(self.config['max_zoom_size']) > 1.5:
    #         warning_message("The maximum value of max_zoom_size is 1.5")
    #         return
        
    #     if int(self.config['min_time_to_change_zoom']) < 3:
    #         self.config['min_time_to_change_zoom'] = 3
    #     if int(self.config['max_time_to_change_zoom']) < 5:
    #         self.config['max_time_to_change_zoom'] = "5"
    #     self.save_config()
    #     edit_videos = os.listdir(video_folder)

    #     for i, video_file in enumerate(edit_videos):
    #         if '.mp4' not in video_file:
    #             continue
    #         video_path = f'{video_folder}\\{video_file}'
    #         is_edit_ok = self.edit_video(video_path)
    #         if is_edit_ok:
    #             print(f"Edited finish video {video_file}")
    #     cnt = len(self.list_edit_finished)
    #     if cnt > 0:
    #         notification(f"Successfully edited {cnt} files: {self.list_edit_finished}")

    # def edit_video_169(self, input_video_path):
    #     self.hide_window()
    #     try:
    #         if int(self.config['quantity_split']) > 1:
    #             quantity_split = int(self.config['quantity_split'])
    #         else:
    #             quantity_split = 1

    #         output_directory = f'{os.path.dirname(input_video_path)}\\output_folder'
    #         file_name = get_file_name_from_path(input_video_path, suffix=False)
    #         file_name = convert_sang_tieng_viet_khong_dau(file_name)
    #         os.makedirs(output_directory, exist_ok=True)
            
    #         input_clip = VideoFileClip(input_video_path)
    #         resized_clip = resize_clip(input_clip)
    #         if self.config['flip_video']:
    #             f_clip = flip_clip(resized_clip)
    #         else:
    #             f_clip = resized_clip
    #         clip_duration = f_clip.duration
    #         video = strip_first_and_end_video(f_clip, first_cut=self.config['first_cut'], end_cut=self.config['end_cut'])
    #         if not video:
    #             return
    #         if os.path.isfile(self.config['background_music_path']):
    #             add_audio_clip = set_audio_for_clip(video, self.config['background_music_path'], self.config['background_music_volume'])
    #         else:
    #             add_audio_clip = video
    #         speed_clip = speed_up_clip(add_audio_clip, speed=self.config['speed_up'])
    #         if self.config['is_random_zoom']:
    #             zoom_clip = zoom_video_random_intervals(clip=speed_clip, max_zoom_size=self.config['max_zoom_size'], min_time_to_change_zoom=self.config['min_time_to_change_zoom'], max_time_to_change_zoom=self.config['max_time_to_change_zoom'], vertical_position=self.config['vertical_position'], horizontal_position=self.config['horizontal_position'])
    #         else:
    #             zoom_clip = apply_zoom(clip=speed_clip, zoom_factor=self.config['max_zoom_size'], vertical_position=self.config['vertical_position'], horizontal_position=self.config['horizontal_position'])
    #         clip_duration = zoom_clip.duration
            
    #         one_clip_duration = clip_duration / quantity_split

    #         for i in range(quantity_split):
    #             if i == 0:
    #                 start_time = 0
    #             else:
    #                 start_time = i * one_clip_duration - 3
    #             end_time = min((i + 1) * one_clip_duration, clip_duration)
    #             one_clip = zoom_clip.subclip(start_time, end_time)
    #             output_file = os.path.join(output_directory, f"{file_name}_{i + 1}.mp4")

    #             one_clip.write_videofile(output_file, codec='libx264', fps=24)
    #             one_clip.close()
    #             self.list_edit_finished.append(input_video_path)
    #         return True
    #     except Exception as e:
    #         getlog()
    #         return False

#---------------------------------------------------------------------Các Hàm common
    def open_common_settings(self):
        pass

    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.4, right=0.6, add_combobox = False):
        frame = self.create_frame()
        self.create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')

        if values:
            val = self.config[config_key]
            if self.config[config_key] == True:
                val = "Yes"
            elif self.config[config_key] == False:
                val = "No"
            var = ctk.StringVar(value=str(val))

            combobox = ctk.CTkComboBox(frame, values=values, variable=var, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            if config_key == "category_id":
                combobox.set(val[0])
            setattr(self, f"{config_key}_var", var)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", self.config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            var = self.config[config_key]
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            return entry
#------------------------------------------------------------------------------------------------------------------------------

    def translate_to_vi(self, original):
        if original:
            original = original.strip().lower()
            if "_" in original:
                original = original.replace("_", " ")
            if "-" in original:
                original = original.replace("-", " ")
            try:
                translation = self.translator.translate(original)
                translation = re.sub(r"\(.*?\)", "", translation)
                return original, translation
            except Exception as e:
                print(f"An error occurred during translation: {e}")
                return None, None
        else:
            return None, None
        

#--------------------------------------------------------------------------------------------------------------------------------------
    def reset(self):
        self.is_setting = False
        self.is_youtube_window = False
        self.is_tiktok_window = False
        self.is_facebook_window= False
        self.is_edit_video_window= False
        self.is_edit_video_window= False
        self.clear_after_action()
        self.clear_widgets()

    def clear_after_action(self):
        self.root.withdraw()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()

    def create_button_icon( self, frame = None, command=None, image=None, side=None, width=60):
        button = ctk.CTkButton( master=frame, text="", command=command, image=image, width=width)
        if side:
            button.pack(side=side, padx=0, pady=0)
        else:    
            button.pack(padx=0, pady=0)
        return button
    def create_button( self, frame = None, text="", command=None, width=0, height=height_element, compound="left", anchor="center", image=None, side=None, pady=pady, padx=padx):
        if width == 0:
            width = self.width
        if frame:
            button = ctk.CTkButton( frame, text=text, command=command, image=image, font=self.font_button, width=width, height= height_element, compound=compound, anchor=anchor, )
        else:
            button = ctk.CTkButton( self.root, text=text, command=command, image=image, font=self.font_button, width=width, height= height_element, compound=compound, anchor=anchor, )
        if side:
            button.pack(side=side, pady=pady, padx=padx)
        else:    
            button.pack(pady=pady, padx=padx)
        return button

    def create_label( self, frame=None, text="", compound="center", anchor="w", width=None, height=height_element, wraplength=None, side=None):
        if not width:
            width = self.width
        wraplength = max(400, self.text_show_width - 20)
        if frame:
            label = ctk.CTkLabel( frame, text=text, font=self.font_label, width=width, height= height_element, wraplength=wraplength, anchor=anchor, compound=compound)
        else:
            label = ctk.CTkLabel( self.root, text=text, font=self.font_label, width=width, height= height_element, wraplength=wraplength, anchor=anchor, compound=compound)
        if side:
            label.pack(side=side, pady=pady, padx=padx)
        else:
            label.pack(pady=pady, padx=padx)
        return label

    def create_frame(self, fill='x', side=None):
        frame = ctk.CTkFrame(self.root, height=height_element*0.9)
        frame.pack(padx=padx, pady=pady, fill=fill, side=side)
        return frame

    def create_text_input(self, frame, width=None, placeholder=None, side="right", default=""):
        if not width:
            width = self.width
        text_input = ctk.CTkEntry(master=frame, width=width, height=height_element*0.8, placeholder_text=placeholder, textvariable=default)
        text_input.pack(pady=pady, padx=padx, side=side)
        return text_input
    
    def create_frame_label_input_input(self, label_text="", place_holder1=None, place_holder2=None, left=0.3, mid=0.575, right=0.125):
        frame = self.create_frame()
        label = self.create_label(frame=frame, text=label_text, side=LEFT, width=self.width*left, compound=LEFT, anchor='w')
        entry1 = self.create_text_input(frame=frame, width=self.width*mid, placeholder=place_holder1, side=RIGHT)
        entry2 = self.create_text_input(frame=frame, width=self.width*right, placeholder=place_holder2)
        return entry1, entry2
    def create_frame_label_and_input(self, label_text="", place_holder=None, left=left, right=right):
        frame = self.create_frame()
        label = self.create_label(frame=frame, text=label_text, side=LEFT, width=self.width*left, compound=LEFT, anchor='center')
        entry = self.create_text_input(frame=frame, width=self.width*right, placeholder=place_holder)
        return entry
    def create_frame_label_and_progress_bar(self, frame, label_text="", left=left, right=right):
        label = self.create_label(frame=frame, text=label_text, side=LEFT, width=self.width*left, compound=LEFT)
        processbar = self.create_progress_bar(frame=frame, width=self.width*right, side=RIGHT)
        return frame, processbar
    def create_progress_bar(self, frame=None, width=None):
        if not frame:
            frame = self.root
        if not width:
            width = self.width
        processbar = ctk.CTkProgressBar(master=frame, width=width)
        processbar.pack(padx=padx, pady=pady)
        return processbar
    def create_frame_button_input_input(self, text, place_holder1=None, place_holder2=None, command=None, left=0.25, mid=0.575, right=0.165):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        entry1 = self.create_text_input(frame, width=self.width*mid, placeholder=place_holder1, side=RIGHT)
        entry2 = self.create_text_input(frame, width=self.width*right, placeholder=place_holder2)
        return entry1, entry2
    def create_frame_button_and_input(self, text, place_holder=None, command=None, left=left, right=right):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        entry = self.create_text_input(frame, width=self.width*right, placeholder=place_holder)
        return entry
    def create_frame_button_and_combobox(self, text, command=None, values=None, variable=None, left=left, right=right):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        combobox = self.create_combobox(frame, width=self.width*right, side=RIGHT, values=values, variable=variable)
        return combobox
    def create_frame_button_and_button(self, text1, text2, command1=None, command2=None, left=left, right=right):
        frame = self.create_frame()
        button1 = self.create_button(frame=frame, text=text1, width=self.width*left , side=LEFT, command=command1)
        button2 = self.create_button(frame=frame, text=text2, width=self.width*right -15, side=RIGHT, command=command2)
        return button1, button2
    
    def load_translate(self):
        from_language = self.config["from_language"]
        to_language = self.config["to_language"]
        self.translator = Translator(from_lang=from_language,to_lang=to_language)
        self.selected_translate_from = ctk.StringVar(value=self.languages[from_language])
        self.selected_translate_to = ctk.StringVar(value=self.languages[to_language])
        if not self.engine:
            self.engine = pyttsx3.init()
        self.voices = self.engine.getProperty('voices')
        self.get_voice()

    def load_data_with_new_config(self):
        self.load_translate()
        
    def save_config(self):
        save_to_json_file(self.config, self.config_path)
        self.load_data_with_new_config()
        
    def create_icon(self):
        try:
            # icon_path = get_file_path("icon.png")
            icon_path = os.path.join(current_dir, 'icon.png')
            if not os.path.exists(icon_path):
                icon_path = None

            image = self.create_image(icon_path)
            menu = (
                item("Open Menu", self.get_start_window),
                item("Exit", self.exit_app),
            )
            self.icon = pystray.Icon("Smart Reminder", image, "Smart Reminder", menu)
            tray_thread = threading.Thread(target=self.icon.run_detached)
            tray_thread.daemon = True
            tray_thread.start()
        except:
            getlog()

    def create_image(self, icon_path=None):
        if icon_path:
            image = Image.open(icon_path)
        else:
            width = 64
            height = 64
            image = Image.new("RGB", (width, height), (255, 255, 255))
            dc = ImageDraw.Draw(image)
            dc.rectangle( (width // 2 - 10, height // 2 - 10, width // 2 + 10, height // 2 + 10), fill=(0, 0, 0), )
        return image

    def exit_app(self):
        self.reset()
        self.icon.stop()
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", 1)
        self.root.attributes("-topmost", 0)

    def hide_window(self):
        self.root.iconify()
        self.root.withdraw()  # ẩn cửa sổ

    def on_close(self):
        self.save_config()
        self.hide_window()

    def setting_screen_position(self):
        try:
            self.root.update_idletasks()
            x = screen_width - self.width - 10
            y = screen_height - self.height_window
            self.root.geometry(f"{self.width}x{self.height_window - 80}+{x}+{y}")
        except:
            getlog()

    def setting_window_size(self):
        if self.is_start_app:
            self.width = 500
            self.height_window = 570
        else:
            if self.is_setting:
                self.root.title("Setting")
                self.width = 300
                self.height_window = 600
                self.is_setting = False
            # elif self.is_edit_video_window:
            #     self.root.title("Edit Videos 16:9")
            #     self.width = 500
            #     self.height_window = 950
            #     self.is_edit_video_window = False
            elif self.is_edit_video_window:
                self.root.title("Edit Videos 9:16")
                self.width = 800
                self.height_window = 1080
                self.is_edit_video_window = False
            elif self.is_edit_audio_window:
                self.root.title("Edit Audio")
                self.width = 500
                self.height_window = 550
                self.is_edit_audio_window = False
            else:
                self.width = 500
                self.height_window = 500
        self.setting_screen_position()
    # Hàm để thêm ứng dụng vào danh sách khởi động cùng Windows
    def set_autostart(self):
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
    def unset_autostart(self):
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

    def open_text_to_mp3_window(self):
        self.reset()
        self.is_text_to_speech = True
        self.setting_window_size()
        self.is_text_to_speech = False
        self.create_button(text="Choose place to save the file", command= self.choose_directory_save_mp3_file)
        self.create_button(text="Choose file want to convert", command= self.choose_directory_get_txt_file)
        self.create_button(text="Convert line by line to mp3", command= self.convert_line_by_line_to_mp3)
        self.create_button(text="convert", command= self.text_to_mp3)
        self.show_window()

    def choose_directory_save_mp3_file(self):
        save_path = filedialog.askdirectory()
        self.file_path_save = f'{save_path}'

    def choose_directory_get_txt_file(self):
        self.file_path_get = filedialog.askopenfilename( title="Select a txt file", filetypes=(("Text files", "*.txt"),)) #(("Text files", "*.txt"),)

    def convert_line_by_line_to_mp3(self):
        self.convert_multiple_record = True

    
    def text_to_mp3(self, voice=None, convert_multiple_record= False):
        if not self.file_path_save:
            messagebox.showinfo( "ERROR", f"Hãy chọn thư mục để lưu file mp3", )
            return
        if not self.file_path_get:
            messagebox.showinfo( "ERROR", f"Hãy chọn file để lấy dữ liệu muốn convert", )
            return
        try:
            if not self.engine:
                self.engine = pyttsx3.init()
            if voice:
                self.engine.setProperty('voice', voice)
            self.engine.setProperty('rate', self.config['speed_talk'] * 150)
            text = get_txt_data(self.file_path_get)
            lines = text.split('\n')
            total_line = len(lines)
            if self.convert_multiple_record:
                for i in range(1, total_line):
                    temp_wav_file = f"{current_dir}\\temp_output{i}"
                    row = lines[i-1].split('\t')
                    correct = row[5]
                    last = row[6]
                    row.remove(correct)
                    row.remove(last)
                    line_row = "!".join(row)
                    lines1=[line_row, correct, last]
                    for j in range(0,3):
                        temp_file = f'{temp_wav_file}_{j}.wav'
                        self.engine.save_to_file(lines1[j], temp_file)
                        self.engine.runAndWait()
                        # Chuyển đổi file WAV sang file MP3
                        sound = AudioSegment.from_wav(temp_file)
                        sound.export(f'{self.file_path_save}\\output{i}_{j}.mp3', format="mp3")
                        os.remove(temp_file)

                    
            else:
                # Lưu giọng nói vào file WAV tạm thời
                temp_wav_file = f"{current_dir}\\temp_output.wav"
                text = text.strip()
                self.engine.save_to_file(text, temp_wav_file)
                self.engine.runAndWait()
                # Chuyển đổi file WAV sang file MP3
                sound = AudioSegment.from_wav(temp_wav_file)
                sound.export(self.file_path_save, format="mp3")
            
                # Xóa file WAV tạm thời
                os.remove(temp_wav_file)
                print(f"File mp3 đã được lưu thành công: {self.file_path_save}")

        except:
            getlog()
            self.engine.stop()
            if os.path.isfile(temp_wav_file):
                os.remove(temp_wav_file)
        self.convert_multiple_record =False
        self.hide_window()

    def get_voice(self):
        voice_from_language_code = self.config["from_language"]
        voice_to_language_code = self.config["to_language"]
        voice_name_from_language_config = self.config["supported_languages"][voice_from_language_code]
        voice_name_to_language_config = self.config["supported_languages"][voice_to_language_code]

        if '(' in voice_name_from_language_config:
            vv = voice_name_from_language_config.split('(')[0].strip().lower()
        else:
            vv = voice_name_from_language_config.strip().lower()

        if '(' in voice_name_to_language_config:
            v = voice_name_to_language_config.split('(')[0].strip().lower()
        else:
            v = voice_name_to_language_config.strip().lower()

        self.all_voice_index = {}

        for voice in self.voices:
            voice_name_engine = voice.name.lower()
            if voice_name_to_language_config.lower() in voice_name_engine or v in voice_name_engine:
                index = self.voices.index(voice)
                self.all_voice_index[voice_to_language_code] = index
            if voice_from_language_code.lower() in voice_name_engine or vv in voice_name_engine:
                index = self.voices.index(voice)
                self.all_voice_index[voice_from_language_code] = index

        if voice_from_language_code not in self.all_voice_index:
            messagebox.askquestion("Warning", f"Hãy cài giọng nói {voice_name_from_language_config} cho window trước\nSetting --> Time & Language --> Language & Region --> Add a language")
            return
        if voice_to_language_code not in self.all_voice_index:
            messagebox.askquestion("Warning", f"Hãy cài giọng nói {voice_name_to_language_config} cho window trước\nSetting --> Time & Language --> Language & Region --> Add a language")
            return
        self.voice_to_language = self.all_voice_index[self.config["to_language"]]
        self.voice_from_language = self.all_voice_index[self.config["from_language"]]

app = MainApp()
try:
    app.root.mainloop()
except:
    getlog()
