from common_function import os, datetime, save_to_json_file, get_json_data, get_json_data_from_url, sys, dtime, config_path, youtube_config_path, facebook_config_path, tiktok_config_path, download_info_path

def load_config():
    if os.path.exists(config_path):
        config = get_json_data(config_path)
    else:
        config = {
            "download_folder":"",
            "output_folder":"",
            "from_language": "en-us",
            "to_language": "vi",
            "auto_start": False,
            "is_delete_video": False,
            "is_move": False,
            "show_browser": False,

            "current_youtube_account": "",
            "current_tiktok_account": "",
            "current_facebook_account": "",
            "current_channel": "",
            "current_page": "",

            "download_by_video_url": "",
            "download_by_channel_id": "",
            "download_by_channel_url": "",
            "filter_by_like": 10000,
            "filter_by_views": 500000,

            "file_name": "",
            "start_index": "",
            "videos_edit_folder": "",
            "quantity_split": "1",
            "first_cut": "1",
            "end_cut": "2",
            "is_delete_original_audio": False,
            "background_music_path": "",
            "background_music_volume": "",
            "speed_up": "1.05",
            "max_zoom_size": "1.05",
            "is_random_zoom": False,
            "vertical_position": 'center',
            "horizontal_position": 'center',
            "flip_video": False,
            "top_image_path": "",
            "bot_image_path": "",
            "top_overlay": "10", 
            "bot_overlay": "10", 
            "water_path": "",
            "watermark_scale": "",
            "vertical_watermark_position": "50",
            "horizontal_watermark_position": "50",
            "watermark_scale": "100,100",
            "left_overlay_width": "100",
            "right_overlay_width": "100",
            "top_overlay_width": "100",
            "bottom_overlay_width": "100",

            "first_cut_audio": "", 
            "end_cut_audio": "", 
            "audio_speed": "", 
            "reversed_audio": False, 
            "audio_edit_path": "", 
            "video_get_audio_path": "", 
            "video_get_audio_url": "", 
            "speed_talk": "1", 
            "convert_multiple_record": False, 

            "supported_languages": {
                "en-us": "English (United States)",
                "vi": "Vietnamese"
            }
        }
        save_to_json_file(config, config_path)
    return config

youtube_category = {
    "Film & Animation": "1",
    "Autos & Vehicles": "2",
    "Music": "10",
    "Pets & Animals": "15",
    "Sports": "17",
    "Short Movies": "18",
    "Travel & Events": "19",
    "Gaming": "20",
    "Videoblogging": "21",
    "People & Blogs": "22",
    "Comedy": "23",
    "Entertainment": "24",
    "News & Politics": "25",
    "Howto & Style": "26",
    "Education": "27",
    "Science & Technology": "28",
    "Nonprofits & Activism": "29",
    "Movies": "30",
    "Anime/Animation": "31",
    "Action/Adventure": "32",
    "Classics": "33",
    "Documentary": "35",
    "Drama": "36",
    "Family": "37",
    "Foreign": "38",
    "Horror": "39",
    "Sci-Fi/Fantasy": "40",
    "Thriller": "41",
    "Shorts": "42",
    "Shows": "43",
    "Trailers": "44"
}

youtube_config = {
   "registered_account":["dxthienx2@gmail.com", "dxthienx10@gmail.com", "tranhangbk.001@gmail.com", "tranghangbk.002@gmail.com"],
   "current_youtube_account": "dxthienx2@gmail.com",
   "current_channel": "The Interesting Football",
   "download_folder": "E:/Video/Super Review/upload_finished",
   "download_by_video_url": "https://drive.google.com/uc?export=download&id=1zzsthUUDxl1B3XX9TpMJVG_laMTLa3n7",
   "download_by_channel_id": "",
   "filter_by_like": "",
   "filter_by_views": "",
   "use_cookies": True,
   "show_browser": False,
   "template": {
      "Brain Training": {
         "gmail": "tranghangbk.002@gmail.com",
         "password": "hang140991",
         "title": "IQ Quiz Every Day - Perfect Yourself | Who can solve it in 30 seconds?  | ",
         "is_title_plus_video_name": True,
         "description": "Welcome to \"Brain Training - Perfect Yourself\"! \nOur channel is dedicated to bringing you engaging and challenging IQ tests. Each video will help you explore and enhance your logical thinking, analytical skills, and problem-solving abilities. We offer a variety of questions, ranging from simple to complex, designed to improve your cognitive skills and help you achieve new milestones in your intellectual journey. Join us to test and elevate your IQ in a fun and rewarding way!\n----------------------------------------------------------------------------------------------------------------------------------------\nYour every like and share will motivate me to try harder!\n\n----------------------------------------------------------------------------------------------------------------------------------------\nWatch more videos:\nhttps://www.youtube.com/channel/UCxBuEz6aETSTRB55MoV9pKA/?sub_confirmation=1\n----------------------------------------------------------------------------------------------------------------------------------------\n- Thank you for following and supporting the channel recently!\n- Wishing you the best!\n----------------------------------------------------------------------------------------------------------------------------------------\nTags:\n#BrainTraining #SelfImprovement #ElevateYourself #IQTest #MentalExercise #BoostYourBrain #CognitiveSkills #MindPower #SmartThinking #IntellectualGrowth #BrainBoost #MentalChallenge #SelfGrowth #KnowledgeIsPower #TrainYourBrain #EnhanceYourMind #BrainTeasers #SmartGoals #PersonalDevelopment #ThinkSmart #UnlockYourPotential #BrainWorkout #IQChallenge #IntellectualDevelopment #Brainy #MindEnhancement #BrainFitness #IQBoost #MindGrowth #ElevateKnowledge #Trending #Trend",
         "tags": "Trending,Trend,BrainTraining,SelfImprovement,PersonalDevelopment,IQTest,MentalExercise,BoostYourBrain,MindPower,CognitiveSkills,SmartThinking,IntellectualGrowth,BrainBoost,SelfGrowth,TrainYourBrain,KnowledgeIsPower,BrainTeasers,MindEnhancement,BrainWorkout,IQChallenge,UnlockYourPotential,BrainFitness,SmartGoals,MentalChallenge,IQBoost,MindGrowth,Brainy,IntellectualDevelopment,ElevateYourself,MemoryTraining,CriticalThinking,ProblemSolving",
         "category_id": "Education",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "privacy_status": "public",
         "license": "creativeCommon",
         "upload_date": "2024-07-27",
         "publish_times": "01:00:00",
         "upload_folder": "E:/Video/Brain Training",
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": "2024-07-22"
      },
      "Animal_Funny_Version": {
         "gmail": "tranhangbk.001@gmail.com",
         "password": "hang140991",
         "title": "",
         "is_title_plus_video_name": True,
         "description": "Here are some unforgettable funny moments with animals. Enjoy hearty laughs with playful dogs, adorable cats, and many other creatures. \nDon't forget to follow for more hilarious videos!\n----------------------------------------------------------------------------------------------------------------------------------------\nTag:\n#FunnyAnimals #FunnyPets #AnimalHumor #PetsOfInstagram #AnimalVideos #FunnyAnimalVi#CuteAndFunny #AnimalLovers #PetHumor #HilariousPets #AnimalsOfInstagram #PetsofTikTok #FunnyDog #FunnyCat #PetsDaily #FunnyAnimalMoments #CrazyAnimals #PetComedy #AdorableAnimals #FunnyAnimals #FunnyPets #CutePets #AnimalHumor #PetEntertainment #PetLaughs #trend #trending\n#Th\u00faC\u01b0ngH\u00e0iH\u01b0\u1edbc #VideoTh\u00faVui #Kho\u1ea3nhKh\u1eafcH\u00e0iTh\u00faC\u01b0ng #\u0110\u1ed9ngV\u1eadtVuiNh\u1ed9n #Th\u00faC\u01b0ng\u0110\u00e1ngY\u00eau #VideoH\u00e0iTh\u00faC\u01b0ng #Th\u00faC\u01b0ngB\u00e1\u0110\u1ea1o #VideoTh\u00faC\u01b0ng #Gi\u1ea3iTr\u00edV\u1edbiTh\u00faC\u01b0ng #Th\u00faC\u01b0ngVuiNh\u1ed9n #h\u00e0ih\u01b0\u1edbc #vuiv\u1ebb #d\u1ec5th\u01b0\u01a1ng #\u0111\u00e1ngy\u00eau #ch\u00f3 #m\u00e8o #c\u00fancon #c\u00fancon\u0111\u00e1ngy\u00eau #si\u00eaucute ##c\u1ef1ch\u00e0i #c\u1ef1chay #c\u1ef1cd\u1ec5th\u01b0\u01a1ng #xuh\u01b0\u1edbng #th\u1ecbnhh\u00e0nh",
         "tags": "FunnyAnimals,FunnyPets,AnimalLovers,FunnyDog,FunnyCat,FunnyAnimalMoments,CrazyAnimals,FunnyAnimals,FunnyPets,CutePets,AnimalHumor,PetEntertainment,PetLaughs,trending,Th\u00faC\u01b0ngH\u00e0iH\u01b0\u1edbc,VideoTh\u00faVui,Kho\u1ea3nhKh\u1eafcH\u00e0iTh\u00faC\u01b0ng,\u0110\u1ed9ngV\u1eadtVuiNh\u1ed9n,Th\u00faC\u01b0ng\u0110\u00e1ngY\u00eau,Gi\u1ea3iTr\u00edV\u1edbiTh\u00faC\u01b0ng,Th\u00faC\u01b0ngVuiNh\u1ed9n,h\u00e0ih\u01b0\u1edbc,vuiv\u1ebb,d\u1ec5th\u01b0\u01a1ng,c\u00fancon\u0111\u00e1ngy\u00eau,si\u00eaucute,c\u1ef1ch\u00e0i,c\u1ef1chay,c\u1ef1cd\u1ec5th\u01b0\u01a1ng",
         "category_id": "Pets & Animals",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "privacy_status": "public",
         "license": "creativeCommon",
         "upload_date": "2024-07-27",
         "publish_times": "01:00:00,08:00:00,20:00:00",
         "upload_folder": "E:/Video/tranhangbk.001",
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": "2024-07-22"
      },
      "Animal Funny Best Version": {
         "gmail": "tranghangbk.002@gmail.com",
         "password": "thien191!",
         "title": "",
         "is_title_plus_video_name": True,
         "description": "Here are some unforgettable funny moments with animals. Enjoy hearty laughs with playful dogs, adorable cats, and many other creatures. \nDon't forget to follow for more hilarious videos!\n----------------------------------------------------------------------------------------------------------------------------------------\nTag:\n#FunnyAnimals #FunnyPets #AnimalHumor #PetsOfInstagram #AnimalVideos #FunnyAnimalVi#CuteAndFunny #AnimalLovers #PetHumor #HilariousPets #AnimalsOfInstagram #PetsofTikTok #FunnyDog #FunnyCat #PetsDaily #FunnyAnimalMoments #CrazyAnimals #PetComedy #AdorableAnimals #FunnyAnimals #FunnyPets #CutePets #AnimalHumor #PetEntertainment #PetLaughs #trend #trending\n#Th\u00faC\u01b0ngH\u00e0iH\u01b0\u1edbc #VideoTh\u00faVui #Kho\u1ea3nhKh\u1eafcH\u00e0iTh\u00faC\u01b0ng #\u0110\u1ed9ngV\u1eadtVuiNh\u1ed9n #Th\u00faC\u01b0ng\u0110\u00e1ngY\u00eau #VideoH\u00e0iTh\u00faC\u01b0ng #Th\u00faC\u01b0ngB\u00e1\u0110\u1ea1o #VideoTh\u00faC\u01b0ng #Gi\u1ea3iTr\u00edV\u1edbiTh\u00faC\u01b0ng #Th\u00faC\u01b0ngVuiNh\u1ed9n #h\u00e0ih\u01b0\u1edbc #vuiv\u1ebb #d\u1ec5th\u01b0\u01a1ng #\u0111\u00e1ngy\u00eau #ch\u00f3 #m\u00e8o #c\u00fancon #c\u00fancon\u0111\u00e1ngy\u00eau #si\u00eaucute ##c\u1ef1ch\u00e0i #c\u1ef1chay #c\u1ef1cd\u1ec5th\u01b0\u01a1ng #xuh\u01b0\u1edbng #th\u1ecbnhh\u00e0nh",
         "tags": "funnyanimals,funnypets,animallovers,funnydog,funnycat,funnyanimalmoments,crazyanimals,funnyanimals,funnypets,cutepets,petlaughs,th\u00fac\u01b0ngh\u00e0ih\u01b0\u1edbc,kho\u1ea3nhkh\u1eafch\u00e0ih\u01b0\u1edbc,\u0111\u1ed9ngv\u1eadtvuinh\u1ed9n,th\u00fac\u01b0ngvuinh\u1ed9n,c\u1ef1ch\u00e0i",
         "category_id": "Pets & Animals",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "privacy_status": "public",
         "license": "creativeCommon",
         "upload_date": "2024-07-28",
         "publish_times": "00:30:00,07:30:00,19:30:00",
         "upload_folder": "E:/Video/tranhangbk.002",
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": "2024-07-22"
      },
      "Super Review": {
         "gmail": "dxthienx10@gmail.com",
         "password": "thien191!",
         "title": "Phim Hay:  ",
         "is_title_plus_video_name": True,
         "description": "Ai Gh\u00e9 Qua Th\u00ec Cho M\u00ecnh Xin 1 Like v\u00e0 1 Follow \u0110\u1ec3 \u1ee6ng H\u1ed9 M\u00ecnh Nh\u00e9! \n---------------------------------------------------------------------------------------\nPh\u1ea7n m\u1ec1m qu\u1ea3n l\u00fd Youtube, Facebook, Tiktok:\n- T\u1ef1 \u0111\u1ed9ng \u0111\u0103ng video Youtube, Facebook, Tiktok. \n- T\u1ef1 \u0111\u1ed9ng t\u1ea3i t\u1ea5t c\u1ea3 c\u00e1c video c\u1ee7a 1 channel youtube, Tiktok b\u1ea5t k\u1ef3, c\u00f3 l\u1ecdc theo s\u1ed1 l\u01b0\u1ee3t like v\u00e0 view \u0111\u1ec3 t\u1ea3i nh\u1eefng video ch\u1ea5t l\u01b0\u1ee3ng. \n- Edit h\u00e0ng lo\u1ea1t video \u0111\u00e3 t\u1ea3i v\u1ec1 \u0111\u1ec3 l\u00e1ch b\u1ea3n quy\u1ec1n - Sau edit \u0111\u0103ng \u0111\u01b0\u1ee3c lu\u00f4n - Cam k\u1ebft sau edit kh\u00f4ng b\u1ecb b\u1eaft b\u1ea3n quy\u1ec1n.\n- Edit video, audio t\u00f9y ch\u1ec9nh theo \u00fd th\u00edch - L\u00e1ch b\u1ea3n quy\u1ec1n.\n- V\u00e0 ...\n---------------------------------------------------------------------------------------\n#manga review\n#manhwa review\n#anime review\n#reviewphimtruyentranh\n#reviewtruyentranh \n#reviewtruy\u1ec7ntranhfullb\u1ed9 \n#truy\u1ec7ntranhtuti\u00ean \n#truy\u1ec7ntranhxuy\u00eankh\u00f4ng \n#truy\u1ec7ntranhmanhwa \n#reviewtruy\u1ec7ntranhfull \n#reviewtruy\u1ec7nfull\n#truy\u1ec7ntranhhay\n#truy\u1ec7ntranhm\u1edbi\n#truy\u1ec7ntranhxuy\u00eankh\u00f4ng\n#truy\u1ec7ntranhmaingi\u1ea3heo\n#truy\u1ec7ntranhmainb\u00e1\n#truy\u1ec7ntranhtr\u01b0\u1eddngh\u1ecdc\n#anime\n#tuy\u1ec3nt\u1eadptruy\u1ec7ntranhhay\n#truy\u1ec7nho\u00e0n th\u00e0nh\n#truy\u1ec7ntranhho\u00e0nth\u00e0nh\n#truy\u1ec7ntranhfull\n#reup \n#reup100%\n#reup2024\n#h\u01b0\u1edbngd\u1eabnreupvideo\n#h\u01b0\u1edbngd\u1eabnreupvideom\u1edbinh\u1ea5t\n#reupyoutube \n#reuptiktok \n#reupfacebook  \n#reupvideo \n#Youtubemanagement  \n#facebookmanagement \n#tiktokmanagement \n#editvideo \n#l\u00e1chb\u1ea3nquy\u1ec1n \n#contentid \n#l\u00e1chcontentid\n-------------------------------------------------------\n* Super Review kh\u00f4ng s\u1edf h\u1eefu t\u1ea5t c\u1ea3 c\u00e1c t\u01b0 li\u1ec7u trong video m\u00e0 tu\u00e2n th\u1ee7 lu\u1eadt b\u1ea3n quy\u1ec1n v\u00e0 s\u1eed d\u1ee5ng h\u1ee3p l\u00fd lu\u1eadt Fair-Use (https://www.youtube.com/yt/copyright/)\nAll Music , Pictures, Videos and Sounds That Appear In This Video Are Owned By Their Respective Owners\n\"Copyright Disclaimer, Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational or personal use tips the balance in favor of fair use.\"\n-------------------------------------------------------",
         "tags": "reviewphimtruyentranh, reviewtruyentranh, reviewtruy\u1ec7ntranhfullb\u1ed9, truy\u1ec7ntranhtuti\u00ean, truy\u1ec7ntranhxuy\u00eankh\u00f4ng, truy\u1ec7ntranhmanhwa, reviewtruy\u1ec7ntranhfull, reviewtruy\u1ec7nfull, truy\u1ec7ntranhhay, truy\u1ec7ntranhm\u1edbi, truy\u1ec7ntranhmaingi\u1ea3heo, truy\u1ec7ntranhmainb\u00e1, truy\u1ec7ntranhtr\u01b0\u1eddngh\u1ecdc, anime, tuy\u1ec3nt\u1eadptruy\u1ec7ntmanga review, manhwa review,anime review,ranhhay, truy\u1ec7nho\u00e0n th\u00e0nh, truy\u1ec7ntranhho\u00e0nth\u00e0nh, truy\u1ec7ntranhfull",
         "category_id": "Film & Animation",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "privacy_status": "public",
         "license": "creativeCommon",
         "upload_date": "2024-08-03",
         "publish_times": "19:30:00",
         "upload_folder": "E:/Video/Super Review",
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": "2024-07-22"
      },
      "The Interesting Football": {
         "gmail": "dxthienx2@gmail.com",
         "password": "thien191!",
         "title": "",
         "is_title_plus_video_name": True,
         "description": "",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "tags": "",
         "category_id": "",
         "privacy_status": "private",
         "license": "creativeCommon",
         "upload_date": "",
         "publish_times": "",
         "upload_folder": "",
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": ""
      },
      "Tuy\u1ec3n T\u1eadp Phim Hay": {
         "gmail": "dxthienx10@gmail.com",
         "password": "thien191!",
         "title": "Phim Hay 2024: ",
         "is_title_plus_video_name": True,
         "description": "Ai Gh\u00e9 Qua Th\u00ec Cho M\u00ecnh Xin 1 Like v\u00e0 1 Follow \u0110\u1ec3 \u1ee6ng H\u1ed9 M\u00ecnh Nh\u00e9! \n---------------------------------------------------------------------------------------\nTuy\u1ec3n t\u1eadp c\u00e1c b\u1ed9 phim hay nh\u1ea5t hi\u1ec7n nay!\n---------------------------------------------------------------------------------------\nPh\u1ea7n m\u1ec1m qu\u1ea3n l\u00fd Youtube, Facebook, Tiktok:\n- T\u1ef1 \u0111\u1ed9ng \u0111\u0103ng video Youtube, Facebook, Tiktok. \n- T\u1ef1 \u0111\u1ed9ng t\u1ea3i t\u1ea5t c\u1ea3 c\u00e1c video c\u1ee7a 1 channel youtube, Tiktok b\u1ea5t k\u1ef3, c\u00f3 l\u1ecdc theo s\u1ed1 l\u01b0\u1ee3t like v\u00e0 view \u0111\u1ec3 t\u1ea3i nh\u1eefng video ch\u1ea5t l\u01b0\u1ee3ng. \n- Edit h\u00e0ng lo\u1ea1t video \u0111\u00e3 t\u1ea3i v\u1ec1 \u0111\u1ec3 l\u00e1ch b\u1ea3n quy\u1ec1n - Sau edit \u0111\u0103ng \u0111\u01b0\u1ee3c lu\u00f4n - Cam k\u1ebft sau edit kh\u00f4ng b\u1ecb b\u1eaft b\u1ea3n quy\u1ec1n.\n- Edit video, audio t\u00f9y ch\u1ec9nh theo \u00fd th\u00edch - L\u00e1ch b\u1ea3n quy\u1ec1n.\n- V\u00e0 ...\n---------------------------------------------------------------------------------------\n#reviewphim #t\u00f3mt\u1eaftphim #phimhay #reviewphimm\u1edbi #topphimhay #phimchi\u1ebfur\u1ea1p #reviewseries #phimkinh\u0111i\u1ec3n #t\u00f3mt\u1eaft #trailerphim #c\u1ea3mnh\u1eadnphim #t\u00f3mt\u1eaftphimng\u1eafn #phimbomt\u1ea5n #phimt\u00ecnhc\u1ea3m #phimh\u00e0nh\u0111\u1ed9ng #phimh\u00e0i  #phimc\u1ed5trang #phimkinhd\u1ecb #phimh\u00e0i #phiml\u1ebb #phimh\u00e0nh\u0111\u1ed9nghay #reviewphimhay #phimt\u00e2ml\u00fdhay #phimchi\u1ebfur\u1ea1phay #t\u00f3mt\u1eaftphimhay #phimhot #phimn\u1ed5i ti\u1ebfng #phimm\u1edbinh\u1ea5t #t\u1ed5ngh\u1ee3pphimhay #phimnextflix  #c\u1ef1chay #si\u00eauhay #phimd\u00e0it\u1eadp #phimhaytronbo #phimh\u00e0nqu\u1ed1chay #phimh\u00e0nh\u0111\u1ed9ngh\u00e0nqu\u1ed1c #m\u1edbinh\u1ea5t #xemnhi\u1ec1u\n#reup \n#reup100%\n#reup2024\n#h\u01b0\u1edbngd\u1eabnreupvideo\n#h\u01b0\u1edbngd\u1eabnreupvideom\u1edbinh\u1ea5t\n#reupyoutube \n#reuptiktok \n#reupfacebook  \n#reupvideo \n#Youtubemanagement  \n#facebookmanagement \n#tiktokmanagement \n#editvideo \n#l\u00e1chb\u1ea3nquy\u1ec1n \n#contentid \n#l\u00e1chcontentid\n-------------------------------------------------------\n* K\u00eanh kh\u00f4ng s\u1edf h\u1eefu t\u1ea5t c\u1ea3 c\u00e1c t\u01b0 li\u1ec7u trong video m\u00e0 tu\u00e2n th\u1ee7 lu\u1eadt b\u1ea3n quy\u1ec1n v\u00e0 s\u1eed d\u1ee5ng h\u1ee3p l\u00fd lu\u1eadt Fair-Use (https://www.youtube.com/yt/copyright/)\nAll Music , Pictures, Videos and Sounds That Appear In This Video Are Owned By Their Respective Owners\n\"Copyright Disclaimer, Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational or personal use tips the balance in favor of fair use.\"\n-------------------------------------------------------",
         "tags": "reviewphim, t\u00f3mt\u1eaftphim, phimhay, reviewphimm\u1edbi, topphimhay, phimchi\u1ebfur\u1ea1p, reviewseries, phimkinh\u0111i\u1ec3n, t\u00f3mt\u1eaft, trailerphim, c\u1ea3mnh\u1eadnphim, t\u00f3mt\u1eaftphimng\u1eafn, phimbomt\u1ea5n, phimt\u00ecnhc\u1ea3m, phimh\u00e0nh\u0111\u1ed9ng, phimh\u00e0i, phimc\u1ed5trang, phimkinhd\u1ecb, phimh\u00e0i, phiml\u1ebb, phimh\u00e0nh\u0111\u1ed9nghay, reviewphimhay, phimt\u00e2ml\u00fdhay, phimchi\u1ebfur\u1ea1phay, t\u00f3mt\u1eaftphimhay, phimhot, phimn\u1ed5iti\u1ebfng, phimm\u1edbinh\u1ea5t, t\u1ed5ngh\u1ee3pphimhay, phimnextflix, c\u1ef1chay, si\u00eauhay, phimd\u00e0it\u1eadp, phimhaytronbo, phimh\u00e0nqu\u1ed1chay, phimh\u00e0nh\u0111\u1ed9ngh\u00e0nqu\u1ed1c, m\u1edbinh\u1ea5t, xemnhi\u1ec1u",
         "category_id": "Film & Animation",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "privacy_status": "private",
         "license": "creativeCommon",
         "upload_date": "2024-08-15",
         "publish_times": "19:30:00, 21:00:00",
         "upload_folder": "E:\\Video\\Tuy\u1ec3n T\u1eadp Phim Hay",
         "is_delete_after_upload": False, 
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": ""
      },
      "Humor Haven - Relaxing Moment": {
         "gmail": "tranhangbk.001@gmail.com",
         "password": "hang140991",
         "title": "",
         "is_title_plus_video_name": True,
         "description": "#Funnymoments #memorablemoment #funnycollection #Comedyclips #Hilariousvideos #Laughoutloud #Funnyfails #Hilariouspranks #Funniestvideos #Sillymoments #HumorHaven #Relaxinghumor #Bestcomedy #Funnycompilations #Prankvideos #Hilariousreactions #moments #Comedicrelief #Bestpranks #comedy #selective #Chinesehumor #trending #trending #xuh\u01b0\u1edbng #h\u00e0ih\u01b0\u1edbc #C\u01b0\u1eddith\u1ea3ga #h\u00e0ituy\u1ec3nch\u1ecdn #c\u01b0\u1eddib\u1ec3b\u1ee5ng #vuah\u00e0i #Tuy\u1ec3nt\u1eadpvideoh\u00e0i #h\u00e0it\u1ed5ngh\u1ee3p #h\u00e0itrungqu\u1ed1c #h\u00e0inh\u1ea5tn\u0103m #nh\u1ecbnc\u01b0\u1eddi #th\u01b0gi\u00e3n #th\u00fav\u1ecb #vuiv\u1ebb #tuy\u1ec3nch\u1ecdn #h\u00e0i",
         "tags": "Funnymoments, memorablemoment, funnycollection, Comedyclips, Hilariousvideos, Laughoutloud, Funnyfails, Hilariouspranks, Funniestvideos, Sillymoments, HumorHaven, Relaxinghumor, Bestcomedy, Funnycompilations, Prankvideos, Hilariousreactions, moments, Comedicrelief, Bestpranks, comedy, selective, Chinesehumor, trending, trending, xuh\u01b0\u1edbng, h\u00e0ih\u01b0\u1edbc, C\u01b0\u1eddith\u1ea3ga, h\u00e0ituy\u1ec3nch\u1ecdn, c\u01b0\u1eddib\u1ec3b\u1ee5ng, vuah\u00e0i, Tuy\u1ec3nt\u1eadpvideoh\u00e0i, h\u00e0it\u1ed5ngh\u1ee3p, h\u00e0itrungqu\u1ed1c, h\u00e0inh\u1ea5tn\u0103m, nh\u1ecbnc\u01b0\u1eddi, th\u01b0gi\u00e3n, th\u00fav\u1ecb, vuiv\u1ebb, tuy\u1ec3nch\u1ecdn, h\u00e0i",
         "category_id": "Comedy",
         "thumbnail": "",
         "curent_playlist": "",
         "playlist": [],
         "altered_content": False,
         "privacy_status": "private",
         "license": "creativeCommon",
         "upload_date": "2024-08-09",
         "publish_times": "01:00:00, 09:00:00",
         "upload_folder": "E:\\Video\\chua xu ly\\Hai\\hai trung quoc\\output_folder\\output_folder\\output_folder",
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1",
         "last_auto_upload_date": ""
      }
   }
   }

tiktok_config = {
   "registered_account": [
      "dxthienx1@gmail.com",
      "tranhang.001@gmail.com",
      "badboymmo1901@gmail.com",
      "dxthienx10@gmail.com"
   ],
   "output_folder": "E:/Video/chua xu ly/animals/smart animal",
   "show_browser": True,
   "download_by_channel_url": "",
   "download_folder": "E:/Video/hh3d HD/chua xu ly",
   "is_move": False,
   "is_delete_after_upload": False,
   "filter_by_like": 20000,
   "filter_by_views": "300000",
   "template": {
      "dxthienx1@gmail.com": {
         "account": "dxthienx1@gmail.com",
         "password": "thien191!",
         "upload_folder": "E:/Python/developping/Super-Social-Media/test",
         "publish_times": "08:00,21:30",
         "description": "Test Auto Upload by python",
         "upload_date": "2024-08-05",
         "waiting_verify": False,
         "is_delete_after_upload": False,
         "number_of_days": "4",
         "day_gap": "1"
      },
      "tranhang.001@gmail.com": {
         "account": "tranhang.001@gmail.com",
         "password": "hang140991",
         "upload_folder": "E:/Python/developping/Super-Social-Media/test",
         "description": "ffff",
         "publish_times": "07:00",
         "title": "",
         "is_title_plus_video_name": False,
         "upload_date": "2024-08-11",
         "waiting_verify": False,
         "is_delete_after_upload": False,
         "number_of_days": "1",
         "day_gap": "1"
      },
      "badboymmo1901@gmail.com": {
         "account": "badboymmo1901@gmail.com",
         "password": "thien191",
         "upload_folder": "",
         "description": "",
         "publish_times": "",
         "title": "",
         "is_title_plus_video_name": False,
         "upload_date": "2024-08-15",
         "is_delete_after_upload": False,
         "waiting_verify": False,
         "number_of_days": "1",
         "day_gap": "1"
      },
      "dxthienx10@gmail.com": {
         "account": "dxthienx10@gmail.com",
         "password": "thien191!",
         "upload_folder": "E:/Video/hh3d HD/edited_videos",
         "description": "#hoathinhtrungquoc #hoathinhtrungquoc3d #animechina #3d #\u0111\u1ea5ula\u0111\u1ea1il\u1ee5c #\u0111\u1ea5uph\u00e1th\u01b0\u01a1ngkhung #ti\u00eanngh\u1ecbch #th\u1ebfgi\u1edbiho\u00e0nm\u1ef9 #ph\u00e0mnh\u00e2ntuti\u00ean #ti\u00eanhi\u1ec7p #tuti\u00ean #ki\u1ebfmhi\u1ec7p #dauladailuc #phimhoathinh3dtrungquoc #phimHD #ho\u1ea1th\u00ecnh3dthuy\u1ebftminh #fullHD #phim4k #ho\u1ea1th\u00ecnh3dvietsub\n#reviewphim #t\u00f3mt\u1eaftphim #phimhay #reviewphimm\u1edbi #topphimhay #phimchi\u1ebfur\u1ea1p #reviewseries #phimkinh\u0111i\u1ec3n #t\u00f3mt\u1eaft #trailerphim #c\u1ea3mnh\u1eadnphim #t\u00f3mt\u1eaftphimhay #phimbomt\u1ea5n #phimh\u00e0nh\u0111\u1ed9ng #phimh\u00e0i #phimc\u1ed5trang #phimh\u00e0i #phiml\u1ebb #phimh\u00e0nh\u0111\u1ed9nghay #reviewphimhay #phimt\u00e2ml\u00fdhay #phimchi\u1ebfur\u1ea1phay #t\u00f3mt\u1eaftphimhay #phimhot #phimn\u1ed5iti\u1ebfng #phimm\u1edbinh\u1ea5t #t\u1ed5ngh\u1ee3pphimhay #phimnextflix #c\u1ef1chay #si\u00eauhay #phimd\u00e0it\u1eadp #phimhaytronbo #phimh\u00e0nqu\u1ed1chay #phimh\u00e0nh\u0111\u1ed9ngh\u00e0nqu\u1ed1c #m\u1edbinh\u1ea5t #xemnhi\u1ec1u",
         "publish_times": "18:30",
         "title": "",
         "is_title_plus_video_name": False,
         "upload_date": "2024-08-24",
         "is_delete_after_upload": False,
         "waiting_verify": False,
         "number_of_days": "8",
         "day_gap": "1"
      }
   }
}

facebook_config = {
   "show_browser": False,
   "download_folder": "",
   "registered_account": [
      "badboymmo1901@gmail.com",
      "dxthienx2@gmail.com"
   ],
   "template": {
      "Super Review": {
         "account": "badboymmo1901@gmail.com",
         "password": "thien191!",
         "upload_folder": "",
         "publish_times": "07:30:PM",
         "title": "Review Phim hay: ",
         "description": "#phim #phimreview #phimhay #phimanime #reviewphim  #reviewphimhay #reviewanime #phimanime #phimhoathinh #phimhoathinhnhatban #topphim #phimhaynhat #phimmoinhay",
         "is_title_plus_video_name": True,
         "upload_date": "2024-08-11",
         "show_browser": False,
         "is_delete_after_upload": False,
         "waiting_verify": False,
         "number_of_days": "10",
         "day_gap": "1"
      },
      "Humor Haven - Relaxing Moment": {
         "account": "badboymmo1901@gmail.com",
         "password": "thien191!",
         "upload_folder": "",
         "description": "",
         "publish_times": "",
         "title": "",
         "is_title_plus_video_name": False,
         "upload_date": "2024-08-07",
         "show_browser": False,
         "is_delete_after_upload": False,
         "waiting_verify": False,
         "number_of_days": "10",
         "day_gap": "1"
      },
      "Tuy\u1ec3n T\u1eadp Phim Hay": {
         "account": "badboymmo1901@gmail.com",
         "password": "thien191!",
         "upload_folder": "",
         "description": "-------------------------------------------------------------------\n#reviewphim #t\u00f3mt\u1eaftphim #phimhay #reviewphimm\u1edbi #topphimhay #phimchi\u1ebfur\u1ea1p #reviewseries #phimkinh\u0111i\u1ec3n #t\u00f3mt\u1eaft #trailerphim #c\u1ea3mnh\u1eadnphim #t\u00f3mt\u1eaftphimng\u1eafn #phimbomt\u1ea5n #phimt\u00ecnhc\u1ea3m #phimh\u00e0nh\u0111\u1ed9ng #phimh\u00e0i  #phimc\u1ed5trang #phimkinhd\u1ecb #phimh\u00e0i #phiml\u1ebb #phimh\u00e0nh\u0111\u1ed9nghay #reviewphimhay #phimt\u00e2ml\u00fdhay #phimchi\u1ebfur\u1ea1phay #t\u00f3mt\u1eaftphimhay #phimhot #phimn\u1ed5i ti\u1ebfng #phimm\u1edbinh\u1ea5t #t\u1ed5ngh\u1ee3pphimhay #phimnextflix  #c\u1ef1chay #si\u00eauhay #phimd\u00e0it\u1eadp #phimhaytronbo #phimh\u00e0nqu\u1ed1chay #phimh\u00e0nh\u0111\u1ed9ngh\u00e0nqu\u1ed1c #m\u1edbinh\u1ea5t #xemnhi\u1ec1u",
         "publish_times": "10:30:AM, 8:00:PM",
         "title": "T\u00f3m T\u1eaft Phim Hay: ",
         "is_title_plus_video_name": True,
         "upload_date": "2024-08-24",
         "show_browser": False,
         "is_delete_after_upload": True,
         "waiting_verify": False,
         "number_of_days": "10",
         "day_gap": "1"
      }
   }
}


def load_youtube_config():
    if os.path.exists(youtube_config_path):
        config = get_json_data(youtube_config_path)
    else:
        config = youtube_config
    save_to_json_file(config, youtube_config_path)
    return config

def load_tiktok_config():
    if os.path.exists(tiktok_config_path):
        config = get_json_data(tiktok_config_path)
    else:
        config = tiktok_config
    save_to_json_file(config, tiktok_config_path)
    return config

def load_facebook_config():
    if os.path.exists(facebook_config_path):
        config = get_json_data(facebook_config_path)
    else:
        config = facebook_config
    save_to_json_file(config, facebook_config_path)
    return config

