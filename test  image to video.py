import os
import subprocess

def adjust_audio_speed(input_folder, output_folder, speed=0.97):
    try:
        # Tạo thư mục đầu ra nếu chưa tồn tại
        os.makedirs(output_folder, exist_ok=True)
        
        # Duyệt qua tất cả các file trong thư mục
        for file_name in os.listdir(input_folder):
            if file_name.endswith(".wav"):
                input_path = os.path.join(input_folder, file_name)
                output_path = os.path.join(output_folder, file_name)
                
                # Command để giảm tốc độ phát bằng ffmpeg
                ffmpeg_command = [
                    'ffmpeg', '-i', input_path, '-filter:a', f"atempo={speed}",
                    '-vn', output_path, '-y', '-loglevel', 'quiet'
                ]
                
                # Thực thi command
                subprocess.run(ffmpeg_command)
                print(f"Đã xử lý: {file_name}")
                
    except Exception as e:
        print(f"Có lỗi xảy ra: {e}")

# Ví dụ sử dụng
input_folder = "E:\\Python\\developping\\review comic\\dataset\\vietnam\\wavs"  # Thư mục chứa file .wav gốc
output_folder = "E:\\Python\\developping\\review comic\\dataset\\vietnam\\out"  # Thư mục lưu file .wav đã giảm tốc độ
os.makedirs(output_folder, exist_ok=True)
adjust_audio_speed(input_folder, output_folder)