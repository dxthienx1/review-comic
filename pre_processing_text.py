from common_function import *

def add_txt_to_metadata(txt_file, csv_file, start_idx=1, type_audio='wav', speaker_name='vi_female', is_eval=False, language='vi'):
    import csv
    try:
        file_exists = os.path.isfile(csv_file)
        with open(txt_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
 
        with open(csv_file, 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                writer.writerow(["audio_file", "text", "speaker_name"])
            for i, line in enumerate(lines):
                try:
                    text = line.strip().lower()
                    if not text or text.isdigit():
                        continue
                    if is_eval:
                        writer.writerow([f"eval/eval_{start_idx}.{type_audio}", text, speaker_name])
                    else:
                        writer.writerow([f"wavs/{start_idx}.{type_audio}", text, speaker_name])
                    start_idx += 1
                except Exception as e:
                    print(f"Lỗi khi xử lý dòng {i + 1}: {e}")
                    return
        
        print(f"Hoàn thành! Dữ liệu đã được ghi vào {csv_file}")
    except Exception as e:
        getlog()

txt_file_path = r"E:\Python\developping\review comic\test\du lieu train\vbee\2.txt"
language = 'en'
speaker_name='ffffffff'
start_idx = 31113
is_eval = True

if language == 'vi':
    if is_eval:
        metadata_path = os.path.join(current_dir, 'dataset', 'vietnam', 'eval.csv')
    else:
        metadata_path = os.path.join(current_dir, 'dataset', 'vietnam', 'train.csv')
elif language == 'en':
    if is_eval:
        metadata_path = os.path.join(current_dir, 'dataset', 'en', 'eval.csv')
    else:
        metadata_path = os.path.join(current_dir, 'dataset', 'en', 'train.csv')

# add_txt_to_metadata(txt_file_path, metadata_path, start_idx, speaker_name=speaker_name, is_eval=is_eval, language=language)




#edit file csv
def add_voice_to_csv(input_file, output_file, voice_tag="vi_female"):
    try:
        # Đọc nội dung file CSV
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            rows = [row for row in reader]
        
        # Thêm voice tag vào cuối mỗi dòng
        updated_rows = []
        for i, row in enumerate(rows):
            if i == 0:  # Header đã sửa ở bước trên
                row = ["audio_file", "text", "speaker_name"]
                updated_rows.append(row)
            else:
                row[0] = f'eval/eval_{i}.wav'
                updated_rows.append([row[0], row[1], voice_tag])
        
        # Ghi nội dung mới vào file đầu ra
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            writer.writerows(updated_rows)
    except:
        getlog()















#edit file csv
def change_index_csv_train(input_file, output_file, start_idx=1, speaker_name="jameson", is_eval=False):
    try:
        # Đọc nội dung file CSV
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            rows = [row for row in reader if row]
        
        # Thêm voice tag vào cuối mỗi dòng
        updated_rows = []
        for i, row in enumerate(rows):
            if i == 0:  # Header đã sửa ở bước trên
                row = ["audio_file", "text", "speaker_name"]
                updated_rows.append(row)
            else:
                row[0] = f'eval/{start_idx}.wav' if is_eval else f'wavs/{start_idx}.wav'
                updated_rows.append([row[0], row[1], speaker_name])
                start_idx += 1
        
        # Ghi nội dung mới vào file đầu ra
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            writer.writerows(updated_rows)
        
    
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# Sử dụng hàm
input_csv = r"E:\Python\developping\review comic\dataset\en\2.csv"
output_csv = r"E:\Python\developping\review comic\dataset\en\2_edit.csv"
speaker_name = 'ian_cartwell'
is_eval=True
start_idx = 130701
change_index_csv_train(input_csv, output_csv, start_idx=start_idx, speaker_name=speaker_name, is_eval=is_eval)






#lọc file trên 250 ký tự
def move_long_audio(input_file, output_file, max_len=250, is_eval=False):
    try:
        current_folder = os.path.dirname(input_file)

        # Xác định thư mục wav và thư mục đích dựa vào is_eval
        wav_folder = os.path.join(current_folder, 'eval' if is_eval else 'wavs')
        long_wav_folder = os.path.join(current_folder, 'long_eval' if is_eval else '_long_wavs')
        os.makedirs(long_wav_folder, exist_ok=True)

        # Đọc file CSV gốc
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            rows = [row for row in reader]

        header = ["audio_file", "text", "speaker_name"]
        valid_rows = [header]
        long_text_rows = [header]

        new_index = 1

        for i, row in enumerate(rows):
            if i == 0:
                continue  # Bỏ qua header gốc

            audio_path, text, voice_tag = row[0], row[1], row[2]

            # Xử lý dấu câu
            if text.endswith(','):
                text = text[:-1] + '.'
            if not text.endswith('.'):
                text += '.'

            full_audio_path = os.path.join(current_folder, audio_path)

            if len(text) > max_len or len(text) < 10:
                # Di chuyển file âm thanh quá dài
                if os.path.exists(full_audio_path):
                    shutil.move(full_audio_path, os.path.join(long_wav_folder, os.path.basename(audio_path)))
                else:
                    print(f"[!] Không tìm thấy file âm thanh: {full_audio_path}")
                long_text_rows.append([audio_path, text, voice_tag])
            else:
                # Đổi tên file audio mới
                new_filename = f"{'eval_' if is_eval else ''}{new_index}.wav"
                new_audio_path = os.path.join(wav_folder, new_filename)

                if os.path.exists(full_audio_path):
                    shutil.move(full_audio_path, new_audio_path)
                else:
                    print(f"[!] Không tìm thấy file âm thanh: {full_audio_path}")
                    continue

                # Đường dẫn mới ghi vào file CSV
                new_audio_path_csv = f"{'eval' if is_eval else 'wavs'}/{new_filename}"
                valid_rows.append([new_audio_path_csv, text, voice_tag])
                new_index += 1

        # Ghi file chứa các dòng dài
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerows(long_text_rows)

        # Ghi đè lại file CSV gốc
        with open(input_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerows(valid_rows)

        print(f"[✓] Đã xử lý: {len(valid_rows)-1} dòng hợp lệ giữ lại, {len(long_text_rows)-1} dòng dài bị di chuyển.")

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# Sử dụng hàm
input_csv = r"E:\Python\developping\review comic\dataset\vietnam\train.csv"
output_csv = r"E:\Python\developping\review comic\dataset\vietnam\long_train.csv"
is_eval= False
# move_long_audio(input_csv, output_csv, is_eval=is_eval)



#đánh lại số thứ tự cho file csv
def edit_index_csv_file(input_file, is_eval=False):
    try:
        current_folder = os.path.dirname(input_file)

        # Xác định thư mục wav và thư mục đích dựa vào is_eval
        wav_folder = os.path.join(current_folder, 'eval' if is_eval else 'wavs')
        long_wav_folder = os.path.join(current_folder, 'long_eval' if is_eval else '_long_wavs')
        os.makedirs(long_wav_folder, exist_ok=True)

        # Đọc file CSV gốc
        with open(input_file, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile, delimiter='|')
            rows = [row for row in reader]

        header = ["audio_file", "text", "speaker_name"]
        valid_rows = [header]

        for i, row in enumerate(rows):
            if i == 0:
                continue  # Bỏ qua header gốc

            audio_path, text, voice_tag = row[0], row[1], row[2]

            # Đổi tên file audio mới
            new_filename = f"{'eval_' if is_eval else ''}{i}.wav"
            # Đường dẫn mới ghi vào file CSV
            new_audio_path_csv = f"{'eval' if is_eval else 'wavs'}/{new_filename}"
            valid_rows.append([new_audio_path_csv, text, voice_tag])

        output_file = input_file.replace('.csv', '_new.csv')
        # Ghi đè lại file CSV gốc
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter='|')
            writer.writerows(valid_rows)

    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# Sử dụng hàm
input_csv = r"E:\Python\developping\review comic\dataset\vietnam\train.csv"
is_eval= False
# edit_index_csv_file(input_csv, is_eval=is_eval)