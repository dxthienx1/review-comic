from common_function import *

def create_video_with_multi_audio_and_background(
    audio_paths,
    texts,
    image_paths=None,
    bg_music_path=None,
    background_video_path=None,
    output_path=None,
    audio_volume=3,
    background_music_volume=0.3,
    sample_rate=44100,
    channels=1,
    alpha=0.6,
    image_display_ratio=1,
    font_path=r"C:\Windows\Fonts\Calibri.ttf",
    font_size=32,
    base_color=(0, 255, 255),
    highlight_color=(0, 255, 0),
    fps=30
):
    if not output_path:
        output_path = 'out_video.mp4'
    audio_durations = [get_audio_duration(p) for p in audio_paths]
    total_audio_duration = sum(audio_durations)
    audio_start_times = [sum(audio_durations[:i]) for i in range(len(audio_durations))]

    # 1. Gộp audio
    concat_list = "temp_concat.txt"
    with open(concat_list, "w") as f:
        for path in audio_paths:
            f.write(f"file '{os.path.abspath(path)}'\n")
    audio_concat = "temp_voice_audio.wav"
    cmd_concat = ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_list, "-c", "copy", audio_concat]
    assert run_command_ffmpeg(cmd_concat), "❌ Failed to concat audio"

    # 2. Lặp nhạc nền
    if bg_music_path:
        looped_music = "temp_looped_music.wav"
        cmd_loop = [
            "ffmpeg", "-y", "-stream_loop", "-1", "-i", bg_music_path,
            "-t", f"{total_audio_duration}", "-acodec", "pcm_s16le", looped_music
        ]
        assert run_command_ffmpeg(cmd_loop), "❌ Failed to loop music"

        # 3. Mix voice + nhạc
        mixed_audio = "temp_mixed_audio.mp3"
        cmd_mix = [
            "ffmpeg", "-y",
            "-i", audio_concat,
            "-i", looped_music,
            "-filter_complex",
            (
                f"[0:a]aresample={sample_rate},volume={audio_volume},pan=mono|c0=c0[va]; "
                f"[1:a]aresample={sample_rate},volume={background_music_volume},pan=mono|c0=c0[bg]; "
                "[va][bg]amix=inputs=2:duration=first:dropout_transition=0"
            ),
            "-ar", str(sample_rate),
            "-ac", str(channels),
            "-c:a", "libmp3lame",
            "-q:a", "2",
            mixed_audio
        ]
        assert run_command_ffmpeg(cmd_mix), "❌ Failed to mix audio"

    # 4. Chuẩn hóa video nền
    bg_video_temp = "temp_bg_video.mp4"
    temp_video_path = "temp_video.mp4"
    if not os.path.exists(bg_video_temp) and background_video_path:
        cmd_bg = [
            "ffmpeg", "-y", "-i", background_video_path,
            "-t", f"{total_audio_duration}", "-vf", "scale=1280:720", bg_video_temp
        ]
        assert run_command_ffmpeg(cmd_bg), "❌ Failed to generate base video"

    # 5. Ghi video overlay
    cap = cv2.VideoCapture(bg_video_temp)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(temp_video_path, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height))
    font = ImageFont.truetype(font_path, font_size)

    total_frames = int(total_audio_duration * fps)
    image_display_frames = int(total_audio_duration * image_display_ratio * fps)
    image_per_frame = image_display_frames // len(image_paths) if image_paths else 0

    print(f"Bắt đầu xử lý các file dữ liệu trước khi xuất video...")
    frame_idx = 0
    while frame_idx < total_frames:
        ret, frame = cap.read()
        if not ret:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            ret, frame = cap.read()
            if not ret:
                print("❌ Không thể đọc frame từ video nền.")
                break

        # Overlay ảnh
        if image_paths and frame_idx < image_display_frames:
            img_idx = frame_idx // image_per_frame
            if img_idx < len(image_paths):
                img_overlay = cv2.imread(image_paths[img_idx])
                img_overlay = cv2.resize(img_overlay, (width, height))
                frame = cv2.addWeighted(frame, 1 - alpha, img_overlay, alpha, 0)

        # Text highlight theo thời gian
        current_time = frame_idx / fps
        for i, txt in enumerate(texts):
            start = audio_start_times[i]
            end = start + audio_durations[i]
            if start <= current_time < end:
                # Ước tính số ký tự đang đọc (tương đối)
                portion = (current_time - start) / (end - start)
                chars_to_highlight = int(len(txt) * portion)

                frame = draw_wrapped_text(
                    frame, txt, chars_to_highlight, font,
                    base_color=base_color,
                    highlight_color=highlight_color
                )

        out.write(frame)
        frame_idx += 1

    cap.release()
    out.release()

    # 6. Gắn audio vào video
    final_audio = mixed_audio if bg_music_path else audio_concat
    cmd_merge = [
        "ffmpeg", "-y",
        "-i", temp_video_path,
        "-i", final_audio,
        "-c:v", "h264_nvenc",
        "-preset", "fast",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        output_path
    ]
    assert run_command_ffmpeg(cmd_merge, False), "❌ Failed to attach final audio"

    # 7. Cleanup
    for f in [concat_list, audio_concat, 'temp_looped_music.wav', 'temp_mixed_audio.mp3', bg_video_temp, temp_video_path]:
        if os.path.exists(f):
            os.remove(f)

    print(f"✅ Video created at: {output_path}")


def draw_wrapped_text(img_cv2, text, chars_to_highlight, font, base_color, highlight_color, margin=50, line_spacing=10):
    img_pil = Image.fromarray(cv2.cvtColor(img_cv2, cv2.COLOR_BGR2RGB))
    draw = ImageDraw.Draw(img_pil)
    w, h = img_pil.size

    # Tách dòng tự động nếu dòng quá dài
    words = text.split()
    lines = []
    current_line = ""

    for word in words:
        test_line = current_line + (' ' if current_line else '') + word
        bbox = draw.textbbox((0, 0), test_line, font=font)
        if bbox[2] - bbox[0] > w - 2 * margin:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    if current_line:
        lines.append(current_line)

    # Tính tổng chiều cao đoạn text
    line_heights = [draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1] for line in lines]
    total_height = sum(line_heights) + line_spacing * (len(lines) - 1)
    y_start = (h - total_height) // 2

    current_y = y_start
    highlighted = 0

    for line in lines:
        bbox_line = draw.textbbox((0, 0), line, font=font)
        line_width = bbox_line[2] - bbox_line[0]
        line_height = bbox_line[3] - bbox_line[1]
        x = (w - line_width) // 2

        # Vẽ từng ký tự để bôi màu
        for char in line:
            color = highlight_color if highlighted < chars_to_highlight else base_color
            draw.text((x, current_y), char, font=font, fill=color)

            bbox_char = draw.textbbox((0, 0), char, font=font)
            char_width = bbox_char[2] - bbox_char[0]
            x += char_width
            highlighted += 1

        current_y += line_height + line_spacing

    return cv2.cvtColor(np.array(img_pil), cv2.COLOR_RGB2BGR)


input_folder = r"E:\Python\developping\review comic\test\Truyen tieng anh\HISTORY STORY FOR SLEEP\output_txt_files\test1"
txt_paths = get_file_in_folder_by_type(input_folder, '.txt')
for txt_file in txt_paths:
    txt_path = os.path.join(input_folder, txt_file)
    texts = get_json_data(txt_path, readline=True)
    texts = [text.strip() for text in texts if text.strip()]

    txt_name = txt_file.replace('.txt', '')
    audio_forder = os.path.join(input_folder, txt_name)
    if not os.path.exists(audio_forder):
        print(f"{thatbai} Không tìm thấy thư mục chứa audio tương ứng với file {txt_file}")
        continue
    audio_paths = get_file_in_folder_by_type(audio_forder, '.mp3')
    audio_paths = [os.path.join(audio_forder, audio) for audio in audio_paths]

    image_folder = os.path.join(audio_forder, f"img")
    image_paths = None
    if os.path.exists(image_folder):
        image_paths = get_file_in_folder_by_type(image_folder, '.png') or None
        image_paths = [os.path.join(image_folder, img) for img in image_paths]
    
    background_folder = os.path.join(input_folder, 'background')
    os.makedirs(background_folder, exist_ok=True)

    background_video_path = None
    bg_music_path = None
    background_video_paths = get_file_in_folder_by_type(background_folder, '.mp4') or None
    if background_video_paths:
        background_video_path = os.path.join(background_folder, background_video_paths[0])
    bg_music_paths = get_file_in_folder_by_type(background_folder, '.mp3') or None
    if bg_music_paths:
        bg_music_path = os.path.join(background_folder, bg_music_paths[0])

    create_video_with_multi_audio_and_background(
        image_paths=image_paths,
        audio_paths=audio_paths,
        texts=texts,
        background_video_path=background_video_path,
        bg_music_path=bg_music_path,
        audio_volume=3,
        background_music_volume=0.3,
        alpha=0.5,
        image_display_ratio=0.6
    )