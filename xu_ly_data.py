
from common_function import *
# -------Sửa chính tả trong file txt và xuất ra file txt khác-------

def adjust_txt_file(old_txt, cnt=1):
    fol = os.path.dirname(old_txt)
    file_name = os.path.basename(old_txt).split('.')[0]
    new_txt = os.path.join(fol, f'{file_name}_1.txt')
    with open(old_txt, 'r', encoding='utf-8') as fff:
        lines = fff.readlines()
    with open(new_txt, 'w', encoding='utf-8') as ggg:
        for line in lines:
            if line and not line.strip().isdigit():
                if 'vbee' not in old_txt:
                    line = cleaner_text(line.strip(), is_loi_chinh_ta=True, is_conver_number=True)
                if not line or len(line) < 3:
                    continue
                if line.endswith(',') or line.endswith('?' or line.endswith('!')):
                    line = f"{line[:-1]}."
                # if line and not line.strip().endswith('.'):
                #     line = line + '.'
                ggg.write(f'{cnt}\n{line.strip()}\n')
                cnt += 1

cnt = 1
old_txt = "E:\\Python\\developping\\review comic\\test\\du lieu train\\Glinnn\\3.txt"
adjust_txt_file(old_txt=old_txt, cnt=cnt)






#--------------tổng hợp các file sub và audio-----------------------------
def get_text_and_audio_in_folder(folder, txt_total='total.txt', audio_total_folder='total'):
    os.makedirs(audio_total_folder, exist_ok=True)
    txt_files = get_file_in_folder_by_type(folder, '.txt')
    unique_lines = set()  # Dùng set để lưu các dòng đã ghi (tìm kiếm nhanh hơn)
    index = 0
    
    try:
        with open(txt_total, mode='w', encoding='utf-8') as total:  # Ghi đè file tổng
            for txt_f in txt_files:
                txt_path = os.path.join(folder, txt_f)
                file_name = os.path.splitext(txt_f)[0]
                audio_folder = os.path.join(folder, file_name)
                audios = get_file_in_folder_by_type(audio_folder, '.wav')
                try:
                    with open(txt_path, mode='r', encoding='utf-8') as fff:
                        lines = fff.readlines()
                    i_au = 0
                    first_index = 0
                    is_next = False
                    for line in lines:
                        if is_next:
                            is_next = False
                            continue
                        line_content = line.strip()
                        # Kiểm tra nếu không phải số
                        if not line_content.isdigit():
                            if i_au >= len(audios):  # Kiểm tra số lượng audio
                                print(f"{canhbao} Không đủ file audio cho file {txt_f}")
                                break
                            
                            if line_content not in unique_lines and len(line_content) < max_lenth_text:
                                index += 1
                                processed_text = line_content.strip().lower()
                                processed_text = cleaner_text(line_content, is_loi_chinh_ta=True, is_conver_number=True)
                                total.write(f'{index}\n{processed_text}\n')
                                unique_lines.add(line_content)  # Thêm vào set để tránh trùng lặp
                                audio_path = os.path.join(audio_folder, audios[i_au])
                                new_au_path = os.path.join(audio_total_folder, f'{index}.wav')
                                shutil.copy(audio_path, new_au_path)
                            i_au += 1
                        else:
                            if int(line_content) == first_index:
                                is_next = True
                            first_index = int(line_content)
                except Exception as e:
                    print(f"Lỗi khi xử lý file {txt_f}: {e}")
    except Exception as e:
        print(f"Lỗi khi ghi file tổng {txt_total}: {e}")
folder = "E:\\Python\\developping\\review comic\\test\\du lieu train\\Hoàn Thành"
total_txt = os.path.join(folder, 'total.txt')
audio_total_folder = os.path.join(folder, 'total_audios')
# get_text_and_audio_in_folder(folder, total_txt, audio_total_folder)








#---------kiểm tra và xử lý file metadata để đúng chuẩn training XTTS-v2 ---------------------------
def add_voice_to_csv(input_file, voice_tag="vi_female"):
    cur_dir = os.path.dirname(input_file)
    name = os.path.basename(input_file)
    output_dir = os.path.join(cur_dir, 'output')
    os.makedirs(output_dir, exist_ok=True)
    wavs_dir = os.path.join(output_dir, 'wavs')
    os.makedirs(wavs_dir, exist_ok=True)
    output_file = os.path.join(output_dir, name)
    index = 0
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
                text = row[1]
                if len(text) >= max_lenth_text or len(text) < 20:
                    continue
                else:
                    audio_path = os.path.join(cur_dir, row[0])
                    if not os.path.exists(audio_path):
                        continue
                    index += 1
                    new_path = os.path.join(wavs_dir, f'{index}.wav')
                    shutil.copy(audio_path, new_path)
                    row[0] = f'wavs/{index}.wav'
                updated_rows.append([row[0], row[1], voice_tag])
        
        # Ghi nội dung mới vào file đầu ra
        with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            writer.writerows(updated_rows)
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

# # Sử dụng hàm
# input_csv = "E:\\Python\\developping\\review comic\\dataset\\vietnam\\train.csv"
# add_voice_to_csv(input_csv)





#------------Thay đổi tốc độ audio hàng loạt---------
def adjust_audio_speed(input_folder, output_folder, speed=1.0, volume_factor=1.0):
    try:
        # Tạo thư mục đầu ra nếu chưa tồn tại
        os.makedirs(output_folder, exist_ok=True)
        audios = get_file_in_folder_by_type(input_folder, '.wav') or []
        # Duyệt qua tất cả các file trong thư mục
        for file_name in audios:
            if file_name.endswith(".wav"):
                input_path = os.path.join(input_folder, file_name)
                output_path = os.path.join(output_folder, file_name)
                
                # Command để thay đổi tốc độ và tăng âm lượng
                ffmpeg_command = [
                    'ffmpeg', '-i', input_path,
                    '-filter:a', f"atempo={speed},volume={volume_factor}",
                    '-vn', output_path, '-y', '-loglevel', 'quiet'
                ]
                
                # Thực thi command
                run_command_ffmpeg(ffmpeg_command)
                print(f"Đã xử lý: {file_name}")
                
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")


input_folder = "E:\\Python\\developping\\review comic\\test\\du lieu train\\last data\\vb"
output_folder = "E:\\Python\\developping\\review comic\\test\\du lieu train\\last data\\vb_1"
# adjust_audio_speed(input_folder, output_folder, speed=1.1, volume_factor=1.05)




#chuyển mp3 sang wav chuẩn training
def convert_mp3_to_wav_in_directory(input_folder, speed):
    mp3_files = get_file_in_folder_by_type(input_folder, '.mp3') or []
    for filename in mp3_files:
        # Kiểm tra xem file có phải là MP3 hay không
        if filename.endswith(".mp3"):
            mp3_path = os.path.join(input_folder, filename)
            wav_path = os.path.join(input_folder, filename[:-4] + ".wav")  # Đổi phần mở rộng từ .mp3 thành .wav

            # Cấu hình lệnh ffmpeg
            ffmpeg_cmd = [
                "ffmpeg", 
                "-y",  # ghi đè file nếu đã tồn tại
                "-i", mp3_path,  # đường dẫn đến file MP3
                "-ac", "1",  # 1 kênh âm thanh (mono)
                "-ar", "24000",  # tần số mẫu (sampling rate) là 24kHz
                "-filter:a", f"atempo={speed}",  # tốc độ phát lại
                "-sample_fmt", "s16",  # định dạng mẫu âm thanh (16-bit)
                wav_path  # đường dẫn file WAV đầu ra
            ]
            
            # Chạy lệnh ffmpeg để chuyển đổi
            run_command_ffmpeg(ffmpeg_cmd)
            print(f"Đã chuyển đổi {mp3_path} thành {wav_path}")

input_folder = "E:\\Python\\developping\\review comic\\test\\du lieu train\\huan luyen khoang lang\\New folder\\10_chua"
speed = 1.0 
# convert_mp3_to_wav_in_directory(input_folder, speed)





#chuyển wav thường sang wav chuẩn training
def convert_wav_to_training_format(input_folder, speed):
    wav_files = get_file_in_folder_by_type(input_folder, '.wav') or []
    output_folder = os.path.join(input_folder, 'out')
    os.makedirs(output_folder, exist_ok=True)
    for filename in wav_files:
        wav_input = os.path.join(input_folder, filename)
        wav_output = os.path.join(output_folder, filename)

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-i", wav_input,
            "-ac", "1",              # mono
            "-ar", "24000",          # sample rate 24kHz
            "-filter:a", f"atempo={speed}",  # playback speed
            "-sample_fmt", "s16",    # 16-bit sample format
            wav_output
        ]

        run_command_ffmpeg(ffmpeg_cmd)
        print(f"Đã chuẩn hóa {filename} thành {wav_output}")

input_folder = "E:\\Python\\developping\\review comic\\test\\du lieu train"
speed = 1.04
# convert_wav_to_training_format(input_folder, speed)