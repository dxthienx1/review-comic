from common_function import *


def join_mp3_with_ffmpeg(input_folder, output_folder=None):
    if not output_folder:
        output_folder = os.path.join(input_folder, 'merge_video')
    os.makedirs(output_folder, exist_ok=True)
    output_path = os.path.join(output_folder, 'merge.mp3')
    # Lấy danh sách file mp3 và sắp xếp
    mp3_files = get_file_in_folder_by_type(input_folder, '.mp3')

    # Tạo file danh sách
    list_path = os.path.join(input_folder, "list.txt")
    with open(list_path, "w", encoding="utf-8") as f:
        for file_name in mp3_files:
            full_path = os.path.join(input_folder, file_name)
            f.write(f"file '{full_path}'\n")

    concat_cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", f"{list_path}",  # Đường dẫn đến file danh sách
        "-c", "copy",           # Không mã hóa lại, giữ nguyên chất lượng
        f"{output_path}"            # File đầu ra
    ]

    if run_command_ffmpeg(concat_cmd):
        remove_file(list_path)
        print(f"{thanhcong} Gộp file thành công.")

input_folder = r"E:\Python\developping\review comic\test\Truyen tieng anh\HISTORY STORY FOR SLEEP\file goc"
output_folder =r"E:\Python\developping\review comic\test\Truyen tieng anh\HISTORY STORY FOR SLEEP"
# join_mp3_with_ffmpeg(input_folder, output_folder)