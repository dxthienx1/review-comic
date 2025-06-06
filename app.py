from common_function import *

class MainApp:
    def __init__(self):
        try:
            self.root = ctk.CTk()
            self.root.title("REVIEW App")
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
            self.config_xtts_last = get_json_data(last_config_xtts_path) or {}
            self.support_languages = supported_languages
            remove_file("log.txt")
            self.device = device
            self.icon = None
            self.is_start_app = True
            self.is_start_window = False
            self.is_edit_video_window = False
            self.is_edit_audio_option = False
            self.is_extract_audio_option = False
            self.is_open_edit_video_menu = False
            self.is_open_common_setting = False
            self.is_other_window = False
            self.is_other_download_window = False
            self.is_text_to_mp3_window = False
            self.is_edit_audio_window = False
            self.is_combine_video_window = False
            self.is_rename_file_by_index_window = False
            self.is_merge_txt_file = False
            self.is_merge_image = False
            self.is_take_screenshot = False
            self.is_convert_jpg_to_png = False
            self.is_remove_char_in_file_name_window = False
            self.is_extract_image_from_video_window = False
            self.is_editing_video = False
            self.first_check_status_video = True
            self.is_stop_edit = False
            self.is_stop_download = False
            self.is_stop_export_next_video = False
            self.driver = None
            self.new_name=None
            self.index = 1
            self.download_image_from_truyenqqto = False
            self.download_text_story = False
            self.edit_image_window = False
            self.export_video_window = False
            self.export_video_from_mp3_window = False
            self.create_video_with_multi_audio_window = False
            self.is_extract_sub_image_audio_from_video_window = False
            self.en_language = False
            self.xtts = None

            self.setting_window_size()
            self.create_icon()
            self.get_start_window()
            if self.config["auto_start"]:
                set_autostart()
            else:
                unset_autostart()
            self.is_start_app = False
        except:
            getlog()

#------------------------------------------------main thread----------------------------------------------------

#-------------------------------------------Điều hướng window--------------------------------------------

    def get_start_window(self):
        if not self.is_start_app:
            self.reset()
            self.is_start_window=True
            self.show_window()
            self.setting_window_size()
        else:
            self.show_window()
        create_button(frame=self.root, text="Tải truyện chữ", command=self.open_download_text_story_window)
        create_button(frame=self.root, text="Tải truyện tranh", command=self.open_download_image_window)
        create_button(frame=self.root, text="Lấy phụ đề từ ảnh", command=self.get_subtitle_from_image_window)
        create_button(frame=self.root, text="Xuất video từ file txt và ảnh/video nền", command=self.export_video_from_subtitles_window)
        create_button(frame=self.root, text="Xuất video từ audio tổng và video nền", command=self.export_video_from_mp3_and_background_video_window)
        create_button(frame=self.root, text="Xuất video từ nhiều audio và video nền + hiển thị chữ", command=self.export_video_with_multi_audio_and_background_window)
        create_button(frame=self.root, text="Tải video", command=self.open_other_download_video_window)
        create_button(frame=self.root, text="Xử lý video", command=self.open_edit_video_menu)
        create_button(frame=self.root, text="Xử lý audio", command=self.open_edit_audio_window)
        create_button(frame=self.root, text="Chức năng khác", command=self.other_function)
        # create_button(frame=self.root, text="Cài đặt chung", command=self.open_common_settings)

    def open_download_text_story_window(self):
        def start_thread_download_text_story():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                self.download_thread = threading.Thread(target=self.start_download_text_story)
                self.download_thread.start()
        
        self.reset()
        self.download_text_story = True
        self.show_window()
        self.setting_window_size()
        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu truyện", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        self.chapters_var = create_frame_label_and_input(self.root, text="chương bắt đầu-chương kết thúc", width=self.width, left=0.4, right=0.6)
        self.download_text_story_var = create_frame_label_and_input(self.root,text="Mẫu link tải chương truyện", place_holder="thay số chương bằng <idx>", width=self.width, left=0.4, right=0.6)
        self.replace_text_var = create_frame_label_and_input(self.root,text="Phần loại bỏ", place_holder="loại bỏ 1|loại bỏ 2|loại bỏ 3", width=self.width, left=0.4, right=0.6)
        create_button(self.root, text="Bắt đầu tải", command=start_thread_download_text_story, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def start_download_text_story(self):
        try:
            main_folder = self.download_folder_var.get()
            if not main_folder.strip():
                print(f'Hãy chọn thư mục chứa truyện tải về!')
                return
            if not check_folder(main_folder):
                return
            base_url = self.download_text_story_var.get()
            if not base_url.startswith('http://vietnamthuquan'):
                is_use_profile = True
            else:
                is_use_profile = False
            replace_text = self.replace_text_var.get().strip()
            if replace_text:
                replace_texts = replace_text.split('|') or []
            start_chapter = self.chapters_var.get().strip()
            if '-' not in start_chapter:
                start_chapter = int(start_chapter)
                end_chapter = 5000
            else:
                try:
                    start_chapter, end_chapter = start_chapter.split('-')
                    start_chapter = int(start_chapter.strip())
                    end_chapter = int(end_chapter.strip())
                except:
                    start_chapter = 1
                    end_chapter = 5000

            if not base_url:
                self.noti("Hãy nhập link truyện muốn tải trước.")
                return
            if is_use_profile:
                driver = get_firefox_driver_with_profile(show=True)
            else:
                driver = get_driver(show=True)
            sleep(1)
            driver.get(base_url)
            sleep(8)
            list_linkes = []
            skip_text = ['discord', 'http', 'Translator:', 'TL:', 'For extra chapters', 'chapters ahead on patreon', 'by removing ads', '~ support & read', 'chapters available on']
            start_down = True
            cnt_err = 0
            first_content = ""
            txt_path = ""
            ads_texts = None
            if '<idx>' in base_url:
                for i in range(0, end_chapter):
                    txt_path = os.path.join(main_folder, f'{start_chapter}.txt')
                    chapter_content = ""
                    with open(txt_path, 'w', encoding='utf-8') as file:
                        link = base_url.replace('<idx>', str(start_chapter))
                        if link not in list_linkes:
                            driver.get(link)
                            sleep(2)
                            if start_down:
                                sleep(8)
                                start_down = False
                            if 'https://metruyenchu' in  link:
                                xpath = get_xpath('article', 'chapter-content', contain=True)
                                ele = get_element_by_xpath(driver, xpath)
                                if ele:
                                    list_contents = ele.find_elements(By.XPATH, './/p') or []
                                    if len(list_contents) > 0:
                                        for p_ele in list_contents:
                                            content = p_ele.text
                                            chapter_content = f'{chapter_content}\n{content}' if chapter_content else content
                            elif 'https://novelbin.com' in  link:
                                xpath = get_xpath_by_multi_attribute('div', ['id="chr-content"'])
                                ele = get_element_by_xpath(driver, xpath)
                                if ele:
                                    list_contents = ele.find_elements(By.XPATH, './/p') or []
                                    if len(list_contents) > 0:
                                        for p_ele in list_contents:
                                            content = p_ele.text
                                            if i == 0 and content.strip().lower().startswith('chapter'):
                                                continue
                                            chapter_content = f'{chapter_content}\n{content}' if chapter_content else content
                                if not chapter_content.strip():
                                    if cnt_err < 2:
                                        webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
                                        sleep(2)
                                        webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
                                        print(f'Xác minh capcha')
                                        sleep(5)
                                        cnt_err += 1
                                        start_chapter -= 1
                                        continue
                                    else:
                                        break
                            elif 'https://www.empirenovel' in  base_url:
                                xpath = get_xpath_by_multi_attribute('div', ['id="read-novel"'])
                                ele = get_element_by_xpath(driver, xpath)
                                if ele:
                                    list_contents = ele.find_elements(By.XPATH, './/p') or []
                                    if len(list_contents) > 0:
                                        for i, p_ele in enumerate(list_contents):
                                            content = p_ele.text
                            
                                            if any(word.lower() in content.lower() for word in skip_text):
                                                continue
                                            chapter_content = f'{chapter_content}\n{content}' if chapter_content else content

                                        if chapter_content.strip() and chapter_content.strip()[:200] not in first_content:
                                            first_content = chapter_content.strip()
                                            file.write(f'{chapter_content.strip()}')
                                            start_chapter += 1
                                            cnt_err = 0
                                            continue
                                        else:
                                            print(f'Không trích xuất được nội dung truyện tại chương {start_chapter}!!!')
                                            break
                            elif 'http://vietnamthuquan' in  link:
                                xpath_links = "//div[contains(@onclick, 'chuongid')]"
                                all_links = get_element_by_xpath(driver, xpath_links, multiple=True)
                                for i, link_chapter in enumerate(all_links):
                                    txt_path1 = os.path.join(main_folder, f'{i+1}.txt')
                                    with open(txt_path1, 'w', encoding='utf-8') as file:
                                        link_chapter.click()
                                        sleep(4)
                                        xpath = get_xpath('div', 'chuhoavn')
                                        ele = get_element_by_xpath(driver, xpath)
                                        if ele:
                                            chapter_content = ele.text
                                        if chapter_content.strip() and first_content != chapter_content.strip():
                                            first_content = chapter_content.strip()
                                            chapter_content = ""
                                            start_chapter += 1
                                        else:
                                            print(f'Không trích xuất được nội dung truyện tại chương {i}!!!')
                                            break
                                return
                            elif 'https://banlong.us/' in  link:
                                xpath = get_xpath('div', 'published-content', contain=True)
                                ele = get_element_by_xpath(driver, xpath)
                                if ele:
                                    list_contents = ele.find_elements(By.XPATH, './/p') or []
                                    if len(list_contents) > 0:
                                        for p_ele in list_contents:
                                            content = p_ele.text
                                            chapter_content = f'{chapter_content}\n{content}' if chapter_content else content
                            elif 'https://truyenyy' in  link:
                                xpath = get_xpath('div', 'chap-content', contain=True)
                                ele = get_element_by_xpath(driver, xpath)
                                if ele:
                                    list_contents = ele.find_elements(By.XPATH, './/p') or []
                                    if len(list_contents) > 0:
                                        for p_ele in list_contents:
                                            content = p_ele.text
                                            chapter_content = f'{chapter_content}\n{content}' if chapter_content else content
                            elif 'https://truyenfull' in  link or 'https://truyenhoan' in link:
                                xpath = get_xpath('div', 'chapter-c', contain=True)
                                ele = get_element_by_xpath(driver, xpath)
                                if ele:
                                    ads_contents = ele.find_elements(By.XPATH, "./*")
                                    if not ads_texts:
                                        ads_texts = [e.text.strip() for e in ads_contents if e.text.strip()]
                                        for replace_text in replace_texts:
                                            if replace_text not in ads_texts:
                                                ads_texts.append(replace_text)

                                    content = ele.text
                                    for ad_text in ads_texts:
                                        content = content.replace(ad_text, '')
                                    if content:
                                        liness = content.split('\n')
                                        lines = [line.strip() for line in liness if line.strip()]
                                        for content in lines:
                                            chapter_content = f'{chapter_content}\n{content}' if chapter_content else content

                            if chapter_content.strip() and first_content != chapter_content.strip():
                                first_content = chapter_content.strip()
                                file.write(f'{chapter_content.strip()}')
                                cnt_err = 0
                                start_chapter += 1
                            else:
                                print(f'Không trích xuất được nội dung truyện tại chương {start_chapter}!!!')
                                remove_file(txt_path)
                                break
            else:
                for i in range(0, end_chapter-start_chapter+1):
                    txt_path = os.path.join(main_folder, f'{start_chapter}.txt')
                    chapter_content = ""
                    with open(txt_path, 'w', encoding='utf-8') as file:
                        if 'https://novelbin.com' in  base_url:
                            xpath = get_xpath_by_multi_attribute('div', ['id="chr-content"'])
                            ele = get_element_by_xpath(driver, xpath)
                            if ele:
                                list_contents = ele.find_elements(By.XPATH, './/p') or []
                                if len(list_contents) > 0:
                                    for i, p_ele in enumerate(list_contents):
                                        content = p_ele.text
                                        if i == 0 and content.strip().lower().startswith('chapter'):
                                            continue
                                        if i == 1 and content.strip().lower().startswith('chapter'):
                                            continue
                                        
                                        if any(word.lower() in content.lower() for word in skip_text):
                                            continue
                                        chapter_content = f'{chapter_content}\n{content}' if chapter_content else content

                                    if chapter_content.strip() and chapter_content.strip()[:200] not in first_content:
                                        first_content = chapter_content.strip()
                                        file.write(f'{chapter_content.strip()}')
                                        start_chapter += 1
                                        cnt_err = 0
                                    else:
                                        if cnt_err < 2:
                                            webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
                                            sleep(2)
                                            webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
                                            print(f'Xác minh capcha')
                                            sleep(5)
                                            cnt_err += 1
                                            continue
                                        else:
                                            print(f'Không trích xuất được nội dung truyện tại chương {start_chapter}!!!')
                                            break
                                    next_chap_ele = get_element_by_text(driver, 'Next Chapter', 'span')
                                    if next_chap_ele:
                                        next_chap_ele.click()
                                        sleep(4)
                                        continue
                        elif 'https://www.lightnovelpub' in  base_url:
                            xpath = get_xpath_by_multi_attribute('div', ['id="chapter-container"'])
                            ele = get_element_by_xpath(driver, xpath)
                            if ele:
                                list_contents = ele.find_elements(By.XPATH, './/p') or []
                                if len(list_contents) > 0:
                                    for i, p_ele in enumerate(list_contents):
                                        content = p_ele.text
                         
                                        if any(word.lower() in content.lower() for word in skip_text):
                                            continue
                                        chapter_content = f'{chapter_content}\n{content}' if chapter_content else content

                                    if chapter_content.strip() and chapter_content.strip()[:200] not in first_content:
                                        first_content = chapter_content.strip()
                                        file.write(f'{chapter_content.strip()}')
                                        start_chapter += 1
                                        cnt_err = 0
                                    else:
                                        print(f'Không trích xuất được nội dung truyện tại chương {start_chapter}!!!')
                                        break
                                    next_xpath = get_xpath('a', 'nextchap', contain=True)
                                    next_chap_ele = get_element_by_xpath(driver, next_xpath)
                                    if next_chap_ele:
                                        next_chap = next_chap_ele.get_attribute('href')
                                        if next_chap and 'lightnovelpub' in next_chap:
                                            driver.get(next_chap)
                                            sleep(4)
                                            continue
                                    break
                        elif 'https://www.empirenovel' in  base_url:
                            xpath = get_xpath_by_multi_attribute('div', ['id="read-novel"'])
                            ele = get_element_by_xpath(driver, xpath)
                            if ele:
                                list_contents = ele.find_elements(By.XPATH, './/p') or []
                                if len(list_contents) > 0:
                                    for i, p_ele in enumerate(list_contents):
                                        content = p_ele.text
                         
                                        if any(word.lower() in content.lower() for word in skip_text):
                                            continue
                                        chapter_content = f'{chapter_content}\n{content}' if chapter_content else content

                                    if chapter_content.strip() and chapter_content.strip()[:200] not in first_content:
                                        first_content = chapter_content.strip()
                                        file.write(f'{chapter_content.strip()}')
                                        start_chapter += 1
                                        cnt_err = 0
                                    else:
                                        print(f'Không trích xuất được nội dung truyện tại chương {start_chapter}!!!')
                                        break
                                    next_xpath = get_xpath_by_multi_attribute('a', ['id="chapter-right"'])
                                    next_chap_ele = get_element_by_xpath(driver, next_xpath)
                                    if next_chap_ele:
                                        next_chap = next_chap_ele.get_attribute('href')
                                        if next_chap and 'lightnovelpub' in next_chap:
                                            driver.get(next_chap)
                                            sleep(4)
                                            continue
                                    break
                        elif 'https://truyenfull' in  base_url or 'https://truyenhoan' in base_url:
                            xpath = get_xpath('div', 'chapter-c', contain=True)
                            ele = get_element_by_xpath(driver, xpath)
                            if ele:
                                ads_contents = ele.find_elements(By.XPATH, "./*")
                                ads_texts = [e.text.strip() for e in ads_contents if e.text.strip()]
                                content = ele.text
                                for ad_text in ads_texts:
                                    content = content.replace(ad_text, '')
                                if content:
                                    liness = content.split('\n')
                                    lines = [line.strip() for line in liness if line.strip()]
                                    for content in lines:
                                        chapter_content = f'{chapter_content}\n{content}' if chapter_content else content

                                    if chapter_content.strip() and first_content.startswith(chapter_content.strip()[:200]):
                                        first_content = chapter_content.strip()
                                        file.write(f'{chapter_content.strip()}')
                                        start_chapter += 1
                                        cnt_err = 0
                                    else:
                                        if cnt_err < 2:
                                            webdriver.ActionChains(driver).send_keys(Keys.TAB).perform()
                                            sleep(2)
                                            webdriver.ActionChains(driver).send_keys(Keys.SPACE).perform()
                                            print(f'Xác minh capcha')
                                            sleep(5)
                                            cnt_err += 1
                                            continue
                                        else:
                                            print(f'Không trích xuất được nội dung truyện tại chương {start_chapter}!!!')
                                            break
                                next_xpath = get_xpath_by_multi_attribute('a', ['id="next_chap"'])
                                next_ele = get_element_by_xpath(driver, next_xpath)
                                if next_ele:
                                    next_chap = next_ele.get_attribute('href')
                                    if next_ele:
                                        if next_chap and 'https://truyenfull' in next_chap:
                                            driver.get(next_chap)
                                            sleep(3)

        except:
            remove_file(txt_path)
            getlog()
        finally:
            self.close_driver()

    def get_subtitle_from_image_window(self):
        def start_get_subtitle_from_image_thread():
            edit_thread = threading.Thread(target=self.start_get_subtitle_from_image)
            edit_thread.start()
        
        self.reset()
        self.edit_image_window = True
        self.show_window()
        self.setting_window_size()
        self.black_word_var = create_frame_label_and_input(self.root, text="Các từ muốn loại bỏ", width=self.width, left=0.4, right=0.6)
        self.language_var = self.create_settings_input(text="Ngôn ngữ muốn lấy", values=['vi', 'en'], left=0.4, right=0.6)
        self.language_var.set('vi')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa truyện", command=self.choose_videos_edit_folder, width=self.width, left=0.4, right=0.6)
        create_button(self.root, text="Bắt đầu", command=start_get_subtitle_from_image_thread, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def start_get_subtitle_from_image(self):
        try:
            lang = self.language_var.get().strip()
            def extract_text_from_images(chapter_folder, lang=lang):

                def input_image_to_gg(image_path):
                    try:
                        xpath = "//input[contains(@accept, '.jpg') and contains(@accept, '.png')]"
                        ele = get_element_by_xpath(self.driver, xpath)
                        ele.send_keys(image_path)
                        return True
                    except:
                        return False
                    

                chapter_name = chapter_folder.split('chuong ')[-1]
                black_words = self.black_word_var.get().strip().split(',') or []
                black_words = [jjj for jjj in black_words if jjj.strip()]
                all_skip_words = [iii for iii in skip_words if 'fff' not in iii and iii not in black_words]
                black_words = all_skip_words + black_words if black_words else all_skip_words
                file_path = os.path.join(chapter_folder, f'chuong {chapter_name}_{lang}.txt')
                if lang == 'vi':
                    link = f'https://translate.google.com/?sl=en&tl={lang}&op=images'
                else:
                    link = f'https://translate.google.com/?sl=fr&tl={lang}&op=images'
                with open(file_path, 'w', encoding='utf-8') as file:
                    for filename in natsorted(os.listdir(chapter_folder)):
                        text = None
                        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                            image_path = os.path.join(chapter_folder, filename)
                            self.driver.get(link)
                            sleep_random(1.5,1.8)
                            print(f'Xử lý ảnh {filename}')
                            if input_image_to_gg(image_path):
                                try:
                                    sleep_random(5,6)
                                    img_xpath = get_xpath('img', 'Jmlpdc')
                                    for cnt in range(5):  
                                        img_ele = get_element_by_xpath(self.driver, img_xpath, index=-1)  
                                        if img_ele:  
                                            break  
                                        print(f"cnt {cnt}")  
                                        sleep_random(1,2)  

                                    if not img_ele:
                                        print("Không tìm thấy ảnh --> bỏ qua")
                                        continue
                                    text = img_ele.get_attribute('alt')
                                    if not text or not text.strip():
                                        text = ' '
                                    else:
                                        texts = text.split('\n')
                                        text_s = [ttt.strip() for ttt in texts if ttt.strip() and not ttt.strip().isdigit()]
                                        for word in black_words:
                                            text_s = [tex for tex in text_s if tex.strip() and word.lower() not in tex.lower()]
                                        if not text_s:
                                            continue
                                        text = "\n".join(text_s)
                                        # text = cleaner_text(text, language=lang, is_conver_number=False, is_loi_chinh_ta=False)
                                        print(f'{thanhcong} nội dung ảnh {filename} --> {text}')
                                    file.write(f"{filename.split('.')[0]}\n{text.strip()}\n")

                                except:
                                    getlog()
                                    continue
                                    
            main_folder = self.videos_edit_folder_var.get()
            if not check_folder(main_folder):
                return
            chapters_folder = get_file_in_folder_by_type(main_folder, 'chuong ')
            if len(chapters_folder) == 0:
                print(f"Không tìm thấy chương truyện nào trong thư mục {main_folder}")
                return
            chapters_folder = natsorted(chapters_folder)
            self.driver = get_driver_with_profile()
            sleep(2)
            for chapter_folder in chapters_folder:
                print(f'Bắt đầu xử lý ảnh chương {chapter_folder}')
                chapter_folder = os.path.join(main_folder, chapter_folder)
                extract_text_from_images(chapter_folder, lang=lang)
                if self.is_stop_edit:
                    break
        except:
            getlog()
            print("Có lỗi trong quá trình xử lý hình ảnh")
        finally:
            self.close_driver()

    def export_video_from_subtitles_window(self):
        def start_export_video_from_subtitles_thread():
            if not self.edit_thread or not self.edit_thread.is_alive():
                self.is_stop_edit = False
                story_type = self.story_type_var.get().strip()

                if story_type == 'comic':
                    export_thread = threading.Thread(target=self.export_comic_video_from_subtitles)
                elif story_type == 'novel':
                    export_thread = threading.Thread(target=self.export_text_story_to_video)
                elif story_type == 'short_story':
                    export_thread = threading.Thread(target=self.export_text_story_to_video, args=(True,))
                export_thread.start()
        
        self.reset()
        self.export_video_window = True
        self.show_window()
        self.setting_window_size()
        self.channel_name_var = self.create_settings_input(text="Xuất video cho kênh", config_key="current_channel", values=self.config["channels"], left=0.3, right=0.7)
        self.language_var = self.create_settings_input(text="Ngôn ngữ", config_key="language_tts", values=self.support_languages, left=0.3, right=0.7)
        self.speed_talk_var = self.create_settings_input(text="Tốc độ giọng đọc", config_key="speed_talk", values=['0.8', '0.9', '1.0', '1.1', '1.2'], left=0.3, right=0.7)
        self.story_type_var = self.create_settings_input(text="Thể loại truyện", values=['comic', 'novel', 'short_story'], left=0.3, right=0.7)
        self.story_type_var.set('novel')
        self.start_idx_var = self.create_settings_input(text="Chỉ số bắt đầu", values=['0', '1', '2'], left=0.3, right=0.7)
        folder_story = self.config.get('folder_story', None)
        start_idx = "0"
        if folder_story:
            temp_output_folder = os.path.join(folder_story, 'temp_output')
            temp_files = get_file_in_folder_by_type(temp_output_folder, '.wav', start_with='temp_audio_', noti=False) or []
            if len(temp_files) > 0:
                err_file = temp_files[-1]
                file_name_err = err_file.replace('.wav', '')
                start_idx = int(file_name_err.split('_')[-1]) + 1
            else:
                audio_files = get_file_in_folder_by_type(temp_output_folder, '.wav', noti=False) or []
                if len(audio_files) == 1 and ' - ' in audio_files[0]:
                    start_idx = "None"
        self.start_idx_var.set(start_idx)
        self.is_merge_var = self.create_settings_input(text="Có gộp video không?", values=['Yes', 'No'], left=0.3, right=0.7)
        self.is_merge_var.set('No')
        self.background_music_volume_var = self.create_settings_input(text="Âm lượng nhạc nền(%)", config_key='background_music_volume', values=['50', '80', '100'], left=0.3, right=0.7)

        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Thư mục chứa truyện", command=self.choose_videos_edit_folder, width=self.width, left=0.3, right=0.7)
        self.videos_edit_folder_var.insert(0, self.config['folder_story'])
        self.output_folder_var = create_frame_button_and_input(self.root,text="Thư mục xuất video", command=self.choose_videos_output_folder, width=self.width, left=0.3, right=0.7)
        self.output_folder_var.insert(0, self.config['output_folder'])
        create_button(self.root, text="Bắt đầu", command=start_export_video_from_subtitles_thread, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def export_video_with_multi_audio_and_background_window(self):
        def start_export_video_from_mp3_thread():
            self.is_stop_edit = False
            export_thread_3 = threading.Thread(target=self.create_video_with_multi_audio_and_background)
            export_thread_3.start()
        
        self.reset()
        self.create_video_with_multi_audio_window = True
        self.show_window()
        self.setting_window_size()
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Thư mục chứa file .txt", command=self.choose_videos_edit_folder, width=self.width, left=0.3, right=0.7)
        self.videos_edit_folder_var.insert(0, self.config['folder_txt'] if 'folder_txt' in self.config else "")
        self.audio_speed_var = self.create_settings_input(text="Tốc độ giọng đọc", config_key="speed_talk", values=['0.8', '0.9', '1.0', '1.1', '1.2'], left=0.3, right=0.7)
        self.audio_speed_var.set(self.config['audio_speed'] if 'audio_speed' in self.config else "1")
        self.audio_volume_var = self.create_settings_input(text="Âm lượng giọng đọc(%)", values=['100', '200', '300'], left=0.3, right=0.7)
        self.audio_volume_var.set(self.config['audio_volume'] if 'audio_volume' in self.config else "100")
        self.background_music_volume_var = self.create_settings_input(text="Âm lượng nhạc nền(%)", config_key='background_music_volume', values=['30', '50', '70'], left=0.3, right=0.7)
        self.background_music_volume_var.set(self.config['background_music_volume'] if 'background_music_volume' in self.config else "20")
        self.image_display_ratio_var = self.create_settings_input(text="Thời lượng hiển thị ảnh(%)", values=['30', '50', '100'], left=0.3, right=0.7)
        self.image_display_ratio_var.set('100')
        self.alpha_var = self.create_settings_input(text="Độ mờ hiển thị ảnh(%)", values=['30', '50', '100'], left=0.3, right=0.7)
        self.alpha_var.set(self.config['alpha'] if 'alpha' in self.config else "50")
        self.random_img_var = self.create_settings_input(text="Thứ tự lấy ảnh", values=['random', 'vị trí', 'sắp xếp theo tên'], left=0.3, right=0.7)
        self.random_img_var.set('sắp xếp theo tên')
        self.is_show_text_var = self.create_settings_input(text="Hiển thị chữ", values=['Yes', 'No'], left=0.3, right=0.7)
        self.is_show_text_var.set('Yes')
        self.text_size_var = self.create_settings_input(text="Kích thước chữ", values=['0.8', '1.0', '1.2'], left=0.3, right=0.7)
        self.text_size_var.set('1.0')
        self.text_position_var = self.create_settings_input(text="Vị trí chữ", values=['bottom', 'center'], left=0.3, right=0.7)
        self.text_position_var.set('bottom')
        create_button(self.root, text="Bắt đầu", command=start_export_video_from_mp3_thread, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)


    def create_video_with_multi_audio_and_background(
        self,
        sample_rate=44100,
        channels=1,
        font_path=r"C:\Windows\Fonts\Calibri.ttf",
        font_size=18,
        base_color=(0, 255, 255),
        highlight_color=(255, 255, 0),
        fps=30,
        random_img=False
    ):
        try:
            input_folder = self.videos_edit_folder_var.get().strip()
            output_folder = os.path.join(input_folder, 'out_videos')
            os.makedirs(output_folder, exist_ok=True)

            # Load and normalize configuration values
            background_music_volume = float(self.background_music_volume_var.get().strip()) / 100
            audio_volume = float(self.audio_volume_var.get().strip()) / 100
            audio_speed = float(self.audio_speed_var.get().strip())
            image_display_ratio = float(self.image_display_ratio_var.get().strip()) / 100
            alpha = float(self.alpha_var.get().strip()) / 100
            try:
                font_size = int(float(self.text_size_var.get().strip()) * font_size)
            except:
                font_size = 18
            is_show_text = self.is_show_text_var.get().strip() == 'Yes'
            is_random_img = self.random_img_var.get().strip()
            if is_random_img == 'random':
                random_img = True
            elif is_random_img == 'vị trí':
                pass
            position = self.text_position_var.get().strip()
            if position != 'bottom':
                position = 'center'
            
            self.config.update({
                'background_music_volume': self.background_music_volume_var.get().strip(),
                'audio_volume': self.audio_volume_var.get().strip(),
                'audio_speed': self.audio_speed_var.get().strip(),
                'image_display_ratio': self.image_display_ratio_var.get().strip(),
                'alpha': self.alpha_var.get().strip()
            })
            self.save_config()

            txt_paths = get_file_in_folder_by_type(input_folder, '.txt') or None
            if not txt_paths:
                print(f"{thatbai} Có lỗi khi xuất video.")
                return
            for txt_file in txt_paths:
                if self.is_stop_export_next_video:
                    return
                start_time = time()
                txt_path = os.path.join(input_folder, txt_file)
                txt_name = os.path.splitext(txt_file)[0]
                print(f"{tot} Bắt đầu xử lý file: {txt_file} --> Vui lòng đợi...")

                # Prepare paths
                audio_concat = f"temp_voice_{txt_name}.wav"
                looped_music = f"temp_music_{txt_name}.wav"
                mixed_audio = f"temp_mix_{txt_name}.mp3"
                bg_video_temp = f"temp_video_bg_{txt_name}.mp4"
                temp_video_path = f"temp_video_{txt_name}.mp4"
                output_path = os.path.join(output_folder, f"{txt_name}.mp4")

                # Load texts
                texts = get_json_data(txt_path, readline=True)
                texts = [t.strip() for t in texts if t.strip()]

                # Audio folder and files
                audio_folder = os.path.join(input_folder, txt_name)
                if not os.path.exists(audio_folder):
                    print(f"Không tìm thấy audio cho {txt_file}")
                    continue
                try:
                    silent_paths = [os.path.join(audio_folder, f) for f in get_file_in_folder_by_type(audio_folder, '.mp3') if f.startswith('silent')]
                except:
                    silent_paths = []
                for silent_path in silent_paths:
                    remove_file(silent_path)
                list_txt_path = os.path.join(audio_folder, 'list.txt')
                remove_file(list_txt_path)

                audio_paths = [os.path.join(audio_folder, f) for f in get_file_in_folder_by_type(audio_folder, '.mp3') if not f.startswith('silent')]

                # Change speed if needed
                if audio_speed != 1.0:
                    audio_paths = [speed_up_audio(path, audio_speed) for path in audio_paths]

                # Image paths
                img_folder = os.path.join(audio_folder, 'img')
                image_paths = []
                if os.path.isdir(img_folder):
                    image_paths = [os.path.join(img_folder, f) for f in get_file_in_folder_by_type(img_folder, '.png')] or []
                    if random_img:
                        random.shuffle(image_paths)

                # Background media
                bg_folder = os.path.join(input_folder, 'background')
                os.makedirs(bg_folder, exist_ok=True)
                
                video_files = get_file_in_folder_by_type(bg_folder, '.mp4')
                bg_video = os.path.join(bg_folder, random.choice(video_files)) if video_files else None
                music_files = get_file_in_folder_by_type(bg_folder, '.mp3')
                bg_music = os.path.join(bg_folder, random.choice(music_files)) if music_files else None
                if not bg_video:
                    print(f"{thatbai} Không tìm thấy file video nền.")
                    return

                # Audio durations and timeline
                audio_durations = [get_audio_duration(p) for p in audio_paths]
                total_duration = sum(audio_durations)
                audio_starts = [sum(audio_durations[:i]) for i in range(len(audio_durations))]

                # 1. Concat voice
                concat_txt = f"temp_concat_{txt_name}.txt"
                with open(concat_txt, 'w', encoding="utf-8") as f:
                    for p in audio_paths:
                        f.write(f"file '{os.path.abspath(p)}'\n")
                run_command_ffmpeg(["ffmpeg","-y","-f","concat","-safe","0","-i",concat_txt,"-c","copy",audio_concat])

                # 2. Loop background music
                if bg_music:
                    run_command_ffmpeg([
                        "ffmpeg","-y","-stream_loop","-1","-i",bg_music,
                        "-t", str(total_duration),"-acodec","pcm_s16le",looped_music
                    ])
                    # 3. Mix audio
                    run_command_ffmpeg([
                        "ffmpeg","-y",
                        "-i",audio_concat,
                        "-i",looped_music,
                        "-filter_complex",
                        f"[0:a]aresample={sample_rate},volume={audio_volume}[va];"
                        f"[1:a]aresample={sample_rate},volume={background_music_volume}[bg];"
                        "[va][bg]amix=inputs=2:duration=first:dropout_transition=0",
                        "-ar",str(sample_rate),"-ac",str(channels),"-c:a","libmp3lame","-q:a","2",mixed_audio
                    ])
                final_audio = mixed_audio if bg_music else audio_concat

                # 4. Prepare background video
                if bg_video and not os.path.exists(bg_video_temp):
                    run_command_ffmpeg([
                        "ffmpeg","-y","-i",bg_video,
                        "-t",str(total_duration),"-vf","scale=1280:720",bg_video_temp
                    ])

                # 5. Render frames
                cap = cv2.VideoCapture(bg_video_temp or '')
                width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
                height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
                out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width,height))
                font = ImageFont.truetype(font_path, font_size)
                total_frames = int(total_duration * fps)
                image_frames = int(total_duration * image_display_ratio * fps)
                # per_img = image_frames // max(len(image_paths),1)
                # image_effects = [random.choice(['left', 'right', 'zoom']) for _ in image_paths]
                min_frame_per_img = 20

                # Số lượng ảnh không vượt quá image_frames // min_frame_per_img
                max_img_displayable = image_frames // min_frame_per_img

                # Chỉ dùng số ảnh phù hợp để đảm bảo mỗi ảnh có đủ frame
                safe_image_paths = image_paths[:max_img_displayable] if max_img_displayable > 0 else []

                # Cập nhật lại các biến liên quan
                image_effects = [random.choice(['left', 'right', 'zoom']) for _ in safe_image_paths]
                per_img = image_frames // max(len(safe_image_paths), 1)
                for frame_idx in range(total_frames):
                    ret, frame = cap.read()
                    if not ret:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        ret, frame = cap.read()
                    if image_paths and frame_idx < image_frames:
                        img_idx = min(frame_idx // per_img, len(image_paths) - 1)
                        img = cv2.imread(image_paths[img_idx])
                        img = cv2.resize(img, (width, height))

                        effect = image_effects[img_idx]
                        local_frame = frame_idx % per_img
                        progress = local_frame / per_img

                        zoom_scale = 1.15  # Zoom mạnh hơn nhẹ
                        pan_max_shift = 60

                        if effect == 'zoom':
                            zoom_factor = 1 + (zoom_scale - 1) * progress
                            new_w = int(width * zoom_factor)
                            new_h = int(height * zoom_factor)
                            resized_img = cv2.resize(img, (new_w, new_h))
                            x_start = (new_w - width) // 2
                            y_start = (new_h - height) // 2
                            cropped_img = resized_img[y_start:y_start+height, x_start:x_start+width]
                        elif effect == 'left':
                            x_shift = int(pan_max_shift * progress)
                            new_w = width + pan_max_shift
                            resized_img = cv2.resize(img, (new_w, height))
                            cropped_img = resized_img[:, x_shift:x_shift+width]
                        elif effect == 'right':
                            x_shift = int(pan_max_shift * progress)
                            new_w = width + pan_max_shift
                            resized_img = cv2.resize(img, (new_w, height))
                            cropped_img = resized_img[:, pan_max_shift - x_shift:pan_max_shift - x_shift + width]
                        else:
                            cropped_img = img  # fallback

                        frame = cv2.addWeighted(frame, 1 - alpha, cropped_img, alpha, 0)

                    if is_show_text:
                        t = frame_idx / fps
                        for i, txt in enumerate(texts):
                            if audio_starts[i] <= t < audio_starts[i] + audio_durations[i]:
                                portion = (t - audio_starts[i]) / audio_durations[i]
                                chars = int(len(txt) * portion)
                                frame = draw_single_text_with_highlight(
                                    frame, txt, chars, font,
                                    base_color=base_color,
                                    highlight_color=highlight_color,
                                    position = position
                                )
                                break
                    out.write(frame)

                cap.release()
                out.release()

                # 6. Merge audio without -shortest, ensure full duration
                cmd_merge = [
                    "ffmpeg","-y",
                    "-i",temp_video_path,
                    "-i",final_audio,
                    "-c:v","h264_nvenc","-preset","fast",
                    "-c:a","aac","-b:a","192k",
                    "-t",str(total_duration),
                    output_path
                ]
                if not run_command_ffmpeg(cmd_merge):
                    for f in [concat_txt,audio_concat,looped_music,mixed_audio,bg_video_temp, temp_video_path]:
                        remove_file(f)
                    print(f"{thatbai} Có lỗi khi xuất video cho file: {txt_path}")
                    return
                # 7. Cleanup temp files
                for f in [concat_txt,audio_concat,looped_music,mixed_audio,bg_video_temp, temp_video_path]:
                    remove_file(f)
                remove_or_move_file(txt_path)
                sleep(1)
                if os.path.exists(output_path):
                    new_path = output_path.replace("--", "'")
                    os.rename(output_path, new_path)
                    print(f"✅ Video created: {new_path} - Time: {time()-start_time:.2f}s")

        except Exception:
            getlog()

    def export_video_from_mp3_and_background_video_window(self):
        def start_export_video_from_mp3_thread():
            self.is_stop_edit = False
            export_thread_2 = threading.Thread(target=self.export_video_with_single_audio_and_background)
            export_thread_2.start()
        
        self.reset()
        self.export_video_from_mp3_window = True
        self.show_window()
        self.setting_window_size()
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Thư mục chứa file mp3", command=self.choose_videos_edit_folder, width=self.width, left=0.3, right=0.7)
        self.videos_edit_folder_var.insert(0, self.config['folder_mp3'] if 'folder_mp3' in self.config else "")
        self.speed_talk_var = self.create_settings_input(text="Tốc độ giọng đọc", config_key="speed_talk", values=['0.8', '0.9', '1.0', '1.1', '1.2'], left=0.3, right=0.7)
        if not self.speed_talk_var.get().strip():
            self.speed_talk_var.insert(0, '1.0')
        self.background_music_volume_var = self.create_settings_input(text="Âm lượng nhạc nền(%)", config_key='background_music_volume', values=['50', '80', '100'], left=0.3, right=0.7)
        create_button(self.root, text="Bắt đầu", command=start_export_video_from_mp3_thread, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def export_video_with_single_audio_and_background(self, audio_type='.mp3'):
        try:
            folder_mp3 = self.videos_edit_folder_var.get().strip()
            try:
                audio_speed = float(self.speed_talk_var.get().strip())
            except:
                audio_speed = 1.0
            try:
                background_music_volume = float(self.background_music_volume_var.get().strip())/100
            except:
                print(f"{thatbai} Âm lượng nhạc nền không hợp lệ.")
                return
            if not check_folder(folder_mp3, noti=False):
                print(f"{thatbai} Thư mục không hợp lệ.")
                return
            background_folder = os.path.join(folder_mp3, 'background')
            os.makedirs(background_folder, exist_ok=True)
            background_music = get_file_in_folder_by_type(background_folder, audio_type) or []
            background_videos = get_file_in_folder_by_type(background_folder, '.mp4') or []
            if not background_videos:
                background_videos = get_file_in_folder_by_type(background_folder, '.png')
            if len(background_videos) == 0:
                print(f"{thatbai} Không tìm thấy file video(.mp4) hoặc ảnh nền(.png).")
                return
            if len(background_music) == 0:
                background_music_path = None
            else:
                background_music_path = os.path.join(background_folder, random.choice(background_music))
            background_path = os.path.join(background_folder, random.choice(background_videos))
            output_folder = os.path.join(folder_mp3, 'out_videos')
            os.makedirs(output_folder, exist_ok=True)
            input_audios = get_file_in_folder_by_type(folder_mp3, audio_type) or []
            for audio_file in input_audios:
                if self.is_stop_export_next_video:
                    return
                input_audio_path = os.path.join(folder_mp3, audio_file)
                name = audio_file.replace(audio_type, '')

                if audio_speed != 1.0:
                    temp_speed_path = os.path.join(folder_mp3, f"speed_{audio_file}")
                    # Giới hạn tốc độ hợp lệ trong khoảng 0.5 đến 2.0
                    if audio_speed > 2.0:
                        adjusted_speed = 2.0
                    elif audio_speed < 0.5:
                        adjusted_speed = 0.5
                    else:
                        adjusted_speed = audio_speed

                    speed_cmd = [ "ffmpeg", "-y", "-i", input_audio_path, "-filter:a", f"atempo={adjusted_speed:.3f}", "-vn", "-c:a", "libmp3lame", "-q:a", "2", temp_speed_path ]
                    if run_command_ffmpeg(speed_cmd):
                        remove_or_move_file(input_audio_path, finish_folder=output_folder)
                        input_audio_path = temp_speed_path
                    else:
                        print(f"{thatbai} Lỗi khi đổi tốc độ audio.")
                        return
                    
                if background_music_path:
                    audio_info = get_audio_info(input_audio_path)
                    duration = audio_info.get('duration', None)
                    sample_rate = audio_info.get('sample_rate', 44100)
                    channels = audio_info.get('channels', 2)
                    if not duration:
                        print(f"Có lỗi khi lấy thông tin audio {audio_file}")
                        return
                    duration = float(duration)
                    print(f"{tot} Đang load nhạc nền và video nền. Vui lòng đợi...")
                    # Lặp và chuyển nhạc nền theo thông số giọng nói
                    looped_music_path = "temp_looped_music.mp3"
                    loop_cmd = [
                        "ffmpeg", "-y",
                        "-stream_loop", "-1",
                        "-i", background_music_path,
                        "-t", str(duration),
                        "-ar", str(sample_rate),
                        "-ac", str(channels),
                        "-c:a", "libmp3lame",
                        "-q:a", "2",  # Chất lượng cao
                        looped_music_path
                    ]
                    if not run_command_ffmpeg(loop_cmd):
                        print(f"{thatbai} Có lỗi khi tạo file {looped_music_path}")
                        return

                    output_video_path = os.path.join(output_folder, audio_file.replace(audio_type, '.mp4'))
                    mixed_audio_path = "mixed_audio.mp3"
                    mix_audio_cmd = [
                        "ffmpeg", "-y",
                        "-i", input_audio_path,
                        "-i", looped_music_path,
                        "-filter_complex",
                        f"[0:a]aresample={sample_rate},volume=3,pan=mono|c0=c0[va]; "
                        f"[1:a]aresample={sample_rate},volume={background_music_volume},pan=mono|c0=c0[bg]; "
                        "[va][bg]amix=inputs=2:duration=first:dropout_transition=0",
                        "-ar", str(sample_rate),
                        "-ac", str(channels),
                        "-c:a", "libmp3lame",
                        "-q:a", "2",  # Giữ chất lượng cao
                        mixed_audio_path
                    ]
                    if run_command_ffmpeg(mix_audio_cmd):
                        remove_or_move_file(input_audio_path, finish_folder=output_folder)
                        remove_file(looped_music_path)
                        input_audio_path = mixed_audio_path

                input_flags = ["-stream_loop", "-1", "-i", background_path] if background_path.lower().endswith('.mp4') else  ["-loop", "1", "-i", background_path]
                if self.device == 'cuda':
                    print("---> Dùng GPU để xuất video...")
                    command = [
                        "ffmpeg", "-y",
                        *input_flags,
                        "-i", input_audio_path,            # đây là mixed audio
                        "-map", "0:v",                     # chỉ lấy video từ đầu vào thứ nhất
                        "-map", "1:a",                     # chỉ lấy audio từ mixed_audio
                        "-t", str(duration),
                        "-c:v", "h264_nvenc", "-cq", "30", "-pix_fmt", "yuv420p",
                        "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-threads", "4",
                        output_video_path
                    ]
                else:
                    command = [
                        "ffmpeg", "-y",
                        *input_flags,
                        "-i", input_audio_path,
                        "-map", "0:v",
                        "-map", "1:a",
                        "-t", str(duration),
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-tune", "stillimage",
                        "-c:a", "aac", "-b:a", "192k",
                        "-shortest", "-threads", "4",
                        output_video_path
                    ]
                if run_command_ffmpeg(command, False):
                    remove_file(mixed_audio_path)
                    txt_path = os.path.join(folder_mp3, f"{name}.txt")
                    if os.path.exists(txt_path):
                        remove_or_move_file(txt_path, finish_folder=output_folder)
                    print(f'{thanhcong} Xuất video thành công: {output_video_path}')
        except:
            getlog()

    def text_to_speech_with_xtts_v2(self, txt_path, speaker_wav, language, output_path=None, min_lenth_text=35, max_lenth_text=250, readline=True, tts_list=[], start_idx=0, end_text="", first_text="", image_path=None, final_folder=None, mid_text=None, background_music_path=None, background_music_volume=0.5):
        try:
            self.stop_audio_file = None
            if not output_path:
                print(f'Chưa có tên file sau khi xuất video')
                return False
            output_folder = os.path.dirname(output_path) if output_path else os.getcwd()
            # Đọc và làm sạch nội dung văn bản
            if txt_path.endswith('.txt'):
                text = get_json_data(txt_path, readline=False)
            else:
                text = txt_path
            
            text = cleaner_text(text, language=language)
            if readline:
                lines = text.split('\n')
                sentences = []
                for line in lines:
                    if language == 'vi':
                        sub_sentences = line.split('.')
                    else:
                        line = re.sub(r'(?<=[^\s])\.(?=\w)', '. ', line)
                        sub_sentences = line.split('. ')
                    for sub in sub_sentences:
                        sub = sub.strip()
                        if sub and sub != '.' and sub != '…':
                            sentences.append(f'{sub}.')

                total_texts = []
                if first_text:
                    total_texts.append(first_text.lower())
                temp_text = ""
                temp_audio_files = []  # Danh sách chứa các file audio nhỏ

                for id, sentence in enumerate(sentences):
                    if id == int(len(sentences)/2) and mid_text:
                        total_texts.append(mid_text)

                    sentence = sentence.strip()
                    if not sentence:
                        continue
                    if temp_text:
                        sentence = f"{temp_text} {sentence}"
     
                    sentence = re.sub(r'^\.+\s*', '', sentence)
                    if not sentence.endswith('.') and not sentence.endswith(','):
                        sentence = f'{sentence}.'
                    sentence = cleaner_text(sentence, language=language)

                    if len(sentence) > max_lenth_text:
                        total_texts.extend(split_text_into_chunks(sentence, max_lenth_text))
                        temp_text = ""
                    else:
                        if len(sentence) < min_lenth_text and sentence != sentences[-1].strip():
                            temp_text = sentence
                            continue
                        else:
                            temp_text = ""
                        if len(sentence) >= min_lenth_text:
                            total_texts.append(sentence)
                        else:
                            if sentence != sentences[-1].strip():
                                print(f'{thatbai} Dữ liệu nhỏ hơn {min_lenth_text} ký tự: {sentence}')
                                return

                if end_text:
                    if len(sentence) < min_lenth_text:
                        end_text = f'{sentence} {end_text}'
                    if len(end_text) > max_lenth_text:
                        total_texts.extend(split_text_into_chunks(end_text, max_lenth_text))
                    else:
                        total_texts.append(end_text.lower())
                print(f'  --->  Tổng số câu cần xử lý: {len(total_texts)}')
                list_file_path = "audio_list.txt"
                list_videos = []
                if start_idx >= len(total_texts):
                    temp_files = get_file_in_folder_by_type(output_folder, '.wav', start_with='temp_audio_') or []
                    for temp in temp_files:
                        temp_path = os.path.join(output_folder, temp)
                        temp_audio_files.append(temp_path)
                else:
                    # Hàng đợi lưu các đoạn văn bản cần xử lý
                    task_queue = queue.Queue()
                    current_text_chunk = ""
                    for idx, text_chunk in enumerate(total_texts):
                        temp_audio_path = os.path.join(output_folder, f"temp_audio_{idx}.wav")
                        if idx < start_idx:
                            if os.path.exists(temp_audio_path):
                                temp_audio_files.append(temp_audio_path)
                            continue
                        current_text_chunk += text_chunk
                        if text_chunk and text_chunk != '.' and text_chunk != '..' and text_chunk != '. .' and text_chunk != ',' and text_chunk != ',,' and text_chunk != '-' and text_chunk != ',,,':
                            if len(current_text_chunk) >= min_lenth_text:
                                task_queue.put((current_text_chunk, temp_audio_path))
                                temp_audio_files.append(temp_audio_path)
                                current_text_chunk = ""
                    
                    def process_tts(tts, speaker_wav, language):
                        while not task_queue.empty():
                            try:
                                text_chunk, temp_audio_path = task_queue.get_nowait()
                                text_chunk = cleaner_text(text=text_chunk, language=language)
                                if text_chunk.startswith(',. '):
                                    text_chunk = text_chunk[3:]
                                elif text_chunk.startswith('. ') or text_chunk.startswith(',.') or text_chunk.startswith('..'):
                                    text_chunk = text_chunk[2:]
                                elif text_chunk.startswith('.') or text_chunk.startswith(',') or text_chunk.startswith('-'):
                                    text_chunk = text_chunk[1:]
                                elif text_chunk.startswith("' "):
                                    text_chunk = text_chunk[2:]
                                elif text_chunk.startswith("'"):
                                    text_chunk = text_chunk[1:]
                                if text_chunk.endswith("'.") or text_chunk.endswith(".."):
                                    text_chunk = f'{text_chunk[:-2]}.'
                                try:
                                    torch.cuda.empty_cache()
                                    tts.tts_to_file(text=text_chunk, speaker_wav=speaker_wav, language=language, file_path=temp_audio_path, split_sentences=False)
                                    if not os.path.exists(temp_audio_path):
                                        print(f"{thatbai} chuyển văn bản thành giọng nói thất bại --> {text_chunk}")
                                        return False
                                    
                                    mix_audio_path = mix_audio_with_background(temp_audio_path, background_music_path, background_music_volume)
                                    if image_path:
                                        output_video_path = export_video_from_audio_image_text(mix_audio_path, image_path, text_chunk)
                                        if output_video_path and os.path.exists(output_video_path):
                                            remove_file(mix_audio_path)
                                            list_videos.append(output_video_path)
                                except:
                                    try:
                                        getlog()
                                        self.stop_audio_file = temp_audio_path
                                        sleep(10)
                                        break
                                    except:
                                        print(f'{thatbai} Xuất file tạm {temp_audio_path} thất bại !')
                                        print(f'{thatbai} text: {text_chunk}')
                                        self.stop_audio_file = temp_audio_path
                                        break
                                print(f'Đã xuất file tạm {temp_audio_path}')
                            except:
                                getlog()
                                self.stop_audio_file = temp_audio_path
                                break

                    # Tạo các luồng để xử lý song song
                    list_threads = []
                    for tts in tts_list:
                        list_threads.append(threading.Thread(target=process_tts, args=(tts, speaker_wav, language)))
                    for thread in list_threads:
                        thread.start()
                    for thread in list_threads:
                        thread.join()

                if len(list_videos) > 0:
                    txt_name = os.path.basename(txt_path).replace('.txt', '')
                    if merge_videos_use_ffmpeg(videos_folder=output_folder, file_name=txt_name, output_folder=final_folder):
                        for video in list_videos:
                            remove_file(video)
                        for temp_audio_file in temp_audio_files:
                            if os.path.exists(temp_audio_file):
                                remove_file(temp_audio_file)
                        if os.path.exists(list_file_path):
                            remove_file(list_file_path)
                        remove_or_move_file(txt_path)
                        return True
                    else:
                        return False
                if self.stop_audio_file:
                    return False
                if len(temp_audio_files) == 0:
                    return True
                    
                if not os.path.exists(output_path):
                    with open(list_file_path, "w", encoding="utf-8") as f:
                        for audio_file in temp_audio_files:
                            if os.path.exists(audio_file):
                                f.write(f"file '{audio_file}'\n")

                    ffmpeg_command = ["ffmpeg", "-f", "concat", "-safe", "0", "-i", list_file_path, "-c", "copy", output_path]
                    run_command_ffmpeg(ffmpeg_command, hide=True)

                for temp_audio_file in temp_audio_files:
                    if os.path.exists(temp_audio_file):
                        remove_file(temp_audio_file)
                if os.path.exists(list_file_path):
                    remove_file(list_file_path)
            else:
                tts_list[0].tts_to_file( text=text, speaker_wav=speaker_wav, language=language, file_path=output_path, split_sentences=True )
            print(f'Xuất file tạm: {output_path}')
            return True
        except:
            getlog()
            return False
    
    def export_text_story_to_video(self, is_short_story=False):
        try:
            start_time = time()
            is_merge_videos = False
            start_idx = self.start_idx_var.get().strip()
            channel_name = self.channel_name_var.get().strip()
            language = self.language_var.get().strip()
            try:
                background_music_volume = float(self.background_music_volume_var.get().strip())/100
            except:
                print(f"{thatbai} Chọn âm lượng nhạc nền không hợp lệ.")
                return
            model_path = os.path.join(current_dir, "models", "last_version_en")
            first_text = mid_text = end_text = None
            if channel_name:
                first_text = f"Welcome to {channel_name}! Enjoy the story, and don't forget to like and subscribe to support the channel."
                mid_text = f"You're listening to a story on {channel_name}. Don't forget to subscribe to follow the next episodes."
                end_text = f"Thank you for listening! If you enjoyed the story, don't forget to like and subscribe. See you next time!"
            if language == 'vi':
                speaker = None
                model_path = os.path.join(current_dir, "models", "last_version_vi")
                if channel_name:
                    first_text = f"Chào mừng bạn đến với {channel_name}, kênh chuyên review các bộ truyện dịch, hãy like và đăng ký để giúp kênh ngày càng phát triển hơn nhé."
                    mid_text = f"Bạn đang nghe truyện tại {channel_name}, đừng quên đăng ký kênh để theo dõi các tập tiếp theo nhé."
                    end_text = f"Cảm ơn bạn đã xem hết video. Nhớ like, đăng ký kênh và ủng hộ mình ở các tập tiếp theo nhé."
            else:
                try:
                    language, speaker = language.strip().split('-')
                except:
                    language, speaker = 'en', 'brian'

            xtts_config_path = os.path.join(model_path, "config.json")

            speed_talk = self.speed_talk_var.get().strip()
            if speed_talk:
                try:
                    speed_talk = float(speed_talk)
                except:
                    speed_talk = 1.0
            speaker_wav = get_ref_speaker_by_language(language, speaker)
            if not speaker_wav:
                return
            
            is_merge = self.is_merge_var.get().strip() == "Yes"
            folder_story = self.videos_edit_folder_var.get().strip()
            if not check_folder(folder_story):
                print(f"{thatbai} Thư mục {folder_story} không hợp lệ hoặc không tồn tại.")
                return False
            background_folder = folder_story
            output_folder = self.output_folder_var.get().strip()
            os.makedirs(output_folder, exist_ok=True)
            self.config["language_tts"] = self.language_var.get().strip()
            self.config["speed_talk"] = str(speed_talk)
            self.config["current_channel"] = channel_name
            self.config["output_folder"] = output_folder
            self.config["folder_story"] = folder_story
            self.config["background_music_volume"] = self.background_music_volume_var.get().strip()
            if channel_name not in self.config["channels"]:
                self.config["channels"].append(channel_name)
            self.save_config()
            txt_files = get_file_in_folder_by_type(folder_story, file_type='.txt') or []
            if len(txt_files) == 0:
                print(f'{thatbai} Không tìm thấy file .txt chứa nội dung truyện trong thư mục {folder_story}')
                return False
            is_mp4 = True
            background_musics = get_file_in_folder_by_type(background_folder, '.wav', noti=False) or []
            if not background_musics:
                background_musics = get_file_in_folder_by_type(background_folder, '.mp3', noti=False) or []
            images = get_file_in_folder_by_type(background_folder, file_type='.mp4', noti=False) or []
            if len(images) == 0:
                images = get_file_in_folder_by_type(background_folder, file_type='.png', noti=False) or []
                if len(images) == 0:
                    background_folder = os.path.join(current_dir, 'background')
                    images = get_file_in_folder_by_type(background_folder, file_type='.mp4') or []
                    if not images:
                        print(f"{thatbai} Phải có ít nhất 1 video nền(.mp4) hoặc 1 ảnh (.png) trong thư mục {folder_story} hoặc thư mục {background_folder}")
                        return False
                    if not background_musics:
                        background_musics = get_file_in_folder_by_type(background_folder, '.wav') or []
                is_mp4 = False
            temp_output_folder = os.path.join(folder_story, 'temp_output')
            os.makedirs(temp_output_folder, exist_ok=True)
            
            file_name = ""
            start_idx = int(start_idx) if start_idx.isdigit() else None
            num_gpus = torch.cuda.device_count() if torch.cuda.is_available() else 0
            
            tts_list = []
            # device = f"cuda:0" if torch.cuda.is_available() else 'cpu'

            if num_gpus == 0:
                self.device = 'cpu'
            if start_idx is not None:
                tts_list.append(TTS(model_path=model_path, config_path=xtts_config_path).to(self.device))

            print(f"Sử dụng {len(tts_list)} mô hình: {num_gpus} trên GPU, {len(tts_list) - num_gpus} trên CPU")
            
            if len(background_musics) > 0:
                mp3_file = random.choice(background_musics)
                mp3_path = os.path.join(background_folder, mp3_file)
                wav_path = os.path.join(background_folder, mp3_path[:-4] + ".wav")  # Đổi phần mở rộng từ .mp3 thành .wav
                # Cấu hình lệnh ffmpeg
                ffmpeg_cmd = [
                    "ffmpeg", 
                    "-y",  # ghi đè file nếu đã tồn tại
                    "-i", mp3_path,  # đường dẫn đến file MP3
                    "-ac", "1",  # 1 kênh âm thanh (mono)
                    "-ar", "24000",  # tần số mẫu (sampling rate) là 24kHz
                    "-sample_fmt", "s16",  # định dạng mẫu âm thanh (16-bit)
                    wav_path  # đường dẫn file WAV đầu ra
                ]
                if run_command_ffmpeg(ffmpeg_cmd):
                    background_musics = get_file_in_folder_by_type(folder_story, '.wav') or []

            for i, txt_file in enumerate(txt_files):
                current_image = os.path.join(background_folder, random.choice(images))
                background_music_path = os.path.join(background_folder, random.choice(background_musics)) if background_musics else None
                one_file_start_time = time()
                print(f'  --->  Bắt đầu chuyển text sang audio: {txt_file}')
                t = time()
                file_name = txt_file.replace('.txt', '')
                txt_path = os.path.join(folder_story, txt_file)

                if speed_talk == 1.0:
                    temp_audio_path = os.path.join(temp_output_folder, f'{file_name}.wav')
                else:
                    temp_audio_path = os.path.join(temp_output_folder, f'origin_{file_name}.wav')
                if is_mp4:
                    img_path = os.path.join(folder_story, f'{file_name}.mp4')
                else:
                    img_path = os.path.join(folder_story, f'{file_name}.png')
                if os.path.exists(img_path):
                    current_image = img_path
                else:
                    img_path = current_image
                
                if is_short_story:
                    if self.text_to_speech_with_xtts_v2(txt_path, speaker_wav, language, output_path=temp_audio_path, tts_list=tts_list, start_idx=start_idx, first_text=None, end_text=None, image_path=img_path, final_folder=output_folder, background_music_path=background_music_path, background_music_volume=background_music_volume):
                        print(f'{thanhcong} Tổng thời gian xử lý file {txt_file}: {time() - one_file_start_time}s')
                        continue
                    else:
                        print(f"{thatbai} Thời gian lỗi {datetime.now()}")
                        return False
                else:
                    if not self.text_to_speech_with_xtts_v2(txt_path, speaker_wav, language, output_path=temp_audio_path, tts_list=tts_list, start_idx=start_idx, first_text=first_text, end_text=end_text, mid_text=mid_text):
                        print(f"{thatbai} Thời gian lỗi {datetime.now()}")
                        return False
                start_idx = 0
                if speed_talk == 1.0:
                    output_audio_path = temp_audio_path
                else:
                    output_audio_path = os.path.join(temp_output_folder, f'{file_name}.wav')
                    if not change_audio_speed(temp_audio_path, output_audio_path, speed_talk):
                        output_audio_path = temp_audio_path
                    else:
                        remove_file(temp_audio_path)

                if os.path.exists(output_audio_path):
                    print(f'{thanhcong} Thời gian chuyển file {txt_file} sang audio là {time() - t}s')
                    if img_path and os.path.exists(img_path):
                        is_merge_videos = True
                        output_video_path = os.path.join(output_folder, f'{file_name}.mp4')
                        print("Đang ghép ảnh và audio thành video. Hãy đợi đến khi có thông báo hoàn thành ...")

                        def is_static_image(path):
                            return path.lower().endswith(('.jpg', '.jpeg', '.png'))

                        def is_gif(path):
                            return path.lower().endswith('.gif')

                        def is_video(path):
                            return path.lower().endswith(('.mp4', '.mov', '.mkv', '.avi'))

                        if is_static_image(img_path):
                            input_flags = ["-loop", "1", "-i", img_path]
                        elif is_gif(img_path) or is_video(img_path):
                            input_flags = ["-stream_loop", "-1", "-i", img_path]  # lặp vô hạn
                        else:
                            print(f"{thatbai} Định dạng không hỗ trợ.")
                            return
                        
                        output_audio_path = mix_audio_with_background(output_audio_path, background_music_path, background_music_volume)
                        audio_info = get_audio_info(output_audio_path) or {}
                        duration = audio_info.get('duration', None)
                        if not duration:
                            print(f"{thatbai} Không lấy được thông tin audio {output_audio_path}")
                            return

                        if self.device == 'cuda':
                            print("---> Dùng GPU để xuất video...")
                            command = [
                                "ffmpeg", "-y",
                                *input_flags,
                                "-i", output_audio_path,
                                "-map", "0:v", "-map", "1:a",
                                "-t", str(duration),
                                "-c:v", "h264_nvenc", "-cq", "30",
                                "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", "128k",
                                "-shortest", "-threads", "4",
                                output_video_path
                            ]
                        else:
                            print("---> Dùng CPU để xuất video...")
                            command = [
                                "ffmpeg", "-y",
                                *input_flags,
                                "-i", output_audio_path,
                                "-map", "0:v", "-map", "1:a",
                                "-t", str(duration),
                                "-c:v", "libx264", "-tune", "stillimage",
                                "-pix_fmt", "yuv420p",
                                "-c:a", "aac", "-b:a", "128k",
                                "-shortest", "-threads", "4",
                                output_video_path
                            ]
                        if run_command_ffmpeg(command, False):
                            print(f'{thanhcong} Xuất video thành công: {output_video_path}')
                            remove_or_move_file(txt_path)
                            remove_file(output_audio_path)
                            print(f'Tổng thời gian xử lý file {txt_file} là {time() - one_file_start_time}s')
                            if self.is_stop_export_next_video:
                                print(f'  --> Đã dừng xuất video !!!')
                                return True

                else:
                    print(f'{thatbai} xuất file {txt_path} sang audio không thành công ---> Dừng chương trình !!!')
                    return False

            if is_merge:
                export_file_name = f"{txt_files[0].replace('.txt', '')} - {txt_files[-1].replace('.txt', '')}"
                if is_merge_videos:
                    merge_videos_use_ffmpeg(output_folder, export_file_name, hide=False)
                    print("  -->  Xuất video hoàn tất.")
                else:
                    merge_audio_use_ffmpeg(output_folder, export_file_name)
                    print("  -->  Xuất audio hoàn tất.")

            print(f'Tổng thời gian xử lý: {time() - start_time}s')
            self.stop_audio_file = None
            return True
        except:
            getlog()
            return False

    def export_comic_video_from_subtitles(self):
        try:
            main_folder = self.videos_edit_folder_var.get()
            main_txt_path = os.path.join(main_folder, 'total_video_file.txt')
            if not check_folder(main_folder):
                return
            channel_name = self.channel_name_var.get().strip()
            language = self.language_var.get().strip()
            model_path = os.path.join(current_dir, "models", "last_version_en")
            end_text = f"You are watching stories on the {channel_name} channel. Don't forget to like and subscribe so you won't miss the next episodes!"
            if language == 'vi':
                end_text = f"Bạn đang xem truyện tại kênh {channel_name}, đừng quên like và đăng ký để không bỏ lỡ các tập tiếp theo nhé."
                model_path = os.path.join(current_dir, "models", "last_version_vi")  
            xtts_config_path = os.path.join(model_path, "config.json")

            speed_talk = self.speed_talk_var.get().strip()
            if speed_talk:
                try:
                    speed_talk = float(speed_talk)
                except:
                    speed_talk = 1.0
            
            chapters_folder = get_file_in_folder_by_type(main_folder, file_type="", start_with='chuong') or get_file_in_folder_by_type(main_folder, file_type="", start_with='chương') or []
            if len(chapters_folder) == 0:
                print(f'Không tìm thấy danh sách chương truyện trong thư mục {main_folder}')
                return

            self.xtts = TTS(model_path=model_path, config_path=xtts_config_path).to(device)
            for chapter_folder in chapters_folder:
                print(f'Bắt đầu xử lý --> {chapter_folder} ...')
                chapter_folder = os.path.join(main_folder, chapter_folder)
                self.processing_subtitle_file_and_export_video(chapter_folder, language=language, end_text=end_text, speed_talk=speed_talk, main_file_path=main_txt_path)
                if self.is_stop_edit:
                    break
            self.xtts = None
        except:
            getlog()
            print(f"{thatbai} Có lỗi trong quá trình xử lý các file phụ đề")
            self.xtts = None

    def processing_subtitle_file_and_export_video(self, chapter_folder, language='vi', speed_talk=1.0, end_text=None, main_file_path=None, min_lenth_text=30, max_lenth_text=250):
        try:
            file_name = os.path.basename(os.path.normpath(chapter_folder))
            subtitle_path = os.path.join(chapter_folder, f'{file_name}_{language}.txt')
            if not os.path.exists(subtitle_path):
                print(f'{thatbai} Không tìm thấy file {subtitle_path}')
                return
            temp_folder = os.path.join(chapter_folder, 'temp_folder')
            os.makedirs(temp_folder, exist_ok=True)

            with open(subtitle_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            lines = [llll.strip() for llll in lines if llll.strip()]
            cnt, idx = 0, 0
            max_height = 1100
            type_image = 'png'
            first_image_path = None
            entries = []  # Lưu danh sách các entry ảnh + nội dung

            current_image_name = None
            total_content = ""
            first_number = 0
            while idx < len(lines):
                line = lines[idx].strip()
                if line.isdigit():  # Bắt đầu một ảnh mới
                    if int(line) == 0 or int(line) <= first_number or int(line) > first_number + 10:
                        idx += 1
                        continue

                    # Nếu có ảnh trước thì lưu lại, kể cả khi không có nội dung
                    if current_image_name:
                        cleaned_content = total_content.strip()
                        if cleaned_content:
                            if not cleaned_content.endswith('.') and not cleaned_content.endswith(','):
                                cleaned_content += '.'
                            entries.append((current_image_name, cleaned_content))
                        else:
                            entries.append((current_image_name, None))

                    total_content = ""

                    image_number = line
                    image_name = f"{image_number}.{type_image}"
                    image_path = os.path.join(chapter_folder, image_name)

                    # Kiểm tra nếu không tồn tại ảnh, thử với phần mở rộng khác
                    if not os.path.exists(image_path):
                        type_image = 'jpg'
                        image_name = f"{image_number}.{type_image}"
                        image_path = os.path.join(chapter_folder, image_name)

                        if not os.path.exists(image_path):
                            if first_image_path:
                                image_path = first_image_path

                    if not image_path or not os.path.exists(image_path):
                        print(f'{thatbai} Không tìm thấy ảnh {image_name} trong thư mục {chapter_folder}')
                        return

                    current_image_name = image_name
                    first_image_path = image_path
                    idx += 1
                    first_number = int(line)
                else:
                    content = cleaner_text(line, language=language)
                    if not content:
                        idx += 1
                        continue
                    if content.endswith(' .'):
                        content = f"{content[:-2]}."
                    elif not content.endswith('.') and not content.endswith(','):
                        content += ','
                    total_content += f" {content}"
                    idx += 1

            # Sau vòng lặp, thêm ảnh cuối cùng (dù có nội dung hay không)
            if current_image_name:
                cleaned_content = total_content.strip()
                if cleaned_content:
                    if not cleaned_content.endswith('.') and not cleaned_content.endswith(','):
                        cleaned_content += '.'
                    if len(cleaned_content) < min_lenth_text and end_text:
                        cleaned_content += f" {end_text}"
                    entries.append((current_image_name, cleaned_content.strip()))
                else:
                    entries.append((current_image_name, None))

            cnt = 0
            for image_name, content in entries:
                if content:
                    content = cleaner_text(content, language=language)
                    if len(content) > max_lenth_text:
                        contents = split_text_into_chunks(content, max_lenth_text)
                    elif len(content) < min_lenth_text:
                        for i in range(35):
                            content = content + ' '
                            if len(content) >= min_lenth_text:
                                content = content + '.'
                                break
                        contents = [content]
                    else:
                        contents = [content]
                    merge_audio_path = os.path.join(temp_folder, f"{image_name.split('.')[0]}.wav")
                    merge_audio_path = self.get_audio_for_all_text_of_image(contents, temp_folder, language=language, speed_talk=speed_talk, merge_audio_path=merge_audio_path)
                else:
                    merge_audio_path = None
                image_path = os.path.join(chapter_folder, image_name)
                img, image_height, image_width = get_image_size_by_cv2(image_path)
                if image_height < max_height:
                    scale_factor = max_height / image_height
                    new_width = int(image_width * scale_factor)
                    resized_image_path = os.path.join(temp_folder, f"{cnt}_resized.png")
                    resize_command = ['ffmpeg', '-y', '-i', image_path, '-vf', f"scale={new_width}:{max_height}", resized_image_path]
                    run_command_ffmpeg(resize_command, True)
                    image_path = resized_image_path

                video_path = f"{temp_folder}/video_{image_name.split('.')[0]}.mp4"
                if process_image_to_video_with_movement(image_path, merge_audio_path, video_path, hide=True):
                    print(f"{thanhcong} Xuất thành công video {video_path}")
                else:
                    print(f"{thatbai} có lỗi trong quá trình xuất video {video_path}")
                    return
                cnt += 1

            merge_videos_use_ffmpeg(temp_folder, f"{file_name}_{language}", hide=False)
            with open(main_file_path, 'w', encoding='utf-8') as main_file:
                main_file.write(f"file '{video_path}'\n")

        except:
            getlog()

    def get_audio_for_all_text_of_image(self, contents, temp_folder, language='vi', speed_talk='1', merge_audio_path='merge.wav'):
        try:
            if not merge_audio_path:
                return None
            audio_paths = []
            cnt = 0
            for text in contents:
                audio_path = os.path.join(temp_folder, f"{cnt}.wav")
                if text.endswith(','):
                    text = f"{text[:-1]}."

                if not text_to_audio_with_xtts(self.xtts, text, audio_path, language):
                    print(f"{thatbai} Không thể TTS: {text}")
                    return None
                # Thay đổi tốc độ nói nếu cần
                if speed_talk != 1.0:
                    speed_audio_path = os.path.join(temp_folder, f"{cnt}_speed.wav")
                    if change_audio_speed(audio_path, speed_audio_path, speed_talk):
                        if os.path.exists(speed_audio_path):
                            remove_file(audio_path)
                            audio_path = speed_audio_path
                if len(contents) == 1:
                    return audio_path
                audio_paths.append(audio_path)
                cnt += 1
            # Tạo file danh sách cho ffmpeg
            concat_list_path = os.path.join(temp_folder, "concat_list.txt")
            with open(concat_list_path, "w", encoding="utf-8") as f:
                for path in audio_paths:
                    full_path = os.path.abspath(path).replace("\\", "/")
                    f.write(f"file '{full_path}'\n")
            cmd = [ "ffmpeg", "-f", "concat", "-safe", "0", "-i", concat_list_path, "-c", "copy", merge_audio_path ]
            if run_command_ffmpeg(cmd):
                remove_file(concat_list_path)
                for audio in audio_paths:
                    remove_file(audio)
                return merge_audio_path
        except:
            getlog()
        return None

    def open_download_image_window(self):
        def start_thread_download_image_from_truyenqqto():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                self.download_thread = threading.Thread(target=self.start_download_image_from_truyenqqto)
                self.download_thread.start()
        
        self.reset()
        self.download_image_from_truyenqqto = True
        self.show_window()
        self.setting_window_size()
        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu ảnh", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        self.chapters_var = create_frame_label_and_input(self.root, text="Tải chương truyện cụ thể", place_holder="22,23,26,28...", width=self.width, left=0.4, right=0.6)
        self.download_image_from_truyenqqto_var = create_frame_button_and_input(self.root,text="Tải các chương truyện", command=start_thread_download_image_from_truyenqqto, place_holder="Link danh sách chương", width=self.width, left=0.4, right=0.6)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def start_download_image_from_truyenqqto(self):
        # nettruyenssr.com, truyenqqto.com
        try:
            main_folder = self.download_folder_var.get()
            if not main_folder.strip():
                print(f'Hãy chọn thư mục chứa truyện tải về!')
                return
            if not check_folder(main_folder):
                return
            chapter_url = self.download_image_from_truyenqqto_var.get()
            current_chapter = self.chapters_var.get().strip()
            if '<idx>' in chapter_url:
                current_chapters = current_chapter.split('-') if '-' in current_chapter else []
                if not current_chapters:
                    print(f"Hãy nhập chương muốn tải. Ví dụ: 1-20 (chương 1 đến chương 20)")
                    return
            else:
                current_chapters = current_chapter.split(',') if ',' in current_chapter else []


            if not chapter_url:
                self.noti("Hãy nhập link truyện muốn tải trước.")
                return

            self.driver = get_driver()
            sleep(3)
            if 'nettruyen' in chapter_url:
                sleep(3.5)

            def get_list_chapter():
                if 'truyenqqto.com' in chapter_url:
                    return get_element_by_text(self.driver, "Chương ", tag_name="a", multiple=True)
                elif '//nettruyen' in chapter_url:
                    def click_view_more():
                        def click_ADS():
                            try:
                                xpath = get_xpath_by_multi_attribute('body', ['id="ctl00_Body"'])
                                ads_ele = get_element_by_xpath(self.driver, xpath)
                                if ads_ele:
                                    ads_ele.click()
                                    sleep(1)
                                    ads_ele.click()
                                    sleep(1)
                                sleep(1)
                            except:
                                pass
                        xpath = get_xpath('a', 'view-more', contain=True)
                        ele = get_element_by_xpath(self.driver, xpath)
                        if ele:
                            scroll_into_view(self.driver, ele)
                            sleep(1)
                            try:
                                click_ADS()
                                sleep(6)
                                ele.click()
                            except:
                                print("Hãy đóng quảng cáo để tải !!!")
                                sleep(20)
                                ele.click()
                            sleep(1)
                    click_view_more()
                    return get_element_by_text(self.driver, "Chapter ", tag_name="a", multiple=True, not_contain_attribute='title')
            
            def get_all_image_of_chapter(folder, link=None, session=None):
                if not link:
                    print("Không tìm thấy link tải truyện.")
                    return
                if not session:
                    return
                self.driver.get(link)
                sleep(4)
                if 'asura' in chapter_url:
                    xpath = "//img[contains(@alt, 'chapter page')]"
                    eles = get_element_by_xpath(self.driver, xpath, multiple=True)
                elif 'manhuafast' in chapter_url:
                    xpath = "//img[substring(@src, string-length(@src) - 3) = '.jpg']"
                    eles = get_element_by_xpath(self.driver, xpath, multiple=True)
                else:
                    xpath = '//div[@class="page-chapter"]//img'
                    eles = get_element_by_xpath(self.driver, xpath, multiple=True)
                if eles:
                    idx = 0

                    for ele in eles:
                        link_image = ele.get_attribute('src')
                        # Bỏ qua các liên kết không hợp lệ
                        if 'imgur' in link_image or 'data:image' in link_image or '/tmp/' in link_image:
                            continue
                        idx += 1
                        image_name = f'{idx}.jpg'
                        img_path = os.path.join(folder, image_name)
                        try:
                            response = session.get(link_image, timeout=10)
                            if response.status_code == 200:
                                with open(img_path, 'wb') as file:
                                    file.write(response.content)
                                print(f'{thanhcong} Tải ảnh thành công: {image_name}')
                            else:
                                print(f"{thatbai} Tải ảnh không thành công (status {response.status_code}) --> {image_name}")
                        except:
                            getlog()

            list_linkes = []
            end_link = chapter_url.split('/')[-1].strip()
            if '<idx>' in chapter_url:
                try:
                    start_chap = int(current_chapters[0])
                    end_chap = int(current_chapters[1])
                except:
                    print(f"Số chương tải không hợp lệ, định dạng 1-20")
                    return
                for current_chap in range(start_chap, end_chap+1):
                    link = chapter_url.replace('<idx>', str(current_chap))
                    list_linkes.append(link)
            elif end_link.startswith('chapter-') or end_link.endswith('.html'):
                list_linkes.append(chapter_url)
            else:
                link_chapters_ele = get_list_chapter()
                if not link_chapters_ele:
                    print("không tìm thấy danh sách chương")
                link_chapters_ele.reverse()
                
                for link_a in link_chapters_ele:
                    link = link_a.get_attribute('href') or ""
                    if link and link not in list_linkes:
                        if len(current_chapters) > 0 and current_chapters[0]:
                            cur_chap = link.split('chapter-')[-1]
                            cur_chap = cur_chap.strip().split('.')[0]
                            if cur_chap not in current_chapters:
                                continue
                        list_linkes.append(link)
            # driver.get(chapter_url)
            if len(list_linkes) > 0:
                # merge_img_folder = os.path.join(main_folder, "merge_img_folder")
                # os.makedirs(merge_img_folder, exist_ok=True)
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
                }
                if 'truyenqqto.com' in chapter_url:
                    headers['referer'] = 'https://truyenqqto.com/'
                with requests.Session() as session:
                    session.headers.update(headers)  # Cập nhật headers dùng chung cho mọi request
                    for idx, link in enumerate(list_linkes):
                        name = link.split('-')[-1].strip() or idx
                        if 'asura' in link:
                            name = link.split('/')[-1].strip() or idx
                        elif 'manhuafast' in link:
                            name = name.replace('/', '')
                        elif '.' in name:
                            name = name.split('.')[0].strip()
                        print(f' --> Bắt đầu tải chương {name}')
                        folder = os.path.join(main_folder, f'chuong {name}')
                        os.makedirs(folder, exist_ok=True)
                        get_all_image_of_chapter(folder, link, session)
                        # output_folder = os.path.join(merge_img_folder, f'chuong {name}')
                        # merge_images(folder, output_folder)

            self.close_driver()
        except:
            getlog()
            print("Có lỗi trong quá trình tải ảnh --> Dừng tải !!!")
        finally:
            self.close_driver()

    def open_other_download_video_window(self):
        def start_download_by_video_url():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                self.download_thread = threading.Thread(target=self.download_video_by_video_url)
                self.download_thread.start()
        
        self.reset()
        self.is_other_download_window = True
        self.show_window()
        self.setting_window_size()
        self.is_start_app = False
        self.download_by_video_url = create_frame_label_and_input(self.root, text="Nhập link video", width=self.width, left=0.4, right=0.6)
        self.download_folder_var = create_frame_button_and_input(self.root, text="Chọn thư mục lưu video", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        create_button(frame=self.root, text="Bắt đầu tải video", command=start_download_by_video_url)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def choose_folder_to_save(self):
        download_folder = filedialog.askdirectory()
        if download_folder:
            self.download_folder_var.delete(0, ctk.END)
            self.download_folder_var.insert(0, download_folder)
            self.config['download_folder'] = download_folder
            self.save_config()

    def download_video_by_video_url(self):
        download_folder = self.config['download_folder']
        video_url = self.download_by_video_url.get()
        if not video_url:
            self.noti("Hãy nhập link video muốn tải trước.")
            return
        if not download_video_by_url(video_url, download_folder):
            video_urls = [video_url]
            download_video_by_bravedown(video_urls, download_folder)
        
    def open_edit_audio_window(self):
        self.reset()
        self.is_edit_audio_window = True
        self.show_window()
        self.setting_window_size()
        create_button(frame=self.root, text="Thay đổi thông tin audio", command=self.open_edit_audio_option)
        create_button(frame=self.root, text="Trích xuất audio", command=self.open_extract_audio_option)
        create_button(frame=self.root, text="Gộp audio", command=self.open_combine_audio_window)
        create_button(frame=self.root, text="Chuyển đổi văn bản sang giọng nói", command=self.open_text_to_mp3_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)

    def other_function(self):
        self.reset()
        self.is_other_window = True
        self.show_window()
        self.setting_window_size()
        create_button(self.root, text="Đổi tên file/thư mục theo chỉ số", command=self.open_rename_file_by_index_window, width=self.width)
        create_button(self.root, text="Đổi file jpg sang png", command=self.open_convert_jpg_to_png_window, width=self.width)
        create_button(self.root, text="Xóa/thay thế ký tự trong tên file", command=self.open_remove_char_in_file_name_window, width=self.width)
        create_button(self.root, text="Trích xuất ảnh từ video", command=self.extract_image_from_video_window, width=self.width)
        create_button(self.root, text="Gộp file txt trong thư mục", command=self.merge_txt_file_in_folder_window, width=self.width)
        create_button(self.root, text="Tách file truyện theo số chương", command=self.split_txt_file_window, width=self.width)
        create_button(self.root, text="Tách/Gộp ảnh trong thư mục", command=self.merge_image_window, width=self.width)
        create_button(self.root, text="Chụp ảnh vùng được chọn và lưu", command=self.take_screenshot_window, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)
 

#---------------------------------------------edit audio-------------------------------------------

    def merge_image_window(self):
        def start_merge_image():
            image_folder = self.videos_edit_folder_var.get().strip()
            output_folder = self.output_folder_var.get().strip()
            target_height = self.max_height_var.get().strip()
            split_or_merge_image = self.split_or_merge_image_var.get().strip()
            min_space_height = self.min_space_height_var.get().strip()
            if not check_folder(image_folder):
                return
            if split_or_merge_image=='gộp ảnh':
                merge_images(image_folder, output_folder, target_height=target_height)
            elif split_or_merge_image == 'cắt ảnh - theo ds chương':
                split_images(chapter_folder=image_folder, output_folder=output_folder, min_space_height=int(min_space_height))
            else:
                split_images(image_folder=image_folder, output_folder=output_folder, min_space_height=int(min_space_height))

        self.reset()
        self.is_merge_image = True
        self.setting_window_size()
        self.show_window()
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa Ảnh", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        self.output_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Lưu Ảnh(no need)", command= self.choose_videos_output_folder, left=0.4, right=0.6, width=self.width)
        self.split_or_merge_image_var = self.create_settings_input(text="Chọn hành động", values=['cắt ảnh - theo ds chương', 'cắt ảnh - theo ds ảnh', 'gộp ảnh'], left=0.4, right=0.6)
        self.split_or_merge_image_var.set('cắt ảnh - theo ds chương')
        self.min_space_height_var = self.create_settings_input(text="chiều cao phát hiện khoảng trắng (cắt ảnh)", values=['40', '60', '80'], left=0.4, right=0.6)
        self.max_height_var = self.create_settings_input(text="Chiều cao ảnh mong muốn", values=['1500', '2000'], left=0.4, right=0.6)
        self.max_height_var.set('2000')
        create_button(frame=self.root, text="Bắt Đầu", command=start_merge_image)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)

    def take_screenshot_window(self):
        def start_take_screenshot():
            image_folder = self.videos_edit_folder_var.get().strip()
            image_type = self.image_type_var.get().strip()
            if not check_folder(image_folder):
                return
            take_screenshot(image_folder, img_type=image_type)

        self.reset()
        self.is_take_screenshot = True
        self.setting_window_size()
        self.show_window()
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Lưu Ảnh", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        self.image_type_var = self.create_settings_input(text="Loại file ảnh muốn lưu", values=['png', 'jpg'], left=0.4, right=0.6)
        self.image_type_var.set('jpg')
        create_button(frame=self.root, text="Bắt Đầu Chụp Ảnh", command=start_take_screenshot)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)


    def split_txt_file_window(self):
        def start_split_txt_file():
            max_chapters_per_file = self.max_chapters_per_file_var.get().strip()
            txt_path = self.audio_edit_path.get().strip()
            split_txt_by_chapter(txt_path, max_chapters_per_file)

        self.reset()
        self.is_merge_txt_file = True
        self.setting_window_size()
        self.show_window()
        self.audio_edit_path = create_frame_button_and_input(self.root,text="Chọn File Truyện .txt", command= self.choose_audio_edit_file, left=0.4, right=0.6, width=self.width)
        self.max_chapters_per_file_var = create_frame_label_and_input(self.root, text="Số lượng chương trong mỗi file", width=self.width, left=0.4, right=0.6)
        self.max_chapters_per_file_var.insert(0, '50')
        create_button(frame=self.root, text="Bắt Đầu Tách File", command=start_split_txt_file)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)

    def merge_txt_file_in_folder_window(self):
        def start_merge_txt_file():
            videos_folder = self.videos_edit_folder_var.get()
            try:
                group_file = int(self.group_file_var.get().strip())
            except:
                group_file = 5000
            if group_file < 2:
                group_file = 5000
            if check_folder(videos_folder):
                merge_txt_files(videos_folder, group_file=group_file)

        self.reset()
        self.is_merge_txt_file = True
        self.setting_window_size()
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa File .txt", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        self.group_file_var = self.create_settings_input(text="Số file mỗi lần gộp", values=['all', '20', '50'], left=0.4, right=0.6)
        self.group_file_var.set('50')
        create_button(frame=self.root, text="Bắt Đầu Gộp File", command= start_merge_txt_file)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

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
        self.end_cut_var, self.first_cut_var = create_frame_label_input_input(self.root, text="Cắt ở đầu/cuối video (s)", width=self.width, left=0.4, mid=0.28, right=0.32)
        # self.end_cut_var.delete(0, ctk.END)
        self.end_cut_var.insert(0, 0)
        self.first_cut_var.insert(0, 0)
        self.audio_speed_var = self.create_settings_input(text="Tốc độ phát", config_key="audio_speed", values=['0.8', '1', '1.2'], left=0.4, right=0.6)
        self.pitch_factor_var = self.create_settings_input(text="Điều chỉnh cao độ (vd: 1.2)", config_key="pitch_factor", values=['-0.8','1','1.2'], left=0.4, right=0.6)
        self.cut_silence_var = self.create_settings_input(text="Cắt bỏ những đoạn im lặng", config_key="cut_silence", values=['Yes', 'No'], left=0.4, right=0.6)
        self.aecho_var = self.create_settings_input(text="Tạo tiếng vang (ms)", config_key="aecho", values=['100', '500', '1000'], left=0.4, right=0.6)
        self.folder_get_audio_var = create_frame_button_and_input(self.root,text="Chọn thư mục chứa audio", command= self.choose_folder_get_audio, left=0.4, right=0.6, width=self.width)
        self.folder_get_audio_var.insert(0, self.config['audios_edit_folder'])
        create_button(self.root, text="Bắt đầu chỉnh sửa audio", command=start_thread_edit_audio, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)
        
    def open_extract_audio_option(self):
        self.reset()
        self.is_extract_audio_option = True
        self.setting_window_size()
        self.show_window()
        self.segment_audio_var = create_frame_label_and_input(self.root, text="Thời gian bắt đầu-kết thúc", width=self.width, left=0.4, right=0.6)
        self.speed_audio_var = create_frame_label_and_input(self.root, text="Thay đổi tốc độ audio", width=self.width, left=0.4, right=0.6)
        self.speed_audio_var.insert(0, '1.0')
        self.video_get_audio_url = create_frame_label_and_input(self.root, text="Lấy audio từ Link", left=0.4, right=0.6)
        self.audio_edit_path = create_frame_button_and_input(self.root,text="Lấy audio từ file MP3", command= self.choose_audio_edit_file, left=0.4, right=0.6)
        self.video_get_audio_path = create_frame_button_and_input(self.root,text="Lấy audio từ file video", command= self.choose_video_get_audio_path, left=0.4, right=0.6)
        self.folder_get_audio_var = create_frame_button_and_input(self.root,text="Lấy audio từ video trong thư mục", command= self.choose_folder_get_audio, left=0.4, right=0.6)
        self.download_folder_var = create_frame_button_and_input(self.root,text="Chọn thư mục lưu file", command= self.choose_folder_download, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt đầu trích xuất audio", command=self.create_thread_edit_audio, padx=8)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)

    def choose_folder_download(self):
        folder = choose_folder()
        self.download_folder_var.delete(0, ctk.END)
        self.download_folder_var.insert(0, folder)

    def choose_folder_get_audio(self):
        folder = choose_folder()
        self.folder_get_audio_var.delete(0, ctk.END)
        self.folder_get_audio_var.insert(0, folder)

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
            download_folder = self.download_folder_var.get()
            speed_audio = self.speed_audio_var.get().strip()
            video_get_audio_url = self.video_get_audio_url.get().strip()
            audio_edit_path = self.audio_edit_path.get().strip()
            video_get_audio_path = self.video_get_audio_path.get().strip()
            video_folder = self.folder_get_audio_var.get().strip()
            if not os.path.exists(download_folder) and video_get_audio_url:
                self.noti("hãy chọn thư mục lưu file tải về.")
                return
            if not video_get_audio_url and not os.path.exists(audio_edit_path) and not os.path.exists(video_get_audio_path) and not os.path.exists(video_folder):
                self.noti("Hãy chọn 1 nguồn lấy audio !!!")
                return
            segment_audio = self.segment_audio_var.get().strip()
            extract_audio_ffmpeg(audio_path=audio_edit_path, video_path=video_get_audio_path, video_url=video_get_audio_url, video_folder=video_folder, segments=segment_audio, download_folder=download_folder, speed=speed_audio)
        except:
            getlog()
            print("Có lỗi trong quá trình trích xuất audio !!!")

#-------------------------------------------edit video-----------------------------------------------------
    def open_edit_video_menu(self):
        self.reset()
        self.is_open_edit_video_menu = True
        self.show_window()
        self.setting_window_size()
        create_button(frame=self.root, text="Thay đổi thông tin video", command=self.open_edit_video_window)
        create_button(frame=self.root, text="Lấy âm thanh/ phụ đề/ ảnh từ video", command=self.open_extract_sub_image_audio_from_video_window)
        create_button(self.root, text="Cắt video", command=self.open_cut_video_window)
        create_button(self.root, text="Gộp video", command=self.open_combine_video_window)
        create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)
    
    def open_extract_sub_image_audio_from_video_window(self):
        self.whisper_model = None
        self.index = 0
        def start_thread_extract_sub_image_audio():
            thread = threading.Thread(target=start_extract_sub_image_audio)
            thread.start()

        def start_extract_sub_image_audio():
            all_type = ['.mp4', '.mp3', '.wav']
            video_path = self.videos_edit_path_var.get().strip()
            if not os.path.exists(video_path):
                print(f"Video {video_path} không tồn tại")
                return
            if video_path.endswith('.mp4') or video_path.endswith('.mp3') or video_path.endswith('.wav'):
                extract_sub_image_audio_from_video(video_path)
            else:
                if os.path.isdir(video_path):
                    file_type = self.file_type_var.get().strip()
                    if file_type not in all_type:
                        print(f'File không được hỗ trợ {file_type} --> Chỉ hỗ trợ mp4/mp3/wav')
                        return
                    videos = get_file_in_folder_by_type(video_path, file_type=file_type)
                    if len(videos) == 0:
                        print(f"Không tìm thấy file phù hợp trong thư mục {video_path}")
                        return
                    for video in videos:
                        if self.is_stop_edit:
                            print("Dừng trích xuất phụ đề!")
                            break
                        vi_path = os.path.join(video_path, video)
                        extract_sub_image_audio_from_video(vi_path)
                        
                    self.whisper_model  = None
                    torch.cuda.empty_cache()
                    gc.collect()
                else:
                    print("Chọn file hoặc thư mục chứa video/audio")

        def extract_sub_image_audio_from_video(video_path, language='vi', min_lenth_text=35):
            if language == 'en':
                min_lenth_text = 0
            cur_folder = os.path.dirname(video_path)
            video_name = os.path.basename(video_path).split('.')[0]
            file_path = os.path.join(cur_folder, f'{video_name}.txt')
            output_dir = os.path.join(cur_folder, video_name)
            os.makedirs(output_dir, exist_ok=True)

            def convert_video_to_audio(video_path):
                try:
                    audio_paths = []
                    print(f'--> Đang trích xuất phụ đề từ video/audio: {video_path}')
                    
                    if video_path.endswith('.mp4'):
                        video_info = get_video_info(video_path)
                    else:
                        video_info = get_audio_info(video_path)
                    try:
                        duration = float(video_info.get('duration'))
                    except:
                        print(f'Không lấy được thông tin file {video_path} --> Dừng xử lý')
                        return None
                    
                    segment_duration = 240
                    cnt_segments = (duration + segment_duration - 1) // segment_duration
                    adjusted_segment_duration = duration / cnt_segments
                    for i in range(int(cnt_segments)):
                        start_time = i * adjusted_segment_duration
                        output_path = os.path.join(output_dir, f"{video_name}_{i + 1}.wav")
                        
                        ffmpeg_cmd = [
                            "ffmpeg", "-y", "-i", video_path,
                            "-ss", str(start_time),
                            "-t", str(adjusted_segment_duration),
                            "-ac", "1", "-ar", "24000", "-sample_fmt", "s16", "-vn",
                            output_path
                        ]
                        
                        if run_command_ffmpeg(ffmpeg_cmd):
                            if os.path.exists(output_path):
                                audio_paths.append(output_path)
                    if len(audio_paths) > 1:
                        print(f'Đã chia video thành {len(audio_paths)} đoạn để xử lý')
                    if len(audio_paths) == 0:
                        print(f'Không trích xuất được audio từ video {video_path}')
                        return
                    for i, audio_path in enumerate(audio_paths):
                        t = time()
                        print(f'  -->  Bắt đầu nhận diện giọng nói cho đoạn {i + 1}/{len(audio_paths)} ({datetime.now().strftime("%H:%M:%S")}) --> Vui lòng chờ ...')
                        segments = transcribe_with_whisper(audio_path)
                        if not segments:
                            print(f'<Cảnh Báo> trích xuất phụ đề từ video {video_path} thất bại')
                            return False
                        if cut_audio_and_image(audio_path, segments):
                            print(f'{thanhcong} Thời gian xử lý đoạn {i + 1}/{len(audio_paths)}: {int(time() - t)}s')
                            remove_file(audio_path)
                            return True
                except:
                    getlog()
                    return False

            def transcribe_with_whisper(audio_path):
                try:
                    if not self.whisper_model:
                        self.whisper_model = whisper.load_model("large-v2", device='cpu')
                    result = self.whisper_model.transcribe(audio_path, language=language)
                    return result['segments']
                except:
                    getlog()
                    return None
            
            def cut_audio_and_image(audio_path, segments):
                try:
                    with open(file_path, 'a', encoding='utf-8') as file:                                                                                                                                                                                                              
                        current_text = ""
                        current_start_time = None
                        min_cnt= 1
                        for i, segment in enumerate(segments):
                            if i == 0 or i == len(segments) - 1:
                                continue
                            text = segment["text"].strip()
                            start_time = segment["start"]
                            if current_start_time is None:
                                current_start_time = start_time
                            if text not in current_text:
                                current_text += (" " if current_text else "") + text
                            if len(current_text) < min_lenth_text:
                                short_dir = os.path.join(cur_folder, 'short')
                                os.makedirs(short_dir, exist_ok=True)
                                short_audio_dir = os.path.join(short_dir, f'{video_name}_short')
                                os.makedirs(short_audio_dir, exist_ok=True)
                                text_output_path = os.path.join(short_audio_dir, f"{video_name}_short.txt")
                                end_time = segment["end"]
                                audio_output_path = os.path.join(short_audio_dir, f"{min_cnt}.wav")
                                audio_cut_cmd = [ "ffmpeg", "-y", "-i", audio_path, "-ss", str(current_start_time), "-to", str(end_time), audio_output_path ]
                                if run_command_ffmpeg(audio_cut_cmd):
                                    with open(text_output_path, "a", encoding="utf-8") as f:
                                        f.write(str(min_cnt) + "\n" + current_text + "\n")
                                    #reset
                                    current_text = ""
                                    current_start_time = None
                                    min_cnt += 1
                            elif current_text.endswith(".") or current_text.endswith("?") or current_text.endswith("!"):
                                if len(current_text) >= max_lenth_text:
                                    current_text = ""
                                    current_start_time = None
                                    continue
                                end_time = segment["end"]
                                self.index += 1
                                audio_output_path = os.path.join(output_dir, f"{self.index}.wav")
                                audio_cut_cmd = [ "ffmpeg", "-y", "-i", audio_path, "-ss", str(current_start_time), "-to", str(end_time), audio_output_path ]
                                if run_command_ffmpeg(audio_cut_cmd):
                                    current_text = cleaner_text(current_text, language=language, is_loi_chinh_ta=True)
                                    file.write(f"{self.index}\n{current_text}\n")
                                    #reset
                                    current_text = ""
                                    current_start_time = None
                    return True
                except:
                    getlog()
                    return False
            
            if video_path.endswith('.mp4') or video_path.endswith('.mp3') or video_path.endswith('.wav'):
                convert_video_to_audio(video_path)
            else:
                print(f'{canhbao} File {video_path} không hợp lệ !!!')
                return False
            if not os.path.isdir(video_path):
                remove_file(video_path)
            return True

        self.reset()
        self.is_extract_sub_image_audio_from_video_window = True
        self.show_window()
        self.setting_window_size()
        self.videos_edit_path_var = create_frame_button_and_input(self.root, "Chọn file hoặc thư mục", command=self.choose_videos_edit_file, width=self.width, left=0.3, right=0.7)
        self.file_type_var = self.create_settings_input("Chọn loại file (nếu ở trên chọn thư mục)", values=['.mp4', '.mp3', '.wav'], left=0.3, right=0.7)
        self.file_type_var.set('.mp4')
        create_button(self.root, text="Bắt đầu trích xuất", command=start_thread_extract_sub_image_audio, width=self.width)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)

    def open_cut_video_window(self):
        self.reset()
        self.is_cut_video_window =True
        self.show_window()
        self.setting_window_size()
        self.segments_var = self.create_settings_input(text="Khoảng thời gian muốn lấy(start-end)", left=0.4, right=0.6)
        self.fast_cut_var = self.create_settings_input(text="Cắt nhanh", values=["Yes", "No"], left=0.4, right=0.6)
        self.fast_cut_var.set(value="No")
        self.get_audio_var = self.create_settings_input(text="Trích xuất MP3", values=["Yes", "No"], left=0.4, right=0.6)
        self.get_audio_var.set(value="No")
        self.choose_is_connect_var = self.create_settings_input(text="Nối các video lại", values=["No", "Connect", "Fast Connect"], left=0.4, right=0.6)
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
        self.fast_combine_var = self.create_settings_input(text="Gộp nhanh", values=["Yes", "No"], left=0.4, right=0.6)
        self.fast_combine_var.set('Yes')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root, "Chọn thư mục chứa video", command=self.choose_videos_edit_folder, width=self.width, left=0.4, right=0.6)
        self.videos_edit_folder_var.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Bắt đầu gộp", command=self.create_thread_combine_video)
        create_button(self.root, text="Lùi lại", command=self.open_edit_video_menu, width=self.width)
    
    def open_combine_audio_window(self):
        self.reset()
        self.is_combine_video_window =True
        self.show_window()
        self.setting_window_size()
        self.file_name_var = create_frame_label_and_input(self.root, "Đặt tên file sau khi gộp", width=self.width, left=0.4, right=0.6)
        self.fast_combine_var = self.create_settings_input(text="Gộp nhanh", values=["Yes", "No"], left=0.4, right=0.6)
        self.fast_combine_var.set('Yes')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root, "Chọn thư mục chứa audio", command=self.choose_videos_edit_folder, width=self.width, left=0.4, right=0.6)
        self.videos_edit_folder_var.insert(0, self.config['videos_edit_folder'])
        create_button(self.root, text="Bắt đầu gộp", command=self.create_thread_combine_audio)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)

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
        if not check_folder(videos_folder):
            return
        try:
            merge_videos_use_ffmpeg(videos_folder, file_name, is_delete=self.config['is_delete_video'], fast_combine=fast_combine)
        except:
            getlog()
            print(f"Có lỗi trong quá trình gộp video. Đang dùng cách khác để gộp video.")

    def combine_audio_by_ffmpeg(self):
        audios_folder = self.videos_edit_folder_var.get()
        file_name = self.file_name_var.get()
        fast_combine = self.fast_combine_var.get() == 'Yes'
        if not check_folder(audios_folder):
            return
        try:
            merge_audio_use_ffmpeg(audios_folder, file_name, fast_combine=fast_combine)
        except:
            print(f"Có lỗi trong quá trình gộp audio !!!")

    def open_edit_video_window(self):
        self.reset()
        self.is_edit_video_window = True
        self.setting_window_size()
        self.show_window()
        self.end_cut_var, self.first_cut_var = create_frame_label_input_input(self.root, text="Cắt ở đầu/cuối video (s)", width=self.width, left=0.4, mid=0.28, right=0.32)
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
        self.pitch_factor_var = self.create_settings_input("Điều chỉnh cao độ audio", "pitch_factor", values=['-0.8','1','1.2'], left=0.4, right=0.6)
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
    def create_thread_combine_audio(self):
        if not self.edit_audio_thread or not self.edit_audio_thread.is_alive():
            self.edit_audio_thread = threading.Thread(target=self.combine_audio_by_ffmpeg)
            self.edit_audio_thread.start()
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
            self.config['pitch_factor'] = self.pitch_factor_var.get() or "1"
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
            is_edit_ok = self.fast_edit_video(video_path)
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
        pitch_factor = self.config.get('pitch_factor', "1")
        try:
            pitch = float(pitch_factor)
        except:
            pitch = 1
        new_audio_folder = self.config.get('background_music_path', None)
        new_audio_path = None
        if new_audio_folder and os.path.exists(new_audio_folder):
            new_audio_path = get_random_audio_path(new_audio_folder)
            if not new_audio_path or not os.path.exists(new_audio_path):
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
            if self.new_name:
                if '<index>' not in self.new_name:
                    self.new_name = f"{self.new_name} <index>"
                file_name = self.new_name.replace("<index>", str(self.index))
                self.index += 1
            else:
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
                    print("Đường dẫn watermark không hợp lệ")
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
                '-loglevel', 'quiet',
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
                        f'-map', f'{audio_index}:a',
                        '-filter:a:0', f'volume={audio_volume}',
                    ])
                else:
                    command.extend([
                        '-map', '[video]',
                        f'-map', f'{audio_index}:a',
                        '-filter:a:0', f'volume=1,atempo={speed_up},rubberband=pitch={pitch}',
                    ])
            elif not remove_original_audio:
                command.extend([
                    '-map', '[video]',
                    '-map', '0:a',  # Âm thanh gốc
                    '-filter:a', f'volume=1,atempo={speed_up},rubberband=pitch={pitch}',
                ])
            else:
                command.extend([
                    '-map', '[video]',
                    '-an' 
                ])
            command.extend([
                '-vcodec', 'libx264', 
                '-acodec', 'aac',
                '-r', f'{video_fps + 1}',
                '-y',
            ])
            if end_cut is not None:
                duration = end_cut - first_cut
                command.extend(['-to', str(duration)])
            command.append(output_file)
            if not run_command_with_progress(command, duration):
                if not run_command_ffmpeg(command):
                    print(f"Video lỗi !!!")
                    return False
            remove_file(combined_audio_path)
            remove_file(temp_audio_path)
            remove_or_move_file(input_video_path, is_delete=self.config['is_delete_video'], is_move=self.config['is_move'])
            return True
        except:
            print(f"Có lỗi trong quá trình xử lý video {input_video_path}")
            getlog()
            return False


    
#---------------------------Các Hàm gọi chung co class----------------------------------

    # def open_common_settings(self):
    #     def save_common_config():
    #         self.config["auto_start"] = self.auto_start_var.get() == "Yes"
    #         self.config["is_delete_video"] = self.is_delete_video_var.get() == "Yes"
    #         self.config['is_move'] = self.is_move_video_var.get() == "Yes"
    #         self.save_config()
    #         self.get_start_window()
    #     self.reset()
    #     self.is_open_common_setting = True
    #     self.show_window()
    #     self.setting_window_size()
    #     self.auto_start_var = self.create_settings_input("Khởi động ứng dụng cùng window", "auto_start", values=["Yes", "No"], left=0.4, right=0.6)
    #     self.is_delete_video_var = self.create_settings_input("Xóa video gốc sau chỉnh sửa", "is_delete_video", values=["Yes", "No"], left=0.4, right=0.6)
    #     self.is_move_video_var = self.create_settings_input("Di chuyển video gốc sau chỉnh sửa", "is_move", values=["Yes", "No"], left=0.4, right=0.6)
    #     create_button(self.root, text="Lưu cài đặt", command=save_common_config, width=self.width)
    #     create_button(self.root, text="Lùi lại", command=self.get_start_window, width=self.width)
        

    def choose_background_music_folder(self):
        background_music_folder = choose_folder()
        self.background_music_path.delete(0, ctk.END)
        self.background_music_path.insert(0, background_music_folder)

    def choose_videos_edit_folder(self):
        videos_edit_folder = filedialog.askdirectory()
        if self.videos_edit_folder_var:
            self.videos_edit_folder_var.delete(0, ctk.END)
            self.videos_edit_folder_var.insert(0, videos_edit_folder)

    def choose_videos_output_folder(self):
        output_folder = filedialog.askdirectory()
        if self.output_folder_var:
            self.output_folder_var.delete(0, ctk.END)
            self.output_folder_var.insert(0, output_folder)

    def choose_videos_edit_file(self):
        videos_edit_path = choose_file()
        self.videos_edit_path_var.delete(0, ctk.END)
        self.videos_edit_path_var.insert(0, videos_edit_path)

    def choose_water_mask_image(self):
        water_mask_image = filedialog.askopenfilename()
        self.water_path_var.delete(0, ctk.END)
        self.water_path_var.insert(0, water_mask_image)

#------------------------------------------------------Common-----------------------------------------------------
    def create_settings_input(self, text, config_key=None, values=None, is_textbox = False, left=0.4, right=0.6, add_button=False, command=None):
        frame = create_frame(self.root)
        if add_button:
            create_button(frame= frame, text=text, command=command, width=0.2, side=RIGHT)
        create_label(frame, text=text, side=LEFT, width=self.width*left, anchor='w')

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
            if config_key == "category_id":
                combobox.set(val[0])
            setattr(self, f"{config_key}_var", var)
            result = combobox
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", self.config[config_key])
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
        self.is_start_window = False
        self.is_edit_video_window= False
        self.is_edit_video_window= False
        self.is_open_common_setting = False
        self.is_open_edit_video_menu = False
        self.is_cut_video_window = False
        self.is_text_to_mp3_window = False
        self.is_combine_video_window = False
        self.is_rename_file_by_index_window = False
        self.is_merge_txt_file = False
        self.is_merge_image = False
        self.is_take_screenshot = False
        self.is_remove_char_in_file_name_window = False
        self.is_extract_image_from_video_window = False
        self.is_other_window = False
        self.is_other_download_window = False
        self.is_edit_audio_window = False
        self.is_edit_audio_option = False
        self.is_extract_audio_option = False
        self.download_image_from_truyenqqto = False
        self.download_text_story = False
        self.edit_image_window = False
        self.export_video_window = False
        self.export_video_from_mp3_window = False
        self.create_video_with_multi_audio_window = False
        self.is_extract_sub_image_audio_from_video_window = False
        self.is_convert_jpg_to_png = False
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
                item("Dừng xuất video tiếp theo.", self.stop_export_next_video),
                item("Dừng tiến trình chỉnh sửa video", self.stop_edit_videos),
                item("Dừng tất cả tiến trình đang chạy", self.stop_all_process),
                item("Thoát ứng dụng", self.exit_app),
            )
            self.icon = pystray.Icon("Review Truyện", image, "Review Truyện", menu)
            tray_thread = threading.Thread(target=self.icon.run_detached)
            tray_thread.daemon = True
            tray_thread.start()
        except:
            getlog()

    def stop_download(self):
        self.is_stop_download = True
        print(f"{canhbao} Đang dừng quá trình tải video, vui lòng chờ trong giây lát ...")

    def stop_export_next_video(self):
        self.is_stop_export_next_video = True
        print(f"{stop} Bạn đã thiết lập dừng xuất video tiếp theo. Nếu muốn dừng ngay thì vui lòng tắt ứng dụng.")

    def stop_edit_videos(self):
        self.is_stop_edit = True
        print(f"{canhbao} Đang dừng quá trình chỉnh sửa video, vui lòng chờ trong giây lát ...")

    def stop_all_process(self):
        self.stop_download()
        self.stop_export_next_video()
        self.stop_edit_videos()

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
    
    def close_driver(self):
        if self.driver:
            self.driver.quit()
            print(f"Đóng trình duyệt!")
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
            self.height_window = 530
        else:
            if self.is_start_window:
                self.root.title("Review App")
                self.width = 500
                self.height_window = 530
                self.is_start_window = False
            elif self.is_open_common_setting:
                self.root.title("Common Setting")
                self.width = 700
                self.height_window = 555
                self.is_open_common_setting = False
            elif self.is_edit_video_window:
                self.root.title("Edit Videos")
                self.width = 700
                self.height_window = 943
                self.is_edit_video_window = False
            elif self.is_open_edit_video_menu:
                self.root.title("Edit Video Window")
                self.width = 500
                self.height_window = 342
                self.is_open_edit_video_menu = False
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
            elif self.is_edit_audio_window:
                self.root.title("Edit Audio Window")
                self.width = 500
                self.height_window = 302
                self.is_edit_audio_window = False
            elif self.is_edit_audio_option:
                self.root.title("Edit Audio Option")
                self.width = 500
                self.height_window = 458
                self.is_edit_audio_option = False
            elif self.is_extract_audio_option:
                self.root.title("Extract Audio Option")
                self.width = 500
                self.height_window = 506
                self.is_extract_audio_option = False
            elif self.is_text_to_mp3_window:
                self.root.title("Text to MP3 window")
                self.width = 500
                self.height_window = 314
                self.is_text_to_mp3_window = False
            elif self.is_rename_file_by_index_window:
                self.root.title("Rename Files")
                self.width = 500
                self.height_window = 361
                self.is_rename_file_by_index_window = False
            elif self.is_merge_txt_file:
                self.root.title("Rename Files")
                self.width = 500
                self.height_window = 267
                self.is_merge_txt_file = False
            elif self.is_merge_image:
                self.root.title("Merge Images")
                self.width = 500
                self.height_window = 406
                self.is_merge_image = False
            elif self.is_take_screenshot:
                self.root.title("Merge Images")
                self.width = 500
                self.height_window = 267
                self.is_take_screenshot = False
            elif self.is_convert_jpg_to_png:
                self.root.title("Convert Image Format")
                self.width = 500
                self.height_window = 315
                self.is_convert_jpg_to_png = False
            elif self.is_remove_char_in_file_name_window:
                self.root.title("Remove Char in Files")
                self.width = 500
                self.height_window = 362
                self.is_remove_char_in_file_name_window = False
            elif self.is_extract_image_from_video_window:
                self.root.title("Extract Image From Video")
                self.width = 500
                self.height_window = 265
                self.is_extract_image_from_video_window = False
            elif self.is_other_window:
                self.root.title("Other")
                self.width = 500
                self.height_window = 485
                self.is_other_window = False
            elif self.is_other_download_window:
                self.root.title("Download Video")
                self.width = 500
                self.height_window = 315
                self.is_other_download_window = False            
            elif self.download_image_from_truyenqqto:
                self.root.title("Tải truyện tranh")
                self.width = 500
                self.height_window = 270
                self.download_image_from_truyenqqto = False              
            elif self.edit_image_window:
                self.root.title("Xử lý ảnh")
                self.width = 500
                self.height_window = 312
                self.edit_image_window = False              
            elif self.export_video_window:
                self.root.title("Xuất video từ phụ đề")
                self.width = 600
                self.height_window = 650
                self.export_video_window = False              
            elif self.export_video_from_mp3_window:
                self.root.title("Xuất video từ mp3 và video nền")
                self.width = 600
                self.height_window = 313
                self.export_video_from_mp3_window = False              
            elif self.create_video_with_multi_audio_window:
                self.root.title("Xuất video từ nhiều audio + hiển thị chữ")
                self.width = 600
                self.height_window = 650
                self.create_video_with_multi_audio_window = False              
            elif self.is_extract_sub_image_audio_from_video_window:
                self.root.title("Lấy âm thanh/ phụ đề/ ảnh từ video")
                self.width = 700
                self.height_window = 270
                self.is_extract_sub_image_audio_from_video_window = False
            elif self.download_text_story:
                self.root.title("Tải Truyện Chữ")
                self.width = 500
                self.height_window = 360
                self.download_text_story = False              

        self.setting_screen_position()


    def open_rename_file_by_index_window(self):
        self.reset()
        self.is_rename_file_by_index_window = True
        self.setting_window_size()
        self.file_name_var = create_frame_label_and_input(self.root, text="Tên file muốn đổi", place_holder="Tên file có chứa \"<index>\" làm vị trí đặt số", width=self.width, left=0.4, right=0.6)
        self.index_file_name_var = create_frame_label_and_input(self.root, text="Số thứ tự bắt đầu", width=self.width, left=0.4, right=0.6)
        self.index_file_name_var.insert(0, '1')
        self.file_name_extension_var = create_frame_label_and_input(self.root, text="Loại file muốn đổi tên", width=self.width, left=0.4, right=0.6)
        self.file_name_extension_var.insert(0, '.wav')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa File", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Đổi Tên", command= self.rename_file_by_index)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def open_convert_jpg_to_png_window(self):
        def start_convert_jpg_to_png():
            img_from_format = self.img_from_format_var.get()
            img_to_format = self.img_to_format_var.get()
            videos_folder = self.videos_edit_folder_var.get()
            if check_folder(videos_folder):
                convert_jpg_to_png(videos_folder, img_from_format, img_to_format)

        self.reset()
        self.is_convert_jpg_to_png = True
        self.setting_window_size()
        self.img_from_format_var = self.create_settings_input(text="Định dạng gốc của ảnh", values=["jpg", "jpeg", "png", "bmp", "tiff", "webp"], left=0.4, right=0.6)
        self.img_to_format_var = self.create_settings_input(text="Định dạng muốn chuyển đổi", values=["jpg", "jpeg", "png", "bmp", "tiff", "webp"], left=0.4, right=0.6)
        self.img_from_format_var.set("jpg")
        self.img_to_format_var.set("png")
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa Ảnh", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Đổi Định Dạng Ảnh", command= start_convert_jpg_to_png)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def extract_image_from_video_window(self):
        self.reset()
        self.is_extract_image_from_video_window = True
        self.setting_window_size()
        self.image_position_var = create_frame_label_and_input(self.root, text="Chọn vị trí trích xuất ảnh", width=self.width, left=0.4, right=0.6, place_holder='Ví dụ: 00:40 hoặc 00:10:15')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa Video", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Trích Xuất Ảnh", command= self.extract_image_from_video)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def open_remove_char_in_file_name_window(self):
        self.reset()
        self.is_remove_char_in_file_name_window = True
        self.setting_window_size()
        self.char_want_to_remove_var = create_frame_label_and_input(self.root, text="Ký tự muốn loại bỏ/thay thế", width=self.width, left=0.4, right=0.6, place_holder='Ví dụ: .,-,#')
        self.char_want_to_replace_var = create_frame_label_and_input(self.root, text="Ký tự muốn thay", width=self.width, left=0.4, right=0.6, place_holder='để trống nếu muốn xóa ký tự')
        self.file_name_extension_var = create_frame_label_and_input(self.root, text="Loại file muốn đổi tên", width=self.width, left=0.4, right=0.6)
        self.file_name_extension_var.insert(0, '.wav')
        self.videos_edit_folder_var = create_frame_button_and_input(self.root,text="Chọn Thư Mục Chứa File", command= self.choose_videos_edit_folder, left=0.4, right=0.6, width=self.width)
        create_button(frame=self.root, text="Bắt Đầu Đổi Tên", command= self.remove_char_in_file_name)
        create_button(self.root, text="Lùi lại", command=self.other_function, width=self.width)
        self.show_window()

    def rename_file_by_index(self):
        base_name = self.file_name_var.get()
        index = self.index_file_name_var.get()
        extension = self.file_name_extension_var.get()
        videos_folder = self.videos_edit_folder_var.get()
        if check_folder(videos_folder):
            rename_files_by_index(videos_folder, base_name, extension, index)

    def remove_char_in_file_name(self):
        chars_want_to_remove = self.char_want_to_remove_var.get()
        char_want_to_replace = self.char_want_to_replace_var.get()
        extension = self.file_name_extension_var.get()
        videos_folder = self.videos_edit_folder_var.get()
        if not chars_want_to_remove:
            self.noti("Hãy nhập các ký tự muốn loại bỏ và cách nhau bởi dấu \",\". Ví dụ:  \".,#\"")
            return
        if check_folder(videos_folder):
            remove_char_in_file_name(folder_path=videos_folder, chars_want_to_remove=chars_want_to_remove, char_want_to_replace=char_want_to_replace, extension=extension)

    def extract_image_from_video(self, videos_folder=None):
        position = self.image_position_var.get().strip()
        if not videos_folder:
            videos_folder = self.videos_edit_folder_var.get()
        if not position:
            self.noti("Hãy nhập vị trí thời gian muốn trích xuất ảnh")
            return
        if check_folder(videos_folder):
            get_image_from_video(videos_folder=videos_folder, position=position)

#-------------------------------Convert MP3------------------------------------------------
    def open_text_to_mp3_window(self):
        self.reset()
        self.is_text_to_mp3_window = True
        self.setting_window_size()
        self.file_path_get_var = create_frame_button_and_input(self.root, text="File \'.txt\' muốn chuyển đổi", command= self.choose_directory_get_txt_file, width=self.width, left=0.4, right=0.6)
        self.speed_talk_var = self.create_settings_input(text="Tốc độ đọc", config_key='speed_talk', values=["0.8", "0.9", "1", "1.1", "1.2"])
        self.convert_multiple_record_var = self.create_settings_input(text="Chế độ chuyển theo từng dòng", values=["Yes", "No"])
        self.convert_multiple_record_var.set("No")
        create_button(frame=self.root, text="Bắt đầu chuyển đổi", command= self.text_to_mp3)
        create_button(self.root, text="Lùi lại", command=self.open_edit_audio_window, width=self.width)
        self.show_window()

    def choose_directory_get_txt_file(self):
        file_path_get = choose_file(file_type="txt")
        self.file_path_get_var.delete(0, ctk.END)
        self.file_path_get_var.insert(0, file_path_get)

    def text_to_mp3(self, voice=None, speed=1):
        pass
if __name__ == "__main__":
    app = MainApp()
    try:
        app.root.mainloop()
    except:
        pass
