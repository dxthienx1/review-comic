from common_function import *


def text_to_speeed_by_vbee(input_txt_path, email=None, start_idx=0, url="https://studio.vbee.vn/studio/text-to-speech"):
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
            if tttt.endswith(',') or tttt.endswith('?' or tttt.endswith('!')):
                tttt = f"{tttt[:-1]}."
            if not tttt.endswith('.'):
                tttt = tttt + '.'
            if tttt not in texts:
                texts.append(tttt)

        driver = get_driver_with_profile(target_email=email)
        driver.get(url)
        sleep(3)
        huy_xpath = get_xpath_by_multi_attribute('button', ['data-id="not-reload-prev-session"'])
        huy_ele = get_element_by_xpath(driver, huy_xpath)
        if huy_ele:
            huy_ele.click()
        sleep(3)
        close_popup_xpath = get_xpath('div', 'brz-popup2__close')
        close_popup_ele = get_element_by_xpath(driver, close_popup_xpath)
        if close_popup_ele:
            for _ in range(2):
                keyboard.press('alt')
                keyboard.press_and_release('tab')
                sleep(0.5)
                keyboard.release('alt')
                sleep(1)
            try:
                close_popup_ele.click()
                sleep(2)
            except:
                sleep(30)
                close_popup_ele = get_element_by_xpath(driver, close_popup_xpath)
                if close_popup_ele:
                    close_popup_ele.click()
        mp3_ele = get_element_by_text(driver, 'mp3', tag_name='span')
        if mp3_ele:
            mp3_ele.click()
            sleep(1)
            wav_ele = get_element_by_text(driver, 'wav', tag_name='span')
            if wav_ele:
                wav_ele.click()
                sleep(1)
        cnt = 0
        for idx, text in enumerate(texts):
            if idx < start_idx:
                continue
            if text in finish_texts:
                continue
            #đặt tên file
            name_xpath = get_xpath('input', 'input', contain=True)
            name_ele = get_element_by_xpath(driver, name_xpath)
            if name_ele:
                name_ele.clear()
                sleep(0.5)
                name_ele.send_keys(str(idx))
                sleep(1)
                #thêm nội dung
                content_xpath = get_xpath_by_multi_attribute('div', ['class="notranslate public-DraftEditor-content"', 'role="textbox"'])
                content_ele = get_element_by_xpath(driver, content_xpath)
                if content_ele:
                    content_ele.click()
                    sleep(0.5)
                    # Ctrl + A để chọn toàn bộ, rồi Delete
                    content_ele.send_keys(Keys.CONTROL, 'a')
                    sleep(0.2)
                    content_ele.send_keys(Keys.DELETE)
                    sleep(1)
                    content_ele.send_keys(f' {text} ')
                    sleep(1)
                    convert_button_xpath = get_xpath_by_multi_attribute('div', ['class="text-button-request"'])
                    convert_button = get_element_by_xpath(driver, convert_button_xpath)
                    if convert_button:
                        convert_button.click()
                        sleep(5)
                        
                        while True:
                            download_ele = get_element_by_text(driver, 'Tải xuống')
                            if download_ele:
                                download_ele.click()
                                sleep(3)
                                finish_texts.append(text)
                                with open(out_txt_path, "a", encoding="utf-8") as fff:
                                    fff.write(f"{str(idx)}\n{text}\n")
                                print(f"{thanhcong} {idx} --> {text}")
                                cnt = 0
                                sleep_random(1,5)
                                break
                            else:
                                in_process = get_element_by_text(driver, 'Đang xử lý')
                                if not in_process:
                                    toi_da_hieu_ele = get_element_by_text(driver, 'Tôi đã hiểu')
                                    if toi_da_hieu_ele:
                                        print(f"{thatbai} tài khoản {email}: từ không hợp lệ {text}")
                                        return None, None
                                    else:
                                        remain_xpath = get_xpath('p', 'remain-characters', contain=True)
                                        remain_ele = get_element_by_xpath(driver, remain_xpath, index=-1)
                                        if remain_ele:
                                            remain_char = remain_ele.text.replace('ký tự', '').strip()
                                            try:
                                                remain_char = int(remain_char)
                                            except:
                                                return None, None
                                            if remain_char < 50:
                                                driver.quit()
                                                sleep(2)
                                                return idx, True
                                        print(f"{thatbai} Tài khoản {email} có lỗi khi xuất audio.")
                                    driver.quit()
                                    return None, None
                                else:
                                    cnt += 1
                                    sleep(1)
                                    if cnt > 4:
                                        print(f"{thatbai} Tài khoản {email} có lỗi khi xuất audio --> tiến trình xử lý bị đứng.")
                                        driver.quit()
                                        return idx, True
    except:
        getlog()
        return None, None

def text_to_speeed_by_vbee_with_multi_email(input_txt_path, emails, start_idx):
    for email in emails:
        start_idx, is_change_email = text_to_speeed_by_vbee(input_txt_path, email, start_idx)
        if not start_idx or not is_change_email:
            return

# emails = [
#     'dxthien1@gmail.com',
#     'dxthien2@gmail.com',
#     'dxthienx11@gmail.com',
#     'themysteries.001@gmail.com',
#     'tranhangbk.001@gmail.com',
#     'dxthienx4@gmail.com',
# ]
emails = [
    'dxthienx1@gmail.com',
    # 'dxthienx2@gmail.com',
    'dxthienx5@gmail.com',
    'dxthienx10@gmail.com',
    'tranghangbk.002@gmail.com',
    'tranhangbk@gmail.com',
]

input_txt_path = "E:\\Du lieu huan luyen\\1.txt"
input_txt_path = "E:\\Python\\developping\\review comic\\test\\du lieu train\\huan luyen khoang lang\\1.txt"
start_idx = 77

text_to_speeed_by_vbee_with_multi_email(input_txt_path=input_txt_path, emails=emails, start_idx=start_idx)