from common_function import *


def export_video(folder_story, background_folder, audio_type='.mp3'):
    try:
        if not check_folder(background_folder, noti=False) or not check_folder(folder_story, noti=False):
            print(f"{thatbai} Thư mục không hợp lệ.")
            return

        background_music = get_file_in_folder_by_type(background_folder, audio_type) or []
        background_videos = get_file_in_folder_by_type(background_folder, '.mp4') or []
        if len(background_music) == 0:
            print(f"{thatbai} Không tìm thấy file nhạc nền.")
            return
        if len(background_videos) == 0:
            print(f"{thatbai} Không tìm thấy file video nền.")
            return
        background_music_path = os.path.join(background_folder, random.choice(background_music))
        background_video_path = os.path.join(background_folder, random.choice(background_videos))

        input_audios = get_file_in_folder_by_type(folder_story, audio_type)
        for audio_file in input_audios:
            input_audio_path = os.path.join(folder_story, audio_file)
            name = audio_file.replace(audio_type, '')
            output_folder = os.path.join(folder_story, name)
            os.makedirs(output_folder, exist_ok=True)
            audio_info = get_audio_info(input_audio_path)
            duration = audio_info.get('duration', None)
            sample_rate = audio_info.get('sample_rate', 44100)
            channels = audio_info.get('channels', 2)
            if not duration:
                print(f"Có lỗi khi lấy thông tin audio {audio_file}")
                return
            duration = float(duration)
            # Lặp và chuyển nhạc nền theo thông số giọng nói
            looped_music_path = "temp_looped_music.mp3"
            loop_cmd = [
                "ffmpeg", "-y",
                "-stream_loop", "-1",
                "-i", background_music_path,
                "-t", str(duration),
                "-ar", str(sample_rate),
                "-ac", str(channels),
                "-c:a", "libmp3lame",
                "-q:a", "2",  # Chất lượng cao
                looped_music_path
            ]
            if not run_command_ffmpeg(loop_cmd):
                print(f"{thatbai} Có lỗi khi tạo file {looped_music_path}")
                return

            output_video_path = os.path.join(output_folder, audio_file.replace(audio_type, '.mp4'))
            mixed_audio_path = "mixed_audio.mp3"
            mix_audio_cmd = [
                "ffmpeg", "-y",
                "-i", input_audio_path,
                "-i", looped_music_path,
                "-filter_complex",
                f"[0:a]aresample={sample_rate},volume=2,pan=mono|c0=c0[va]; "
                f"[1:a]aresample={sample_rate},volume=0.5,pan=mono|c0=c0[bg]; "
                "[va][bg]amix=inputs=2:duration=first:dropout_transition=0",
                "-ar", str(sample_rate),
                "-ac", str(channels),
                "-c:a", "libmp3lame",
                "-q:a", "2",  # Giữ chất lượng cao
                mixed_audio_path
            ]
            if run_command_ffmpeg(mix_audio_cmd):
                remove_or_move_file(input_audio_path, finish_folder=output_folder)
                remove_file(looped_music_path)
                input_audio_path = mixed_audio_path

            input_flags = ["-stream_loop", "-1", "-i", background_video_path]
            if torch.cuda.is_available():
                print("---> Dùng GPU để xuất video...")
                command = ["ffmpeg", "-y", *input_flags, "-i", input_audio_path, "-c:v", "h264_nvenc", "-cq", "30", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest", "-threads", "4", output_video_path]
            else:
                input_str = ' '.join(input_flags)
                command = f'ffmpeg -y {input_str} -i "{input_audio_path}" -c:v libx264 -pix_fmt yuv420p -tune stillimage -c:a aac -b:a 192k -shortest -threads 4 "{output_video_path}"'
            if run_command_ffmpeg(command, False):
                remove_file(mixed_audio_path)
                txt_path = os.path.join(folder_story, f"{name}.txt")
                if os.path.exists(txt_path):
                    remove_or_move_file(txt_path, finish_folder=output_folder)
                temp_audios = get_file_in_folder_by_type(output_folder, '.mp3') or []
                for temp_audio in temp_audios:
                    temp_audio_path = os.path.join(output_folder, temp_audio)
                    remove_file(temp_audio_path)
                print(f'{thanhcong} Xuất video thành công: {output_video_path}')

    except:
        getlog()
folder = r"E:\Python\developping\review comic\test\Truyen tieng anh\HISTORY STORY FOR SLEEP"
background_folder = r"E:\Python\developping\review comic\test\Truyen tieng anh\HISTORY STORY FOR SLEEP\fire"
export_video(folder, background_folder)