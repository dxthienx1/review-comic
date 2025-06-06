
from common_function import *
# -------Sửa chính tả trong file txt và xuất ra file txt khác-------

def adjust_txt_file(old_txt, cnt=1, language='vi'):
    fol = os.path.dirname(old_txt)
    file_name = os.path.basename(old_txt).split('.')[0]
    new_txt = os.path.join(fol, f'{file_name}_1.txt')
    with open(old_txt, 'r', encoding='utf-8') as fff:
        lines = fff.readlines()
    with open(new_txt, 'w', encoding='utf-8') as ggg:
        for line in lines:
            if line and not line.strip().isdigit():
                if 'vbee' not in old_txt:
                    line = cleaner_text(line.strip(), is_loi_chinh_ta=True, language=language, is_conver_number=False)
                if not line or len(line) < 3:
                    continue
                if line.endswith(',') or line.endswith('?' or line.endswith('!')):
                    line = f"{line[:-1]}."
                if line and not line.strip().endswith('.'):
                    line = line.strip() + '.'
                ggg.write(f'{cnt}\n{line.strip()}\n')
                cnt += 1

cnt = 1
language = 'vi'
old_txt = r"E:\Python\developping\review comic\test\du lieu train\Phương Thảo\2.txt"
# adjust_txt_file(old_txt=old_txt, cnt=cnt, language=language)






#--------------tổng hợp các file sub và audio-----------------------------
def get_text_and_audio_in_folder(folder, txt_total='total.txt', audio_total_folder='total', language='vi'):
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
                                if 'vbee' not in txt_path:
                                    processed_text = cleaner_text(line_content, language=language, is_conver_number=False)
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
folder = r"E:\Python\developping\review comic\test\du lieu train\Hoàn Thành\vbee"
total_txt = os.path.join(folder, 'total.txt')
audio_total_folder = os.path.join(folder, 'total_audios')
language = 'vi'
# get_text_and_audio_in_folder(folder, total_txt, audio_total_folder, language=language)








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
def adjust_audio_speed(input_folder, speed=1.0, volume_factor=1.0):
    try:
        # Tạo thư mục đầu ra nếu chưa tồn tại
        output_folder = os.path.join(input_folder, 'audios_speed')
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


input_folder = r"E:\Python\developping\review comic\dataset\en_old\eval"
speed = 1
# adjust_audio_speed(input_folder, speed=speed, volume_factor=1)




#chuyển mp3 sang wav chuẩn training
def convert_mp3_to_wav_in_directory(input_folder, speed, volume_level=1.0):
    all_folders = get_file_in_folder_by_type(input_folder, file_type='')
    for folder in all_folders:
        mp3_folder = os.path.join(input_folder, folder)
        mp3_files = get_file_in_folder_by_type(mp3_folder, '.mp3') or []
        for filename in mp3_files:
            # Kiểm tra xem file có phải là MP3 hay không
            if filename.lower().endswith(".mp3"):
                mp3_path = os.path.join(mp3_folder, filename)
                output_folder = os.path.join(mp3_folder, 'out')
                os.makedirs(output_folder, exist_ok=True)
                wav_path = os.path.join(output_folder, filename[:-4] + ".wav")  # Đổi phần mở rộng từ .mp3 thành .wav

                # Cấu hình lệnh ffmpeg
                ffmpeg_cmd = [
                    "ffmpeg", 
                    "-y",  # ghi đè file nếu đã tồn tại
                    "-i", mp3_path,  # đường dẫn đến file MP3
                    "-ac", "1",  # 1 kênh âm thanh (mono)
                    "-ar", "24000",  # tần số mẫu (sampling rate) là 24kHz
                    "-filter:a", f"atempo={speed},volume={volume_level}",  # tốc độ phát lại
                    "-sample_fmt", "s16",  # định dạng mẫu âm thanh (16-bit)
                    wav_path  # đường dẫn file WAV đầu ra
                ]
                
                # Chạy lệnh ffmpeg để chuyển đổi
                if run_command_ffmpeg(ffmpeg_cmd):
                    print(f"Đã chuyển đổi {mp3_path} thành {wav_path}")

input_folder = r"D:\Train\Hoan Thanh\Ian Cartwell 1.07 x 1.1"
speed = 1.06
volume_level = 1
# convert_mp3_to_wav_in_directory(input_folder, speed, volume_level=volume_level)





#chuyển wav thường sang wav chuẩn training
def convert_wav_to_training_format(input_folder, speed=1.0, volume_level=1.0, trim_end=0):
    wav_files = get_file_in_folder_by_type(input_folder, '.wav') or []
    output_folder = os.path.join(input_folder, 'out')
    os.makedirs(output_folder, exist_ok=True)
    
    for idx, filename in enumerate(wav_files):
        wav_input = os.path.join(input_folder, filename)
        wav_output = os.path.join(output_folder, filename)

        # Nếu cần cắt 0.3s cuối thì cần lấy thời lượng file đầu vào
        if trim_end != 0:
            # Lấy duration của file input
            probe_cmd = [
                "ffprobe", "-v", "error",
                "-select_streams", "a:0",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                wav_input
            ]
            duration_str = subprocess.check_output(probe_cmd).decode().strip()
            duration = float(duration_str)
            trim_duration = max(0, duration - trim_end)  # Đảm bảo không âm

            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i", wav_input,
                "-ac", "1",                  # mono
                "-ar", "24000",              # sample rate 24kHz
                "-filter:a", f"atempo={speed},volume={volume_level}",
                "-t", f"{trim_duration}",    # cắt đi 0.3s cuối
                "-sample_fmt", "s16",        # 16-bit
                wav_output
            ]
        else:
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i", wav_input,
                "-ac", "1",
                "-ar", "24000",
                "-filter:a", f"atempo={speed},volume={volume_level}",
                "-sample_fmt", "s16",
                wav_output
            ]

        run_command_ffmpeg(ffmpeg_cmd)
        print(f"Đã chuẩn hóa {filename} thành {wav_output}")

input_folder = r"E:\Python\developping\XTTS-v2\dataset\en\ryan"
speed = 1.06
volume_level = 0.3
trim_end = 0
# convert_wav_to_training_format(input_folder, speed, volume_level, trim_end=trim_end)




#tăng tốc video
def speed_up_video_ffmpeg(input_path, speed=1.05):
    output_path = input_path.replace(".mp4", "_speedup.mp4")
    # Giới hạn tốc độ hợp lệ cho atempo (ffmpeg chỉ hỗ trợ 0.5 - 2.0, nên cần lặp nếu speed > 2)
    def atempo_filters(s):
        filters = []
        while s > 2.0:
            filters.append("atempo=2.0")
            s /= 2.0
        while s < 0.5:
            filters.append("atempo=0.5")
            s *= 2.0
        filters.append(f"atempo={s:.2f}")
        return ",".join(filters)

    # Video filter: setpts
    v_filter = f"setpts={1/speed}*PTS"
    a_filter = atempo_filters(speed)

    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-filter:v", v_filter,
        "-filter:a", a_filter,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-movflags", "+faststart",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Video đã được tăng tốc và lưu tại: {output_path}")
        return True
    except subprocess.CalledProcessError:
        print("❌ Lỗi khi tăng tốc video.")
        return False
input_path = ""
speed = 0.96
# speed_up_video_ffmpeg(input_path, speed=speed)






#Xử lý file txt trước khi dùng phần mềm tts mua
replacements = [
    ('🧡', ''), ('.“', '.'), ('”.', '.'), (',“', ','), ('”,', ','),
    (' “', ' '), ('” ', ' '), ('“', ' '), ('”', ' '), ('."', '.'),
    (',"', ','), (' "', ' '), ('" ', ' '), ('".', '.'), ('",', ','), (':.', '.'), (';', '.'),
    ('... ', '. '), ('...', '. '), ('***', ''), ('**', ''), ('*', ''), ('---', '')
]
def process_txt_file(folder):
    try:
        output_folder = os.path.join(folder, 'output_txt_files')
        os.makedirs(output_folder, exist_ok=True)
        txt_files = get_file_in_folder_by_type(folder, '.txt')
        for txt_file in txt_files:
            name = txt_file.replace('.txt', '_train.txt')
            new_txt_path = os.path.join(output_folder, txt_file.replace("'", '--'))
            train_txt_path = os.path.join(output_folder, name.replace("'", '--'))
            txt_path = os.path.join(folder, txt_file)
            texts = get_json_data(txt_path)
            final_texts = []
            temp = ''
            for text in texts:
                if not text:
                    continue
                if text.strip() == '***' or text.strip() == '**' or text.strip() == '—' or text.strip() == '.' or text.strip() == '---':
                    continue

                for old, new in replacements:
                    text = text.replace(old, new)

                text = text.strip()

                sub_texts = text.split('. ')
                sub_texts = [subtext.strip() for subtext in sub_texts if subtext.strip()]
                for sub_text in sub_texts:
                    if not sub_text.endswith(('.', '?', '!', ':')):
                        sub_text += '.'
                    if temp:
                        if temp.startswith('<break time='):
                            final_texts[-1] += temp
                            temp = ''
                            continue
                        sub_text = temp + ' ' + sub_text
                        temp = ""
                    if len(sub_text) < 20:
                        temp = sub_text
                    else:
                        final_texts.append(sub_text)

            if temp:
                if final_texts:
                    final_texts[-1] += ' ' + temp
                else:
                    final_texts.append(temp)
                
            with open(new_txt_path, 'w', encoding='utf-8') as fff:
                for final_text in final_texts:
                    fff.write(f"{final_text}\n\n")
            with open(train_txt_path, 'w', encoding='utf-8') as fff_train:
                cnt = 1
                for final_text in final_texts:
                    fff_train.write(f"{cnt}\n{final_text}\n")
                    cnt += 1
            remove_or_move_file(txt_path)
            
    except:
        getlog()

folder = r"D:\youtube\Truyen tieng anh\SHORT STORIES"
# process_txt_file(folder)


