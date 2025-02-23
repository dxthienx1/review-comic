from common_function import *

input_audio_path = "E:/Python/developping/review comic/test/fffffff/merge_audios/1.wav"
output_video_path = "E:/Python/developping/review comic/test/fffffff/output/740.mp4"

# Tốc độ phát mong muốn
speed = 1.1  
temp_audio_path = "E:/Python/developping/review comic/test/fffffff/merge_audios/1_speed.wav"
img_path = "E:/Python/developping/review comic/test/fffffff/1.png"

# Lệnh FFmpeg thay đổi tốc độ âm thanh
command_audio = f'ffmpeg -y -i "{input_audio_path}" -filter:a "atempo={speed}" -c:a aac -b:a 192k "{temp_audio_path}"'
run_command_ffmpeg(command_audio, False)

# Kiểm tra nếu file âm thanh mới đã được tạo thành công
if os.path.exists(temp_audio_path):
    print("✅ Âm thanh đã được xử lý xong!")

    # Lệnh FFmpeg để ghép ảnh với âm thanh đã chỉnh sửa
    command_video = f'ffmpeg -y -loop 1 -i "{img_path}" -i "{temp_audio_path}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -shortest "{output_video_path}"'
    run_command_ffmpeg(command_video, False)
    if os.path.exists(temp_audio_path):
        os.remove(temp_audio_path)
    print("✅ Video đã được tạo thành công!")
else:
    print("❌ Lỗi trong quá trình xử lý âm thanh!")
