from common_function import *

def prepare_xtts_training_data(base_dir, speaker_name, is_eval=False):
    if is_eval:
        wavs_dir=r'E:\Python\developping\review comic\dataset\en\eval'
        csv_path=r'E:\Python\developping\review comic\dataset\en\eval.csv'
    else:
        # wavs_dir=r'E:\Python\developping\XTTS-v2\dataset\en\ryan'
        wavs_dir=r'E:\Python\developping\XTTS-v2\dataset\en\wavs'
        csv_path=r'E:\Python\developping\XTTS-v2\dataset\en\train.csv'

    os.makedirs(wavs_dir, exist_ok=True)
    if not check_folder(base_dir):
        return
    
    # Tìm số index lớn nhất trong thư mục wavs để đặt tên tiếp theo
    existing_wavs = [
        int(f.split('.')[0]) for f in os.listdir(wavs_dir)
        if f.endswith('.wav') and f.split('.')[0].isdigit()
    ]
    index = max(existing_wavs, default=0) + 1

    txt_files = get_file_in_folder_by_type(base_dir, '.txt') or []
    # Mở file CSV ở chế độ nối thêm
    with open(csv_path, mode='a', encoding='utf-8', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter='|')

        for file in txt_files:
            if file.endswith('.txt'):
                txt_path = os.path.join(base_dir, file)
                audio_folder = os.path.join(base_dir, file.replace('.txt', ''))
                wav_files = get_file_in_folder_by_type(audio_folder, '.wav', noti=False) or None
                if not wav_files:
                    audio_folder = os.path.join(audio_folder, 'out')
                    if not os.path.isdir(audio_folder):
                        print(f"[WARNING] Không tìm thấy thư mục audio tương ứng: {audio_folder}")
                        return
                    wav_files = get_file_in_folder_by_type(audio_folder, '.wav') or None

                try:
                    with open(txt_path, 'r', encoding='utf-8') as f:
                        lines = [line.strip() for line in f if line.strip()]

                    last_audio_number = None

                    for line in lines:
                        if is_eval:
                            if len(line) > 250:
                                continue
                        else:
                            if len(line) > 300:
                                continue

                        if line.strip().isdigit():
                            last_audio_number = line  # lưu lại số thứ tự audio
                        else:
                            if last_audio_number is None:
                                print(f"[WARNING] Gặp dòng text nhưng không có số thứ tự audio trước đó: {line}")
                                continue

                            audio_file = os.path.join(audio_folder, f"{last_audio_number}.wav")
                            if not os.path.exists(audio_file):
                                print(f"[WARNING] Không tìm thấy audio: {audio_file}")
                                continue

                            # 1. Ghi bản gốc
                            wav_name_1 = f"{index}.wav"
                            shutil.copy(audio_file, os.path.join(wavs_dir, wav_name_1))
                            if is_eval:
                                writer.writerow([f"eval/{wav_name_1}", line, speaker_name])
                            else:
                                writer.writerow([f"wavs/{wav_name_1}", line, speaker_name])
                            index += 1

                            # 2. Ghi bản chuẩn hóa
                            normalized = cleaner_text(line, language='en')
                            if line != normalized:
                                wav_name_2 = f"{index}.wav"
                                shutil.copy(audio_file, os.path.join(wavs_dir, wav_name_2))
                                if is_eval:
                                    writer.writerow([f"eval/{wav_name_2}", normalized, speaker_name])
                                else:
                                    writer.writerow([f"wavs/{wav_name_2}", normalized, speaker_name])
                                index += 1

                            # Reset để tránh lỗi khi text tiếp theo không có số tương ứng
                            last_audio_number = None

                except Exception as e:
                    print(f"[ERROR] Lỗi khi xử lý file {txt_path}: {e}")


# prepare_xtts_training_data(
#     base_dir= r'D:\Train\Hoan Thanh\Ian Cartwell 1.07 x 1.1',
#     speaker_name='ian_cartwell',
#     is_eval=False
# )





#Chuẩn hóa Âm Lượng audio
def get_mean_volume(filepath):
    """Đo mean_volume bằng ffmpeg volumedetect"""
    try:
        result = subprocess.run(
            ['ffmpeg', '-i', filepath, '-filter:a', 'volumedetect', '-f', 'null', 'NUL' if os.name == 'nt' else '/dev/null'],
            stderr=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            text=True
        )
        for line in result.stderr.splitlines():
            if "mean_volume:" in line:
                vol = float(line.strip().split(":")[1].replace(" dB", "").strip())
                return vol
    except Exception as e:
        print(f"Lỗi đo âm lượng file {filepath}: {e}")
    return None

def normalize_to_reference(folder, ref_volume=-22, speed=1.0, file_type='.wav'):
    try:
        out_folder = f"{folder}_out"
        finish_folder = f"{folder}_done"
        os.makedirs(out_folder, exist_ok=True)
        os.makedirs(finish_folder, exist_ok=True)
        wav_files = get_file_in_folder_by_type(folder, file_type) or []
        for file in wav_files:
            path = os.path.join(folder, file)
            out_path = os.path.join(out_folder, file)
            finish_path = os.path.join(finish_folder, file)

            cur_volume = get_mean_volume(path)
            if cur_volume is None:
                continue

            diff_db = ref_volume - cur_volume
            new_file = os.path.join(out_folder, file)
            if abs(diff_db) > 1:
                cmd = [
                    'ffmpeg', '-y',
                    '-i', path,
                    '-filter:a', f'volume={diff_db:.2f}dB,atempo={speed:.2f}',
                    new_file
                ]
                if run_command_ffmpeg(cmd):
                    print(f"🎧 {file}: {cur_volume:.2f} dB → {ref_volume:.2f} dB  ✅ OK")
                    shutil.move(path, finish_path)
                else:
                    print(f"❌ {file}: Lỗi khi điều chỉnh")
                    return
            else:
                print(f"   ---> File {path} có âm lượng {cur_volume} ---> không lệch nhiều so với {ref_volume}")
                shutil.copy(path, new_file)
                shutil.move(path, finish_path)
    except:
        getlog()

# 🔧 GỌI THỰC TẾ
audio_folder   = r'D:\youtube\Truyen tieng anh\HORROR\output_txt_files\The Midnight Funeral Dream'
speed = 1
ref_volume = -24
file_type = '.mp3'

normalize_to_reference(audio_folder, ref_volume, speed, file_type=file_type)




