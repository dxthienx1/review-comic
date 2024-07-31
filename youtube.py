import requests
import httplib2
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.client import flow_from_clientsecrets
from oauth2client.file import Storage
from oauth2client.tools import run_flow
from common_function import *
from common_function_CTK import *
from Common import *

SCOPES = ["https://www.googleapis.com/auth/youtube.upload", "https://www.googleapis.com/auth/youtube.force-ssl"]
YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"

#-----------------------------------------------------------------------------------------------------------------
class YouTubeManager():
    def __init__(self, gmail, channel_name, is_auto_upload=False, lock=None, download_thread=None, upload_thread=None):
        # if lock:
        #     self.lock = lock
        # else:
        #     lock = threading.Lock()
        self.root = ctk.CTk()
        self.is_auto_upload = is_auto_upload
        if not is_auto_upload:
            self.title = self.root.title(gmail)
            self.root.protocol("WM_DELETE_WINDOW", self.on_close)
            self.width = width_window
            self.is_start_youtube = True
        self.download_thread = download_thread
        self.upload_thread = upload_thread
        self.gmail = gmail
        self.channel_name = channel_name
        self.get_youtube_config()
        self.youtube = self.get_authenticated_service()
        if not self.youtube:
            return


            
        self.pre_time_check_status = 0
        if self.gmail not in self.youtube_config:
            self.youtube_config[self.gmail] = {}
        if "cnt_request_upload" not in self.youtube_config[self.gmail]:
            self.youtube_config[self.gmail]['cnt_request_upload'] = 0

        self.list_waiting_dowload_videos = []
        self.list_videos_download_from_channel = []
        self.list_videos_detail = []
        self.list_video_ids_delete = []
        self.is_quotaExceeded = False
        self.is_upload_video_window = False
        if is_auto_upload:
            self.is_schedule = True
        else:
            self.is_schedule = False
        self.is_download_window = False

        self.is_stop_download = False
        self.is_stop_upload = False
        self.is_first_start = True

    def get_youtube_config(self):

        self.youtube_config = get_json_data(youtube_config_path)
    def save_youtube_config(self):
        save_to_json_file(self.youtube_config, youtube_config_path)

    def load_secret_info(self):
        try:
            self.secret_data = get_json_data(secret_path)
            self.secret_info={}
            gmails = [self.youtube_config['template'][channel_name]['gmail'] for channel_name in self.youtube_config['template'].keys()]
            for gmail in gmails:
                oauth = self.secret_data[gmail]['oauth']
                api = self.secret_data[gmail]['api']
                oauth_path = f'{current_dir}\\oauth\\{gmail}.json'
                save_to_json_file(oauth, oauth_path)
                self.secret_info[gmail] = {}
                self.secret_info[gmail]["oauth_path"] = oauth_path
                self.secret_info[gmail]["api"] = api
            self.oauth_path = self.secret_info[self.gmail]["oauth_path"]
            self.api_key = self.secret_info[self.gmail]["api"]
        except:
            getlog()
            self.oauth_path = None
            self.api_key = None

    def get_start_youtube(self):
        if not self.is_first_start:
            self.reset()
        else:
            self.is_first_start = False
        self.is_start_youtube = True
        self.show_window()
        self.setting_window_size()
        create_button(frame = self.root,text="Upload Videos", command= self.open_upload_video_window)
        create_button(frame = self.root,text="Download Videos", command=self.open_download_video_window)
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
            download_folder = self.output_folder_var.get()
            download_url = self.download_by_video_url.get()
            download_channel_id = self.download_by_channel_id.get()
            if not self.youtube_config['download_folder']:
                warning_message("hãy chọn thư mục lưu file tải về.")
                return False
            if not download_url and not download_channel_id:
                warning_message("hãy nhập url hoặc Id channel muốn tải video.")
                return False
            self.youtube_config['download_folder'] = download_folder
            self.youtube_config['download_by_video_url'] = download_url
            self.youtube_config['download_by_channel_id'] = download_channel_id
            self.youtube_config['filter_by_like'] = self.filter_by_like_var.get()
            self.youtube_config['filter_by_views'] = self.filter_by_views_var.get()
            self.save_youtube_config()
            return True

        def start_download_by_video_url():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                if save_download_settings():
                    self.download_thread = threading.Thread(target=self.download_video_by_video_url)
                    self.download_thread.start()
                else:
                    return

        def start_download_by_channel_id():
            if not self.download_thread or not self.download_thread.is_alive():
                self.is_stop_download = False
                if save_download_settings():
                    self.download_thread = threading.Thread(target=self.download_videos_by_channel_id)
                    self.download_thread.start()
                else:
                    return

        self.output_folder_var = create_frame_button_and_input(self.root,text="Choose folder to save", command=self.choose_folder_to_save, width=self.width, left=0.4, right=0.6)
        self.output_folder_var.insert(0, self.youtube_config['download_folder'])
        self.download_by_video_url = create_frame_button_and_input(self.root,text="Download By Video URL", command=start_download_by_video_url, width=self.width, left=0.4, right=0.6)
        self.download_by_channel_id = create_frame_button_and_input(self.root,text="Download By Channel Id", command=start_download_by_channel_id, width=self.width, left=0.4, right=0.6)
        self.filter_by_like_var = self.create_settings_input("Filter By Number Of Likes", "filter_by_like", is_data_in_template= False, values=["10000", "20000", "30000", "50000", "100000"], left=0.4, right=0.6)
        self.filter_by_views_var = self.create_settings_input("Filter By Number Of Views", "filter_by_views", is_data_in_template=False, values=["100000", "200000", "300000", "500000", "1000000"], left=0.4, right=0.6)
        create_button(self.root, text="Back", command=self.get_start_youtube, width=self.width)

    def choose_folder_to_save(self):
        output_folder = filedialog.askdirectory()
        if output_folder:
            self.output_folder_var.delete(0, ctk.END)
            self.output_folder_var.insert(0, output_folder)
        

    def open_upload_video_window(self):
        self.reset()
        self.is_upload_video_window = True
        self.setting_window_size()

        def set_upload_folder():
            folder_path = filedialog.askdirectory()
            if folder_path:
                self.upload_folder_var.delete(0, ctk.END)
                self.upload_folder_var.insert(0, folder_path)

        def load_template():
            self.get_youtube_config()
            template_name = self.load_template_combobox.get()
            template = self.youtube_config['template'][template_name]
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
            self.upload_folder_var.insert(0, template.get("upload_folder", ""))

        self.title_var = self.create_settings_input("Title", "title", left=left, right=right)
        self.is_title_plus_video_name_var = self.create_settings_input("Title + Video Name", "is_title_plus_video_name", values=["Yes", "No"], left=left, right=right)
        self.description_var = self.create_settings_input("Description", "description", is_textbox=True, left=left, right=right)
        self.tags_var = self.create_settings_input("Tags", "tags", left=left, right=right)
        self.category_id_var = self.create_settings_input("Category Id", "category_id", values=[ca for ca in youtube_category.keys()], left=left, right=right)
        self.privacy_status_var = self.create_settings_input("Privacy Status", "privacy_status", values=["public", "private", "unlisted"], left=left, right=right)
        self.license_var = self.create_settings_input("License", "license", values=["youtube", "creativeCommon"], left=left, right=right)
        self.start_date_var = self.create_settings_input("Start Date", "start_date", left=left, right=right)
        self.publish_times_var = self.create_settings_input("Publish Times", "publish_times", left=left, right=right)
        self.is_delete_video_var = self.create_settings_input("Delete video after upload", "is_delete_video", values=["Yes", "No"], left=left, right=right )
        self.upload_folder_var = create_frame_button_and_input(self.root,text="Select Videos Folder", command=set_upload_folder, width=self.width)
        self.upload_folder_var.insert(0, self.youtube_config['template'][self.channel_name]['upload_folder'])
        self.load_template_combobox = create_frame_button_and_combobox(self.root,text="Load Template", width=self.width, command=load_template, values=list(self.youtube_config['template'].keys()))
        self.load_template_combobox.set(self.youtube_config['current_channel'])
        create_frame_button_and_button(self.root,text1="Start upload video now", width=self.width, command1=self.start_upload_videos_now, text2="Start upload video with schedule", command2=self.start_upload_videos_with_schedule, left=0.5, right=0.5)
        create_button(self.root, text="Back", command=self.get_start_youtube, width=self.width)
        self.show_window()

    def save_upload_setting(self):
        try:
            self.get_youtube_config()
            self.youtube_config['template'][self.channel_name]["title"] = self.title_var.get()
            self.youtube_config['template'][self.channel_name]["is_title_plus_video_name"] = self.is_title_plus_video_name_var.get() == "Yes"
            self.youtube_config['template'][self.channel_name]["description"] = self.description_var.get("1.0", ctk.END).strip()
            self.youtube_config['template'][self.channel_name]["tags"] = self.tags_var.get()
            self.youtube_config['template'][self.channel_name]["category_id"] = self.category_id_var.get()
            self.youtube_config['template'][self.channel_name]["privacy_status"] = self.privacy_status_var.get()
            self.youtube_config['template'][self.channel_name]["license"] = self.license_var.get()
            self.youtube_config['template'][self.channel_name]["is_delete_video"] = self.is_delete_video_var.get() == "Yes"
            self.youtube_config['template'][self.channel_name]["start_date"] = self.start_date_var.get()
            self.youtube_config['template'][self.channel_name]["publish_times"] = self.publish_times_var.get()
            self.youtube_config['template'][self.channel_name]["upload_folder"] = self.upload_folder_var.get()
            self.youtube_config['template'][self.channel_name]['gmail'] = self.gmail
            self.save_youtube_config()
            validate_message = ""
            if len(self.youtube_config['template'][self.channel_name]["title"]) > 100:
                validate_message += "The maximum length of Title is 100 characters.\n"
            if len(self.youtube_config['template'][self.channel_name]["description"]) > 5000:
                validate_message += "The maximum length of Description is 5000 characters.\n"
            if len(self.youtube_config['template'][self.channel_name]["tags"]) > 500:
                validate_message += "The maximum length of tags is 500 characters.\n"
            if not self.youtube_config['template'][self.channel_name]["upload_folder"]:
                validate_message += "The folder containing the videos has not been selected.\n"
            if validate_message:
                warning_message(validate_message)
                return False
            
            self.is_upload_video_window = False
            return True
        except:
            getlog()
            return False

    def start_upload_videos_now(self):
        self.is_schedule = False
        if self.save_upload_setting():
            self.start_thread_upload_video()

    def start_upload_videos_with_schedule(self):
        self.is_schedule = True
        if self.save_upload_setting():
            self.start_thread_upload_video()
            
    def start_thread_upload_video(self):
        if not self.upload_thread or not self.upload_thread.is_alive():
            self.is_stop_upload = False
            thread_upload = threading.Thread(target=self.schedule_videos)
            thread_upload.start()

    def open_dowload_video_from_channel_window(self):
        create_text_input(self.root)


    def get_authenticated_service(self):
        try:
            self.load_secret_info()
            if not self.oauth_path:
                warning_message("Tài khoản gmail này chưa đăng ký hoặc đã hết hạn.")
                return
            try:
                flow = flow_from_clientsecrets(self.oauth_path, scope=SCOPES, message="ERR get_authenticated_service")
                storage = Storage(f"{sys.argv[0]}-{self.gmail}-{self.channel_name}.json")
                credentials = storage.get()
            except:
                getlog()
                credentials = None
            if credentials is None or credentials.invalid:
                credentials = run_flow(flow, storage, None)
            return build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION, http=credentials.authorize(httplib2.Http()))
        except Exception as e:
            error_message(f"Make sure you are logging into gmail {self.gmail} in your web browser")
            getlog()
            return None

    def upload_video(self, video_file, publish_at=None):
        cnt_request_upload = self.youtube_config[self.gmail]['cnt_request_upload']
        if cnt_request_upload >= 6:
            if not self.is_auto_upload:
                warning_message(f"Gmail {self.gmail} can only post a maximum of 6 videos per day")
            else:
                print(f"Gmail {self.gmail} can only post a maximum of 6 videos per day")
            return
        try:
            category_name = self.youtube_config['template'][self.channel_name]['category_id']
            category_id = int(youtube_category[category_name])
            body = {
                "snippet": {
                    "title": self.full_title,
                    "description": self.youtube_config['template'][self.channel_name]['description'],
                    "tags": self.youtube_config['template'][self.channel_name]['tags'],
                    "categoryId": category_id,
                    "defaultLanguage": "en",  # Thêm ngôn ngữ tiếng Anh
                    "automaticChapters": False  # Tắt tự động chương và khoảnh khắc chính
                },
                "status": {
                    "privacyStatus": self.youtube_config['template'][self.channel_name]['privacy_status'],
                    "selfDeclaredMadeForKids": False,
                    'license': self.youtube_config['template'][self.channel_name]['license'],
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
                # onBehalfOfContentOwner=self.youtube_config['channel_id']  #chưa xử lý được
            )
            video_id = self.resumable_upload(insert_request)
            if video_id:
                sleep(10)
                return True
            return False
        except:
            getlog()
            return False

    def resumable_upload(self, insert_request):
        response = None
        while response is None:
            try:
                if self.is_stop_upload:
                    return None
                self.youtube_config[self.gmail]['cnt_request_upload'] += 1
                self.save_youtube_config()
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
        try:
            self.finished_upload_videos = []
            if self.is_schedule:
                start_date_str = self.youtube_config['template'][self.channel_name]['start_date']
                publish_times = self.youtube_config['template'][self.channel_name]['publish_times'].split(',')
                start_date = convert_date_string_to_datetime(start_date_str)
                if not start_date:
                    warning_message("format of date is yyyy-mm-dd")
                    return False
            videos = os.listdir(self.youtube_config['template'][self.channel_name]['upload_folder'])
            if len(videos) == 0:
                return
            for k in videos:
                if '.mp4' not in k:
                    videos.remove(k)        
            videos = natsorted(videos)
            upload_count = 0
            for i, video_file in enumerate(videos):
                if self.is_stop_upload:
                    break
                if '.mp4' not in video_file:
                    continue
                video_name = os.path.splitext(video_file)[0] #lấy tên
                title = self.youtube_config['template'][self.channel_name]['title']
                if self.youtube_config['template'][self.channel_name]['is_title_plus_video_name']:
                    self.full_title = f"{title}{video_name}"
                else:
                    self.full_title = title
                if len(self.full_title) > 100:
                    if not self.is_auto_upload:
                        warning_message(f"The maximum length of Title is 100 characters:\n{self.full_title}: {len(self.full_title)} characters")
                    return False
                video_path = os.path.join(self.youtube_config['template'][self.channel_name]['upload_folder'], video_file)
                if self.is_schedule:
                    # Xác định thời gian đăng cho video
                    publish_time_str = publish_times[upload_count % len(publish_times)]
                    try:
                        publish_time = datetime.strptime(publish_time_str, '%H:%M:%S').time()
                    except:
                        getlog()
                        if not self.is_auto_upload:
                            warning_message("time data %r does not match format %r" % (publish_time_str, '%H:%M:%S'))
                    publish_datetime = datetime.combine(start_date, publish_time)
                    publish_at = convert_time_to_UTC(publish_datetime.year, publish_datetime.month, publish_datetime.day, publish_datetime.hour, publish_datetime.minute, publish_datetime.second)
                else:
                    publish_at=None
                
                if not self.is_quotaExceeded:
                    if self.upload_video(video_path, publish_at=publish_at):
                        self.finished_upload_videos.append(f"{video_name}")
                        old_video_path = os.path.join(self.youtube_config['template'][self.channel_name]['upload_folder'], video_file)
                        
                        if self.youtube_config['template'][self.channel_name]['is_delete_video']:
                            os.remove(old_video_path)
                        else:
                            finish_folder = os.path.join(self.youtube_config['template'][self.channel_name]['upload_folder'], 'upload_finished')
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
                        #         start_date += timedelta(days=1)
                        upload_count += 1
                        print(f"Uploaded video '{video_file}' scheduled for {publish_at} UTC")
                        if self.is_schedule:
                            if upload_count == len(publish_times):
                                break
                        else:
                            break
                    else:
                        print("uploaded fail")
                        return False
                else:
                    if not self.is_auto_upload:
                        warning_message("Today's limit for using the \"Super Social Media\" application has expired. Please wait until the next day")
                    return False
            if len(self.finished_upload_videos) > 0:
                if not self.is_auto_upload:
                    notification(f"Videos uploaded successfully: {self.finished_upload_videos}\nTotal: {len(self.finished_upload_videos)}")
                return True
            else:
                return False
        except:
            getlog()
            return False

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

    # def upload_videos_in_directory(self, directory ):
    #     video_files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    #     upload_responses = []
    #     for video_file in video_files:
    #         video_path = os.path.join(directory, video_file)
    #         response = self.upload_video(video_path)
    #         upload_responses.append(response)
    #     return upload_responses

    def get_video_ids_by_channel_id(self, mine=False):
        try:
            if mine:
                response = self.youtube.channels().list(part="contentDetails", maxResults=50, mine=True).execute()
            else:
                response = self.youtube.channels().list(part="contentDetails", id=self.youtube_config['download_by_channel_id']).execute()
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
        self.youtube_config['download_folder'] = self.output_folder_var.get()
        video_url = self.download_by_video_url.get()
        self.download_video_youtube_by_url(video_url)

    def download_videos_by_channel_id(self):
        self.youtube_config['download_folder'] = self.output_folder_var.get()
        self.list_videos_download_from_channel = []
        video_ids = self.get_video_ids_by_channel_id()
        self.get_video_details(video_ids)
        if len(self.list_videos_detail) > 0:
            self.get_download_info()
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
            if like_count > int(self.youtube_config['filter_by_like']) and view_count > int(self.youtube_config['filter_by_views']):
                video_id = video['id']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                if video_url in self.download_info['downloaded_urls'] or video_url in self.download_info['waiting_download_urls']:
                    print("url này đã tải hoặc có trong danh sách đợi download")
                    continue
                print(f"bắt đầu tải video: {video_url} với {like_count} lượt thích và {view_count} lượt xem")
                title = self.video_info[video_id]['title']
                download_folder = self.youtube_config['download_folder']
                file_name = f"{convert_sang_tieng_viet_khong_dau(title)}.mp4"
                video_file_path = f'{download_folder}\\{file_name}'
                if not os.path.exists(video_file_path):
                    self.list_waiting_dowload_videos.append(video_url)
                    self.download_video_youtube_by_url(video_url)

    def get_download_info(self):
        self.download_info = get_json_data(download_info_path)
        if not self.download_info:
            self.download_info = {}
        if 'waiting_download_urls' not in self.download_info:
            self.download_info['waiting_download_urls'] = []
        if 'downloaded_urls' not in self.download_info:
            self.download_info['downloaded_urls'] = []
    def download_video_youtube_by_url(self, video_url):
        try:
            self.get_download_info()
            download_video_by_url(video_url, self.youtube_config['download_folder'])
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
            self.root.title(f"{self.gmail}: {self.channel_name}")
            self.width = 500
            self.height_window = 170
            self.is_start_youtube = False
        elif self.is_upload_video_window:
            self.root.title(f"Upload video: {self.channel_name}")
            self.width = 800
            self.height_window = 830
            self.is_upload_video_window = False
        elif self.is_download_window:
            self.root.title("Download videos")
            self.width = 600
            self.height_window = 370
            self.is_download_window = False
        self.setting_screen_position()

    def exit_app(self):
        self.reset()
        self.root.destroy()

    def on_close(self):
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
        clear_widgets(self.root)

    def clear_after_action(self):
        self.root.withdraw()

    def create_settings_input(self, label_text, config_key, values=None, is_textbox = False, left=0.5, right=0.5, is_data_in_template=True):
        if is_data_in_template:
            config = config=self.youtube_config['template'][self.channel_name]
        else:
            config = self.youtube_config
        frame = create_frame(self.root)
        create_label(frame, text=label_text, side=LEFT, width=self.width*left, anchor='w')

        if values:
            if not config_key:
                val = ""
            elif config_key not in config:
                val = ""
            else:
                val = config[config_key]
                if config[config_key] == True:
                    val = "Yes"
                elif config[config_key] == False:
                    val = "No"

            var = ctk.StringVar(value=str(val))
            combobox = ctk.CTkComboBox(frame, values=values, variable=var, width=self.width*right)
            combobox.pack(side="right", padx=padx)
            setattr(self, f"{config_key}_var", var)
            return combobox
        
        elif is_textbox:
            textbox = ctk.CTkTextbox(frame, height=120, width=self.width*right)
            textbox.insert("1.0", config[config_key])  # Đặt giá trị ban đầu vào textbox
            textbox.pack(side=RIGHT, padx=padx)
            return textbox
        else:
            var = config[config_key]
            entry = ctk.CTkEntry(frame, width=self.width*right)
            entry.pack(side="right", padx=padx)
            entry.insert(0, var)
            setattr(self, f"{config_key}_var", var)
            return entry
