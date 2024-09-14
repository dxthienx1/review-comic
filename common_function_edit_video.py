from common_function import *
from common_function_CTK import *


def run_command_ffmpeg(command):
    subprocess.run(command, check=True, text=True, encoding='utf-8', errors='ignore')

def run_command_with_progress(command, duration):
    # Khởi chạy ffmpeg và theo dõi tiến trình
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,  # Đọc dữ liệu dưới dạng văn bản
        encoding='utf-8',  # Chỉ định mã hóa utf-8
    )

    # Biến lưu thời gian đã xử lý
    current_time = 0.0

    for line in process.stdout:
        if 'out_time_ms=' in line:
            # Phân tích thời gian xử lý từ dòng tiến trình
            match = re.search(r'out_time_ms=(\d+)', line)
            if match:
                out_time_ms = int(match.group(1))
                # Tính toán thời gian đã xử lý (giây)
                current_time = out_time_ms / 1000000.0
                # Tính toán phần trăm
                percent_complete = (current_time / duration) * 100
                sys.stdout.write(f'\rĐã xử lý: {percent_complete:.2f}%')
                sys.stdout.flush()

    process.wait()  # Đợi tiến trình hoàn tất

def convert_time_to_seconds(time_str):
    try:
        list_time = time_str.split(':')
        cnt = len(list_time)
        if cnt == 3:
            return float(list_time[0]) * 3600 + float(list_time[1]) * 60 + float(list_time[2])
        elif cnt == 2:
            return float(list_time[0]) * 60 + float(list_time[1])
        elif cnt == 1:
            return float(list_time[0])
        else:
            print("Định dạng thời gian không hợp lệ")
            return None
    except:
        print("Định dạng thời gian không hợp lệ")
        return None

def get_video_info(input_file):
    try:
        cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=width,height,r_frame_rate,duration',
            '-of', 'json',
            input_file
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(result.stdout)
        # Lấy thông tin từ JSON
        video_info = info['streams'][0]
        width = video_info['width']
        height = video_info['height']
        duration = video_info['duration']
        r_frame_rate = video_info.get('r_frame_rate', '0/1')
        numerator, denominator = map(int, r_frame_rate.split('/'))
        fps = numerator / denominator if denominator != 0 else 0
        return {
            'width': width,
            'height': height,
            'fps': fps,
            'duration': duration
        }
    except:
        try:
            clip = VideoFileClip(input_file)
            video_info = {}
            width, height = clip.size
            duration = clip.duration
            fps = clip.fps
            clip.close()
            return {
                'width': width,
                'height': height,
                'fps': fps,
                'duration': duration
            }
        except:
            return None

def cut_video_by_timeline_use_ffmpeg(input_video_path, segments, is_connect='no', is_delete=False, fast_cut=True):
    ti = time()
    if fast_cut:
        print("..........................")
        print("Bắt đầu cắt nhanh video...")
    else:
        print("Bắt đầu cắt video...")
    try:
        output_folder, output_file_path, file_name = get_output_folder(input_video_path, output_folder_name='cut_video')
        temp_list_file = os.path.join(output_folder, "temp_list.txt")
        remove_file(temp_list_file)
        combine_videos = []
        video_info = get_video_info(input_video_path)
        if not video_info:
            return None, f"Không lấy được thông tin video {input_video_path}"
        duration = float(video_info['duration'])
        end = "0"
        try:
            segments = segments.split(',')
        except:
            print("Định dạng thời gian cắt là start-end với start,end là hh:mm:ss hoặc mm:ss hoặc ss")
            return None, "Có lỗi khi cắt video"
        for i, segment in enumerate(segments, start=0):
            segment = segment.strip()
            if i==0 and '-' not in segment:
                start, end = "0", segment
            elif '-' not in segment:
                start = str(end)
                end = segment
            else:
                start, end = segment.split('-')
            start = convert_time_to_seconds(start)
            end = convert_time_to_seconds(end)
            if start is None or end is None:
                print("Thời gian cắt không hợp lệ.")
                return
            if end > duration:
                end = duration
            base_name = file_name.split('.mp4')[0]
            index = 1
            if len(segments) == 1:
                segment_file_path = os.path.join(output_folder, file_name)
                if os.path.exists(segment_file_path):
                    segment_file_path = os.path.join(output_folder, f"{base_name}_{index}.mp4")
            else:
                segment_file_path = os.path.join(output_folder, f"{base_name}_{index}.mp4")
            while True:
                if os.path.exists(segment_file_path):
                    index +=1
                    segment_file_path = os.path.join(output_folder, f"{base_name}_{index}.mp4")
                else:
                    break

            if fast_cut:
                command = [
                    'ffmpeg', '-accurate_seek', '-ss', str(start), '-i', input_video_path,
                    '-to', str(end - start), '-c:v', 'copy', '-c:a', 'copy', '-fps_mode', 'cfr',
                    '-y', segment_file_path, '-loglevel', 'quiet'
                ]
            else:
                command = [
                    'ffmpeg', '-i', input_video_path, '-ss', str(start), '-to', str(end), '-c:v', 'libx264', '-c:a', 'aac', '-strict', 'experimental', '-b:a', '192k', '-y', segment_file_path, '-loglevel', 'quiet'
                ]
            try:
                subprocess.run(command, check=True)

            except:
                cut_video_by_moviepy(input_video_path, segment_file_path, start, end)

            if is_connect:
                combine_videos.append(segment_file_path)

        cat = time() - ti
        print(f'---> Thời gian cắt cho video {input_video_path} là {cat}s')

        if is_connect != 'no' and combine_videos:
            try:
                with open(temp_list_file, 'w', encoding= 'utf-8') as f:
                    for video in combine_videos:
                        f.write(f"file '{video}'\n")
                command = connect_video(temp_list_file, output_file_path, fast_connect=is_connect == 'fast connect')
                run_command_ffmpeg(command)
                try:
                    for video in combine_videos:
                        remove_file(video)
                    remove_file(temp_list_file)
                except:
                    pass
            except:
                print("Có lỗi khi nối video, vui lòng đợi dùng cách khác để nối...")
                merge_videos_use_moviepy(videos_list=combine_videos, file_path=output_file_path, is_delete=is_delete, fps=int(video_info['fps']))
        noi = time() - ti
        print(f'---> Thời gian xử lý cho video {input_video_path} là {noi}s')
        return True, None
    except:
        print("Cắt video thất bại, vui lòng đợi dùng cách khác để cắt video...")
        cut_video_by_timeline_use_moviepy(input_video_path, segments, is_connect, is_delete=is_delete)
        noi = time() - ti
        print(f'---> Thời gian cắt cho video {input_video_path} là {noi}s')
        
def cut_video_by_moviepy(input_video_path, output_file_path, start, end):
    try:
        clip = VideoFileClip(input_video_path)
        sub_clip = clip.subclip(start, end)
        sub_clip.write_videofile(output_file_path, codec='libx264')
        sub_clip.close()
        clip.close()
    except:
        print(f"Cắt video {input_video_path} thất bại")

def cut_video_by_timeline_use_moviepy(input_video_path, segments, is_connect, is_delete=False):
    try:
        output_folder, output_file_path, file_name = get_output_folder(input_video_path, output_folder_name='cut_video')
        # Tạo danh sách các đoạn video cắt ra
        clips = []
        i = 0
        video = VideoFileClip(input_video_path)
        duration = video.duration
        try:
            segments = segments.split(',')
        except:
            print("Định dạng thời gian cắt là start-end với start,end là hh:mm:ss hoặc mm:ss hoặc ss")
            return None, "Có lỗi khi cắt video"
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
            file_path = f"{output_folder}\\{file_name.split('.mp4')[0]}_1.mp4"
            final_clip.write_videofile(file_path, codec='libx264')
            final_clip.close()
            for clip in clips:
                clip.close()

        video.close()
        # remove_or_move_file(input_video_path, is_delete=is_delete, is_move=is_move)
        return True, None
    except Exception as e:
        if video:
            video.close()
        getlog()
        return False, "Có lỗi trong quá trình cắt video."


def merge_videos_use_ffmpeg(videos_folder, file_name=None, is_delete=False, videos_path=None, fast_combine=True):
    ti = time()
    if fast_combine:
        print("..........................")
        print("Bắt đầu nối nhanh video...")
    else:
        print("Bắt đầu nối video...")

    temp_file_path = os.path.join(videos_folder, "temp.txt")
    max_fps = 24
    if not videos_path:
        videos = natsorted(os.listdir(videos_folder))
        videos = [k for k in videos if '.mp4' in k]
        if len(videos) <= 1:
            return False, "Phải có ít nhất 2 video trong videos folder"
        videos_path = []
        with open(temp_file_path, 'w') as f:
            for video in videos:
                if video.endswith('.mp4'):
                    video_path = os.path.join(videos_folder, video)
                    video_info = get_video_info(video_path)
                    if not video_info:
                        warning_message(f"Dừng gộp video vì không lấy được thông tin từ video {video_path}")
                        return
                    fps = video_info['fps']
                    if fps > max_fps:
                        max_fps = fps
                    f.write(f"file '{video_path}'\n")
                    videos_path.append(video_path)
    else:
        with open(temp_file_path, 'w') as f:
            for video_path in videos_path:
                video_info = get_video_info(video_path)
                if not video_info:
                    warning_message(f"Dừng gộp video vì không lấy được thông tin từ video {video_path}")
                    return
                fps = video_info['fps']
                if fps > max_fps:
                    max_fps = fps
                if video_path.endswith('.mp4'):
                    f.write(f"file '{video_path}'\n")
        
    output_folder = f"{videos_folder}\\merge_videos"
    os.makedirs(output_folder, exist_ok=True)
    if file_name:
        file_path = f"{output_folder}\\{file_name}.mp4"
    else:
        file_path = f"{output_folder}\\merge_video.mp4"
    command = connect_video(temp_file_path, file_path, fast_connect=fast_combine, max_fps=max_fps)
    try:
        run_command_ffmpeg(command)
        try:
            remove_file(temp_file_path)
            if is_delete:
                for video_path in videos_path:
                    remove_file(video_path)
        except:
            pass
        noi = time() - ti
        print(f'Tổng thời gian nối là {noi}')
        return True, f"Gộp video thành công vào file {file_path}"
    except:
        print(f"Có lỗi khi ghép nhanh video. Đang thử dùng cách khác để ghép...")
        merge_videos_use_moviepy(videos_folder, file_path, is_delete, fps=max_fps)
        noi = time() - ti
        print(f'Tổng thời gian nối là {noi}')

def merge_videos_use_moviepy(videos_folder, file_path=None, is_delete=False, is_move=True, videos_list=None, fps=30):
    output_folder = f'{videos_folder}\\merge_videos'
    os.makedirs(output_folder, exist_ok=True)
    if videos_list:
        edit_videos = videos_list
    else:
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
        final_clip.write_videofile(file_path, codec='libx264', fps=fps)
        final_clip.close()
        for clip in clips:
            clip.close()
        for clip in clips:
            clip.close()
    for video_path in remove_videos:
        remove_or_move_file(video_path, is_delete=is_delete, is_move=is_move)

def connect_video(temp_file_path, output_file_path, fast_connect=True, max_fps=None):
    if fast_connect:
        print("---> đang nối nhanh video...")
        command = [
            'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, 
            '-vf', 'fps=30', '-c:v', 'libx264', '-crf', '23', '-preset', 'veryfast', 
            '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', '-y', output_file_path, '-loglevel', 'quiet'
        ]
    else:
        print("---> đang nối video...")
        if max_fps:
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c:v', 'libx264', '-c:a', 'aac', '-r', f'{max_fps}', '-y', output_file_path, '-loglevel', 'quiet'
            ]
        else:
            command = [
                'ffmpeg', '-f', 'concat', '-safe', '0', '-i', temp_file_path, '-c:v', 'libx264', '-c:a', 'aac', '-y', output_file_path, '-loglevel', 'quiet'
            ]
    return command

def get_index_of_temp_file (input_path):
    return int(input_path.split('temp')[-1].split('.mp4')[0])
    
def strip_first_and_end_video(clip, first_cut, end_cut):
    try:
        first_cut = int(first_cut)
    except:
        first_cut = 0
    try:
        end_cut = int(end_cut)
    except:
        end_cut = 0

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
    elif vertical_position == 'bottom':
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

def zoom_video_random_intervals(clip, max_zoom_size, vertical_position='center', horizontal_position='center'):
    min_time_to_change_zoom = 4
    max_time_to_change_zoom = 8
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

    zoom_factors = [round(random.uniform(1.01, max_zoom_size), 2) for _ in range(len(start_times) - 1)]
    
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
        return None
    
def resize_clip(clip, re_size=0.999):
    try:
        target_ratio = get_clip_ratio(clip)
        clip_width, clip_height = clip.size
        if target_ratio:
            target_width, target_height = target_ratio
            if clip_width / clip_height != target_width / target_height:
                clip_width = clip_height * target_width / target_height
            
            width = int(clip_width * re_size)
            height = int(clip_height * re_size)
            try:
                clip = resize(clip, newsize=(width, height))
            except:
                ratio = clip_width/clip_height
                new_height = 720/ratio
                clip = resize(clip, newsize=(720, new_height))
        else:
            ratio = clip_width/clip_height
            new_height = 720/ratio
            clip = resize(clip, newsize=(720, new_height))
        return clip
    except:
        getlog()
        return None

def flip_clip(clip):
    # Áp dụng hiệu ứng đối xứng (flip) theo chiều ngang
    flipped_clip = mirror_x(clip)
    return flipped_clip

def increase_video_quality(input_path, output_path): #Tăng chất lượng video
    try:
        ffmpeg_command = [
            'ffmpeg',
            '-i', input_path,
            '-vf', 'unsharp=luma_msize_x=7:luma_msize_y=7:luma_amount=1.5,'
                    'eq=contrast=1.2:saturation=1.2',  # Tăng cường độ sắc nét và điều chỉnh độ tương phản
            '-c:a', 'copy', '-y',  # Sao chép âm thanh gốc
            output_path 
        ]
        subprocess.run(ffmpeg_command, check=True)
        print(f"Xử lý tăng độ phân giải thành công: \n{output_path}")
        return True
    except:
        print(f"Có lỗi trong quá trình tăng chất lượng video: \n{input_path}")
        return False
    
def add_watermark_by_ffmpeg(video_width, video_height, horizontal_watermark_position, vertical_watermark_position):
    try:
        if horizontal_watermark_position == 'center':
            horizontal_watermark_position = 50
        elif horizontal_watermark_position == 'left':
            horizontal_watermark_position = 0
        elif horizontal_watermark_position == 'right':
            horizontal_watermark_position = 100
        else:
            try:
                horizontal_watermark_position = float(horizontal_watermark_position)
                if horizontal_watermark_position > 100:
                    horizontal_watermark_position = 100
                elif horizontal_watermark_position < 0:
                    horizontal_watermark_position = 0
            except:
                horizontal_watermark_position = 50
        if vertical_watermark_position == 'center':
            vertical_watermark_position = 50
        elif vertical_watermark_position == 'top':
            vertical_watermark_position = 0
        elif vertical_watermark_position == 'bottom':
            vertical_watermark_position = 100
        else:
            try:
                vertical_watermark_position = float(vertical_watermark_position)
                if vertical_watermark_position > 100:
                    vertical_watermark_position = 100
                elif vertical_watermark_position < 0:
                    vertical_watermark_position = 0
            except:
                vertical_watermark_position = 50
        watermark_x = int(video_width * horizontal_watermark_position / 100)
        watermark_y = int(video_height * vertical_watermark_position / 100)
        return watermark_x, watermark_y
    except:
        return None, None

def add_image_watermark_into_video(clip, top_bot_overlay_height='2,2', left_right_overlay_width='2,2', watermark=None, vertical_watermark_position=0, horizontal_watermark_position=0, watermark_scale='1,1'):
    w, h = clip.size
    try:
        if not top_bot_overlay_height:
            top_bot_overlay_height = '2,2'
        top_overlay_height, bot_overlay_height = top_bot_overlay_height.split(',')
        if not top_overlay_height or int(top_overlay_height) < 0 or int(top_overlay_height) >= h:
            top_overlay_height = 2
        else:
            top_overlay_height = int(top_overlay_height)
        if not bot_overlay_height or int(bot_overlay_height) < 0 or int(bot_overlay_height) >= (h-top_overlay_height):
            bot_overlay_height = 2
        else:
            bot_overlay_height = int(bot_overlay_height)
    except:
        print("kích thước lớp phủ trên và dưới đã nhập không hợp lệ, lấy kích thước lớp phủ mặc định là 2")
        bot_overlay_height = top_overlay_height = 2

    try:
        if not left_right_overlay_width:
            left_right_overlay_width = '2,2'
        left_overlay_width, right_overlay_width = left_right_overlay_width.split(',')
        if not left_overlay_width or int(left_overlay_width) < 0 or int(left_overlay_width) >= w:
            left_overlay_width = 2
        else:
            left_overlay_width = int(left_overlay_width)
        if not right_overlay_width or int(right_overlay_width) < 0 or int(right_overlay_width) >= (w - left_overlay_width):
            right_overlay_width = 2
        else:
            right_overlay_width = int(right_overlay_width)
    except:
        print("kích thước lớp phủ trái và phải đã nhập không hợp lệ, lấy kích thước lớp phủ mặc định là 2")
        left_overlay_width = right_overlay_width = 2

    try:
        width, height = clip.size
        top_image = ColorClip(size=(width, top_overlay_height), color=(0, 0, 0)).set_position(('center', 0)).set_duration(clip.duration)
        bottom_image = ColorClip(size=(width, bot_overlay_height), color=(0, 0, 0)).set_position(('center', height - bot_overlay_height)).set_duration(clip.duration)
        left_image = ColorClip(size=(left_overlay_width, height), color=(0, 0, 0)).set_position((0, 'center')).set_duration(clip.duration)
        right_image = ColorClip(size=(right_overlay_width, height), color=(0, 0, 0)).set_position((width - right_overlay_width, 'center')).set_duration(clip.duration)

        if watermark:
            try:
                scale_w, scale_h = [float(s) for s in watermark_scale.split(',')]
            except:
                scale_w = scale_h = 1.0
            watermark_image = ImageClip(watermark).set_duration(clip.duration)
            watermark_width, watermark_height = watermark_image.size
            scaled_width = int(watermark_width * scale_w)
            scaled_height = int(watermark_height * scale_h)

            watermark_image = watermark_image.resize((scaled_width, scaled_height))
            if horizontal_watermark_position == 'center':
                horizontal_watermark_position = (width - scaled_width) / 2
            elif horizontal_watermark_position == 'left':
                horizontal_watermark_position = 0
            elif horizontal_watermark_position == 'right':
                horizontal_watermark_position = width - scaled_width
            else:
                try:
                    horizontal_watermark_position = int(float(horizontal_watermark_position) * width / 100)
                except ValueError:
                    horizontal_watermark_position = (width - scaled_width) / 2

            if vertical_watermark_position == 'center':
                vertical_watermark_position = (height - scaled_height) / 2
            elif vertical_watermark_position == 'top':
                vertical_watermark_position = 0
            elif vertical_watermark_position == 'bottom':
                vertical_watermark_position = height - scaled_height
            else:
                try:
                    vertical_watermark_position = int(float(vertical_watermark_position) * height / 100)
                except ValueError:
                    vertical_watermark_position = (height - scaled_height) / 2

            watermark_image = watermark_image.set_position((horizontal_watermark_position, vertical_watermark_position))
            final_clip = CompositeVideoClip([clip, top_image, bottom_image, left_image, right_image, watermark_image])
        else:
            final_clip = CompositeVideoClip([clip, top_image, bottom_image, left_image, right_image])
        return final_clip

    except Exception as e:
        print(f"Lỗi khi thêm watermark: {e}")
        return None

def convert_video_169_to_916(input_video_path, zoom_size=None, resolution="1080x1920", is_delete=False, is_move=True):
    try:
        output_folder, output_file_path, file_name = get_output_folder(input_video_path, output_folder_name='converted_videos')
        video = VideoFileClip(input_video_path)
        width, height = video.size
        if not zoom_size:
            zoom_size = 0.9
        else:
            zoom_size = float(zoom_size)
        target_width, target_height = list(map(int, resolution.split('x')))
        video_display_height = target_height * zoom_size
        zoom = video_display_height / height
        zoomed_video = video.resize(newsize=(int(width * zoom), int(height * zoom)))
        zoomed_width, zoomed_height = zoomed_video.size
        background = ColorClip(size=(target_width, target_height), color=(0, 0, 0), duration=video.duration)
        x_pos = (target_width - zoomed_width) / 2
        y_pos = (target_height - zoomed_height) / 2
        final_video = CompositeVideoClip([background, zoomed_video.set_position((x_pos, y_pos))], size=(target_width, target_height))
        final_video.write_videofile(output_file_path, codec='libx264', audio_codec='aac')
        final_video.close()
        zoomed_video.close()
        video.close()
        remove_or_move_file(input_video_path, is_delete=is_delete, is_move=is_move)
        return True
    except Exception as e:
        getlog()
        return False
    
def convert_video_916_to_169(input_video_path, resolution="1920x1080", is_delete=False, is_move=True):
    try:
        if not resolution:
            resolution = '1920x1080'
        resolution = resolution.split('x')
        output_folder, output_file_path, file_name = get_output_folder(input_video_path, output_folder_name='converted_videos')
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
        resized_video.close()
        video.close()
        sleep(1)
        remove_or_move_file(input_video_path, is_delete=is_delete, is_move=is_move)
        return True
    except:
        getlog()
        return False

def get_and_adjust_resolution_from_clip(clip, scale_factor=0.997):
    width = int(clip.size[0] * scale_factor)
    height = int(clip.size[1] * scale_factor)
    resized_video = clip.resize((width, height))
    return resized_video

def edit_audio(audio_path=None, video_path=None, video_url=None, speed="1", first_cut_audio="0", end_cut_audio="0", download_folder=None):
    
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
        # Thay đổi tốc độ âm thanh
        if speed != 1:
            audio_clip = audio_clip.fx(speedx, speed)
        output_folder, output_file_path, file_name = get_output_folder(target_path, output_folder_name='edited_audio')
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
    try:
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
    except:
        print("Có lỗi ghi ghép audio vào video")

