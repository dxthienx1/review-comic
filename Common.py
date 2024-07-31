from common_function import os, datetime, save_to_json_file, get_json_data, get_json_data_from_url, sys, dtime, config_path, youtube_config_path, facebook_config_path, tiktok_config_path

def load_config():
    if os.path.exists(config_path):
        config = get_json_data(config_path)
    else:
        config = {
            "registered_gmails":["dxthienx2@gmail.com", "dxthienx10@gmail.com", "tranhangbk.001@gmail.com", "tranghangbk.002@gmail.com"],
            "registered_channel":["UCw84Zm5eXZHTMONt_OiqRXA", "UCxBuEz6aETSTRB55MoV9pKA", "UChWQUjInuNW5rVWvVlN-mJg", "UC9D6E5sCF2wGx1ApLEnr5XQ", "UCgxzKC2hwgkod7Xb2Lpb5uA"],
            "auto_channel_id":"",
            "download_folder":"",
            "output_folder":"",
            "from_language": "en-us",
            "to_language": "vi",
            "auto_start": False,

            "current_youtube_account": "dxthienx2@gmail.com",
            "current_tiktok_account": "dxthienx2@gmail.com",
            "current_facebook_account": "dxthienx2@gmail.com",
            "current_channel": "",
            "current_channel_id": "",

            "download_by_video_url": "",
            "download_by_channel_id": "",
            "download_by_channel_url": "",
            "filter_by_like": 100000,
            "filter_by_views": 5000000,

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
            "min_time_to_change_zoom": "3", 
            "max_time_to_change_zoom": "7", 
            "top_image_path": "",
            "bot_image_path": "",
            "top_height": "10", 
            "bot_height": "10", 
            "water_path": "",
            "vertical_watermask_position": "50",
            "horizontal_watermask_position": "50",

            "first_cut_audio": "", 
            "end_cut_audio": "", 
            "audio_speed": "", 
            "reversed_audio": False, 
            "audio_edit_path": "", 
            "video_get_audio_path": "", 
            "video_get_audio_url": "", 

            "supported_languages": {
                "ar": "Arabic",
                "bn": "Bengali",
                "zh-cn": "Chinese (Simplified, China)",
                "zh-tw": "Chinese (Traditional, Taiwan)",
                "cs": "Czech",
                "da": "Danish",
                "nl": "Dutch",
                "en-us": "English (United States)",
                "en-uk": "English (United Kingdom)",
                "fi": "Finnish",
                "fr": "French",
                "de": "German",
                "el": "Greek",
                "he": "Hebrew",
                "hi": "Hindi",
                "hu": "Hungarian",
                "id": "Indonesian",
                "it": "Italian",
                "ja": "Japanese",
                "ko": "Korean",
                "ms": "Malay",
                "no": "Norwegian",
                "fa": "Persian",
                "pl": "Polish",
                "pt": "Portuguese",
                "ro": "Romanian",
                "ru": "Russian",
                "sr": "Serbian",
                "sk": "Slovak",
                "sl": "Slovenian",
                "es": "Spanish",
                "sv": "Swedish",
                "th": "Thai",
                "tr": "Turkish",
                "uk": "Ukrainian",
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
   "template": {
      "Brain Training": {
         "title": "IQ Quiz Every Day - Perfect Yourself | Who can solve it in 30 seconds?  | ",
         "is_title_plus_video_name": True,
         "description": "Welcome to \"Brain Training - Perfect Yourself\"! \nOur channel is dedicated to bringing you engaging and challenging IQ tests. Each video will help you explore and enhance your logical thinking, analytical skills, and problem-solving abilities. We offer a variety of questions, ranging from simple to complex, designed to improve your cognitive skills and help you achieve new milestones in your intellectual journey. Join us to test and elevate your IQ in a fun and rewarding way!\n----------------------------------------------------------------------------------------------------------------------------------------\nYour every like and share will motivate me to try harder!\n\n----------------------------------------------------------------------------------------------------------------------------------------\nWatch more videos:\nhttps://www.youtube.com/channel/UCxBuEz6aETSTRB55MoV9pKA/?sub_confirmation=1\n----------------------------------------------------------------------------------------------------------------------------------------\n- Thank you for following and supporting the channel recently!\n- Wishing you the best!\n----------------------------------------------------------------------------------------------------------------------------------------\nTags:\n#BrainTraining #SelfImprovement #ElevateYourself #IQTest #MentalExercise #BoostYourBrain #CognitiveSkills #MindPower #SmartThinking #IntellectualGrowth #BrainBoost #MentalChallenge #SelfGrowth #KnowledgeIsPower #TrainYourBrain #EnhanceYourMind #BrainTeasers #SmartGoals #PersonalDevelopment #ThinkSmart #UnlockYourPotential #BrainWorkout #IQChallenge #IntellectualDevelopment #Brainy #MindEnhancement #BrainFitness #IQBoost #MindGrowth #ElevateKnowledge #Trending #Trend",
         "tags": "Trending,Trend,BrainTraining,SelfImprovement,PersonalDevelopment,IQTest,MentalExercise,BoostYourBrain,MindPower,CognitiveSkills,SmartThinking,IntellectualGrowth,BrainBoost,SelfGrowth,TrainYourBrain,KnowledgeIsPower,BrainTeasers,MindEnhancement,BrainWorkout,IQChallenge,UnlockYourPotential,BrainFitness,SmartGoals,MentalChallenge,IQBoost,MindGrowth,Brainy,IntellectualDevelopment,ElevateYourself,MemoryTraining,CriticalThinking,ProblemSolving",
         "category_id": "Education",
         "privacy_status": "public",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "2024-07-27",
         "publish_times": "01:00:00",
         "upload_folder": "E:/Video/Brain Training",
         "channel_id": "UCxBuEz6aETSTRB55MoV9pKA",
         "gmail": "tranghangbk.002@gmail.com",
         "last_auto_upload_date": "2024-07-22"
      },
      "Luyen Tri Nao": {
         "title": "Test IQ M\u1ed7i Ng\u00e0y | Ph\u00e1t Tri\u1ec3n Tr\u00ed N\u00e3o | Ai tr\u1ea3 l\u1eddi trong 20s th\u00ec qu\u00e1 \u0111\u1ec9nh | ",
         "is_title_plus_video_name": True,
         "description": "Ch\u00e0o m\u1eebng b\u1ea1n \u0111\u1ebfn v\u1edbi \"Luy\u1ec7n Tr\u00ed N\u00e3o - Ho\u00e0n Thi\u1ec7n B\u1ea3n Th\u00e2n\"!\nK\u00eanh c\u1ee7a ch\u00fang t\u00f4i cam k\u1ebft mang \u0111\u1ebfn cho b\u1ea1n nh\u1eefng b\u00e0i ki\u1ec3m tra IQ th\u00fa v\u1ecb v\u00e0 \u0111\u1ea7y th\u1eed th\u00e1ch. M\u1ed7i video s\u1ebd gi\u00fap b\u1ea1n kh\u00e1m ph\u00e1 v\u00e0 n\u00e2ng cao kh\u1ea3 n\u0103ng t\u01b0 duy logic, luy\u1ec7n ph\u1ea3n x\u1ea1. \nH\u00e3y tham gia c\u00f9ng ch\u00fang t\u00f4i \u0111\u1ec3 ki\u1ec3m tra v\u00e0 n\u00e2ng cao IQ c\u1ee7a b\u1ea1n m\u1ed9t c\u00e1ch vui v\u1ebb v\u00e0 b\u1ed5 \u00edch!\n----------------------------------------------------------------------------------------------------------------------------------------\nM\u1ed7i l\u01b0\u1ee3t th\u00edch v\u00e0 chia s\u1ebb c\u1ee7a b\u1ea1n s\u1ebd l\u00e0 \u0111\u1ed9ng l\u1ef1c \u0111\u1ec3 t\u00f4i c\u1ed1 g\u1eafng h\u01a1n!\n\n----------------------------------------------------------------------------------------------------------------------------------------\nXem th\u00eam nh\u1eefng c\u00e2u h\u1ecfi kh\u00f3 :\nhttps://www.youtube.com/channel/UCxBuEz6aETSTRB55MoV9pKA/?sub_confirmation=1\n\n----------------------------------------------------------------------------------------------------------------------------------------\n-  C\u1ea3m \u01a1n b\u1ea1n \u0111\u00e3 theo d\u00f5i v\u00e0 \u1ee7ng h\u1ed9 k\u00eanh trong th\u1eddi gian qua!\n- Ch\u00fac b\u1ea1n nh\u1eefng \u0111i\u1ec1u tuy\u1ec7t v\u1eddi nh\u1ea5t!\n\n----------------------------------------------------------------------------------------------------------------------------------------\nTags:\n#Luy\u1ec7nTr\u00edN\u00e3o #Ho\u00e0nThi\u1ec7nB\u1ea3nTh\u00e2n #N\u00e2ngCaoB\u1ea3nTh\u00e2n #Ki\u1ec3mTraIQ #T\u1eadpLuy\u1ec7nTr\u00edN\u00e3o #T\u0103ngC\u01b0\u1eddngTr\u00edN\u00e3o #K\u1ef9N\u0103ngNh\u1eadnTh\u1ee9c #S\u1ee9cM\u1ea1nhT\u01b0Duy #T\u01b0DuyTh\u00f4ngMinh #Ph\u00e1tTri\u1ec3nTr\u00edTu\u1ec7 #T\u0103ngC\u01b0\u1eddngTr\u00edTu\u1ec7 #Th\u1eedTh\u00e1chTr\u00edTu\u1ec7 #Ph\u00e1tTri\u1ec3nB\u1ea3nTh\u00e2n #Ki\u1ebfnTh\u1ee9cL\u00e0S\u1ee9cM\u1ea1nh #R\u00e8nLuy\u1ec7nTr\u00edN\u00e3o #N\u00e2ngCaoT\u01b0Duy #C\u00e2u\u0110\u1ed1Tr\u00edN\u00e3o #M\u1ee5cTi\u00eauTh\u00f4ngMinh #Ph\u00e1tTri\u1ec3nC\u00e1Nh\u00e2n #T\u01b0DuyTh\u00f4ngMinh #KhaiPh\u00e1Ti\u1ec1mN\u0103ng #Luy\u1ec7nT\u1eadpTr\u00edN\u00e3o #Th\u1eedTh\u00e1chIQ #Ph\u00e1tTri\u1ec3nTr\u00edTu\u1ec7 #Th\u00f4ngMinh #N\u00e2ngCaoT\u00e2mTr\u00ed #R\u00e8nLuy\u1ec7nTr\u00edTu\u1ec7 #T\u0103ngIQ #Ph\u00e1tTri\u1ec3nT\u00e2mTr\u00ed #N\u00e2ngCaoKi\u1ebfnTh\u1ee9c #xuh\u01b0\u1edbng #th\u1ecbnh\u00e0nh",
         "tags": "Luy\u1ec7nTr\u00edN\u00e3o,Ho\u00e0nThi\u1ec7nB\u1ea3nTh\u00e2n,N\u00e2ngCaoB\u1ea3nTh\u00e2n,Ki\u1ec3mTraIQ,T\u1eadpLuy\u1ec7nTr\u00edN\u00e3o,T\u0103ngC\u01b0\u1eddngTr\u00edN\u00e3o,K\u1ef9N\u0103ngNh\u1eadnTh\u1ee9c,S\u1ee9cM\u1ea1nhT\u01b0Duy,T\u01b0DuyTh\u00f4ngMinh,Ph\u00e1tTri\u1ec3nTr\u00edTu\u1ec7,T\u0103ngC\u01b0\u1eddngTr\u00edTu\u1ec7,Th\u1eedTh\u00e1chTr\u00edTu\u1ec7,Ph\u00e1tTri\u1ec3nB\u1ea3nTh\u00e2n,Ki\u1ebfnTh\u1ee9cL\u00e0S\u1ee9cM\u1ea1nh,R\u00e8nLuy\u1ec7nTr\u00edN\u00e3o,N\u00e2ngCaoT\u01b0Duy,C\u00e2u\u0110\u1ed1Tr\u00edN\u00e3o,M\u1ee5cTi\u00eauTh\u00f4ngMinh,Ph\u00e1tTri\u1ec3nC\u00e1Nh\u00e2n,T\u01b0DuyTh\u00f4ngMinh,KhaiPh\u00e1Ti\u1ec1mN\u0103ng,Luy\u1ec7nT\u1eadpTr\u00edN\u00e3o,Th\u1eedTh\u00e1chIQ,Ph\u00e1tTri\u1ec3nTr\u00edTu\u1ec7,Th\u00f4ngMinh,N\u00e2ngCaoT\u00e2mTr\u00ed,R\u00e8nLuy\u1ec7nTr\u00edTu\u1ec7,T\u0103ngIQ,Ph\u00e1tTri\u1ec3nT\u00e2mTr\u00ed,N\u00e2ngCaoKi\u1ebfnTh\u1ee9c,xuh\u01b0\u1edbng,th\u1ecbnhh\u00e0nh",
         "category_id": "Education",
         "privacy_status": "public",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "2024-07-28",
         "publish_times": "19:30:00",
         "upload_folder": "E:/Video/Brain Test",
         "channel_id": "UCw84Zm5eXZHTMONt_OiqRXA",
         "gmail": "tranghangbk.002@gmail.com",
         "last_auto_upload_date": "2024-07-22"
      },
      "Animal_Funny_Version": {
         "title": "",
         "is_title_plus_video_name": True,
         "description": "Here are some unforgettable funny moments with animals. Enjoy hearty laughs with playful dogs, adorable cats, and many other creatures. \nDon't forget to follow for more hilarious videos!\n----------------------------------------------------------------------------------------------------------------------------------------\nTag:\n#FunnyAnimals #FunnyPets #AnimalHumor #PetsOfInstagram #AnimalVideos #FunnyAnimalVi#CuteAndFunny #AnimalLovers #PetHumor #HilariousPets #AnimalsOfInstagram #PetsofTikTok #FunnyDog #FunnyCat #PetsDaily #FunnyAnimalMoments #CrazyAnimals #PetComedy #AdorableAnimals #FunnyAnimals #FunnyPets #CutePets #AnimalHumor #PetEntertainment #PetLaughs #trend #trending\n#Th\u00faC\u01b0ngH\u00e0iH\u01b0\u1edbc #VideoTh\u00faVui #Kho\u1ea3nhKh\u1eafcH\u00e0iTh\u00faC\u01b0ng #\u0110\u1ed9ngV\u1eadtVuiNh\u1ed9n #Th\u00faC\u01b0ng\u0110\u00e1ngY\u00eau #VideoH\u00e0iTh\u00faC\u01b0ng #Th\u00faC\u01b0ngB\u00e1\u0110\u1ea1o #VideoTh\u00faC\u01b0ng #Gi\u1ea3iTr\u00edV\u1edbiTh\u00faC\u01b0ng #Th\u00faC\u01b0ngVuiNh\u1ed9n #h\u00e0ih\u01b0\u1edbc #vuiv\u1ebb #d\u1ec5th\u01b0\u01a1ng #\u0111\u00e1ngy\u00eau #ch\u00f3 #m\u00e8o #c\u00fancon #c\u00fancon\u0111\u00e1ngy\u00eau #si\u00eaucute ##c\u1ef1ch\u00e0i #c\u1ef1chay #c\u1ef1cd\u1ec5th\u01b0\u01a1ng #xuh\u01b0\u1edbng #th\u1ecbnhh\u00e0nh",
         "tags": "FunnyAnimals,FunnyPets,AnimalLovers,FunnyDog,FunnyCat,FunnyAnimalMoments,CrazyAnimals,FunnyAnimals,FunnyPets,CutePets,AnimalHumor,PetEntertainment,PetLaughs,trending,Th\u00faC\u01b0ngH\u00e0iH\u01b0\u1edbc,VideoTh\u00faVui,Kho\u1ea3nhKh\u1eafcH\u00e0iTh\u00faC\u01b0ng,\u0110\u1ed9ngV\u1eadtVuiNh\u1ed9n,Th\u00faC\u01b0ng\u0110\u00e1ngY\u00eau,Gi\u1ea3iTr\u00edV\u1edbiTh\u00faC\u01b0ng,Th\u00faC\u01b0ngVuiNh\u1ed9n,h\u00e0ih\u01b0\u1edbc,vuiv\u1ebb,d\u1ec5th\u01b0\u01a1ng,c\u00fancon\u0111\u00e1ngy\u00eau,si\u00eaucute,c\u1ef1ch\u00e0i,c\u1ef1chay,c\u1ef1cd\u1ec5th\u01b0\u01a1ng",
         "category_id": "Pets & Animals",
         "privacy_status": "public",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "2024-07-27",
         "publish_times": "01:00:00,08:00:00,20:00:00",
         "upload_folder": "E:/Video/tranhangbk.001",
         "channel_id": "UChWQUjInuNW5rVWvVlN-mJg",
         "gmail": "tranhangbk.001@gmail.com",
         "last_auto_upload_date": "2024-07-22"
      },
      "Animal Funny Best Version": {
         "title": "",
         "is_title_plus_video_name": True,
         "description": "Here are some unforgettable funny moments with animals. Enjoy hearty laughs with playful dogs, adorable cats, and many other creatures. \nDon't forget to follow for more hilarious videos!\n----------------------------------------------------------------------------------------------------------------------------------------\nTag:\n#FunnyAnimals #FunnyPets #AnimalHumor #PetsOfInstagram #AnimalVideos #FunnyAnimalVi#CuteAndFunny #AnimalLovers #PetHumor #HilariousPets #AnimalsOfInstagram #PetsofTikTok #FunnyDog #FunnyCat #PetsDaily #FunnyAnimalMoments #CrazyAnimals #PetComedy #AdorableAnimals #FunnyAnimals #FunnyPets #CutePets #AnimalHumor #PetEntertainment #PetLaughs #trend #trending\n#Th\u00faC\u01b0ngH\u00e0iH\u01b0\u1edbc #VideoTh\u00faVui #Kho\u1ea3nhKh\u1eafcH\u00e0iTh\u00faC\u01b0ng #\u0110\u1ed9ngV\u1eadtVuiNh\u1ed9n #Th\u00faC\u01b0ng\u0110\u00e1ngY\u00eau #VideoH\u00e0iTh\u00faC\u01b0ng #Th\u00faC\u01b0ngB\u00e1\u0110\u1ea1o #VideoTh\u00faC\u01b0ng #Gi\u1ea3iTr\u00edV\u1edbiTh\u00faC\u01b0ng #Th\u00faC\u01b0ngVuiNh\u1ed9n #h\u00e0ih\u01b0\u1edbc #vuiv\u1ebb #d\u1ec5th\u01b0\u01a1ng #\u0111\u00e1ngy\u00eau #ch\u00f3 #m\u00e8o #c\u00fancon #c\u00fancon\u0111\u00e1ngy\u00eau #si\u00eaucute ##c\u1ef1ch\u00e0i #c\u1ef1chay #c\u1ef1cd\u1ec5th\u01b0\u01a1ng #xuh\u01b0\u1edbng #th\u1ecbnhh\u00e0nh",
         "tags": "funnyanimals,funnypets,animallovers,funnydog,funnycat,funnyanimalmoments,crazyanimals,funnyanimals,funnypets,cutepets,petlaughs,th\u00fac\u01b0ngh\u00e0ih\u01b0\u1edbc,kho\u1ea3nhkh\u1eafch\u00e0ih\u01b0\u1edbc,\u0111\u1ed9ngv\u1eadtvuinh\u1ed9n,th\u00fac\u01b0ngvuinh\u1ed9n,c\u1ef1ch\u00e0i",
         "category_id": "Pets & Animals",
         "privacy_status": "public",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "2024-07-28",
         "publish_times": "00:30:00,07:30:00,19:30:00",
         "upload_folder": "E:/Video/tranhangbk.002",
         "channel_id": "UC9D6E5sCF2wGx1ApLEnr5XQ",
         "gmail": "tranghangbk.002@gmail.com",
         "last_auto_upload_date": "2024-07-22"
      },
      "Super Review": {
         "title": "Phim Hay:  ",
         "is_title_plus_video_name": True,
         "description": "Ai Gh\u00e9 Qua Th\u00ec Cho M\u00ecnh Xin 1 Like v\u00e0 1 Follow \u0110\u1ec3 \u1ee6ng H\u1ed9 M\u00ecnh Nh\u00e9! \n---------------------------------------------------------------------------------------\nPh\u1ea7n m\u1ec1m qu\u1ea3n l\u00fd Youtube, Facebook, Tiktok:\n- T\u1ef1 \u0111\u1ed9ng \u0111\u0103ng video Youtube, Facebook, Tiktok. \n- T\u1ef1 \u0111\u1ed9ng t\u1ea3i t\u1ea5t c\u1ea3 c\u00e1c video c\u1ee7a 1 channel youtube, Tiktok b\u1ea5t k\u1ef3, c\u00f3 l\u1ecdc theo s\u1ed1 l\u01b0\u1ee3t like v\u00e0 view \u0111\u1ec3 t\u1ea3i nh\u1eefng video ch\u1ea5t l\u01b0\u1ee3ng. \n- Edit h\u00e0ng lo\u1ea1t video \u0111\u00e3 t\u1ea3i v\u1ec1 \u0111\u1ec3 l\u00e1ch b\u1ea3n quy\u1ec1n - Sau edit \u0111\u0103ng \u0111\u01b0\u1ee3c lu\u00f4n - Cam k\u1ebft sau edit kh\u00f4ng b\u1ecb b\u1eaft b\u1ea3n quy\u1ec1n.\n- Edit video, audio t\u00f9y ch\u1ec9nh theo \u00fd th\u00edch - L\u00e1ch b\u1ea3n quy\u1ec1n.\n- V\u00e0 ...\n---------------------------------------------------------------------------------------\n#manga review\n#manhwa review\n#anime review\n#reviewphimtruyentranh\n#reviewtruyentranh \n#reviewtruy\u1ec7ntranhfullb\u1ed9 \n#truy\u1ec7ntranhtuti\u00ean \n#truy\u1ec7ntranhxuy\u00eankh\u00f4ng \n#truy\u1ec7ntranhmanhwa \n#reviewtruy\u1ec7ntranhfull \n#reviewtruy\u1ec7nfull\n#truy\u1ec7ntranhhay\n#truy\u1ec7ntranhm\u1edbi\n#truy\u1ec7ntranhxuy\u00eankh\u00f4ng\n#truy\u1ec7ntranhmaingi\u1ea3heo\n#truy\u1ec7ntranhmainb\u00e1\n#truy\u1ec7ntranhtr\u01b0\u1eddngh\u1ecdc\n#anime\n#tuy\u1ec3nt\u1eadptruy\u1ec7ntranhhay\n#truy\u1ec7nho\u00e0n th\u00e0nh\n#truy\u1ec7ntranhho\u00e0nth\u00e0nh\n#truy\u1ec7ntranhfull\n#reup \n#reup100%\n#reup2024\n#h\u01b0\u1edbngd\u1eabnreupvideo\n#h\u01b0\u1edbngd\u1eabnreupvideom\u1edbinh\u1ea5t\n#reupyoutube \n#reuptiktok \n#reupfacebook  \n#reupvideo \n#Youtubemanagement  \n#facebookmanagement \n#tiktokmanagement \n#editvideo \n#l\u00e1chb\u1ea3nquy\u1ec1n \n#contentid \n#l\u00e1chcontentid\n-------------------------------------------------------\n* Super Review kh\u00f4ng s\u1edf h\u1eefu t\u1ea5t c\u1ea3 c\u00e1c t\u01b0 li\u1ec7u trong video m\u00e0 tu\u00e2n th\u1ee7 lu\u1eadt b\u1ea3n quy\u1ec1n v\u00e0 s\u1eed d\u1ee5ng h\u1ee3p l\u00fd lu\u1eadt Fair-Use (https://www.youtube.com/yt/copyright/)\nAll Music , Pictures, Videos and Sounds That Appear In This Video Are Owned By Their Respective Owners\n\"Copyright Disclaimer, Under Section 107 of the Copyright Act 1976, allowance is made for 'fair use' for purposes such as criticism, comment, news reporting, teaching, scholarship, and research. Fair use is a use permitted by copyright statute that might otherwise be infringing. Non-profit, educational or personal use tips the balance in favor of fair use.\"\n-------------------------------------------------------",
         "tags": "reviewphimtruyentranh, reviewtruyentranh, reviewtruy\u1ec7ntranhfullb\u1ed9, truy\u1ec7ntranhtuti\u00ean, truy\u1ec7ntranhxuy\u00eankh\u00f4ng, truy\u1ec7ntranhmanhwa, reviewtruy\u1ec7ntranhfull, reviewtruy\u1ec7nfull, truy\u1ec7ntranhhay, truy\u1ec7ntranhm\u1edbi, truy\u1ec7ntranhmaingi\u1ea3heo, truy\u1ec7ntranhmainb\u00e1, truy\u1ec7ntranhtr\u01b0\u1eddngh\u1ecdc, anime, tuy\u1ec3nt\u1eadptruy\u1ec7ntmanga review, manhwa review,anime review,ranhhay, truy\u1ec7nho\u00e0n th\u00e0nh, truy\u1ec7ntranhho\u00e0nth\u00e0nh, truy\u1ec7ntranhfull",
         "category_id": "Film & Animation",
         "privacy_status": "public",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "2024-07-29",
         "publish_times": "19:30:00",
         "upload_folder": "E:/Video/Super Review",
         "channel_id": "UCgxzKC2hwgkod7Xb2Lpb5uA",
         "gmail": "dxthienx10@gmail.com",
         "last_auto_upload_date": "2024-07-22"
      },
      "Funny Moments": {
         "gmail": "dxthienx10@gmail.com",
         "channel_id": "UCYJd1eetbGhbwJ8A9TP2Eiw",
         "title": "",
         "is_title_plus_video_name": True,
         "description": "",
         "tags": "",
         "category_id": "",
         "privacy_status": "private",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "",
         "publish_times": "",
         "upload_folder": "",
         "last_auto_upload_date": ""
      },
      "The Interesting Football": {
         "gmail": "dxthienx2@gmail.com",
         "channel_id": "UCS_BTKUld0EoDUFownHP3sA",
         "title": "",
         "is_title_plus_video_name": True,
         "description": "",
         "tags": "",
         "category_id": "",
         "privacy_status": "private",
         "license": "creativeCommon",
         "is_delete_video": False,
         "start_date": "",
         "publish_times": "",
         "upload_folder": "",
         "last_auto_upload_date": ""
      }
   },
   "current_youtube_account": "dxthienx2@gmail.com",
   "current_channel": "The Interesting Football",
   "download_folder": "E:/Video/Super Review/upload_finished",
   "download_by_video_url": "https://drive.google.com/uc?export=download&id=1zzsthUUDxl1B3XX9TpMJVG_laMTLa3n7",
   "download_by_channel_id": "",
   "filter_by_like": "",
   "filter_by_views": "",
   "dxthienx10@gmail.com": {
      "cnt_request_upload": 0
   },
   "dxthienx2@gmail.com": {
      "cnt_request_upload": 0
   }
}

tiktok_config = {
   "output_folder": "",
   "download_by_channel_url": "",
   "filter_by_like": 20000,
   "filter_by_views": 500000,
   "template": {
      "dxthienx1@gmail.com": {
         "account": "dxthienx1@gmail.com",
         "password": "thien191!",
         "upload_folder": "E:/Python/developping/Super-Social-Media/test",
         "publish_times": "08:00,21:30",
         "description": "Test Auto Upload by python",
         "upload_date": "2024-08-05"
      }
   },
   "registered_account": [
      "dxthienx1@gmail.com"
   ]
}

facebook_config = {
   "registered_account": [
      "badboymmo1901@gmail.com",
      "dxthienx2@gmail.com"
   ],
   "template": {
      "Super Review": {
         "account": "badboymmo1901@gmail.com",
         "password": "thien191!",
         "upload_folder": "E:/Python/developping/Super-Social-Media/test",
         "publish_times": "07:30:PM",
         "title": "",
         "description": "#phim #phimreview #phimhay #phimanime #reviewphim  #reviewphimhay #reviewanime #phimanime #phimhoathinh #phimhoathinhnhatban #topphim #phimhaynhat #phimmoinhay",
         "is_title_plus_video_name": True,
         "upload_date": "2024-07-31"
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