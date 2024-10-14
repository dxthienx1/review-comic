from common_function_edit_video import *
from Common import *
from PIL import Image, ImageDraw
import pystray
from pystray import MenuItem as item
from tiktok import TikTokManager
from facebook import FacebookManager
from youtube import YouTubeManager
icon_path = os.path.join(current_dir, 'import' , 'icon.png')
ico_path = os.path.join(current_dir, 'import' , 'icon.ico')
mac_registered = {
    "0025_38D2_1104_730B.":{ #máy chính
        "telegram_user_name":"0915714682",
        "password":"123456",
        "expiration_date":"2025-09-19",
        "referral":""
    },
    "Z530FFSL":{ #cơ quan Hằng
        "telegram_user_name":"0367272579",
        "password":"123456",
        "expiration_date":"2025-09-19",
        "referral":""
    }
}
is_registed_mac_address = False
list_mac_registered = [mac for mac in mac_registered.keys()]

mac_address = get_disk_serial().strip()
if mac_address in list_mac_registered:
    expiration_date_str = mac_registered[mac_address]['expiration_date']
    if is_date_greater_than_current_day(expiration_date_str):
        is_registed_mac_address = True
        if is_date_greater_than_current_day(expiration_date_str, day_delta=-5):
            print(f'Tài khoản của bạn sẽ hết hạn vào ngày {expiration_date_str} lúc 00:00:00')

class MainApp:
    def __init__(self):
        try:
            self.root = ctk.CTk()
            self.root.title("Super App")
            if not os.path.exists(ico_path):
                if os.path.exists(icon_path):
                    image = Image.open(icon_path)
                    image.save(ico_path, format='ICO')
                    image.close()
            
            if os.path.exists(ico_path):
                self.root.iconbitmap(ico_path)

            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.download_thread = threading.Thread()
            self.upload_thread = threading.Thread()
            self.edit_thread = threading.Thread()
            self.edit_audio_thread = threading.Thread()
            self.config = load_config()
            self.youtube_config = load_youtube_config()
            self.tiktok_config = load_tiktok_config()
            self.facebook_config = load_facebook_config()
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
            self.thread_main = None
            self.icon = None
            self.translator=None
            self.languages = self.config["supported_languages"]
            self.convert_multiple_record = False
            # self.load_translate()
            self.load_download_info()
            self.is_start_app = True
            self.is_setting = False
            self.is_edit_video_window = False
            self.is_edit_audio_option = False
            self.is_extract_audio_option = False
            self.is_open_edit_video_menu = False
            self.is_open_common_setting = False
            self.is_other_window = False
            self.is_other_download_window = False
            self.is_download_douyin_video_window = False
            self.is_download_douyin_channel = False


            self.is_text_to_mp3_window = False
            self.is_edit_audio_window = False
            self.is_169_to_916 = True
            self.is_combine_video_window = False
            self.is_increse_video_quality_window = False
            self.is_rename_file_by_index_window = False
            self.is_remove_char_in_file_name_window = False
            self.is_open_register_mac_addres_window = False
            self.is_extract_image_from_video_window = False
            self.is_editing_video = False
            self.is_add_new_channel = False
            self.is_remove_channel = False
            self.pre_time_check_auto_upload_youtube = 0
            self.pre_time_check_auto_upload_facebook = 0
            self.pre_time_check_auto_upload_tiktok = 0
            self.is_stop_edit = False
            self.is_stop_download = False
            self.is_stop_upload = False
            self.driver = None
            self.start_main_check_thread()

            if is_registed_mac_address:
                self.setting_window_size()
                self.create_icon()
                self.get_start_window()

                if self.config["auto_start"]:
                    set_autostart()
                else:
                    unset_autostart()
            else:
                self.open_register_mac_addres_window()
        except:
            getlog()

#------------------------------------------------main thread----------------------------------------------------
    def start_main_check_thread(self):
            if self.is_start_app:
                self.config['time_check_auto_upload'] = "0"
                self.save_config()
            self.thread_main = threading.Thread(target=self.main_check_thread)
            self.thread_main.daemon = True
            self.thread_main.start()

    def main_check_thread(self):
        while True:
            try:
                if not self.upload_thread.is_alive() and not self.download_thread.is_alive() and not self.edit_thread.is_alive():
                    self.auto_upload_youtube()
                    self.auto_upload_facebook()
                    self.auto_upload_tiktok()
                sleep(30)
            except:
                getlog()
                sleep(500)

    def check_status_process(self):
        status = False
        if self.upload_thread.is_alive() or self.download_thread.is_alive() or self.edit_thread.is_alive():
            return True

    def auto_upload_youtube(self):
        try:
            time_check_cycle = get_time_check_cycle(self.config['time_check_auto_upload'])
            if time_check_cycle == 0:
                return
            if self.config['auto_upload_youtube']:
                if time() - self.pre_time_check_auto_upload_youtube >= time_check_cycle:
                    self.pre_time_check_auto_upload_youtube = time()
                    auto_channel_name = [channel for channel in self.youtube_config['template'].keys()]
                    for channel_name in auto_channel_name:
                        try:
                            if self.is_stop_upload:
                                return
                            self.get_youtube_config()
                            gmail = self.youtube_config['template'][channel_name].get('gmail', None)
                            videos_folder = self.youtube_config['template'][channel_name].get('upload_folder')
                            videos = get_file_in_folder_by_type(videos_folder, ".mp4", False)   
                            if not videos:
                                return
                            print(f"đang thực hiện đăng video tự động cho kênh {channel_name} ...")
                            if self.is_stop_upload:
                                return
                            auto_youtube= YouTubeManager(gmail, channel_name, is_auto_upload=True, upload_thread=self.upload_thread, download_thread=self.download_thread)
                            auto_youtube.schedule_videos_by_selenium()
                        except:
                            getlog()
                            print(f"Có lỗi trong quá trình đăng video tự động cho kênh {channel_name} !!!")
                        sleep(2)

        except:
            getlog()

    def auto_upload_facebook(self):
        try:
            time_check_cycle = get_time_check_cycle(self.config['time_check_auto_upload'])
            if time_check_cycle == 0:
                return
            if self.config['auto_upload_facebook']:
                if time() - self.pre_time_check_auto_upload_facebook >= time_check_cycle:
                    self.pre_time_check_auto_upload_facebook = time()
                    auto_page_name = [page for page in self.facebook_config['template'].keys()]
                    for page_name in auto_page_name:
                        try:
                            if self.is_stop_upload:
                                return
                            self.get_facebook_config()
                            videos_folder = self.facebook_config['template'][page_name].get('upload_folder')
                            videos = get_file_in_folder_by_type(videos_folder, ".mp4", False)   
                            if not videos:
                                return
                            print(f"đang thực hiện đăng video tự động cho trang {page_name} ...")
                            facebook_account = self.facebook_config['template'][page_name].get('account')
                            facebook_password = self.facebook_config['template'][page_name].get('password')
                            if self.is_stop_upload:
                                return
                            auto_facebook= FacebookManager(facebook_account, facebook_password, page_name, self.download_thread, self.upload_thread, is_auto_upload=True)
                            auto_facebook.upload_video()
                        except:
                            getlog()
                            print(f"Có lỗi trong quá trình đăng video tự động cho trang {page_name} !!!")
                        sleep(2)

        except:
            getlog()

    def auto_upload_tiktok(self):
        try:
            time_check_cycle = get_time_check_cycle(self.config['time_check_auto_upload'])
            if time_check_cycle == 0:
                return
            if self.config['auto_upload_tiktok']:
                if time() - self.pre_time_check_auto_upload_tiktok >= time_check_cycle:
                    self.pre_time_check_auto_upload_tiktok = time()
                    auto_tiktok_acc = [acc for acc in self.tiktok_config['template'].keys()]
                    for account in auto_tiktok_acc:
                        try:
                            if self.is_stop_upload:
                                return
                            self.get_tiktok_config()
                            videos_folder = self.youtube_config['template'][account].get('upload_folder')
                            videos = get_file_in_folder_by_type(videos_folder, ".mp4", False)   
                            if not videos:
                                return
                            print(f"đang thực hiện đăng video tự động cho tài khoản tiktok {account} ...")
                            tiktok_password = self.tiktok_config['template'][account].get('password')
                            if self.is_stop_upload:
                                return
                            auto_tiktok= TikTokManager(account, tiktok_password, self.download_thread, self.upload_thread, is_auto_upload=True)
                            auto_tiktok.upload_video()
                        except:
                            getlog()
                            print(f"Có lỗi trong quá trình đăng video tự động cho tài khoản tiktok {account} !!!")
                        sleep(2)
        except:
            getlog()
#-------------------------------------------Điều hướng window--------------------------------------------

    def get_start_window(self):
        if not is_registed_mac_address:
            self.noti('Vui lòng đăng ký mã máy trước khi sử dụng')
            return
        if not self.is_start_app:
            self.reset()
        self.show_window()
        self.is_start_app = True
        self.setting_window_size()
        self.is_start_app = False
        create_button(frame=self.root, text="Quản lý Youtube", command=self.open_youtube_window)
        create_button(frame=self.root, text="Quản lý Tiktok", command=self.open_tiktok_window)
        create_button(frame=self.root, text="Quản lý Facebook", command=self.open_facebook_window)
        create_button(frame=self.root, text="Xử lý video", command=self.open_edit_video_menu)
        create_button(frame=self.root, text="Xử lý audio", command=self.open_edit_audio_window)
        create_button(frame=self.root, text="Tải video từ link/các nền tảng khác", command=self.open_other_download_video_window)
        create_button(frame=self.root, text="Chức năng khác", command=self.other_function)
        create_button(frame=self.root, text="Cài đặt chung", command=self.open_common_settings)
    
    def open_other_download_video_window(self):
        def start_download_by_video_url():
            download_url = self.download_by_video_url.get()
            if not download_url:
                self.noti("Hãy nhập link video muốn tải trước.")
                return
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                self.download_thread = threading.Thread(target=self.download_video_by_video_url)
                self.download_thread.start()
        
        self.reset()
        self.is_other_download_window = True
        self.show_window()
        self.setting_window_size()
        self.is_start_app = False
        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu video", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        self.download_by_video_url = create_frame_button_and_input(self.root,text="Tải video từ URL", command=start_download_by_video_url, width=self.width, left=0.4, right=0.6)
        create_button(frame=self.root, text="Tải video từ Douyin", command=self.open_download_douyin_video_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def choose_folder_to_save(self):
        download_folder = filedialog.askdirectory()
        if download_folder:
            self.download_folder_var.delete(0, ctk.END)
            self.download_folder_var.insert(0, download_folder)
            self.config['download_folder'] = download_folder
            self.save_config()

    def download_video_by_video_url(self):
        video_url = self.download_by_video_url.get()
        download_video_by_url(video_url, self.config['download_folder'])


    def open_download_douyin_video_window(self):
        self.reset()
        self.is_download_douyin_video_window = True
        self.show_window()
        self.setting_window_size()

        
        def start_thread_download_douyin_video_by_url():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_download_douyin_channel = False
                self.download_thread = threading.Thread(target=start_download_douyin_video)
                self.download_thread.start()
            else:
                self.noti("Đang tải video ở một luồng khác.")


        def start_thread_download_douyin_channel():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_download_douyin_channel = True
                self.download_thread = threading.Thread(target=start_download_douyin_video)
                self.download_thread.start()
            else:
                self.noti("Đang tải video ở một luồng khác.")

        def start_download_douyin_video():
            try:
                def check_quang_cao():
                    xpath = get_xpath_by_multi_attribute('div', ['id="dismiss-button"'])
                    ele = get_element_by_xpath(self.driver, xpath)
                    if ele:
                        ele.click()

                def download_douyin_video_by_tikvideoapp(url):
                    try:
                        file_name = f"{url.split('/')[-1]}.mp4"
                        output_path = os.path.join(self.config['download_folder'], file_name)
                        self.driver.get('https://tikvideo.app/vi/download-douyin-video')
                        sleep(2)
                        check_quang_cao()
                        input_xpath = get_xpath_by_multi_attribute('input', ['id="s_input"'])
                        input_ele = get_element_by_xpath(self.driver, input_xpath)
                        if input_ele:
                            input_ele.send_keys(url)
                            input_ele.send_keys(Keys.ENTER)
                            check_quang_cao()
                            video_link_xpath = "//a[contains(text(),'Tải xuống MP4 HD')]"
                            video_link_ele = get_element_by_xpath(self.driver, video_link_xpath)
                            if video_link_ele:
                                url = video_link_ele.get_attribute('href')
                                response = requests.get(url, stream=True)

                                # Lưu video vào file
                                with open(output_path, 'wb') as file:
                                    for chunk in response.iter_content(chunk_size=1024):
                                        if chunk:
                                            file.write(chunk)
                                if not os.path.exists(output_path):
                                    if download_douyin_video_by_snaptikapp(url):
                                        return True
                                    else:
                                        return False
                                else:
                                    return True
                        return False
                    except:
                        return False

                def download_douyin_video_by_snaptikapp(url):
                    try:
                        file_name = f"{url.split('/')[-1]}.mp4"
                        output_path = os.path.join(self.config['download_folder'], file_name)
                        self.driver.get('https://snaptik.app/vn/douyin-downloader')
                        sleep(2)
                        check_quang_cao()
                        input_xpath = get_xpath_by_multi_attribute('input', ['id="url"', 'name="url"'])
                        input_ele = get_element_by_xpath(self.driver, input_xpath)
                        if input_ele:
                            input_ele.send_keys(url)
                            ele.send_keys(Keys.ENTER)
                            check_quang_cao()
                            video_link_xpath = "//a[contains(text(),'Tải xuống MP4 HD')]"
                            video_link_ele = get_element_by_xpath(self.driver, video_link_xpath)
                            if video_link_ele:
                                url = video_link_ele.get_attribute('href')
                                response = requests.get(url, stream=True)
                                with open(output_path, 'wb') as file:
                                    for chunk in response.iter_content(chunk_size=1024):
                                        if chunk:
                                            file.write(chunk)
                                if os.path.exists(output_path):
                                    return True
                        return False
                    except:
                        return False

                video_urls = []
                cnt_download = 0
                if self.is_download_douyin_channel:
                    cnt_search = 0
                    channel_link = self.download_by_channel_link.get()
                    if not channel_link:
                        self.noti("Hãy nhập link kênh muốn tải video trước.")
                        return
                    self.driver = get_driver()
                    self.driver.get(channel_link)
                    self.check_noti_login_douyin(self.driver)
                    if self.is_stop_download:
                        return
                    last_height = self.driver.execute_script("return document.body.scrollHeight")
                    k = False
                    print(f"Bắt đầu quét video trong kênh theo link {channel_link} ...")
                    while True:
                        if self.is_stop_download:
                            return
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Cuộn xuống cuối trang
                        sleep(2)
                        new_height = self.driver.execute_script("return document.body.scrollHeight") # Tính chiều cao mới của trang
                        if new_height == last_height: # Kiểm tra nếu không có thêm nội dung mới
                            if k:
                                break
                            else:
                                k = True
                                sleep(2)
                                continue
                        k = False
                        last_height = new_height
                        cnt_search += 1
                        if cnt_search > 100:
                            break

                    xpath = get_xpath('a', 'uz1VJwFY TyuBARdT IdxE71f8')
                    eles = self.driver.find_elements(By.XPATH, xpath)
                    if len(eles) > 0:
                        for ele in eles:
                            if self.is_stop_download:
                                return
                            video_link = ele.get_attribute('href')
                            if video_link not in video_urls:
                                video_urls.append(video_link)
                    else:
                        xpath = "//div[starts-with(@id, 'waterfall_item_')]"
                        eles = self.driver.find_elements(By.XPATH, xpath)
                        if eles:
                            for ele in eles:
                                if self.is_stop_download:
                                    return
                                ele_id = ele.get_attribute('id')
                                video_id = ele_id.split('waterfall_item_')[-1]
                                video_link = f'https://www.douyin.com/video/{video_id}'
                                if video_link not in video_urls:
                                    video_urls.append(video_link)
                else:
                    video_url = self.download_by_video_url.get().strip()
                    video_urls.append(video_url)
                if len(video_urls) > 0:
                    print(f'Đã tìm thấy {len(video_urls)} video')
                    print("Bắt đầu tải video ...")
                    for url in video_urls:
                        if self.is_stop_download:
                            break
                        print(f'Bắt đầu tải video {url}')
                        if download_douyin_video_by_tikvideoapp(url):
                            print(f"Tải thành công video {url}")
                            cnt_download += 1
                        else:
                            print(f"Tải video không thành công: {url}!!!")
                if cnt_download > 0:
                    self.noti(f'Đã tải thành công {cnt_download} video')
            except:
                print("Có lỗi trong quá trình tải video từ douyin")
            finally:
                self.close()

        self.download_by_video_url = create_frame_button_and_input(self.root, text="Tải video từ link video", command=start_thread_download_douyin_video_by_url, width=self.width, left=0.45, right=0.55)
        self.download_by_channel_link = create_frame_button_and_input(self.root, text="Tải video từ link kênh/ link tìm kiếm", command=start_thread_download_douyin_channel, width=self.width, left=0.45, right=0.55)
        create_button(self.root, text="Lùi lại", command=self.open_other_download_video_window, width=self.width)



        

    def check_noti_login_douyin(self, driver):
        xpath = get_xpath('div', 'douyin-login__close dy-account-close')
        ele = get_element_by_xpath(driver, xpath)
        if ele:
            ele.click()
        
    def open_edit_audio_window(self):
        self.reset()
        self.is_edit_audio_window = True
        self.show_window()
        self.setting_window_size()
        create_button(frame=self.root, text="Thay đổi thông tin audio", command=self.open_edit_audio_option)
        create_button(frame=self.root, text="Trích xuất/Chỉnh sửa audio", command=self.open_extract_audio_option)
        create_button(frame=self.root, text="Chuyển đổi văn bản sang giọng nói", command=self.open_text_to_mp3_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def other_function(self):
        self.reset()
        self.is_other_window = True
        self.show_window()
        self.setting_window_size()
        create_button(self.root, text="Đặt tên file theo chỉ số", command=self.open_rename_file_by_index_window, width=self.width)
        create_button(self.root, text="Xóa ký tự trong file", command=self.open_remove_char_in_file_name_window, width=self.width)
        create_button(self.root, text="Trích xuất ảnh từ video", command=self.extract_image_from_video_window, width=self.width)
        create_button(self.root, text="Đăng ký mã máy", command=self.open_register_mac_addres_window, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def open_youtube_window(self):
        self.reset()
        self.is_youtube_window = True
        self.show_window()
        self.setting_window_size()
        values = list(set([self.youtube_config['template'][key]['gmail'] for key in self.youtube_config['template'].keys()]))
        if not values:
            values = ['-------------------------']
        self.input_gmail = self.create_settings_input("Chọn tài khoản Youtube", "current_youtube_account" ,values=values, left=0.4, right=0.6, add_button=True, text='Tìm channel', command=self.choose_a_youtube_channel)
        self.input_gmail.set(self.youtube_config['current_youtube_account'])
        if self.youtube_config['current_youtube_account']:
            values = [k for k,v in self.youtube_config['template'].items() if v.get('gmail') == self.youtube_config['current_youtube_account']]
        else:
            values = ['-------------------------']
        self.input_current_channel_name = self.create_settings_input("Chọn tên kênh", "current_channel" ,values=values, left=0.4, right=0.6)
        self.input_current_channel_name.set(self.youtube_config['current_channel'])
        create_button(self.root, text="Mở cửa sổ quản lý kênh Youtube", command=self.start_youtube_management)
        create_button(self.root, text="Đăng ký kênh youtube mới", command=self.add_new_channel)
        create_button(self.root, text="Xóa thông tin kênh youtube", command=self.remove_youtube_channel_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)
    
    def choose_a_youtube_channel(self):
        current_youtube_account = self.input_gmail.get()
        channels_of_gmail = [k for k,v in self.youtube_config['template'].items() if v.get('gmail') == current_youtube_account]
        if len(channels_of_gmail) == 0:
            self.noti(f"Gmail {current_youtube_account} chưa được đăng ký hoặc hết hạn.")
            return
        self.input_current_channel_name.configure(values=channels_of_gmail)
        self.input_current_channel_name.set(channels_of_gmail[0])

    def remove_youtube_channel_window(self):
        def remove_channel_now():
            try:
                channel_name = self.channel_remove_var.get()
                if not channel_name:
                    self.noti("Hãy chọn channel muốn xóa.")
                    return
                self.get_youtube_config()
                if channel_name in self.youtube_config['template'].keys():
                    removed_channel = self.youtube_config['template'].pop(channel_name, None)
                    self.save_youtube_config()
                    self.noti(f'Xóa kênh [{channel_name}] thành công.')
                    self.remove_youtube_channel_window()
                else:
                    self.noti(f"Kênh {channel_name} không tồn tại trong cơ sở dữ liệu")
            except:
                self.noti(f"Xóa kênh [{channel_name}] thất bại !!!")
            
        self.reset()
        self.is_remove_channel = True
        self.setting_window_size()
        self.show_window()
        self.channel_remove_var = self.create_settings_input(label_text="Nhập tên kênh youtube", config_key='current_channel', values=[key for key in self.youtube_config['template'].keys()], left=0.3, right=0.7)
        create_button(frame=self.root, text="Bắt đầu xóa thông tin kênh youtube", command=remove_channel_now)
        create_button(self.root, text="Lùi lại", command=self.open_youtube_window, width=self.width)

    def add_new_channel(self):
        self.reset()
        self.is_add_new_channel = True
        self.setting_window_size()
        self.show_window()
        self.input_gmail = self.create_settings_input(label_text="Tài khoản youtube", config_key='current_youtube_account', values=self.youtube_config['registered_account'], left=0.3, right=0.7)
        self.input_current_channel_name = create_frame_label_and_input(self.root, label_text="Nhập tên kênh")
        create_button(frame=self.root, text="Đăng ký ngay", command=self.sign_up_youtube_channel)
        create_button(self.root, text="Lùi lại", command=self.open_youtube_window, width=self.width)
    
    def sign_up_youtube_channel(self):
        self.is_add_new_channel = True
        gmail = self.input_gmail.get().strip()
        channel_name = self.input_current_channel_name.get().strip()
        if not gmail or not channel_name:
            self.noti("Hãy nhập đầy đủ thông tin!")
            return
        if '@gmail.com' not in gmail:
            self.noti("Không đúng định dạng gmail.")
            return
            
        if channel_name not in self.youtube_config['template']:
            self.youtube_config['template'][channel_name] = {}
        self.youtube_config['template'][channel_name]['gmail'] = gmail
        self.youtube_config['template'][channel_name]['title'] = ""
        self.youtube_config['template'][channel_name]['is_title_plus_video_name'] = True
        self.youtube_config['template'][channel_name]['description'] = ""
        self.youtube_config['template'][channel_name]['curent_playlist'] = ""
        self.youtube_config['template'][channel_name]['playlist'] = [" "]
        self.youtube_config['template'][channel_name]['altered_content'] = False
        self.youtube_config['template'][channel_name]['upload_date'] = ""
        self.youtube_config['template'][channel_name]['publish_times'] = ""
        self.youtube_config['template'][channel_name]['thumbnail_folder'] = ""
        self.youtube_config['template'][channel_name]['upload_folder'] = ""
        self.youtube_config['template'][channel_name]['is_delete_after_upload'] = False
        self.youtube_config['template'][channel_name]['number_of_days'] = "1"
        self.youtube_config['template'][channel_name]['day_gap'] = "1"
        # self.youtube_config['template'][channel_name]['last_auto_upload_date'] = ""
        self.start_youtube_management(channel_name)

    def start_youtube_management(self, channel_name=None):
        if self.is_add_new_channel:
            gmail = self.youtube_config['template'][channel_name]['gmail']
            self.is_add_new_channel = False
        else:
            gmail = self.input_gmail.get().strip()
            channel_name = self.input_current_channel_name.get().strip()
            if not gmail or not channel_name:
                self.noti("Hãy nhập đủ thông tin!")
                return
            if channel_name not in self.youtube_config['template'].keys():
                self.noti(f"kênh {channel_name} chưa được đăng ký!")
                return
            if gmail not in self.youtube_config['registered_account']: 
                self.noti(f"tài khoản gmail {gmail} chưa được đăng ký!")
                return
        self.youtube = YouTubeManager(gmail, channel_name, is_auto_upload=False, download_thread=self.download_thread, upload_thread=self.upload_thread)
        self.reset()
        self.youtube_config['current_youtube_account'] = gmail
        self.youtube_config['current_channel'] = channel_name
        if gmail not in self.youtube_config['registered_account']:
            self.youtube_config['registered_account'].append(gmail)
        self.save_config()
        self.save_youtube_config()
        self.youtube.get_start_youtube()

    def open_tiktok_window(self):
        self.get_tiktok_config()
        self.reset()
        self.is_tiktok_window = True
        self.show_window()
        self.setting_window_size()
        self.tiktok_account_var = self.create_settings_input(label_text="Chọn tài khoản", config_key="current_tiktok_account", values=self.tiktok_config['registered_account'])
        create_button(self.root, text="Mở cửa sổ quản lý kênh tiktok", command=self.start_tiktok_management)
        create_button(self.root, text="Đăng ký tài khoản tiktok mới", command=self.sign_up_tiktok_window)
        create_button(self.root, text="Xóa thông tin kênh tiktok", command=self.remove_tiktok_channel_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def remove_tiktok_channel_window(self):
        def remove_channel_now():
            try:
                channel_name = self.tiktok_channel_remove_var.get()
                if not channel_name:
                    self.noti("Hãy chọn channel muốn xóa.")
                    return
                self.get_youtube_config()
                if channel_name in self.tiktok_config['template'].keys():
                    self.tiktok_config['template'].pop(channel_name, None)
                    if channel_name in self.tiktok_config['registered_account']:
                        self.tiktok_config['registered_account'].remove(channel_name)
                    if self.config['current_tiktok_account'] == channel_name:
                        self.config['current_tiktok_account'] = ""
                        self.save_config()
                    self.save_tiktok_config()
                    self.noti(f'Xóa kênh [{channel_name}] thành công.')
                    self.remove_tiktok_channel_window()
                else:
                    self.noti(f"Kênh {channel_name} không tồn tại trong cơ sở dữ liệu")
            except:
                self.noti(f"Xóa kênh [{channel_name}] thất bại !!!")
        self.reset()
        self.is_remove_channel = True
        self.setting_window_size()
        self.show_window()
        self.tiktok_channel_remove_var = self.create_settings_input(label_text="Nhập tên kênh tiktok", config_key='current_tiktok_account', values=[key for key in self.tiktok_config['template'].keys()], left=0.3, right=0.7)
        create_button(frame=self.root, text="Bắt đầu xóa thông tin kênh tiktok", command=remove_channel_now)
        create_button(self.root, text="Lùi lại", command=self.open_tiktok_window, width=self.width)

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
                self.noti("Hãy nhập đầy đủ thông tin!")
                return
            if self.tiktok_account not in self.tiktok_config['template']:
                self.tiktok_config['template'][self.tiktok_account] = {}
            self.tiktok_config['template'][self.tiktok_account]['account'] = self.tiktok_account
            self.tiktok_config['template'][self.tiktok_account]['password'] = self.tiktok_password
            self.tiktok_config['template'][self.tiktok_account]['thumbnail_folder'] = ""
            self.tiktok_config['template'][self.tiktok_account]['upload_folder'] = ""
            self.tiktok_config['template'][self.tiktok_account]['description'] = ""
            self.tiktok_config['template'][self.tiktok_account]['location'] = ""
            self.tiktok_config['template'][self.tiktok_account]['publish_times'] = ""
            self.tiktok_config['template'][self.tiktok_account]['title'] = ""
            self.tiktok_config['template'][self.tiktok_account]['is_title_plus_video_name'] = False
            self.tiktok_config['template'][self.tiktok_account]['upload_date'] = datetime.now().strftime('%Y-%m-%d')
            self.tiktok_config['template'][self.tiktok_account]['is_delete_after_upload'] = False
            self.tiktok_config['template'][self.tiktok_account]['waiting_verify'] = False
            self.tiktok_config['template'][self.tiktok_account]['number_of_days'] = "1"
            self.tiktok_config['template'][self.tiktok_account]['day_gap'] = "1"
            self.tiktok_config['template'][self.tiktok_account]['first_login'] = True
            if self.tiktok_account not in self.tiktok_config['registered_account']:
                self.tiktok_config['registered_account'].append(self.tiktok_account)
            save_to_json_file(self.tiktok_config, tiktok_config_path)
            self.start_tiktok_management()

        self.tiktok_account_var = create_frame_label_and_input(self.root, label_text="Nhập tài khoản tiktok")
        self.tiktok_password_var = create_frame_label_and_input(self.root, label_text="Nhập mật khẩu", is_password=True)
        create_button(self.root, text="Đăng ký ngay", command=sign_up_tiktok)
        create_button(self.root, text="Lùi lại", command=self.open_tiktok_window, width=self.width)

    def start_tiktok_management(self):
        self.tiktok_account = self.tiktok_account_var.get()
        if not self.is_sign_up_tiktok:
            if self.tiktok_account not in self.tiktok_config['registered_account'] or self.tiktok_account not in self.tiktok_config['template']:
                self.noti(f"tài khoản {self.tiktok_account} chưa được đăng ký")
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
        self.facebook_account_var = self.create_settings_input(label_text="Chọn tài khoản facebook", config_key="current_facebook_account", values=self.facebook_config['registered_account'])
        self.facebook_page_name_var = self.create_settings_input(label_text="Chọn trang facebook", config_key="current_page", values=[key for key in self.facebook_config['template'].keys()])
        create_button(self.root, text="Mở cửa sổ quản lý trang facebook", command=self.start_facebook_management)
        create_button(self.root, text="Đăng ký trang facebook mới", command=self.sign_up_facebook_window)
        create_button(self.root, text="Xóa thông tin trang facebook", command=self.remove_facebook_page_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

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
                self.noti("Hãy nhập đầy đủ thông tin!")
                return
            if self.facebook_page_name not in self.facebook_config['template']:
                self.facebook_config['template'][self.facebook_page_name] = {}
            self.config['current_page'] = self.facebook_page_name
            self.facebook_config['template'][self.facebook_page_name]['account'] = self.facebook_account
            self.facebook_config['template'][self.facebook_page_name]['password'] = self.facebook_password
            self.facebook_config['template'][self.facebook_page_name]['upload_folder'] = ""
            self.facebook_config['template'][self.facebook_page_name]['description'] = ""
            self.facebook_config['template'][self.facebook_page_name]['publish_times'] = ""
            self.facebook_config['template'][self.facebook_page_name]['title'] = ""
            self.facebook_config['template'][self.facebook_page_name]['is_title_plus_video_name'] = False
            self.facebook_config['template'][self.facebook_page_name]['upload_date'] = datetime.now().strftime('%Y-%m-%d')
            self.facebook_config['template'][self.facebook_page_name]['is_delete_after_upload'] = False
            self.facebook_config['template'][self.facebook_page_name]['is_move_after_upload'] = False
            self.facebook_config['template'][self.facebook_page_name]['number_of_days'] = "1"
            self.facebook_config['template'][self.facebook_page_name]['day_gap'] = "1"
            self.facebook_config['template'][self.facebook_page_name]['is_reel_video'] = False
            self.facebook_config['template'][self.facebook_page_name]['waiting_verify'] = False
            if self.facebook_account not in self.facebook_config['registered_account']:
                self.facebook_config['registered_account'].append(self.facebook_account)
            save_to_json_file(self.facebook_config, facebook_config_path)
            self.start_facebook_management()

        # self.facebook_account_var = create_frame_label_and_input(self.root, label_text="Nhập tên đăng nhập facebook")
        self.facebook_account_var = self.create_settings_input(label_text="Tài khoản Facebook", config_key='current_facebook_account', values=self.facebook_config['registered_account'], left=0.3, right=0.7)
        self.facebook_password_var = create_frame_label_and_input(self.root, label_text="Nhập mật khẩu", is_password=True)
        self.facebook_page_name_var = create_frame_label_and_input(self.root, label_text="Nhập tên trang")
        create_button(self.root, text="Đăng ký ngay", command=sign_up_facebook)
        create_button(self.root, text="Lùi lại", command=self.open_facebook_window, width=self.width)

    def remove_facebook_page_window(self):
        def remove_channel_now():
            try:
                page_name = self.page_remove_var.get()
                if not page_name:
                    self.noti("Hãy chọn trang facebook muốn xóa.")
                    return
                self.get_youtube_config()
                if page_name in self.facebook_config['template'].keys():
                    removed_page = self.facebook_config['template'].pop(page_name, None)
                    self.save_facebook_config()
                    self.noti(f'Xóa trang [{page_name}] thành công.')
                    self.remove_facebook_page_window()
                else:
                    self.noti(f"Trang {page_name} không tồn tại trong cơ sở dữ liệu")
            except:
                self.noti(f"Xóa trang [{page_name}] thất bại !!!")
            
        self.reset()
        self.is_remove_channel = True
        self.setting_window_size()
        self.show_window()
        self.page_remove_var = self.create_settings_input(label_text="Nhập tên kênh youtube", config_key='current_facebook_account', values=[key for key in self.facebook_config['template'].keys()], left=0.3, right=0.7)
        create_button(frame=self.root, text="Bắt đầu xóa thông tin trang facebook", command=remove_channel_now)
        create_button(self.root, text="Lùi lại", command=self.open_facebook_window, width=self.width)

    def start_facebook_management(self):
        self.facebook_page_name = self.facebook_page_name_var.get()
        self.facebook_account = self.facebook_account_var.get()
        if not self.is_sign_up_facebook:
            if not self.facebook_page_name or not self.facebook_account:
                self.noti("Hãy nhập đầy đủ thông tin!")
                return
            if self.facebook_page_name not in self.facebook_config['template']:
                self.noti(f"Trang {self.facebook_page_name} chưa được đăng ký!")
                return
            if self.facebook_account != self.facebook_config['template'][self.facebook_page_name]['account']:
                self.noti(f"Tài khoản {self.facebook_account} chưa được đăng ký!")
                return
        self.config['current_facebook_account'] = self.facebook_account
        self.config['current_page'] = self.facebook_page_name
        self.save_config()
        self.reset()
        self.facebook_password = self.facebook_config['template'][self.facebook_page_name]['password']
        self.facebook = FacebookManager(self.facebook_account, self.facebook_password, self.facebook_page_name, self.download_thread, self.upload_thread)
        self.facebook.get_start_facebook()

#---------------------------------------------edit audio-------------------------------------------
        
    def open_edit_audio_option(self):
        def start_thread_edit_audio():
            def start_edit_audio():
                if save_seting_input():
                    first_cut = self.first_cut_var.get().strip()
                    end_cut = self.end_cut_var.get().strip()
                    edit_audio_ffmpeg(input_audio_folder=self.config['audios_edit_folder'], start_cut=first_cut, end_cut=end_cut, pitch_factor=self.config['pitch_factor'], cut_silence=self.config['cut_silence'], aecho=self.config['aecho'])

            if not self.edit_audio_thread or not self.edit_audio_thread.is_alive():
                self.edit_audio_thread = threading.Thread(target=start_edit_audio)
                self.edit_audio_thread.start()
        def save_seting_input():
            self.config['audio_speed'] = self.audio_speed_var.get().strip()
            self.config['pitch_factor'] = self.pitch_factor_var.get().strip()
            self.config['cut_silence'] = self.cut_silence_var.get().strip() == 'Yes'
            self.config['aecho'] = self.aecho_var.get().strip()
            self.config['audios_edit_folder'] = self.folder_get_audio_var.get().strip()
            if not check_folder(self.config['audios_edit_folder']):
                return False
            self.save_config()
            return True

        self.reset()
        self.is_edit_audio_option = True
        self.setting_window_size()
        self.show_window()
        self.end_cut_var, self.first_cut_var = create_frame_label_input_input(self.root, label_text="Cắt ở đầu/cuối video (s)", width=self.width, left=0.4, mid=0.28, right=0.32)
        # self.end_cut_var.delete(0, ctk.END)
        self.end_cut_var.insert(0, 0)
        self.first_cut_var.insert(0, 0)
        self.audio_speed_var = self.create_settings_input(label_text="Tốc độ phát", config_key="audio_speed", values=['0.8', '1', '1.2'], left=0.4, right=0.6)
        self.pitch_factor_var = self.create_settings_input(label_text="Điều chỉnh cao độ (vd: 1.2)", config_key="pitch_factor", values=['-0.8','1','1.2'], left=0.4, right=0.6)
        self.cut_silence_var = self.create_settings_input(label_text="Cắt bỏ những đoạn im lặng", config_key="cut_silence", values=['Yes', 'No'], left=0.4, right=0.6)
        self.aecho_var = self.create_settings_input(label_text="Tạo tiếng vang (ms)", config_key="aecho", values=['100', '500', '1000'], left=0.4, right=0.6)
        self.folder_get_audio_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa audio", command= self.choose_folder_get_audio, left=0.4, right=0.6, width=self.width)
        self.folder_get_audio_var.insert(0, self.config['audios_edit_folder'])
        create_button(self.root, text="Bắt đầu chỉnh sửa audio", command=start_thread_edit_audio, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)
        
    def open_extract_audio_option(self):
        self.reset()
        self.is_extract_audio_option = True
        self.setting_window_size()
        self.show_window()
        self.segment_audio_var = create_frame_label_and_input(self.root, label_text="Thời gian bắt đầu-kết thúc", width=self.width, left=0.4, right=0.6)
        self.video_get_audio_url = create_frame_label_and_input(self.root, label_text="Lấy audio từ Link", left=0.4, right=0.6)
        self.audio_edit_path = create_frame_button_and_input(self.root,text="Lấy audio từ file MP3", command= self.choose_audio_edit_file, left=0.4, right=0.6)
        self.video_get_audio_path = create_frame_button_and_input(self.root,text="Lấy audio từ file video", command= self.choose_video_get_audio_path, left=0.4, right=0.6)
        self.get_audio_from_folder_var = create_frame_button_and_input(self.root,text="Lấy audio từ video trong thư mục", command= self.choose_folder_get_audio, left=0.4, right=0.6)
        self.folder_get_audio_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu file", command= self.choose_folder_download, left=0.4, right=0.6, width=self.width)
        self.folder_get_audio_var.insert(0, self.config['download_folder'])
        create_button(frame=self.root, text="Bắt đầu trích xuất audio", command=self.create_thread_edit_audio, padx=8)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)

    def choose_folder_download(self):
        folder = choose_folder()
        self.folder_get_audio_var.delete(0, ctk.END)
        self.folder_get_audio_var.insert(0, folder)

    def choose_folder_get_audio(self):
        folder = choose_folder()
        self.get_audio_from_folder_var.delete(0, ctk.END)
        self.get_audio_from_folder_var.insert(0, folder)

    def choose_audio_edit_file(self):
        audio_edit_path = choose_file()
        if audio_edit_path:
            self.audio_edit_path.delete(0, ctk.END)
            self.audio_edit_path.insert(0, audio_edit_path)
        else:
            self.noti("Hãy chọn file audio muốn xử lý")

    def choose_video_get_audio_path(self):
        video_get_audio_path = choose_file()
        if video_get_audio_path:
            self.video_get_audio_path.delete(0, ctk.END)
            self.video_get_audio_path.insert(0, video_get_audio_path)
        else:
            self.noti("Hãy chọn file video chứa audio muốn xử lý")

    def create_thread_edit_audio(self):
        thread_edit_audio = threading.Thread(target=self.start_edit_audio)
        thread_edit_audio.daemon = True
        thread_edit_audio.start()

    def start_edit_audio(self):
        try:
            download_folder = self.choose_folder_download_var.get()
            if not os.path.exists(download_folder):
                self.noti("hãy chọn thư mục lưu file tải về.")
                return
            video_get_audio_url = self.video_get_audio_url.get()
            audio_edit_path = self.audio_edit_path.get()
            video_get_audio_path = self.video_get_audio_path.get()
            video_folder = self.get_audio_from_folder_var.get()
            if not video_get_audio_url and not os.path.exists(audio_edit_path) and not os.path.exists(video_get_audio_path) and not os.path.exists(video_folder):
                self.noti("Hãy chọn 1 nguồn lấy audio !!!")
                return
            segment_audio = self.segment_audio_var.get().strip()
            extract_audio_ffmpeg(audio_path=self.config['audio_edit_path'], video_path=video_get_audio_path, video_url=video_get_audio_url, video_folder=video_folder, segments=segment_audio, download_folder=download_folder)
        except:
            print("Có lỗi trong quá trình trích xuất audio !!!")

#-------------------------------------------edit video-----------------------------------------------------
    def open_edit_video_menu(self):
        self.reset()
        self.is_open_edit_video_menu = True
        self.show_window()
        self.setting_window_size()
        create_button(frame=self.root, text="Thay đổi thông tin video", command=self.open_edit_video_window)
        create_button(self.root, text="Chuyển đổi tỷ lệ video", command=self.convert_videos_window)
        create_button(self.root, text="Cắt video", command=self.open_cut_video_window)
        create_button(self.root, text="Gộp video", command=self.open_combine_video_window)
        create_button(self.root, text="Tăng chất lượng video", command=self.open_increse_video_quality_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)
    
    def open_cut_video_window(self):
        self.reset()
        self.is_cut_video_window =True
        self.show_window()
        self.setting_window_size()
        self.segments_var = self.create_settings_input(label_text="Khoảng thời gian muốn lấy(start-end)", left=0.4, right=0.6)
        self.fast_cut_var = self.create_settings_input(label_text="Cắt nhanh", values=["Yes", "No"], left=0.4, right=0.6)
        self.fast_cut_var.set(value="No")
        self.get_audio_var = self.create_settings_input(label_text="Trích xuất MP3", values=["Yes", "No"], left=0.4, right=0.6)
        self.get_audio_var.set(value="No")
        self.choose_is_connect_var = self.create_settings_input(label_text="Nối các video lại", values=["No", "Connect", "Fast Connect"], left=0.4, right=0.6)
        self.choose_is_connect_var.set(value="No")
        self.videos_edit_path_var = create_frame_button_and_input(self.root, "Chọn video muốn cắt", width=self.width, command=self.choose_videos_edit_file, left=0.4, right=0.6)
        self.videos_edit_folder_var = create_frame_button_and_input(self.root, "Chọn thư mục chứa các video", width=self.width, command=self.choose_videos_edit_folder, left=0.4, right=0.6)
        create_button(self.root, text="Bắt đầu cắt video", command=self.start_thread_cut_video)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)

    def open_combine_video_window(self):
        self.reset()
        self.is_combine_video_window =True
        self.show_window()
        self.setting_window_size()
        self.file_name_var = create_frame_label_and_input(self.root, "Đặt tên file sau khi gộp", width=self.width, left=0.4, right=0.6)
        self.fast_combine_var = self.create_settings_input(label_text="Gộp nhanh", values=["Yes", "No"], left=0.4, right=0.6)
        self.fast_combine_var.set('Yes')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root, "Chọn thư mục chứa video", command=self.choose_videos_edit_folder, width=self.width, left=0.4, right=0.6)
        self.videos_edit_folder_var.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Bắt đầu gộp", command=self.create_thread_combine_video)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)

    def open_increse_video_quality_window(self):
        self.reset()
        self.is_increse_video_quality_window =True
        self.show_window()
        self.setting_window_size()
        self.videos_edit_folder_var = create_frame_button_and_input(self.root, "Chọn thư mục chứa video", command=self.choose_videos_edit_folder, width=self.width, left=0.4, right=0.6)
        self.videos_edit_folder_var.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Bắt đầu tăng chất lượng video", command=self.create_thread_increse_video_quality)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)

    def convert_videos_window(self):
        self.reset()
        self.is_convert_video_window = True
        self.show_window()
        self.setting_window_size()
        self.choose_convert_type = self.create_settings_input(label_text="Chọn tỷ lệ muốn chuyển đổi", config_key="convert_type", values=["16:9 to 9:16", "9:16 to 16:9"])
        self.choose_convert_type.set("16:9 to 9:16")
        self.choose_zoom_size = self.create_settings_input(label_text="Zoom video(16:9 to 9:16)")
        self.videos_edit_folder_var = create_frame_button_and_input(self.root, "Chọn thư mục chứa video", width=self.width, command=self.choose_videos_edit_folder, left=0.4, right=0.6)
        self.videos_edit_folder_var.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Bắt đầu chuyển đổi", width=self.width, command=self.start_convert_video)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)
    

    def start_convert_video(self):
        convert_type = self.choose_convert_type.get()
        if convert_type == "16:9 to 9:16":
            self.is_169_to_916 = True
        elif convert_type == "9:16 to 16:9":
            self.is_169_to_916 = False
        else:
            self.noti("Hãy chọn tỷ lệ chuyển đổi cho phù hợp!")
            return
        self.start_thread_edit_video()

    def start_thread_edit_video(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.is_stop_edit = False
            self.edit_thread = threading.Thread(target=self.convert_videos)
            self.edit_thread.start()

    def start_thread_cut_video(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.is_stop_edit = False
            self.edit_thread = threading.Thread(target=self.cut_videos_by_timeline)
            self.edit_thread.start()

    def cut_videos_by_timeline(self):
        segments = self.segments_var.get()
        is_connect = self.choose_is_connect_var.get().lower()
        fast_cut = self.fast_cut_var.get() == 'Yes'
        get_audio = self.get_audio_var.get() == 'Yes'
        if not segments:
            self.noti("Hãy nhập các khoảng thời gian muốn cắt, ví dụ: 05:50,60:90,...")
            return
    
        video_path = self.videos_edit_path_var.get()
        if os.path.exists(video_path):
            is_edit_ok, message = cut_video_by_timeline_use_ffmpeg(video_path, segments=segments, is_connect=is_connect, fast_cut=fast_cut, get_audio=get_audio)
            if is_edit_ok:
                self.noti(f"--> Xử lý thành công video: {video_path}")
            else:
                self.noti(message)
        else:
            videos_folder = self.videos_edit_folder_var.get()
            edit_videos = get_file_in_folder_by_type(videos_folder, ".mp4")
            if not edit_videos:
                return
            cnt = 0
            for i, video_file in enumerate(edit_videos):
                if self.is_stop_edit:
                    return
                video_path = f'{videos_folder}\\{video_file}'
                is_edit_ok, message = cut_video_by_timeline_use_ffmpeg(video_path, segments=segments, is_connect=is_connect, fast_cut=fast_cut, get_audio=get_audio)
                if is_edit_ok:
                    print(f"--> Xử lý thành công video: {video_path}")
                    cnt += 1
                else:
                    print(message)
            self.noti(f"Xử lý thành công {cnt} video")

    def combine_video_by_ffmpeg(self):
        videos_folder = self.videos_edit_folder_var.get()
        file_name = self.file_name_var.get()
        fast_combine = self.fast_combine_var.get() == 'Yes'
        if not videos_folder:
            self.noti("Hãy chọn thư mục chứa video")
            return
        if not os.path.isdir(videos_folder):
            self.noti("Thư mục chứa video không tồn tại")
            return
        try:
            is_ok, message = merge_videos_use_ffmpeg(videos_folder, file_name, is_delete=self.config['is_delete_video'], fast_combine=fast_combine)
            self.noti(message)
        except Exception as e:
            getlog()
            print(f"Có lỗi trong quá trình gộp video. Đang dùng cách khác để gộp video.")
            self.combine_video_by_moviepy()

    def combine_video_by_moviepy(self):
        videos_folder = self.videos_edit_folder_var.get()
        if not self.check_folder(videos_folder):
            return
        try:
            output_folder = f'{videos_folder}\\merge_videos'
            os.makedirs(output_folder, exist_ok=True)
            edit_videos = get_file_in_folder_by_type(videos_folder)
            if not edit_videos:
                return
            if len(edit_videos) <= 1:
                warning_message("Phải có ít nhất 2 video trong videos folder")
                return
            clips = []
            remove_videos = []
            for i, video_file in enumerate(edit_videos):
                if self.is_stop_edit:
                    return
                video_path = f'{videos_folder}\\{video_file}'
                remove_videos.append(video_path)
                clip = VideoFileClip(video_path)
                clips.append(clip)

            if len(clips) > 0:
                final_clip = concatenate_videoclips(clips, method="compose")
                file_path = f"{output_folder}\\combine_video.mp4"
                final_clip.write_videofile(file_path, codec='libx264')
                final_clip.close()
                for clip in clips:
                    clip.close()
            try:
                for video_path in remove_videos:
                    remove_or_move_file(video_path, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'])
            except:
                getlog()
            self.noti(f"Gộp thành công {len(edit_videos)} vào file: {file_path}")
        except Exception as e:
            getlog()
            print(f"Có lỗi trong quá trình gộp video")

    def increse_video_quality_by_ffmpeg(self):
        try:
            videos_folder = self.videos_edit_folder_var.get()
            edit_videos = get_file_in_folder_by_type(videos_folder, ".mp4")
            if not edit_videos:
                return
            output_folder = f'{videos_folder}\\increse_videos_quality'
            os.makedirs(output_folder, exist_ok=True)
            for i, video_file in enumerate(edit_videos):
                if self.is_stop_edit:
                    return
                video_path = f'{videos_folder}\\{video_file}'
                outpath_video = os.path.join(output_folder, video_file)
                if increase_video_quality(video_path, outpath_video):
                    remove_or_move_file(video_path, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'])
        except:
            getlog()

    def convert_videos(self):
        try:
            zoom_size = self.choose_zoom_size.get()
            videos_folder = self.videos_edit_folder_var.get()
            if not self.check_folder(videos_folder):
                return
            self.config['videos_edit_folder'] = videos_folder
            self.save_config()
            edit_videos = os.listdir(videos_folder)
            edit_videos = [k for k in edit_videos if k.endswith('.mp4')]
            if len(edit_videos) == 0:
                self.noti(f"Không tìm thấy video trong thư mục {videos_folder}")
                return
            list_edit_finished = []
            for i, video_file in enumerate(edit_videos):
                if self.is_stop_edit:
                    return
                video_path = f'{videos_folder}\\{video_file}'
                if self.is_169_to_916:
                    is_edit_ok = convert_video_169_to_916(video_path, zoom_size=zoom_size, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'])
                else:
                    is_edit_ok = convert_video_916_to_169(video_path, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'])
                if is_edit_ok:
                    list_edit_finished.append(video_file)
            cnt = len(list_edit_finished)
            if cnt > 0:
                self.noti(f"Xử lý thành công {cnt} video: {list_edit_finished}")
        except:
            getlog()

    def open_edit_video_window(self):
        self.reset()
        self.is_edit_video_window = True
        self.setting_window_size()
        self.show_window()
        self.end_cut_var, self.first_cut_var = create_frame_label_input_input(self.root, label_text="Cắt ở đầu/cuối video (s)", width=self.width, left=0.4, mid=0.28, right=0.32)
        self.first_cut_var.insert(0, self.config['first_cut'])
        self.end_cut_var.insert(0, self.config['end_cut'])
        self.flip_video_var = self.create_settings_input("Lật ngang video", "flip_video", values=["Yes", "No"])
        self.speed_up_var = self.create_settings_input("Tăng tốc", "speed_up", values=["0.8", "0.9", "1", "1.1", "1.2"])
        self.max_zoom_size_var = self.create_settings_input("Tỷ lệ Zoom", "max_zoom_size", values=["1", "1.1", "1.2", "1.3", "1.4"])
        self.is_random_zoom_var = self.create_settings_input("Zoom ngẫu nhiên (xử lý chậm)", "is_random_zoom")
        self.is_random_zoom_var.delete(0, ctk.END)
        self.is_random_zoom_var.insert(0, "3-5")
        self.horizontal_position_var = self.create_settings_input("Vị trí zoom theo chiều ngang", "horizontal_position", values=["left", "center", "right"])
        self.vertical_position_var = self.create_settings_input("Vị trí zoom theo chiều dọc", "vertical_position", values=["top", "center", "bottom"])
        self.top_bot_overlay_var = self.create_settings_input("Chiều cao lớp phủ trên, dưới(vd: 100,50)", "top_bot_overlay", values=["50", "100", "150"])
        self.left_right_overlay_var = self.create_settings_input("Chiều cao lớp phủ trái, phải(vd: 100,50)", "left_right_overlay", values=["50", "100", "150"])
        self.is_delete_original_audio_var = self.create_settings_input("Xóa audio gốc", "is_delete_original_audio", values=["Yes", "No"])
        self.background_music_path, self.background_music_volume_var = create_frame_button_input_input(self.root,text="Chọn thư mục chứa nhạc nền", width=self.width, command= self.choose_background_music_folder, place_holder1="Đường dẫn thư mục chứa file mp3", place_holder2="âm lượng")
        self.background_music_path.insert(0, self.config['background_music_path'])
        self.background_music_volume_var.insert(0, self.config['background_music_volume'])
        self.water_path_var = create_frame_button_and_input(self.root,text="Chọn ảnh Watermark", width=self.width, command= self.choose_water_mask_image, left=0.4, right=0.6)
        self.vertical_watermark_position_var, self.horizontal_watermark_position_var = create_frame_label_input_input(self.root, "Vị trí Watermark (ngang - dọc)", place_holder1="nhập vị trí chiều ngang", place_holder2="Nhập vị trí chiều dọc", width=self.width, left=0.4, mid=0.28, right=0.32)
        self.horizontal_watermark_position_var.insert(0, self.config['horizontal_watermark_position'])
        self.vertical_watermark_position_var.insert(0, self.config['vertical_watermark_position'])
        self.watermark_scale_var = self.create_settings_input("Chỉnh kích thước Watermark (ngang - dọc)", config_key='watermark_scale')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa video", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        self.water_path_var.insert(0, self.config['water_path'])
        self.videos_edit_folder_var.insert(0, self.config['videos_edit_folder'])
        create_frame_button_and_button(self.root, text1="Xử lý video", text2="Xử lý video nhanh", command1=self.start_edit_video_slow, command2=self.start_edit_video_fast, width=self.width, left=0.5, right=0.5)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)

    def start_edit_video_slow(self):
        self.is_fast_edit = False
        self.create_thread_edit_video()
    def start_edit_video_fast(self):
        self.is_fast_edit = True
        self.create_thread_edit_video()
    def create_thread_edit_video(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.is_stop_edit = False
            self.edit_thread = threading.Thread(target=self.start_edit_video)
            self.edit_thread.start()

    def create_thread_combine_video(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.edit_thread = threading.Thread(target=self.combine_video_by_ffmpeg)
            self.edit_thread.start()
    def create_thread_increse_video_quality(self):
        if not self.edit_thread or not self.edit_thread.is_alive():
            self.edit_thread = threading.Thread(target=self.increse_video_quality_by_ffmpeg)
            self.edit_thread.start()

    def start_edit_video(self):
        def save_edit_setting():
            self.config['videos_edit_folder'] = self.videos_edit_folder_var.get()
            self.config['is_delete_original_audio'] = self.is_delete_original_audio_var.get() == "Yes"
            self.config['background_music_path'] = self.background_music_path.get()
            self.config['background_music_volume'] = self.background_music_volume_var.get()
            self.config['first_cut'] = self.first_cut_var.get()
            self.config['end_cut'] = self.end_cut_var.get()
            self.config['flip_video'] = self.flip_video_var.get() == "Yes"
            self.config['speed_up'] = self.speed_up_var.get()
            self.config['max_zoom_size'] = self.max_zoom_size_var.get()
            self.config['is_random_zoom'] = self.is_random_zoom_var.get()
            self.config['vertical_position'] = self.vertical_position_var.get()
            self.config['horizontal_position'] = self.horizontal_position_var.get()
            self.config['water_path'] = self.water_path_var.get()
            self.config['vertical_watermark_position'] = self.vertical_watermark_position_var.get()
            self.config['horizontal_watermark_position'] = self.horizontal_watermark_position_var.get()
            self.config['watermark_scale'] = self.watermark_scale_var.get()
            if not self.config['watermark_scale']:
                self.config['watermark_scale'] = "1,1"
            self.config['top_bot_overlay'] = self.top_bot_overlay_var.get()
            self.config['left_right_overlay'] = self.left_right_overlay_var.get()
            if not self.config['videos_edit_folder']:
                self.noti("Hãy chọn thư mục lưu video.")
                return
            try:
                if not self.config['max_zoom_size'] or float(self.config['max_zoom_size']) <= 1:
                    self.config['max_zoom_size'] = "1.01"
            except:
                self.config['max_zoom_size'] = "1.01"
            self.save_config()
        save_edit_setting()
        videos_folder = self.config['videos_edit_folder']
        list_edit_finished = []
        edit_videos = get_file_in_folder_by_type(videos_folder, ".mp4")
        if not edit_videos:
            return
        
        for i, video_file in enumerate(edit_videos):
            if self.is_stop_edit:
                return
            if '.mp4' not in video_file:
                continue
            print(f'Bắt đầu xử lý video: {video_file}')
            video_path = f'{videos_folder}\\{video_file}'
            if self.is_fast_edit:
                is_edit_ok = self.fast_edit_video(video_path)
            else:
                is_edit_ok = self.edit_video_by_moviepy(video_path)
            if is_edit_ok:
                list_edit_finished.append(video_file)
                print(f"  --> Xử lý thành công video: {video_file}")
        cnt = len(list_edit_finished)
        if cnt > 0:
            self.noti(f"Chỉnh sửa thành công {cnt} video")


    def fast_edit_video(self, input_video_path):
        speed_up = self.config.get('speed_up', '1')
        if not speed_up:
            speed_up = '1'
        first_cut = self.config.get('first_cut', '0')
        end_cut = self.config.get('end_cut', '0')
        zoom_size = self.config.get('max_zoom_size', '1')
        horizontal_position = self.config.get('horizontal_position', 'center')
        vertical_position = self.config.get('vertical_position', 'center')
        watermark = self.config.get('water_path', None)
        horizontal_watermark_position = self.config.get('horizontal_watermark_position', 'center')
        vertical_watermark_position = self.config.get('vertical_watermark_position', 'center')
        watermark_scale = self.config.get('watermark_scale', '1,1')
        flip_horizontal = self.config.get('flip_video', False)
        top_bot_overlay = self.config.get('top_bot_overlay', '2,2')
        left_right_overlay = self.config.get('left_right_overlay', '2,2')
        new_audio_folder = self.config.get('background_music_path', None)
        new_audio_path = None
        if new_audio_folder and os.path.exists(new_audio_folder):
            new_audio_path = get_random_audio_path(new_audio_folder)
            if not os.path.exists(new_audio_path):
                print(f"Không có file .mp3 nào trong thư mục {new_audio_folder}")
                return
        background_music_volume = self.config.get('background_music_volume', '100')
        remove_original_audio = self.config.get('is_delete_original_audio', False)

        try:
            audio_volume = int(background_music_volume)/100
        except:
            audio_volume = 1.0

        try:
            top_bot = top_bot_overlay.split(',')
            top_overlay, bot_overlay = top_bot[0], top_bot[1]
            if int(top_overlay) == 0:
                top_overlay = 1
            if int(bot_overlay) == 0:
                bot_overlay = 1
        except:
            top_overlay = bot_overlay = 1

        try:
            left_right = left_right_overlay.split(',')
            left_overlay, right_overlay = left_right[0], left_right[1]
            if int(left_overlay) == 0:
                left_overlay = 1
            if int(right_overlay) == 0:
                right_overlay = 1
        except:
            left_right = right_overlay = 1

        try:
            output_folder, file_name = get_output_folder(input_video_path, output_folder_name='edited_videos')
            file_name = file_name.split('.mp4')[0]
            output_file = os.path.join(output_folder, f"{file_name}.mp4")
            video_info = get_video_info(input_video_path)
            if not video_info:
                print(f"Không lấy được thông tin từ video {input_video_path}, hãy đảm bảo rằng video không bị hỏng.")
                return
            video_width = video_info['width']
            video_height = video_info['height']
            video_duration = float(video_info.get('duration', None))
            if not video_duration:
                return
            video_fps = video_info['fps']
            if speed_up:
                try:
                    speed_up = float(speed_up)
                except:
                    speed_up = 1.01
            duration = video_duration/speed_up

            first_cut = convert_time_to_seconds(first_cut)/speed_up
            end_cut = convert_time_to_seconds(end_cut)/speed_up
            if not end_cut or end_cut >= duration:
                end_cut = 0
            if not first_cut or first_cut >= duration - end_cut:
                first_cut = 0
            end_cut = duration - end_cut

            if watermark:
                if os.path.isfile(watermark):
                    watermark_x, watermark_y = add_watermark_by_ffmpeg(video_width, video_height, horizontal_watermark_position, vertical_watermark_position)
                    if watermark_x is None or watermark_y is None:
                        print("Có lỗi trong khi lấy vị trí watermark. Hãy đảm bảo thông số đầu vào chính xác!")
                        return
                else:
                    self.noti("Đường dẫn watermark không hợp lệ")
                    return

            if zoom_size:
                try:
                    zoom_size = float(zoom_size)
                except:
                    zoom_size = 1.01

            if horizontal_position == 'center':
                zoom_x = int(video_width * (1 - 1 / zoom_size) / 2)
            elif horizontal_position == 'left':
                zoom_x = 0
            elif horizontal_position == 'right':
                zoom_x = int(video_width * (1 - 1 / zoom_size))
            else:
                try:
                    zoom_x = int(video_width * horizontal_position / 100)
                except:
                    print("Vị trí zoom theo chiều ngang không hợp lệ. Lấy mặc định zoom từ trung tâm")
                    zoom_x = int(video_width * (1 - 1 / zoom_size) / 2)

            if vertical_position == 'center':
                zoom_y = int(video_height * (1 - 1 / zoom_size) / 2)
            elif vertical_position == 'top':
                zoom_y = 0
            elif vertical_position == 'bottom':
                zoom_y = int(video_height * (1 - 1 / zoom_size))
            else:
                try:
                    zoom_y = int(video_height * vertical_position / 100)
                except:
                    print("Vị trí zoom theo chiều dọc không hợp lệ. Lấy mặc định zoom từ trung tâm")
                    zoom_y = int(video_height * (1 - 1 / zoom_size) / 2)

            flip_filter = ''
            if flip_horizontal:
                flip_filter += ',hflip'

            top_black_bar = f"drawbox=x=0:y=0:w=iw:h={top_overlay}:color=black:t=fill"
            bottom_black_bar = f"drawbox=x=0:y=ih-{bot_overlay}:w=iw:h={bot_overlay}:color=black:t=fill"
            left_black_bar = f"drawbox=x=0:y=0:w={left_overlay}:h=ih:color=black:t=fill"
            right_black_bar = f"drawbox=x=iw-{right_overlay}:y=0:w={right_overlay}:h=ih:color=black:t=fill"

            zoom_filter = f"scale=iw*{zoom_size}:ih*{zoom_size},crop={int(video_width*0.999)}:{int(video_height*0.999)}:{zoom_x}:{zoom_y}{flip_filter}"

            if watermark:
                try:
                    watermark_scale = watermark_scale.split(',')
                    scale_w = float(watermark_scale[0])
                    scale_h = float(watermark_scale[1])
                except:
                    scale_w = 1
                    scale_h = 1
                watermark_filter = f"[0:v]{zoom_filter},{top_black_bar},{bottom_black_bar},{left_black_bar},{right_black_bar},setpts=PTS/{speed_up}[v];[1:v]scale=iw*{scale_w}:ih*{scale_h},format=yuva420p[wm];[v][wm]overlay={watermark_x}:{watermark_y}[video]"
            else:
                watermark_filter = f"[0:v]{zoom_filter},{top_black_bar},{bottom_black_bar},{left_black_bar},{right_black_bar},setpts=PTS/{speed_up}[video]"
            combined_audio_path = os.path.join(output_folder, "combined_audio.wav")
            temp_audio_path = os.path.join(output_folder, "new_combined_audio.wav")
            if new_audio_path:
                audio_duration_info = get_audio_info(new_audio_path)
                audio_duration = float(audio_duration_info.get('duration', 0))
                if audio_duration < video_duration:
                    repeat_count = int(video_duration / audio_duration) + 1
                    loop_audio_command = [
                        'ffmpeg',
                        '-loglevel', 'quiet',
                        '-stream_loop', str(repeat_count - 1),  # Lặp lại âm thanh
                        '-i', new_audio_path,
                        '-t', str(video_duration),  # Giới hạn thời gian phát lại âm thanh
                        '-y', temp_audio_path
                    ]
                    if not run_command_ffmpeg(loop_audio_command):
                        return
                    new_audio_path = temp_audio_path
                combine_audio_command = [
                    'ffmpeg',
                    '-loglevel', 'quiet',
                    '-i', input_video_path,   # Đầu vào video để lấy âm thanh gốc
                    '-i', new_audio_path,     # Đầu vào âm thanh mới
                    '-filter_complex', f'[0:a]volume=1[a1];[1:a]volume={audio_volume}[a2];[a1][a2]amerge=inputs=2[a]',
                    '-map', '[a]',
                    '-ac', '2',  # Đảm bảo đầu ra âm thanh có 2 kênh
                    '-y', combined_audio_path
                ]
                run_command_ffmpeg(combine_audio_command)

            command = [
                'ffmpeg',
                '-progress', 'pipe:1',
            ]
            if first_cut > 0:
                command.extend(['-ss', str(first_cut)])
            command.extend(['-i', input_video_path])
            if watermark:
                command.extend(['-i', watermark])
            audio_index = 1
            if new_audio_path:
                if remove_original_audio:
                    command.extend(['-i', new_audio_path])
                else:
                    command.extend(['-i', combined_audio_path]) 
            if watermark and new_audio_path:
                audio_index = 2

            command.extend(['-filter_complex', watermark_filter])
            if new_audio_path:
                if remove_original_audio:
                    command.extend([
                        '-map', '[video]',
                        f'-map', f'{audio_index}:a',  # Âm thanh mới
                        '-filter:a:0', f'volume={audio_volume},atempo={speed_up}',  # Chỉnh âm lượng âm thanh mới
                    ])
                else:
                    command.extend([
                        '-map', '[video]',
                        f'-map', f'{audio_index}:a',  # Âm thanh kết hợp
                        '-filter:a:0', f'volume=1,atempo={speed_up}',
                    ])
            elif not remove_original_audio:
                command.extend([
                    '-map', '[video]',
                    '-map', '0:a',  # Âm thanh gốc
                    '-filter:a', f'volume=1,atempo={speed_up}',  # Chỉnh âm lượng âm thanh gốc
                ])
            else:
                command.extend([
                    '-map', '[video]',
                    '-an'  # Loại bỏ âm thanh gốc
                ])
            command.extend([
                '-vcodec', 'libx264',  # Sử dụng codec H.264
                '-acodec', 'aac',      # Sử dụng codec âm thanh AAC
                '-r', f'{video_fps + 1}',
                '-y',
            ])
            if end_cut is not None:
                duration = end_cut - first_cut
                command.extend(['-to', str(duration)])
            command.append(output_file)
            if not run_command_with_progress(command, duration):
                if not run_command_ffmpeg(command):
                    return False
            remove_file(combined_audio_path)
            remove_file(temp_audio_path)
            remove_or_move_file(input_video_path, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'], finish_folder_name='Finished Edit')
            return True
        except:
            print(f"Có lỗi trong quá trình xử lý video {input_video_path}")
            getlog()
            return False


    def edit_video_by_moviepy(self, input_video_path):
        try:
            new_audio_folder = self.config.get('background_music_path', None)
            new_audio_path = None
            if new_audio_folder and os.path.exists(new_audio_folder):
                new_audio_path = get_random_audio_path(new_audio_folder)
                if not os.path.exists(new_audio_path):
                    print(f"Không có file .mp3 nào trong thư mục {new_audio_folder}")
                    return
            output_folder, file_name = get_output_folder(input_video_path, output_folder_name='edited_videos')
            file_name = file_name.split('.mp4')[0]
            output_file = os.path.join(output_folder, f"{file_name}.mp4")
            
            input_clip = VideoFileClip(input_video_path)
            resized_clip = resize_clip(input_clip)
            if not resized_clip:
                resized_clip = input_clip
            if self.config['flip_video']:
                f_clip = flip_clip(resized_clip)
            else:
                f_clip = resized_clip
            video_clip = strip_first_and_end_video(f_clip, first_cut=self.config['first_cut'], end_cut=self.config['end_cut'])
            if not video_clip:
                return
            if self.config['is_delete_original_audio']:
                video_clip = remove_audio_from_clip(video_clip)
            if new_audio_path:
                add_audio_clip = set_audio_for_clip(video_clip, new_audio_path, self.config['background_music_volume'])
            else:
                add_audio_clip = video_clip
            speed_clip = speed_up_clip(add_audio_clip, speed=self.config['speed_up'])
            if self.config['is_random_zoom']:
                zoom_clip = zoom_video_random_intervals(clip=speed_clip, max_zoom_size=self.config['max_zoom_size'], vertical_position=self.config['vertical_position'], horizontal_position=self.config['horizontal_position'], is_random_zoom=self.config['is_random_zoom'])
            else:
                zoom_clip = apply_zoom(clip=speed_clip, zoom_factor=self.config['max_zoom_size'], vertical_position=self.config['vertical_position'], horizontal_position=self.config['horizontal_position'])
            if not zoom_clip:
                return
            water_clip = add_image_watermark_into_video(zoom_clip, top_bot_overlay_height=self.config['top_bot_overlay'], left_right_overlay_width=self.config['left_right_overlay'], watermark=self.config['water_path'], vertical_watermark_position=self.config['vertical_watermark_position'], horizontal_watermark_position=self.config['horizontal_watermark_position'], watermark_scale=self.config['watermark_scale'])
            if self.is_stop_edit:
                water_clip.close()
                input_clip.close()
                return

            water_clip.write_videofile(output_file, codec='libx264', threads=4, fps=input_clip.fps + 1)
            water_clip.close()
            input_clip.close()
            sleep(1)
            remove_or_move_file(input_video_path, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'])
            return True
        except:
            getlog()
            return False
    
#---------------------------Các Hàm gọi chung co class----------------------------------
    def load_download_info(self):
        self.download_info = get_json_data(download_info_path)
        if not self.download_info:
            self.download_info = {}
        if 'downloaded_urls' not in self.download_info:
            self.download_info['downloaded_urls'] = []
        save_to_json_file(self.download_info, download_info_path)

    def get_youtube_config(self):
        self.youtube_config = get_json_data(youtube_config_path)

    def get_tiktok_config(self):
        self.tiktok_config = get_json_data(tiktok_config_path)

    def get_facebook_config(self):
        self.facebook_config = get_json_data(facebook_config_path)

    def save_youtube_config(self):
        save_to_json_file(self.youtube_config, youtube_config_path)
    def save_tiktok_config(self):
        save_to_json_file(self.tiktok_config, tiktok_config_path)
    def save_facebook_config(self):
        save_to_json_file(self.facebook_config, facebook_config_path)

    def open_common_settings(self):
        def save_common_config():
            self.config["auto_start"] = self.auto_start_var.get() == "Yes"
            self.config["auto_upload_youtube"] = self.auto_upload_youtube_var.get() == "Yes"
            self.config["auto_upload_facebook"] = self.auto_upload_facebook_var.get() == "Yes"
            self.config["auto_upload_tiktok"] = self.auto_upload_tiktok_var.get() == "Yes"
            self.config["time_check_auto_upload"] = self.time_check_auto_upload_var.get()
            self.config["time_check_status_video"] = self.time_check_status_video_var.get()
            self.config["is_delete_video"] = self.is_delete_video_var.get() == "Yes"
            self.config['is_move'] = self.is_move_video_var.get() == "Yes"
            self.save_config()
            self.save_youtube_config()
            self.save_tiktok_config()
            self.save_facebook_config()
            self.get_start_window()
        self.reset()
        self.is_open_common_setting = True
        self.show_window()
        self.setting_window_size()
        self.auto_start_var = self.create_settings_input("Khởi động ứng dụng cùng window", "auto_start", values=["Yes", "No"], left=0.4, right=0.6)
        self.auto_upload_youtube_var = self.create_settings_input("Tự động đăng video youtube", "auto_upload_youtube", values=["Yes", "No"], left=0.4, right=0.6)
        self.auto_upload_facebook_var = self.create_settings_input("Tự động đăng video facebook", "auto_upload_facebook", values=["Yes", "No"], left=0.4, right=0.6)
        self.auto_upload_tiktok_var = self.create_settings_input("Tự động đăng video tiktok", "auto_upload_tiktok", values=["Yes", "No"], left=0.4, right=0.6)
        self.time_check_auto_upload_var = self.create_settings_input("Khoảng thời gian kiểm tra và tự động đăng video (phút)", "time_check_auto_upload", values=["0", "60"], left=0.4, right=0.6)
        self.time_check_status_video_var = self.create_settings_input("Khoảng cách mỗi lần kiểm tra trạng thái video (phút)", "time_check_status_video", values=["0", "60"], left=0.4, right=0.6)
        self.is_delete_video_var = self.create_settings_input("Xóa video gốc sau chỉnh sửa", "is_delete_video", values=["Yes", "No"], left=0.4, right=0.6)
        self.is_move_video_var = self.create_settings_input("Di chuyển video gốc sau chỉnh sửa", "is_move", values=["Yes", "No"], left=0.4, right=0.6)
        create_button(self.root, text="Lưu cài đặt", command=save_common_config, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)
        

    def choose_background_music_folder(self):
        background_music_folder = choose_folder()
        self.background_music_path.delete(0, ctk.END)
        self.background_music_path.insert(0, background_music_folder)

    def choose_videos_edit_folder(self):
        videos_edit_folder = filedialog.askdirectory()
        if self.videos_edit_folder_var:
            self.videos_edit_folder_var.delete(0, ctk.END)
            self.videos_edit_folder_var.insert(0, videos_edit_folder)

    def choose_videos_edit_file(self):
        videos_edit_path = choose_file()
        self.videos_edit_path_var.delete(0, ctk.END)
        self.videos_edit_path_var.insert(0, videos_edit_path)

    def choose_water_mask_image(self):
        water_mask_image = filedialog.askopenfilename()
        self.water_path_var.delete(0, ctk.END)
        self.water_path_var.insert(0, water_mask_image)

#------------------------------------------------------Common-----------------------------------------------------
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
    
    def reset(self):
        self.is_setting = False
        self.is_youtube_window = False
        self.is_tiktok_window = False
        self.is_facebook_window= False
        self.is_edit_video_window= False
        self.is_edit_video_window= False
        self.is_add_new_channel= False
        self.is_remove_channel= False
        self.is_sign_up_facebook = False
        self.is_sign_up_tiktok = False
        self.is_convert_video_window = False
        self.is_open_common_setting = False
        self.is_open_edit_video_menu = False
        self.is_cut_video_window = False
        self.is_text_to_mp3_window = False
        self.is_combine_video_window = False
        self.is_increse_video_quality_window = False
        self.is_rename_file_by_index_window = False
        self.is_remove_char_in_file_name_window = False
        self.is_open_register_mac_addres_window = False
        self.is_extract_image_from_video_window = False
        self.is_other_window = False
        self.is_other_download_window = False
        self.is_download_douyin_video_window = False
        self.is_edit_audio_window = False
        self.is_edit_audio_option = False
        self.is_extract_audio_option = False
        self.clear_after_action()
        clear_widgets(self.root)
        self.videos_edit_folder_var = None
        self.file_name_var = None
        self.index_file_name_var = None

    def clear_after_action(self):
        self.root.withdraw()
    
    def noti(self, message):
        notification(parent=self.root, message=message)
        
    def save_config(self):
        save_to_json_file(self.config, config_path)
        
    def create_icon(self):
        try:
            icon_path = os.path.join(current_dir, 'import' , 'icon.png')
            if not os.path.exists(icon_path):
                icon_path = None
            image = self.create_image(icon_path)
            menu = (
                item("Hiển thị menu", self.get_start_window),
                item("Dừng tiến trình tải video/audio", self.stop_download),
                item("Dừng tiến trình đăng video", self.stop_upload),
                item("Dừng tiến trình chỉnh sửa video", self.stop_edit_videos),
                item("Dừng tất cả tiến trình đang chạy", self.stop_all_process),
                item("Thoát ứng dụng", self.exit_app),
            )
            self.icon = pystray.Icon("Super Social Media", image, "Super Social Media", menu)
            tray_thread = threading.Thread(target=self.icon.run_detached)
            tray_thread.daemon = True
            tray_thread.start()
        except:
            getlog()

    def stop_download(self):
        self.is_stop_download = True
        if self.youtube:
            self.youtube.is_stop_download = True
        if self.facebook:
            self.facebook.is_stop_download = True
        if self.tiktok:
            self.tiktok.is_stop_download = True
        print("Đã dừng quá trình tải video (những file đang tải sẽ không hủy được, nếu muốn dừng thì phải khởi động lại chương trình)")
    def stop_upload(self):
        self.is_stop_upload = True
        if self.youtube:
            self.youtube.is_stop_upload = True
        if self.facebook:
            self.facebook.is_stop_upload = True
        if self.tiktok:
            self.tiktok.is_stop_upload = True
        print("Đã dừng quá trình đăng video (những video đang đăng sẽ không hủy được, nếu muốn dừng thì phải khởi động lại chương trình)")
    def stop_edit_videos(self):
        self.is_stop_edit = True
        print("Đã dừng quá trình chỉnh sửa video (những video đang chỉnh sửa sẽ không dừng được, nếu muốn dừng thì phải khởi động lại chương trình)")

    def stop_all_process(self):
        self.stop_download()
        self.stop_upload()
        self.stop_edit_videos()
        if self.config['time_check_auto_upload']:
            self.config['time_check_auto_upload'] = "0"
            self.save_config()
        print("Đã dừng tất cả các chương trình")

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
        self.root.withdraw()

    def on_close(self):
        self.save_config()
        self.hide_window()
    
    def close(self):
        if self.driver:
            self.driver.close()
#----------------------------------Setting Window--------------------------------------------------------
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
                self.height_window = 266
            elif self.is_remove_channel:
                self.root.title("Add New Youtube Channel")
                self.width = 500
                self.height_window = 217
                self.is_remove_channel = False
            elif self.is_open_common_setting:
                self.root.title("Common Setting")
                self.width = 700
                self.height_window = 555
                self.is_open_common_setting = False
            elif self.is_edit_video_window:
                self.root.title("Edit Videos")
                self.width = 700
                self.height_window = 895
                self.is_edit_video_window = False
            elif self.is_open_edit_video_menu:
                self.root.title("Edit Video Window")
                self.width = 500
                self.height_window = 342
                self.is_open_edit_video_menu = False
            elif self.is_convert_video_window:
                self.root.title("Convert Videos Window")
                self.width = 500
                self.height_window = 315
                self.is_convert_video_window = False
            elif self.is_cut_video_window:
                self.root.title("Cut Video Window")
                self.width = 500
                self.height_window = 457
                self.is_cut_video_window = False
            elif self.is_combine_video_window:
                self.root.title("Combine Video Window")
                self.width = 500
                self.height_window = 315
                self.is_combine_video_window = False
            elif self.is_increse_video_quality_window:
                self.root.title("Increse Video Quality Window")
                self.width = 500
                self.height_window = 218
                self.is_increse_video_quality_window = False
            elif self.is_edit_audio_window:
                self.root.title("Edit Audio Window")
                self.width = 500
                self.height_window = 258
                self.is_edit_audio_window = False
            elif self.is_edit_audio_option:
                self.root.title("Edit Audio Option")
                self.width = 500
                self.height_window = 458
                self.is_edit_audio_option = False
            elif self.is_extract_audio_option:
                self.root.title("Extract Audio Option")
                self.width = 500
                self.height_window = 458
                self.is_extract_audio_option = False
            elif self.is_text_to_mp3_window:
                self.root.title("Text to MP3 window")
                self.width = 500
                self.height_window = 314
                self.is_text_to_mp3_window = False
            elif self.is_youtube_window:
                self.root.title("Youtube Window")
                self.width = 500
                self.height_window = 355
                self.is_youtube_window = False
            elif self.is_sign_up_youtube:
                self.root.title("Sign Up Youtube")
                self.width = 500
                self.height_window = 265
                self.is_sign_up_youtube = False
            elif self.is_facebook_window:
                self.root.title("Facebook Window")
                self.width = 500
                self.height_window = 355
                self.is_facebook_window = False
            elif self.is_sign_up_facebook:
                self.root.title("Sign Up Facebook")
                self.width = 500
                self.height_window = 313
                self.is_sign_up_facebook = False
            elif self.is_tiktok_window:
                self.root.title("Tiktok Window")
                self.width = 500
                self.height_window = 307
                self.is_tiktok_window = False
            elif self.is_sign_up_tiktok:
                self.root.title("Sign Up Tiktok")
                self.width = 500
                self.height_window = 265
                self.is_sign_up_tiktok = False
            elif self.is_rename_file_by_index_window:
                self.root.title("Rename Files")
                self.width = 500
                self.height_window = 361
                self.is_rename_file_by_index_window = False
            elif self.is_remove_char_in_file_name_window:
                self.root.title("Remove Char in Files")
                self.width = 500
                self.height_window = 315
                self.is_remove_char_in_file_name_window = False
            elif self.is_extract_image_from_video_window:
                self.root.title("Extract Image From Video")
                self.width = 500
                self.height_window = 265
                self.is_extract_image_from_video_window = False
            elif self.is_open_register_mac_addres_window:
                self.root.title("Change Mac Address")
                self.width = 500
                self.height_window = 365
                self.is_open_register_mac_addres_window = False
            elif self.is_other_window:
                self.root.title("Other")
                self.width = 500
                self.height_window = 303
                self.is_other_window = False
            elif self.is_other_download_window:
                self.root.title("Other Download Window")
                self.width = 500
                self.height_window = 263
                self.is_other_download_window = False
            elif self.is_download_douyin_video_window:
                self.root.title("Download Douyin Video")
                self.width = 500
                self.height_window = 215
                self.is_download_douyin_video_window = False

        self.setting_screen_position()


    def open_rename_file_by_index_window(self):
        self.reset()
        self.is_rename_file_by_index_window = True
        self.setting_window_size()
        self.file_name_var = create_frame_label_and_input(self.root, label_text="Tên file muốn đổi", place_holder="Tên file có chứa \"<index>\" làm vị trí đặt số", width=self.width, left=0.4, right=0.6)
        self.index_file_name_var = create_frame_label_and_input(self.root, label_text="Số thứ tự bắt đầu", width=self.width, left=0.4, right=0.6)
        self.index_file_name_var.insert(0, '1')
        self.file_name_extension_var = create_frame_label_and_input(self.root, label_text="Loại file muốn đổi tên", width=self.width, left=0.4, right=0.6)
        self.file_name_extension_var.insert(0, '.mp4')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa File", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Đổi Tên", command= self.rename_file_by_index)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def extract_image_from_video_window(self):
        self.reset()
        self.is_extract_image_from_video_window = True
        self.setting_window_size()
        self.image_position_var = create_frame_label_and_input(self.root, label_text="Chọn vị trí trích xuất ảnh", width=self.width, left=0.4, right=0.6, place_holder='Ví dụ: 00:40 hoặc 00:10:15')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa Video", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Trích Xuất Ảnh", command= self.extract_image_from_video)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def open_remove_char_in_file_name_window(self):
        self.reset()
        self.is_remove_char_in_file_name_window = True
        self.setting_window_size()
        self.char_want_to_remove_var = create_frame_label_and_input(self.root, label_text="Nhập các ký tự muốn loại bỏ", width=self.width, left=0.4, right=0.6, place_holder='Ví dụ: .,-,#')
        self.file_name_extension_var = create_frame_label_and_input(self.root, label_text="Loại file muốn đổi tên", width=self.width, left=0.4, right=0.6)
        self.file_name_extension_var.insert(0, '.mp4')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa File", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Đổi Tên", command= self.remove_char_in_file_name)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def open_register_mac_addres_window(self):
        if not self.is_start_app:
            self.reset()
        self.is_open_register_mac_addres_window = True
        self.show_window()
        self.setting_window_size()

        def sign_up_mac_address():
            print("chưa kết nối server")

        def change_mac_address_now():
            print("chưa kết nối server")

        def change_mac_address_window():
            self.reset()
            self.is_open_register_mac_addres_window = True
            self.show_window()
            self.setting_window_size()
            self.get_mac_address_var = create_frame_label_and_input(self.root, label_text="Nhập mã máy cũ",  width=self.width, left=0.4, right=0.6)
            self.pass_mac_var = create_frame_label_and_input(self.root, label_text="Nhập mật mã xác nhận", width=self.width, left=0.4, right=0.6)
            self.get_mac_address_var = create_frame_label_and_input(self.root, label_text="Nhập mã máy mới",  width=self.width, left=0.4, right=0.6)
            create_button(frame=self.root, text="Đổi thông tin ngay", command= change_mac_address_now, width=self.width)
            create_button(self.root, text="Lùi lại", command=self.open_register_mac_addres_window, width=self.width)

        self.app_account_var = create_frame_label_and_input(self.root, label_text="Tài khoản telegram (user_name)",  width=self.width, left=0.4, right=0.6)
        self.pass_mac_var = create_frame_label_and_input(self.root, label_text="Tạo mật mã xác nhận", width=self.width, left=0.4, right=0.6)
        self.deadline_var = create_frame_label_and_input(self.root, label_text="Nhập số tháng đã đăng ký", width=self.width, left=0.4, right=0.6)
        self.deadline_var = create_frame_label_and_input(self.root, label_text="Nhập mã giới thiệu(user_name telegram)", width=self.width, left=0.4, right=0.6)
        self.get_mac_address_var = create_frame_button_and_input(self.root, text="Lấy mã máy", command=self.get_mac_address_now, width=self.width, left=0.4, right=0.6)
        create_button(frame=self.root, text="Gửi đăng ký và chờ duyệt (duyệt trong vòng 24h)", command= sign_up_mac_address, width=self.width)
        if is_registed_mac_address:
            create_button(frame=self.root, text="Đổi thông tin", command= change_mac_address_window, width=self.width)
            

    def rename_file_by_index(self):
        base_name = self.file_name_var.get()
        index = self.index_file_name_var.get()
        extension = self.file_name_extension_var.get()
        videos_folder = self.videos_edit_folder_var.get()
        if self.check_folder(videos_folder):
            rename_files_by_index(videos_folder, base_name, extension, index)
    
    def get_mac_address_now(self):
        mac = get_disk_serial()
        self.get_mac_address_var.delete(0, ctk.END)
        self.get_mac_address_var.insert(0, mac)

    def remove_char_in_file_name(self):
        chars_want_to_remove = self.char_want_to_remove_var.get()
        extension = self.file_name_extension_var.get()
        videos_folder = self.videos_edit_folder_var.get()
        if not chars_want_to_remove:
            self.noti("Hãy nhập các ký tự muốn loại bỏ và cách nhau bởi dấu \",\". Ví dụ:  \".,#\"")
            return
        if self.check_folder(videos_folder):
            remove_char_in_file_name(folder_path=videos_folder, chars_want_to_remove=chars_want_to_remove, extension=extension)

    def extract_image_from_video(self):
        position = self.image_position_var.get().strip()
        videos_folder = self.videos_edit_folder_var.get()
        if not position:
            self.noti("Hãy nhập vị trí thời gian muốn trích xuất ảnh")
            return
        if self.check_folder(videos_folder):
            get_image_from_video(videos_folder=videos_folder, position=position)


#-------------------------------Convert MP3------------------------------------------------
    def open_text_to_mp3_window(self):
        self.reset()
        self.is_text_to_mp3_window = True
        self.setting_window_size()
        self.file_path_get_var = create_frame_button_and_input(self.root, text="File \'.txt\' muốn chuyển đổi", command= self.choose_directory_get_txt_file, width=self.width, left=0.4, right=0.6)
        self.speed_talk_var = self.create_settings_input(label_text="Tốc độ đọc", config_key='speed_talk', values=["0.8", "0.9", "1", "1.1", "1.2"])
        self.convert_multiple_record_var = self.create_settings_input(label_text="Chế độ chuyển theo từng dòng", values=["Yes", "No"])
        self.convert_multiple_record_var.set("No")
        create_button(frame=self.root, text="Bắt đầu chuyển đổi", command= self.text_to_mp3)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)
        self.show_window()

    def choose_directory_get_txt_file(self):
        file_path_get = filedialog.askopenfilename( title="Select a txt file", filetypes=(("Text files", "*.txt"),))
        self.file_path_get_var.delete(0, ctk.END)
        self.file_path_get_var.insert(0, file_path_get)

    def text_to_mp3(self, voice=None, speed=1):
        convert_multiple_record = self.convert_multiple_record_var.get() == 'Yes'
        file_path_get = self.file_path_get_var.get()
        try:
            speed_talk = float(self.speed_talk_var.get())
        except:
            print("định dạng tốc độ đọc không đúng, lấy mặc định là 1")
            speed_talk = 1
        temp_wav_file = None
        if not file_path_get or '.txt' not in file_path_get:
            self.noti(f"Hãy chọn file \".txt\" để lấy dữ liệu muốn convert")
            return
        curren_folder, base_name = get_current_folder_and_basename(file_path_get)
        output_folder = os.path.join(curren_folder, 'convert_audio')
        os.makedirs(output_folder, exist_ok=True)
        file_path_save = os.path.join(output_folder, f"{base_name.split('.txt')[0]}.mp3")
        try:
            if not self.engine:
                self.engine = pyttsx3.init()
            if voice:
                self.engine.setProperty('voice', voice)
            self.engine.setProperty('rate', speed_talk * 140)
            text = get_txt_data(file_path_get)
            lines = text.split('\n')
            
            if convert_multiple_record:
                index = 0
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    index += 1
                    temp_file = f'temp_file_{index}.wav'
                    self.engine.save_to_file(line, temp_file)
                    self.engine.runAndWait()
                    sound = AudioSegment.from_wav(temp_file)
                    sound.export(f"{output_folder}\\{base_name.split('.txt')[0]}_{index}.mp3", format='mp3')
                    os.remove(temp_file)
                    if index == len(lines):
                        break
            else:
                temp_wav_file = f"{current_dir}\\temp_output.wav"
                text = text.strip()
                self.engine.save_to_file(text, temp_wav_file)
                self.engine.runAndWait()
                sound = AudioSegment.from_wav(temp_wav_file)
                sound.export(file_path_save, format="mp3")
                os.remove(temp_wav_file)
            print(f"File mp3 đã được lưu thành công tại thư mục: {output_folder}")
        except:
            getlog()
            self.engine.stop()
            if temp_wav_file:
                if os.path.isfile(temp_wav_file):
                    os.remove(temp_wav_file)
        self.convert_multiple_record =False

app = MainApp()
try:
    app.root.mainloop()
except:
    pass
