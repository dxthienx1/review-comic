from common_function import *
from common_function_CTK import *

class FacebookManager:
    def __init__(self, account, password, page_name, download_thread=None, upload_thread=None, is_auto_upload=False):
        self.download_thread = download_thread
        self.upload_thread = upload_thread
        self.account = account
        self.password = password
        self.page_name = page_name
        self.is_auto_upload = is_auto_upload
        if not is_auto_upload:
            self.root = ctk.CTk()
            self.title = self.root.title(account)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.is_schedule = False
        else:
            self.is_schedule = True
        self.width = 500

        self.get_facebook_config()
        self.driver = None
        self.cookies_info = {}
        self.local_storage_info = {}

        self.is_start_tiktok = True
        self.download_thread = None
        self.download_thread_url = None
        self.is_upload_video_window = False
        self.is_stop_upload = False
        self.is_stop_download = False
        self.is_first_start = True
    
    def get_start_facebook(self):
        if not self.is_first_start:
            self.reset()
        else:
            self.is_first_start = False
        
        self.is_start_facebook = True
        self.show_window()
        self.setting_window_size()
        create_button(frame = self.root, text="Upload Videos", command= self.open_upload_video_window)
        create_button(frame = self.root, text="Download Videos", command=self.open_download_page_video_window)
        try:
            self.root.mainloop()
        except:
            getlog()

    def get_facebook_config(self):
        self.facebook_config = get_json_data(facebook_config_path)

    def open_upload_video_window(self):
        self.reset()
        self.is_upload_video_window = True
        self.show_window()
        self.setting_window_size()

        def load_template():
            self.get_facebook_config()
            template_name = self.load_template_var.get()
            temppale = self.facebook_config['template'][template_name]
            self.title_var.delete(0, ctk.END)
            self.title_var.insert(0, temppale['title'])
            self.description_var.delete("1.0", ctk.END)
            self.description_var.insert(ctk.END, temppale['description'])
            self.upload_date_var.delete(0, ctk.END)
            self.upload_date_var.insert(0, temppale['upload_date'])
            self.publish_times_var.delete(0, ctk.END)
            self.publish_times_var.insert(0, temppale['publish_times'])
            self.is_title_plus_video_name_var.set(convert_boolean_to_Yes_No(temppale['is_title_plus_video_name']))
            self.show_browser_var.set(convert_boolean_to_Yes_No(self.facebook_config['show_browser']))
            self.is_delete_after_upload_var.set(convert_boolean_to_Yes_No(temppale['is_delete_after_upload']))
            self.is_move_after_upload_var.set(convert_boolean_to_Yes_No(temppale['is_move_after_upload']))
            self.is_reel_video_var.set(convert_boolean_to_Yes_No(temppale['is_reel_video']))
            self.waiting_verify_var.set(convert_boolean_to_Yes_No(temppale['waiting_verify']))
            self.upload_folder_var.delete(0, ctk.END)
            self.upload_folder_var.insert(0, temppale['upload_folder'])
            self.number_of_days_var.delete(0, ctk.END)
            self.number_of_days_var.insert(0, temppale['number_of_days'])
            self.day_gap_var.delete(0, ctk.END)
            self.day_gap_var.insert(0, temppale['day_gap'])

        def choose_folder_upload():
            folder = choose_folder()
            if folder:
                self.upload_folder_var.delete(0, ctk.END)
                self.upload_folder_var.insert(0, folder)
        self.title_var = self.create_settings_input("Tiêu đề", "title", left=0.3, right=0.7)
        self.is_title_plus_video_name_var = self.create_settings_input("Thêm tên video vào tiêu đề", "is_title_plus_video_name", values=["Yes", "No"], left=0.3, right=0.7)
        self.description_var = self.create_settings_input("Mô tả", "description", is_textbox=True, left=0.3, right=0.7)
        self.upload_date_var = self.create_settings_input("Ngày đăng(yyyy-mm-dd)", "upload_date", left=0.3, right=0.7)
        self.publish_times_var = self.create_settings_input("Giờ đăng(vd: 08:00)", "publish_times", left=0.3, right=0.7)
        self.number_of_days_var = self.create_settings_input("Số ngày muốn đăng", "number_of_days", left=0.3, right=0.7)
        self.day_gap_var = self.create_settings_input("Khoảng cách giữa các ngày đăng", "day_gap", left=0.3, right=0.7)
        self.is_delete_after_upload_var = self.create_settings_input("Xóa video sau khi đăng", "is_delete_after_upload", values=["Yes", "No"], left=0.3, right=0.7)
        self.is_move_after_upload_var = self.create_settings_input("Di chuyển video sau khi đăng", "is_move_after_upload", values=["Yes", "No"], left=0.3, right=0.7)
        self.is_reel_video_var = self.create_settings_input("Đây là thước phim?", "is_reel_video", values=["Yes", "No"], left=0.3, right=0.7)
        self.waiting_verify_var = self.create_settings_input("Thêm thời gian chờ xác minh", "waiting_verify", values=["Yes", "No"], left=0.3, right=0.7)
        self.show_browser_var = self.create_settings_input(label_text="Hiển thị trình duyệt", config_key="show_browser", values=['Yes', 'No'], left=0.3, right=0.7, is_data_in_template=False)
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa video", command=choose_folder_upload, width=self.width, left=0.3, right=0.7)
        self.upload_folder_var.insert(0, self.facebook_config['template'][self.page_name]['upload_folder'])
        self.load_template_var = create_frame_button_and_combobox(self.root, "Tải mẫu có sẵn", command=load_template, values=[key for key in self.facebook_config['template'].keys()], width=self.width, left=0.3, right=0.7)
        self.load_template_var.set(self.page_name)
        create_frame_button_and_button(self.root, text1="Đăng video ngay", text2="Lên lịch đăng video", command1=self.start_upload_video_now, command2=self.start_schedule_upload, width=self.width, left=0.5, right=0.5)
        create_button(self.root, text="Lùi lại", command=self.get_start_facebook, width=self.width)

    def start_schedule_upload(self):
        self.is_schedule = True
        if not self.save_upload_setting():
            return
        self.start_thread_upload_video()
    def start_upload_video_now(self):
        self.is_schedule = False
        if not self.save_upload_setting():
            return
        self.start_thread_upload_video()

    def start_thread_upload_video(self):
        if not self.upload_thread or not self.upload_thread.is_alive():
            self.is_stop_upload = False
            self.upload_video_thread = threading.Thread(target=self.upload_video)
            self.upload_video_thread.start()

    def save_upload_setting(self):
        def check_publish_times_facebook(publish_times):
            try:
                publish_times = publish_times.split(',')
                for time in publish_times:
                    get_time = get_pushlish_time_hh_mm(time, facebook_time=True)
                    if not get_time:
                        return False
                return True
            except:
                return False
        videos_folder = self.upload_folder_var.get()
        if not videos_folder:
            notification(self.root, "Vui lòng chọn thư mục chứa video!")
            return False
        try:
            self.get_facebook_config()
            upload_date = self.upload_date_var.get()
            is_valid_date, message = is_format_date_yyyymmdd(upload_date, daydelta=29)
            if not is_valid_date:
                notification(self.root, message)
                return False
            publish_times = self.publish_times_var.get()
            if self.is_schedule:
                if not check_publish_times_facebook(publish_times):
                    return
            self.facebook_config['template'][self.page_name]["title"] = self.title_var.get()
            self.facebook_config['template'][self.page_name]["description"] = self.description_var.get("1.0", ctk.END).strip()
            self.facebook_config['template'][self.page_name]["upload_date"] = upload_date
            self.facebook_config['template'][self.page_name]["publish_times"] = publish_times
            self.facebook_config['template'][self.page_name]["is_title_plus_video_name"] = self.is_title_plus_video_name_var.get() == "Yes"
            self.facebook_config['template'][self.page_name]["upload_folder"] = self.upload_folder_var.get()
            self.facebook_config['template'][self.page_name]["is_delete_after_upload"] = self.is_delete_after_upload_var.get() == 'Yes'
            self.facebook_config['template'][self.page_name]["is_move_after_upload"] = self.is_move_after_upload_var.get() == 'Yes'
            self.facebook_config['template'][self.page_name]["is_reel_video"] = self.is_reel_video_var.get() == 'Yes'
            self.facebook_config['template'][self.page_name]["waiting_verify"] = self.waiting_verify_var.get() == 'Yes'
            self.facebook_config['template'][self.page_name]["number_of_days"] = self.number_of_days_var.get()
            self.facebook_config['template'][self.page_name]["day_gap"] = self.day_gap_var.get()
            self.facebook_config['show_browser'] = self.show_browser_var.get() == "Yes"
            self.save_facebook_config()
            return True
        except:
            getlog()
            return False
        

    def open_download_page_video_window(self):
        self.reset()
        self.is_download_video_window = True
        self.show_window()
        self.setting_window_size()

        def choose_folder_to_save():
            download_folder = choose_folder()
            if download_folder:
                self.download_folder_var.delete(0, ctk.END)
                self.download_folder_var.insert(0, download_folder)
                self.facebook_config['download_folder'] = download_folder
                self.save_facebook_config()

        def download_page_videos_now():
            try:
                t = time()
                video_urls = []
                page_link = self.page_link_var.get()
                if self.login(is_download=True):
                    self.driver.get(page_link)
                    press_esc_key(2, self.driver)
                    sleep(2)
                    last_height = self.driver.execute_script("return document.body.scrollHeight") # Tự động cuộn trang
                    cnt_search = 0
                    k = False
                    print(f"Bắt đầu quét video trong trang facebook theo link {page_link}...")
                    while True:
                        if self.is_stop_download:
                            break
                        self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);") # Cuộn xuống cuối trang
                        sleep(2)
                        new_height = self.driver.execute_script("return document.body.scrollHeight") # Tính chiều cao mới của trang
                        if new_height == last_height: # Kiểm tra nếu không có thêm nội dung mới
                            if k:
                                break
                            else:
                                k = True
                                sleep(6)
                                continue
                        k = False
                        last_height = new_height
                        cnt_search += 1
                        if cnt_search > 250:
                            break

                    # link_video_eles = self.driver.find_elements(By.XPATH, './/a[contains(@href, "/videos/")]')
                    link_video_eles = self.driver.find_elements(By.XPATH, './/a[contains(@href, "/videos/") and not(contains(@href, "?comment"))]')
                    if len(link_video_eles) > 0:
                        for ele in link_video_eles:
                            if self.is_stop_download:
                                    break
                            url = ele.get_attribute('href') or None
                            if url and url not in video_urls:
                                video_urls.append(url)
                        t1 = int(time() - t)
                        print(f'Thời gian quét video là {int(t1/60)} phút {t1%60} giây --> Tổng tìm thấy {len(link_video_eles)} video ...')
                    else:
                        print(f"Không tìm thấy video nào từ link {page_link}")
                    if len(video_urls) > 0:
                        print('Quá trình tải video bắt đầu ...')
                        download_info = get_json_data(download_info_path)
                        cnt = 0
                        for url in video_urls:
                            if self.is_stop_download:
                                    break
                            if download_video_by_url(url, self.facebook_config['download_folder']):
                                if url not in download_info['downloaded_urls']:
                                    download_info['downloaded_urls'].append(url)
                                    video_urls.remove(url)
                                    save_to_json_file(download_info, download_info_path)
                                    cnt += 1
                    if len(video_urls) > 0:
                        save_list_to_txt(video_urls, f"{os.path.join(self.facebook_config['download_folder'], 'danh sach video chua tai.txt')}")
                    if cnt > 0:
                        print(f'Đã tải thành công {cnt} video')
                    else:
                        print('Không tải được video.')
                self.close()
            except:
                getlog()
                if len(video_urls) > 0:
                    save_list_to_txt(video_urls, f"{os.path.join(self.facebook_config['download_folder'], 'danh sach video chua tai.txt')}")
                self.close()

        def start_thread_download_page_video():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                self.download_thread = threading.Thread(target=download_page_videos_now)
                self.download_thread.start()
        
        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu video", command=choose_folder_to_save, width=self.width, left=0.35, right=0.65)
        self.download_folder_var.insert(0, self.facebook_config['download_folder'])
        self.page_link_var = create_frame_button_and_input(self.root,text="Tải từ link trang facebook", command=start_thread_download_page_video, width=self.width, left=0.35, right=0.65)
        create_button(self.root, text="Lùi lại", command=self.get_start_facebook, width=self.width)

#-----------------------------------Đăng Nhập FB--------------------------------------------
    def load_session(self, url="https://www.facebook.com"):
        self.driver.get(url)
        sleep(2)
        try:
            self.cookies_info = get_json_data(facebook_cookies_path)
            if not self.cookies_info:
                self.cookies_info = {}
            if 'facebook' not in self.cookies_info:
                self.cookies_info['facebook'] = {}
            if self.account in self.cookies_info['facebook']:
                current_cookies = self.cookies_info['facebook'][self.account]
                for cookie in current_cookies:
                    if 'domain' in cookie and cookie['domain'] in self.driver.current_url:
                        self.driver.add_cookie(cookie)
                    elif 'domain' not in cookie:
                        self.driver.add_cookie(cookie)
        except FileNotFoundError:
            sleep(0.1)
        try:
            self.local_storage_info = get_json_data(local_storage_path)
            if not self.local_storage_info:
                self.local_storage_info = {}
            if 'facebook' not in self.local_storage_info:
                self.local_storage_info['facebook'] = {}
            if self.account in self.local_storage_info['facebook']:
                local_storage = self.local_storage_info['facebook'][self.account]
                for key, value in local_storage.items():
                    self.driver.execute_script(f"window.localStorage.setItem('{key}', '{value}');")
            sleep(0.5)
            self.driver.refresh()
            sleep(3)
        except FileNotFoundError:
            sleep(0.1)

    def save_session(self):
        if 'facebook' not in self.cookies_info:
            self.cookies_info['facebook'] = {}
        self.cookies_info['facebook'][self.account] = self.driver.get_cookies()
        save_to_json_file(self.cookies_info, facebook_cookies_path)
        if 'facebook' not in self.local_storage_info:
            self.local_storage_info['facebook'] = {}
        local_storage = self.driver.execute_script("return {...window.localStorage};")
        self.local_storage_info['facebook'][self.account] = local_storage
        save_to_json_file(self.local_storage_info, local_storage_path)

    def waiting_for_capcha_verify(self):
        sleep(2)
        if self.facebook_config['template'][self.page_name]['waiting_verify']:
            sleep(28)
        self.save_session()

    def login(self, is_download=False):
        try:
            if is_download:
                self.driver = get_driver(show=False)
            else:
                self.driver = get_driver(show=self.facebook_config['show_browser'])
            self.load_session()
            self.profile_element, language = self.get_profile_element()
            if not self.profile_element:
                email_input = self.driver.find_element(By.ID, 'email')
                email_input.send_keys(self.account)
                sleep(0.8)
                password_input = self.driver.find_element(By.ID, 'pass')
                password_input.send_keys(self.password)
                sleep(0.8)
                password_input.send_keys(Keys.RETURN)
                sleep(2)
                self.waiting_for_capcha_verify()
                self.profile_element, language = self.get_profile_element()
            if self.profile_element:
                if language == 'en':
                    self.en_language = True
                else:
                    self.en_language = False
                print("Đăng nhập thành công!")
                return True
            else:
                print("Đăng nhập không thành công, có thể cần xác minh tài khoản!")
                return False
        except:
            getlog()
            if self.is_auto_upload:
                print("Lỗi khi đăng nhập, có thể do đường truyền mạng không ổn định!")
            else:
                notification(self.root, "Lỗi khi đăng nhập, có thể do đường truyền mạng không ổn định!")
            return False
        

#-----------------------------------Thao tác trên facebook--------------------------------------------  

    def try_click_page_list(self):
        xpath = get_xpath('span', "x193iq5w xeuugli x13faqbe x1vvkbs x1xmvt09 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x xudqn12 x3x7a5m x6prxxf xvq8zen xk50ysn x1qq9wsj")
        if self.en_language:
            page_list_ele = get_element_by_xpath(self.driver, xpath, 'See all profiles')
        else:
            page_list_ele = get_element_by_xpath(self.driver, xpath, 'Xem tất cả trang cá nhân')
        if page_list_ele:
            page_list_ele.click()
            sleep(1)
        else:
            print("Dừng đăng video vì không tìm thấy danh sách trang!")
            self.is_stop_upload = True

    def click_page_list(self):
        if self.en_language:
            xpath = get_xpath('div', "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3", "aria-label", "See all profiles")
        else:
            xpath = get_xpath('div', "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3", "aria-label", "Xem tất cả trang cá nhân")
        page_list_ele = get_element_by_xpath(self.driver, xpath, 'See all profiles')
        if page_list_ele:
            page_list_ele.click()
            sleep(1)
        else:
            self.try_click_page_list()

    def get_profile_element(self):
        profile_xpath = get_xpath("div", "x1i10hfl x1qjc9v5 xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xdl72j9 x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xeuugli xexx8yu x4uap5 x18d9i69 xkhd6sd x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x1q0g3np x87ps6o x1lku1pv x1a2a7pz xzsf02u x1rg5ohu")
        profile_element = get_element_by_xpath(self.driver, profile_xpath, "Your profile")
        if profile_element:
            return profile_element, 'en'
        else:
            profile_element = get_element_by_xpath(self.driver, profile_xpath, "Trang cá nhân của bạn")
            if profile_element:
                return profile_element, 'vi'
            else:
                return None, None

    def click_element_by_js(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(1)
            
    def get_element_by_class(self, class_name, key=None):
        elements = self.driver.find_elements(By.CLASS_NAME, class_name)
        kq = []
        if len(elements) > 0:
            if key:
                for ele in elements:
                    if key in ele.accessible_name or key in ele.text or key in ele.tag_name or key in ele.aria_role:
                        kq.append(ele)
                        break
                if len(kq) > 0:
                    ele = kq[0]
                else:
                    ele = None
            else:
                ele = elements[0]
        else:
            ele = None
        return ele
    
    def get_element_by_id(self, id):
        element = self.driver.find_element(By.ID, id)
        return element

    def close(self):
        if self.driver:
            self.driver.quit()
            print("Đã đóng trình duyệt.")

    def click_schedule_link(self):
        xpath  = get_xpath_by_multi_attribute("a", ["role='link'"])
        ele = get_element_by_xpath(self.driver, xpath, "Meta Business Suite")
        if ele:
            link = ele.get_attribute('href')
            self.driver.get(link) 
            sleep(4)

    def get_meta_business_suite(self):
        def click_page_name():
            xpath = get_xpath('div', 'x1xqt7ti xsuwoey x63nzvj xbsr9hj xuxw1ft x6ikm8r x10wlt62 xlyipyv x1mzt3pk x1vvkbs x13faqbe x1fcty0u xeuugli')
            ele = get_element_by_xpath(self.driver, xpath, self.page_name)
            if ele:
                if ele.text == self.page_name:
                    ele.click()
                    return True
            return False
    
        def check_meta_bussiness_name():
            xpath = get_xpath('div', 'xmi5d70 x1fvot60 xxio538 xbsr9hj xuxw1ft x6ikm8r x10wlt62 xlyipyv x1h4wwuj x1fcty0u')
            ele = get_element_by_xpath(self.driver, xpath)
            if ele:
                page = ele.text
                if page != self.page_name:
                    ele.click()
                    if not click_page_name():
                        print(f'Có lỗi trong quá trình chuyển trang {self.page_name} trên Meta Bussiness Suite')
                        self.is_stop_upload = True
                        
        self.driver.get("https://business.facebook.com/latest/home?")
        sleep(3)
        check_meta_bussiness_name()
        self.driver.get("https://www.facebook.com/latest/content_calendar?")
        sleep(3)

    def click_option_menu(self):
        att1 = "class='x3nfvp2 x120ccyz x1heor9g x2lah0s x1c4vz4f x1gryazu'"
        att2 = "role='presentation'"
        xpath = get_xpath_by_multi_attribute("div", [att1, att2])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(2)
    def input_date(self, date):
        att1 = "class='xjbqb8w x972fbf xcfux6l x1qhh985 xm0m39n xdj266r x11i5rnm xat24cr x1mh8g0r x1t137rt xexx8yu x4uap5 x18d9i69 xkhd6sd xlyipyv xr4vacz x1gnnqk1 xbsr9hj x1urst0s x1glnyev x1ad04t7 x1ix68h3 x19gujb8 xni1clt x1tutvks xfrpkgu x15h3p50 x1gf4pb6 xh7izdl x10emqs4 x2yyzbt xu8dvwe xmi5d70 x1fvot60 xo1l8bm xxio538 xh8yej3'"
        if self.en_language:
            att2 = "placeholder='mm/dd/yyyy'"
            upload_date = convert_date_format_yyyymmdd_to_mmddyyyy(date)
        else:
            att2 = "placeholder='dd/mm/yyyy'"
            upload_date = convert_date_format_yyyymmdd_to_mmddyyyy(date, vi_date=True)
        xpath = get_xpath_by_multi_attribute("input", [att1, att2])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.send_keys(Keys.CONTROL + "a")
            ele.send_keys(upload_date)
            sleep(1)
    def input_hours(self, hour):
        if self.en_language:
            xpath = get_xpath('input', 'x972fbf xcfux6l x1qhh985 xm0m39n x5yr21d xg01cxk xexx8yu x4uap5 x18d9i69 xkhd6sd x10l6tqk x17qophe x13vifvy xuxw1ft xh8yej3', 'aria-label', 'hours')
        else:
            xpath = get_xpath('input', 'x972fbf xcfux6l x1qhh985 xm0m39n x5yr21d xg01cxk xexx8yu x4uap5 x18d9i69 xkhd6sd x10l6tqk x17qophe x13vifvy xuxw1ft xh8yej3', 'aria-label', 'giờ')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.send_keys(hour)
            sleep(1)
    def input_minutes(self, minute):
        if self.en_language:
            xpath = get_xpath('input', 'x972fbf xcfux6l x1qhh985 xm0m39n x5yr21d xg01cxk xexx8yu x4uap5 x18d9i69 xkhd6sd x10l6tqk x17qophe x13vifvy xuxw1ft xh8yej3', 'aria-label', 'minutes')
        else:
            xpath = get_xpath('input', 'x972fbf xcfux6l x1qhh985 xm0m39n x5yr21d xg01cxk xexx8yu x4uap5 x18d9i69 xkhd6sd x10l6tqk x17qophe x13vifvy xuxw1ft xh8yej3', 'aria-label', 'phút')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.send_keys(minute)
            sleep(1)

    def input_AM_or_PM(self, meridiem):
        att1 = "class='x972fbf xcfux6l x1qhh985 xm0m39n x5yr21d xg01cxk xexx8yu x4uap5 x18d9i69 xkhd6sd x10l6tqk x17qophe x13vifvy xuxw1ft xh8yej3'"
        att2 = "aria-label='meridiem'"
        xpath = get_xpath_by_multi_attribute("input", [att1, att2])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.send_keys(meridiem)
            sleep(2)
    def click_update_schedule_button(self):
        xpath = get_xpath('div', "x1xqt7ti x1fvot60 xk50ysn xxio538 x1heor9g xuxw1ft x6ikm8r x10wlt62 xlyipyv x1h4wwuj xeuugli")
        if self.en_language:
            ele = get_element_by_xpath(self.driver, xpath, "Update")
        else:
            ele = get_element_by_xpath(self.driver, xpath, "Cập nhật")
        if ele:
            ele.click()
            sleep(1)
    def click_public_schedule_button(self):
        xpath = get_xpath('div', "x1xqt7ti x1fvot60 xk50ysn xxio538 x1heor9g xuxw1ft x6ikm8r x10wlt62 xlyipyv x1h4wwuj xeuugli")
        if self.en_language:
            ele = get_element_by_xpath(self.driver, xpath, "Publish")
        else:
            ele = get_element_by_xpath(self.driver, xpath, "Đăng")
        if ele:
            ele.click()
            sleep(5)
    def click_schedule_option(self):
        xpath = get_xpath('div', "x1xqt7ti x1fvot60 xk50ysn xxio538 x1heor9g xuxw1ft x6ikm8r x10wlt62 xlyipyv x1h4wwuj xeuugli")
        if self.en_language:
            ele = get_element_by_xpath(self.driver, xpath, "Schedule")
        else:
            ele = get_element_by_xpath(self.driver, xpath, "Lên lịch")
        if ele:
            ele.click()
            sleep(1)

    def click_bulk_upload_video_button(self):
        xpath = get_xpath("div", "xmi5d70 x1fvot60 xo1l8bm xxio538 xbsr9hj xq9mrsl x1mzt3pk x1vvkbs x13faqbe xeuugli x1iyjqo2")
        if self.en_language:
            if self.is_reel_video:
                ele = get_element_by_xpath(self.driver, xpath, "Bulk upload reels")
            else:
                ele = get_element_by_xpath(self.driver, xpath, "Bulk upload videos")
        else:
            if self.is_reel_video:
                ele = get_element_by_xpath(self.driver, xpath, "Tải hàng loạt thước phim lên")
            else:
                ele = get_element_by_xpath(self.driver, xpath, "Tải video lên hàng loạt")
        if ele:
            ele.click()
            sleep(5)

    def input_schedule_video_on_facebook(self, video_path):
        att1 = "accept='video/*'"
        att2 = "class='_44hf'"
        xpath = get_xpath_by_multi_attribute("input", [att1, att2])
        ele = get_element_by_xpath(self.driver, xpath, )
        if ele:
            ele.send_keys(video_path)
            sleep(2)
        else:
            self.is_stop_upload = True

    def click_upload_video_icon(self):
        xpath_photo_video = "//div[@class=\"x1i10hfl xjbqb8w xjqpnuy xa49m3k xqeqjp1 x2hbi6w x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x87ps6o x1lku1pv x1a2a7pz x6s0dn4 x1lq5wgf xgqcy7u x30kzoy x9jhf4c x78zum5 x1r8uery x1iyjqo2 xs83m0k xl56j7k x1pshirs x1y1aw1k x1sxyh0 xwib8y2 xurb0ha\"]"
        if self.en_language:
            if self.is_reel_video:
                photo_video_button = get_element_by_xpath(self.driver, xpath_photo_video, "Reel")
            else:
                photo_video_button = get_element_by_xpath(self.driver, xpath_photo_video, "photo/video")
        else:
            if self.is_reel_video:
                photo_video_button = get_element_by_xpath(self.driver, xpath_photo_video, "Thước phim")
            else:
                photo_video_button = get_element_by_xpath(self.driver, xpath_photo_video, "Ảnh/video")
        if photo_video_button:
            photo_video_button.click()
            sleep(1.5)

    def input_video_on_facebook(self, video_path):
        if self.is_reel_video:
            xpath = get_xpath('input', 'x1s85apg', 'accept', 'video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv')
        else:
            xpath = "//input[@accept='image/*,image/heif,image/heic,video/*,video/mp4,video/x-m4v,video/x-matroska,.mkv' and @class='x1s85apg']"
        upload_input = get_element_by_xpath(self.driver, xpath)
        if upload_input:
            upload_input.send_keys(video_path)
            sleep(2)

    def input_title(self, title):
        title_xpath = get_xpath("div", "xzsf02u x1a2a7pz x1n2onr6 x14wi4xw x9f619 x1lliihq x5yr21d xh8yej3 notranslate")
        if self.en_language:
            title_element = get_element_by_xpath(self.driver, title_xpath, "What's on your mind")
        else:
            title_element = get_element_by_xpath(self.driver, title_xpath, "bạn đang nghĩ gì thế?")
        if title_element:
            title_element.send_keys(title)
            sleep(2)
        else:
            self.is_stop_upload = True

    def check_status_upload_video(self):
        status_xpath = get_xpath("div", "x117nqv4 x1sln4lm xexx8yu x10l6tqk xh8yej3", contain=True)
        # status_xpath = "//div[contains(@class, 'x117nqv4') and contains(@class, 'x1sln4lm') and contains(@class, 'xexx8yu') and contains(@class, 'x10l6tqk') and contains(@class, 'xh8yej3')]"
        cnt = 0
        pre_v = "0%"
        while True:
            if self.is_stop_upload:
                break
            try:
                status_xpath_element = get_element_by_xpath(self.driver, status_xpath)
                v = status_xpath_element.text
                if v != pre_v:
                    print(v)
                    pre_v = v
                if v == "100%":
                    break
            except:
                cnt += 1
                if cnt > 10:
                    self.is_stop_upload = True
            sleep(2)

    def check_status_schedule_upload_video(self):
        status_xpath = get_xpath("span", "xmi5d70 xw23nyj xo1l8bm x63nzvj xbsr9hj xq9mrsl x1h4wwuj xeuugli xsgj6o6")
        cnt = 0
        pre_v = "0%"
        while True:
            if self.is_stop_upload:
                break
            try:
                status_xpath_element = get_element_by_xpath(self.driver, status_xpath)
                v = status_xpath_element.text
                if v != pre_v:
                    sys.stdout.write(f'\rĐã tải lên được {v} ...')
                    sys.stdout.flush()
                    # print(f'Đã tải lên được {v} ...')
                    pre_v = v
                if v == "100%":
                    break
            except:
                cnt += 1
                if cnt > 10:
                    self.is_stop_upload = True
            sleep(2)

    def input_description(self, description):
        try:
            if self.en_language:
                xpath = get_xpath('div', "notranslate _5rpu", attribute="aria-label", attribute_value="Write into the dialogue box to include text with your post.")
            else:
                xpath = get_xpath('div', "notranslate _5rpu", attribute="aria-label", attribute_value="Hãy viết vào ô hộp thoại để thêm văn bản vào bài viết.")
            ele = get_element_by_xpath(self.driver, xpath)
            if ele:
                ele.send_keys(description)
        except:
            getlog()

    def change_page(self):
        try:
            press_esc_key(4, self.driver)
            self.profile_element.click()
            sleep(1)
            self.click_page_list()
            page_xpath = f"//div[span[text()='{self.page_name}']]"
            page_element = get_element_by_xpath(self.driver, page_xpath, self.page_name)
            page_element.click()
            print(f'Đã chuyển sang trang {self.page_name}')
            sleep(4)
            press_esc_key(2, self.driver)
            return True
        except:
            return False

    def check_switch_button(self):
        xpath = get_xpath("div", "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3")
        element = get_element_by_xpath(self.driver, xpath, "Switch Now")
        if element:
            element.click()
            sleep(4)
    
    def click_next_button_if_short_video(self):
        for i in range(2):
            if self.en_language:
                xpath = get_xpath("div", "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3", "aria-label", "Next")
            else:
                xpath = get_xpath("div", "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3", "aria-label", "Tiếp")
            element = get_element_by_xpath(self.driver, xpath)
            if element:
                element.click()
                sleep(1)
    
    def input_describe_short_video(self, text):
        if self.en_language:
            xpath = get_xpath("div", "xzsf02u x1a2a7pz x1n2onr6 x14wi4xw x9f619 x1lliihq x5yr21d xh8yej3 notranslate", "aria-label", "Describe your reel...")
        else:
            xpath = get_xpath("div", "xzsf02u x1a2a7pz x1n2onr6 x14wi4xw x9f619 x1lliihq x5yr21d xh8yej3 notranslate", "aria-label", "Mô tả thước phim của bạn...")
        element = get_element_by_xpath(self.driver, xpath)
        if element:
            element.send_keys(text)
            sleep(1)

    def click_public_short_video(self):
        xpath = get_xpath("div", "x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3")
        cnt = 0
        while True:
            try:
                if self.is_stop_upload:
                    break
                if self.en_language:
                    element = get_element_by_xpath(self.driver, xpath, "Publish")
                else:
                    element = get_element_by_xpath(self.driver, xpath, "Đăng")
                if element:
                    element.click()
                    sleep(3)
                    break
            except:
                pass
            cnt += 1
            sleep(3)
            if cnt > 10:
                self.is_stop_upload = True

            

    def click_post_button(self):
        if self.en_language:
            xpath = get_xpath('div', 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3', 'aria-label', 'Post')
        else:
            xpath = get_xpath('div', 'x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x1ypdohk xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1o1ewxj x3x9cwd x1e5q0jg x13rtm0m x87ps6o x1lku1pv x1a2a7pz x9f619 x3nfvp2 xdt5ytf xl56j7k x1n2onr6 xh8yej3', 'aria-label', 'Đăng')
        element = get_element_by_xpath(self.driver, xpath)
        if element:
            element.click()
            print("Đang tiến hành đăng video...")
            sleep(5)
        else:
            print("không tìm thấy post_button")

    def upload_video(self):
        try:
            videos_folder = self.facebook_config['template'][self.page_name]['upload_folder']
            self.is_reel_video = self.facebook_config['template'][self.page_name]['is_reel_video']
            if not check_folder(videos_folder):
                return False
            all_file = os.listdir(videos_folder)
            videos = [k for k in all_file if '.mp4' in k]
            if len(videos) == 0:
                if self.is_auto_upload:
                    print(f"Thư mục {videos_folder} không chứa video(loại \n.mp4\n).")
                else:
                    notification(self.root, f"Thư mục {videos_folder} không chứa video(loại \n.mp4\n).")
                return False
            videos = natsorted(videos)
            upload_count = 0
            date_cnt = 0
            time_cnt = 0
            number_of_days = get_number_of_days(self.facebook_config['template'][self.page_name]['number_of_days'])
            if self.is_schedule:
                # Xác định thời gian đăng cho video
                day_gap = get_day_gap(self.facebook_config['template'][self.page_name]['day_gap'])
                upload_date_yymmdd_str = self.facebook_config['template'][self.page_name]['upload_date']
                upload_date_yymmdd = convert_date_string_to_datetime(upload_date_yymmdd_str)
                upload_date_yymmdd = get_upload_date(upload_date_yymmdd)
                upload_date_yymmdd = convert_datetime_to_string(upload_date_yymmdd)
                publish_times_str = self.facebook_config['template'][self.page_name]['publish_times']
                publish_times = publish_times_str.split(',')
                if self.is_auto_upload:
                    number_of_days = 100
                    self.facebook_config['show_browser'] = False

            if not self.login():
                return
            if not self.change_page():
                print(f"Gặp lỗi khi chuyển trang {self.page_name}")
                return
            for i, video_file in enumerate(videos, start=0):
                if self.is_stop_upload:
                    break
                # self.check_switch_button()
                video_name = os.path.splitext(video_file)[0] #lấy tên
                title = self.facebook_config['template'][self.page_name]['title']
                description = self.facebook_config['template'][self.page_name]['description']
                if self.facebook_config['template'][self.page_name]['is_title_plus_video_name']:
                    full_title = f"{title} {video_name}"
                else:
                    full_title = title
                full_title = f"{full_title}"
                description=f"{full_title}\n{description}"

                video_path = os.path.join(videos_folder, video_file)
                print(f'--> Bắt đầu đăng video {video_file}')
                if self.is_schedule:
                    publish_time = publish_times[time_cnt].strip()
                    if self.en_language:
                        publish_time = get_pushlish_time_hh_mm(publish_time, facebook_time=True)
                        if not publish_time:
                            return
                        hour, minute, am_pm = publish_time.split(':')
                    else:
                        publish_time = get_pushlish_time_hh_mm(publish_time)
                        if not publish_time:
                            return
                        hour, minute = publish_time.split(':')
                    self.get_meta_business_suite()
                    if self.is_stop_upload:
                        break
                    try:
                        self.click_option_menu()
                    except:
                        press_esc_key(2, self.driver)
                        self.click_option_menu()

                    self.click_bulk_upload_video_button()
                    if self.is_stop_upload:
                        break
                    self.input_schedule_video_on_facebook(video_path)
                    if self.is_stop_upload:
                        break
                    self.input_description(description)
                    self.click_option_menu()
                    self.click_schedule_option()
                    self.input_date(upload_date_yymmdd)
                    if self.is_stop_upload:
                        break
                    self.input_hours(hour)
                    self.input_minutes(minute)
                    if self.en_language:
                        self.input_AM_or_PM(am_pm)
                    if self.is_stop_upload:
                        break
                    self.click_update_schedule_button()
                    self.check_status_schedule_upload_video()
                    if self.is_stop_upload:
                        break
                    self.click_public_schedule_button()
                    upload_count += 1
                    time_cnt += 1
                    if self.facebook_config['template'][self.page_name]['upload_date'] != upload_date_yymmdd:
                        self.facebook_config['template'][self.page_name]['upload_date'] = upload_date_yymmdd
                        self.save_facebook_config()
                    print(f'--> Đăng thành công video {video_file}')
                    remove_or_move_after_upload(video_path, self.facebook_config['template'][self.page_name]['is_delete_after_upload'], self.facebook_config['template'][self.page_name]['is_move_after_upload'], 'facebook_upload_finished')
                    if (time_cnt) % len(publish_times) == 0:
                        upload_date_yymmdd = add_date_into_string(upload_date_yymmdd, day_gap)
                        date_cnt += 1
                        time_cnt = 0
                        if date_cnt == number_of_days:
                            break
                        if is_date_greater_than_current_day(upload_date_yymmdd, 28):
                            print("Dừng đăng video vì ngày lên lịch đã vượt  quá giới hạn mà facebook cho phép(tối đa 29 ngày)")
                            break
                else:
                    if self.is_reel_video:
                        self.driver.get("https://www.facebook.com/reels/create/?surface=ADDL_PROFILE_PLUS")
                        sleep(1)
                        self.input_video_on_facebook(video_path)
                        press_esc_key(2, self.driver)
                        self.click_next_button_if_short_video()
                        self.input_describe_short_video(description)
                        press_esc_key(1, self.driver)
                        if self.is_stop_upload:
                            break
                        self.click_public_short_video()
                    else:
                        self.click_upload_video_icon()
                        self.input_video_on_facebook(video_path)
                        press_esc_key(1, self.driver)
                        self.input_title(description)
                        press_esc_key(1, self.driver)
                        self.check_status_upload_video()
                        if self.is_stop_upload:
                            break
                        self.click_post_button()
                    print(f'--> Đăng thành công video {video_file}')
                    remove_or_move_after_upload(video_path, self.facebook_config['template'][self.page_name]['is_delete_after_upload'], self.facebook_config['template'][self.page_name]['is_move_after_upload'], 'facebook_upload_finished')
                    upload_count += 1
                    if upload_count == number_of_days:
                        break
            if not self.is_auto_upload:
                notification(self.root, f"Đăng thành công {upload_count} video")
            else:
                print(f"Đăng thành công {upload_count} video")
            if upload_count > 0:
                return True
            else:
                return False
        except:
            getlog()
            return False
        finally:
            self.close()
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
        if self.is_start_facebook:
            self.root.title(f"Facebook: {self.account}")
            self.width = 500
            self.height_window = 170
            self.is_start_facebook = False
        elif self.is_upload_video_window:
            self.root.title(f"Facebook: {self.account}")
            self.width = 700
            self.height_window = 918
            self.is_upload_video_window = False
        elif self.is_download_video_window:
            self.root.title(f"Download Fanpage Videos")
            self.width = 500
            self.height_window = 217
            self.is_upload_video_window = False
       
        self.setting_screen_position()

    def save_facebook_config(self):
        save_to_json_file(self.facebook_config, facebook_config_path)

    def exit_app(self):
        self.reset()
        self.root.destroy()

    def on_close(self):
        self.save_facebook_config()
        self.reset()
        self.hide_window()
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", 1)
        self.root.attributes("-topmost", 0)

    def hide_window(self):
        self.root.iconify()
        self.root.withdraw()  # ẩn cửa sổ

    def reset(self):
        self.is_start_facebook = False
        self.clear_after_action()
        clear_widgets(self.root)
        self.root.withdraw()

    def clear_after_action(self):
        pass

    def create_settings_input(self, label_text, config_key=None, values=None, is_textbox = False, left=0.4, right=0.6, add_button=False, text=None, command=None, is_data_in_template=True):
        if is_data_in_template:
            config = self.facebook_config['template'][self.page_name]
        else:
            config = self.facebook_config
        frame = create_frame(self.root)
        if add_button:
            create_button(frame= frame, text=text, command=command, width=0.2, side=RIGHT)
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
            result = combobox
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            result = textbox
        else:
            if not config_key:
                var = ""
            else:
                var = config[config_key]
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            result = entry
        return result
        
