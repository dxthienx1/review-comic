from common_function import *

class TikTokManager:
    def __init__(self, config, gmail):
        self.config = config
        self.gmail = gmail
        self.root = ctk.CTk()
        self.title = self.root.title(gmail)
        self.font_label = ctk.CTkFont(family="Arial", size=font_size)
        self.font_button = ctk.CTkFont( family="Arial", size=font_size, weight="bold" )
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.width = 500

        self.is_start_tiktok = True
        self.download_thread = None
        self.download_thread_url = None
        self.is_upload_video_window = False
    
    def get_start_tiktok(self):
        self.show_window()
        self.setting_window_size()
        self.create_button(text="Upload Videos", command= self.open_upload_video_window)
        self.create_button(text="Download Videos From Channel", command=self.open_download_video_window)
        try:
            self.root.mainloop()
        except:
            getlog()

    def open_upload_video_window(self):
        pass


#--------------------------------------------------download
    def open_download_video_window(self):
            self.reset()
            self.is_download_window = True
            self.setting_window_size()
            self.show_window()

            def save_download_settings():
                self.config['output_folder'] = self.output_folder_var.get()
                self.config['download_by_channel_url'] = self.download_by_channel_url.get()
                self.config['filter_by_like'] = self.filter_by_like_var.get()
                self.config['filter_by_views'] = self.filter_by_views_var.get()
                self.save_config()

            def start_download_by_channel_url():
                save_download_settings()
                download_thread = threading.Thread(target=self.download_videos_by_channel_url)
                download_thread.daemon = True
                download_thread.start()
                

            self.output_folder_var = self.create_frame_button_and_input("Choose folder to save", command=self.choose_folder_to_save)
            self.download_by_channel_url = self.create_frame_button_and_input("Download By Channel URL", command=start_download_by_channel_url)
            self.filter_by_like_var = self.create_settings_input("Filter By Number Of Likes", "filter_by_like", values=["10000", "20000", "30000", "50000", "100000"])
            self.filter_by_views_var = self.create_settings_input("Filter By Number Of Views", "filter_by_views", values=["200000", "500000", "1000000", "2000000", "5000000"])
            self.progress_bar = ctk.CTkProgressBar(self.root, width=self.width)
            self.progress_bar.set(0)

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
        self.get_tiktok_videos_by_channel_url(channel_url=channel_url, view_cnt=self.config['filter_by_views'], like_cnt=self.config['filter_by_like'])
        print(f"đã tải thành công {self.cnt_downlaod} video")

    def create_thread_download(self):
        self.thread_download = threading.Thread(target=self.download_video_by_list_url)
        self.thread_download.start()
     
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
            service = Service(ChromeDriverManager().install())
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')  # Chạy ở chế độ không giao diện
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
            options.add_experimental_option('excludeSwitches', ['enable-automation'])
            options.add_experimental_option('useAutomationExtension', False)
            driver = webdriver.Chrome(service=service, options=options)
            #ẩn mình
            stealth(driver,
                    languages=["en-US", "en"],
                    vendor="Google Inc.",
                    platform="Win32",
                    webgl_vendor="Intel Inc.",
                    renderer="Intel Iris OpenGL Engine",
                    fix_hairline=True,
                    )
            
            driver.get(channel_url) # Mở trang TikTok
            sleep(20)  # Đợi trang tải
            last_height = driver.execute_script("return document.body.scrollHeight") # Tự động cuộn trang
            while True:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Cuộn xuống cuối trang
                sleep(5) # Đợi trang tải
                new_height = driver.execute_script("return document.body.scrollHeight") # Tính chiều cao mới của trang
                if new_height == last_height: # Kiểm tra nếu không có thêm nội dung mới
                    break
                last_height = new_height

            video_urls = []
            video_elements = driver.find_elements(By.TAG_NAME, 'a')
            for item in video_elements:
                url = item.get_attribute('href')
                if url and '/video/' in url:
                    video_urls.append(url)
            driver.quit()
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
        save_to_json_file(self.config, config_path)
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
    def create_button( self, text="", command=None, width=0, height=0, compound="left", anchor="center", frame = None, image=None, side=None, pady=None, padx=None):
        if width == 0:
            width = self.width
        if height == 0:
            height = height
        if not padx:
            padx=padx
        if not pady:
            padx=pady

        if frame:
            button = ctk.CTkButton( frame, text=text, command=command, image=image, font=self.font_button, width=width, height= height_element, compound=compound, anchor=anchor, )
        else:
            button = ctk.CTkButton( self.root, text=text, command=command, image=image, font=self.font_button, width=width, height= height_element, compound=compound, anchor=anchor, )
        if side:
            button.pack(side=side, pady=pady, padx=padx)
        else:    
            button.pack(pady=pady, padx=padx)
        return button

    def create_label( self, frame=None, text="", compound="center", anchor='center', width=None, height=None, wraplength=None, side=LEFT):
        if not width:
            width = self.width
        if not height:
            height = height_element
        wraplength = max(600, self.width)
        if frame:
            button = ctk.CTkLabel( frame, text=text, font=self.font_label, width=width, height= height_element, wraplength=wraplength, compound=compound, anchor=anchor)
        else:
            button = ctk.CTkLabel( self.root, text=text, font=self.font_label, width=width, height= height_element, wraplength=wraplength, compound=compound)
        if side:
            button.pack(side=side, pady=pady, padx=padx)
        else:
            button.pack(pady=pady, padx=padx)

    def create_frame(self, fill='x', side=None):
        frame = ctk.CTkFrame(self.root)
        frame.pack(padx=padx, pady=pady, fill=fill, side=side)
        return frame

    def create_text_input(self, frame, width=None, placeholder=None, side="right"):
        if not width:
            width = self.width
        text_input = ctk.CTkEntry(master=frame, width=width, height= height_element, placeholder_text_color=placeholder)
        text_input.pack(pady=pady, padx=padx, side=side)
        return text_input
    
    def create_combobox(self, frame, values=None, variable=None, side=RIGHT, width=None, height=None):
        val=None
        if variable:
            val = ctk.StringVar(value=str(variable))
        if not width:
            width = self.width
        if not height:
            height = height_element
        combobox = ctk.CTkComboBox(master=frame, values=values, variable=val, width=width, height=height)
        combobox.pack(side=side, padx=padx, pady=pady)
        return combobox

    
    def create_frame_label_and_input(self, label_text="", place_holder=None, left=0.4, right=0.6):
        frame = self.create_frame()
        label = self.create_label(frame=frame, text=label_text, side=LEFT, width=self.width*left, compound=LEFT)
        entry = self.create_text_input(frame=frame, width=self.width*right, placeholder=place_holder)
        return entry
    def create_frame_button_and_input(self, text, place_holder=None, command=None, left=0.4, right=0.6):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        entry = self.create_text_input(frame, width=self.width*right, placeholder=place_holder)
        return entry
    def create_frame_button_and_combobox(self, text, command=None, values=None, variable=None, left=0.4, right=0.6):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        combobox = self.create_combobox(frame, width=self.width*right, side=RIGHT, values=values, variable=variable)
        return combobox
    def create_frame_button_and_button(self, text1, text2, command1=None, command2=None, left=0.4, right=0.6):
        frame = self.create_frame()
        button1 = self.create_button(frame=frame, text=text1, width=self.width*left , side=LEFT, command=command1)
        button2 = self.create_button(frame=frame, text=text2, width=self.width*right -15, side=RIGHT, command=command2)
        return button1, button2
    
    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.4, right=0.6):
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
            combobox.set(val)
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