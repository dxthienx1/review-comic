from common_function import *
from common_function_CTK import *
import pickle

def load_download_info():
    download_info = {
         "downloaded_urls": []
      }
    if os.path.exists(download_info_path):
        download_if = get_json_data(download_info_path)
    else:
        download_if = download_info
    save_to_json_file(download_if, download_info_path)
    return download_if
class TikTokManager:
    def __init__(self, account, password, upload_thread=None, download_thread=None):
        self.upload_thread = upload_thread
        self.download_thread = download_thread
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
        self.is_first_start = True
        self.is_upload_video_window = False
        self.is_stop_upload = True
        self.is_stop_download = False
        self.is_download_by_search_url = False

#-----------------------------Thao tác trên tiktok--------------------------------------------------------------

    def login(self):
        try:
            self.is_stop_upload = False
            self.driver = get_driver()
            if not self.driver:
                return
            self.load_session()
            sleep(1)
            self.driver.refresh()
            sleep(6)
            xpath = get_xpath_by_multi_attribute('a', ["aria-label='Upload a video'"])
            upload_link = self.get_element_by_xpath(xpath, "Upload a video")
            if not upload_link:
                if "TikTok" in self.driver.title:
                    print("check email...................")
                    email_xpath = '//input[@name="username"]'
                    email_input = self.get_element_by_xpath(email_xpath)
                    if email_input:
                        email_input.send_keys(self.account)
                        sleep(1)
                    pass_xpath = get_xpath_by_multi_attribute("input", ["type='password'", "placeholder='Password'"])
                    password_input = self.get_element_by_xpath(pass_xpath, "password")
                    if password_input:
                        password_input.send_keys(self.password)
                        sleep(1)
                        password_input.send_keys(Keys.RETURN)
                        sleep(1)
                        sleep(20)  # Adjust this time according to your needs
                        self.save_session()
                    upload_link = self.get_element_by_xpath(xpath, "Upload a video")
            if upload_link:
                upload_link.click()
                sleep(1)
                if self.check_capcha_image():
                    self.save_session()
                    return True
                else:
                    return False
            else:
                return False
        except Exception as e:
            getlog()
            notification(self.root, "Lỗi đường truyền mạng không ổn định!")
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
                notification(self.root, "Phải xác minh capcha thủ công.")
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
        if not self.is_first_start:
            self.reset()
        else:
            self.is_first_start = False
        self.is_start_tiktok = True
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
        self.description_var = self.create_settings_input("Description", "description", config=self.tiktok_config['template'][self.account], is_textbox=True, left=0.3, right=0.7)
        self.upload_date_var = self.create_settings_input("Upload Date(For Schedule)", "upload_date", config=self.tiktok_config['template'][self.account], left=0.3, right=0.7)
        self.publish_times_var = self.create_settings_input("Publish Times(For Schedule)", "publish_times", config=self.tiktok_config['template'][self.account], left=0.3, right=0.7)
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Select Videos Folder", command=choose_folder_upload, width=self.width, left=0.3, right=0.7)
        self.upload_folder_var.insert(0, self.tiktok_config['template'][self.account]['upload_folder'])
        self.load_template_var = create_frame_button_and_combobox(self.root, "Load Template", command=load_template, values=[key for key in self.tiktok_config['template'].keys()], width=self.width, left=0.3, right=0.7)
        create_frame_button_and_button(self.root, text1="Upload now", text2="Schedule Upload", command1=self.upload_video_now, command2=self.schedule_upload, width=self.width, left=0.5, right=0.5)
        create_button(self.root, text="Back", command=self.get_start_tiktok, width=self.width)
    
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
            notification(self.root, "Hãy chọn thư mục chứa video!")
            return False
        try:
            self.get_tiktok_config()
            upload_date = self.upload_date_var.get()
            is_valid_date, message = is_format_date_yyyymmdd(upload_date, daydelta=10)
            if not is_valid_date:
                notification(self.root, message)
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
                notification(self.root, "Please choose the upload video folder")
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
                            notification(self.root, "Time format must be hh:mm")
                            return
                        self.click_schedule_button()
                        self.select_time(public_time)
                        if self.is_stop_upload:
                            break
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
                            if self.tiktok_config['is_delete_video']:
                                os.remove(old_video_path)
                            else:
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
                            if self.tiktok_config['is_delete_video']:
                                os.remove(old_video_path)
                            else:
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
            notification(self.root, "Lỗi đường truyền mạng không ổn định!")
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
                self.output_folder = self.output_folder_var.get()
                if not os.path.exists(self.output_folder):
                    notification(self.root, "Please select the folder containing the downloaded file.")
                    return
                self.tiktok_config['output_folder'] = self.output_folder
                self.tiktok_config['show_browser'] = self.show_browser_var.get() == "Yes"
                self.tiktok_config['download_by_channel_url'] = self.download_by_channel_url_var.get()
                # self.tiktok_config['filter_by_like'] = self.filter_by_like_var.get()
                self.tiktok_config['filter_by_views'] = self.filter_by_views_var.get()
                self.save_tiktok_config()

            def start_download_by_video_url():
                if not self.download_thread or not self.download_thread.is_alive():
                    save_download_settings()
                    self.download_thread = threading.Thread(target=self.download_videos_by_video_url)
                    self.download_thread.start()
                else:
                    notification(self.root, "Đang tải ở một luồng khác.")
            def start_download_by_search_url():
                if not self.download_thread or not self.download_thread.is_alive():
                    self.is_download_by_search_url = True
                    save_download_settings()
                    self.download_thread = threading.Thread(target=self.download_videos_by_channel_url)
                    self.download_thread.start()
                else:
                    notification(self.root, "Đang tải ở một luồng khác.")
            def start_download_by_channel_url():
                if not self.download_thread or not self.download_thread.is_alive():
                    self.is_download_by_search_url = False
                    save_download_settings()
                    self.download_thread = threading.Thread(target=self.download_videos_by_channel_url)
                    self.download_thread.start()
                else:
                    notification(self.root, "Đang tải ở một luồng khác.")
            self.show_browser_var = self.create_settings_input(label_text="Show Browser When Searching", config_key="show_browser", config=self.tiktok_config, values=['Yes', 'No'])
            self.file_name_var, self.start_index_var = create_frame_label_input_input(self.root, label_text="Name Files By Index", width=self.width, place_holder1="Nhập tên file có chứa chuỗi <index>", place_holder2="start index")
            self.filter_by_views_var = self.create_settings_input("Filter By Number Of Views", "filter_by_views", config=self.tiktok_config, values=["100000", "200000", "300000", "500000", "1000000"], left=0.4, right=0.6)
            self.download_by_search_url_var = create_frame_button_and_input(self.root,text="Download By Search URL", command=start_download_by_search_url, left=0.4, right=0.6, width=self.width)
            self.download_by_channel_url_var = create_frame_button_and_input(self.root,text="Download By Channel URL", command=start_download_by_channel_url, left=0.4, right=0.6, width=self.width)
            self.download_by_video_url_var = create_frame_button_and_input(self.root,text="Download By Video URL", command=start_download_by_video_url, left=0.4, right=0.6, width=self.width)
            # self.filter_by_like_var = self.create_settings_input("Filter By Number Of Likes", "filter_by_like", config=self.tiktok_config, values=["10000", "20000", "30000", "50000", "100000"], left=0.4, right=0.6)
            self.output_folder_var = create_frame_button_and_input(self.root,text="Choose folder to save", command=self.choose_folder_to_save, left=0.4, right=0.6, width=self.width)
            self.output_folder_var.insert(0, self.tiktok_config['output_folder'])
            create_button(self.root, text="Back", command=self.get_start_tiktok, width=self.width)

    def choose_folder_to_save(self):
        self.output_folder = filedialog.askdirectory()
        self.output_folder_var.delete(0, ctk.END)
        self.output_folder_var.insert(0, self.output_folder)

    def download_videos_by_video_url(self):
        video_url = self.download_by_video_url_var.get()
        if not video_url:
            notification(self.root, "Hãy nhập link tải video.")
            return
        if download_video_by_url(video_url, self.tiktok_config['output_folder']):
            notification(self.root, f"Tải video từ link {video_url} thành công.")
        else:
            notification(self.root, "Tải video không thành công. Đảm bảo URL bạn nhập thuộc về tiktok.")

    def download_videos_by_channel_url(self):
        if self.is_download_by_search_url:
            url = self.download_by_search_url_var.get()
        else:
            url = self.download_by_channel_url_var.get()
        self.get_tiktok_videos_by_channel_url(url=url, view_cnt=self.tiktok_config['filter_by_views'])
        # self.get_tiktok_videos_by_channel_url(channel_url=channel_url, view_cnt=self.tiktok_config['filter_by_views'], like_cnt=self.tiktok_config['filter_by_like'])

    def get_tiktok_videos_by_channel_url(self, url, view_cnt=0):
        file_name = self.file_name_var.get()
        if file_name:
            if '<index>' not in file_name:
                notification("Đặt tên kèm theo chuỗi <index> để xác định vị trí sô thứ tự.\nVí dụ: Phần <index> video")
                return
            index = self.start_index_var.get()
            try:
                index = int(index)
            except:
                index = 1
        self.hide_window()
        cnt_downlaod = 0
        cnt_search = 0
        try:
            view_cnt = int(view_cnt)
        except:
            notification(self.root,"Số lượt xem không đúng định dạng số")
            return
        if not url:
            notification(self.root, "Hãy nhập đường link đến kênh muốn tải video")
            return
            
        try:
            self.driver = get_driver(show=self.tiktok_config['show_browser'])
            if not self.driver:
                return
            if self.is_download_by_search_url:
                self.load_session()
                sleep(1)
                self.driver.refresh()
                sleep(2)
            self.driver.get(url) # Mở trang TikTok
            sleep(4)  # Đợi trang tải
            if self.is_stop_download:
                self.close()
                return None
            last_height = self.driver.execute_script("return document.body.scrollHeight") # Tự động cuộn trang
            while True:
                if self.is_stop_download:
                    self.close()
                    return None
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Cuộn xuống cuối trang
                sleep(2)
                new_height = self.driver.execute_script("return document.body.scrollHeight") # Tính chiều cao mới của trang
                if new_height == last_height: # Kiểm tra nếu không có thêm nội dung mới
                    break
                last_height = new_height
                if self.is_download_by_search_url:
                    cnt_search += 1
                    if cnt_search > 15:
                        break
            
            self.download_info = load_download_info()
            video_urls = []
            if self.is_download_by_search_url:
                xpath = get_xpath('div', "css-1soki6-DivItemContainerForSearch e19c29qe10")
                video_divs = self.driver.find_elements(By.XPATH, xpath)
                for video_div in video_divs:
                    if self.is_stop_download:
                        self.close()
                        return None
                    try:
                        views_element = video_div.find_element(By.XPATH, './/strong[contains(@class, "css-ws4x78-StrongVideoCount")]')
                        if views_element:
                            view_count = views_element.text
                        if view_count:
                            if 'M' in view_count:
                                view_count = float(view_count.replace('M', '')) * 1000000
                            elif 'K' in view_count:
                                view_count = float(view_count.replace('K', '')) * 1000
                            else:
                                try:
                                    view_count = int(view_count)
                                except:
                                    continue
                        if view_count >= view_cnt:
                            try:
                                link_video = video_div.find_element(By.XPATH, './/a[contains(@href, "/video/")]')
                                if link_video:
                                    url = link_video.get_attribute('href')
                                    video_urls.append(url)
                                else:
                                    continue
                            except:
                                continue
                    except:
                        continue

            else:
                video_elements = self.driver.find_elements(By.TAG_NAME, 'a')
                for item in video_elements:
                    if self.is_stop_download:
                        self.close()
                        return None
                    url = item.get_attribute('href')
                    if url and '/video/' in url:
                        if url in self.download_info['downloaded_urls']:
                            print("url này đã tải trước đó.")
                            continue
                        view_count_element = item.find_element(By.XPATH, '//strong[@data-e2e="video-views"]')
                        if view_count_element:
                            view_count = view_count_element.text
                        else:
                            continue
                        if view_count:
                            if 'M' in view_count:
                                view_count = float(view_count.replace('M', '')) * 1000000
                            elif 'K' in view_count:
                                view_count = float(view_count.replace('K', '')) * 1000
                            else:
                                try:
                                    view_count = int(view_count)
                                except:
                                    continue
                            if view_count >= view_cnt:
                                video_urls.append(url)
            self.close()
            notification(self.root, f"tổng số video tìm được là {len(video_urls)}")
            for url in video_urls:
                try:
                    if self.is_stop_download:
                        break
                    if file_name:
                        name = file_name.replace('<index>', str(index))
                        file_path = os.path.join(self.output_folder, f"{name}.mp4")
                    else:
                        file_path = None
                    if download_video_by_url(url, download_folder=self.output_folder, file_path=file_path):
                        print(f"tải thành công {url}")
                        if file_name:
                            index += 1
                        cnt_downlaod += 1
                        video_urls.remove(url)
                        if url not in self.download_info['downloaded_urls']:
                            self.download_info['downloaded_urls'].append(url)
                        self.save_download_info()
                    else:
                        print(f"Tải không thành công {url}")
                except:
                    getlog()
                    print(f"Tải không thành công {url}")
            if cnt_downlaod > 0:
                notification(self.root, f"Đã tải thành công {cnt_downlaod} video.")
        except:
            getlog()
            notification(self.root, "Gặp lỗi trong quá trình tìm kiếm. Có thể Tiktok đã đổi cấu trúc trang web.")

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
            self.height_window = 170
            self.is_start_tiktok = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video: {self.account}")
            self.width = 800
            self.height_window = 450
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos")
            self.width = 700
            self.height_window = 460
            self.is_download_window = False
        self.setting_screen_position()

    def save_tiktok_config(self):
        save_to_json_file(self.tiktok_config, tiktok_config_path)
    def save_download_info(self):
        save_to_json_file(self.download_info, download_info_path)

    def exit_app(self):
        self.reset()
        self.root.destroy()

    def on_close(self):
        self.save_tiktok_config()
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