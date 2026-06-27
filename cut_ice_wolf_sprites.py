"""
Script to cut the White Wolf sprite sheet into individual frames.
Uses bounding-box centering and relative vertical alignment to guarantee
perfect, jitter-free animations.
"""

from PIL import Image
import os
import numpy as np
import cv2

def remove_checkered_bg_clean(img, tol=22, min_size=50):
    """Remove the blue-gray checkered background of the sprite sheet cleanly
    using color thresholding and connected components analysis to eliminate noise."""
    data = np.array(img)
    r = data[:,:,0].astype(int)
    g = data[:,:,1].astype(int)  
    b = data[:,:,2].astype(int)
    
    # Light checker: ~(146, 160, 171)
    light = (np.abs(r - 146) < tol) & (np.abs(g - 160) < tol) & (np.abs(b - 171) < tol)
    # Dark checker: ~(120, 136, 149)
    dark = (np.abs(r - 120) < tol) & (np.abs(g - 136) < tol) & (np.abs(b - 149) < tol)
    # Background top bar/border matching: (64, 82, 94)
    border = (np.abs(r - 64) < tol) & (np.abs(g - 82) < tol) & (np.abs(b - 94) < tol)
    
    # Combine background masks
    bg_mask = light | dark | border
    data[bg_mask, 3] = 0
    
    # Use connected components to clean up isolated noise pixels in background
    alpha = data[:, :, 3]
    binary_mask = (alpha > 0).astype(np.uint8)
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_mask)
    for i in range(1, num_labels):
        area = stats[i, cv2.CC_STAT_AREA]
        if area < min_size:
            data[labels == i, 3] = 0
            
    return Image.fromarray(data)

def cut_sprites():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf', 'spritesheet.png')
    output_base = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf')

    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    print(f"Sprite sheet size: {w}x{h}")

    # Layout coordinates: (x1, y1, x2, y2)
    animations = {
        'idle': [
            (14, 56, 128, 117),
            (128, 56, 242, 117),
            (278, 56, 386, 117),
            (398, 56, 507, 117)
        ],
        'walk': [
            (534, 56, 647, 117),
            (647, 56, 760, 117),
            (772, 56, 879, 117),
            (893, 56, 999, 117)
        ],
        'run': [
            (21, 155, 129, 226),
            (140, 155, 248, 226),
            (263, 155, 372, 226),
            (383, 155, 496, 226)
        ],
        'jump': [
            (496, 155, 609, 226),
            (651, 155, 757, 226),
            (769, 155, 881, 226),
            (881, 155, 994, 226)
        ],
        'attack': [
            (18, 250, 127, 330),
            (138, 250, 254, 330),
            (254, 250, 371, 330),
            (382, 250, 495, 330)
        ],
        'hurt': [
            (14, 352, 114, 411),
            (114, 352, 250, 411)
        ],
        'die': [
            (280, 352, 386, 411),
            (423, 352, 590, 411),
            (590, 352, 778, 411)
        ]
    }
    
    # Clear existing pngs in directories
    for anim_name in animations.keys():
        anim_dir = os.path.join(output_base, anim_name)
        if os.path.exists(anim_dir):
            for file in os.listdir(anim_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(anim_dir, file))
        os.makedirs(anim_dir, exist_ok=True)
        
    for anim_name, frames in animations.items():
        out_dir = os.path.join(output_base, anim_name)
        
        for i, (x1, y1, x2, y2) in enumerate(frames):
            frame = sheet.crop((x1, y1, x2, y2))
            frame_clean = remove_checkered_bg_clean(frame)
            bbox = frame_clean.getbbox()
            
            canvas = Image.new("RGBA", (200, 90), (0, 0, 0, 0))
            if bbox:
                left, top, right, bottom = bbox
                w = right - left
                h = bottom - top
                trimmed = frame_clean.crop(bbox)
                
                # Center the wolf body horizontally
                paste_x = 100 - w // 2
                # Align vertically relative to the ground floor of the crop box (y2)
                paste_y = 90 - (y2 - y1) + top
                
                canvas.paste(trimmed, (paste_x, paste_y))
            
            filename = f"{anim_name.capitalize()}_{i}.png"
            canvas.save(os.path.join(out_dir, filename))
            print(f"  Saved {anim_name}/{filename} ({canvas.size[0]}x{canvas.size[1]})")

    print("\nDone cutting new sprites with perfect alignment!")

if __name__ == "__main__":
    cut_sprites()
