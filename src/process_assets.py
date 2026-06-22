import os
import sys
from PIL import Image

def is_bright_neutral(pixel):
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a == 0:
            return True
    else:
        r, g, b = pixel
    
    # Bất cứ pixel nào gần xám và có độ sáng cao (> 180) thì được coi là checkerboard
    if abs(r - g) <= 15 and abs(g - b) <= 15 and abs(r - b) <= 15:
        if r > 180 and g > 180 and b > 180:
            return True
    return False

def remove_background_and_crop(input_path, output_path):
    img = Image.open(input_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()

    # Thuật toán Loang (Flood Fill) để xóa nền checkerboard
    # Điểm bắt đầu loang: tất cả các pixel nằm trên 4 đường biên của ảnh
    queue = []
    visited = set()

    for x in range(width):
        for y in [0, height - 1]:
            if is_bright_neutral(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))
    for y in range(height):
        for x in [0, width - 1]:
            if (x, y) not in visited and is_bright_neutral(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))

    # Thực hiện loang
    while queue:
        cx, cy = queue.pop(0)
        pixels[cx, cy] = (0, 0, 0, 0)  # Gán độ trong suốt hoàn toàn

        # Duyệt 4 hướng lân cận
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and is_bright_neutral(pixels[nx, ny]):
                    queue.append((nx, ny))
                    visited.add((nx, ny))

    # Tìm Bounding Box của các phần không trong suốt để tự động CROP bỏ rìa thừa
    min_x, min_y = width, height
    max_x, max_y = -1, -1

    for x in range(width):
        for y in range(height):
            _, _, _, a = pixels[x, y]
            if a > 0:
                if x < min_x: min_x = x
                if x > max_x: max_x = x
                if y < min_y: min_y = y
                if y > max_y: max_y = y

    if max_x >= min_x and max_y >= min_y:
        # Thực hiện crop theo bounding box
        cropped_img = img.crop((min_x, min_y, max_x + 1, max_y + 1))
        cropped_img.save(output_path, "PNG")
        print(f"[SUCCESS] Đã xử lý và lưu: {output_path} (Kích thước gốc: {img.size} -> Kích thước mới: {cropped_img.size})")
    else:
        # Nếu không tìm thấy pixel nào có màu (ảnh trống), lưu ảnh gốc đã xóa nền
        img.save(output_path, "PNG")
        print(f"[WARNING] Không tìm thấy phần tử hiển thị, lưu ảnh gốc đã xóa nền: {output_path}")

if __name__ == '__main__':
    brain_dir = r"C:\Users\dotai\.gemini\antigravity\brain\66c119e7-a14b-4ce9-9896-79e547a809b7"
    dest_dir = r"d:\ky 2 nam 2\AI_cuoiky\Stickyman-Battle\assets\backgrounds"
    
    # Xử lý platform
    plat_src = os.path.join(brain_dir, "media__1782111767533.png")
    plat_dest = os.path.join(dest_dir, "custom_platform.png")
    remove_background_and_crop(plat_src, plat_dest)
    
    # Xử lý ground
    gnd_src = os.path.join(brain_dir, "media__1782111741626.png")
    gnd_dest = os.path.join(dest_dir, "custom_ground.png")
    remove_background_and_crop(gnd_src, gnd_dest)
