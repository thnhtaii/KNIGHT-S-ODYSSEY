"""
Preview level5.tmj as a colored PNG using only tkinter + built-in modules.
Saves preview_level5.png in the levels/ directory then opens it.
"""
import json, os, tkinter as tk
from tkinter import Canvas

# ── Load map data ──────────────────────────────────────────────
with open("level5.tmj", encoding="utf-8") as f:
    tmj = json.load(f)

COLS   = tmj["width"]   # 50
ROWS   = tmj["height"]  # 38
T_WALL = 54

# Terrain grid
terrain_flat = next(l["data"] for l in tmj["layers"] if l["name"] == "map")
terrain = [[terrain_flat[r * COLS + c] for c in range(COLS)] for r in range(ROWS)]

# Object positions
objects = next(l["objects"] for l in tmj["layers"] if l["name"] == "objLV5")
ladders_layer = next(l["objects"] for l in tmj["layers"] if l["name"] == "ladder")

TILE  = 16  # source tile size
SCALE = 14  # pixels per tile in preview

# ── Colour palette ─────────────────────────────────────────────
C_WALL   = "#3a3a4a"   # dark blue-grey wall
C_AIR    = "#d4b896"   # warm tan / stone floor
C_LADDER = "#8B5E3C"   # brown ladder strip
C_L2SLOW = "#e8d88a"   # yellow slow zone
C_PLAYER = "#4fc3f7"   # cyan knight
C_DRAGON = "#ef5350"   # red dragon
C_EXIT   = "#ffd700"   # gold exit
C_GRID   = "#00000022" # very faint grid

W = COLS * SCALE
H = ROWS * SCALE

# ── Build canvas with tkinter ───────────────────────────────────
root = tk.Tk()
root.title("Level 5 Map Preview  (800x608  |  50x38 tiles)")
root.resizable(False, False)

cv = Canvas(root, width=W, height=H, bg=C_AIR, highlightthickness=0)
cv.pack()

# 1. Draw tiles
for r in range(ROWS):
    for c in range(COLS):
        x1, y1 = c * SCALE, r * SCALE
        x2, y2 = x1 + SCALE, y1 + SCALE
        if terrain[r][c] == T_WALL:
            color = C_WALL
        elif terrain[r][c] == 30:   # Slow zone tile
            color = C_L2SLOW
        else:
            color = C_AIR
        cv.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

# 2. Draw ladder holes (dark brown strips)
for lad in ladders_layer:
    x1 = int(lad["x"]      / TILE * SCALE)
    y1 = int(lad["y"]      / TILE * SCALE)
    x2 = int((lad["x"] + lad["width"])  / TILE * SCALE)
    y2 = int((lad["y"] + lad["height"]) / TILE * SCALE)
    cv.create_rectangle(x1, y1, x2, y2, fill=C_LADDER, outline="")
    # Ladder rungs
    rung_y = y1 + SCALE
    while rung_y < y2:
        cv.create_line(x1, rung_y, x2, rung_y, fill="#5d3a1a", width=1)
        rung_y += SCALE

# 3. Faint grid lines
for r in range(ROWS + 1):
    cv.create_line(0, r * SCALE, W, r * SCALE, fill="#aaaaaa", width=1)
for c in range(COLS + 1):
    cv.create_line(c * SCALE, 0, c * SCALE, H, fill="#aaaaaa", width=1)

# 4. Draw spawn objects
for obj in objects:
    cx = int((obj["x"] + obj["width"]  / 2) / TILE * SCALE)
    cy = int((obj["y"] + obj["height"] / 2) / TILE * SCALE)
    name = obj["name"]

    if name == "knight":
        r_px = SCALE
        cv.create_oval(cx-r_px, cy-r_px, cx+r_px, cy+r_px,
                       fill=C_PLAYER, outline="white", width=2)
        cv.create_text(cx, cy, text="P", fill="white",
                       font=("Arial", 8, "bold"))
    elif name == "dragon":
        r_px = SCALE
        cv.create_oval(cx-r_px, cy-r_px, cx+r_px, cy+r_px,
                       fill=C_DRAGON, outline="#b71c1c", width=2)
        cv.create_text(cx, cy, text="D", fill="white",
                       font=("Arial", 8, "bold"))
    elif name == "BGDoor":
        r_px = SCALE
        cv.create_rectangle(cx-r_px, cy-r_px*2, cx+r_px, cy+r_px,
                            fill=C_EXIT, outline="#b8860b", width=2)
        cv.create_text(cx, cy - SCALE//2, text="EXIT", fill="#4a3000",
                       font=("Arial", 7, "bold"))

# 5. Section labels (tiny)
labels = [
    # L4
    ( 6,  6, "L4A"), (18,  6, "L4B"), (30,  6, "L4C"), (42,  6, "L4D"),
    # L3
    ( 8, 11, "L3A"), (24, 11, "L3B"), (40, 11, "L3C"),
    # L2
    (11, 18, "L2A\n(slow)"), (36, 18, "L2B"),
    # L1
    ( 8, 27, "L1A\nSTART"), (24, 27, "L1B"), (40, 27, "L1C"),
]
for (tc, tr, label) in labels:
    cv.create_text(tc * SCALE, tr * SCALE, text=label, fill="#333",
                   font=("Arial", 7), anchor="center")

# 6. Legend
leg_x, leg_y = 4, H - 30
items = [
    (C_WALL,   "Wall"),
    (C_AIR,    "Walkable"),
    (C_L2SLOW, "Slow Zone"),
    (C_LADDER, "Ladder"),
    (C_PLAYER, "Player"),
    (C_DRAGON, "Dragon"),
    (C_EXIT,   "EXIT"),
]
for i, (col, lbl) in enumerate(items):
    x = leg_x + i * 78
    cv.create_rectangle(x, leg_y, x+12, leg_y+12, fill=col, outline="black")
    cv.create_text(x+16, leg_y+6, text=lbl, anchor="w",
                   font=("Arial", 8), fill="black")

# 7. Save as PNG via tkinter PostScript → convert
# (tkinter can't save PNG natively, so we use postscript then convert to PNG)
# If we can't convert, just show the window.
root.update()

# Try to save PNG using tkinter's postscript + ghostscript, or just show
try:
    import subprocess
    ps_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview_level5.ps")
    png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "preview_level5.png")
    cv.postscript(file=ps_path, colormode="color")
    # Try ghostscript
    gs_cmds = ["gswin64c", "gswin32c", "gs"]
    for gs in gs_cmds:
        try:
            subprocess.run(
                [gs, "-dBATCH", "-dNOPAUSE", "-sDEVICE=png16m",
                 f"-g{W}x{H}", f"-sOutputFile={png_path}", ps_path],
                check=True, capture_output=True, timeout=10
            )
            print(f"[OK] PNG saved: {png_path}")
            break
        except Exception:
            continue
    else:
        print("[INFO] Ghostscript not found. Showing window only.")
except Exception as e:
    print(f"[INFO] PS export failed ({e}). Showing window only.")

print("Close the window when done reviewing.")
root.mainloop()
