from PIL import Image
import os

# Đường dẫn đến thư mục chứa sprite sheet
sprite_dir = "assets/sprites/slime/jump"

# Số khung hình trong sprite sheet Jump Land
frame_count = 6

# Kích thước mỗi khung hình
sprite_width = 96
sprite_height = 32

# Đường dẫn tới file sprite sheet
sprite_path = os.path.join(sprite_dir, "Sprite Sheet - Blue Jump Land.png")

if not os.path.exists(sprite_path):
    print(f"File not found: {sprite_path}")
else:
    img = Image.open(sprite_path)
    for i in range(frame_count):
        box = (i * sprite_width, 0, (i + 1) * sprite_width, sprite_height)
        sprite = img.crop(box)
        output_path = os.path.join(sprite_dir, f"Jump_Land_{i}.png")
        sprite.save(output_path)
        print(f"Saved: {output_path}")
