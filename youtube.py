import requests
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from common_function import *
from common_function_CTK import *
from Common import *
from oauth2client.client import OAuth2WebServerFlow
import keyboard

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#-----------------------------------------------------------------------------------------------------------------
class YouTubeManager():
    def __init__(self, gmail, channel_name=None, is_auto_upload=False, lock=None, download_thread=None, upload_thread=None):
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
        self.youtube = self.get_authenticated_service()
        if not self.youtube:
            return
        self.pre_time_check_status = 0

        self.list_waiting_dowload_videos = []
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
        self.is_use_cookies = False
        

#--------------------------------------Selenium--------------------------start

    def login(self):
        try:
            self.driver = get_driver(show=self.youtube_config['show_browser'])
            self.load_session()
            account_menu, language = self.get_account_menu()
            if account_menu:
                if language == 'en':
                    self.en_language = True
                else:
                    self.en_language = False
                account_menu.click()
                sleep(1)
                self.click_switch_account()
                return True
            else:
                return False
        except:
            getlog()
            return False

    def load_session(self, url="https://www.youtube.com/"):
        self.driver.get(url)
        sleep(1)  # Ensure the page is fully loaded before adding cookies
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
            sleep(2)
            self.driver.refresh()
            sleep(2)
        except:
            getlog()

    def click_switch_account(self):
        xpath = get_xpath('yt-formatted-string', 'style-scope ytd-compact-link-renderer')
        if self.en_language:
            ele = self.get_element_by_xpath(xpath, 'Switch account')
        else:
            ele = self.get_element_by_xpath(xpath, 'Chuyển đổi tài khoản')
        if ele:
            ele.click()
            sleep(0.5)
            self.choose_channel()

    def choose_channel(self):
        xpath= get_xpath('yt-formatted-string', 'style-scope ytd-account-item-renderer')
        ele = self.get_element_by_xpath(xpath, self.channel_name)
        if ele:
            ele.click()
            sleep(1)

    def get_account_menu(self):
        xpath = get_xpath('button', 'style-scope ytd-topbar-menu-button-renderer', attribute='aria-label', attribute_value='Account menu')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            return ele, 'en'
        else:
            xpath = get_xpath('button', 'style-scope ytd-topbar-menu-button-renderer', attribute='aria-label', attribute_value='Trình đơn tài khoản')
            ele = self.get_element_by_xpath(xpath)
            if ele:
                return ele, 'vi'
            else:
                return None, None
            
    def click_upload_video_button(self):
        xpath = get_xpath('yt-formatted-string', 'style-scope ytd-compact-link-renderer')
        if self.en_language:
            ele = self.get_element_by_xpath(xpath, 'Upload video')
        else:
            ele = self.get_element_by_xpath(xpath, 'Tải video lên')
        if ele:
            ele.click()
            sleep(2)

    def click_upload_button(self):
        if self.en_language:
            xpath = get_xpath('button', 'style-scope yt-icon-button', attribute='aria-label', attribute_value='Create')
        else:
            xpath = get_xpath('button', 'style-scope yt-icon-button', attribute='aria-label', attribute_value='Tạo')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
            sleep(0.5)
            self.click_upload_video_button()

    def click_upload_button_again(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--outline ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m ytcp-button-shape-impl--icon-leading', attribute='aria-label', attribute_value='Create')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--outline ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m ytcp-button-shape-impl--icon-leading', attribute='aria-label', attribute_value='Tạo')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
            sleep(0.4)
            self.click_upload_video_button_again()
    
    def click_upload_video_button_again(self):
        xpath = get_xpath('yt-formatted-string', 'item-text main-text style-scope ytcp-text-menu')
        if self.en_language:
            ele = self.get_element_by_xpath(xpath, 'Upload video')
        else:
            ele = self.get_element_by_xpath(xpath, 'Tải video lên')
        if ele:
            ele.click()
            sleep(1)
    
    def send_video_to_youtube(self, video_path):
        xpath = get_xpath_by_multi_attribute('input', ['type="file"', 'name="Filedata"'])
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.send_keys(video_path)
            sleep(2)

    def input_title(self, title):
        if self.en_language:
            xpath = get_xpath('div', 'style-scope ytcp-social-suggestions-textbox', attribute='aria-label', attribute_value='Add a title that describes your video (type @ to mention a channel)')
        else:
            xpath = get_xpath('div', 'style-scope ytcp-social-suggestions-textbox', attribute='aria-label', attribute_value='Thêm tiêu đề để mô tả video của bạn (nhập ký tự @ để đề cập tên một kênh)')
        cnt = 0
        while True:
            ele = self.get_element_by_xpath(xpath)
            if ele:
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
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.clear()
            ele.send_keys(description)
            sleep(1)

    def input_thumbnail(self, thumbnail_path):
        xpath = get_xpath('input', 'style-scope ytcp-thumbnail-uploader', attribute='accept', attribute_value='image/jpeg,image/png')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.send_keys(thumbnail_path)
            sleep(1)

    def choose_playlist(self, playlist_name):
        def click_done():
            if self.en_language:
                xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Done')
            else:
                xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Xong')
            ele = self.get_element_by_xpath(xpath)
            if ele:
                ele.click()
                sleep(0.5)
        xpath = get_xpath('ytcp-text-dropdown-trigger', 'dropdown style-scope ytcp-video-metadata-playlists')
        dropdown = self.get_element_by_xpath(xpath)
        if dropdown:
            self.scroll_into_view(dropdown)
            dropdown.click()
            sleep(1)
            xpath = get_xpath('span', 'checkbox-label style-scope ytcp-checkbox-group')
            ele = self.get_element_by_xpath(xpath, playlist_name)
            if ele:
                ele.click()
                sleep(1)
            click_done()

    def click_show_more(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Show more')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Hiện thêm')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            self.scroll_into_view(ele)
            ele.click()
            sleep(1)

    def click_altered_content(self):
        xpath = get_xpath('tp-yt-paper-radio-button', 'style-scope ytkp-altered-content-select', 'name', 'VIDEO_HAS_ALTERED_CONTENT_YES')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            self.scroll_into_view(ele)
            ele.click()
            sleep(0.5)

    def click_next_button(self):
        cnt = 0
        while True:
            try:
                if self.en_language:
                    xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Next')
                else:
                    xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Tiếp')
                ele = self.get_element_by_xpath(xpath)
                if ele:
                    self.scroll_into_view(ele)
                    sleep(1)
                    ele.click()
                    sleep(1)
                    ele.click()
                    sleep(1)
                    ele.click()
                    break
                else:
                    cnt += 1
                    sleep(2)
            except:
                cnt += 1
                sleep(2)
            if cnt > 3:
                break
    
    def click_public_radio(self):
        xpath = get_xpath('tp-yt-paper-radio-button', 'style-scope ytcp-video-visibility-select iron-selected', attribute='name', attribute_value='PUBLIC')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
            sleep(1)

    def click_public_now(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', attribute='aria-label', attribute_value='Publish')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', attribute='aria-label', attribute_value='Xuất bản')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
            sleep(5)

    def click_schedule_option(self):
        xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-video-visibility-select', attribute='id', attribute_value='second-container-expand-button')
        ele = self.get_element_by_xpath(xpath)
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
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
            sleep(1)
            # self.click_next_month()
            # self.click_previous_month()
            #tìm ngày
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
        ele = self.get_element_by_xpath(xpath)
        if ele:
            if click:
                ele.click()
            self.is_selected_today = False
            sleep(0.5)
        else:
            xpath = get_xpath('span', 'calendar-day selected today  style-scope ytcp-scrollable-calendar style-scope ytcp-scrollable-calendar')
            ele = self.get_element_by_xpath(xpath)
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
        ele = self.get_element_by_xpath(xpath)
        if ele:
            for i in range(2):
                ele.click()
                sleep(1)
    def click_previous_month(self):
        if self.en_language:
            xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-date-picker', 'aria-label', 'Previous month')
        else:
            xpath = get_xpath('ytcp-icon-button', 'style-scope ytcp-date-picker', 'aria-label', 'Tháng trước')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            for i in range(2):
                ele.click()
                sleep(1)

    def choose_publish_time(self, publish_time):
        xpath = "//input[starts-with(@aria-labelledby, 'paper-input-label-')]"
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.clear()
            ele.send_keys(publish_time)
            sleep(1)
            
    def click_schedule_now(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Schedule')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--filled ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Lên lịch')
        ele = self.get_element_by_xpath(xpath)
        if ele:
            ele.click()
            sleep(5)

    def click_close_button(self):
        if self.en_language:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Close')
        else:
            xpath = get_xpath('button', 'ytcp-button-shape-impl ytcp-button-shape-impl--tonal ytcp-button-shape-impl--mono ytcp-button-shape-impl--size-m', 'aria-label', 'Đóng')
        elements = self.get_elements_by_xpath(xpath)
        if elements:
            for ele in elements:
                try:
                    ele.click()
                    break
                except:
                    pass

    def close_driver(self):
        if self.driver:
            self.driver.quit()
            print("Đã đóng trình duyệt.")

    def scroll_into_view(self, element):
        self.driver.execute_script("arguments[0].scrollIntoView(true);", element)
        sleep(0.1)  # Đợi một chút để trình duyệt hoàn thành cuộn

    def get_element_by_xpath(self, xpath, key=None):
        kq = []
        cnt=0
        while(len(kq)==0):
            cnt+=1
            elements = self.get_elements_by_xpath(xpath)
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
            if cnt > 5:
                print(f"Không tìm thấy: {key}: {xpath}")
                break

    def get_elements_by_xpath(self, xpath):
        eles = self.driver.find_elements(By.XPATH, xpath)
        return eles




#--------------------------------------Selenium--------------------------end




    def get_youtube_config(self):
        self.youtube_config = get_json_data(youtube_config_path)

    def save_youtube_config(self):
        save_to_json_file(self.youtube_config, youtube_config_path)

    def load_secret_info(self):
        try:
            self.secret_data = get_json_data(secret_path)
            self.secret_info={}
            gmails = [self.youtube_config['template'][channel_name]['gmail'] for channel_name in self.youtube_config['template'].keys()]
            for gmail in gmails:
                oauth = self.secret_data[gmail]['oauth']
                api = self.secret_data[gmail]['api']
                oauth_path = f'{current_dir}\\oauth\\{gmail}.json'
                save_to_json_file(oauth, oauth_path)
                self.secret_info[gmail] = {}
                self.secret_info[gmail]["oauth_path"] = oauth_path
                self.secret_info[gmail]["api"] = api
            self.oauth_path = self.secret_info[self.gmail]["oauth_path"]
            self.api_key = self.secret_info[self.gmail]["api"]
        except:
            getlog()
            self.oauth_path = None
            self.api_key = None

    def get_start_youtube(self):
        self.get_youtube_config()
        if not self.is_first_start:
            self.reset()
        else:
            self.is_first_start = False
        self.is_start_youtube = True
        self.show_window()
        self.setting_window_size()
        create_button(frame = self.root,text="Đăng video sử dụng cookies(khuyến khích)", command= self.open_upload_video_by_cookies_window)
        create_button(frame = self.root,text="Đăng video bằng google(tối đa 6 video/ ngày / 1 gmail)", command= self.open_upload_video_by_API_window)
        create_button(frame = self.root,text="Download Videos", command=self.open_download_video_window)
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
            download_url = self.download_by_video_url.get()
            download_channel_id = self.download_by_channel_id.get()
            if not self.youtube_config['download_folder']:
                notification(self.root, "hãy chọn thư mục lưu file tải về.")
                return False
            if not download_url and not download_channel_id:
                notification(self.root, "hãy nhập url hoặc Id channel muốn tải video.")
                return False
            self.youtube_config['download_folder'] = download_folder
            self.youtube_config['download_by_video_url'] = download_url
            self.youtube_config['download_by_channel_id'] = download_channel_id
            self.youtube_config['filter_by_like'] = self.filter_by_like_var.get()
            self.youtube_config['filter_by_views'] = self.filter_by_views_var.get()
            self.save_youtube_config()
            return True

        def start_download_by_video_url():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                if save_download_settings():
                    self.download_thread = threading.Thread(target=self.download_video_by_video_url)
                    self.download_thread.start()
                else:
                    return

        def start_download_by_channel_id():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                if save_download_settings():
                    self.download_thread = threading.Thread(target=self.download_videos_by_channel_id)
                    self.download_thread.start()
                else:
                    return

        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu video", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        self.download_folder_var.insert(0, self.youtube_config['download_folder'])
        self.download_by_video_url = create_frame_button_and_input(self.root,text="Tải video từ URL", command=start_download_by_video_url, width=self.width, left=0.4, right=0.6)
        self.download_by_channel_id = create_frame_button_and_input(self.root,text="Tải từ ID kênh", command=start_download_by_channel_id, width=self.width, left=0.4, right=0.6)
        self.filter_by_like_var = self.create_settings_input("Lọc theo số lượt thích", "filter_by_like", is_data_in_template= False, values=["10000", "20000", "30000", "50000", "100000"], left=0.4, right=0.6)
        self.filter_by_views_var = self.create_settings_input("Lọc theo số lượt xem", "filter_by_views", is_data_in_template=False, values=["100000", "200000", "300000", "500000", "1000000"], left=0.4, right=0.6)
        create_button(self.root, text="Lùi lại", command=self.get_start_youtube, width=self.width)

    def choose_folder_to_save(self):
        download_folder = filedialog.askdirectory()
        if download_folder:
            self.download_folder_var.delete(0, ctk.END)
            self.download_folder_var.insert(0, download_folder)
        
    def open_upload_video_by_cookies_window(self):
        self.is_use_cookies = True
        self.open_upload_video_window()

    def open_upload_video_by_API_window(self):
        self.is_use_cookies = False
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

        def load_template():
            self.get_youtube_config()
            template_name = self.load_template_combobox.get()
            template = self.youtube_config['template'][template_name]
            # Clear existing values
            self.title_var.delete(0, ctk.END)
            self.description_var.delete("1.0", ctk.END)
            self.upload_date_var.delete(0, ctk.END)
            self.publish_times_var.delete(0, ctk.END)
            self.upload_folder_var.delete(0, ctk.END)
            self.number_of_days_var.delete(0, ctk.END)
            self.day_gap_var.delete(0, ctk.END)

            # Insert new values from template
            self.title_var.insert(0, template.get("title", ""))
            self.is_title_plus_video_name_var.set(convert_boolean_to_Yes_No(self.youtube_config['template'][self.channel_name]['is_title_plus_video_name']))
            self.description_var.delete("1.0", ctk.END)
            self.description_var.insert(ctk.END, template.get("description", ""))
            if not self.is_use_cookies:
                self.tags_var.delete(0, ctk.END)
                self.tags_var.insert(0, template.get("tags", ""))
                self.category_id_var.set(template.get("category_id", ""))
                self.privacy_status_var.set(template.get("privacy_status", ""))
                self.license_var.set(template.get("license", ""))
            self.upload_date_var.insert(0, template.get("upload_date", ""))
            self.publish_times_var.insert(0, template.get("publish_times", ""))
            if self.is_use_cookies:
                self.thumbnail_var.delete(0, ctk.END)
                self.thumbnail_var.insert(0, template.get("thumbnail", ""))
                self.playlist_var.set(template.get("playlist", ""))
                self.altered_content_var.set(convert_boolean_to_Yes_No(template.get("altered_content", False)))
            self.upload_folder_var.insert(0, template.get("upload_folder", ""))
            self.is_delete_after_upload_var.set(convert_boolean_to_Yes_No(self.youtube_config['template'][self.channel_name]['is_delete_after_upload']))
            self.number_of_days_var.insert(0, template.get("number_of_days", "1"))
            self.day_gap_var.insert(0, template.get("day_gap", "1"))

        self.title_var = self.create_settings_input("Tiêu đề", "title", left=left, right=right)
        self.is_title_plus_video_name_var = self.create_settings_input("Thêm tên video vào tiêu đề", "is_title_plus_video_name", values=["Yes", "No"], left=left, right=right)
        self.description_var = self.create_settings_input("Mô tả", "description", is_textbox=True, left=left, right=right)
        if not self.is_use_cookies:
            self.tags_var = self.create_settings_input("Thẻ tag", "tags", left=left, right=right)
            self.category_id_var = self.create_settings_input("Danh mục", "category_id", values=[ca for ca in youtube_category.keys()], left=left, right=right)
            self.privacy_status_var = self.create_settings_input("Chế độ hiển thị", "privacy_status", values=["public", "private", "unlisted"], left=left, right=right)
            self.license_var = self.create_settings_input("Giấy phép", "license", values=["youtube", "creativeCommon"], left=left, right=right)
        self.upload_date_var = self.create_settings_input("Ngày đăng(yyyy-mm-dd)", "upload_date", left=left, right=right)
        self.number_of_days_var = self.create_settings_input("Số ngày muốn đăng", "number_of_days", left=left, right=right)
        self.day_gap_var = self.create_settings_input("Khoảng cách giữa các ngày đăng", "day_gap", left=left, right=right)
        self.publish_times_var = self.create_settings_input("Giờ đăng(vd: 20:30:00)", "publish_times", left=left, right=right)
        if self.is_use_cookies:
            self.altered_content_var = self.create_settings_input(label_text="Nội dung đã bị chỉnh sửa", config_key="altered_content", values=['Yes', 'No'], left=0.3, right=0.7)
            self.playlist_var = self.create_settings_input("Chọn Playlist", "curent_playlist", values=self.youtube_config['template'][self.channel_name]["playlist"], left=left, right=right)
            try:
                self.playlist_var.set(self.youtube_config['template'][self.channel_name]["curent_playlist"])
            except:
                self.playlist_var.insert(0, self.youtube_config['template'][self.channel_name]["curent_playlist"])
            self.show_browser_var = self.create_settings_input(label_text="Hiển thị trình duyệt", config_key="show_browser", values=['Yes', 'No'], left=0.3, right=0.7, is_data_in_template=False)
            self.cookies_var = create_frame_label_and_input(self.root, label_text="Nhập cookies", width=self.width, left=left, right=right)
        self.is_delete_after_upload_var = self.create_settings_input("Xóa video sau khi đăng", "is_delete_after_upload", values=["Yes", "No"], left=left, right=right)
        if self.is_use_cookies: 
            self.thumbnail_var = create_frame_button_and_input(self.root, text="Chọn Thumbnail", command=self.choose_thumbnail_image, width=self.width, left=left, right=right)
            self.thumbnail_var.insert(0, self.youtube_config['template'][self.channel_name]['thumbnail'])
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa video", command=set_upload_folder, width=self.width)
        self.upload_folder_var.insert(0, self.youtube_config['template'][self.channel_name]['upload_folder'])
        self.load_template_combobox = create_frame_button_and_combobox(self.root,text="Tải mẫu có sẵn", width=self.width, command=load_template, values=list(self.youtube_config['template'].keys()))
        self.load_template_combobox.set(self.youtube_config['current_channel'])
        create_frame_button_and_button(self.root,text1="Đăng video ngay", width=self.width, command1=self.start_upload_videos_now, text2="Lên lịch đăng video", command2=self.start_upload_videos_with_schedule, left=0.5, right=0.5)
        create_button(self.root, text="Lùi lại", command=self.get_start_youtube, width=self.width)
        self.show_window()

    def choose_thumbnail_image(self):
        thumbnail_image = choose_file()
        self.thumbnail_var.delete(0, ctk.END)
        self.thumbnail_var.insert(0, thumbnail_image)

    def save_upload_setting(self):
        try:
            self.get_youtube_config()
            self.youtube_config['template'][self.channel_name]["title"] = self.title_var.get()
            self.youtube_config['template'][self.channel_name]["is_title_plus_video_name"] = self.is_title_plus_video_name_var.get() == "Yes"
            self.youtube_config['template'][self.channel_name]["description"] = self.description_var.get("1.0", ctk.END).strip()
            if self.is_use_cookies:
                playlist_name = self.playlist_var.get()
                self.youtube_config['template'][self.channel_name]["curent_playlist"] = playlist_name
                self.youtube_config['template'][self.channel_name]["playlist"].append(playlist_name)
                self.youtube_config['template'][self.channel_name]['altered_content'] = self.altered_content_var.get() == 'Yes'
                self.youtube_config['template'][self.channel_name]["thumbnail"] = self.thumbnail_var.get()
            else:
                self.youtube_config['template'][self.channel_name]["tags"] = self.tags_var.get()
                self.youtube_config['template'][self.channel_name]["category_id"] = self.category_id_var.get()
                self.youtube_config['template'][self.channel_name]["privacy_status"] = self.privacy_status_var.get()
                self.youtube_config['template'][self.channel_name]["license"] = self.license_var.get()
            self.youtube_config['template'][self.channel_name]["upload_date"] = self.upload_date_var.get()
            self.youtube_config['template'][self.channel_name]["number_of_days"] = self.number_of_days_var.get()
            self.youtube_config['template'][self.channel_name]["day_gap"] = self.day_gap_var.get()
            self.youtube_config['template'][self.channel_name]["publish_times"] = self.publish_times_var.get()
            self.youtube_config['template'][self.channel_name]["upload_folder"] = self.upload_folder_var.get()
            self.youtube_config['template'][self.channel_name]['gmail'] = self.gmail
            self.youtube_config['template'][self.channel_name]['is_delete_after_upload'] = self.is_delete_after_upload_var.get() == 'Yes'
            self.youtube_config['show_browser'] = self.show_browser_var.get() == 'Yes'
            self.save_youtube_config()
            validate_message = ""
            if len(self.youtube_config['template'][self.channel_name]["title"]) > 100:
                validate_message += "Tiêu đề có tối đa 100 ký tự.\n"
            if len(self.youtube_config['template'][self.channel_name]["description"]) > 5000:
                validate_message += "Mô tả có tối đa 5000 ký tự.\n"
            if len(self.youtube_config['template'][self.channel_name]["tags"]) > 500:
                validate_message += "thẻ tag có tối đa 500 ký tự.\n"
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
        if self.is_use_cookies:
            if self.login():
                print("Đăng nhập bằng cookies thành công")
                self.schedule_videos_by_selenium()
            else:
                print("Đăng nhập bằng cookies thất bại. Hãy sử dụng cookies mới nhất và thử đăng nhập lại.")
        else:
            self.schedule_videos()

    def open_dowload_video_from_channel_window(self):
        create_text_input(self.root)

    def get_authenticated_service(self):
        try:
            self.load_secret_info()
            if not self.oauth_path:
                notification(self.root, "Tài khoản gmail này chưa đăng ký hoặc đã hết hạn.")
                return
            try:
                flow = flow_from_clientsecrets(self.oauth_path, scope=SCOPES, message="xác minh thất bại")
                storage = Storage(f"{sys.argv[0]}-{self.gmail}-{self.channel_name}.json")
                credentials = storage.get()
            except:
                getlog()
                credentials = None
            if credentials is None or credentials.invalid:
                credentials = run_flow(flow, storage, None)
            return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
        except Exception as e:
            error_message(f"Xác minh thất bại. Hãy đảm bảo gmail {self.gmail} đăng đăng nhập trong trình duyệt xác minh")
            getlog()
            return None

    def upload_video(self, video_file, publish_at=None):
        try:
            category_name = self.youtube_config['template'][self.channel_name]['category_id']
            category_id = int(youtube_category[category_name])
            body = {
                "snippet": {
                    "title": self.full_title,
                    "description": self.youtube_config['template'][self.channel_name]['description'],
                    "tags": self.youtube_config['template'][self.channel_name]['tags'],
                    "categoryId": category_id,
                    "defaultLanguage": "en",  # Thêm ngôn ngữ tiếng Anh
                    "automaticChapters": False  # Tắt tự động chương và khoảnh khắc chính
                },
                "status": {
                    "privacyStatus": self.youtube_config['template'][self.channel_name]['privacy_status'],
                    "selfDeclaredMadeForKids": False,
                    'license': self.youtube_config['template'][self.channel_name]['license'],
                    'notifySubscribers': False,   # Disable notifications to subscribers
                }
            }
            if publish_at:
                body['status']['publishAt'] = publish_at
                body['status']['privacyStatus'] = 'private'
            insert_request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True),
            )
            video_id = self.resumable_upload(insert_request)
            if video_id:
                sleep(2)
                return True
            return False
        except:
            getlog()
            return False

    def resumable_upload(self, insert_request):
        response = None
        while response is None:
            try:
                if self.is_stop_upload:
                    return None
                self.save_youtube_config()
                print ("Đang đăng video...")
                status, response = insert_request.next_chunk()
                if response is not None and 'id' in response:
                    video_id = response['id']
                    print(f"Video id '{video_id}' was successfully uploaded.")
                    sleep(2)
                    return video_id
            except HttpError as e:
                if e.resp.status == 403:
                    error_details = e._get_reason()
                    if 'quota' in error_details:
                        print("Quota exceeded. Please wait before making more requests.")
                        time_reset = get_time_remaining_until_quota_reset()
                        notification(self.root, f"Tài khoản {self.gmail} đã đăng 6 video trong hôm nay(mức tối đa khi dùng dịch vụ của google), vui lòng đợi thêm {time_reset/3600} giờ để tiếp tục đăng!")
                    else:
                        print(f"HTTP error occurred: {error_details}")
                else:
                    print(f"An error occurred when resumable_upload: {e}")
                return None
            except:
                getlog()
                return None

    def schedule_videos_by_selenium(self):
        try:
            videos_folder = self.youtube_config['template'][self.channel_name]['upload_folder']
            if not videos_folder or not os.path.isdir(videos_folder):
                print(f"Thư mục chứa video của channel {self.channel_name} không tồn tại")
                return
            videos = os.listdir(videos_folder)
            videos = [k for k in videos if '.mp4' in k]      
            if len(videos) == 0:
                print(f"Không có video nào trong thư mục {videos_folder}")
                return
            videos = natsorted(videos)

            if self.is_schedule:
                number_of_days = get_number_of_days(self.youtube_config['template'][self.channel_name]['number_of_days'])
                day_gap = get_day_gap(self.youtube_config['template'][self.channel_name]['day_gap'])
                upload_date_str = self.youtube_config['template'][self.channel_name]['upload_date']
                if not upload_date_str:
                    return
                publish_times = self.youtube_config['template'][self.channel_name]['publish_times'].split(',')
                if not publish_times:
                    return
                if self.is_auto_upload:
                    number_of_days = 200
                    upload_date_str = add_date_into_string(upload_date_str, day_gap)
                upload_date = get_upload_date(upload_date_str, next_day=True)
                upload_date_str = convert_datetime_to_string(upload_date)
                tomorow_str = convert_datetime_to_string(datetime.now() + timedelta(days=1))
            upload_count = 0
            date_cnt = 0
            for i, video_file in enumerate(videos):
                day_delta = 60
                if is_date_greater_than_current_day(upload_date_str, day_delta):
                    print(f"Ngày đăng {upload_date_str} vượt quá {day_delta} ngày so với ngày hiện tại. Không thể tiếp tục đăng video.")
                    break
                if self.is_schedule:
                    publish_time = publish_times[upload_count % len(publish_times)].strip()
                    try:
                        datetime.strptime(publish_time.strip(), '%H:%M:%S').time()
                    except:
                        if not self.is_auto_upload:
                            notification(self.root, "time data %r does not match format %r" % (publish_time, '%H:%M:%S'))
                        return
                    hh, mm, ss = publish_time.split(':')
                    publish_time = f'{hh}:{mm}'
                    try:
                        if int(hh) < 0 or int(hh) > 23:
                            print("Giờ không hợp lệ, lấy mặc định là 00")
                            hh = '00'
                        if int(mm) != 0 and int(mm) != 15 and int(mm) != 30 and int(mm) != 45:
                            print("Phút không hợp lệ, lấy mặc định là 00")
                            mm = '00'
                    except:
                        print("Giờ đăng video không hợp lệ. Định dạng đúng là hh:mm (Ví dụ: 09:00,21:00)")
                        return
                
                if self.is_stop_upload:
                    break
                video_name = os.path.splitext(video_file)[0] #lấy tên
                title = self.youtube_config['template'][self.channel_name]['title']
                if self.youtube_config['template'][self.channel_name]['is_title_plus_video_name']:
                    full_title = f"{title}{video_name}"
                else:
                    full_title = title
                if len(full_title) > 100:
                    if not self.is_auto_upload:
                        notification(self.root, f"Chiều dài tối đa của tiêu đề là 100 ký tự:\n{self.full_title}: có tổng {len(self.full_title)} ký tự")
                    continue
                video_path = os.path.join(videos_folder, video_file)
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
                if self.youtube_config['template'][self.channel_name]['thumbnail']:
                    self.input_thumbnail(thumbnail_path=self.youtube_config['template'][self.channel_name]['thumbnail'])
                if self.youtube_config['template'][self.channel_name]['curent_playlist']:
                    self.choose_playlist(self.youtube_config['template'][self.channel_name]['curent_playlist'])
                if self.youtube_config['template'][self.channel_name]['altered_content']:
                    self.click_show_more()
                    self.click_altered_content()

                self.click_next_button()
                if self.is_schedule:
                    self.click_schedule_option()
                    if not upload_date_str == tomorow_str:
                        self.choose_date(upload_date_str)
                    self.choose_publish_time(publish_time)
                    if self.is_stop_upload:
                        break
                    self.click_schedule_now()
                    # self.click_close_button()
                    upload_count += 1
                    if self.youtube_config['template'][self.channel_name]['upload_date'] != upload_date_str:
                        self.youtube_config['template'][self.channel_name]['upload_date'] = upload_date_str
                        self.save_youtube_config()
                    remove_or_move_after_upload(video_path, self.youtube_config['template'][self.channel_name]['is_delete_after_upload'], finish_folder_name='youtube_upload_finished')
                    if (upload_count) % len(publish_times) == 0:
                        upload_date_str = add_date_into_string(upload_date_str, day_gap)
                        date_cnt += 1
                        if date_cnt == number_of_days:
                            break
                else:
                    self.click_public_radio()
                    if self.is_stop_upload:
                        break
                    self.click_public_now()
                    upload_count += 1
                    remove_or_move_after_upload(video_path, self.youtube_config['template'][self.channel_name]['is_delete_after_upload'], finish_folder_name='youtube_upload_finished')
                    break
                
 
            if not self.is_auto_upload:
                notification(self.root, f"Đăng thành công {upload_count} video")
            else:
                print(f"Đăng thành công {upload_count} video")

            return True
        except:
            getlog()
            return False
        finally:
            self.close_driver()
        
    def schedule_videos(self):
        try:
            videos_folder = self.youtube_config['template'][self.channel_name]['upload_folder']
            if not videos_folder or not os.path.isdir(videos_folder):
                print(f"Thư mục chứa video của channel {self.channel_name} không tồn tại")
                return
            videos = os.listdir(videos_folder)
            videos = [k for k in videos if '.mp4' in k]      
            if len(videos) == 0:
                print(f"Không có video nào trong thư mục {videos_folder}")
                return
            videos = natsorted(videos)

            if self.is_schedule:
                number_of_days = get_number_of_days(self.youtube_config['template'][self.channel_name]['number_of_days'])
                day_gap = get_day_gap(self.youtube_config['template'][self.channel_name]['day_gap'])
                upload_date_str = self.youtube_config['template'][self.channel_name]['upload_date']
                if not upload_date_str:
                    return
                publish_times = self.youtube_config['template'][self.channel_name]['publish_times'].split(',')
                if not publish_times:
                    return
                if self.is_auto_upload:
                    number_of_days = 10
                    upload_date_str = add_date_into_string(upload_date_str, day_gap)
                upload_date = convert_date_string_to_datetime(upload_date_str)
                if not upload_date:
                    return False

            upload_count = 0
            date_cnt = 0
            for i, video_file in enumerate(videos):
                if self.is_stop_upload:
                    break
                video_name = os.path.splitext(video_file)[0] #lấy tên
                title = self.youtube_config['template'][self.channel_name]['title']
                if self.youtube_config['template'][self.channel_name]['is_title_plus_video_name']:
                    self.full_title = f"{title}{video_name}"
                else:
                    self.full_title = title
                if len(self.full_title) > 100:
                    if not self.is_auto_upload:
                        notification(self.root, f"Chiều dài tối đa của tiêu đề là 100 ký tự:\n{self.full_title}: có tổng {len(self.full_title)} ký tự")
                    return False
                video_path = os.path.join(videos_folder, video_file)
                if self.is_schedule:
                    publish_time_str = publish_times[upload_count % len(publish_times)]
                    try:
                        publish_time = datetime.strptime(publish_time_str.strip(), '%H:%M:%S').time()
                    except:
                        getlog()
                        if not self.is_auto_upload:
                            notification(self.root, "time data %r does not match format %r" % (publish_time_str, '%H:%M:%S'))
                    publish_datetime = datetime.combine(upload_date, publish_time)
                    publish_at = convert_time_to_UTC(publish_datetime.year, publish_datetime.month, publish_datetime.day, publish_datetime.hour, publish_datetime.minute, publish_datetime.second)
                else:
                    publish_at=None
                
                if self.upload_video(video_path, publish_at=publish_at):
                    remove_or_move_after_upload(video_path, self.youtube_config['template'][self.channel_name]['is_delete_after_upload'], finish_folder_name='youtube_upload_finished')
                    upload_count += 1
                    self.youtube_config['template'][self.channel_name]['upload_date'] = convert_datetime_to_string(upload_date)
                    self.save_youtube_config()
                    print(f"Đăng thành công video '{video_file}' lúc {publish_datetime}")
                    if self.is_schedule:
                        if (i + 1) % len(publish_times) == 0:
                            upload_date += timedelta(days=day_gap)
                            date_cnt += 1
                            if date_cnt == number_of_days:
                                break
                    else:
                        break
                else:
                    print("uploaded fail")
                    return False
            if upload_count > 0:
                self.save_youtube_config()
            if not self.is_auto_upload:
                notification(self.root, f"Đăng thành công {upload_count} video")
            else:
                print(f"Đăng thành công {upload_count} video")

            return True
        except:
            getlog()
            return False

    
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
                response = self.youtube.channels().list(part="contentDetails", id=self.youtube_config['download_by_channel_id']).execute()
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
            print(f"An error occurred when get_video_ids_by_channel_id: {e}")
        return []
    
    def get_video_details(self, video_ids, check_status=False):
        # Chia nhóm video ID để yêu cầu thông tin chi tiết
        chunk_size = 50  # Số lượng video ID trong mỗi nhóm (giới hạn của API)
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
                    

    
    def download_video_by_video_url(self):
        self.youtube_config['download_folder'] = self.download_folder_var.get()
        video_url = self.download_by_video_url.get()
        self.download_video_youtube_by_url(video_url)

    def download_videos_by_channel_id(self):
        self.youtube_config['download_folder'] = self.download_folder_var.get()
        self.list_videos_download_from_channel = []
        video_ids = self.get_video_ids_by_channel_id()
        self.get_video_details(video_ids)
        if len(self.list_videos_detail) > 0:
            self.get_download_info()
            if not self.download_info:
                self.download_info = {}
            if 'downloaded_urls' not in self.download_info:
                self.download_info['downloaded_urls'] = []

            for videos_detail in self.list_videos_detail:
                self.check_videos_and_dowload(videos_detail)
            cnt = len(self.list_videos_download_from_channel)
            if cnt == 0:
                notification(self.root, "There are no videos that meet the criteria for number of likes and views!")
            else:
                notification(self.root, f"Videos Downloaded Successfully {cnt} video")

    def check_videos_and_dowload(self, video_details):
        for video in video_details['items']:
            statistics = video['statistics']
            like_count = int(statistics.get('likeCount', 0))
            view_count = int(statistics.get('viewCount', 0))
            if like_count > int(self.youtube_config['filter_by_like']) and view_count > int(self.youtube_config['filter_by_views']):
                video_id = video['id']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                if video_url in self.download_info['downloaded_urls']:
                    print("url này đã tải hoặc có trong danh sách đợi download")
                    continue
                print(f"bắt đầu tải video: {video_url} với {like_count} lượt thích và {view_count} lượt xem")
                title = self.video_info[video_id]['title']
                download_folder = self.youtube_config['download_folder']
                file_name = f"{convert_sang_tieng_viet_khong_dau(title)}.mp4"
                video_file_path = f'{download_folder}\\{file_name}'
                if not os.path.exists(video_file_path):
                    self.list_waiting_dowload_videos.append(video_url)
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
            download_video_by_url(video_url, self.youtube_config['download_folder'])
            self.list_videos_download_from_channel.append(video_url)
            if video_url not in self.download_info['downloaded_urls']:
                self.download_info['downloaded_urls'].append(video_url)
            save_to_json_file(self.download_info, download_info_path)
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
        if self.is_start_youtube:
            self.root.title(f"Youtube: {self.gmail}: {self.channel_name}")
            self.width = 500
            self.height_window = 215
            self.is_start_youtube = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video Youtube: {self.channel_name}")
            self.width = 800
            if self.is_use_cookies:
                self.height_window = 971
            else:
                self.height_window = 924
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos Youtube")
            self.width = 600
            self.height_window = 370
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
                else:
                    val = ""

            combobox = ctk.CTkComboBox(frame, values=values, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            combobox.set(val)
            setattr(self, f"{config_key}_var", val)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", val)
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, val)
            setattr(self, f"{config_key}_var", val)
            return entry
