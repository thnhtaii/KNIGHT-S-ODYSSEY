"""
Script to cut the new White Wolf sprite sheet into individual frames.
New sprite sheet: 1024 x 430 pixels, RGBA.
Layout:
  IDLE:   4 frames, y=[56,117], x in [14, 128], [128, 242], [278, 386], [398, 507]
  WALK:   4 frames, y=[56,117], x in [534, 647], [647, 760], [772, 879], [893, 999]
  RUN:    4 frames, y=[155,226], x in [21, 129], [140, 248], [263, 372], [383, 496]
  JUMP:   4 frames, y=[155,226], x in [496, 609], [651, 757], [769, 881], [881, 994]
  ATTACK: 4 frames, y=[250,330], x in [18, 127], [138, 254], [254, 371], [382, 495]
  HURT:   2 frames, y=[330,422], x in [14, 114], [114, 250]
  DIE:    3 frames, y=[330,422], x in [280, 386], [423, 590], [590, 778]
"""

from PIL import Image
import os
import numpy as np
import cv2

def remove_checkered_bg_clean(img, tol=22, min_size=50):
    """Remove the blue-gray checkered background of the new sprite sheet cleanly
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
    
    # Combine background masks (excluding white matching to preserve wolf's body)
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
    print(f"New Sprite sheet size: {w}x{h}")

    # Layout coordinates: (x1, y1, x2, y2, cell_start)
    animations = {
        'idle': [
            (14, 56, 128, 117, 0),
            (128, 56, 242, 117, 128),
            (278, 56, 386, 117, 256),
            (398, 56, 507, 117, 384)
        ],
        'walk': [
            (534, 56, 647, 117, 512),
            (647, 56, 760, 117, 640),
            (772, 56, 879, 117, 768),
            (893, 56, 999, 117, 896)
        ],
        'run': [
            (21, 155, 129, 226, 0),
            (140, 155, 248, 226, 128),
            (263, 155, 372, 226, 256),
            (383, 155, 496, 226, 384)
        ],
        'jump': [
            (496, 155, 609, 226, 512),
            (651, 155, 757, 226, 640),
            (769, 155, 881, 226, 768),
            (881, 155, 994, 226, 896)
        ],
        'attack': [
            (18, 250, 127, 330, 0),
            (138, 250, 254, 330, 128),
            (254, 250, 371, 330, 256),
            (382, 250, 495, 330, 384)
        ],
        'hurt': [
            (14, 352, 114, 411, 0),
            (114, 352, 250, 411, 128)
        ],
        'die': [
            (280, 352, 386, 411, 256),
            (423, 352, 590, 411, 384),
            (590, 352, 778, 411, 512)
        ]
    }
    
    # We will first clear existing pngs in these directories to avoid mixing old and new sprites
    for anim_name in animations.keys():
        anim_dir = os.path.join(output_base, anim_name)
        if os.path.exists(anim_dir):
            for file in os.listdir(anim_dir):
                if file.endswith('.png'):
                    os.remove(os.path.join(anim_dir, file))
        os.makedirs(anim_dir, exist_ok=True)
        
    for anim_name, frames in animations.items():
        out_dir = os.path.join(output_base, anim_name)
        
        for i, (x1, y1, x2, y2, cell_start) in enumerate(frames):
            frame = sheet.crop((x1, y1, x2, y2))
            frame_clean = remove_checkered_bg_clean(frame)
            
            # Pad to uniform canvas size (200x90) to eliminate jitter
            canvas = Image.new("RGBA", (200, 90), (0, 0, 0, 0))
            dx = x1 - cell_start
            w = x2 - x1
            h = y2 - y1
            
            # Center the cell horizontally in the canvas, align feet with bottom (y=90)
            paste_x = dx + (200 - 128) // 2
            paste_y = 90 - h
            
            canvas.paste(frame_clean, (paste_x, paste_y))
            
            filename = f"{anim_name.capitalize()}_{i}.png"
            canvas.save(os.path.join(out_dir, filename))
            print(f"  Saved {anim_name}/{filename} ({canvas.size[0]}x{canvas.size[1]})")

    print("\nDone cutting new sprites!")

if __name__ == "__main__":
    cut_sprites()
