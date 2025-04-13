from common_function import *

def split_image_by_white_space(image_path, output_folder=None, min_space_height=40, threshold_value=230):
    if not output_folder:
        output_folder = os.path.join(os.path.dirname(image_path), 'split_images')
    os.makedirs(output_folder, exist_ok=True)
    # Đọc ảnh và chuyển sang ảnh xám
    img = cv2.imread(image_path)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Nhị phân hóa ảnh trắng đen
    _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
    # Tính trung bình độ sáng theo từng dòng
    row_avg = np.mean(binary, axis=1)
    # Tìm các dòng có độ trắng gần như tuyệt đối
    white_lines = np.where(row_avg > 245)[0]
    # Gom các dòng trắng liên tiếp thành các cụm
    white_blocks = []
    for k, g in groupby(enumerate(white_lines), lambda ix: ix[0] - ix[1]):
        block = list(map(itemgetter(1), g))
        if len(block) >= min_space_height:
            white_blocks.append((block[0], block[-1]))
    # Cắt hình tại vị trí trung tâm của mỗi vùng trắng
    img_height = img.shape[0]
    prev_cut = 0
    count = 1
    for top, bottom in white_blocks:
        middle = (top + bottom) // 2
        # Kiểm tra nếu vùng cắt đủ lớn để không bị cắt trúng chữ
        if middle - prev_cut > 200:
            crop = img[prev_cut:middle, :]
            out_path = os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0]}_part_{count}.png")
            cv2.imwrite(out_path, crop)
            print(f"✅ Đã lưu: {out_path}")
            count += 1
            prev_cut = middle
    # Cắt phần còn lại nếu vẫn còn dư dưới
    if img_height - prev_cut > 200:
        crop = img[prev_cut:, :]
        out_path = os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0]}_part_{count}.png")
        cv2.imwrite(out_path, crop)
        print(f"✅ Đã lưu: {out_path}")

    print("✔️ Hoàn tất cắt ảnh theo khoảng trắng.")

# Gọi hàm test
split_image_by_white_space("E:\\Python\\developping\\review comic\\test\\1.jpg")
