from common_function import *

img_path = "E:/Python/developping/review comic/test/fffffff/201.png"
output_audio_path = "E:/Python/developping/review comic/test/fffffff/output/201.wav"
output_video_path = "E:/Python/developping/review comic/test/fffffff/output/201.mp4"
command = f'ffmpeg -y -loop 1 -i "{img_path}" -i "{output_audio_path}" -c:v libx264 -tune stillimage -c:a aac -b:a 192k -shortest "{output_video_path}"'
run_command_ffmpeg(command)
