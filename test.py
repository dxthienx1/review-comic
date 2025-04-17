# from common_function import *
import re

def number_to_vietnamese_with_units(text):
    number_words = {
        0: "không", 1: "một", 2: "hai", 3: "ba", 4: "bốn", 5: "năm",
        6: "sáu", 7: "bảy", 8: "tám", 9: "chín", 10: "mười",
        11: "mười một", 12: "mười hai", 13: "mười ba", 14: "mười bốn",
        15: "mười lăm", 16: "mười sáu", 17: "mười bảy", 18: "mười tám", 19: "mười chín",
        20: "hai mươi", 30: "ba mươi", 40: "bốn mươi", 50: "năm mươi",
        60: "sáu mươi", 70: "bảy mươi", 80: "tám mươi", 90: "chín mươi"
    }

    unit_mapping = {
        "km": "ki lô mét", "m": "mét", "cm": "xen ti mét", "mm": "mi li mét",
        "h": "giờ", "s": "giây", "ms": "mi li giây", "%": "phần trăm",
        "kg": "ki lô gam", "g": "gam"
    }

    def read_number(n):
        n = int(n)
        if n < 20:
            return number_words[n]
        elif n < 100:
            chuc = (n // 10) * 10
            donvi = n % 10
            if donvi == 0:
                return number_words[chuc]
            if donvi == 5:
                return number_words[chuc] + " lăm"
            return number_words[chuc] + " " + number_words[donvi]
        elif n < 1000:
            tram = n // 100
            chuc_dv = n % 100
            res = number_words[tram] + " trăm"
            if chuc_dv == 0:
                return res
            return res + " " + read_number(chuc_dv)
        else:
            parts = []
            unit_names = ["", "nghìn", "triệu", "tỷ"]
            str_n = str(n)
            while len(str_n) % 3 != 0:
                str_n = '0' + str_n
            groups = [str_n[i:i+3] for i in range(0, len(str_n), 3)]
            for i, group in enumerate(groups):
                val = int(group)
                if val == 0:
                    continue
                words = read_number(val)
                unit = unit_names[len(groups) - 1 - i]
                parts.append(words + (" " + unit if unit else ""))
            return " ".join(parts)

    def convert_units(match):
        raw_num = match.group(1)
        unit = match.group(2)
        unit_text = unit_mapping.get(unit, unit)

        if re.match(r"^\d{1,3}(\.\d{3})+$", raw_num):  # 1.000.000 style
            raw_num = raw_num.replace(".", "")
        elif re.match(r"^\d+[.,]\d+$", raw_num):  # 97.05 or 1,4
            sep = "." if "." in raw_num else ","
            int_part, dec_part = raw_num.split(sep)
            int_text = read_number(int_part)
            dec_text = " ".join([number_words[int(d)] for d in dec_part])
            return f"{int_text} phẩy {dec_text} {unit_text}"
        
        num = int(raw_num.replace(".", ""))
        return read_number(num) + " " + unit_text

    def convert_decimal(match):
        int_part = match.group(1)
        dec_part = match.group(2)
        return read_number(int_part) + " phẩy " + " ".join([number_words[int(d)] for d in dec_part])

    def convert_integer(match):
        return read_number(match.group(0))

    # Xử lý số có đơn vị trước
    text = re.sub(r"(\d+(?:[.,]\d+)?)(km|m|cm|mm|h|s|ms|%|kg|g)\b", convert_units, text)

    # Số thập phân
    text = re.sub(r"(\d+)[.,](\d+)", convert_decimal, text)

    # Số nguyên (hàng nghìn có thể có dấu chấm)
    text = re.sub(r"\b(\d{1,3}(?:\.\d{3})+)\b", lambda m: read_number(m.group(1).replace(".", "")), text)

    # Số nguyên thông thường
    text = re.sub(r"\b\d+\b", convert_integer, text)

    return text




tttt = "1.4 - 12.5 - 250kg - 57g - 97.05km - 2345 - - 15mm - 300cm - 340.56 - 1000500000 - 2000000"
gg = number_to_vietnamese_with_units(tttt)
print(gg)

# def split_image_by_white_space(image_path, output_folder=None, min_space_height=40, threshold_value=230):
#     if not output_folder:
#         output_folder = os.path.join(os.path.dirname(image_path), 'split_images')
#     os.makedirs(output_folder, exist_ok=True)
#     # Đọc ảnh và chuyển sang ảnh xám
#     img = cv2.imread(image_path)
#     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#     # Nhị phân hóa ảnh trắng đen
#     _, binary = cv2.threshold(gray, threshold_value, 255, cv2.THRESH_BINARY)
#     # Tính trung bình độ sáng theo từng dòng
#     row_avg = np.mean(binary, axis=1)
#     # Tìm các dòng có độ trắng gần như tuyệt đối
#     white_lines = np.where(row_avg > 245)[0]
#     # Gom các dòng trắng liên tiếp thành các cụm
#     white_blocks = []
#     for k, g in groupby(enumerate(white_lines), lambda ix: ix[0] - ix[1]):
#         block = list(map(itemgetter(1), g))
#         if len(block) >= min_space_height:
#             white_blocks.append((block[0], block[-1]))
#     # Cắt hình tại vị trí trung tâm của mỗi vùng trắng
#     img_height = img.shape[0]
#     prev_cut = 0
#     count = 1
#     for top, bottom in white_blocks:
#         middle = (top + bottom) // 2
#         # Kiểm tra nếu vùng cắt đủ lớn để không bị cắt trúng chữ
#         if middle - prev_cut > 200:
#             crop = img[prev_cut:middle, :]
#             out_path = os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0]}_part_{count}.png")
#             cv2.imwrite(out_path, crop)
#             print(f"✅ Đã lưu: {out_path}")
#             count += 1
#             prev_cut = middle
#     # Cắt phần còn lại nếu vẫn còn dư dưới
#     if img_height - prev_cut > 200:
#         crop = img[prev_cut:, :]
#         out_path = os.path.join(output_folder, f"{os.path.basename(image_path).split('.')[0]}_part_{count}.png")
#         cv2.imwrite(out_path, crop)
#         print(f"✅ Đã lưu: {out_path}")

#     print("✔️ Hoàn tất cắt ảnh theo khoảng trắng.")

# # Gọi hàm test
# split_image_by_white_space("E:\\Python\\developping\\review comic\\test\\1.jpg")
