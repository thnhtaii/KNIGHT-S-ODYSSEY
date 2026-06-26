"""
Script to cut Ice Wolf sprite sheet into individual frames.
Sprite sheet: 1024 x 885 pixels
Detected layout:
  IDLE:   4 frames, y=[28,164]
  WALK:   5 frames, y=[168,297] (not 4!)
  RUN:    6 frames, y=[300,429] (not 4!)
  ATTACK: 5 frames, y=[435,557]
  JUMP:   3 frames, y=[560,689] (left portion)
  HURT:   2 frames, y=[560,689] (right portion)
  DIE:    5 frames, y=[775,860] (lower sub-row)
"""

from PIL import Image
import os
import numpy as np

def cut_sprites():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sheet_path = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf', 'spritesheet.jpg')
    output_base = os.path.join(script_dir, 'assets', 'sprites', 'ice_wolf')

    sheet = Image.open(sheet_path).convert("RGBA")
    w, h = sheet.size
    print(f"Sprite sheet size: {w}x{h}")

    # Precise frame positions measured from pixel analysis
    # Format: anim_name -> list of (x1, y1, x2, y2) bounding boxes with padding
    PAD = 8  # Padding around detected sprites
    
    animations = {
        'idle': [
            (21-PAD, 28-PAD, 153+PAD, 164+PAD),
            (163-PAD, 28-PAD, 317+PAD, 164+PAD),
            (328-PAD, 28-PAD, 454+PAD, 164+PAD),
            (467-PAD, 28-PAD, 613+PAD, 164+PAD),
        ],
        'walk': [
            (21-PAD, 168-PAD, 167+PAD, 297+PAD),
            (186-PAD, 168-PAD, 335+PAD, 297+PAD),
            (348-PAD, 168-PAD, 497+PAD, 297+PAD),
            (511-PAD, 168-PAD, 654+PAD, 297+PAD),
            (670-PAD, 168-PAD, 814+PAD, 297+PAD),
        ],
        'run': [
            (21-PAD, 300-PAD, 168+PAD, 429+PAD),
            (186-PAD, 300-PAD, 337+PAD, 429+PAD),
            (354-PAD, 300-PAD, 504+PAD, 429+PAD),
            (521-PAD, 300-PAD, 670+PAD, 429+PAD),
            (687-PAD, 300-PAD, 836+PAD, 429+PAD),
            (856-PAD, 300-PAD, 1007+PAD, 429+PAD),
        ],
        'attack': [
            (20-PAD, 435-PAD, 177+PAD, 557+PAD),
            (208-PAD, 435-PAD, 408+PAD, 557+PAD),
            (423-PAD, 435-PAD, 563+PAD, 557+PAD),
            (576-PAD, 435-PAD, 731+PAD, 557+PAD),
            (761-PAD, 435-PAD, 858+PAD, 557+PAD),
        ],
        'jump': [
            (30-PAD, 560-PAD, 164+PAD, 689+PAD),
            (184-PAD, 560-PAD, 365+PAD, 689+PAD),
            (387-PAD, 560-PAD, 498+PAD, 689+PAD),
        ],
        'hurt': [
            (598-PAD, 560-PAD, 762+PAD, 689+PAD),
            (782-PAD, 560-PAD, 885+PAD, 689+PAD),
        ],
        'die': [
            # Die sprites are in lower portion, y ~ 775-860
            (20-PAD, 770-PAD, 190+PAD, 860+PAD),
            (214-PAD, 770-PAD, 385+PAD, 860+PAD),
            (409-PAD, 770-PAD, 575+PAD, 860+PAD),
            (575-PAD, 770-PAD, 735+PAD, 860+PAD),
            # Skip portrait frame (852+, bottom right)
        ],
    }
    
    for anim_name, frames in animations.items():
        out_dir = os.path.join(output_base, anim_name)
        os.makedirs(out_dir, exist_ok=True)
        
        for i, (x1, y1, x2, y2) in enumerate(frames):
            # Clamp to image bounds
            x1 = max(0, x1)
            y1 = max(0, y1)
            x2 = min(w, x2)
            y2 = min(h, y2)
            
            frame = sheet.crop((x1, y1, x2, y2))
            frame = remove_checkered_bg(frame)
            frame = trim_transparent(frame)
            
            if frame.size[0] < 15 or frame.size[1] < 15:
                print(f"  WARNING: {anim_name}/{i} too small ({frame.size}), using untrimmed")
                frame = sheet.crop((x1, y1, x2, y2))
                frame = remove_checkered_bg(frame)
            
            filename = f"{anim_name.capitalize()}_{i}.png"
            frame.save(os.path.join(out_dir, filename))
            print(f"  Saved {anim_name}/{filename} ({frame.size[0]}x{frame.size[1]})")

    # Clean up debug files
    debug_path = os.path.join(output_base, 'die_row_debug.png')
    if os.path.exists(debug_path):
        os.remove(debug_path)
    
    print("\nDone cutting sprites!")


def remove_checkered_bg(img):
    """Remove the blue-gray checkered background."""
    data = np.array(img)
    r = data[:,:,0].astype(int)
    g = data[:,:,1].astype(int)  
    b = data[:,:,2].astype(int)
    
    tol = 28
    
    # Light checker: ~(148, 164, 179)
    light = (np.abs(r - 148) < tol) & (np.abs(g - 164) < tol) & (np.abs(b - 179) < tol)
    # Dark checker: ~(124, 140, 155)
    dark = (np.abs(r - 124) < tol) & (np.abs(g - 140) < tol) & (np.abs(b - 155) < tol)
    # White
    white = (r > 230) & (g > 230) & (b > 230)
    
    bg_mask = light | dark | white
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
