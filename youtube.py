
from common_function import *

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#-----------------------------------------------------------------------------------------------------------------
class YouTubeManager():
    def __init__(self, gmail, channel_name=None, is_auto_upload=False, download_thread=None, upload_thread=None):
        self.is_auto_upload = is_auto_upload
        if not is_auto_upload:
            self.root = ctk.CTk()
            self.title = self.root.title(gmail)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.width = width_window
            self.is_start_youtube = True
        self.download_thread = download_thread
        self.upload_thread = upload_thread
        self.gmail = gmail
        self.channel_name = channel_name
        self.get_youtube_config()
        self.youtube = None
        self.pre_time_check_status = 0

        self.list_videos_download_from_channel = []
        self.list_videos_detail = []
        self.list_video_ids_delete = []
        self.is_upload_video_window = False
        if is_auto_upload:
            self.is_schedule = True
        else:
            self.is_schedule = False
        self.is_download_window = False

        self.is_stop_download = False
        self.is_stop_upload = False
        self.is_first_start = True
        self.driver = None
        self.download_by_selenium = True
        self.cookies_var = None
        self.first_upload = False

#--------------------------------------Selenium--------------------------start

    def login(self, show=False):
        try:
            if self.cookies_var and self.cookies_var.get().strip():
                self.driver = get_driver(show=show)
                print(f'--> Đang sử dụng cookies để đăng nhập ...')
            else:
                self.driver = get_driver_with_profile(target_gmail=self.gmail, show=show)
                print(f'--> Đang sử dụng chrome profile để đăng nhập ...')
            if not self.driver:
                return
            self.driver.get("https://www.youtube.com/")
            sleep(3)
            press_esc_key(2, self.driver)
            account_menu, language = self.get_account_menu()
            if not account_menu:
                self.load_session()
                press_esc_key(2, self.driver)
                account_menu, language = self.get_account_menu()
            if account_menu:
                if language == 'en':
                    self.en_language = True
                else:
                    self.en_language = False
                press_esc_key(1, self.driver)
                account_menu.click()
                sleep(1)
                self.click_switch_account()
                return True
            else:
                print(f'Đăng nhập thất bại. Hãy thử dùng cookies mới nhất để đăng nhập !!!')
                return False
        except:
            getlog()
            return False

    def load_session(self, url="https://www.youtube.com/"):
        self.driver.get(url)
        sleep(1)
        try:
            youtube_cookies = get_pickle_data(youtube_cookies_path)
            cookies = youtube_cookies[self.gmail]
            for cookie in cookies:
                if "sameSite" in cookie:
                    if cookie["sameSite"] not in ["Strict", "Lax", "None"]:
                        cookie["sameSite"] = "None"
                else:
                    cookie["sameSite"] = "None"
                try:
                    self.driver.add_cookie(cookie)
                except:
                    getlog()
            sleep(1)
            self.driver.refresh()
            sleep(3)
        except:
            getlog()

    def click_switch_account(self):
        xpath = get_xpath('yt-formatted-string', 'style-scope ytd-compact-link-renderer')
        if self.en_language:
            ele = get_element_by_xpath(self.driver, xpath, 'Switch account')
        else:
            ele = get_element_by_xpath(self.driver, xpath, 'Chuyển đổi tài khoản')
        if ele:
            ele.click()
            sleep(0.5)
            self.choose_channel()

    def choose_channel(self):
        xpath= get_xpath('yt-formatted-string', 'style-scope ytd-account-item-renderer')
        ele = get_element_by_xpath(self.driver, xpath, self.channel_name)
        if ele:
            ele.click()
            sleep(1)

    def get_account_menu(self):
        xpath = get_xpath('button', 'style-scope ytd-topbar-menu-button-renderer', attribute='aria-label', attribute_value='Account menu')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            return ele, 'en'
        else:
            xpath = get_xpath('button', 'style-scope ytd-topbar-menu-button-renderer', attribute='aria-label', attribute_value='Trình đơn tài khoản')
            ele = get_element_by_xpath(self.driver, xpath)
            if ele:
                return ele, 'vi'
            else:
                return None, None
            
    def click_upload_video_button(self):
        xpath = get_xpath('yt-formatted-string', 'style-scope ytd-compact-link-renderer')
        if self.en_language:
            ele = get_element_by_xpath(self.driver, xpath, 'Upload video')
        else:
            ele = get_element_by_xpath(self.driver, xpath, 'Tải video lên')
        if ele:
            ele.click()
            sleep(2)

    def click_upload_button(self):
        if self.en_language:
            xpath = get_xpath_by_multi_attribute('button', ['aria-label="Create"'])
        else:
            xpath = get_xpath_by_multi_attribute('button', ['aria-label="Tạo"'])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(0.5)
            self.click_upload_video_button()

    def click_upload_button_again(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--outline ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m ytcp-button-shape-impl--icon-leading', attribute='aria-label', attribute_value='Create')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--outline ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m ytcp-button-shape-impl--icon-leading', attribute='aria-label', attribute_value='Tạo')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(0.4)
            self.click_upload_video_button_again()
    
    def click_upload_video_button_again(self):
        xpath = get_xpath('yt-formatted-string', 'item-text main-text style-scope ytcp-text-menu')
        if self.en_language:
            ele = get_element_by_xpath(self.driver, xpath, 'Upload video')
        else:
            ele = get_element_by_xpath(self.driver, xpath, 'Tải video lên')
        if ele:
            ele.click()
            sleep(1)
    
    def send_video_to_youtube(self, video_path):
        xpath = get_xpath_by_multi_attribute('input', ['type="file"', 'name="Filedata"'])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.send_keys(video_path)
            sleep(4.5)
    
    def check_daily_update_limit(self):
        err_xpath = get_xpath('div', 'error-short style-scope ytcp-uploads-dialog')
        if self.en_language:
            err_ele = get_element_by_xpath(self.driver, err_xpath, 'Daily upload limit')
        else:
            err_ele = get_element_by_xpath(self.driver, err_xpath, 'Đã đạt giới hạn tải video lên hằng ngày')
        if err_ele:
            notification(self.root, "Đã đạt giới hạn tải video lên hằng ngày. Có thể phải cần xác minh số điện thoại để tăng số lượt tải video mỗi ngày\n--> Dừng đăng video ...")
            self.is_stop_upload = True

    def input_title(self, title):
        if self.en_language:
            xpath = get_xpath('div', 'style-scope ytcp-social-suggestions-textbox', attribute='aria-label', attribute_value='Add a title that describes your video (type @ to mention a channel)')
        else:
            xpath = get_xpath('div', 'style-scope ytcp-social-suggestions-textbox', attribute='aria-label', attribute_value='Thêm tiêu đề để mô tả video của bạn (nhập ký tự @ để đề cập tên một kênh)')
        cnt = 0
        while True:
            ele = get_element_by_xpath(self.driver, xpath)
            if ele:
                press_esc_key(1, self.driver)
                ele.clear()
                ele.send_keys(title)
                sleep(1)
                break
            else:
                cnt += 1
                if cnt > 5:
                    break
                sleep(2)

    def input_description(self, description):
        if self.en_language:
            xpath = get_xpath('div', 'style-scope ytcp-social-suggestions-textbox', attribute='aria-label', attribute_value='Tell viewers about your video (type @ to mention a channel)')
        else:
            xpath = get_xpath('div', 'style-scope ytcp-social-suggestions-textbox', attribute='aria-label', attribute_value='Giới thiệu về video của bạn cho người xem (nhập ký tự @ để đề cập tên một kênh)')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.clear()
            ele.send_keys(description)
            press_esc_key(1, self.driver)

    def input_thumbnail(self, thumbnail_path):
        xpath = get_xpath('input', 'style-scope ytcp-thumbnail-uploader', attribute='accept', attribute_value='image/jpeg,image/png')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.send_keys(thumbnail_path)
            sleep(1)

    def choose_playlist(self, playlist_name):
        def click_done():
            if self.en_language:
                xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Done')
            else:
                xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Xong')
            ele = get_element_by_xpath(self.driver, xpath)
            if ele:
                ele.click()
                sleep(1)
        try:
            xpath = get_xpath('ytcp-text-dropdown-trigger', 'dropdown style-scope ytcp-video-metadata-playlists')
            dropdown = get_element_by_xpath(self.driver, xpath)
            if dropdown:
                self.scroll_into_view(dropdown)
                dropdown.click()
                sleep(1)
                xpath = get_xpath('span', 'checkbox-label style-scope ytcp-checkbox-group')
                ele = get_element_by_xpath(self.driver, xpath, playlist_name)
                if ele:
                    ele.click()
                    sleep(1)
                click_done()
        except:
            print("Chức năng chọn thumbnail chỉ áp dụng cho những tài khoản youtube đã xác minh số điện thoại !!!")
            
    
    def click_not_make_for_kid(self):
        xpath = get_xpath_by_multi_attribute('tp-yt-paper-radio-button', ['name="VIDEO_MADE_FOR_KIDS_NOT_MFK"'])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            try:
                ele.click()
                sleep(0.3)
            except:
                print(f'Có lỗi trong quá trình đăng video. Có thể tải khoản {self.gmail} đã đạt giới hạn đăng video trong ngày !!!')
                self.is_stop_upload = True

    def click_show_more(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Show more')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Hiện thêm')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            self.scroll_into_view(ele)
            ele.click()
            sleep(1)

    def click_altered_content(self, no_altered=True):
        if no_altered:
            xpath = get_xpath_by_multi_attribute('tp-yt-paper-radio-button', ['name="VIDEO_HAS_ALTERED_CONTENT_YES"'])
        else:
            xpath = get_xpath_by_multi_attribute('tp-yt-paper-radio-button', ['name="VIDEO_HAS_ALTERED_CONTENT_NO"'])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            self.scroll_into_view(ele)
            ele.click()
            sleep(0.5)

    def click_next_button(self):
        def add_an_end_screen():
            try:
                if self.en_language:
                    main_xpath = "//h3[text()='Add an end screen']/ancestor::div[@class='container style-scope ytcp-uploads-video-elements']"
                    add_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Add"'])
                    subscribe_xpath = get_xpath_by_multi_attribute('div', ['aria-label="1 video, 1 subscribe"'])
                    save_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Save"'])
                else:
                    main_xpath = "//h3[text()='Thêm màn hình kết thúc']/ancestor::div[@class='container style-scope ytcp-uploads-video-elements']"
                    add_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Thêm"'])
                    subscribe_xpath = get_xpath_by_multi_attribute('div', ['aria-label="1 video, 1 đăng ký"'])
                    save_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Lưu"'])
                main_ele = get_element_by_xpath(self.driver, main_xpath)
                if main_ele:
                    add_end = get_element_by_xpath(main_ele, add_xpath, index=1)
                    if add_end:
                        add_end.click()
                        sleep(3)
                        end_ele = get_element_by_xpath(self.driver, subscribe_xpath, index=0)
                        if end_ele:
                            end_ele.click()
                            sleep(1)
                        try:
                            save_ele = get_element_by_xpath(self.driver, save_xpath, index=1)
                        except:
                            save_ele = get_element_by_xpath(self.driver, save_xpath)
                        if save_ele:
                            save_ele.click()
                            sleep(3)
                else:
                    sleep(0.5)
            except:
                sleep(0.5)

        def add_related_video():
            def click_close():
                xpath = get_xpath_by_multi_attribute('ytcp-icon-button', ['icon="icons:close"'])
                ele = get_element_by_xpath(self.driver, xpath)
                if ele:
                    ele.click()
                    sleep(2)
            try:
                main_xpath = get_xpath_by_multi_attribute('div', ['id="upload-container"'])
                if self.en_language:
                    add_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Add"'])
                else:
                    add_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Thêm"'])
                related_xpath = get_xpath('ytcp-entity-card', 'card style-scope ytcp-video-pick-dialog-contents')
                main_ele = get_element_by_xpath(self.driver, main_xpath)
                if main_ele:
                    add_end = get_element_by_xpath(main_ele, add_xpath)
                    if add_end:
                        add_end.click()
                        related_ele = get_element_by_xpath(self.driver, related_xpath, index=0, timeout=6)
                        if related_ele:
                            related_ele.click()
                            sleep(2)
                        else:
                            press_esc_key(2, self.driver)
                            click_close()
                            self.first_upload = True
                else:
                    add_an_end_screen()
            except:
                sleep(0.5)
        try:
            if self.en_language:
                xpath = get_xpath_by_multi_attribute('button', ['aria-label="Next"'])
            else:
                xpath = get_xpath_by_multi_attribute('button', ['aria-label="Tiếp"'])
            next_ele = get_element_by_xpath(self.driver, xpath)
            if next_ele:
                self.scroll_into_view(next_ele)
                next_ele.click()
                sleep(1)
                if self.first_upload:
                    add_related_video()
                    sleep(1)
                try:
                    next_ele.click()
                except:
                    next_ele = get_element_by_xpath(self.driver, xpath)
                    try:
                        next_ele.click()
                    except:
                        if self.en_language:
                            print("Không tìm thấy nút \"Next\" --> Dừng đăng video ...")
                        else:
                            print("Không tìm thấy nút \"Tiếp\" --> Dừng đăng video ...")
                        self.is_stop_upload = True
                        return
                sleep(1)
                next_ele.click()
                sleep(1)
            else:
                if self.en_language:
                    print("Không tìm thấy nút \"Next\" --> Dừng đăng video ...")
                else:
                    print("Không tìm thấy nút \"Tiếp\" --> Dừng đăng video ...")
                self.is_stop_upload = True
        except:
            print("Có lỗi khi đăng video --> Dừng đăng video !!!")
            self.is_stop_upload = True

    
    def click_public_radio(self):
        xpath = get_xpath_by_multi_attribute('tp-yt-paper-radio-button', ['name="PUBLIC"'])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(1)

    def click_public_now(self):
        if self.en_language:
            xpath = get_xpath_by_multi_attribute('button', ['aria-label="Publish"'])
        else:
            xpath = get_xpath_by_multi_attribute('button', ['aria-label="Xuất bản"'])
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(5)
        else:
            print("Không tìm thấy nút xuất bản video !!!")
            self.is_stop_upload = True
            return

    def click_schedule_option(self):
        xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-video-visibility-select', attribute='id', attribute_value='second-container-expand-button')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
                
    def choose_date(self, date_string):
        current_day = convert_datetime_to_string(datetime.now())
        c_year, c_month, c_day = current_day.split('-')
        year, month, day = date_string.split('-')
        month_delta = int(month.strip()) - int(c_month.strip())
        day_delta = int(day.strip()) - int(c_day.strip())
        if month_delta < 0:
            month_delta = int(month.strip()) - (int(c_month.strip()) - 12)

        if month_delta > 0 and day_delta > 0:
            i = month_delta
        elif month_delta > 1 and day_delta <= 0:
            i = month_delta - 1
        else:
            i = 0
        kq = []
        xpath = get_xpath('ytcp-text-dropdown-trigger', 'style-scope ytcp-datetime-picker', 'id', 'datepicker-trigger')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(1)
            xpath = get_xpath('span', 'calendar-day   style-scope ytcp-scrollable-calendar style-scope ytcp-scrollable-calendar')
            date_elements = self.driver.find_elements(By.XPATH, xpath)
            j = 0
            for day_ele in date_elements:
                date = day_ele.text.strip()
                if not date:
                    continue
                if int(date) == int(day):
                    if j == i:
                        kq.append(day_ele)
                        break
                    else:
                        j += 1
            if len(kq) == 0:
                print(f"Không tìm thấy ngày {date_string}")
            else:
                day_ele = kq[0]
                day_ele.click()
                print(f"đã chọn ngày {year}-{month}-{date}")
                sleep(1)

    def click_today(self, click=True):
        xpath = get_xpath('span', 'calendar-day today  style-scope ytcp-scrollable-calendar style-scope ytcp-scrollable-calendar')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            if click:
                ele.click()
            self.is_selected_today = False
            sleep(0.5)
        else:
            xpath = get_xpath('span', 'calendar-day selected today  style-scope ytcp-scrollable-calendar style-scope ytcp-scrollable-calendar')
            ele = get_element_by_xpath(self.driver, xpath)
            if ele:
                if click:
                    ele.click()
                self.is_selected_today = True
                sleep(0.5)


    def click_next_month(self):
        if self.en_language:
            xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-date-picker', 'aria-label', 'Next month')
        else:
            xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-date-picker', 'aria-label', 'Tháng sau')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            for i in range(3):
                ele.click()
                sleep(1)
    def click_previous_month(self):
        if self.en_language:
            xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-date-picker', 'aria-label', 'Previous month')
        else:
            xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-date-picker', 'aria-label', 'Tháng trước')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            for i in range(2):
                ele.click()
                sleep(1)

    def choose_publish_time(self, publish_time):
        xpath = "//input[starts-with(@aria-labelledby, 'paper-input-label-')]"
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.clear()
            ele.send_keys(publish_time)
            sleep(1)
            
    def click_schedule_now(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Schedule')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Lên lịch')
        ele = get_element_by_xpath(self.driver, xpath)
        if ele:
            ele.click()
            sleep(5)

    def check_status_upload(self):
        xpath = get_xpath('span', 'progress-label style-scope ytcp-video-upload-progress')
        cnt = 0
        while True:
            try:
                ele = get_element_by_xpath(self.driver, xpath)
                status = ele.text
                if 'Đã tải được' in status:
                    sys.stdout.write(f'\r{status}')
                    sys.stdout.flush()
                    sleep(1)
                else:
                    print("\nĐã tải xong ...")
                    print(status)
                    return True
            except:
                getlog()
                cnt += 1
                if cnt > 1:
                    self.is_stop_upload = True
                    return False
                sleep(1)

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            print("Đã đóng trình duyệt.")

    def scroll_into_view(self, element, center=False):
        if center:
            self.driver.execute_script("arguments[0].scrollIntoView({ behavior: 'smooth', block: 'center' });", element)
        else:
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(0.2)

    def get_elements_by_xpath(self, xpath):
        eles = self.driver.find_elements(By.XPATH, xpath)
        return eles

#--------------------------------------Selenium--------------------------end

    def get_youtube_config(self):
        self.youtube_config = get_json_data(youtube_config_path)

    def save_youtube_config(self):
        save_to_pickle_file(self.youtube_config, youtube_config_path)

    def load_secret_info(self):
        try:
            if not os.path.exists(secret_path):
                return False
            self.secret_data = get_json_data(secret_path)
            self.secret_info={}
            gmails = [gmail for gmail in self.secret_data.keys()]
            if not gmails:
                print(f"Tài khoản {self.gmail} chưa được đăng ký API !!!")
                return False
            if self.gmail not in gmails:
                notification(self.root, f"Tài khoản {self.gmail} chưa được đăng ký API !!!")
                return False
            else:
                oauth = self.secret_data[self.gmail]['oauth']
                self.api_key = self.secret_data[self.gmail]['api']
                self.oauth_path = f'{current_dir}\\oauth\\{self.gmail}.json'
                save_to_pickle_file(oauth, self.oauth_path)
                return True
        except:
            getlog()
            return False

    def get_start_youtube(self):
        self.get_youtube_config()
        if not self.is_first_start:
            self.reset()
        else:
            self.is_first_start = False
        self.is_start_youtube = True
        self.show_window()
        self.setting_window_size()
        create_button(frame = self.root,text="Đăng video", command= self.open_upload_video_by_cookies_window)
        create_button(frame = self.root,text="Tải videos từ kênh", command=self.open_download_video_window)
        try:
            self.root.mainloop()
        except:
            getlog()



    def open_download_video_window(self):
        self.reset()
        self.is_download_window = True
        self.setting_window_size()
        self.show_window()

        def save_download_settings():
            download_folder = self.download_folder_var.get()
            download_channel_id = self.download_url_var.get()
            if not download_folder:
                notification(self.root, "hãy chọn thư mục lưu file tải về.")
                return False
            if not download_channel_id:
                notification(self.root, "hãy nhập link kênh hoặc Id kênh muốn tải.")
                return False
            self.youtube_config['download_folder'] = download_folder
            if 'http' in download_channel_id:
                self.download_by_selenium = True
            else:
                self.download_by_selenium = False
            self.youtube_config['download_url'] = download_channel_id.strip()
            self.youtube_config['filter_by_like'] = self.filter_by_like_var.get().strip()
            self.youtube_config['filter_by_views'] = self.filter_by_views_var.get().strip()
            self.save_youtube_config()
            return True

        def start_thread_download_from_channel():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                if save_download_settings():
                    if self.download_by_selenium:
                        self.download_thread = threading.Thread(target=self.download_videos_by_channel_id_selenium)
                    else:
                        if not self.youtube:
                            get_driver_with_profile(self.gmail, show=False)
                            self.youtube = self.get_authenticated_service()
                            if not self.youtube:
                                print(f"Xác thực với google không thành công. Hãy đảm bảo bạn đã đăng ký api trước đó.")
                                return
                        self.download_thread = threading.Thread(target=self.download_videos_by_channel_id_api)
                    self.download_thread.start()
                else:
                    return

        self.download_url_var = create_frame_label_and_input(self.root,label_text="Nhập link kênh", width=self.width, left=0.4, right=0.6)
        self.filter_by_views_var = self.create_settings_input("Lọc theo số lượt xem", "filter_by_views", is_data_in_template=False, values=["100000", "200000", "300000", "500000", "1000000"], left=0.4, right=0.6)
        self.filter_by_like_var = self.create_settings_input("Lọc theo số lượt thích(đăng ký API google)", "filter_by_like", is_data_in_template= False, values=["10000", "20000", "30000", "50000", "100000"], left=0.4, right=0.6)
        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu video", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        self.download_folder_var.insert(0, self.youtube_config['download_folder'])
        create_button(self.root, text="Bắt đầu tải video từ kênh", command=start_thread_download_from_channel, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_youtube, width=self.width)

    def choose_folder_to_save(self):
        download_folder = choose_folder()
        if download_folder:
            self.download_folder_var.delete(0, ctk.END)
            self.download_folder_var.insert(0, download_folder)
        
    def open_upload_video_by_cookies_window(self):
        self.open_upload_video_window()

    def open_upload_video_window(self):
        self.reset()
        self.is_upload_video_window = True
        self.setting_window_size()

        def set_upload_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.upload_folder_var.delete(0, ctk.END)
                self.upload_folder_var.insert(0, folder_path)
        def set_thumbnail_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.thumbnail_folder_var.delete(0, ctk.END)
                self.thumbnail_folder_var.insert(0, folder_path)

        def load_template():
            self.get_youtube_config()
            template_name = self.load_template_combobox.get()
            template = self.youtube_config['template'][template_name]

            self.title_var.delete(0, ctk.END)
            self.description_var.delete("1.0", ctk.END)
            self.upload_date_var.delete(0, ctk.END)
            self.publish_times_var.delete(0, ctk.END)
            self.upload_folder_var.delete(0, ctk.END)
            self.thumbnail_folder_var.delete(0, ctk.END)
            self.number_of_days_var.delete(0, ctk.END)
            self.day_gap_var.delete(0, ctk.END)

            self.title_var.insert(0, template.get("title", ""))
            self.is_title_plus_video_name_var.set(convert_boolean_to_Yes_No(self.youtube_config['template'][self.channel_name]['is_title_plus_video_name']))
            self.description_var.delete("1.0", ctk.END)
            self.description_var.insert(ctk.END, template.get("description", ""))
            self.upload_date_var.insert(0, template.get("upload_date", ""))
            self.publish_times_var.insert(0, template.get("publish_times", ""))
            try:
                self.playlist_var.set(template.get("curent_playlist", ""))
            except:
                self.playlist_var.delete(0, ctk.END)
                self.playlist_var.insert(0, template.get("curent_playlist", ""))
            self.altered_content_var.set(convert_boolean_to_Yes_No(template.get("altered_content", False)))
            self.upload_folder_var.insert(0, template.get("upload_folder", ""))
            self.thumbnail_folder_var.insert(0, template.get("thumbnail_folder", ""))
            self.is_delete_after_upload_var.set(convert_boolean_to_Yes_No(self.youtube_config['template'][self.channel_name]['is_delete_after_upload']))
            self.number_of_days_var.insert(0, template.get("number_of_days", "1"))
            self.day_gap_var.insert(0, template.get("day_gap", "1"))

        self.title_var = self.create_settings_input("Tiêu đề", "title", left=left, right=right)
        self.is_title_plus_video_name_var = self.create_settings_input("Thêm tên video vào tiêu đề", "is_title_plus_video_name", values=["Yes", "No"], left=left, right=right)
        self.description_var = self.create_settings_input("Mô tả", "description", is_textbox=True, left=left, right=right)
        self.upload_date_var = self.create_settings_input("Ngày bắt đầu đăng video (yyyy-mm-dd)", "upload_date", left=left, right=right)
        self.day_gap_var, self.number_of_days_var = create_frame_label_input_input(self.root,label_text="Số ngày đăng/Khoảng cách ngày đăng", width=self.width, left=left, mid=0.33, right=0.37)
        self.number_of_days_var.insert(0, self.youtube_config['template'][self.channel_name]['number_of_days'])
        self.day_gap_var.insert(0, self.youtube_config['template'][self.channel_name]['day_gap'])
        self.publish_times_var = self.create_settings_input("Giờ đăng(vd: 20:30)", "publish_times", left=left, right=right)
        self.altered_content_var = self.create_settings_input(label_text="Nội dung đã bị chỉnh sửa", config_key="altered_content", values=['Yes', 'No'], left=0.3, right=0.7)
        self.playlist_var = self.create_settings_input("Chọn Playlist", "curent_playlist", values=self.youtube_config['template'][self.channel_name]["playlist"], left=left, right=right)
        try:
            self.playlist_var.set(self.youtube_config['template'][self.channel_name]["curent_playlist"])
        except:
            self.playlist_var.insert(0, self.youtube_config['template'][self.channel_name]["curent_playlist"])
        self.show_browser_var = self.create_settings_input(label_text="Hiển thị trình duyệt", config_key="show_browser", values=['Yes', 'No'], left=0.3, right=0.7, is_data_in_template=False)
        self.is_delete_after_upload_var = self.create_settings_input("Xóa video sau khi đăng", "is_delete_after_upload", values=["Yes", "No"], left=left, right=right)
        self.cookies_var = create_frame_label_and_input(self.root, label_text="Đăng nhập bằng cookies", width=self.width, left=left, right=right)
        self.thumbnail_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa thumbnail", command=set_thumbnail_folder, width=self.width)
        self.thumbnail_folder_var.insert(0, self.youtube_config['template'][self.channel_name]['thumbnail_folder'])
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa video", command=set_upload_folder, width=self.width)
        self.upload_folder_var.insert(0, self.youtube_config['template'][self.channel_name]['upload_folder'])
        self.load_template_combobox = create_frame_button_and_combobox(self.root,text="Tải mẫu có sẵn", width=self.width, command=load_template, values=list(self.youtube_config['template'].keys()))
        self.load_template_combobox.set(self.channel_name)
        create_frame_button_and_button(self.root,text1="Đăng video ngay", width=self.width, command1=self.start_upload_videos_now, text2="Lên lịch đăng video", command2=self.start_upload_videos_with_schedule, left=0.5, right=0.5)
        create_button(self.root, text="Lùi lại", command=self.get_start_youtube, width=self.width)
        self.show_window()

    def save_upload_setting(self):
        try:
            self.youtube_config['template'][self.channel_name]["title"] = self.title_var.get()
            self.youtube_config['template'][self.channel_name]["is_title_plus_video_name"] = self.is_title_plus_video_name_var.get() == "Yes"
            self.youtube_config['template'][self.channel_name]["description"] = self.description_var.get("1.0", ctk.END).strip()
            playlist_name = self.playlist_var.get()
            self.youtube_config['template'][self.channel_name]["curent_playlist"] = playlist_name
            if playlist_name not in self.youtube_config['template'][self.channel_name]["playlist"]:
                self.youtube_config['template'][self.channel_name]["playlist"].append(playlist_name)
            self.youtube_config['template'][self.channel_name]['altered_content'] = self.altered_content_var.get() == 'Yes'
            self.youtube_config['show_browser'] = self.show_browser_var.get() == 'Yes'
            self.youtube_config['template'][self.channel_name]["upload_date"] = self.upload_date_var.get()
            self.youtube_config['template'][self.channel_name]["number_of_days"] = self.number_of_days_var.get()
            self.youtube_config['template'][self.channel_name]["day_gap"] = self.day_gap_var.get()
            self.youtube_config['template'][self.channel_name]["publish_times"] = self.publish_times_var.get()
            self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = 0
            self.youtube_config['template'][self.channel_name]["thumbnail_folder"] = self.thumbnail_folder_var.get()
            self.youtube_config['template'][self.channel_name]["upload_folder"] = self.upload_folder_var.get()
            self.youtube_config['template'][self.channel_name]['gmail'] = self.gmail
            self.youtube_config['template'][self.channel_name]['is_delete_after_upload'] = self.is_delete_after_upload_var.get() == 'Yes'
            self.save_youtube_config()
            validate_message = ""
            if len(self.youtube_config['template'][self.channel_name]["title"]) > 100:
                validate_message += "Tiêu đề có tối đa 100 ký tự.\n"
            if len(self.youtube_config['template'][self.channel_name]["description"]) > 5000:
                validate_message += "Mô tả có tối đa 5000 ký tự.\n"
            if not self.youtube_config['template'][self.channel_name]["upload_folder"]:
                validate_message += "Chưa chọn thư mục chứa video.\n"
            if validate_message:
                notification(self.root, validate_message)
                return False
            
            self.is_upload_video_window = False
            return True
        except:
            getlog()
            return False

    def start_upload_videos_now(self):
        self.is_schedule = False
        if self.save_upload_setting():
            self.start_thread_upload_video()

    def start_upload_videos_with_schedule(self):
        self.is_schedule = True
        if self.save_upload_setting():
            self.start_thread_upload_video()
            
    def start_thread_upload_video(self):
        if not self.upload_thread or not self.upload_thread.is_alive():
            self.is_stop_upload = False
            thread_upload = threading.Thread(target=self.run_thread_upload_video)
            thread_upload.start()

    def run_thread_upload_video(self):
        cookies = self.cookies_var.get().strip()
        if cookies:
            cookie_data = json.loads(cookies)
            youtube_cookies = get_pickle_data(youtube_cookies_path)
            if not youtube_cookies:
                youtube_cookies = {}
            youtube_cookies[self.gmail] = cookie_data
            save_to_pickle_file(youtube_cookies, youtube_cookies_path)
        self.schedule_videos_by_selenium()

    def open_dowload_video_from_channel_window(self):
        create_text_input(self.root)

    def get_authenticated_service(self):
        try:
            if self.load_secret_info():
                if not self.oauth_path:
                    notification(self.root, f"Tài khoản gmail {self.gmail} chưa được đăng ký hoặc đã hết hạn.")
                    return
                try:
                    flow = flow_from_clientsecrets(self.oauth_path, scope=SCOPES, message="xác minh thất bại")
                    self.curent_oath_path = f"{sys.argv[0]}-{self.gmail}-{self.channel_name}.json"
                    storage = Storage(self.curent_oath_path)
                    credentials = storage.get()
                except:
                    getlog()
                    credentials = None
                if credentials is None or credentials.invalid:
                    credentials = run_flow(flow, storage, None)
                return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
            else:
                return None
        except Exception as e:
            error_message(f"Xác minh thất bại. Hãy đảm bảo bạn đang dùng gmail {self.gmail} để xác minh !!!")
            getlog()
            return None
        
    def check_status_videos_by_selenium(self):
        try:
            def get_studio():
                self.driver.get('https://studio.youtube.com/')
                sleep(2)
                if self.en_language:
                    ele = get_element_by_text(self.driver, 'Content', 'div')
                else:
                    ele = get_element_by_text(self.driver, 'Nội dung', 'div')
                if ele:
                    ele.click()
                else:
                    xpath = get_xpath_by_multi_attribute('tp-yt-paper-icon-item', ['id="menu-paper-icon-item-1"'])
                    ele = get_element_by_xpath(self.driver, xpath)
                    if ele:
                        ele.click()
                sleep(2)

            def click_more_action_and_delete():
                def click_delete_video():
                    ele = get_element_by_text(self.driver, 'Xóa vĩnh viễn', 'yt-formatted-string')
                    if ele:
                        ele.click()
                ele = get_element_by_text(self.driver, 'Thao tác khác', tag_name='span')
                if ele:
                    ele.click()
                    click_delete_video()
                    sleep(0.5)
                    press_TAB_key(self.driver)
                    sleep(1)
                    press_ENTER_key(self.driver)
                    sleep(1)
                    press_TAB_key(self.driver, 2)
                    press_ENTER_key(self.driver)
                    sleep(60)
                    
            def click_short_tag():
                short_tag = get_element_by_text(self.driver, 'Shorts', tag_name='span')
                if short_tag:
                    short_tag.click()
                    sleep(3)

            def get_all_video_in_one_page():
                xpath = get_xpath_by_multi_attribute('div', ['id="row-container"'])
                self.scroll_page()
                eles = get_element_by_xpath(self.driver, xpath, multiple_ele=True)
                next_ele = None
                if eles and len(eles) >= 30:
                    next_xpath = get_xpath_by_multi_attribute('ytcp-icon-button', ['id="navigate-after"', 'tabindex="0"'])
                    next_ele = get_element_by_xpath(self.driver, next_xpath)
                return eles, next_ele
            
            if not self.login(True):
                return
            get_studio()
            check_short_video = False
            while True:
                div_videos, next_ele = get_all_video_in_one_page()
                if div_videos and len(div_videos) > 0:
                    self.cnt_delete_video = 0
                    for div_video in div_videos:
                        texts = div_video.text.split('\n')
                        if 'Không có' not in texts and 'None' not in texts or 'Bản quyền' in texts:
                            checkbox_element = div_video.find_element(By.XPATH, './/div[contains(@class, "ytcp-checkbox-lit")]')
                            if checkbox_element:
                                self.scroll_into_view(div_video, center=True)
                                sleep(0.5)
                                checkbox_element.click()
                                self.cnt_delete_video += 1
                    if self.cnt_delete_video > 0:
                        click_more_action_and_delete()
                    if next_ele:
                        next_ele.click()
                        sleep(3)
                    else:
                        if check_short_video:
                            break
                        click_short_tag()
                        check_short_video = True
        except:
            getlog()
            print("Có lỗi trong quá trình check bản quyền video !!!")
        finally:
            self.close_driver()


    def schedule_videos_by_selenium(self, folder=None):
        try:
            thumbnail_folder = self.youtube_config['template'][self.channel_name]['thumbnail_folder']
            if folder:
                videos_folder = folder
            else:
                videos_folder = self.youtube_config['template'][self.channel_name]['upload_folder']
            if not check_folder(videos_folder):
                return False
            videos = get_file_in_folder_by_type(videos_folder, ".mp4")   
            if not videos:
                return False
            if 'cnt_upload_in_day' not in self.youtube_config['template'][self.channel_name]:
                self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = 0
            current_day = convert_datetime_to_string(datetime.now().date())
            tomorow_str = convert_datetime_to_string(datetime.now() + timedelta(days=1))
            number_of_days = get_number_of_days(self.youtube_config['template'][self.channel_name]['number_of_days'])
            if self.is_schedule:
                day_gap = get_day_gap(self.youtube_config['template'][self.channel_name]['day_gap'])
                old_upload_date_str = self.youtube_config['template'][self.channel_name]['upload_date']
                if not old_upload_date_str:
                    return False
                publish_times = self.youtube_config['template'][self.channel_name]['publish_times'].split(',')
                if not publish_times:
                    return False
                upload_date = get_upload_date(old_upload_date_str)
                upload_date_str = convert_datetime_to_string(upload_date)
                if upload_date_str != old_upload_date_str:
                    self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = 0
                if self.is_auto_upload:
                    number_of_days = 100
                    if self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] == 0 or self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] >= len(publish_times):
                        upload_date_str = add_date_into_string(upload_date_str, day_gap)
                        self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = 0
                    self.youtube_config['show_browser'] = False
                    if folder:
                        self.youtube_config['show_browser'] = True
            else:
                upload_date_str = current_day
            if not self.login(self.youtube_config['show_browser']):
                print(f'Đăng nhập thất bại !!!')
                return False
            else:
                print(f'Đăng nhập thành công !!!')

            upload_count = 0
            date_cnt = 0
            for i, video_file in enumerate(videos):
                day_delta = 60
                if is_date_greater_than_current_day(upload_date_str, day_delta):
                    print(f"Ngày đăng {upload_date_str} vượt quá {day_delta} ngày so với ngày hiện tại. Không thể tiếp tục đăng video.")
                    break
                if self.is_schedule:
                    cnt_upload_in_day = self.youtube_config['template'][self.channel_name]['cnt_upload_in_day']
                    while True:
                        publish_time = publish_times[cnt_upload_in_day % len(publish_times)].strip()
                        publish_time = get_pushlish_time_hh_mm(publish_time)
                        if not check_datetime_input(upload_date_str, publish_time):
                            cnt_upload_in_day += 1
                            if cnt_upload_in_day % len(publish_times) == 0:
                                upload_date_str = add_date_into_string(upload_date_str, day_gap)
                                self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = 0
                        else:
                            break
                if self.is_stop_upload:
                    break
                video_name = os.path.splitext(video_file)[0]
                title = self.youtube_config['template'][self.channel_name]['title']
                if self.youtube_config['template'][self.channel_name]['is_title_plus_video_name']:
                    full_title = f"{title} {video_name}"
                else:
                    full_title = title
                if len(full_title) > 100:
                    if not self.is_auto_upload:
                        print(f"Chiều dài tối đa của tiêu đề là 100 ký tự:\n{full_title}: có tổng {len(full_title)} ký tự")
                    continue
                video_path = os.path.join(videos_folder, video_file)
                print(f'--> Bắt đầu đăng video: {video_file}')
                if upload_count > 0:
                    self.driver.get("https://www.youtube.com/")
                    sleep(4)
                self.click_upload_button()
                self.send_video_to_youtube(video_path)
                if self.is_stop_upload:
                    break
                if full_title:
                    self.input_title(title=full_title)
                if self.youtube_config['template'][self.channel_name]['description']:
                    self.input_description(description=self.youtube_config['template'][self.channel_name]['description'])
                self.check_daily_update_limit()
                if self.is_stop_upload:
                    break
                thumnail_path = os.path.join(thumbnail_folder, f'{video_name}.png')
                if os.path.exists(thumnail_path):
                    self.input_thumbnail(thumbnail_path=thumnail_path)
                if self.youtube_config['template'][self.channel_name]['curent_playlist']:
                    self.choose_playlist(self.youtube_config['template'][self.channel_name]['curent_playlist'])
                    
                self.click_not_make_for_kid()
                if self.is_stop_upload:
                    break
                self.click_show_more()
                self.click_altered_content(self.youtube_config['template'][self.channel_name]['altered_content'])
                self.click_next_button()
                if self.is_schedule:
                    self.click_schedule_option()
                    if not upload_date_str == tomorow_str:
                        self.choose_date(upload_date_str)
                    self.choose_publish_time(publish_time)
                    if self.is_stop_upload:
                        break
                    self.check_status_upload()
                    if self.is_stop_upload:
                        break
                    self.click_schedule_now()
                    upload_count += 1
                    cnt_upload_in_day += 1
                    self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = cnt_upload_in_day
                    if self.youtube_config['template'][self.channel_name]['upload_date'] != upload_date_str:
                        self.youtube_config['template'][self.channel_name]['upload_date'] = upload_date_str
                    remove_or_move_file(video_path, self.youtube_config['template'][self.channel_name]['is_delete_after_upload'], finish_folder_name='youtube_upload_finished')
                    print(f'--> Đăng thành công video: {video_file}')
                    if (cnt_upload_in_day) % len(publish_times) == 0:
                        upload_date_str = add_date_into_string(upload_date_str, day_gap)
                        date_cnt += 1
                        self.youtube_config['template'][self.channel_name]['cnt_upload_in_day'] = 0
                    self.save_youtube_config()
                    if date_cnt == number_of_days:
                        break
                else:
                    self.click_public_radio()
                    if self.is_stop_upload:
                        break
                    self.click_public_now()
                    if self.youtube_config['template'][self.channel_name]['upload_date'] != upload_date_str:
                        self.youtube_config['template'][self.channel_name]['upload_date'] = upload_date_str
                        self.save_youtube_config()
                    upload_count += 1
                    remove_or_move_file(video_path, self.youtube_config['template'][self.channel_name]['is_delete_after_upload'], finish_folder_name='youtube_upload_finished')
                    print(f'--> Đăng thành công video: {video_file}')
                    if upload_count == number_of_days:
                        break
            if upload_count > 0:
                if not self.is_auto_upload:
                    notification(self.root, f"Đăng thành công {upload_count} video")
                else:
                    print(f"Đăng thành công {upload_count} video")
                return True
            return False
        except:
            getlog()
            return False
        finally:
            self.close_driver()

    def delete_video(self, video_id):
        request = self.youtube.videos().delete(id=video_id)
        response = request.execute()
        print(f"delete video {video_id} info: {response}")
        return response

    def get_video_ids_by_channel_id(self, mine=False):
        try:
            if mine:
                response = self.youtube.channels().list(part="contentDetails", maxResults=50, mine=True).execute()
            else:
                response = self.youtube.channels().list(part="contentDetails", id=self.youtube_config['download_url']).execute()
            if "items" not in response or len(response["items"]) == 0:
                raise Exception("No items found in channel details response.")
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            self.video_info = {}
            video_ids = []
            next_page_token = None
            while True:
                playlist_response = self.youtube.playlistItems().list(
                    part="snippet,contentDetails,status",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                for item in playlist_response["items"]:
                    if item['status']['privacyStatus'] == 'private':
                        continue
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    if video_id == 'KL69Lqiwc3Q':
                        print(video_id)
                    self.video_info[video_id]={}
                    self.video_info[video_id]["title"] = item["snippet"]["title"]
                    self.video_info[video_id]["status"] = item['status']
                    self.video_info[video_id]["contentDetails"] = item['contentDetails']
                    video_ids.append(video_id)
                next_page_token = playlist_response.get("nextPageToken")

                if not next_page_token:
                    break
            return video_ids
        except Exception as e:
            getlog()
            remove_file(self.curent_oath_path)
        return []
    
    def get_video_details(self, video_ids, check_status=False):
        if not video_ids:
            print("Không tìm thấy video nào.")
        chunk_size = 50 
        for i in range(0, len(video_ids), chunk_size):
            chunk_video_ids = video_ids[i:i+chunk_size]
            video_ids_str = ','.join(chunk_video_ids)
            url_videos = f'https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet,status,contentDetails&id={video_ids_str}&key={self.api_key}'
            response_videos = requests.get(url_videos)
            videos_info = response_videos.json()
            self.list_videos_detail.append(videos_info)

            if check_status: #kiểm tra các video trong channel của mình
                if len(chunk_video_ids) == len(videos_info['items']):
                    continue
                ok_ids = [item['id'] for item in videos_info['items']]
                for id in chunk_video_ids:
                    if id not in ok_ids:
                        self.list_video_ids_delete.append(id)
                
                for item in videos_info['items']:
                    content_details = item.get('contentDetails', {})
                    if 'contentRating' in content_details and 'youtubereportabuse' in content_details['contentRating']:
                        self.list_video_ids_delete.append(item['id'])
                    
    def download_videos_by_channel_id_selenium(self):
        try:
            self.download_info = load_download_info()
            video_urls = []
            def get_views_from_video(div_content, short=True):
                try:
                    if short:
                        view_div = div_content.find_element(By.XPATH, ".//div[contains(@aria-label, 'views')]")
                        views_text = view_div.get_attribute("aria-label").split(' ')[0].strip()
                    else:
                        view_div = div_content.find_element(By.XPATH, ".//span[contains(text(), 'views')]")
                        views_text = view_div.text.split(' ')[0].strip()
                    view_count = get_view_count(views_text)
                    return view_count
                except:
                    return 0
            def get_videos(view_cnt="", short=True):
                try:
                    view_cnt = int(view_cnt)
                except:
                    view_cnt = 0
                def get_link_video(div_content):
                    if short:
                        link_video = get_element_by_xpath(div_content, './/a[contains(@href, "/shorts")]')
                    else:
                        link_video = get_element_by_xpath(div_content, './/a[contains(@href, "/watch?")]')
                    if link_video:
                        url = link_video.get_attribute('href')
                        if url and url not in video_urls:
                            if url in self.download_info['downloaded_urls']:
                                print(f"video {url} đã tải trước đó ...")
                            else:
                                video_urls.append(url)
                    
                xpath = get_xpath_by_multi_attribute('div', ['id="content"'])
                div_contents = get_element_by_xpath(self.driver, xpath, multiple_ele=True)
                if div_contents:
                    for div_content in div_contents:
                        view_count = get_views_from_video(div_content, short)
                        if view_count >= view_cnt:
                            get_link_video(div_content)

            download_folder = self.youtube_config['download_folder']
            self.driver = get_driver(show=False)
            channel_url = self.youtube_config['download_url']
            filter_by_views = self.youtube_config['filter_by_views']
            
            self.driver.get(channel_url)
            t=time()
            if channel_url.endswith('/videos'):
                print(f"Bắt đầu tìm video dài trong kênh {channel_url} ...")
                sleep(3)
                self.scroll_page()
                get_videos(filter_by_views, short=False)
            elif channel_url.endswith('/shorts'):
                print(f"Bắt đầu tìm video ngắn trong kênh {channel_url} ...")
                sleep(3)
                self.scroll_page()
                get_videos(filter_by_views, short=True)
            else:
                print(f"Bắt đầu tìm video trong kênh {channel_url} ...")
                short_video_url = f'{channel_url}/shorts'
                self.driver.get(short_video_url)
                self.scroll_page()
                get_videos(filter_by_views, short=True)
                long_video_url = f'{channel_url}/videos'
                self.driver.get(long_video_url)
                self.scroll_page()
                get_videos(filter_by_views, short=False)
            self.close_driver()
            print(f"--> Tổng thời gian tìm video là {int((time() - t)/60)} phút {int(time() - t)%60} giây")
            if len(video_urls) > 0:
                print(f"--> Tổng số video tìm được là {len(video_urls)}. Bắt đầu quá trình tải video ...")
            else:
                print("Không tìm thấy video nào phù hợp.")
                return
            cnt_download = 0
            
            for url in video_urls.copy():
                try:
                    if self.is_stop_download:
                        break
                    if download_video_by_url(url, download_folder=download_folder, video_urls=video_urls.copy()):
                        print(f"--> Tải thành công video: {url}")
                        cnt_download += 1
                        video_urls.remove(url)
                        if url not in self.download_info['downloaded_urls']:
                            self.download_info['downloaded_urls'].append(url)
                        save_download_info(self.download_info)
                except:
                    getlog()
                    print(f"Tải không thành công {url}")
            
            if cnt_download > 0:
                notification(self.root, f"Đã tải thành công {cnt_download} video.")
            else:
                download_video_by_bravedown(video_urls, download_folder)
        except:
            getlog()
        finally:
            self.close_driver()
            

    def scroll_page(self):      
        last_height = self.driver.execute_script("return document.documentElement.scrollHeight")
        k = 0
        cnt_search = 0
        sleep(1)
        while True:
            if self.is_stop_download:
                self.close_driver()
                return None
            self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
            sleep(2)
            new_height = self.driver.execute_script("return document.documentElement.scrollHeight")
            if new_height == last_height:
                if k < 2:
                    k += 1
                    self.driver.execute_script("window.scrollBy(0, -400);")
                    sleep(0.5)
                    self.driver.execute_script("window.scrollTo(0, document.documentElement.scrollHeight);")
                    sleep(2)
                else:
                    break
            else:
                k = 0
            last_height = new_height
            cnt_search += 1
            sys.stdout.write(f'\rCuộn trang lần thứ {cnt_search} ...')
            sys.stdout.flush()
            if cnt_search > 200:
                break

    def download_videos_by_channel_id_api(self):
        self.youtube_config['download_folder'] = self.download_folder_var.get()
        self.list_videos_download_from_channel = []
        video_ids = self.get_video_ids_by_channel_id()
        self.get_video_details(video_ids)
        if len(self.list_videos_detail) > 0:
            print(f'Đã tìm thấy {len(self.list_videos_detail)} video. Bắt đầu lọc và tải xuống')
            self.get_download_info()

            for videos_detail in self.list_videos_detail:
                self.check_videos_and_dowload(videos_detail)
            cnt = len(self.list_videos_download_from_channel)
            if cnt == 0:
                notification(self.root, "Tải không thành công. Có thể điều kiện số lượt xem và thích không thỏa mãn!")
            else:
                notification(self.root, f"Tải thành công {cnt} video")

    def check_videos_and_dowload(self, video_details):
        for video in video_details['items']:
            statistics = video['statistics']
            like_count = int(statistics.get('likeCount', 0))
            view_count = int(statistics.get('viewCount', 0))
            if like_count > int(self.youtube_config['filter_by_like']) and view_count > int(self.youtube_config['filter_by_views']):
                video_id = video['id']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                if video_url in self.download_info['downloaded_urls']:
                    print(f"video này đã tải trước đây rồi: {video_url}")
                    continue
                print(f"bắt đầu tải video: {video_url} với {like_count} lượt thích và {view_count} lượt xem")
                self.download_video_youtube_by_url(video_url)

    def get_download_info(self):
        self.download_info = get_json_data(download_info_path)
        if not self.download_info:
            self.download_info = {}
        if 'downloaded_urls' not in self.download_info:
            self.download_info['downloaded_urls'] = []
    def download_video_youtube_by_url(self, video_url):
        try:
            self.get_download_info()
            if download_video_by_url(video_url, self.youtube_config['download_folder']):
                self.list_videos_download_from_channel.append(video_url)
                if video_url not in self.download_info['downloaded_urls']:
                    self.download_info['downloaded_urls'].append(video_url)
                save_to_pickle_file(self.download_info, download_info_path)
        except:
            sleep(1)


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
        if self.is_start_youtube:
            self.root.title(f"Youtube: {self.gmail}: {self.channel_name}")
            self.width = 500
            self.height_window = 170
            self.is_start_youtube = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video Youtube: {self.channel_name}")
            self.width = 800
            self.height_window = 893
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos Youtube")
            self.width = 600
            self.height_window = 363
            self.is_download_window = False
        self.setting_screen_position()

    def exit_app(self):
        self.reset()
        self.root.destroy()

    def on_close(self):
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
        self.is_youtube_window = False
        self.clear_after_action()
        clear_widgets(self.root)

    def clear_after_action(self):
        self.root.withdraw()

    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.5, right=0.5, is_data_in_template=True):
        if is_data_in_template:
            config = config=self.youtube_config['template'][self.channel_name]
        else:
            config = self.youtube_config
        frame = create_frame(self.root)
        create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')
        val = config[config_key]
        if values:
            if not config_key:
                val = ""
            elif config_key not in config:
                val = ""
            else:
                if config[config_key] == True:
                    val = "Yes"
                elif config[config_key] == False:
                    val = "No"

            combobox = ctk.CTkComboBox(frame, values=values, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            combobox.set(val)
            setattr(self, f"{config_key}_var", val)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=90, width=self.width*right)
            textbox.insert("1.0", val)
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, val)
            setattr(self, f"{config_key}_var", val)
            return entry
