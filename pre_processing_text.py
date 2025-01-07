from common_function import *

def add_txt_to_metadata(txt_file, csv_file, start_idx=1, type_audio='wav', speaker_name='vi_female', is_eval=False):
    import csv
    try:
        file_exists = os.path.isfile(csv_file)
        with open(txt_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()
 
        with open(csv_file, 'a', encoding='utf-8', newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_MINIMAL)
            if not file_exists:
                writer.writerow(["audio_file", "text", "speaker_name"])
            for i, line in enumerate(lines):
                try:
                    transcription = line.strip()
                    if not transcription or transcription.isdigit():
                        continue
                    text = cleaner_text(transcription)
                    if is_eval:
                        writer.writerow([f"eval/eval_{start_idx}.{type_audio}", text, speaker_name])
                    else:
                        writer.writerow([f"wavs/{start_idx}.{type_audio}", text, speaker_name])
                    start_idx += 1
                except Exception as e:
                    print(f"Lỗi khi xử lý dòng {i + 1}: {e}")
                    return
        
        print(f"Hoàn thành! Dữ liệu đã được ghi vào {csv_file}")
    except Exception as e:
        print(f"Đã xảy ra lỗi: {e}")

audio_folder = 'wavs'
txt_file_path = "E:\\Python\\developping\\review comic\\test\\1_1.txt"
start_idx = 5434
is_eval = False

if is_eval:
    metadata_path = os.path.join(current_dir, 'dataset', 'vietnam', 'eval.csv')
else:
    metadata_path = os.path.join(current_dir, 'dataset', 'vietnam', 'train.csv')

add_txt_to_metadata(txt_file_path, metadata_path, start_idx, type_audio='wav', speaker_name='vi_female', is_eval=is_eval)









#khi huấn luyện từ đầu thì thêm các ký tự trong metadata vào file vocab.txt
# def update_vocab_from_metadata(metadata_file, vocab_file):
#     # Đọc nội dung của file vocab.txt
#     with open(vocab_file, 'r', encoding='utf-8') as f:
#         vocab = set(f.read().splitlines())

#     with open(metadata_file, 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         for row in reader:
#             text = row[1]
#             words = text.split()
            
#             for word in words:
#                 if word not in vocab:
#                     vocab.add(word)

#     with open(vocab_file, 'a', encoding='utf-8') as f:  # Mở file ở chế độ append
#         for word in sorted(vocab):  # Bạn có thể bỏ qua việc sắp xếp nếu không cần thiết
#             f.write(word + '\n')
#     print(f"Đã thêm các từ mới vào {vocab_file}")
# update_vocab_from_metadata(metadata_path, "e:\\Python\\text to speech\\F5 TTS\\F5-TTS\\vietnamese_dataset\\vietnamese_dataset_custom\\vocab.txt")




# #edit file csv
# def add_voice_to_csv(input_file, output_file, voice_tag="vi_female"):
#     try:
#         # Đọc nội dung file CSV
#         with open(input_file, 'r', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile, delimiter='|')
#             rows = [row for row in reader]
        
#         # Thêm voice tag vào cuối mỗi dòng
#         updated_rows = []
#         for i, row in enumerate(rows):
#             if i == 0:  # Header đã sửa ở bước trên
#                 row = ["audio_file", "text", "speaker_name"]
#                 updated_rows.append(row)
#             else:
#                 row[0] = f'eval/eval_{i}.wav'
#                 updated_rows.append([row[0], row[1], voice_tag])
        
#         # Ghi nội dung mới vào file đầu ra
#         with open(output_file, 'w', encoding='utf-8', newline='') as csvfile:
#             writer = csv.writer(csvfile, delimiter='|')
#             writer.writerows(updated_rows)
        
    
#     except Exception as e:
#         print(f"Đã xảy ra lỗi: {e}")

# # Sử dụng hàm
# input_csv = "E:\\Python\\text to speech\\XTTS - v2\\vietnamese_dataset\\vietnam\\eval1.csv"
# output_csv = "E:\\Python\\text to speech\\XTTS - v2\\vietnamese_dataset\\vietnam\\eval.csv"
# add_voice_to_csv(input_csv, output_csv)