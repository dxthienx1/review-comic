from common_function import *
from common_function_CTK import *
from Common import *
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from tiktok import TikTokManager
from facebook import FacebookManager
from youtube import YouTubeManager

class MainApp:
    def __init__(self):
        try:
            self.root = ctk.CTk()
            self.root.title("Super App")
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.lock = threading.Lock()
            self.download_thread = threading.Thread()
            self.upload_thread = threading.Thread()
            self.edit_thread = threading.Thread()
            self.config = load_config()
            self.youtube_config = load_youtube_config()
            load_tiktok_config()
            load_facebook_config()
            self.youtube = None
            self.is_youtube_window = False
            self.is_sign_up_youtube = False
            self.tiktok = None
            self.is_tiktok_window = False
            self.is_sign_up_tiktok = False
            self.facebook = None
            self.is_sign_up_facebook = False
            self.is_facebook_window = False

            self.engine = pyttsx3.init()
            self.voices = []
            self.all_voice_index = {}

            remove_file("log.txt")
            #kiem tra quota
            time_remaining = get_time_remaining_until_quota_reset()
            print(f"thời gian reset quota là {time_remaining/3600} giờ")
            self.next_time_check_quocta = time() + time_remaining

            self.thread_main = None
            self.icon = None
            self.translator=None
            self.languages = self.config["supported_languages"]
            self.convert_multiple_record = False
            self.load_translate()

            self.is_start_app = True
            self.is_setting = False
            self.is_edit_video_window = False
            self.is_edit_audio_window = False
            self.is_open_edit_video_menu = False
            self.is_open_common_setting = False
            self.is_169_to_916 = True

            self.is_editing_video = False
            self.is_auto_upload_youtube = False
            self.is_add_new_channel = False
            self.is_setting_auto_upload = False
            self.pre_time_check_auto_upload = 0
            self.is_stop_edit = False

            self.start_main_check_thread()
            self.setting_window_size()
            self.create_icon()
            self.get_start_window()

            if self.config["auto_start"]:
                set_autostart()
            else:
                unset_autostart()
        except:
            getlog()
#------------------------------------------------main thread----------------------------------------------------
    def start_main_check_thread(self):
            self.thread_main = threading.Thread(target=self.main_check_thread)
            self.thread_main.daemon = True  # Để thread kết thúc khi chương trình chính kết thúc
            self.thread_main.start()

    def main_check_thread(self):
        while True:
            try:
                self.check_quota_reset()
                self.auto_upload_every_day()
                sleep(5)
            except:
                getlog()
    def check_process_status(self):
        if self.youtube:
            if self.youtube.is_stop_download:
                self.youtube.download_thread.join()
    def auto_upload_every_day(self):
        try:
            if time() - self.pre_time_check_auto_upload >= 30:
                self.pre_time_check_auto_upload = time()
                if self.is_auto_upload_youtube:
                    self.config = get_json_data(config_path)
                    auto_channel_name = self.config['registered_channel']
                    for channel_name in auto_channel_name: #những channel muốn chạy auto
                        self.get_youtube_config()
                        if channel_name in self.youtube_config:
                            current_time = datetime.now()
                            current_date_str = current_time.strftime('%Y-%m-%d')
                            if 'last_auto_upload_date' not in self.youtube_config['template'][channel_name]:
                                self.youtube_config['template'][channel_name]['last_auto_upload_date'] = ""
                            last_auto_upload_date_str = self.youtube_config['template'][channel_name]['last_auto_upload_date'] #yyyy-mm-dd
                            if current_date_str != last_auto_upload_date_str:
                                gmail = self.youtube_config['template'][channel_name].get('gmail', None)
                                if not gmail:
                                    continue 
                                oauth_path = f'app.py-{gmail}-{channel_name}.json'
                                if os.path.isfile(oauth_path):
                                    
                                    print(f"đang check auto upload channel {channel_name} ...")
                                    recent_upload_date_str = self.youtube_config['template'][channel_name].get('start_date')
                                    recent_upload_date = None
                                    if recent_upload_date_str:
                                        recent_upload_date = datetime.strptime(recent_upload_date_str, '%Y-%m-%d')
                                    else:
                                        recent_upload_date = current_time
                                    next_upload_date = recent_upload_date + timedelta(days=1)
                                    if next_upload_date <= current_time:
                                        next_upload_date = current_time
                                    # Cập nhật lại ngày đăng tiếp theo trong thông tin YouTube
                                    self.youtube_config['template'][channel_name]['start_date'] = next_upload_date.strftime('%Y-%m-%d')
                                    self.save_youtube_config()
                                    
                                    auto_youtube= YouTubeManager(self.config, gmail, channel_name, is_auto_upload=True)
                                    rp = auto_youtube.schedule_videos()
                                    if rp:
                                        self.youtube_config['template'][channel_name]['last_auto_upload_date'] = current_date_str
                                        self.save_youtube_config()
                                    else:
                                        warning_message(f"Có lỗi trong quá trình đăng video cho kênh {channel_name}")
                            else:
                                print(f"Hôm nay đã đăng video tự dộng cho kênh {channel_name}")
                    # self.is_auto_upload_youtube = False
        except:
            getlog()
                
            
    def check_quota_reset(self):
        if time() - self.next_time_check_quocta >= 0:
            self.is_auto_upload_youtube = True
            for gmail in self.config['registered_gmails']:
                if self.youtube:
                    if gmail in self.youtube:
                        self.youtube.is_quotaExceeded = False
                        self.config[gmail]['cnt_request_upload'] = 0
            self.save_config()
#------------------------------------------------
    def get_tiktok_config(self):
        self.tiktok_config = get_json_data(tiktok_config_path)
        if not self.tiktok_config:
            self.tiktok_config = {}
        if 'template' not in self.tiktok_config:
            self.tiktok_config['template'] = {}
        if 'registered_account' not in self.tiktok_config:
            self.tiktok_config['registered_account'] = []

    def get_facebook_config(self):
        self.facebook_config = get_json_data(facebook_config_path)
        if not self.facebook_config:
            self.facebook_config = {}
        if 'template' not in self.facebook_config:
            self.facebook_config['template'] = {}
        if 'registered_account' not in self.facebook_config:
            self.facebook_config['registered_account'] = []

    def save_youtube_config(self):
        save_to_json_file(self.youtube_config, youtube_config_path)

    def get_start_window(self):
        if not self.is_start_app:
            self.reset()
        self.show_window()
        self.is_start_app = True
        self.setting_window_size()
        self.is_start_app = False
        create_button(frame=self.root, text="Open YouTube Management", command=self.open_youtube_window)
        create_button(frame=self.root, text="Open Tiktok Management", command=self.open_tiktok_window)
        create_button(frame=self.root, text="Open Facebook Management", command=self.open_facebook_window)
        create_button(frame=self.root, text="Setting Auto Upload", command=self.setting_auto_upload)
        create_button(frame=self.root, text="Edit Videos", command=self.open_edit_video_menu)
        create_button(frame=self.root, text="Text To MP3", command=self.open_text_to_mp3_window)
        create_button(frame=self.root, text="Download And Edit Audio", command=self.open_edit_audio_window)
        create_button(frame=self.root, text="Common Settings", command=self.open_common_settings)

    def setting_auto_upload(self):
        self.reset()
        self.is_setting_auto_upload = True
        self.setting_window_size()
        self.show_window()
        create_button(frame=self.root, text="Auto upload Youtube", command=self.auto_upload_youtube)
        create_button(frame=self.root, text="Auto upload Tiktok", command=self.auto_upload_tiktok)
        create_button(frame=self.root, text="Auto upload Facebook", command=self.auto_upload_facebook)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)

    def auto_upload_youtube(self):
        self.is_auto_upload_youtube = True
        notification(f"Đã thiết lập tự động đăng video cho các kênh youtube")
    def auto_upload_tiktok(self):
        self.is_auto_upload_youtube = True
        notification(f"Đã thiết lập tự động đăng video cho các kênh tiktok")
    def auto_upload_facebook(self):
        self.is_auto_upload_youtube = True
        notification(f"Đã thiết lập tự động đăng video cho các trang facebook")

    def open_youtube_window(self):
        self.reset()
        self.is_youtube_window = True
        self.show_window()
        self.setting_window_size()
        self.input_gmail = self.create_settings_input("Choose Gmail Account", "current_youtube_account" ,values=list(set([self.youtube_config['template'][key]['gmail'] for key in self.youtube_config['template'].keys()])), left=0.4, right=0.6, add_button=True, text='Tìm channel', command=self.choose_a_youtube_channel)
        self.input_gmail.set(self.youtube_config['current_youtube_account'])
        if self.youtube_config['current_youtube_account']:
            values = [k for k,v in self.youtube_config['template'].items() if v.get('gmail') == self.youtube_config['current_youtube_account']]
        else:
            values = ['-------------------------']
        self.input_current_channel_name = self.create_settings_input("Choose Youtube Channel Id", "current_channel" ,values=values, left=0.4, right=0.6)
        self.input_current_channel_name.set(self.youtube_config['current_channel'])
        create_button(self.root, text="Start Youtube Management", command=self.start_youtube_management)
        create_button(self.root, text="Sign Up A Channel", command=self.add_new_channel)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)
    
    def choose_a_youtube_channel(self):
        current_youtube_account = self.input_gmail.get()
        channels_of_gmail = [k for k,v in self.youtube_config['template'].items() if v.get('gmail') == current_youtube_account]
        if len(channels_of_gmail) == 0:
            warning_message("Gmail này chưa đăng ký hoặc hết hạn.")
            return
        self.input_current_channel_name.configure(values=channels_of_gmail)
        self.input_current_channel_name.set(channels_of_gmail[0])

    def add_new_channel(self):
        self.reset()
        self.is_add_new_channel = True
        self.setting_window_size()
        self.show_window()
        self.input_gmail = create_frame_label_and_input(self.root, label_text="Gmail")
        self.input_current_channel_name = create_frame_label_and_input(self.root, label_text="Channel Name")
        create_button(frame=self.root, text="Submit And Verify Now", command=self.sign_up_youtube_channel)
        create_button(self.root, text="Back", command=self.open_youtube_window, width=self.width)
    
    def sign_up_youtube_channel(self):
        self.is_add_new_channel = True
        gmail = self.input_gmail.get().strip()
        channel_name = self.input_current_channel_name.get()
        if not gmail or not channel_name:
            warning_message("Please enter complete information!")
            return
        if '@gmail.com' not in gmail:
            warning_message("Không đúng định dạng gmail.")
            return
        if channel_name not in self.youtube_config['template']:
            self.youtube_config['template'][channel_name] = {}
        self.youtube_config['template'][channel_name]['gmail'] = gmail
        self.youtube_config['template'][channel_name]['title'] = ""
        self.youtube_config['template'][channel_name]['is_title_plus_video_name'] = True
        self.youtube_config['template'][channel_name]['description'] = ""
        self.youtube_config['template'][channel_name]['tags'] = ""
        self.youtube_config['template'][channel_name]['category_id'] = ""
        self.youtube_config['template'][channel_name]['privacy_status'] = "private"
        self.youtube_config['template'][channel_name]['license'] = "creativeCommon"
        self.youtube_config['template'][channel_name]['is_delete_video'] = False
        self.youtube_config['template'][channel_name]['start_date'] = ""
        self.youtube_config['template'][channel_name]['publish_times'] = ""
        self.youtube_config['template'][channel_name]['upload_folder'] = ""
        self.youtube_config['template'][channel_name]['last_auto_upload_date'] = ""
        self.start_youtube_management(channel_name)
        self.save_youtube_config()

    def start_youtube_management(self, channel_name=None):
        if self.is_add_new_channel:
            gmail = self.youtube_config['template'][channel_name]['gmail']
            self.is_add_new_channel = False
        else:
            gmail = self.input_gmail.get().strip()
            channel_name = self.input_current_channel_name.get().strip()
            if not gmail or not channel_name:
                warning_message("Hãy nhập đủ thông tin!")
            if channel_name not in self.youtube_config['template'].keys():
                warning_message("Channel này chưa đăng ký!")
                return
            if gmail not in self.config['registered_gmails']:
                warning_message("Gmail này chưa đăng ký!")
                return

        self.youtube_config['current_youtube_account'] = gmail
        self.youtube_config['current_channel'] = channel_name
        self.save_youtube_config()
        self.reset()
        self.youtube = YouTubeManager(gmail, channel_name, is_auto_upload=False, lock=self.lock, download_thread=self.download_thread, upload_thread=self.upload_thread)
        self.youtube.get_start_youtube()
    
    def open_tiktok_window(self):
        self.get_tiktok_config()
        self.reset()
        self.is_tiktok_window = True
        self.show_window()
        self.setting_window_size()
        self.tiktok_account_var = self.create_settings_input(label_text="Choose Gmail", config_key="current_tiktok_account", values=self.tiktok_config['registered_account'])
        create_button(self.root, text="Start Tiktok Management", command=self.start_tiktok_management)
        create_button(self.root, text="Sign Up A Account", command=self.sign_up_tiktok_window)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)

    def sign_up_tiktok_window(self):
        self.reset()
        self.is_sign_up_tiktok = True
        self.show_window()
        self.setting_window_size()
        def sign_up_tiktok():
            self.is_sign_up_tiktok = True
            self.tiktok_account = self.tiktok_account_var.get()
            self.tiktok_password = self.tiktok_password_var.get()
            if not self.tiktok_account or not self.tiktok_password:
                warning_message("Hãy nhập đầy đủ thông tin!")
                return
            if self.tiktok_account not in self.tiktok_config['template']:
                self.tiktok_config['template'][self.tiktok_account] = {}
            self.config['current_tiktok_account'] = self.tiktok_account
            self.tiktok_config['template'][self.tiktok_account]['account'] = self.tiktok_account
            self.tiktok_config['template'][self.tiktok_account]['password'] = self.tiktok_password
            self.tiktok_config['template'][self.tiktok_account]['upload_folder'] = ""
            self.tiktok_config['template'][self.tiktok_account]['publish_times'] = ""
            self.tiktok_config['template'][self.tiktok_account]['title'] = ""
            self.tiktok_config['template'][self.tiktok_account]['is_title_plus_video_name'] = False
            self.tiktok_config['template'][self.tiktok_account]['upload_date'] = datetime.now().strftime('%Y-%m-%d')
            self.tiktok_config['registered_account'].append(self.tiktok_account)
            save_to_json_file(self.tiktok_config, tiktok_config_path)
            self.start_tiktok_management()

        self.tiktok_account_var = create_frame_label_and_input(self.root, label_text="Input A tiktok Account")
        self.tiktok_password_var = create_frame_label_and_input(self.root, label_text="Input Password")
        create_button(self.root, text="Sign Up Now", command=sign_up_tiktok)
        create_button(self.root, text="Back", command=self.open_tiktok_window, width=self.width)

    def start_tiktok_management(self):
        self.tiktok_account = self.tiktok_account_var.get()
        if not self.is_sign_up_tiktok:
            if self.tiktok_account not in self.tiktok_config['registered_account'] or self.tiktok_account not in self.tiktok_config['template']:
                warning_message("Account này chưa đăng ký")
                return
        self.config['current_tiktok_account'] = self.tiktok_account
        self.tiktok_password = self.tiktok_config['template'][self.tiktok_account]['password']
        self.save_config()
        self.reset()
        self.setting_window_size()
        self.tiktok = TikTokManager(self.tiktok_account, self.tiktok_password, self.upload_thread)
        self.tiktok.get_start_tiktok()

    def open_facebook_window(self):
        self.get_facebook_config()
        self.reset()
        self.is_facebook_window = True
        self.show_window()
        self.setting_window_size()
        self.facebook_account_var = self.create_settings_input(label_text="Choose Gmail", config_key="current_facebook_account", values=self.facebook_config['registered_account'])
        self.facebook_page_name_var = self.create_settings_input(label_text="Choose Page Name", config_key="current_page", values=[key for key in self.facebook_config['template'].keys()])
        create_button(self.root, text="Start Facebook Management", command=self.start_facebook_management)
        create_button(self.root, text="Sign Up A Account", command=self.sign_up_facebook_window)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)

    def sign_up_facebook_window(self):
        self.reset()
        self.is_sign_up_facebook = True
        self.show_window()
        self.setting_window_size()
        def sign_up_facebook():
            self.is_sign_up_facebook = True
            self.facebook_account = self.facebook_account_var.get()
            self.facebook_password = self.facebook_password_var.get()
            self.facebook_page_name = self.facebook_page_name_var.get()
            if not self.facebook_account or not self.facebook_password or not self.facebook_page_name:
                warning_message("Please input full infomation!")
                return
            if self.facebook_page_name not in self.facebook_config['template']:
                self.facebook_config['template'][self.facebook_page_name] = {}
            self.config['current_facebook_account'] = self.facebook_account
            self.config['current_page'] = self.facebook_page_name
            self.facebook_config['template'][self.facebook_page_name]['account'] = self.facebook_account
            self.facebook_config['template'][self.facebook_page_name]['password'] = self.facebook_password
            self.facebook_config['template'][self.facebook_page_name]['upload_folder'] = ""
            self.facebook_config['template'][self.facebook_page_name]['publish_times'] = ""
            self.facebook_config['template'][self.facebook_page_name]['title'] = ""
            self.facebook_config['template'][self.facebook_page_name]['is_title_plus_video_name'] = False
            self.facebook_config['template'][self.facebook_page_name]['upload_date'] = datetime.now().strftime('%Y-%m-%d')
            save_to_json_file(self.facebook_config, facebook_config_path)
            self.start_facebook_management()

        self.facebook_account_var = create_frame_label_and_input(self.root, label_text="Input A Facebook Account")
        self.facebook_password_var = create_frame_label_and_input(self.root, label_text="Input Password")
        self.facebook_page_name_var = create_frame_label_and_input(self.root, label_text="Input A Page Name")
        create_button(self.root, text="Sign Up Now", command=sign_up_facebook)

    def start_facebook_management(self):
        self.facebook_page_name = self.facebook_page_name_var.get()
        self.facebook_account = self.facebook_account_var.get()
        if not self.is_sign_up_facebook:
            if not self.facebook_page_name or not self.facebook_account:
                warning_message("Please input full infomation!")
                return
            if self.facebook_page_name not in self.facebook_config['template']:
                warning_message("This page not registered!")
                return
            if self.facebook_account != self.facebook_config['template'][self.facebook_page_name]['account']:
                warning_message("Account not registered!")
                return
        self.config['current_facebook_account'] = self.facebook_account
        self.config['current_page'] = self.facebook_page_name
        self.save_config()
        self.reset()
        self.facebook_password = self.facebook_config['template'][self.facebook_page_name]['password']
        self.facebook = FacebookManager(self.facebook_account, self.facebook_password, self.facebook_page_name, self.download_thread, self.upload_thread)
        self.facebook.get_start_facebook()
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
        self.video_get_audio_url = create_frame_label_and_input(self.root, label_text="Get Audio From Video URL", left=0.4, right=0.6)
        self.audio_edit_path = create_frame_button_and_input(self.root,text="Edit Audio From MP3 File", command= self.choose_audio_edit_file, left=0.4, right=0.6)
        self.video_get_audio_path = create_frame_button_and_input(self.root,text="Get Audio From Video", command= self.choose_video_get_audio_path, left=0.4, right=0.6)
        self.choose_folder_download_var = create_frame_button_and_input(self.root,text="Choose Download Folder", command= self.choose_folder_download, left=0.4, right=0.6, width=self.width)
        self.choose_folder_download_var.insert(0, self.config['download_folder'])
        create_button(frame=self.root, text="Start Edit Audio", command=self.create_thread_edit_audio, padx=8)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)

    def choose_folder_download(self):
        folder = choose_folder()
        self.choose_folder_download_var.delete(0, ctk.END)
        self.choose_folder_download_var.insert(0, folder)
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
        download_folder = self.choose_folder_download_var.get()
        if not os.path.exists(download_folder):
            warning_message("hãy chọn thư mục lưu file tải về.")
            return
        audio_edit_path = self.audio_edit_path.get()
        video_get_audio_path = self.video_get_audio_path.get()
        video_get_audio_url = self.video_get_audio_url.get()
        if not audio_edit_path and not video_get_audio_path and not video_get_audio_url:
            warning_message("Hãy chọn 1 nguồn lấy audio")
            return
        if (audio_edit_path and video_get_audio_path) or (audio_edit_path and video_get_audio_url) or (video_get_audio_path and video_get_audio_url):
            warning_message("Chỉ chọn 1 nguồn lấy audio.")
            return
        def save_edit_audio_setting():
            self.config['download_folder'] = download_folder
            self.config['first_cut_audio'] = self.first_cut_audio_var.get()
            self.config['end_cut_audio'] = self.end_cut_audio_var.get()
            self.config['audio_speed'] = self.audio_speed_var.get()
            self.config['reversed_audio'] = self.reversed_audio_var.get() == 'Yes'
            self.config['audio_edit_path'] = audio_edit_path
            self.config['video_get_audio_path'] = video_get_audio_path
            self.config['video_get_audio_url'] = video_get_audio_url
        save_edit_audio_setting()
        self.save_config()
        edit_audio(audio_path=self.config['audio_edit_path'], video_path=self.config['video_get_audio_path'], video_url=self.config['video_get_audio_url'], speed=self.config['audio_speed'], first_cut_audio=self.config['first_cut_audio'], end_cut_audio=self.config['end_cut_audio'], reversed_audio=self.config['reversed_audio'], download_folder=self.config['download_folder'])

#---------------------------------------------------------------------edit video
    def open_edit_video_menu(self):
        self.reset()
        self.is_open_edit_video_menu = True
        self.show_window()
        self.setting_window_size()
        create_button(frame=self.root, text="Edit Videos 16:9", command=self.open_edit_video_window)
        create_button(frame=self.root, text="Edit Videos 9:16", command=self.open_edit_video_window)
        create_button(self.root, text="Convert Videos", command=self.convert_videos_window)
        create_button(self.root, text="Cut Video", command=self.cut_video_window)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)
    
    def cut_video_window(self):
        self.reset()
        self.is_cut_video_window =True
        self.show_window()
        self.setting_window_size()
        self.cut_by_quantity_var = self.create_settings_input(label_text="Enter Cutting Quantity", config_key="quantity_split", values=["1","2","3","4"], left=0.4, right=0.6)
        self.segments_var = self.create_settings_input(label_text="Enter Cutting Times", left=0.4, right=0.6)
        self.choose_is_connect_var = self.create_settings_input(label_text="Is Connect", values=["Yes", "No"], left=0.4, right=0.6)
        self.choose_is_connect_var.set(value="No")
        self.videos_folder_handle_path = create_frame_button_and_input(self.root, "Choose videos folder", width=self.width, command=self.choose_videos_edit_folder, left=0.4, right=0.6)
        self.videos_folder_handle_path.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Start Cut Video By Quantity", command=self.cut_videos_by_quantity)
        create_button(self.root, text="Start Cut Video By Times", command=self.cut_videos_by_timeline)
        create_button(self.root, text="Back", command=self.open_edit_video_menu, width=self.width)

    def convert_videos_window(self):
        self.reset()
        self.is_convert_video_window = True
        self.show_window()
        self.setting_window_size()
        self.choose_convert_type = self.create_settings_input(label_text="Choose Convert Type", config_key="convert_type", values=["16:9 to 9:16", "9:16 to 16:9"])
        self.choose_convert_type.set("16:9 to 9:16")
        self.choose_zoom_size = self.create_settings_input(label_text="Zoom Size (16:9 to 9:16)")
        self.videos_folder_handle_path = create_frame_button_and_input(self.root, "Choose videos folder", width=self.width, command=self.choose_videos_edit_folder, left=0.4, right=0.6)
        self.videos_folder_handle_path.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Start Convert Videos", width=self.width, command=self.start_convert_video)
        create_button(self.root, text="Back", command=self.open_edit_video_menu, width=self.width)
    

    def start_convert_video(self):
        convert_type = self.choose_convert_type.get()
        if convert_type == "16:9 to 9:16":
            self.is_169_to_916 = True
        elif convert_type == "9:16 to 16:9":
            self.is_169_to_916 = False
        else:
            warning_message("Convert type không đúng định dạng")
            return
        self.start_thread_edit_video()

    def start_thread_edit_video(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.is_stop_edit = False
            self.edit_thread = threading.Thread(target=self.convert_videos)
            self.edit_thread.start()

    def cut_videos_by_quantity(self):
        try:
            cut_quantity = self.cut_by_quantity_var.get()
            cut_quantity = int(cut_quantity)
            self.cut_videos_by_timeline(cut_quantity)
        except:
            getlog()

    def cut_videos_by_timeline(self, cut_quantity=None):
        if not cut_quantity:
            segments = self.segments_var.get()
            if not segments:
                warning_message("Hãy nhập các khoảng thời gian muốn cắt, ví dụ: 05:50,60:90,...")
                return
        videos_folder = self.videos_folder_handle_path.get()
        if not videos_folder:
            warning_message("Hãy chọn thư mục lưu video.")
            return
        self.config['videos_edit_folder'] = videos_folder
        self.save_config()
        is_connect = self.choose_is_connect_var.get() == "Yes"
        edit_videos = os.listdir(videos_folder)
        for k in edit_videos:
            if '.mp4' not in k:
                edit_videos.remove(k)
        if len(edit_videos) == 0:
            warning_message(f"Không tìm thấy video trong thư mục {videos_folder}")
            return
        list_edit_finished = []
        for i, video_file in enumerate(edit_videos):
            if '.mp4' not in video_file:
                continue
            video_path = f'{videos_folder}\\{video_file}'
            if self.is_stop_edit:
                return
            if cut_quantity:
                is_edit_ok = cut_video_by_quantity(video_path, cut_quantity)
            else:
                is_edit_ok = cut_video_by_timeline(video_path, segments=segments, is_connect=is_connect)
            if is_edit_ok:
                list_edit_finished.append(video_file)
        cnt = len(list_edit_finished)
        if cnt > 0:
            notification(f"Xử lý thành công {cnt} video: {list_edit_finished}")

    def convert_videos(self):
        zoom_size = self.choose_zoom_size.get()
        videos_folder = self.videos_folder_handle_path.get()
        if not videos_folder:
            warning_message("Hãy chọn thư mục lưu video.")
            return
        self.config['videos_edit_folder'] = videos_folder
        self.save_config()
        edit_videos = os.listdir(videos_folder)
        for k in edit_videos:
            if '.mp4' not in k:
                edit_videos.remove(k)
        if len(edit_videos) == 0:
            warning_message(f"Không tìm thấy video trong thư mục {videos_folder}")
            return
        list_edit_finished = []
        for i, video_file in enumerate(edit_videos):
            if self.is_stop_edit:
                return
            if '.mp4' not in video_file:
                continue
            video_path = f'{videos_folder}\\{video_file}'
            if self.is_169_to_916:
                # is_edit_ok = convert_video_169_to_916_test(video_path, zoom_size=zoom_size)
                is_edit_ok = convert_video_169_to_916(video_path, zoom_size=zoom_size)
            else:
                is_edit_ok = convert_video_916_to_169(video_path)
            if is_edit_ok:
                list_edit_finished.append(video_file)
        cnt = len(list_edit_finished)
        if cnt > 0:
            notification(f"Xử lý thành công {cnt} video: {list_edit_finished}")

    def open_edit_video_window(self):
        self.reset()
        self.is_edit_video_window = True
        self.setting_window_size()
        self.show_window()
        self.file_name_var, self.start_index_var = create_frame_label_input_input(self.root, label_text="Batch file naming by index", width=self.width, place_holder1="Input file name containing the string <index>", place_holder2="start index")
        # self.quantity_split_var = self.create_settings_input("Quantity split", "quantity_split", values=["1", "2", "3", "4", "5"])
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
        self.background_music_path, self.background_music_volume_var = create_frame_button_input_input(self.root,text="Choose background music", width=self.width, command= self.choose_background_music, place_holder1="background music path", place_holder2="Volume")
        self.water_path_var = create_frame_button_and_input(self.root,text="Choose WaterMask Image", width=self.width, command= self.choose_water_mask_image, left=0.4, right=0.6)
        self.vertical_watermask_position_var = self.create_settings_input("Vertical Watermask Position", "vertical_watermask_position", values=["top", "center", "bottum"])
        self.horizontal_watermask_position_var = self.create_settings_input("Horizontal Watermask Position", "horizontal_watermask_position", values=["left", "center", "right"])
        self.videos_folder_handle_path = create_frame_button_and_input(self.root,text="Choose videos Edit folder", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        self.background_music_path.insert(0, self.config['background_music_path'])
        self.background_music_volume_var.insert(0, self.config['background_music_volume'])
        self.water_path_var.insert(0, self.config['water_path'])
        self.videos_folder_handle_path.insert(0, self.config['videos_edit_folder'])
        create_button(frame=self.root, text="Start Edit Videos", command=self.create_thread_edit_video, width=self.width)
        create_button(self.root, text="Back", command=self.open_edit_video_menu, width=self.width)

    def create_thread_edit_video(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.list_edit_finished = []
            self.edit_thread = threading.Thread(target=self.start_edit_video)
            self.edit_thread.start()

    def start_edit_video(self):
        def save_edit_setting():
            self.config['videos_edit_folder'] = self.videos_folder_handle_path.get()
            self.config['is_delete_original_audio'] = self.is_delete_original_audio_var.get() == "Yes"
            self.config['background_music_path'] = self.background_music_path.get()
            self.config['background_music_volume'] = self.background_music_volume_var.get()
            # self.config['quantity_split'] = self.quantity_split_var.get()
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
        videos_folder = self.config['videos_edit_folder']
        if not videos_folder:
            warning_message("Hãy chọn thư mục lưu video.")
            return
        if float(self.config['max_zoom_size']) < 1.05:
            self.config['max_zoom_size'] = "1.05"
        if float(self.config['max_zoom_size']) > 1.5:
            warning_message("The maximum value of max_zoom_size is 1.5")
            return

        self.save_config()
        self.index_file_name = self.file_name_var.get()
        if self.index_file_name and "<index>" not in self.index_file_name:
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
        
        edit_videos = os.listdir(videos_folder)
        for k in edit_videos:
            if '.mp4' not in k:
                edit_videos.remove(k)
        if len(edit_videos) == 0:
            warning_message(f"Không tìm thấy video trong thư mục {videos_folder}")
            return
        for i, video_file in enumerate(edit_videos):
            if self.is_stop_edit:
                return
            if '.mp4' not in video_file:
                continue
            index += 1
            video_path = f'{videos_folder}\\{video_file}'
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

            output_folder, output_file_path, file_name, finish_folder = get_output_folder(input_video_path)
            if not self.index_file_name:
                file_name = get_file_name_from_path(input_video_path, suffix=False)
                file_name = convert_sang_tieng_viet_khong_dau(file_name)
            else:
                file_name = self.index_file_name.replace("<index>", str(index))
            
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
                if self.is_stop_edit:
                    return
                if i == 0:
                    start_time = 0
                else:
                    start_time = i * one_clip_duration - 3
                end_time = min((i + 1) * one_clip_duration, clip_duration)
                one_clip = zoom_clip.subclip(start_time, end_time)
                final_clip = add_image_watermask_into_video(one_clip, top_overlay_height=self.config['top_height'], bot_overlay_height=self.config['bot_height'], watermask=self.config['water_path'], vertical_watermask_position=self.config['vertical_watermask_position'], horizontal_watermask_position=self.config['horizontal_watermask_position'])
                if final_clip:
                    if self.index_file_name:
                        output_file = os.path.join(output_folder, f"{file_name}.mp4")
                    else:
                        output_file = os.path.join(output_folder, f"{file_name}_{i + 1}.mp4")
                    if self.is_stop_edit:
                        final_clip.close()
                        return
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



#---------------------------------------------------------------------Các Hàm gọi chung
    def open_common_settings(self):
        self.reset()
        self.is_open_common_setting = True
        self.show_window()
        self.setting_window_size()
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)
        pass

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

    def create_settings_input(self, label_text, config_key=None, values=None, is_textbox = False, left=0.4, right=0.6, add_button=False, text=None, command=None):
        frame = create_frame(self.root)
        if add_button:
            create_button(frame= frame, text=text, command=command, width=0.2, side=RIGHT)
        create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')

        if values:
            if not config_key:
                val = ""
            elif config_key not in self.config:
                val = ""
            else:
                val = self.config[config_key]
                if self.config[config_key] == True:
                    val = "Yes"
                elif self.config[config_key] == False:
                    val = "No"
            var = ctk.StringVar(value=str(val))

            combobox = ctk.CTkComboBox(frame, values=values, variable=var, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            # combobox.set(val)
            if config_key == "category_id":
                combobox.set(val[0])
            setattr(self, f"{config_key}_var", var)
            result = combobox
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", self.config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            result = textbox
        else:
            if config_key:
                var = self.config[config_key]
            else:
                var = ""
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            result = entry
        return result
        

#------------------------------------------------------Common--------------------------------------------------------------------------------
    def reset(self):
        self.is_setting = False
        self.is_youtube_window = False
        self.is_tiktok_window = False
        self.is_facebook_window= False
        self.is_edit_video_window= False
        self.is_edit_video_window= False
        self.is_add_new_channel= False
        self.is_sign_up_facebook = False
        self.is_sign_up_tiktok = False
        self.is_convert_video_window = False
        self.is_open_common_setting = False
        self.is_cut_video_window = False
        self.clear_after_action()
        clear_widgets(self.root)

    def clear_after_action(self):
        self.root.withdraw()
    
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
        save_to_json_file(self.config, config_path)
        self.load_data_with_new_config()
        
    def create_icon(self):
        try:
            icon_path = os.path.join(current_dir, 'icon.png')
            if not os.path.exists(icon_path):
                icon_path = None

            image = self.create_image(icon_path)
            menu = (
                item("Open Menu", self.get_start_window),
                item("Stop Download", self.stop_download),
                item("Stop Upload", self.stop_upload),
                item("Stop All Process", self.stop_all_process),
                item("Exit", self.exit_app),
            )
            self.icon = pystray.Icon("Smart Reminder", image, "Smart Reminder", menu)
            tray_thread = threading.Thread(target=self.icon.run_detached)
            tray_thread.daemon = True
            tray_thread.start()
        except:
            getlog()

    def stop_download(self):
        if self.youtube:
            self.youtube.is_stop_download = True
        if self.facebook:
            self.facebook.is_stop_download = True
        if self.tiktok:
            self.tiktok.is_stop_download = True
    def stop_upload(self):
        if self.youtube:
            self.youtube.is_stop_upload = True
        if self.facebook:
            self.facebook.is_stop_upload = True
        if self.tiktok:
            self.tiktok.is_stop_upload = True

    def stop_all_process(self):
        self.stop_download()
        self.stop_upload()
        self.youtube = None
        self.facebook = None
        self.tiktok = None

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
            self.height_window = 435
        else:
            if self.is_setting:
                self.root.title("Setting")
                self.width = 300
                self.height_window = 600
                self.is_setting = False
            elif self.is_add_new_channel:
                self.root.title("Add New Youtube Channel")
                self.width = 500
                self.height_window = 270
            elif self.is_setting_auto_upload:
                self.root.title("Setting Auto Upload")
                self.width = 500
                self.height_window = 265
                self.is_setting_auto_upload = False
            elif self.is_open_common_setting:
                self.root.title("Common Setting")
                self.width = 500
                self.height_window = 300
                self.is_open_common_setting = False
            elif self.is_edit_video_window:
                self.root.title("Edit Videos 9:16")
                self.width = 700
                self.height_window = 1080
                self.is_edit_video_window = False
            elif self.is_edit_audio_window:
                self.root.title("Edit Audio")
                self.width = 500
                self.height_window = 550
                self.is_edit_audio_window = False
            elif self.is_open_edit_video_menu:
                self.root.title("Edit Video Window")
                self.width = 500
                self.height_window = 300
                self.is_open_edit_video_menu = False
            elif self.is_convert_video_window:
                self.root.title("Convert Videos Window")
                self.width = 500
                self.height_window = 460
                self.is_convert_video_window = False
            elif self.is_cut_video_window:
                self.root.title("Cut Video Window")
                self.width = 500
                self.height_window = 300
                self.is_cut_video_window = False
            elif self.is_youtube_window:
                self.root.title("Youtube Window")
                self.width = 500
                self.height_window = 320
                self.is_youtube_window = False
            elif self.is_facebook_window:
                self.root.title("Facebook Window")
                self.width = 500
                self.height_window = 310
                self.is_facebook_window = False
            elif self.is_sign_up_facebook:
                self.root.title("Sign Up")
                self.width = 500
                self.height_window = 300
                self.is_sign_up_facebook = False
            elif self.is_tiktok_window:
                self.root.title("Tiktok Window")
                self.width = 500
                self.height_window = 265
                self.is_tiktok_window = False
            elif self.is_sign_up_tiktok:
                self.root.title("Sign Up")
                self.width = 500
                self.height_window = 265
                self.is_sign_up_tiktok = False
            elif self.is_sign_up_youtube:
                self.root.title("Sign Up")
                self.width = 500
                self.height_window = 265
                self.is_sign_up_youtube = False
            else:
                self.width = 500
                self.height_window = 500
        self.setting_screen_position()

    def open_text_to_mp3_window(self):
        self.reset()
        self.is_text_to_speech = True
        self.setting_window_size()
        self.is_text_to_speech = False
        create_button(frame=self.root, text="Choose place to save the file", command= self.choose_directory_save_mp3_file)
        create_button(frame=self.root, text="Choose file want to convert", command= self.choose_directory_get_txt_file)
        create_button(frame=self.root, text="Convert line by line to mp3", command= self.convert_line_by_line_to_mp3)
        create_button(frame=self.root, text="convert", command= self.text_to_mp3)
        create_button(self.root, text="Back", command=self.get_start_window, width=self.width)
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
    #     self.background_music_path = create_frame_button_and_input(self.root,text="Choose background music", command= self.choose_background_music, left=0.4, right=0.6)
    #     self.background_music_volume_var = self.create_settings_input("Background music volume", "background_music_volume", values=["5", "10", "15"])
    #     self.videos_folder_handle_path = create_frame_button_and_input(self.root,text="Choose videos Edit folder", command= self.choose_videos_edit_folder, left=0.4, right=0.6)
    #     self.background_music_path.insert(0, self.config['background_music_path'])
    #     self.videos_folder_handle_path.insert(0, self.config['videos_edit_folder'])
    #     create_button(frame=self.root, text="Start Edit Videos", command=self.create_thread_edit_video)

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