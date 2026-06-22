import os
from PIL import Image

def is_near_white(pixel):
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a == 0:
            return True
    else:
        r, g, b = pixel
    
    # Định nghĩa màu trắng/gần trắng (RGB đều lớn hơn 235)
    return r > 235 and g > 235 and b > 235

def process_portal():
    brain_dir = r"C:\Users\dotai\.gemini\antigravity\brain\66c119e7-a14b-4ce9-9896-79e547a809b7"
    src_path = os.path.join(brain_dir, "media__1782114436643.jpg")
    dest_path = r"d:\ky 2 nam 2\AI_cuoiky\Stickyman-Battle\assets\backgrounds\BGDoor.png"
    
    img = Image.open(src_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    # 1. Xóa phần đảo đất bên dưới bằng cách đặt mọi pixel từ y >= 695 thành trong suốt
    for y in range(695, height):
        for x in range(width):
            pixels[x, y] = (0, 0, 0, 0)
            
    # 2. Loang từ 4 góc để xóa màu nền trắng
    queue = []
    visited = set()
    
    for x in range(width):
        for y in [0, height - 1]:
            if is_near_white(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))
    for y in range(height):
        for x in [0, width - 1]:
            if (x, y) not in visited and is_near_white(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))
                
    while queue:
        cx, cy = queue.pop(0)
        pixels[cx, cy] = (0, 0, 0, 0)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and is_near_white(pixels[nx, ny]):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    
    # 3. Tìm bounding box để crop phần chứa portal
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
        cropped_img = img.crop((min_x, min_y, max_x + 1, max_y + 1))
        # Lưu đè lên file BGDoor.png
        cropped_img.save(dest_path, "PNG")
        print(f"[SUCCESS] Đã xử lý portal: {dest_path} (Cỡ cũ: {img.size} -> Cỡ mới sau crop: {cropped_img.size})")
    else:
        img.save(dest_path, "PNG")
        print(f"[WARNING] Không crop được, lưu ảnh gốc đã xóa nền: {dest_path}")

if __name__ == '__main__':
    process_portal()
