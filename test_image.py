from common_function import *

def merge_txt_files(input_dir, output_dir=None):
    # Lấy danh sách tất cả các tệp .txt trong thư mục
    txt_files = get_file_in_folder_by_type(input_dir, '.txt') or []
    if not output_dir:
        output_dir = os.path.join(input_dir, 'output')
        os.makedirs(output_dir, exist_ok=True)
    # Chia danh sách file thành từng nhóm 20 file
    for i in range(0, len(txt_files), 20):
        batch_files = txt_files[i:i+20]
        merged_content = ""
        
        for file in batch_files:
            with open(os.path.join(input_dir, file), 'r', encoding='utf-8') as f:
                merged_content += f.read() + '\n'  # Đọc nội dung và nối thêm dòng mới
        
        # Tạo tên file đầu ra từ file đầu và cuối trong batch
        first_file_name = os.path.splitext(batch_files[0])[0]
        last_file_name = os.path.splitext(batch_files[-1])[0]
        output_filename = f'{first_file_name}_{last_file_name}.txt'
        output_path = os.path.join(output_dir, output_filename)
        
        # Ghi nội dung đã ghép vào tệp mới
        with open(output_path, 'w', encoding='utf-8') as out_file:
            out_file.write(merged_content)
        
        print(f"Đã tạo {output_filename}")

# Ví dụ sử dụng
merge_txt_files("E:\\Python\\developping\\review comic\\test\\tai truyen chu\\thieu gia bi bo roi")