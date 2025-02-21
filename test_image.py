from common_function import *
from PIL import Image
import tkinter as tk
from tkinter import Canvas, PhotoImage, Scrollbar

def merge_images_vertically(image_files, folder):
    output_path = os.path.join(folder, "merged_image.png")
    # Mở tất cả ảnh và tính toán kích thước của canvas
    image_paths = [os.path.join(folder, img) for img in image_files] or []
    if len(image_paths) == 0:
        print(f"Không tìm thấy ảnh trong thư mục {folder}")
        return
    images = [Image.open(img_path) for img_path in image_paths]
    max_width = max(img.width for img in images)
    total_height = sum(img.height for img in images)

    # Tạo một canvas mới
    merged_image = Image.new("RGB", (max_width, total_height))

    # Vẽ từng ảnh lên canvas
    y_offset = 0
    for img in images:
        merged_image.paste(img, (0, y_offset))
        y_offset += img.height

    # Lưu ảnh kết quả
    merged_image.save(output_path)
    return output_path

def show_image_with_scrollbar(image_path):
    root = tk.Tk()
    root.title("Ảnh nối với thanh cuộn")

    # Tạo canvas và thanh cuộn
    canvas = Canvas(root)
    scrollbar = Scrollbar(root, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    # Đặt thanh cuộn và canvas
    scrollbar.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Mở ảnh
    img = PhotoImage(file=image_path)
    canvas.create_image(0, 0, anchor="nw", image=img)
    canvas.config(scrollregion=canvas.bbox("all"))

    root.mainloop()

folder = "D:\\download\\Truyen\\ta bi ket trong 1 ngay 1000 nam\\chuong 1"
# Danh sách các ảnh cần nối
images = get_file_in_folder_by_type(folder, '.jpg')


# Nối ảnh và hiển thị với thanh cuộn
merged_image_path = merge_images_vertically(images, folder)
# show_image_with_scrollbar(merged_image_path)
