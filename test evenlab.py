from common_function import *


def text_to_speeed_by_evenlab(input_txt_path, email=None, start_idx=0, url="https://elevenlabs.io/app/speech-synthesis/text-to-speech"):
    try:
        if not email:
            print(f"{thatbai} Nhập email của profile trước.")
            return None, False
        if not os.path.exists(input_txt_path):
            print(f"{thatbai} file {input_txt_path} không tồn tại.")
            return None, False
        folder = os.path.dirname(input_txt_path)
        file_name = os.path.basename(input_txt_path)
        name = file_name[:-4]
        split_txt_path = os.path.join(folder, f"{name}_split.txt")
        out_txt_path = os.path.join(folder, f"{name}_tts.txt")
        finish_texts = []
        texts = []
        driver = None
        if name.endswith('_split'):
            all_texts = get_json_data(input_txt_path)
            texts = [ttt.lower().strip() for ttt in all_texts if ttt.strip() and len(ttt.strip()) > 1]
        else:
            all_texttttt = get_json_data(input_txt_path, readline=False)
            all_texttttt = cleaner_text(all_texttttt, language='en')
            all_texts = all_texttttt.split('\n')
            all_texts = [ttt.lower().strip() for ttt in all_texts if ttt.strip() and len(ttt.strip()) > 1]
            for tttt in all_texts:
                sub_sentences = tttt.split('.')
                for sub in sub_sentences:
                    if not sub or not sub.strip():
                        continue
                    sub = sub.strip()
                    if sub and sub != '.' and sub != '…':
                        if sub.endswith(','):
                            sub = f"{sub[:-1]}."
                        elif not sub.endswith('.'):
                            sub = sub + '.'
                        if sub not in texts:
                            texts.append(sub)
            if not os.path.exists(split_txt_path):
                with open(split_txt_path, "w", encoding="utf-8") as hhh:
                    for line in texts:
                        hhh.write(f"{line}\n")
                print(f"{thanhcong} Đã chuẩn hóa file txt thành công!")

        driver = get_firefox_driver_with_profile(target_email=email)
        if not driver:
            return None, None
        driver.get(url)
        sleep(3)
        textarea_xpath = get_xpath_by_multi_attribute('textarea', ['aria-label="Main textarea"'])
        textarea = get_element_by_xpath(driver, textarea_xpath)
        if not textarea:
            email_x = get_xpath_by_multi_attribute('input', ['type="email"'])
            email_ele = get_element_by_xpath(driver, email_x)
            if email_ele:
                email_ele.clear()
                sleep(0.5)
                email_ele.send_keys(email)
                sleep(0.5)
                pass_x = get_xpath_by_multi_attribute('input', ['type="password"'])
                pass_ele = get_element_by_xpath(driver, pass_x)
                if pass_ele:
                    pass_ele.clear()
                    sleep(0.5)
                    pass_ele.send_keys('thien191!')
                    sleep(0.5)
                    pass_ele.send_keys(Keys.RETURN)
                    sleep(4)
                    textarea_xpath = get_xpath_by_multi_attribute('textarea', ['aria-label="Main textarea"'])
                    textarea = get_element_by_xpath(driver, textarea_xpath)
                    if not textarea:
                        print(f"Không tìm thấy chỗ nhập nội dung.")
                        return None, None
            else:
                print(f"Không tìm thấy chỗ nhập nội dung.")
                return None, None
        sleep(3)
   
        for idx, text in enumerate(texts):
            if idx < start_idx:
                continue
            if text in finish_texts:
                continue
            text = cleaner_text(text, language='en')
            textarea.clear()
            sleep(0.5)
            textarea.send_keys(text)
            sleep(0.5)
            convert_button_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Generate speech (Shift+Enter)"'])
            convert_button = get_element_by_xpath(driver, convert_button_xpath)
            if convert_button:
                convert_button.click()
                sleep(6)
                if len(text) > 150:
                    sleep(4)
                err = 0
                is_break = False
                while True:
                    if is_break:
                        break
                    tai_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Download Audio"'])
                    tai_ele = get_element_by_xpath(driver, tai_xpath)
                    if tai_ele:
                        tai_ele.click()
                        sleep(3)
                        in_fol = "C:\\Users\\dxthi\\Downloads"
                        out_fol = os.path.join(folder, 'out_files')
                        if 'eval' in input_txt_path:
                            out_fol = os.path.join(folder, 'eval')

                        os.makedirs(out_fol, exist_ok=True)
                        while True:
                            if move_file(in_fol, out_fol, idx):
                                finish_texts.append(text)
                                with open(out_txt_path, "a", encoding="utf-8") as fff:
                                    fff.write(f"{str(idx)}\n{text}\n")
                                print(f"{thanhcong} {idx} --> {text}")
                                is_break = True
                                break
                            sleep(2)
                            err += 1
                            if err == 6:
                                tai_ele = get_element_by_xpath(driver, tai_xpath)
                                if tai_ele:
                                    tai_ele.click()
                                    sleep(3)
                            if err == 10:
                                convert_button = get_element_by_xpath(driver, convert_button_xpath)
                                if convert_button:
                                    convert_button.click()
                                    sleep(6)
                                    if len(text) > 150:
                                        sleep(4)
                            if err > 20:
                                print(f"{thatbai} Lỗi tại idx {idx} --> {text}")
                                return idx, True
                    else:
                        sleep(2)
                        err += 1
                        if err == 5 or err == 10:
                            remain_char = get_element_by_text(driver, 'credits remaining', tag_name='span', contain=True)
                            if remain_char:
                                remain_char = remain_char.text.replace('credits remaining', '').replace(',', '').replace('.', '').strip()
                                remain_char = int(remain_char)
                                if remain_char < len(text):
                                    return idx, True
                                else:
                                    convert_button = get_element_by_xpath(driver, convert_button_xpath)
                                    if convert_button:
                                        convert_button.click()
                                        sleep(6)
                                        if len(text) > 150:
                                            sleep(4)
                            else:
                                print(f"{thatbai} Có lỗi khi tải audio --> dừng tại {idx} --> {text}")
                                return None, None
                        if err > 20:
                            return idx, True
        print(f"{thanhcong} Hoàn thành chuyển file {input_txt_path} sang audio")
        return None, None
    except:
        getlog()
        return idx, True
    finally:
        if driver:
            driver.quit()

def text_to_speeed_by_evenlab_with_multi_email(input_txt_path, emails, start_idx):
    for email in emails:
        start_idx, is_change_email = text_to_speeed_by_evenlab(input_txt_path, email, start_idx)
        if not start_idx or not is_change_email:
            return

def move_file(input_folder, output_folder, idx):
    wav_files = get_file_in_folder_by_type(input_folder, file_type='.mp3')
    if not wav_files:
        return False
    if len(wav_files) > 1:
        for ggg in wav_files:
            ggg_path = os.path.join(input_folder, ggg)
            remove_file(ggg_path)
        return False
    for wav_file in wav_files:
        wav_file_path = os.path.join(input_folder, wav_file)
        wav_file_outpath = os.path.join(output_folder, f"{idx}.wav")
        try:
            shutil.move(wav_file_path, wav_file_outpath)
            return True
        except:
            getlog()
            return False
        
emails = [
    'LeeLopez1979911@hotmail.com',
    'JasonPotts19741119@hotmail.com',
]

input_txt_path = r"E:\Python\developping\review comic\test\du lieu train\evenlab\3.txt"
start_idx = 352

# text_to_speeed_by_evenlab_with_multi_email(input_txt_path=input_txt_path, emails=emails, start_idx=start_idx)





