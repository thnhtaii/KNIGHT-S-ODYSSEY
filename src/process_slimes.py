import os
from PIL import Image

def is_near_white(pixel):
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a == 0:
            return True
    else:
        r, g, b = pixel
    return r > 235 and g > 235 and b > 235

def is_bright_neutral(pixel):
    if len(pixel) == 4:
        r, g, b, a = pixel
        if a == 0:
            return True
    else:
        r, g, b = pixel
    # Checkerboard check
    if abs(r - g) <= 15 and abs(g - b) <= 15 and abs(r - b) <= 15:
        if r > 180 and g > 180 and b > 180:
            return True
    return False

def remove_background_and_crop(src_path, dest_path, check_func):
    img = Image.open(src_path).convert("RGBA")
    width, height = img.size
    pixels = img.load()
    
    queue = []
    visited = set()
    
    # Add border pixels to queue
    for x in range(width):
        for y in [0, height - 1]:
            if check_func(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))
    for y in range(height):
        for x in [0, width - 1]:
            if (x, y) not in visited and check_func(pixels[x, y]):
                queue.append((x, y))
                visited.add((x, y))
                
    while queue:
        cx, cy = queue.pop(0)
        pixels[cx, cy] = (0, 0, 0, 0)
        
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = cx + dx, cy + dy
            if 0 <= nx < width and 0 <= ny < height:
                if (nx, ny) not in visited and check_func(pixels[nx, ny]):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    
    # Find bounding box
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
        cropped_img.save(dest_path, "PNG")
        print(f"[SUCCESS] Saved: {dest_path} (Old: {img.size} -> New: {cropped_img.size})")
    else:
        img.save(dest_path, "PNG")
        print(f"[WARNING] BBox not found, saved default: {dest_path}")

def main():
    brain_dir = r"C:\Users\dotai\.gemini\antigravity\brain\66c119e7-a14b-4ce9-9896-79e547a809b7"
    dest_dir = r"d:\ky 2 nam 2\AI_cuoiky\Stickyman-Battle\assets\sprites\slime"
    os.makedirs(dest_dir, exist_ok=True)
    
    # 1. Pink holographic slime (white background)
    slime1_src = os.path.join(brain_dir, "media__1782115311302.jpg")
    slime1_dest = os.path.join(dest_dir, "custom_slime1.png")
    remove_background_and_crop(slime1_src, slime1_dest, is_near_white)
    
    # 2. Blue space slime (checkerboard background)
    slime2_src = os.path.join(brain_dir, "media__1782115466537.png")
    slime2_dest = os.path.join(dest_dir, "custom_slime2.png")
    remove_background_and_crop(slime2_src, slime2_dest, is_bright_neutral)

if __name__ == '__main__':
    main()
