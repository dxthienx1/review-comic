# youtube_manager.py
import requests
from common_function import *
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from Common import *

# Đường dẫn tương đối đến thư mục dự án
parent_dir = get_file_path()
sys.path.append(parent_dir)
current_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(current_dir)
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
RETRIABLE_EXCEPTIONS = (httplib2.HttpLib2Error, IOError) # Always retry when these exceptions are raised.
SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#-----------------------------------------------------------------------------------------------------------------
class YouTubeManager():
    def __init__(self, config, secret_info, gmail, channel_id):
        self.config = config
        self.secret_info = secret_info
        self.gmail = gmail
        self.channel_id = channel_id
        
        self.root = ctk.CTk()
        self.title = self.root.title(gmail)
        self.font_label = ctk.CTkFont(family="Arial", size=font_size)
        self.font_button = ctk.CTkFont( family="Arial", size=font_size, weight="bold" )
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.width = 400

        self.youtube = self.get_authenticated_service()
        if not self.youtube:
            return

        self.templates = get_json_data(templates_path)
        if not self.templates:
            self.templates = {}
        if self.channel_id not in self.templates:
            self.templates[self.channel_id] = {}
            
        self.pre_time_check_status = 0
        if self.gmail not in self.config:
            self.config[self.gmail] = {}
        if "cnt_request_upload" not in self.config[self.gmail]:
            self.config[self.gmail]['cnt_request_upload'] = 0

        self.list_waiting_dowload_videos = []
        self.list_videos_detail = []
        self.list_video_ids_delete = []
        self.validate_message = ""
        self.is_quotaExceeded = False
        self.is_upload_video_window = False
        self.is_schedule = False
        self.is_start_youtube = True
        self.is_download_window = False
        self.is_download_by_url = False

        self.download_thread = None
        self.download_thread_url = None
        self.quota_reset_thread = None

    def load_secret(self):
        self.oauth_path = self.secret_info[self.gmail]["oauth_path"]
        self.api_key = self.secret_info[self.gmail]["api"]
    def get_start_youtube(self):
        self.show_window()
        self.setting_window_size()
        self.create_button(text="Upload Videos", command= self.open_upload_video_window)
        self.create_button(text="Download Videos", command=self.open_download_video_window)
        self.create_button(text="Auto check status videos", command=self.start_check_status_videos_thread)
        try:
            self.root.mainloop()
        except:
            getlog()

    def open_download_video_window(self):
        self.reset()
        self.is_download_window = True
        self.setting_window_size()
        self.show_window()

        def save_download_settings():
            self.config['download_by_video_url'] = self.download_by_video_url.get()
            self.config['download_by_channel_id'] = self.download_by_channel_id.get()
            self.config['filter_by_like'] = self.filter_by_like_var.get()
            self.config['filter_by_views'] = self.filter_by_views_var.get()
            self.save_config()

        def start_download_by_video_url():
            save_download_settings()
            self.download_thread_url = threading.Thread(target=self.download_video_by_video_url)
            self.download_thread_url.daemon = True
            self.download_thread_url.start()

        def start_download_by_channel_id():
            save_download_settings()
            self.download_thread = threading.Thread(target=self.download_videos_by_channel_id)
            self.download_thread.daemon = True
            self.download_thread.start()

        self.output_folder_var = self.create_frame_button_and_input("Choose folder to save", command=self.choose_folder_to_save)
        self.download_by_video_url = self.create_frame_button_and_input("Download By Video URL", command=start_download_by_video_url)
        self.download_by_channel_id = self.create_frame_button_and_input("Download By Channel Id", command=start_download_by_channel_id)
        self.filter_by_like_var = self.create_settings_input("Filter By Number Of Likes", "filter_by_like", values=["10000", "20000", "30000", "50000", "100000"])
        self.filter_by_views_var = self.create_settings_input("Filter By Number Of Views", "filter_by_views", values=["200000", "500000", "1000000", "2000000", "5000000"])

    def choose_folder_to_save(self):
        self.output_folder = filedialog.askdirectory()
        self.output_folder_var.delete(0, ctk.END)
        self.output_folder_var.insert(0, self.output_folder)

    def auto_check_status_videos(self):
        if time() - self.pre_time_check_status > self.config['check_status_cycle']:
            print("start check video status")
            self.pre_time_check_status = time()
            my_video_ids = self.get_video_ids_by_channel_id(mine=True)
            self.get_video_details(my_video_ids, check_status=True)
            for video_id_del in self.list_video_ids_delete:
                self.delete_video(video_id_del)
        

    def open_upload_video_window(self):
        self.reset()
        self.is_upload_video_window = True
        self.setting_window_size()

        def set_upload_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.upload_folder_var.delete(0, ctk.END)
                self.upload_folder_var.insert(0, folder_path)
        def save_template():
            self.templates[self.channel_id] = {}
            self.templates[self.channel_id]["title"] = self.title_var.get()
            self.templates[self.channel_id]["is_title_plus_video_name"] = self.is_title_plus_video_name_var.get() == "Yes"
            self.templates[self.channel_id]["channel_id"] = self.is_title_plus_video_name_var.get()
            self.templates[self.channel_id]["description"] = self.description_var.get("1.0", ctk.END).strip()
            self.templates[self.channel_id]["tags"] = self.tags_var.get()
            self.templates[self.channel_id]["category_id"] = self.category_id_var.get()
            self.templates[self.channel_id]["privacy_status"] = self.privacy_status_var.get()
            self.templates[self.channel_id]["license"] = self.license_var.get()
            self.templates[self.channel_id]["is_delete_video"] = self.is_delete_video_var.get() == "Yes"
            self.templates[self.channel_id]["start_date"] = self.start_date_var.get()
            self.templates[self.channel_id]["publish_times"] = self.publish_times_var.get()
            self.templates[self.channel_id]["upload_folder"] = self.upload_folder_var.get()
            self.templates[self.channel_id]['gmail'] = self.gmail
            save_to_json_file(self.templates, templates_path)
            notification(f"Template {self.templates[self.channel_id]} saved successfully")

        def load_template():
            self.templates = get_json_data(templates_path) or {}
            template_name = self.load_template_combobox.get()
            template = self.templates[template_name]
            # Clear existing values
            self.title_var.delete(0, ctk.END)
            self.description_var.delete("1.0", ctk.END)
            self.tags_var.delete(0, ctk.END)
            self.start_date_var.delete(0, ctk.END)
            self.publish_times_var.delete(0, ctk.END)
            self.upload_folder_var.delete(0, ctk.END)

            # Insert new values from template
            self.title_var.insert(0, template.get("title", ""))
            is_title_plus_video_name = template.get("is_title_plus_video_name", "")
            if is_title_plus_video_name:
                val = "Yes"
            else:
                val = "No"
            self.is_title_plus_video_name_var.set(val)
            self.description_var.delete("1.0", ctk.END)
            self.description_var.insert(ctk.END, template.get("description", ""))
            self.tags_var.insert(0, template.get("tags", ""))
            self.category_id_var.set(template.get("category_id", ""))
            self.privacy_status_var.set(template.get("privacy_status", ""))
            self.license_var.set(template.get("license", ""))
            self.start_date_var.insert(0, template.get("start_date", ""))
            self.publish_times_var.insert(0, template.get("publish_times", ""))
            # self.thumbnail_file_var.insert(0, template.get("thumbnail_file", ""))
            self.upload_folder_var.insert(0, template.get("upload_folder", ""))
            # self.save_template_input.set(template_name)

        self.title_var = self.create_settings_input("Title", "title", left=left, right=right)
        self.is_title_plus_video_name_var = self.create_settings_input("Title Plus Video Name", "is_title_plus_video_name", values=["Yes", "No"], left=left, right=right)
        self.description_var = self.create_settings_input("Description", "description", is_textbox=True, left=left, right=right)
        self.tags_var = self.create_settings_input("Tags", "tags", left=left, right=right)
        self.category_id_var = self.create_settings_input("Category Id", "category_id", values=[ca for ca in youtube_category.keys()], left=left, right=right)
        self.privacy_status_var = self.create_settings_input("Privacy Status", "privacy_status", values=["public", "private", "unlisted"], left=left, right=right)
        self.license_var = self.create_settings_input("License", "license", values=["youtube", "creativeCommon"], left=left, right=right)
        self.start_date_var = self.create_settings_input("Start Date", "start_date", left=left, right=right)
        self.publish_times_var = self.create_settings_input("Publish Times", "publish_times", left=left, right=right)
        self.is_delete_video_var = self.create_settings_input("Delete video after upload", "is_delete_video", values=["Yes", "No"], left=left, right=right )
        self.upload_folder_var = self.create_frame_button_and_input("Select Videos Folder", command=set_upload_folder)
        self.upload_folder_var.insert(0, self.config['upload_folder'])
        # self.save_template_input = self.create_frame_button_and_combobox(text="Save Template", command=save_template, values=[temp for temp in self.templates.keys()])
        self.load_template_combobox = self.create_frame_button_and_combobox(text="Load Template", command=load_template, values=[temp for temp in self.templates.keys()])
        self.create_frame_button_and_button(text1="Start upload video now", command1=self.start_upload_videos_now, text2="Start upload video with schedule", command2=self.start_upload_videos_with_schedule)
        self.show_window()

    def save_upload_setting(self):
        try:
            self.templates[self.channel_id]["title"] = self.title_var.get()
            self.templates[self.channel_id]["is_title_plus_video_name"] = self.is_title_plus_video_name_var.get() == "Yes"
            self.templates[self.channel_id]["description"] = self.description_var.get("1.0", ctk.END).strip()
            self.templates[self.channel_id]["tags"] = self.tags_var.get()
            self.templates[self.channel_id]["category_id"] = youtube_category[self.category_id_var.get()]
            self.templates[self.channel_id]["privacy_status"] = self.privacy_status_var.get()
            self.templates[self.channel_id]["license"] = self.license_var.get()
            self.templates[self.channel_id]["is_delete_video"] = self.is_delete_video_var.get() == "Yes"
            self.templates[self.channel_id]["start_date"] = self.start_date_var.get()
            self.templates[self.channel_id]["publish_times"] = self.publish_times_var.get()
            self.templates[self.channel_id]["upload_folder"] = self.upload_folder_var.get()
            self.templates[self.channel_id]['gmail'] = self.gmail
            save_to_json_file(self.templates, templates_path)
            if len(self.templates[self.channel_id]["title"]) > 100:
                self.validate_message += "The maximum length of Title is 100 characters.\n"
            if len(self.templates[self.channel_id]["description"]) > 5000:
                self.validate_message += "The maximum length of Description is 5000 characters.\n"
            if len(self.templates[self.channel_id]["tags"]) > 500:
                self.validate_message += "The maximum length of tags is 500 characters.\n"
            if not self.templates[self.channel_id]["upload_folder"]:
                self.validate_message += "The folder containing the videos has not been selected.\n"
            if self.validate_message:
                warning_message(self.validate_message)
                return False
            
            self.is_upload_video_window = False
            return True
        except:
            getlog()
            return False

    def start_upload_videos_now(self):
        self.is_schedule = False
        if self.save_upload_setting():
            self.hide_window()
            self.schedule_videos()

    def start_upload_videos_with_schedule(self):
        self.is_schedule = True
        if self.save_upload_setting():
            self.hide_window()
            self.schedule_videos()
            
        
    def open_dowload_video_from_channel_window(self):
        self.create_text_input()


    def get_authenticated_service(self):
        try:
            self.load_secret()
            flow = flow_from_clientsecrets(self.oauth_path, scope=SCOPES, message="ERR get_authenticated_service")
            storage = Storage(f"{sys.argv[0]}-{self.gmail.split('@')[0]}-{self.channel_id}.json")
            credentials = storage.get()
            if credentials is None or credentials.invalid:
                credentials = run_flow(flow, storage, None)
            return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
        except Exception as e:
            error_message(f"Make sure you are logging into gmail {self.gmail} in your web browser")
            getlog()
            return None

    def upload_video(self, video_file, publish_at=None):
        if self.config[self.gmail]['cnt_request_upload'] >= 6:
            warning_message(f"Gmail {self.gmail} can only post a maximum of 6 videos per day")
            return
        try:
            body = {
                "snippet": {
                    "title": self.full_title,
                    "description": self.templates[self.channel_id]['description'],
                    "tags": self.templates[self.channel_id]['tags'],
                    "categoryId": self.templates[self.channel_id]['category_id'],
                    "defaultLanguage": "en",  # Thêm ngôn ngữ tiếng Anh
                    "automaticChapters": False  # Tắt tự động chương và khoảnh khắc chính
                },
                "status": {
                    "privacyStatus": self.templates[self.channel_id]['privacy_status'],
                    "selfDeclaredMadeForKids": self.templates[self.channel_id]['selfDeclaredMadeForKids'],
                    'license': self.templates[self.channel_id]['license'],
                    'notifySubscribers': False,   # Disable notifications to subscribers
                }
            }
            if publish_at:
                body['status']['publishAt'] = publish_at
                body['status']['privacyStatus'] = 'private'

            insert_request = self.youtube.videos().insert(
                part=",".join(body.keys()),
                body=body,
                media_body=MediaFileUpload(video_file, chunksize=-1, resumable=True),
                # onBehalfOfContentOwner=self.config['channel_id']  #chưa xử lý được
            )
            video_id = self.resumable_upload(insert_request)
            if video_id:
                return True
            return False
        except:
            getlog()
            return False

    def resumable_upload(self, insert_request):
        response = None
        while response is None:
            try:
                self.config[self.gmail]['cnt_request_upload'] += 1
                self.save_config()
                print ("Uploading file...")
                status, response = insert_request.next_chunk()
                if response is not None and 'id' in response:
                    video_id = response['id']
                    print(f"Video id '{video_id}' was successfully uploaded.")
                    sleep(2)
                    return video_id
            except HttpError as e:
                if e.resp.status == 403:
                    error_details = e._get_reason()
                    if 'quota' in error_details:
                        print("Quota exceeded. Please wait before making more requests.")
                        time_reset = get_time_remaining_until_quota_reset()
                        warning_message(f"Today's video posting limit has expired. Please wait another {time_reset/3600} hours")
                        self.is_quotaExceeded = True
                    else:
                        print(f"HTTP error occurred: {error_details}")
                else:
                    print(f"An error occurred when resumable_upload: {e}")
                    error_message(f"An error occurred when resumable_upload: {e}")
                return None
            except Exception as e:
                print("A retriable error occurred: %s" % e)
                getlog()
                return None

    def schedule_videos(self):
        self.finished_upload_videos = []
        if self.is_schedule:
            start_date = self.templates[self.channel_id]['start_date']
            publish_times = self.templates[self.channel_id]['publish_times'].split(',')
            self.current_date = convert_date_string_to_datetime(start_date)
            if not self.current_date:
                warning_message("format of date is yyyy-mm-dd")
                return
        videos = os.listdir(self.templates[self.channel_id]['upload_folder'])
        for k in videos:
            if '.mp4' not in k:
                videos.remove(k)        
        videos = natsorted(videos)
        upload_count = 0
        for i, video_file in enumerate(videos):
            if '.mp4' not in video_file:
                continue
            video_name = os.path.splitext(video_file)[0] #lấy tên
            title = self.config['title']
            if self.templates[self.channel_id]['is_title_plus_video_name']:
                self.full_title = f"{title}{video_name}"
            else:
                self.full_title = title
            if len(self.full_title) > 100:
                warning_message(f"The maximum length of Title is 100 characters:\n{self.full_title}: {len(self.full_title)} characters")
                return
            video_path = os.path.join(self.templates[self.channel_id]['upload_folder'], video_file)
            if self.is_schedule:
                # Xác định thời gian đăng cho video
                publish_time_str = publish_times[upload_count % len(publish_times)]
                try:
                    publish_time = datetime.strptime(publish_time_str, '%H:%M:%S').time()
                except:
                    warning_message("time data %r does not match format %r" % (publish_time_str, '%H:%M:%S'))
                publish_datetime = datetime.combine(self.current_date, publish_time)
                publish_at = convert_time_to_UTC(publish_datetime.year, publish_datetime.month, publish_datetime.day, publish_datetime.hour, publish_datetime.minute, publish_datetime.second)
            else:
                publish_at=None
            
            if not self.is_quotaExceeded:
                if self.upload_video(video_path, publish_at=publish_at):
                    self.finished_upload_videos.append(f"{video_name}")
                    old_video_path = os.path.join(self.templates[self.channel_id]['upload_folder'], video_file)
                    
                    if self.templates[self.channel_id]['is_delete_video']:
                        os.remove(old_video_path)
                    else:
                        finish_folder = os.path.join(self.templates[self.channel_id]['upload_folder'], 'upload_finished')
                        new_video_path = os.path.join(finish_folder, video_file)
                        # Di chuyển video vào thư mục finish
                        os.makedirs(finish_folder, exist_ok=True)
                        
                        try:
                            shutil.move(old_video_path, new_video_path)
                        except:
                            getlog()
                    # Chuyển sang ngày tiếp theo nếu đã hết số lượng đăng video trong ngày
                    # if self.is_schedule:
                    #     if (i + 1) % len(publish_times) == 0:
                    #         self.current_date += timedelta(days=1)
                    upload_count += 1
                    print(f"Uploaded video '{video_file}' scheduled for {publish_at} UTC")
                    if upload_count == len(publish_times):
                        break
                else:
                    print("uploaded fail")
                    return
            else:
                warning_message("Today's limit for using the \"Super App\" application has expired. Please wait until the next day")
                return
        if len(self.finished_upload_videos) > 0:
            notification(f"Videos uploaded successfully: {self.finished_upload_videos}\nTotal: {len(self.finished_upload_videos)}")

    def upload_thumbnail(self, video_id, thumbnail_file):
        request = self.youtube.thumbnails().set(
            videoId=video_id,
            media_body=MediaFileUpload(thumbnail_file)
        )
        response = request.execute()
        return response

    def add_video_to_playlist(self, video_id, playlist_id):
        body = {
            'snippet': {
                'playlistId': playlist_id,
                'resourceId': {
                    'kind': 'youtube#video',
                    'videoId': video_id
                }
            }
        }
        request = self.youtube.playlistItems().insert(
            part='snippet',
            body=body
        )
        response = request.execute()
        return response
    
    def delete_video(self, video_id):
        request = self.youtube.videos().delete(id=video_id)
        response = request.execute()
        print(f"delete video {video_id} info: {response}")
        return response

    def upload_videos_in_directory(self, directory ):
        video_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        upload_responses = []
        for video_file in video_files:
            video_path = os.path.join(directory, video_file)
            response = self.upload_video(video_path)
            upload_responses.append(response)
        return upload_responses

    def get_video_ids_by_channel_id(self, mine=False):
        try:
            if mine:
                response = self.youtube.channels().list(part="contentDetails", maxResults=50, mine=True).execute()
            else:
                response = self.youtube.channels().list(part="contentDetails", id=self.config['download_by_channel_id']).execute()
            if "items" not in response or len(response["items"]) == 0:
                raise Exception("No items found in channel details response.")
            uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
            self.video_info = {}
            video_ids = []
            next_page_token = None
            while True:
                playlist_response = self.youtube.playlistItems().list(
                    part="snippet,contentDetails,status",
                    playlistId=uploads_playlist_id,
                    maxResults=50,
                    pageToken=next_page_token
                ).execute()
                for item in playlist_response["items"]:
                    if item['status']['privacyStatus'] == 'private':
                        continue
                    video_id = item["snippet"]["resourceId"]["videoId"]
                    self.video_info[video_id]={}
                    self.video_info[video_id]["title"] = item["snippet"]["title"]
                    self.video_info[video_id]["status"] = item['status']
                    self.video_info[video_id]["contentDetails"] = item['contentDetails']
                    video_ids.append(video_id)
                next_page_token = playlist_response.get("nextPageToken")

                if not next_page_token:
                    break
            return video_ids
        except Exception as e:
            getlog()
            print(f"An error occurred when get_video_ids_by_channel_id: {e}")
        return []
    
    def get_video_details(self, video_ids, check_status=False):
        # Chia nhóm video ID để yêu cầu thông tin chi tiết
        chunk_size = 50  # Số lượng video ID trong mỗi nhóm (giới hạn của API)
        for i in range(0, len(video_ids), chunk_size):
            chunk_video_ids = video_ids[i:i+chunk_size]
            video_ids_str = ','.join(chunk_video_ids)
            url_videos = f'https://www.googleapis.com/youtube/v3/videos?part=statistics,snippet,status,contentDetails&id={video_ids_str}&key={self.api_key}'
            response_videos = requests.get(url_videos)
            videos_info = response_videos.json()
            self.list_videos_detail.append(videos_info)

            if check_status: #kiểm tra các video trong channel của mình
                if len(chunk_video_ids) == len(videos_info['items']):
                    continue
                ok_ids = [item['id'] for item in videos_info['items']]
                for id in chunk_video_ids:
                    if id not in ok_ids:
                        self.list_video_ids_delete.append(id)
                
                for item in videos_info['items']:
                    content_details = item.get('contentDetails', {})
                    if 'contentRating' in content_details and 'youtubereportabuse' in content_details['contentRating']:
                        self.list_video_ids_delete.append(item['id'])
                    

    
    def download_video_by_video_url(self):
        self.is_download_by_url = True
        video_url = self.download_by_video_url.get()
        self.download_video_youtube_by_url(video_url)
        self.is_download_by_url = False

    def download_videos_by_channel_id(self):
        self.list_videos_download_from_channel = []
        video_ids = self.get_video_ids_by_channel_id()
        self.get_video_details(video_ids)
        if len(self.list_videos_detail) > 0:
            self.download_info = get_json_data(download_info_path)
            if not self.download_info:
                self.download_info = {}
            if 'waiting_download_urls' not in self.download_info:
                self.download_info['waiting_download_urls'] = []
            if 'downloaded_urls' not in self.download_info:
                self.download_info['downloaded_urls'] = []

            for videos_detail in self.list_videos_detail:
                self.check_videos_and_dowload(videos_detail)
            cnt = len(self.list_videos_download_from_channel)
            if cnt == 0:
                notification("There are no videos that meet the criteria for number of likes and views!")
            else:
                notification(f"Videos Downloaded Successfully {cnt} video")

    def check_videos_and_dowload(self, video_details):
        for video in video_details['items']:
            statistics = video['statistics']
            like_count = int(statistics.get('likeCount', 0))
            view_count = int(statistics.get('viewCount', 0))
            if like_count > int(self.config['filter_by_like']) and view_count > int(self.config['filter_by_views']):
                video_id = video['id']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                if video_url in self.download_info['downloaded_urls'] or video_url in self.download_info['waiting_download_urls']:
                    print("url này đã tải hoặc có trong danh sách đợi download")
                    continue
                print(f"bắt đầu tải video: {video_url} với {like_count} lượt thích và {view_count} lượt xem")
                title = self.video_info[video_id]['title']
                self.temp_file_path = f'{download_folder}\\temp.mp4'
                self.file_name = f"{convert_sang_tieng_viet_khong_dau(title)}.mp4"
                self.video_file_path = f'{finish_folder}\\{self.file_name}'
                if not os.path.exists(self.video_file_path):
                    self.list_waiting_dowload_videos.append(video_url)
                    # Tải video sử dụng pytube
                    self.download_video_youtube_by_url(video_url)

    def download_video_youtube_by_url(self, video_url):
        try:
            download_video_by_url(video_url, self.output_folder)
            self.list_videos_download_from_channel.append(video_url)
            if video_url in self.download_info['waiting_download_urls']:
                self.download_info['waiting_download_urls'].remove(video_url)
            self.download_info['downloaded_urls'].append(video_url)
            save_to_json_file(self.download_info, download_info_path)
        except:
            getlog()


#common -------------------------------------------------------------------------------------------------------------
    def setting_screen_position(self):
        try:
            self.root.update_idletasks()
            x = screen_width - self.width - 10
            y = screen_height - self.height_window
            self.root.geometry(f"{self.width}x{self.height_window - 80}+{x}+{y}")
        except:
            getlog()

    def setting_window_size(self):
        if self.is_start_youtube:
            self.root.title(f"{self.gmail}: {self.channel_id}")
            self.width = 400
            self.height_window = 250
            self.is_start_youtube = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video: {self.channel_id}")
            self.width = 800
            self.height_window = 910
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos")
            self.width = 600
            self.height_window = 340
            self.is_download_window = False
        self.setting_screen_position()

    def save_config(self):
        save_to_json_file(self.config, config_path)

    def exit_app(self):
        self.reset()
        self.root.destroy()

    def on_close(self):
        self.save_config()
        self.reset()
        self.hide_window()
        self.root.destroy()

    def show_window(self):
        self.root.deiconify()
        self.root.attributes("-topmost", 1)
        self.root.attributes("-topmost", 0)

    def hide_window(self):
        self.root.iconify()
        self.root.withdraw()  # ẩn cửa sổ

    def reset(self):
        self.is_youtube_window = False
        self.clear_after_action()
        self.clear_widgets()

    def clear_after_action(self):
        self.root.withdraw()

    def clear_widgets(self):
        for widget in self.root.winfo_children():
            widget.pack_forget()

    def create_button_icon( self, frame = None, command=None, image=None, side=None, width=60):
        button = ctk.CTkButton( master=frame, text="", command=command, image=image, width=width)
        if side:
            button.pack(side=side, padx=0, pady=0)
        else:    
            button.pack(padx=0, pady=0)
        return button
    def create_button( self, text="", command=None, width=0, height=0, compound="left", anchor="center", frame = None, image=None, side=None, pady=None, padx=None):
        if width == 0:
            width = self.width
        if height == 0:
            height = height
        if not padx:
            padx=padx
        if not pady:
            padx=pady

        if frame:
            button = ctk.CTkButton( frame, text=text, command=command, image=image, font=self.font_button, width=width, height= height_element, compound=compound, anchor=anchor, )
        else:
            button = ctk.CTkButton( self.root, text=text, command=command, image=image, font=self.font_button, width=width, height= height_element, compound=compound, anchor=anchor, )
        if side:
            button.pack(side=side, pady=pady, padx=padx)
        else:    
            button.pack(pady=pady, padx=padx)
        return button

    def create_label( self, frame=None, text="", compound="center", anchor='center', width=None, height=None, wraplength=None, side=LEFT):
        if not width:
            width = self.width
        if not height:
            height = height_element
        wraplength = max(600, self.width)
        if frame:
            button = ctk.CTkLabel( frame, text=text, font=self.font_label, width=width, height= height_element, wraplength=wraplength, compound=compound, anchor=anchor)
        else:
            button = ctk.CTkLabel( self.root, text=text, font=self.font_label, width=width, height= height_element, wraplength=wraplength, compound=compound)
        if side:
            button.pack(side=side, pady=pady, padx=padx)
        else:
            button.pack(pady=pady, padx=padx)

    def create_frame(self, fill='x', side=None):
        frame = ctk.CTkFrame(self.root)
        frame.pack(padx=padx, pady=pady, fill=fill, side=side)
        return frame

    def create_text_input(self, frame, width=None, placeholder=None, side="right"):
        if not width:
            width = self.width
        text_input = ctk.CTkEntry(master=frame, width=width, height= height_element, placeholder_text_color=placeholder)
        text_input.pack(pady=pady, padx=padx, side=side)
        return text_input
    
    def create_combobox(self, frame, values=None, variable=None, side=RIGHT, width=None, height=None):
        val=None
        if variable:
            val = ctk.StringVar(value=str(variable))
        if not width:
            width = self.width
        if not height:
            height = height_element
        combobox = ctk.CTkComboBox(master=frame, values=values, variable=val, width=width, height=height)
        combobox.pack(side=side, padx=padx, pady=pady)
        return combobox

    
    def create_frame_label_and_input(self, label_text="", place_holder=None, left=0.5, right=0.5):
        frame = self.create_frame()
        label = self.create_label(frame=frame, text=label_text, side=LEFT, width=self.width*left, compound=LEFT)
        entry = self.create_text_input(frame=frame, width=self.width*right, placeholder=place_holder)
        return entry
    def create_frame_button_and_input(self, text, place_holder=None, command=None, left=0.5, right=0.5):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        entry = self.create_text_input(frame, width=self.width*right, placeholder=place_holder)
        return entry
    def create_frame_button_and_combobox(self, text, command=None, values=None, variable=None, left=0.5, right=0.5):
        frame = self.create_frame()
        button = self.create_button(frame=frame, text=text, width=self.width*left, side=LEFT, command=command)
        combobox = self.create_combobox(frame, width=self.width*right, side=RIGHT, values=values, variable=variable)
        return combobox
    def create_frame_button_and_button(self, text1, text2, command1=None, command2=None, left=0.5, right=0.5):
        frame = self.create_frame()
        button1 = self.create_button(frame=frame, text=text1, width=self.width*left , side=LEFT, command=command1)
        button2 = self.create_button(frame=frame, text=text2, width=self.width*right -15, side=RIGHT, command=command2)
        return button1, button2
    
    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.5, right=0.5):
        frame = self.create_frame()
        self.create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')

        if values:
            val = self.config[config_key]
            if self.config[config_key] == True:
                val = "Yes"
            elif self.config[config_key] == False:
                val = "No"
            elif config_key == "category_id":
                val = [key for key, value in youtube_category.items() if value == self.config[config_key]]

            var = ctk.StringVar(value=str(val))

            combobox = ctk.CTkComboBox(frame, values=values, variable=var, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            if config_key == "category_id":
                combobox.set(val[0])
            else:
                combobox.set(val)
            setattr(self, f"{config_key}_var", var)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", self.config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            var = self.config[config_key]
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            return entry
#-----------------------------------------------------------------------------------------------------------------
if __name__=="main":
    self = YouTubeManager()
    
    # file = "E:\Video\Elevate Knowledge\Elevate Knowledge 1\\11.mp4"
    # start_date = "2024/07/07 "
    # self.schedule_videos(video_folder, start_date)

    # my_list = self.list_videos()
    # for video in my_list.get('items', []):
    #     video_id = video['id']
    #     self.check_video_status(video_id)
    #     video_title = video['snippet']['title']
    #     privacy_status = video['status']['privacyStatus']
        
    #     # Kiểm tra xem có thông tin về vi phạm không
    #     if 'contentDetails' in video:
    #         if 'contentRating' in video['contentDetails']:
    #             rating = video['contentDetails']['contentRating']['ytRating']
    #             if rating == 'ytAgeRestricted':
    #                 print(f"Video '{video_title}' (ID: {video_id}) is age-restricted.")
    #         # Kiểm tra thêm các thông tin khác trong contentDetails nếu cần
        
    #     # In ra các trường hợp khác
    #     print(f"Video '{video_title}' (ID: {video_id}) has privacy status: {privacy_status}")
    #     print("-" * 30)