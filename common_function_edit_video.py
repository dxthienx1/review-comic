from common_function import *
from common_function_CTK import *


def convert_time_to_seconds(time_str):
    """Chuyển đổi thời gian từ định dạng hh:mm:ss hoặc mm:ss hoặc ss thành giây."""
    list_time = time_str.split(':')
    cnt = len(list_time)
    if cnt == 3:
        return int(list_time[0]) * 3600 + int(list_time[1]) * 60 + int(list_time[2])
    elif cnt == 2:
        return int(list_time[0]) * 60 + int(list_time[1])
    elif cnt == 1:
        return int(list_time[0])
    else:
        raise ValueError("Định dạng thời gian không hợp lệ")

def cut_video_by_timeline_use_ffmpeg(input_video_path, segments, is_connect, is_delete=False):
    def get_video_duration():
        """Trả về độ dài của video bằng giây."""
        command = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', input_video_path]
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        return float(result.stdout.strip())
    
    try:
        output_folder, output_file_path, file_name, finish_folder = get_output_folder(input_video_path)
        move_file_path = os.path.join(finish_folder, file_name)
        temp_list_file = "temp_list.txt"
        
        # Xóa tệp danh sách tạm thời nếu tồn tại
        if os.path.exists(temp_list_file):
            os.remove(temp_list_file)

        # Tách các đoạn video
        segments = segments.split(',')
        clips = []
        duration = get_video_duration()

        # Tạo lệnh ffmpeg để cắt video
        for i, segment in enumerate(segments):
            segment = segment.strip()
            start, end = segment.split('-')

            # Chuyển đổi thời gian bắt đầu và kết thúc
            start = convert_time_to_seconds(start)
            end = convert_time_to_seconds(end)
            
            if end > duration:
                end = duration
            
            segment_file_path = os.path.join(output_folder, f"{file_name.split('.')[0]}_{i + 1}.mp4")
            command = [
                'ffmpeg', '-i', input_video_path, '-ss', str(start), '-to', str(end),
                '-c', 'copy', segment_file_path
            ]
            
            subprocess.run(command, check=True)
            clips.append(segment_file_path)

        if is_connect and clips:
            # Tạo danh sách video để ghép
            with open(temp_list_file, 'w') as f:
                for clip in clips:
                    f.write(f"file '{clip}'\n")
            
            final_clip_path = os.path.join(output_folder, f"{file_name.split('.')[0]}_final.mp4")
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_list_file, '-c', 'copy', final_clip_path
            ]
            subprocess.run(command, check=True)
            
        try:
            # Xóa các đoạn video đã cắt
            for clip in clips:
                os.remove(clip)
            if is_delete:
                os.remove(input_video_path)
            else:
                shutil.move(input_video_path, move_file_path)
            
            # Xóa danh sách tạm thời
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)
        except:
            getlog()
            pass
        
        return True, None
    except:
        print("Có lỗi khi dùng ffmpeg để cắt video, đang thử dùng moviepy để cắt video...")
        cut_video_by_timeline_use_moviepy(input_video_path, segments, is_connect, is_delete=is_delete)
        

def cut_video_by_timeline_use_moviepy(input_video_path, segments, is_connect, is_delete=False):
    try:
        output_folder, output_file_path, file_name, finish_folder = get_output_folder(input_video_path)
        move_file_path = f"{finish_folder}\\{file_name}"
        
        # Tạo danh sách các đoạn video cắt ra
        segments = segments.split(',')
        clips = []
        i = 0
        video = VideoFileClip(input_video_path)
        duration = video.duration
        print("-------------------------------------------------------------------------------------")
        print(f"{file_name}: {video.size}")
        print("-------------------------------------------------------------------------------------")
        for segment in segments:
            segment = segment.strip()
            start, end = segment.split('-')

            # Chuyển đổi thời gian bắt đầu
            list_start = start.split(':')
            cnt = len(list_start)
            if cnt == 3:
                start = int(list_start[0]) * 3600 + int(list_start[1]) * 60 + int(list_start[2])
            elif cnt == 2:
                start = int(list_start[0]) * 60 + int(list_start[1])
            elif cnt == 1:
                start = int(list_start[0])
            else:
                message = "Định dạng thời gian cắt ở đầu video không đúng. Định dạng đúng là hh:mm:ss-hh:mm:ss hoặc mm:ss-mm:ss hoặc ss-ss"
                return False, message

            # Chuyển đổi thời gian kết thúc
            list_end = end.split(':')
            cnt = len(list_end)
            if cnt == 3:
                end = int(list_end[0]) * 3600 + int(list_end[1]) * 60 + int(list_end[2])
            elif cnt == 2:
                end = int(list_end[0]) * 60 + int(list_end[1])
            elif cnt == 1:
                end = int(list_end[0])
            else:
                message = "Định dạng thời gian cắt ở đầu video không đúng. Định dạng đúng là hh:mm:ss-hh:mm:ss hoặc mm:ss-mm:ss hoặc ss-ss"
                return False, message
            
            if end > duration:
                end = duration
            
            # Cắt đoạn video
            clip = video.subclip(start, end)
            if is_connect:
                clips.append(clip)
                sleep(1)
            else:
                i += 1
                file_path = f"{output_folder}\\{file_name}"
                clip.write_videofile(file_path, codec='libx264')
                clip.close()
                sleep(1)

        if is_connect and len(clips) > 0:
            final_clip = concatenate_videoclips(clips, method="compose")
            file_path = f"{output_folder}\\{file_name.split('.')[0]}_1.mp4"
            final_clip.write_videofile(file_path, codec='libx264')
            final_clip.close()
            for clip in clips:
                clip.close()

        video.close()
        try:
            if is_delete:
                os.remove(input_video_path)
            else:
                shutil.move(input_video_path, move_file_path)
        except:
            getlog()
        
        return True, None
    except Exception as e:
        if video:
            video.close()
        getlog()
        return False, "Có lỗi trong quá trình cắt video."

def merge_videos_use_ffmpeg(videos_folder, file_name=None, is_delete=False):
    def check_all_videos_h264(videos_path):
        command_check_codec = [
            'ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=codec_name', '-of', 'default=nw=1:nk=1'
        ]
        for video_path in videos_path:
            try:
                codec = subprocess.check_output(command_check_codec + [video_path], text=True).strip()
                if codec != 'h264':
                    return False
            except subprocess.CalledProcessError as e:
                print(f"FFmpeg error output:\n{e.stderr}\n")
                getlog()
                return False
        return True
    
    temp_file_path = os.path.join(videos_folder, "temp.txt")
    videos = natsorted(os.listdir(videos_folder))
    videos = [k for k in videos if '.mp4' in k]
    if len(videos) <= 1:
         return False, "Phải có ít nhất 2 video trong videos folder"
    videos_path = []

    def add_file_list():
        try:
            with open(temp_file_path, 'w') as f:
                for video in videos:
                    if video.endswith('.mp4'):
                        video_path = os.path.join(videos_folder, video)
                        f.write(f"file '{video_path}'\n")
                        videos_path.append(video_path)
            return temp_file_path
        except:
            getlog()
            return None
        
    output_folder = f"{videos_folder}\\output_folder"
    os.makedirs(output_folder, exist_ok=True)
    if file_name:
        file_path = f"{output_folder}\\{file_name}.mp4"
    else:
        file_path = f"{output_folder}\\merge_video.mp4"
    temp_file_path = add_file_list()
    all_videos_h264 = check_all_videos_h264(videos_path)
    command = [
        'ffmpeg', '-fflags', '+genpts', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c', 'copy'
    ]
    if all_videos_h264:
        command.extend(['-bsf:v', 'h264_mp4toannexb'])
    command.append(file_path)
    try:
        result = subprocess.run(command, check=True, text=True, capture_output=True)
        print(f"----> {result.stdout}")
        remove_file(temp_file_path)
        if is_delete:
            for video_path in videos_path:
                remove_file(video_path)
        return True, f"Gộp video thành công vào file {file_path}"
    except subprocess.CalledProcessError as e:
        print(f"Có lỗi khi dùng ffmpeg để ghép video. Đang thử dùng moviepy để ghép...")
        merge_videos_use_moviepy(videos_folder, file_path, is_delete)



def download_videos_form_playhh3dhay_by_txt_file(id_file_txt, download_folder=download_folder):
    def download_video_by_url(url, output_path):
        try:
            headers = {
                'Referer': 'https://playhh3dhay.xyz',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, stream=True)
            
            if response.status_code == 200:
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=1024):
                        if chunk:
                            f.write(chunk)
                print(f"Video downloaded successfully to {output_path}")
                return True
            else:
                print(f"Failed to download video. Status code: {response.status_code}")
                return False
        except:
            return False
        
    file_data = get_txt_data(id_file_txt)
    if file_data is None:
        print(f"File {id_file_txt} không tồn tại.")
        return
    lines = file_data.splitlines()
    index = 1938
    temp_list_file = f"{download_folder}\\temp_list.txt"
    remove_file(temp_list_file)
    for line in lines:
        no_video_downloaded = False
        line = line.split(',')
        if len(line) == 1:
            server, video_id, end_url = 's1', line[0], '1080p/1080p_003.html'
        elif len(line) == 2:
            server, video_id, end_url = line[0], line[1], '1080p/1080p_003.html'
        else:
            server, video_id, end_url = line[0], line[1], line[2] #dạng s1,81ff33517ddda537c8858780626cfc12,1080p/1080p_003.html
        resolution = end_url.split('_')[0]
        exp = end_url.split('_')[1].split('.')[-1]
        print("-----------------------------------------")
        print(f"Bắt đầu tải tập phim với id {video_id} - Độ phân giải {resolution}")
        output_folder = os.path.join(download_folder, video_id)
        os.makedirs(output_folder, exist_ok=True)
        for j in range(1, 2000):
            if no_video_downloaded:
                break
            if j < 1000:
                j_str = f"{j:03}"
            else:
                j_str = f"{j:04}"
            for i in range(1, 6):
                video_url = f"https://{server}.playhh3dhay{i}.com/cdn/down/{video_id}/Video/{resolution}_{j_str}.{exp}"
                segment_path = os.path.join(output_folder, f"video_{index}.mp4")
                
                if download_video_by_url(video_url, segment_path):
                    no_video_downloaded = False  # Đặt lại cờ vì đã tải được video
                    index += 1
                    break
            else:
                no_video_downloaded = True

def merge_videos_use_moviepy(videos_folder, file_path=None, is_delete=False):
    output_folder = f'{videos_folder}\\output_folder'
    os.makedirs(output_folder, exist_ok=True)
    edit_videos = os.listdir(videos_folder)
    edit_videos = [k for k in edit_videos if '.mp4' in k]
    if len(edit_videos) <= 1:
        warning_message("Phải có ít nhất 2 video trong videos folder")
        return
    edit_videos = natsorted(edit_videos)
    clips = []
    remove_videos = []
    for i, video_file in enumerate(edit_videos):
        video_path = f'{videos_folder}\\{video_file}'
        remove_videos.append(video_path)
        clip = VideoFileClip(video_path)
        clips.append(clip)
    if len(clips) > 0:
        final_clip = concatenate_videoclips(clips, method="compose")
        if not file_path:
            file_path = f"{output_folder}\\combine_video.mp4"
        final_clip.write_videofile(file_path, codec='libx264')
        final_clip.close()
        for clip in clips:
            clip.close()
        for clip in clips:
            clip.close()
    try:
        if is_delete:
            for video_path in remove_videos:
                os.remove(video_path)
        else:
            move_file_path = f'{videos_folder}\\finish_folder'
            os.makedirs(move_file_path, exist_ok=True)
            for video_path in remove_videos:
                shutil.move(video_path, move_file_path)
    except:
        getlog()

def strip_first_and_end_video(clip, first_cut, end_cut):
    first_cut = int(first_cut)
    end_cut = int(end_cut)
    if first_cut < 0:
        first_cut = 0
    if end_cut < 0 or end_cut >= clip.duration:
        warning_message("Thời gian cắt video không hợp lệ.")
        return None
    return clip.subclip(first_cut, clip.duration - end_cut)

def zoom_and_crop(clip, zoom_factor, vertical_position='center', horizontal_position='center'):
    resized_clip = clip.resize(zoom_factor)
    new_width, new_height = resized_clip.size
    y1, y2 = 0, new_height
    x1, x2 = 0, new_width
    # Tính toán vị trí cắt theo chiều dọc
    if vertical_position == 'center':
        y1 = (new_height - clip.h) // 2
        y2 = y1 + clip.h
    elif vertical_position == 'top':
        y1 = 0
        y2 = clip.h
    elif vertical_position == 'bot':
        y1 = new_height - clip.h
        y2 = new_height
    # Tính toán vị trí cắt theo chiều ngang
    if horizontal_position == 'center':
        x1 = (new_width - clip.w) // 2
        x2 = x1 + clip.w
    elif horizontal_position == 'left':
        x1 = 0
        x2 = clip.w
    elif horizontal_position == 'right':
        x1 = new_width - clip.w
        x2 = new_width
    cropped_clip = resized_clip.crop(x1=x1, y1=y1, x2=x2, y2=y2)
    return cropped_clip

def apply_zoom(clip, zoom_factor, vertical_position, horizontal_position):
    if not zoom_factor:
        return clip
    zoom_factor = float(zoom_factor)
    if zoom_factor < 0 or zoom_factor > 3:
        warning_message('Tỷ lệ zoom không hợp lệ.')
        return None
    return zoom_and_crop(clip, zoom_factor, vertical_position, horizontal_position)

def zoom_video_random_intervals(clip, max_zoom_size, min_time_to_change_zoom=3, max_time_to_change_zoom=5, vertical_position='center', horizontal_position='center'):
    if not min_time_to_change_zoom or min_time_to_change_zoom < 3:
        min_time_to_change_zoom = 3
    if not max_time_to_change_zoom or max_time_to_change_zoom < 5:
        max_time_to_change_zoom = 5

    max_zoom_size = float(max_zoom_size)
    min_time_to_change_zoom = int(min_time_to_change_zoom)
    max_time_to_change_zoom = int(max_time_to_change_zoom)
    if max_time_to_change_zoom > clip.duration:
        max_time_to_change_zoom = clip.duration
    
    start_times = []
    current_time = 0

    while current_time < clip.duration:
        start_times.append(current_time)
        current_time += random.uniform(min_time_to_change_zoom, max_time_to_change_zoom)

    if start_times[-1] < clip.duration:
        start_times.append(clip.duration)

    zoom_factors = [round(random.uniform(1.1, max_zoom_size), 2) for _ in range(len(start_times) - 1)]
    
    zoomed_clips = []
    try:
        for i, start_time in enumerate(start_times[:-1]):
            end_time = start_times[i + 1]
            sub_clip = clip.subclip(start_time, end_time)
            zoomed_clip = apply_zoom(sub_clip, zoom_factors[i], vertical_position, horizontal_position)
            zoomed_clips.append(zoomed_clip)
    
        final_zoom_clip = concatenate_videoclips(zoomed_clips, method="compose")
        return final_zoom_clip
    except:
        getlog()

def speed_up_clip(clip, speed):
    speed = float(speed)
    if speed < 0 or speed > 3:
        warning_message('invalid speed up')
        return None
    sped_up_clip = clip.fx(speedx, factor=speed)
    return sped_up_clip

def get_clip_ratio(clip, tolerance=0.02):  #Kiểm tra video thuộc tỷ lệ 16:9 hay 9:16
    clip_width, clip_height = clip.size
    ratio = clip_width / clip_height
    if abs(ratio - (16/9)) < tolerance:  # Kiểm tra xem tỷ lệ gần bằng 16:9
        return (16,9)
    elif abs(ratio - (9/16)) < tolerance:  # Kiểm tra xem tỷ lệ gần bằng 9:16
        return (9,16)
    else:
        return False
    
def resize_clip(clip):
    target_ratio = get_clip_ratio(clip)
    target_width, target_height = target_ratio
    clip_width, clip_height = clip.size
    if clip_width / clip_height != target_width / target_height:
        target_clip_width = clip_height * target_width / target_height
        resized_clip = resize(clip, newsize=(target_clip_width, clip_height))
        return resized_clip
    return clip

def flip_clip(clip):
    # Áp dụng hiệu ứng đối xứng (flip) theo chiều ngang
    flipped_clip = mirror_x(clip)
    return flipped_clip

def add_image_watermask_into_video(clip, top_overlay_height="10", bot_overlay_height="10", watermask = None, vertical_watermask_position=50, horizontal_watermask_position=50):
    if not top_overlay_height or int (top_overlay_height) < 0:
        top_overlay_height = 2
    else:
        top_overlay_height = int(top_overlay_height)
    if not bot_overlay_height or int (bot_overlay_height) < 0:
        bot_overlay_height = 2
    else:
        bot_overlay_height = int(bot_overlay_height)
    
    try:
        width, height = clip.size
        top_image = ColorClip(size=(width, top_overlay_height), color=(0, 0, 0)).set_position(('center', 0)).set_duration(clip.duration)
        bottom_image = ColorClip(size=(width, bot_overlay_height), color=(0, 0, 0)).set_position(('center', height - bot_overlay_height)).set_duration(clip.duration)
    
        if watermask:
            watermask_image = ImageClip(watermask).set_duration(clip.duration)
            watermask_width, watermask_height = watermask_image.size
            if horizontal_watermask_position == 'center':
                horizontal_watermask_position = (width - watermask_width) / 2
            elif horizontal_watermask_position == 'left':
                horizontal_watermask_position = 0
            elif horizontal_watermask_position == 'right':
                horizontal_watermask_position = width - watermask_width
            else:
                try:
                    horizontal_watermask_position = int(horizontal_watermask_position) * width / 100
                except ValueError:
                    horizontal_watermask_position = 'center'

            if vertical_watermask_position == 'center':
                vertical_watermask_position = (height - watermask_height) / 2
            elif vertical_watermask_position == 'top':
                vertical_watermask_position = 0
            elif vertical_watermask_position == 'bottom':
                vertical_watermask_position = height - watermask_height
            else:
                try:
                    vertical_watermask_position = int(vertical_watermask_position) * height / 100
                except ValueError:
                    vertical_watermask_position = 'center'

            watermask_image = (ImageClip(watermask).set_position((horizontal_watermask_position, vertical_watermask_position)).set_duration(clip.duration))
            final_clip = CompositeVideoClip([clip, top_image, bottom_image, watermask_image])
        else:
            final_clip = CompositeVideoClip([clip, top_image, bottom_image])
        return final_clip
    except:
        getlog()
        return None

def convert_video_169_to_916(input_video_path, zoom_size=None, resolution="720x1280", is_delete=False):
    try:
        output_folder, output_file_path, file_name, finish_folder = get_output_folder(input_video_path)
        move_file_path = f"{finish_folder}\\{file_name}"
        video = VideoFileClip(input_video_path)
        width, height = video.size
        if zoom_size:
            zoom_size = float(zoom_size)
            zoomed_video = video.resize(zoom_size)
        else:
            # Tính toán tỷ lệ zoom để đảm bảo không hụt chiều cao
            new_height = height
            new_width = height * 9 / 16
            if new_width > width:
                new_width = width
                new_height = width * 16 / 9

            zoom_factor = new_height / height
            zoomed_video = video.resize(zoom_factor)
        # Thêm lớp màu đen vào video để đạt được tỷ lệ 9:16 mà không kéo giãn video
        resolution = list(map(int, resolution.split('x')))
        background = ColorClip(size=resolution, color=(0, 0, 0), duration=video.duration)
        
        zoomed_width, zoomed_height = zoomed_video.size
        x_pos = (resolution[0] - zoomed_width) / 2
        y_pos = (resolution[1] - zoomed_height) / 2

        final_video = CompositeVideoClip([background, zoomed_video.set_position((x_pos, y_pos))], size=resolution)
        final_video.write_videofile(output_file_path, codec='libx264', audio_codec='aac')
        
        try:
            final_video.close()
            zoomed_video.close()
            video.close()
            if is_delete:
                os.remove(input_video_path)
            else:
                shutil.move(input_video_path, move_file_path)
        except:
            getlog()
        return True
    except:
        getlog()
        return False

def convert_video_916_to_169(input_video_path, resolution="1920x1080", is_delete=False):
    try:
        if not resolution:
            resolution = '1920x1080'
        resolution = resolution.split('x')
        output_folder, output_file_path, file_name, finish_folder = get_output_folder(input_video_path)
        move_file_path = f"{finish_folder}\\{file_name}"
        video = VideoFileClip(input_video_path)
        input_width, input_height = video.size
        new_height = input_width * 9 / 16
        if new_height <= input_height:
            # Crop video từ giữa theo chiều cao
            y1 = (input_height - new_height) / 2
            y2 = y1 + new_height
            cropped_video = video.crop(x1=0, x2=input_width, y1=y1, y2=y2)
        else:
            # Thêm viền đen để giữ nguyên cảnh quay
            new_width = input_height * 16 / 9
            black_bar = ColorClip(size=(int(new_width), input_height), color=(0, 0, 0))
            video = video.set_position(("center", "center"))
            cropped_video = CompositeVideoClip([black_bar, video]).set_duration(video.duration)
        resized_video = cropped_video.resize(newsize=(resolution[0], resolution[1]))
        resized_video.write_videofile(output_file_path, codec='libx264', audio_codec='aac')
        try:
            resized_video.close()
            video.close()
            sleep(1)
            if is_delete:
                os.remove(input_video_path)
            else:
                shutil.move(input_video_path, move_file_path)
        except:
            getlog()
        return True
    except:
        getlog()
        return False

def get_and_adjust_resolution_from_clip(clip, scale_factor=0.997):
    width = int(clip.size[0] * scale_factor)
    height = int(clip.size[1] * scale_factor)
    resized_video = clip.resize((width, height))
    return resized_video

def edit_audio(audio_path=None, video_path=None, video_url=None, reversed_audio=False, speed="1", first_cut_audio="0", end_cut_audio="0", download_folder=None):
    
    speed = float(speed)
    first_cut_audio = int(first_cut_audio)
    end_cut_audio = int(end_cut_audio)
    
    if audio_path:
        target_path = audio_path
    elif video_path:
        target_path = video_path
    elif video_url:
        video_path = download_video_by_url(video_url, download_folder)
        target_path = video_path
    else:
        warning_message("Vui lòng chọn nguồn để edit video")
        return
    if '.mp3' in target_path:
        audio_clip = AudioFileClip(target_path)
    else:
        video_clip = VideoFileClip(video_path)
        audio_clip = video_clip.audio
    try:
        if int(end_cut_audio) > 0 or int(first_cut_audio) > 0:
            audio_clip = audio_clip.subclip(first_cut_audio, audio_clip.duration - end_cut_audio)
        # Đảo ngược âm thanh
        if reversed_audio:
            audio_clip = audio_clip.fx(vfx.time_mirror)
        # Thay đổi tốc độ âm thanh
        if speed != 1:
            audio_clip = audio_clip.fx(speedx, speed)
        output_folder, output_file_path, file_name, finish_folder = get_output_folder(target_path)
        if check_vietnamese_characters(file_name):
            file_name = convert_sang_tieng_viet_khong_dau(file_name)
        audio_name = file_name.split('.')[0]
        output_audio_path = f'{output_folder}/{audio_name}.mp3'

        try:
            audio_clip.write_audiofile(output_audio_path, codec='mp3')
        except:
            output_audio_path = f'{output_folder}/audio.mp3'
            audio_clip.write_audiofile(output_audio_path, codec='mp3')
        audio_clip.close()
        if video_clip:
            video_clip.close()
    except Exception as e:
        getlog()

def check_vietnamese_characters(filename):
    # Dải ký tự Unicode tiếng Việt bao gồm các ký tự có dấu
    vietnamese_pattern = re.compile(
        r'[àáạảãâầấậẩẫăằắặẳẵèéẹẻẽêềếệểễìíịỉĩòóọỏõôồốộổỗơờớợởỡùúụủũưừứựửữỳýỵỷỹđ'
        r'ÀÁẠẢÃÂẦẤẬẨẪĂẰẮẶẲẴÈÉẸẺẼÊỀẾỆỂỄÌÍỊỈĨÒÓỌỎÕÔỒỐỘỔỖƠỜỚỢỞỠÙÚỤỦŨƯỪỨỰỬỮỲÝỴỶỸĐ]'
    )
    return bool(vietnamese_pattern.search(filename))

def remove_audio_from_clip(clip):
    return clip.without_audio()

def set_audio_for_clip(clip, background_music, background_music_volume="10"):
    volume = float(background_music_volume)/100
    background_music = AudioFileClip(background_music)
    background_music = background_music.volumex(volume)
    background_music = afx.audio_loop(background_music, duration=clip.duration)
    current_audio = clip.audio
    if current_audio is None:
        clip = clip.set_audio(background_music)
    else:
        # Kết hợp giọng thuyết minh và nhạc nền
        combined_audio = CompositeAudioClip([current_audio, background_music])
        clip = clip.set_audio(combined_audio)
    return clip
