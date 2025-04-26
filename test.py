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
        # Đơn vị vận tốc, gia tốc
        "km/h2": "ki lô mét trên giờ bình phương",
        "km/h": "ki lô mét trên giờ",
        "m/s2": "mét trên giây bình phương",
        "m/s": "mét trên giây",
        "cm/s": "xen ti mét trên giây",

        # Đơn vị độ
        "°c": "độ xê",
        "°f": "độ ép",
        "°": "độ",

        # Độ dài - theo độ phức
        "km3": "ki lô mét khối",
        "km2": "ki lô mét vuông",
        "km": "ki lô mét",

        "m³": "mét khối",
        "m3": "mét khối",
        "m²": "mét vuông",
        "m2": "mét vuông",
        "m": "mét",

        "dm3": "đề xi mét khối",
        "dm2": "đề xi mét vuông",
        "dm": "đề xi mét",

        "cm³": "xen ti mét khối",
        "cm3": "xen ti mét khối",
        "cm²": "xen ti mét vuông",
        "cm2": "xen ti mét vuông",
        "cm": "xen ti mét",

        "mm³": "mi li mét khối",
        "mm3": "mi li mét khối",
        "mm²": "mi li mét vuông",
        "mm2": "mi li mét vuông",
        "mm": "mi li mét",

        "nm": "nano mét",
        "inch": "in",
        "in": "in",
        "ft": "feet",
        "yd": "yard",
        "mi": "dặm",

        # Khối lượng
        "kg/m3": "ki lô gam trên mét khối",
        "g/cm3": "gam trên xen ti mét khối",
        "t": "tấn",
        "kg": "ki lô gam",
        "g": "gam",
        "mg": "mi li gam",
        "lb": "pao",
        "oz": "ao xơ",

        # Dung tích
        "dl": "đề xi lít",
        "cl": "xen ti lít",
        "ml": "mi li lít",
        "l": "lít",

        # Thời gian
        "h": "giờ",
        "s": "giây",
        "ms": "mi li giây",
        "ns": "nano giây",

        # Dữ liệu
        "tb": "tê ra bai",
        "gb": "ghi ga bai",
        "mb": "mê ga bai",
        "kb": "ki lô bai",
        "mp": "mê ga pixel",
        "px": "pixel",

        # Điện - vật lý - kỹ thuật
        "kwh": "ki lô watt giờ",
        "kw": "ki lô watt",
        "w": "watt",

        "v": "vôn",
        "ma": "mi li ampe",
        "a": "ampe",

        "kΩ": "ki lô ôm",
        "ω": "ôm",

        "hz": "héc",
        "bps": "bít trên giây",

        "dpi": "đi pi ai",
        "gpa": "gi pi ê",
        "pa": "pát can",
        "nm": "niutơn mét",
        "n": "niutơn",

        "kcal": "ki lô ca lo",
        "cal": "ca lo",
        "kj": "ki lô jun",
        "j": "jun",

        # Tỷ lệ
        "%": "phần trăm",

        # Tiền tệ
        "vnđ": "việt nam đồng",
        "đ": "đồng",
        "$": "đô la",
        "€": "ơ rô",
        "£": "bảng anh",
        "¥": "yên nhật"
    }
    def read_number(n, hang_tram=False):
        n = int(n)

        unit_names = ["", "nghìn", "triệu", "tỷ"]

        # Số nhỏ hơn 20 đọc trực tiếp
        if n < 20 and not hang_tram:
            return number_words[n]

        # Số nhỏ hơn 100 xử lý theo dạng chục và đơn vị
        elif n < 100 and not hang_tram:
            chuc = (n // 10) * 10
            donvi = n % 10
            if donvi == 0:
                return number_words[chuc]
            if donvi == 1:
                return number_words[chuc] + " mốt"
            if donvi == 5:
                return number_words[chuc] + " lăm"
            if donvi == 4 and chuc > 1:
                return number_words[chuc] + " tư"
            return number_words[chuc] + " " + number_words[donvi]
                
        # Số nhỏ hơn 1000 xử lý theo dạng trăm
        elif n < 1000:
            tram = n // 100
            chuc_dv = n % 100
            res = number_words[tram] + " trăm"
            if chuc_dv == 0:
                return res
            elif chuc_dv < 10:
                if chuc_dv == 4:
                    return res + " linh tư"
                return res + " linh " + number_words[chuc_dv]
            return res + " " + read_number(chuc_dv)

        # Số lớn hơn 1000 xử lý theo nhóm nghìn, triệu, tỷ
        else:
            str_n = str(n)
            while len(str_n) % 3 != 0:
                str_n = '0' + str_n  # Thêm số 0 vào đầu nếu cần để chia thành các nhóm 3 chữ số
            groups = [str_n[i:i+3] for i in range(0, len(str_n), 3)]  # Chia thành các nhóm 3 chữ số
            parts = []
            # Đọc từng nhóm
            for i, group in enumerate(groups):
                val = int(group)
                if val == 0:
                    continue  # Bỏ qua nhóm 0 đầu tiên
                hang_tram = False if i == 0 else True
                words = read_number(val, hang_tram=hang_tram)  # Đọc nhóm số
                unit = unit_names[len(groups) - 1 - i]  # Đơn vị nghìn, triệu, tỷ
                if val == 0:
                    parts.append(words + " " + unit)  # Nếu là 0, không thêm "không"
                else:
                    parts.append(words + " " + unit)
            # Trả về kết quả ghép các nhóm
            return " ".join(parts).strip()

    def convert_units(match):
        raw_num = match.group(1)
        unit = match.group(2)
        unit_text = unit_mapping.get(unit, unit)
        return raw_num + " " + unit_text

    def convert_complex_number(match):
        num_str = match.group(0)

        # Xác định vị trí xuất hiện cuối cùng của , và .
        last_dot = num_str.rfind('.')
        last_comma = num_str.rfind(',')

        # Nếu cả 2 cùng xuất hiện
        if '.' in num_str and ',' in num_str:
            if last_dot > last_comma:
                sep_decimal = '.'
                sep_thousand = ','
            else:
                sep_decimal = ','
                sep_thousand = '.'
        else:
            # Không đủ thông tin để xác định, trả lại nguyên
            return num_str

        try:
            int_part, dec_part = num_str.rsplit(sep_decimal, 1)
            int_part_clean = int_part.replace(sep_thousand, "")
            int_text = read_number(int_part_clean)
            dec_text = " ".join([number_words[int(d)] for d in dec_part])
            return f"{int_text} phẩy {dec_text}"
        except Exception:
            return num_str

    def convert_large_grouped_number(match):
        num_str = match.group(1)

        # Tìm dấu tách và phần sau dấu
        if '.' in num_str:
            parts = num_str.split('.')
            sep = '.'
        elif ',' in num_str:
            parts = num_str.split(',')
            sep = ','
        else:
            parts = [num_str]
            sep = ''

        # Nếu có phần thập phân
        if len(parts) == 2:
            int_part, decimal_part = parts
            if len(decimal_part) == 3 and sep == '.':
                # là dấu ngăn cách hàng nghìn, bỏ dấu
                cleaned = num_str.replace(sep, "")
                return read_number(int(cleaned))
            else:
                # là số thập phân, đổi dấu thành " phẩy "
                return num_str.replace(sep, " phẩy ")
        else:
            # không có dấu, hoặc có nhiều dấu mà không rõ cấu trúc, xử lý như bình thường
            if len(num_str) < 6:
                num_str = num_str.replace(".", "").replace(",", " phẩy ")
                return num_str
            cleaned = num_str.replace(".", "").replace(",", "")
            return read_number(int(cleaned))

    def convert_decimal(match):
        full_match = match.group(0)
        int_part = match.group(1)
        dec_part = match.group(2)
        if '.' in full_match:
            separator_word = "chấm"
        else:
            separator_word = "phẩy"
        return read_number(int_part) + f" {separator_word} " + read_number(dec_part)
        # return read_number(int_part) + f" {separator_word} " + " ".join([number_words[int(d)] for d in dec_part])

    def convert_integer(match):
        return read_number(match.group(0))

    def convert_time_format(match):
        hour = int(match.group(1))
        minute = int(match.group(2))
        return f"{read_number(hour)} giờ {read_number(minute)} phút"

    def convert_fraction(match):
        tu_so = int(match.group(1))
        mau_so = int(match.group(2))
        return f"{read_number(tu_so)} trên {read_number(mau_so)}"
    
    def convert_number_with_unit_inside(match):
        num1 = int(match.group(1))
        unit = match.group(2)
        num2 = int(match.group(3))
        unit_text = unit_mapping.get(unit.lower(), unit)
        return f"{read_number(num1)} {unit_text} {read_number(num2)}"
    
    def convert_date_format(match):
        day = int(match.group(1))
        month = int(match.group(2))
        year = int(match.group(3))
        return f"{read_number(day)} tháng {read_number(month)} năm {read_number(year)}"
    
    units_pattern = "|".join(re.escape(k) for k in unit_mapping.keys())
    text = re.sub(r"\b(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{4})\b", convert_date_format, text)
    text = re.sub(r"\b(\d+)\/(\d+)\b", convert_fraction, text)  # phân số
    text = re.sub(r"\b(\d+)(m|cm|km|kg|g)(\d+)\b", convert_number_with_unit_inside, text)  # 1m65
    text = re.sub(r"\b(\d{1,2})(?:h|:)(\d{1,2})\b", convert_time_format, text)
    text = re.sub( rf"(\d{{1,3}}(?:[.,]\d{{3}})+|\d+)\s*({units_pattern})(?!\w)", convert_units, text )
    text = re.sub(r"\b\d{1,3}(?:[.,]\d{3})+[.,]\d+\b", convert_complex_number, text)
    text = re.sub(r"\b(\d{1,3}(?:[.,]\d{3})+)\b", convert_large_grouped_number, text)
    text = re.sub(r"\b(\d+)[.,](\d+)\b", convert_decimal, text)
    text = re.sub(r"\b\d+\b", convert_integer, text)

    return text




tttt = "1.234 - 1,234 - 2.75 - 35,55 - 24/56 - 1m75 - 24 - 14 - 114 - 154 - 1204 - 1234 - ngày 15-4-2025 - 250kg - 57g - 97.05km - 2345 - - 15mm - 300cm - 340.56 - 1000500000 - 2000000"
gg = number_to_vietnamese_with_units(tttt)
print(gg)
