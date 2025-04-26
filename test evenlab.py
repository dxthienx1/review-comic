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
        out_txt_path = os.path.join(folder, f"{file_name[:-4]}_tts.txt")
        finish_texts = []
        all_texts = get_json_data(input_txt_path)
        all_texts = [ttt.lower().strip() for ttt in all_texts if ttt.strip() and len(ttt.strip()) > 1]
        texts = []
        for tttt in all_texts:
            if tttt.endswith(','):
                tttt = f"{tttt[:-1]}."
            if not tttt.endswith('.'):
                tttt = tttt + '.'
            if tttt not in texts:
                texts.append(tttt)

        driver = get_driver_with_profile(target_email=email)
        driver.get(url)
        sleep(3)
        textarea_xpath = get_xpath_by_multi_attribute('textarea', ['aria-label="Main textarea"'])
        textarea = get_element_by_xpath(driver, textarea_xpath)
        if not textarea:
            print(f"Không tìm thấy chỗ nhập nội dung.")
            return
        sleep(3)
   
        cnt = 0
        for idx, text in enumerate(texts):
            if idx < start_idx:
                continue
            if text in finish_texts:
                continue
            # content_ele.click()
            # sleep(0.5)
            # # Ctrl + A để chọn toàn bộ, rồi Delete
            # content_ele.send_keys(Keys.CONTROL, 'a')
            # sleep(0.2)
            # content_ele.send_keys(Keys.DELETE)
            # sleep(1)
            # content_ele.send_keys(f' {text} ')
            # sleep(1)
            textarea.clear()
            sleep(0.5)
            textarea.send_keys(text)
            sleep(0.5)
            convert_button_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Generate speech (Shift+Enter)"'])
            convert_button = get_element_by_xpath(driver, convert_button_xpath)
            if convert_button:
                convert_button.click()
                sleep(6)
                err = 0
                is_break = False
                while True:
                    if is_break:
                        break
                    tai_xpath = get_xpath_by_multi_attribute('button', ['aria-label="Download"'])
                    tai_ele = get_element_by_xpath(driver, tai_xpath)
                    if tai_ele:
                        tai_ele.click()
                        sleep(3)
                        in_fol = "C:\\Users\\dxthi\\Downloads"
                        out_fol = os.path.join(folder, 'out_files')
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
                            if err > 10:
                                print(f"{thatbai} Lỗi tại idx {idx} --> {text}")
                                return idx, True
                    else:
                        sleep(2)
                        err += 1
                        if err > 3:
                            remain_char = get_element_by_text(driver, 'credits remaining', tag_name='span', contain=True)
                            if remain_char:
                                remain_char = remain_char.text.replace('credits remaining', '').replace(',', '').replace('.', '').strip()
                                remain_char = int(remain_char)
                                if remain_char < len(text):
                                    return idx, True
                            else:
                                print(f"{thatbai} Có lỗi khi tải audio --> dừng tại {idx} --> {text}")
                                return None, None
        print(f"{thanhcong} Hoàn thành chuyển file {input_txt_path} sang audio")
        return None, None
    except:
        getlog()
        return None, None

def text_to_speeed_by_evenlab_with_multi_email(input_txt_path, emails, start_idx):
    for email in emails:
        start_idx, is_change_email = text_to_speeed_by_evenlab(input_txt_path, email, start_idx)
        if not start_idx or not is_change_email:
            return

def move_file(input_folder, output_folder, idx):
    wav_files = get_file_in_folder_by_type(input_folder, file_type='.mp3')
    if not wav_files:
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
    'dxthienx5@gmail.com',
    'dxthienx10@gmail.com',
    'tranghangbk.002@gmail.com',
    'tranhangbk@gmail.com',
    'badboymmo1901@gmail.com',
    'dxthien4@gmail.com',
    'dxthien5@gmail.com',
    'themysteries.001@gmail.com',
    'tranhangbk.001@gmail.com',
    'dxthien1@gmail.com',
    'dxthien2@gmail.com',
    'dxthienx11@gmail.com',
    'dxthienx2@gmail.com',
    'dxthienx4@gmail.com',
]

# input_txt_path = "E:\\Du lieu huan luyen\\1.txt"
input_txt_path = "E:\\Python\\developping\\review comic\\test\\du lieu train\\vbee\\1.txt"
start_idx = 405

text_to_speeed_by_evenlab_with_multi_email(input_txt_path=input_txt_path, emails=emails, start_idx=start_idx)