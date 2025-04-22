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




tttt = "<1> - 12.5 - 250kg - 57g - 97.05km - 2345 - - 15mm - 300cm - 340.56 - 1000500000 - 2000000"
gg = number_to_vietnamese_with_units(tttt)
print(gg)
