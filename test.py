# from common_function import *
import re

def number_to_english_with_units(text):
    words = {
        0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five",
        6: "six", 7: "seven", 8: "eight", 9: "nine", 10: "ten",
        11: "eleven", 12: "twelve", 13: "thirteen", 14: "fourteen",
        15: "fifteen", 16: "sixteen", 17: "seventeen", 18: "eighteen",
        19: "nineteen", 20: "twenty", 30: "thirty", 40: "forty",
        50: "fifty", 60: "sixty", 70: "seventy", 80: "eighty", 90: "ninety"
    }
    units = ["", "thousand", "million", "billion", "trillion"]
    unit_mapping = {
        "km": "kilometers", "m": "meters", "cm": "centimeters", "mm": "millimeters",
        "h": "hours", "s": "seconds", "ms": "milliseconds", "%": "percent",
        "kg": "kilograms", "g": "grams"
    }

    def number_to_english(number):
        number = int(number)
        if number == 0:
            return "zero"

        def read_three_digits(num):
            hundreds = num // 100
            tens_units = num % 100
            result = []

            if hundreds > 0:
                result.append(f"{words[hundreds]} hundred")
            if tens_units > 0:
                if tens_units < 20:
                    result.append(words[tens_units])
                else:
                    tens = tens_units // 10 * 10
                    ones = tens_units % 10
                    result.append(words[tens])
                    if ones > 0:
                        result.append(words[ones])
            return " ".join(result)

        parts = []
        idx = 0
        while number > 0:
            num_part = number % 1000
            if num_part > 0:
                part = read_three_digits(num_part)
                if units[idx]:
                    part += f" {units[idx]}"
                parts.append(part)
            number //= 1000
            idx += 1
        return " ".join(reversed(parts))

    def convert_units(match):
        raw_number = match.group(1)
        unit = match.group(2)
        unit_text = unit_mapping.get(unit, unit)

        if "," in raw_number:
            raw_number = raw_number.replace(",", "")
        if "." in raw_number:
            integer_part, decimal_part = raw_number.split(".")
            integer_text = number_to_english(integer_part)
            decimal_text = " ".join([words[int(d)] for d in decimal_part])
            return f"{integer_text} point {decimal_text} {unit_text}"
        else:
            return f"{number_to_english(raw_number)} {unit_text}"

    def convert_decimal(match):
        integer_part = match.group(1).replace(",", "")
        decimal_part = match.group(2)
        return f"{number_to_english(integer_part)} point {' '.join([words[int(d)] for d in decimal_part])}"

    def convert_integer(match):
        number = match.group(0).replace(",", "")
        return number_to_english(number)

    # Xử lý số có đơn vị và tránh trùng lặp đơn vị
    text = re.sub(r"(\d{1,3}(?:,\d{3})*(?:\.\d+)?|\d+\.\d+)(?=\s*(km|m|cm|mm|h|s|ms|%|kg|g))", convert_units, text)

    # Decimal độc lập (không có đơn vị)
    text = re.sub(r"\b(\d{1,3}(?:,\d{3})*)\.(\d+)\b", convert_decimal, text)

    # Số nguyên có dấu phẩy
    text = re.sub(r"\b\d{1,3}(?:,\d{3})+\b", convert_integer, text)

    # Tránh đổi sai các dạng giờ, ký hiệu, etc.
    text = re.sub(r"\b\d+\b", lambda m: convert_integer(m) if not re.match(r"\d+:\d+", text[m.start():]) else m.group(0), text)

    # Xử lý các đơn vị đã gán vào cuối (để tránh lặp đơn vị)
    text = re.sub(r"(kg|g|km|m|cm|mm|h|s|ms|%)(?=\b)", lambda m: m.group(1) if m.group(1) not in ["kg", "g", "km", "m", "cm", "mm", "h", "s", "ms", "%"] else "", text)

    return text




tttt = "1.4 - 12.5 - 250kg - 57g - 97.05km - 2345 - - 15mm - 300cm - 340.56 - 1000500000 - 2000000"
gg = number_to_english_with_units(tttt)
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
