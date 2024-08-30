from common_function import *
from common_function_CTK import *

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
    def __init__(self, account, password, upload_thread=None, download_thread=None, is_auto_upload=False):
        self.upload_thread = upload_thread
        self.download_thread = download_thread
        self.is_auto_upload = is_auto_upload
        self.get_tiktok_config()
        self.account = account
        self.password = password
        if not is_auto_upload:
            self.root = ctk.CTk()
            self.title = self.root.title(account)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.is_schedule = False
        else:
            self.is_schedule = True
        self.width = 500
        self.driver = None
        self.is_start_tiktok = True
        self.is_first_start = True
        self.is_upload_video_window = False
        self.is_stop_upload = False
        self.is_stop_download = False
        self.is_download_by_search_url = False

#-----------------------------Thao tác trên tiktok--------------------------------------------------------------

    def login(self):
        try:
            self.is_stop_upload = False
            self.driver = get_driver(show=self.tiktok_config['show_browser'])
            if not self.driver:
                return False
            self.load_session()
            self.driver.refresh()
            sleep(6)
            upload_link = self.get_upload_button()
            if not upload_link:
                if "TikTok" in self.driver.title:
                    print("Đang đăng nhập bằng email và password...")
                    email_xpath = '//input[@name="username"]'
                    email_input = self.get_element_by_xpath(email_xpath)
                    if email_input:
                        email_input.send_keys(self.account)
                        sleep(0.3)
                    pass_xpath = get_xpath_by_multi_attribute("input", ["type='password'", "placeholder='Password'"])
                    password_input = self.get_element_by_xpath(pass_xpath, "password")
                    if password_input:
                        password_input.send_keys(self.password)
                        sleep(0.3)
                        password_input.send_keys(Keys.RETURN)
                    self.waiting_for_capcha_verify()
                    upload_link = self.get_upload_button()
            if upload_link:
                upload_link.click()
                self.waiting_for_capcha_verify()
                return True
            else:
                print("Đăng nhập thất bại, hãy kiểm tra lại thông tin đăng nhập đã đúng chưa!")
                return False
        except:
            getlog()
            print("Lỗi trong quá trình đăng nhập tiktok. Hãy đảm bảo đường truyền ổn định!")
            return False

    def get_upload_button(self):
        xpath = get_xpath('a', 'e14l9ebt5 css-12zznuq-StyledLink-StyledTmpLink er1vbsz0', 'data-e2e', 'nav-upload')
        upload_link = self.get_element_by_xpath(xpath)
        if not upload_link:
            xpath = get_xpath('a', 'e18d3d942 css-2gvzau-ALink-StyledLink er1vbsz1', 'aria-label', 'Upload a video')
            upload_link = self.get_element_by_xpath(xpath)
            if upload_link:
                self.upload_button_at_left = False

        else:
            self.upload_button_at_left = True
        return upload_link

    def load_session(self, url="https://www.tiktok.com/login/phone-or-email/email"):
        self.driver.get(url)
        sleep(1.5)
        try:
            cookies_info = get_pickle_data(tiktok_cookies_path)
            if not cookies_info:
                cookies_info = {}
            if self.account in cookies_info:
                cookies = cookies_info[self.account]
                for cookie in cookies:
                    self.driver.add_cookie(cookie)
                sleep(2)
        except:
            getlog()
        
    def save_session(self):
        try:
            cookies_info = get_pickle_data(tiktok_cookies_path) or {}
            cookies_info[self.account] = self.driver.get_cookies() or []
            save_to_pickle_file(cookies_info, tiktok_cookies_path)
            print("Lưu cookies thành công.")
        except:
            getlog()

    def select_time(self, public_time):
        hh, mm = public_time.split(':')
        xpath = get_xpath('input', "TUXTextInputCore-input", "type", "text")
        date_time_ele = self.driver.find_elements(By.XPATH, xpath)
        if date_time_ele:
            time_ele = date_time_ele[0]
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
                    print(f"Không tìm thấy ngày {date_string}")
                else:
                    ele = kq[0]
                    ele.click()
                    print(f"đã chọn ngày {date}")
                    break
        sleep(1)
            
    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(0.1)  # Đợi một chút để trình duyệt hoàn thành cuộn

    def input_video_on_tiktok(self, video_path):
        cnt = 0
        while True:
            try:
                xpath = "//input[@accept='video/*']"
                ele = self.get_element_by_xpath(xpath)
                if ele:
                    ele.send_keys(video_path)
                    return True
                else:
                    cnt += 1
                    if cnt > 3:
                        return False
            except:
                sleep(2)
                cnt += 1
                if cnt > 3:
                    return False
   
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
        try:
            xpath = get_xpath("input", "TUXSwitch-input", attribute="type", attribute_value="checkbox")
            ele = self.get_element_by_xpath(xpath)
            if ele:
                ele.click()
        except:
            pass

    def check_status_copyright_check(self):
        cnt = 0
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
                else:
                    cnt += 1
                    sleep(2)
            except:
                cnt += 1
                sleep(3)
            if cnt > 2:
                break

    def click_post_button(self):
        cnt = 0
        while True:
            xpath = get_xpath("button", "TUXButton TUXButton--default TUXButton--large TUXButton--primary")
            ele = self.get_element_by_xpath(xpath)
            if ele:
                ele.click()
                sleep(4)
                # post_anyway_xpath = get_xpath('div', 'TUXButton-label')
                # post_anyway = self.get_element_by_xpath(post_anyway_xpath, 'Post')
                # if post_anyway:
                #     post_anyway.click()
                #     sleep(4)
                # else:
                #     sleep(3)
                break
            else:
                cnt += 1
                sleep(2)
            if cnt > 3:
                break
            

    def check_progress_upload(self):
        cnt = 0
        while True:
            if self.is_stop_upload:
                break
            xpath = get_xpath("div", "jsx-1384908514 info-progress-num")
            ele = self.get_element_by_xpath(xpath)
            if ele:
                ff = ele.text
                print(ff)
                if ff == '100%':
                    break
                sleep(5)
                cnt += 1
            if cnt > 200:
                break


    def click_schedule_post(self):
        xpath = get_xpath("div", "TUXButton-label")
        ele = self.get_element_by_xpath(xpath, "Schedule")
        if ele:
            ele.click()
            sleep(5)
        else:
            print(f'không tìm thấy Schedule button')

    def click_upload_more_video_button(self):
        xpath = get_xpath('div', "TUXButton-label")
        ele = self.get_element_by_xpath(xpath, "Upload")
        if ele:
            ele.click()
            sleep(1)
        else:
            print("không thấy upload more video button")
    
    def waiting_for_capcha_verify(self):
        sleep(1.5)
        if self.tiktok_config['template'][self.account]['waiting_verify']:
            sleep(20)
        self.save_session()

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
    
    # def get_element_by_name(self, name):
    #     ele = self.driver.find_element(By.NAME, name)
    #     return ele
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
            # template = 
            self.description_var.delete("1.0", ctk.END)
            self.description_var.insert(ctk.END, self.tiktok_config['template'][self.account]['description'])
            self.upload_date_var.delete(0, ctk.END)
            self.upload_date_var.insert(0, self.tiktok_config['template'][self.account]['upload_date'])
            self.publish_times_var.delete(0, ctk.END)
            self.publish_times_var.insert(0, self.tiktok_config['template'][self.account]['publish_times'])
            self.upload_folder_var.delete(0, ctk.END)
            self.upload_folder_var.insert(0, self.tiktok_config['template'][self.account]['upload_folder'])
            self.number_of_days_var.delete(0, ctk.END)
            self.number_of_days_var.insert(0, self.tiktok_config['template'][self.account]['number_of_days'])
            self.day_gap_var.delete(0, ctk.END)
            self.day_gap_var.insert(0, self.tiktok_config['template'][self.account]['day_gap'])
            self.show_browser_var.set(convert_boolean_to_Yes_No(self.tiktok_config['show_browser']))
            self.is_delete_after_upload_var.set(convert_boolean_to_Yes_No(self.tiktok_config['template'][self.account]['is_delete_after_upload']))

        def choose_folder_upload():
            folder = choose_folder()
            if folder:
                self.upload_folder_var.delete(0, ctk.END)
                self.upload_folder_var.insert(0, folder)
        self.description_var = self.create_settings_input("Mô tả", "description", config=self.tiktok_config['template'][self.account], is_textbox=True, left=0.3, right=0.7)
        self.upload_date_var = self.create_settings_input("Ngày đăng(yyyy-mm-dd)", "upload_date", config=self.tiktok_config['template'][self.account], left=0.3, right=0.7)
        self.publish_times_var = self.create_settings_input("Giờ đăng(hh:mm)", "publish_times", config=self.tiktok_config['template'][self.account], left=0.3, right=0.7)
        self.waiting_verify_var = self.create_settings_input(label_text="Thêm giời gian chờ xác minh capcha", config_key="waiting_verify", config=self.tiktok_config['template'][self.account], values=['Yes', 'No'], left=0.3, right=0.7)
        self.number_of_days_var = self.create_settings_input("Số ngày muốn đăng", config_key="number_of_days", config=self.tiktok_config['template'][self.account], left=0.3, right=0.7)
        self.day_gap_var = self.create_settings_input("Khoảng cách giữa các ngày đăng", "day_gap", config=self.tiktok_config['template'][self.account], left=0.3, right=0.7)
        self.is_delete_after_upload_var = self.create_settings_input("Xóa video sau khi đăng", "is_delete_after_upload", config=self.tiktok_config['template'][self.account], values=["Yes", "No"], left=0.3, right=0.7)
        self.show_browser_var = self.create_settings_input(label_text="Hiển thị trình duyệt", config_key="show_browser", config=self.tiktok_config, values=['Yes', 'No'], left=0.3, right=0.7)
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa video", command=choose_folder_upload, width=self.width, left=0.3, right=0.7)
        self.upload_folder_var.insert(0, self.tiktok_config['template'][self.account]['upload_folder'])
        self.load_template_var = create_frame_button_and_combobox(self.root, "Tải mẫu có sẵn", command=load_template, values=[key for key in self.tiktok_config['template'].keys()], width=self.width, left=0.3, right=0.7)
        self.load_template_var.set(self.account)
        create_frame_button_and_button(self.root, text1="Đăng video ngay", text2="Lên lịch đăng video", command1=self.upload_video_now, command2=self.schedule_upload, width=self.width, left=0.5, right=0.5)
        create_button(self.root, text="Lùi lại", command=self.get_start_tiktok, width=self.width)
    
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
            self.tiktok_config['template'][self.account]["waiting_verify"] = self.waiting_verify_var.get() == 'Yes'
            self.tiktok_config["show_browser"] = self.show_browser_var.get() == 'Yes'
            self.tiktok_config["is_delete_after_upload"] = self.is_delete_after_upload_var.get() == 'Yes'
            self.tiktok_config['template'][self.account]["number_of_days"] = self.number_of_days_var.get()
            self.tiktok_config['template'][self.account]["day_gap"] = self.day_gap_var.get()
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
                if not self.is_auto_upload:
                    notification(self.root, "Hãy chọn thư mục chứa video muốn đăng")
                return
            if not os.path.isdir(videos_folder):
                if not self.is_auto_upload:
                    notification(self.root, f"Thư mục {videos_folder} không tồn tại")
                return
            videos = os.listdir(videos_folder)
            videos = [k for k in videos if '.mp4' in k]      
            if len(videos) == 0:
                return
            videos = natsorted(videos)
            upload_count = 0
            date_cnt = 0
            number_of_days = get_number_of_days(self.tiktok_config['template'][self.account]['number_of_days'])
            if self.is_schedule:
                day_gap = get_day_gap(self.tiktok_config['template'][self.account]['day_gap'])
                upload_date_str = self.tiktok_config['template'][self.account]['upload_date']
                if not upload_date_str:
                    return
                if self.is_auto_upload:
                    number_of_days = 10
                    upload_date = add_date_into_string(upload_date_str, day_gap)
                    self.tiktok_config['show_browser'] = True
                upload_date = get_upload_date(upload_date_str, next_day=True)
                upload_date = convert_datetime_to_string(upload_date)
                if not is_date_greater_than_current_day(upload_date_str):
                    print(f"Ngày lên lịch đăng phải lớn hơn ngày hiện tại. Sẽ lấy ngày bắt đầu dăng là {upload_date}")
                # Xác định thời gian đăng cho video
                publish_times_str = self.tiktok_config['template'][self.account]['publish_times']
                publish_times = publish_times_str.split(',')   
                if not publish_times:
                    return

            for i, video_file in enumerate(videos):
                if self.is_stop_upload:
                    break
                if upload_count == 0:
                    if not self.login():
                        print(f'Có lỗi trong quá trình đăng nhập. Hãy kiểm tra xem tài khoản có cần phải xác minh capcha không.')
                        return
                video_name = os.path.splitext(video_file)[0] #lấy tên
                description = self.tiktok_config['template'][self.account]['description']
                description = f"{video_name}\n{description}"
                video_path = os.path.join(videos_folder, video_file)
                if upload_count > 0:
                    self.click_upload_more_video_button()
                if self.is_stop_upload:
                    break
                if not self.input_video_on_tiktok(video_path):
                    print(f'Có lỗi trong quá trình tải video lên.')
                    break
                self.input_description(description)
                if self.is_stop_upload:
                    break
                if self.is_schedule:
                    publish_time = publish_times[upload_count % len(publish_times)].strip()
                    publish_time = get_pushlish_time_hh_mm(publish_time)
                    if not publish_time:
                        return False
                    self.click_schedule_button()
                    self.select_date(upload_date)
                    if self.is_stop_upload:
                        break
                    self.select_time(publish_time)
                    self.check_progress_upload()
                    # self.click_copyright_check()
                    # self.check_status_copyright_check()
                    if self.is_stop_upload:
                        break

                    self.click_schedule_post()
                    upload_count += 1
                    if self.tiktok_config['template'][self.account]['upload_date'] != upload_date:
                        self.tiktok_config['template'][self.account]['upload_date'] = upload_date
                        self.save_tiktok_config()
                    remove_or_move_after_upload(video_path, is_delete=self.tiktok_config['template'][self.account]['is_delete_after_upload'], finish_folder_name='tiktok_upload_finished')
                    if (upload_count) % len(publish_times) == 0:
                        upload_date = add_date_into_string(upload_date, day_gap)
                        date_cnt += 1
                        if date_cnt == number_of_days:
                            break
                else:
                    if self.is_stop_upload:
                        break
                    if self.is_stop_upload:
                        break
                    self.check_progress_upload()
                    self.click_post_button()
                    
                    remove_or_move_after_upload(video_path, is_delete=self.tiktok_config['template'][self.account]['is_delete_after_upload'], finish_folder_name='tiktok_upload_finished')
                    upload_count += 1
                    if upload_count == number_of_days:
                        break
            if upload_count > 0:
                print(f"Đăng thành công {upload_count} video.")

        except:
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
                self.download_folder = self.download_folder_var.get()
                if not os.path.exists(self.download_folder):
                    notification(self.root, "Please select the folder containing the downloaded file.")
                    return
                self.tiktok_config['download_folder'] = self.download_folder
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
            self.show_browser_var = self.create_settings_input(label_text="Hiển thị trình duyệt(khi có capcha)", config_key="show_browser", config=self.tiktok_config, values=['Yes', 'No'])
            self.file_name_var, self.start_index_var = create_frame_label_input_input(self.root, label_text="Tên file theo chỉ số", width=self.width, place_holder1="Nhập tên file có chứa chuỗi <index>", place_holder2="chỉ số bắt đầu")
            self.filter_by_views_var = self.create_settings_input("Lọc theo số lượt xem", "filter_by_views", config=self.tiktok_config, values=["100000", "200000", "300000", "500000", "1000000"], left=0.4, right=0.6)
            self.download_by_search_url_var = create_frame_button_and_input(self.root,text="Tải video từ Link kết quả tìm kiếm", command=start_download_by_search_url, left=0.4, right=0.6, width=self.width)
            self.download_by_channel_url_var = create_frame_button_and_input(self.root,text="Tải video từ Link kênh tiktok", command=start_download_by_channel_url, left=0.4, right=0.6, width=self.width)
            self.download_by_video_url_var = create_frame_button_and_input(self.root,text="Tải video từ Link video", command=start_download_by_video_url, left=0.4, right=0.6, width=self.width)
            self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu file", command=self.choose_folder_to_save, left=0.4, right=0.6, width=self.width)
            self.download_folder_var.insert(0, self.tiktok_config['download_folder'])
            create_button(self.root, text="Back", command=self.get_start_tiktok, width=self.width)

    def choose_folder_to_save(self):
        self.download_folder = filedialog.askdirectory()
        self.download_folder_var.delete(0, ctk.END)
        self.download_folder_var.insert(0, self.download_folder)

    def download_videos_by_video_url(self):
        video_url = self.download_by_video_url_var.get()
        if not video_url:
            notification(self.root, "Hãy nhập link tải video.")
            return
        if download_video_by_url(video_url, self.tiktok_config['download_folder']):
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
                        file_path = os.path.join(self.download_folder, f"{name}.mp4")
                    else:
                        file_path = None
                    if download_video_by_url(url, download_folder=self.download_folder, file_path=file_path):
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
            print("Đã đóng trình duyệt.")

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
            self.root.title(f"Tiktok: {self.account}")
            self.width = 400
            self.height_window = 170
            self.is_start_tiktok = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video Tiktok: {self.account}")
            self.width = 800
            self.height_window = 730
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos Tiktok")
            self.width = 700
            self.height_window = 463
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