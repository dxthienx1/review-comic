from common_function import *
class Facebook:
    def __init__(self, access_token, page_id):
        self.access_token = access_token
        self.page_id = page_id

    def upload_video(self, video_path, message):
        video_endpoint = f"https://graph.facebook.com/v12.0/{self.page_id}/videos"
        video_data = {
            'access_token': self.access_token,
            'description': message,
        }

        with open(video_path, 'rb') as video_file:
            video_files = {
                'source': video_file
            }
            response = requests.post(video_endpoint, data=video_data, files=video_files)
        
        if response.status_code == 200:
            print("Video uploaded successfully!")
        else:
            print(f"Failed to upload video. Status code: {response.status_code}")
            print(f"Response: {response.json()}")

    def schedule_video(self, video_path, message, delay_minutes):
        # Tính thời gian đăng video
        scheduled_time = datetime.now() + timedelta(minutes=delay_minutes)
        print(f"Video will be uploaded at {scheduled_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while datetime.now() < scheduled_time:
            sleep(10)  # Chờ đến khi đến thời gian đăng video
        
        self.upload_video(video_path, message)

# Sử dụng lớp Facebook
access_token = 'your_access_token'
page_id = 'your_page_id'
video_path = 'path_to_your_video.mp4'
message = 'This is a test video upload.'
delay_minutes = 5  # Số phút trì hoãn trước khi đăng video

fb = Facebook(access_token, page_id)
fb.upload_video(video_path, message)  # Đăng video ngay lập tức
fb.schedule_video(video_path, message, delay_minutes)  # Lên lịch đăng video
