from common_function import requests, os
from common_function import get_txt_data, remove_file

def download_videos_form_playhh3dhay_by_txt_file(id_file_txt, download_folder=None):
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