from common_function import *
from common_function_CTK import *
import pickle

class TikTokManager:
    def __init__(self, account, password, upload_thread=None):
        self.upload_thread = upload_thread
        self.get_tiktok_config()
        self.account = account
        self.password = password
        self.root = ctk.CTk()
        self.title = self.root.title(account)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.width = 500
        self.cookies_info = {}
        self.local_storage_info = {}
        self.driver = None
        self.is_start_tiktok = True
        self.is_upload_video_window = False
        self.is_stop_upload = True
        self.is_stop_download = False


#-----------------------------Thao tác trên tiktok--------------------------------------------------------------

    def login(self):
        try:
            self.is_stop_upload = False
            self.driver = get_driver()
            if not self.driver:
                return
            self.load_session()
            self.driver.refresh()
            sleep(3)
            # self.check_captcha_img()
            xpath = get_xpath_by_multi_attribute('a', ["aria-label='Upload a video'"])
            upload_link = self.get_element_by_xpath(xpath, "Upload a video")
            if not upload_link:
                if "TikTok" in self.driver.title:
                    email_input = self.driver.find_element(By.NAME, 'username')
                    email_input.send_keys(self.account)
                    sleep(1)
                    pass_xpath = get_xpath_by_multi_attribute("input", ["type='password'", "placeholder='Password'"])
                    password_input = self.get_element_by_xpath(pass_xpath, "password")
                    password_input.send_keys(self.password)
                    sleep(1)
                    password_input.send_keys(Keys.RETURN)
                    sleep(30)  # Adjust this time according to your needs
                    self.save_session()
                    upload_link = self.get_element_by_xpath(xpath, "Upload a video")
            if upload_link:
                upload_link.click()
                sleep(3)
                if self.check_capcha_image():
                    self.save_session()
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            getlog()
            warning_message("Lỗi đường truyền mạng không ổn định!")
            return False

    def load_session(self, url="https://www.tiktok.com/login/phone-or-email/email"):
        self.driver.get(url)
        sleep(2)  # Ensure the page is fully loaded before adding cookies
        try:
            with open(cookies_tiktok_path, "rb") as file:
                cookies = pickle.load(file)
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
            print("Cookies loaded successfully.")
        except:
            getlog()
        
    def select_time(self, public_time):
        hh, mm = public_time.split(':')
        xpath = get_xpath('input', "TUXTextInputCore-input", "type", "text")
        date_time_ele = self.driver.find_elements(By.XPATH, xpath)
        time_ele = date_time_ele[0]
        if time_ele:
            time_ele.click()
            sleep(1)
            xpath_hh = get_xpath('span', "tiktok-timepicker-option-text tiktok-timepicker-left")
            hh_elements = self.driver.find_elements(By.XPATH, xpath_hh)
            cnt = 0
            for element in hh_elements:
                # cnt += 1
                # if cnt % 3 == 0:
                self.scroll_into_view(element)
                if element.text == hh:
                    element.click()
                    print("đã chọn giờ")
                    break
            sleep(1)
            time_ele.click()
            sleep(1)
            xpath_mm = get_xpath('span', "tiktok-timepicker-option-text tiktok-timepicker-right")
            mm_elements = self.driver.find_elements(By.XPATH, xpath_mm)
            cnt = 0
            for element in mm_elements:
                # cnt += 1
                # if cnt % 3 == 0:
                self.scroll_into_view(element)
                if element.text == mm:
                    element.click()
                    print("đã chọn phút")
                    break
            sleep(2)

    def save_session(self):
        try:
            with open(cookies_tiktok_path, "wb") as file:
                pickle.dump(self.driver.get_cookies(), file)
            print("Cookies saved successfully.")
        except Exception as e:
            getlog()

    def select_date(self, date_string):
        year, month, day = date_string.strip().split("-")
        xpath1 = get_xpath('input', "TUXTextInputCore-input", "type", "text")
        xpath2 = get_xpath('span', "jsx-2986588792 day valid")
        kq=[]
        date_time_ele = self.driver.find_elements(By.XPATH, xpath1)
        date_ele = date_time_ele[1]
        if date_ele:
            while True:
                date_ele.click()
                sleep(1)
                date_elements = self.driver.find_elements(By.XPATH, xpath2)
                for ele in date_elements:
                    date = ele.text
                    if int(date) == int(day):
                        kq.append(ele)
                        break
                if len(kq) == 0:
                    ele.click()
                else:
                    ele = kq[0]
                    ele.click()
                    break
        sleep(1)
            
    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(0.1)  # Đợi một chút để trình duyệt hoàn thành cuộn

    def input_video_on_tiktok(self, video_path):
        xpath = get_xpath('input', "jsx-200839578", attribute="accept", attribute_value="video/*")
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.send_keys(video_path)
   
    def input_description(self, description):
        xpath = get_xpath_by_multi_attribute("div", ["class='notranslate public-DraftEditor-content'", "contenteditable='true'", "role='combobox'"])
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.send_keys(description)
            sleep(1)
    def click_schedule_button(self):
        xpath = get_xpath('input', "TUXRadioStandalone-input", attribute="name", attribute_value="postSchedule")
        ele = self.get_element_by_xpath(xpath, "Schedule")
        if ele:
            ele.click()
            print(f"clicked schedule_button")
        else:
            print("khong thay schedule_button")

    def click_copyright_check(self):
        while True:
            if self.is_stop_upload:
                break
            xpath = get_xpath("input", "TUXSwitch-input", attribute="type", attribute_value="checkbox")
            ele = self.get_element_by_xpath(xpath)
            if ele:
                ele.click()
                sleep(5)
                break

    def check_status_copyright_check(self):
        while True:
            try:
                if self.is_stop_upload:
                    break
                xpath = "//img[contains(@class, 'check-icon')]"
                ele = self.get_element_by_xpath(xpath)
                if ele:
                    src = ele.get_attribute('src')
                    if src == "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxnIGNsaXAtcGF0aD0idXJsKCNjbGlwMF8yMjI3XzQ5MTM3KSI+CiAgICAgICAgPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiCiAgICAgICAgICAgIGQ9Ik05Ljk5OTkyIDE5LjE2NjhDMTUuMDYyNSAxOS4xNjY4IDE5LjE2NjYgMTUuMDYyOCAxOS4xNjY2IDEwLjAwMDJDMTkuMTY2NiA0LjkzNzU1IDE1LjA2MjUgMC44MzM0OTYgOS45OTk5MiAwLjgzMzQ5NkM0LjkzNzMxIDAuODMzNDk2IDAuODMzMjUyIDQuOTM3NTUgMC44MzMyNTIgMTAuMDAwMkMwLjgzMzI1MiAxNS4wNjI4IDQuOTM3MzEgMTkuMTY2OCA5Ljk5OTkyIDE5LjE2NjhaTTE0LjMzMTYgNi4zODg3MkwxMy40NDIgNS44Mjk2OUMxMy4xOTQxIDUuNjc5IDEyLjg2ODQgNS43NTE5MSAxMi43MTc3IDUuOTk5ODNMOC44ODcxMSAxMi4xMjk3TDYuNzYyODEgOS43MDRDNi41NjgzNiA5LjQ4NTI1IDYuMjM3ODEgOS40NjA5NCA2LjAyMzkyIDkuNjUwNTNMNS4yMjY2OSAxMC4zNDU3QzUuMDA3OTUgMTAuNTM1MiA0Ljk4MzY0IDEwLjg3NTUgNS4xNzgwOCAxMS4wODk0TDguMjM1NzIgMTQuNTg0NkM4LjQ1NDQ3IDE0LjgzNzMgOC43NzUzMSAxNC45Njg2IDkuMTA1ODYgMTQuOTM5NEM5LjQ0MTI4IDE0LjkxNTEgOS43Mzc4MSAxNC43MzA0IDkuOTE3NjcgMTQuNDQzNkwxNC41MDE3IDcuMTE3ODlDMTQuNjUyNCA2Ljg2OTk3IDE0LjU3OTUgNi41NDQyOCAxNC4zMzE2IDYuMzg4NzJaIgogICAgICAgICAgICBmaWxsPSIjMDBDMzlCIiAvPgogICAgPC9nPgogICAgPGRlZnM+CiAgICAgICAgPGNsaXBQYXRoIGlkPSJjbGlwMF8yMjI3XzQ5MTM3Ij4KICAgICAgICAgICAgPHJlY3Qgd2lkdGg9IjIwIiBoZWlnaHQ9IjIwIiBmaWxsPSJ3aGl0ZSIgLz4KICAgICAgICA8L2NsaXBQYXRoPgogICAgPC9kZWZzPgo8L3N2Zz4KICAgIA==":
                        return "noissues"
                    elif src == "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjAiIHZpZXdCb3g9IjAgMCAyMCAyMCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTkuMDM3NzIgMi4yMjYyMkM5LjQ2MTkzIDEuNDc5OTMgMTAuNTM3OSAxLjQ3OTkzIDEwLjk2MjEgMi4yMjYyMkwxOS4wMjA1IDE2LjQwMjhDMTkuNDM5NyAxNy4xNDAyIDE4LjkwNjggMTguMDU1NCAxOC4wNTgzIDE4LjA1NTRIMS45NDE1NEMxLjA5MzAyIDE4LjA1NTQgMC41NjAxNyAxNy4xNDAyIDAuOTc5MzQ2IDE2LjQwMjhMOS4wMzc3MiAyLjIyNjIyWiIgZmlsbD0iI0ZGNEMzQSIvPgo8cGF0aCBkPSJNOS4xNjY0NSA2LjkzMTY2QzkuMTY2NDUgNi43ODUyMiA5LjI5MDgyIDYuNjY2NSA5LjQ0NDIzIDYuNjY2NUgxMC41NTUzQzEwLjcwODggNi42NjY1IDEwLjgzMzEgNi43ODUyMiAxMC44MzMxIDYuOTMxNjZWMTIuMjM0N0MxMC44MzMxIDEyLjM4MTEgMTAuNzA4OCAxMi40OTk4IDEwLjU1NTMgMTIuNDk5OEg5LjQ0NDIzQzkuMjkwODIgMTIuNDk5OCA5LjE2NjQ1IDEyLjM4MTEgOS4xNjY0NSAxMi4yMzQ3VjYuOTMxNjZaIiBmaWxsPSJ3aGl0ZSIvPgo8cGF0aCBkPSJNMTEuMTEwOSAxNC43MjIxQzExLjExMDkgMTUuMzM1NyAxMC42MTM0IDE1LjgzMzIgOS45OTk3OCAxNS44MzMyQzkuMzg2MTMgMTUuODMzMiA4Ljg4ODY3IDE1LjMzNTcgOC44ODg2NyAxNC43MjIxQzguODg4NjcgMTQuMTA4NCA5LjM4NjEzIDEzLjYxMDkgOS45OTk3OCAxMy42MTA5QzEwLjYxMzQgMTMuNjEwOSAxMS4xMTA5IDE0LjEwODQgMTEuMTEwOSAxNC43MjIxWiIgZmlsbD0id2hpdGUiLz4KPC9zdmc+Cg==":
                        return "issues"
            except:
                getlog()

    def click_post_button(self):
        xpath = get_xpath("button", "TUXButton TUXButton--default TUXButton--large TUXButton--primary")
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
        else:
            print(f'không tìm thấy post button')

    def click_schedule_post(self):
        xpath = get_xpath("div", "TUXButton-label")
        ele = self.get_element_by_xpath(xpath, "Schedule")
        if ele:
            ele.click()
            sleep(3)
        else:
            print(f'không tìm thấy Schedule button')

    def click_upload_more_video_button(self):
        xpath = get_xpath('div', "TUXButton-label")
        ele = self.get_element_by_xpath(xpath, "Upload another video")
        if ele:
            ele.click()
            sleep(2)
        else:
            print("không thấy upload more video button")
    
    def check_capcha_image(self):
        xpath = "//img[id='captcha-verify-image']"
        ele = self.get_element_by_xpath(xpath)
        if ele:
            sleep(15)
            ele = self.get_element_by_xpath(xpath)
            if ele:
                warning_message("Phải xác minh capcha thủ công.")
                return False
        return True

    def get_element_by_xpath(self, xpath, key=None):
        kq = []
        cnt=0
        while(len(kq)==0):
            cnt+=1
            elements = self.driver.find_elements(By.XPATH, xpath)
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
                    ele = elements[0]
                    return ele
            sleep(1)
            if cnt > 10:
                print(f"Không tìm thấy: {key}: {xpath}")
                break
    
    def get_element_by_name(self, name):
        ele = self.driver.find_element(By.NAME, name)
        return ele
#--------------------------------Giao diện upload--------------------------------------
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
        self.reset()
        self.is_upload_video_window = True
        self.show_window()
        self.setting_window_size()

        def load_template():
            self.description_var.delete("1.0", ctk.END)
            self.description_var.insert(ctk.END, self.tiktok_config['template'][self.account]['description'])
            self.upload_date_var.delete(0, ctk.END)
            self.upload_date_var.insert(0, self.tiktok_config['template'][self.account]['upload_date'])
            self.publish_times_var.delete(0, ctk.END)
            self.publish_times_var.insert(0, self.tiktok_config['template'][self.account]['publish_times'])
            self.upload_folder_var.delete(0, ctk.END)
            self.upload_folder_var.insert(0, self.tiktok_config['template'][self.account]['upload_folder'])

        def choose_folder_upload():
            folder = choose_folder()
            if folder:
                self.upload_folder_var.delete(0, ctk.END)
                self.upload_folder_var.insert(0, folder)
        self.description_var = self.create_settings_input("Description", "description", config=self.tiktok_config['template'][self.account], is_textbox=True, left=0.4, right=0.6)
        self.upload_date_var = self.create_settings_input("Upload Date(For Schedule)", "upload_date", config=self.tiktok_config['template'][self.account], left=0.4, right=0.6)
        self.publish_times_var = self.create_settings_input("Publish Times(For Schedule)", "publish_times", config=self.tiktok_config['template'][self.account], left=0.4, right=0.6)
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Select Videos Folder", command=choose_folder_upload, width=self.width, left=0.4, right=0.6)
        self.upload_folder_var.insert(0, self.tiktok_config['template'][self.account]['upload_folder'])
        self.load_template_var = create_frame_button_and_combobox(self.root, "Load Template", command=load_template, values=[key for key in self.tiktok_config['template'].keys()], width=self.width, left=0.4, right=0.6)
        create_frame_button_and_button(self.root, text1="Upload now", text2="Schedule Upload", command1=self.upload_video_now, command2=self.schedule_upload, width=self.width, left=0.5, right=0.5)
    
    def schedule_upload(self):
        if not self.save_upload_setting():
            return
        self.is_schedule = True
        self.start_thread_upload_video()
    def upload_video_now(self):
        if not self.save_upload_setting():
            return
        self.is_schedule = False
        self.start_thread_upload_video()

    def save_upload_setting(self):
        videos_folder = self.upload_folder_var.get()
        if not videos_folder:
            warning_message("Hãy chọn thư mục chứa video!")
            return False
        try:
            self.get_tiktok_config()
            upload_date = self.upload_date_var.get()
            is_valid_date, message = is_format_date_yyyymmdd(upload_date, daydelta=10)
            if not is_valid_date:
                warning_message(message)
                return False
            self.tiktok_config['template'][self.account]["description"] = self.description_var.get("1.0", ctk.END).strip()
            self.tiktok_config['template'][self.account]["upload_date"] = upload_date
            self.tiktok_config['template'][self.account]["publish_times"] = self.publish_times_var.get()
            self.tiktok_config['template'][self.account]["upload_folder"] = self.upload_folder_var.get()
            self.save_tiktok_config()
            return True
        except:
            getlog()
            return False
        
    def start_thread_upload_video(self):
        if not self.upload_thread or not self.upload_thread.is_alive():
            self.is_stop_upload = False
            self.upload_video_thread = threading.Thread(target=self.upload_video)
            self.upload_video_thread.start()

    def upload_video(self):
        try:
            videos_folder = self.tiktok_config['template'][self.account]['upload_folder']
            if not videos_folder:
                warning_message("Please choose the upload video folder")
                return
            videos = os.listdir(videos_folder)
            if len(videos) == 0:
                return
            for k in videos:
                if '.mp4' not in k:
                    videos.remove(k)        
            videos = natsorted(videos)
            finish_folder = os.path.join(self.tiktok_config['template'][self.account]['upload_folder'], 'upload_finished')
            os.makedirs(finish_folder, exist_ok=True)
            upload_count = 0
            finishes_upload_videos = []
            if self.is_schedule:
                # Xác định thời gian đăng cho video
                upload_date = self.tiktok_config['template'][self.account]['upload_date']
                publish_times_str = self.tiktok_config['template'][self.account]['publish_times']
                publish_times = publish_times_str.split(',')

            for i, video_file in enumerate(videos):
                if self.is_stop_upload:
                    break
                if '.mp4' not in video_file:
                    continue
                old_video_path = os.path.join(self.tiktok_config['template'][self.account]['upload_folder'], video_file)
                new_video_path = os.path.join(finish_folder, video_file)
                if upload_count == 0:
                    is_continue = self.login()
                else:
                    is_continue = True
                if is_continue:
                    video_name = os.path.splitext(video_file)[0] #lấy tên
                    description = self.tiktok_config['template'][self.account]['description']
                    description = f"{video_name}\n{description}"
                    video_path = os.path.join(videos_folder, video_file)

                    if upload_count > 0:
                        self.click_upload_more_video_button()
                    if self.is_stop_upload:
                        break
                    self.input_video_on_tiktok(video_path)
                    self.input_description(description)
                    if self.is_stop_upload:
                        break
                    if self.is_schedule:
                        public_time = publish_times[upload_count].strip()
                        if len(public_time.split(':')) != 2:
                            warning_message("Time format must be hh:mm")
                            return
                        self.click_schedule_button()
                        self.select_time(public_time)
                        self.select_date(upload_date)
                        self.click_copyright_check()
                        status = self.check_status_copyright_check()
                        if self.is_stop_upload:
                            break
                        if status == "noissues":
                            self.click_schedule_post()
                        else:
                            self.click_schedule_post()
                        upload_count += 1
                        try:
                            shutil.move(old_video_path, new_video_path)
                        except:
                            getlog()
                        finishes_upload_videos.append(video_file)
                        if upload_count < len(publish_times):
                            continue
                        else:
                            break
                    else:
                        self.click_copyright_check()
                        if self.is_stop_upload:
                            break
                        self.check_status_copyright_check()
                        if self.is_stop_upload:
                            break
                        self.click_post_button()
                        try:
                            shutil.move(old_video_path, new_video_path)
                        except:
                            getlog()
                        finishes_upload_videos.append(video_file)
                        break
                else:
                    break
            cnt = len(finishes_upload_videos)
            if cnt > 0:
                print(f"Uploaded finish {cnt} video: {finishes_upload_videos}")
        except:
            warning_message("Lỗi đường truyền mạng không ổn định!")
            getlog()
        finally:
            self.close()

    def save_tiktok_config(self):
        save_to_json_file(self.tiktok_config, tiktok_config_path)

    def get_tiktok_config(self):
        self.tiktok_config = get_json_data(tiktok_config_path)

#---------------------------------Giao diện download------------------------------------------
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
            self.filter_by_like_var = self.create_settings_input("Filter By Number Of Likes", "filter_by_like", config=self.tiktok_config, values=["10000", "20000", "30000", "50000", "100000"])
            self.filter_by_views_var = self.create_settings_input("Filter By Number Of Views", "filter_by_views", config=self.tiktok_config, values=["100000", "200000", "300000", "500000", "1000000"])

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
            self.driver = get_driver(show=False)
            if not self.driver:
                return
            
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
            self.root.title(f"{self.account}")
            self.width = 400
            self.height_window = 250
            self.is_start_tiktok = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video: {self.account}")
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
        save_to_json_file(self.tiktok_config, tiktok_config_path)
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

    
    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.4, right=0.6, config=None):
        frame = create_frame(self.root)
        create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')

        if values:
            if not config_key:
                val = ""
            elif config_key not in config:
                val = ""
            else:
                val = config[config_key]
                if config[config_key] == True:
                    val = "Yes"
                elif config[config_key] == False:
                    val = "No"

            var = ctk.StringVar(value=str(val))

            combobox = ctk.CTkComboBox(frame, values=values, variable=var, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            combobox.set(val)
            setattr(self, f"{config_key}_var", var)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            var = config[config_key]
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            return entry