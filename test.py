
from common_function import *

def add_image_into_video(clip, top_image_path=None, bot_image_path=None, top_height=0, bot_height=0, watermask = None):
    # Lấy kích thước của video
    width, height = clip.size

    # Tạo ImageClip cho hình ảnh trên
    if top_image_path:
        top_image = (ImageClip(top_image_path)
                    .resize(width=width, height=top_height)  # Đảm bảo chiều rộng của hình ảnh bằng chiều rộng video
                    .set_position(('center', 'top'))
                    .set_duration(clip.duration))
    else:
        top_image = (ColorClip(size=(width, top_height), color=(0, 0, 0))
           .set_position(('center', 'top'))
           .set_duration(clip.duration))

    # Tạo ImageClip cho hình ảnh dưới
    if bot_image_path:
        bottom_image = (ImageClip(bot_image_path)
                        .resize(width=width, height=bot_height)  # Đảm bảo chiều rộng của hình ảnh bằng chiều rộng video
                        .set_position(('center', 'bottom'))
                        .set_duration(clip.duration))
    else:
        bottom_image = (ColorClip(size=(width, bot_height), color=(0, 0, 0))
                    .set_position(('center', 'bottom'))
                    .set_duration(clip.duration))
    if watermask:
        watermask_image = (ImageClip(watermask).set_position(('center', 'center')).set_duration(clip.duration))
        final_clip = CompositeVideoClip([clip, top_image, bottom_image, watermask_image])
    else:
        final_clip = CompositeVideoClip([clip, top_image, bottom_image])
    return final_clip


    final_clip.write_videofile(f"{output_folder}\\fff.mp4", codec='libx264', fps=24)


video_path = f"{test_folder}\\a4.mp4"
top_imange = f"{test_folder}\\a1.png"
bot_imange = f"{test_folder}\\a2.png"
water_path = f"{test_folder}\\a3.png"
clip = VideoFileClip(video_path)
add_image_into_video(clip, top_imange, bot_imange, 1, 450, )



        

        # Part <index> - Funny Animals - Unforgettable Funny Moments







