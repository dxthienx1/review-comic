from common_function import *


def split_text_into_chunks(text, max_length=250):
    chunks = []
    while len(text) > max_length:
        mid_point = max_length // 2
        before_mid = text[:max_length]

        # Tìm dấu "," gần nhất với mid_point
        split_point = before_mid.rfind(",", 0, mid_point + (max_length // 4))
        if split_point == -1:
            split_point = before_mid.rfind(" ", 0, mid_point + (max_length // 4))
            if split_point == -1:
                split_point = max_length  # Chia tại max_length

        first_text = text[:split_point].strip()
        chunks.append(f'{first_text}.')
        text = text[split_point + 1:].strip()

    if text:
        chunks.append(f'{text}')
    
    return chunks

text = "duyên sinh thiên tàn la lại lần nữa được phóng ra, ngay tức khắc màn hắc vụ nồng đậm lại lần nữa phóng ra lan tỏa trong không gian xung quanh lão, lão muốn giết chết diệp mặc trong thời gian ngắn nhất, nếu không đem dài lắm mộng, nhưng khi màn hắc vụ nồng đậm đó còn chưa hình thành thần thông, ánh mắt lại lần nữa ngưng tụ lại, lão nhìn thấy mũi tên thứ hai, mũi tên thứ ba, thứ tư thậm chí là mũi thứ năm đồng thời bắn ra."
fff = split_text_into_chunks(text)
print(fff)