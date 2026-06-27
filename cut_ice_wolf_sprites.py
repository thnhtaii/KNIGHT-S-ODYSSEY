"""
Script to cut Ice Wolf sprite sheet into individual frames.
Sprite sheet: 1024 x 885 pixels (JPG format with checkered background)

Uses flood-fill from edges to remove background while preserving the wolf body.
Crop regions are carefully adjusted to exclude text labels.
"""

from PIL import Image, ImageFilter
import os
import numpy as np
from collections import deque


def cut_sprites():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf', 'spritesheet.jpg')
    output_base = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf')

    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    print(f"Sprite sheet size: {w}x{h}")

    # Adjusted bounding boxes - exclude text labels at top of each row
    # Text labels ("ICE WOLF HERO", "IDLE", "RUN", etc.) occupy roughly first 28 rows
    # of each section. Wolf bodies start below the text.
    animations = {
        'idle': [
            # Row y=28-164, wolves start around y=30
            (21, 30, 153, 164),
            (163, 30, 317, 164),
            (328, 30, 454, 164),
            (467, 30, 613, 164),
        ],
        'walk': [
            # Row y=168-297, text "WALK" at top
            (21, 180, 167, 297),
            (186, 180, 335, 297),
            (348, 180, 497, 297),
            (511, 180, 654, 297),
            (670, 180, 814, 297),
        ],
        'run': [
            # Row y=300-429, text "RUN" at top
            (21, 312, 168, 429),
            (186, 312, 337, 429),
            (354, 312, 504, 429),
            (521, 312, 670, 429),
            (687, 312, 836, 429),
            (856, 312, 1007, 429),
        ],
        'attack': [
            # Row y=435-557, text "ATTACK" at top
            (20, 447, 177, 557),
            (208, 447, 408, 557),
            (423, 447, 563, 557),
            (576, 447, 731, 557),
            (761, 447, 858, 557),
        ],
        'jump': [
            # Row y=560-689, text "JUMP" at top
            (30, 572, 164, 689),
            (184, 572, 365, 689),
            (387, 572, 498, 689),
        ],
        'hurt': [
            # Same row as jump, right portion, text "HURT" at top
            (598, 572, 762, 689),
            (782, 572, 885, 689),
        ],
        'die': [
            # Row y=770-860, text "DIE" at top (only 3 frames)
            (20, 782, 200, 860),
            (210, 782, 395, 860),
            (405, 782, 600, 860),
        ],
    }

    for anim_name, frames in animations.items():
        out_dir = os.path.join(output_base, anim_name)
        os.makedirs(out_dir, exist_ok=True)

        for i, (x1, y1, x2, y2) in enumerate(frames):
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)

            frame = sheet.crop((x1, y1, x2, y2))
            frame = remove_checkered_bg_floodfill(frame)
            frame = trim_transparent(frame)

            if frame.size[0] < 15 or frame.size[1] < 15:
                print(f"  WARNING: {anim_name}/{i} too small ({frame.size}), using untrimmed")
                frame = sheet.crop((x1, y1, x2, y2))
                frame = remove_checkered_bg_floodfill(frame)

            filename = f"{anim_name.capitalize()}_{i}.png"
            frame.save(os.path.join(out_dir, filename))
            print(f"  Saved {anim_name}/{filename} ({frame.size[0]}x{frame.size[1]})")

    print("\nDone cutting sprites!")


def remove_checkered_bg_floodfill(img):
    """Remove the checkered background using flood-fill from edges.
    
    The checkered BG has two alternating colors that are very close to the 
    ice wolf's body color. Instead of color-matching everything, we flood-fill 
    from the image edges to only remove connected background regions.
    """
    data = np.array(img)
    h, w = data.shape[:2]
    
    r = data[:,:,0].astype(float)
    g = data[:,:,1].astype(float)
    b = data[:,:,2].astype(float)
    
    # Background checker colors (JPG-compressed, blurred):
    # Light: ~(126-150, 141-165, 157-180)
    # Dark:  ~(118-130, 136-145, 150-160)
    tol = 18
    
    # Checker color 1 (lighter)
    c1 = (np.abs(r - 140) < tol+5) & (np.abs(g - 156) < tol+5) & (np.abs(b - 172) < tol+5)
    # Checker color 2 (darker)
    c2 = (np.abs(r - 123) < tol) & (np.abs(g - 141) < tol) & (np.abs(b - 156) < tol)
    # Wider mid-range (general checker area)
    mid = (r > 110) & (r < 155) & (g > 130) & (g < 170) & (b > 145) & (b < 185)
    # Check blue-gray ratio typical of checker
    bg_ratio = (np.abs(g - r - 16) < 10) & (np.abs(b - g - 16) < 10)
    checker = mid & bg_ratio
    
    # White (remaining text or bright spots)
    white = (r > 200) & (g > 200) & (b > 200)
    # Near-black (text)
    black = (r < 40) & (g < 40) & (b < 40)
    
    could_be_bg = c1 | c2 | checker | white | black
    
    # Flood-fill from edges
    visited = np.zeros((h, w), dtype=bool)
    bg_mask = np.zeros((h, w), dtype=bool)
    queue = deque()
    
    # Seed from all edge pixels that match background
    for x in range(w):
        for y_edge in [0, h-1]:
            if could_be_bg[y_edge, x] and not visited[y_edge, x]:
                queue.append((y_edge, x))
                visited[y_edge, x] = True
    for y in range(h):
        for x_edge in [0, w-1]:
            if could_be_bg[y, x_edge] and not visited[y, x_edge]:
                queue.append((y, x_edge))
                visited[y, x_edge] = True
    
    # BFS flood fill with 8-connectivity
    while queue:
        cy, cx = queue.popleft()
        bg_mask[cy, cx] = True
        
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dy == 0 and dx == 0:
                    continue
                ny, nx = cy + dy, cx + dx
                if 0 <= ny < h and 0 <= nx < w and not visited[ny, nx] and could_be_bg[ny, nx]:
                    visited[ny, nx] = True
                    queue.append((ny, nx))
    
    # Set background to transparent
    data[bg_mask, 3] = 0
    
    return Image.fromarray(data)


def trim_transparent(img):
    """Trim transparent borders."""
    bbox = img.getbbox()
    if bbox:
        return img.crop(bbox)
    return img


if __name__ == "__main__":
    cut_sprites()
