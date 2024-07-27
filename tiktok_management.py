from common_function import *
from common_function_CTK import *

class TikTokManager:
    def __init__(self, gmail, password, upload_thread=None):
        self.upload_thread = upload_thread
        self.tiktok_config = get_json_data(tiktok_config_path)
        self.gmail = gmail
        self.root = ctk.CTk()
        self.title = self.root.title(gmail)
        self.font_label = ctk.CTkFont(family="Arial", size=font_size)
        self.font_button = ctk.CTkFont( family="Arial", size=font_size, weight="bold" )
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.width = 500

        self.driver = None
        self.is_start_tiktok = True
        self.is_upload_video_window = False
        self.is_stop_upload = True
        self.is_stop_download = False

    def init_driver(self):
        service = Service(ChromeDriverManager().install())
        options = webdriver.ChromeOptions()
        if self.is_stop_upload:
            options.add_argument('--headless')  # Chạy ở chế độ không giao diện
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
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
                fix_hairline=True,
                )
        self.driver = driver

    def load_session(self, url="https://www.tiktok.com/login/phone-or-email/email"):
        self.driver.get(url)
        sleep(2)

        # Tải cookies
        try:
            with open(cookies_path, 'r') as file:
                cookies_info = json.load(file)
            if "tiktok" in cookies_info and self.gmail in cookies_info["tiktok"]:
                current_cookies = cookies_info["tiktok"][self.gmail]
                for cookie in current_cookies:
                    if 'domain' in cookie and cookie['domain'] in self.driver.current_url:
                        self.driver.add_cookie(cookie)
                    elif 'domain' not in cookie:
                        self.driver.add_cookie(cookie)
        except FileNotFoundError:
            pass

        # Tải local storage
        try:
            with open(local_storage_path, 'r') as file:
                local_storage_info = json.load(file)
            if "tiktok" in local_storage_info and self.gmail in local_storage_info["tiktok"]:
                local_storage = local_storage_info["tiktok"][self.gmail]
                for key, value in local_storage.items():
                    self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
        except FileNotFoundError:
            pass

    def save_session(self):
        # Lưu cookies
        try:
            with open(cookies_path, 'r') as file:
                cookies_info = json.load(file)
        except FileNotFoundError:
            cookies_info = {}
        if "tiktok" not in cookies_info:
            cookies_info["tiktok"] = {}
        cookies_info["tiktok"][self.gmail] = self.driver.get_cookies()
        with open(cookies_path, 'w') as file:
            json.dump(cookies_info, file)

        # Lưu local storage
        try:
            with open(local_storage_path, 'r') as file:
                local_storage_info = json.load(file)
        except FileNotFoundError:
            local_storage_info = {}
        if "tiktok" not in local_storage_info:
            local_storage_info["tiktok"] = {}
        local_storage = self.driver.execute_script("return {...window.localStorage};")
        local_storage_info["tiktok"][self.gmail] = local_storage
        with open(self.local_storage_path, 'w') as file:
            json.dump(local_storage_info, file)

    def login(self):
        self.is_stop_upload = False
        self.init_driver()
        self.load_session()
        sleep(1)
        self.driver.refresh()
        sleep(1)
        try:
            profile_element = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "YOUR_PROFILE_XPATH"))
            )
        except:
            if "TikTok" in self.driver.title:
                email_input = self.driver.find_element(By.ID, 'loginUsername')
                email_input.send_keys(self.gmail)
                sleep(1)
                password_input = self.driver.find_element(By.ID, 'loginPassword')
                password_input.send_keys(self.password)
                sleep(1)
                password_input.send_keys(Keys.RETURN)
                sleep(10)  # Adjust this time according to your needs
                self.save_session()
                profile_element = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "YOUR_PROFILE_XPATH"))
                )
        # Tiếp tục với các bước sau khi đăng nhập thành công

    def upload_video(self, video_file):
        self.driver.get('https://www.tiktok.com/upload')
        # Chờ cho trang tải xong
        WebDriverWait(self.driver, 30).until(EC.presence_of_element_located((By.NAME, 'video')))

        # Tải video lên
        video_input = self.driver.find_element(By.NAME, 'video')
        video_input.send_keys(video_file)
        
        # Chờ tải lên hoàn tất và thêm mô tả nếu cần
        # ...
        print("Video uploaded")

    def get_start_tiktok(self):
        self.show_window()
        self.setting_window_size()
        create_button(frame = self.root,text="Upload Videos", command= self.open_upload_video_window)
        create_button(frame = self.root,text="Download Videos From Channel", command=self.open_download_video_window)
        try:
            self.root.mainloop()
        except:
            getlog()

    def open_upload_video_window(self):
        self.login()


#--------------------------------------------------download
    def open_download_video_window(self):
            self.reset()
            self.is_download_window = True
            self.setting_window_size()
            self.show_window()

            def save_download_settings():
                if not self.output_folder:
                    warning_message("Please select the folder containing the downloaded file.")
                    return
                self.tiktok_config['output_folder'] = self.output_folder
                self.tiktok_config['download_by_channel_url'] = self.download_by_channel_url.get()
                self.tiktok_config['filter_by_like'] = self.filter_by_like_var.get()
                self.tiktok_config['filter_by_views'] = self.filter_by_views_var.get()
                self.save_config()

            def start_download_by_channel_url():
                save_download_settings()
                download_thread = threading.Thread(target=self.download_videos_by_channel_url)
                download_thread.daemon = True
                download_thread.start()          

            self.output_folder_var = create_frame_button_and_input(self.root,text="Choose folder to save", command=self.choose_folder_to_save)
            self.output_folder_var.insert(0, self.tiktok_config['output_folder'])
            self.download_by_channel_url = create_frame_button_and_input(self.root,text="Download By Channel URL", command=start_download_by_channel_url)
            self.filter_by_like_var = self.create_settings_input("Filter By Number Of Likes", "filter_by_like", values=["10000", "20000", "30000", "50000", "100000"])
            self.filter_by_views_var = self.create_settings_input("Filter By Number Of Views", "filter_by_views", values=["100000", "200000", "300000", "500000", "1000000"])

    def choose_folder_to_save(self):
        self.output_folder = filedialog.askdirectory()
        self.output_folder_var.delete(0, ctk.END)
        self.output_folder_var.insert(0, self.output_folder)

    def download_videos_by_channel_url(self):
        self.cnt_downlaod = 0
        self.list_videos_url_download = []
        channel_url = self.download_by_channel_url.get()
        if not channel_url:
            return
        self.hide_window()
        self.get_tiktok_videos_by_channel_url(channel_url=channel_url, view_cnt=self.tiktok_config['filter_by_views'], like_cnt=self.tiktok_config['filter_by_like'])
        print(f"đã tải thành công {self.cnt_downlaod} video")

    def create_thread_download(self):
        thread_download = threading.Thread(target=self.download_video_by_list_url)
        thread_download.start()
     
    def download_video_by_list_url(self):
        while True:
            if len(self.download_info['waiting_download_urls']) > 0:
                self.pre_time_download = time()
                for url in self.download_info['waiting_download_urls']:
                    try:
                        download_video_by_url(url, download_folder = self.output_folder)

                        print(f"tải thành công {url}")
                        self.cnt_downlaod += 1
                    except:
                        getlog()
                        try:
                            download_video_no_watermask_from_tiktok(url, download_folder = self.output_folder)
                            self.download_info['waiting_download_urls'].remove(url)
                            self.download_info['downloaded_urls'].append(url)
                            print(f"tải lần 2 thành công {url}")
                            self.cnt_downlaod += 1
                        except:
                            getlog()
                    self.save_download_info()
            else:
                sleep(30)
                if time() - self.pre_time_download > 10*60:
                    break

    #lấy thông tin và download video từ channel
    def get_tiktok_videos_by_channel_url(self, channel_url, view_cnt=0, like_cnt=0):
        try:
            if not channel_url:
                warning_message("please input the channel url!")
                return
            def is_recent_video(upload_date, months=2):
                try:
                    current_date = datetime.now()
                    upload_date = datetime.strptime(upload_date, '%Y%m%d')
                    return current_date - upload_date <= timedelta(days=months*30)
                except:
                    getlog()
                    return False
            self.init_driver()
            
            self.driver.get(channel_url) # Mở trang TikTok
            sleep(20)  # Đợi trang tải
            last_height = self.driver.execute_script("return document.body.scrollHeight") # Tự động cuộn trang
            while True:
                if self.is_stop_download:
                    self.close()
                    return None
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Cuộn xuống cuối trang
                sleep(5) # Đợi trang tải
                new_height = self.driver.execute_script("return document.body.scrollHeight") # Tính chiều cao mới của trang
                if new_height == last_height: # Kiểm tra nếu không có thêm nội dung mới
                    break
                last_height = new_height

            video_urls = []
            video_elements = self.driver.find_elements(By.TAG_NAME, 'a')
            for item in video_elements:
                if self.is_stop_download:
                    self.close()
                    return None
                url = item.get_attribute('href')
                if url and '/video/' in url:
                    video_urls.append(url)
            self.close()
            # Xác định tên file
            # if '@' in channel_url:
            #     folder_name = channel_url.split('@')[-1]
            print(f"tổng số url tìm được là {len(video_urls)}")
            self.download_info = get_json_data(download_info_path)
            if not self.download_info:
                self.download_info = {}
            if 'waiting_download_urls' not in self.download_info:
                self.download_info['waiting_download_urls'] = []
            if 'downloaded_urls' not in self.download_info:
                self.download_info['downloaded_urls'] = []
            self.pre_time_download = time()
            self.create_thread_download()
            for url in video_urls:
                if self.is_stop_download:
                    return None
                if url in self.download_info['downloaded_urls'] or url in self.download_info['waiting_download_urls']:
                    print("url này đã tải hoặc có trong danh sách đợi download")
                    continue
                video_info = get_info_by_url(url)
                like_count = video_info.get('like_count', 0)
                view_count = video_info.get('view_count', 0)
                upload_date = video_info.get('upload_date', None)
                # title = video_info.get('title', None)
                # description = video_info.get('description', None)
                # comment_count = video_info.get('comment_count', 0)
                # duration = video_info.get('duration', 0)
                # filesize = video_info.get('filesize', 0)
                # resolution = video_info.get('resolution', 0)
                # Check if the video meets the criteria

                view_cnt = int(view_cnt)
                like_cnt = int(like_cnt)
                if view_count > view_cnt and like_count > like_cnt:
                    pass
                elif view_count > view_cnt/3 and like_count > like_cnt/3 and is_recent_video(upload_date, months=2):
                    pass
                elif view_count > view_cnt/2 and like_count > like_cnt/2 and is_recent_video(upload_date, months=3):
                    pass
                else:
                    continue
                self.download_info['waiting_download_urls'].append(url)
        except:
            getlog()

    def close(self):
        if self.driver:
            self.driver.quit()

#common -------------------------------------------------------------------------------------------------------------
    def setting_screen_position(self):
        try:
            self.root.update_idletasks()
            x = screen_width - self.width - 10
            y = screen_height - self.height_window
            self.root.geometry(f"{self.width}x{self.height_window - 80}+{x}+{y}")
        except:
            getlog()

    def setting_window_size(self):
        if self.is_start_tiktok:
            self.root.title(f"{self.gmail}")
            self.width = 400
            self.height_window = 250
            self.is_start_tiktok = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video: {self.gmail}")
            self.width = 800
            self.height_window = 910
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos")
            self.width = 600
            self.height_window = 340
            self.is_download_window = False
        self.setting_screen_position()

    def save_config(self):
        save_to_json_file(self.tiktok_config, config_path)
    def save_download_info(self):
        save_to_json_file(self.download_info, download_info_path)

    def exit_app(self):
        self.reset()
        self.root.destroy()

    def on_close(self):
        self.save_config()
        self.hide_window()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", 1)
        self.root.attributes("-topmost", 0)

    def hide_window(self):
        self.root.iconify()
        self.root.withdraw()  # ẩn cửa sổ

    def reset(self):
        self.is_youtube_window = False
        self.clear_after_action()
        clear_widgets(self.root)

    def clear_after_action(self):
        self.root.withdraw()

    
    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.4, right=0.6):
        frame = create_frame(self.root)
        create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')

        if values:
            val = self.tiktok_config[config_key]
            if self.tiktok_config[config_key] == True:
                val = "Yes"
            elif self.tiktok_config[config_key] == False:
                val = "No"

            var = ctk.StringVar(value=str(val))

            combobox = ctk.CTkComboBox(frame, values=values, variable=var, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            combobox.set(val)
            setattr(self, f"{config_key}_var", var)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", self.tiktok_config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            var = self.tiktok_config[config_key]
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            return entry