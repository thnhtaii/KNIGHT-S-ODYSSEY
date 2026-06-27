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

def cut_sprites():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf', 'spritesheet.png')
    output_base = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf')

    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    print(f"New Sprite sheet size: {w}x{h}")

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
        
        for i, (x1, y1, x2, y2) in enumerate(frames):
            frame = sheet.crop((x1, y1, x2, y2))
            frame = remove_checkered_bg(frame)
            frame = trim_transparent(frame)
            
            filename = f"{anim_name.capitalize()}_{i}.png"
            frame.save(os.path.join(out_dir, filename))
            print(f"  Saved {anim_name}/{filename} ({frame.size[0]}x{frame.size[1]})")

    print("\nDone cutting new sprites!")


def remove_checkered_bg(img):
    """Remove the blue-gray checkered background of the new sprite sheet."""
    data = np.array(img)
    r = data[:,:,0].astype(int)
    g = data[:,:,1].astype(int)  
    b = data[:,:,2].astype(int)
    
    # Tolerance for checkerboard color matching
    tol = 18
    
    # Light checker: ~(146, 160, 171)
    light = (np.abs(r - 146) < tol) & (np.abs(g - 160) < tol) & (np.abs(b - 171) < tol)
    # Dark checker: ~(120, 136, 149)
    dark = (np.abs(r - 120) < tol) & (np.abs(g - 136) < tol) & (np.abs(b - 149) < tol)
    # Background top bar/border matching: (64, 82, 94)
    border = (np.abs(r - 64) < tol) & (np.abs(g - 82) < tol) & (np.abs(b - 94) < tol)
    # White / text matching
    white = (r > 220) & (g > 220) & (b > 220)
    
    # Combine background masks
    # Keep wolf pixels that might overlap white by checking if they are not surrounded by blue-gray
    bg_mask = light | dark | border | white
    
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
