#!/usr/bin/env python3
"""
Level 5 TMJ Generator for Stickyman Battle
===============================================
Maze layout: 4 horizontal levels connected by ladders
- Level 4 (top)   : rows 2-6   → EXIT at top-right
- Level 3         : rows 9-13
- Level 2         : rows 16-20 → SLOW ZONE (center)
- Level 1 (bottom): rows 23-30 → PLAYER STARTS here

Separators (solid 2-tile walls with ladder holes):
- Between L4↔L3  : rows 7-8
- Between L3↔L2  : rows 14-15
- Between L2↔L1  : rows 21-22
- Bottom ground   : rows 31-36

Vertical dividers in each level create sections:
- L4: cols 12, 24, 36 → sections L4A / L4B / L4C / L4D(EXIT)
- L3: cols 16, 33     → sections L3A / L3B / L3C
- L2: col  24         → sections L2A(slow) / L2B
- L1: cols 16, 32     → sections L1A(start) / L1B / L1C

Ladder connections (vertical):
  HoleA(c5-6)  : L4A ↕ L3A
  HoleB(c29-30): L4C ↕ L3B
  HoleC(c44-45): L4D ↕ L3C
  HoleD(c9-10) : L3A ↕ L2A
  HoleE(c40-41): L3C ↕ L2B
  HoleF(c14-15): L2A ↕ L1A
  HoleG(c21-22): L2A ↕ L1B
  HoleH(c36-37): L2B ↕ L1C

Routes from L1A (START) to L4D (EXIT):
  Route 1: L1A→(F)→L2A→(gap)→L2B→(E)→L3C→(B up)→L4C→→L4D
  Route 2: L1A→(F)→L2A→(D)→L3A→(A)→L4A→→→→→→→L4D
  Route 3: L1B→(G)→L2A→(D)→L3A→→L3B→(B)→L4C→→L4D
  Route 4: L1C→(H)→L2B→(E)→L3C→(C)→L4D ← shortest but hardest

Dragon spawn positions:
  D1: L4C col 30  → guards passage L4C→L4D
  D2: L3B col 24  → guards center of L3
  D3: L2A col 12  → guards slow zone entrance (Ladder D area)
  D4: L1B col 24  → guards center of bottom level
"""

import json
import os

COLS = 50
ROWS = 38
TILE = 16  # tile size in pixels

# Tile IDs (matching level1.tmj tileset)
T_AIR  = 0
T_WALL = 54  # solid block (wall/floor/ceiling)

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────
terrain = [[T_AIR] * COLS for _ in range(ROWS)]

def fill_row(r, c1, c2, t=T_WALL):
    for c in range(c1, c2 + 1):
        if 0 <= r < ROWS and 0 <= c < COLS:
            terrain[r][c] = t

def fill_col(c, r1, r2, t=T_WALL):
    for r in range(r1, r2 + 1):
        if 0 <= r < ROWS and 0 <= c < COLS:
            terrain[r][c] = t

def air(r, c):
    if 0 <= r < ROWS and 0 <= c < COLS:
        terrain[r][c] = T_AIR

def air_rect(r1, r2, c1, c2):
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            air(r, c)

# ─────────────────────────────────────────────
# Background layer (Blue.tsx repeating pattern)
# ─────────────────────────────────────────────
def bg_tile(col, row):
    return (row % 4) * 4 + (col % 4) + 1

bg_data = [bg_tile(c, r) for r in range(ROWS) for c in range(COLS)]

# ─────────────────────────────────────────────
# BUILD TERRAIN
# ─────────────────────────────────────────────

# ── 1. Outer boundary ──
fill_row(0,        0, COLS-1)
fill_row(ROWS-1,   0, COLS-1)
fill_col(0,        0, ROWS-1)
fill_col(COLS-1,   0, ROWS-1)

# ── 2. Inner ceiling (top of L4) ──
fill_row(1, 1, 48)

# ── 3. Level separators ──
for r in [7, 8]:    fill_row(r, 1, 48)   # L4 ↔ L3
for r in [14, 15]:  fill_row(r, 1, 48)   # L3 ↔ L2
for r in [21, 22]:  fill_row(r, 1, 48)   # L2 ↔ L1
for r in range(31, 37): fill_row(r, 1, 48)  # Bottom ground

# ── 4. Vertical dividers ──
# Level 4  (rows 2-6)
for c in [12, 24, 36]: fill_col(c, 2, 6)
# Level 3  (rows 9-13)
for c in [16, 33]:     fill_col(c, 9, 13)
# Level 2  (rows 16-20)
fill_col(24, 16, 20)
# Level 1  (rows 23-30)
for c in [16, 32]:     fill_col(c, 23, 30)

# ── 5. Passages through vertical walls (horizontal movement) ──
# L4 passages at rows 5-6 (floor level)
for c in [12, 24, 36]:
    air(5, c); air(6, c)

# L3 passages at rows 12-13
for c in [16, 33]:
    air(12, c); air(13, c)

# L2 passage at rows 19-20
air(19, 24); air(20, 24)

# L1 passages at rows 29-30
for c in [16, 32]:
    air(29, c); air(30, c)

# ── 6. Ladder holes in separators (vertical movement) ──
HOLES = {
    "A": (7, 8,  5,  6),   # L4A ↕ L3A
    "B": (7, 8,  29, 30),  # L4C ↕ L3B
    "C": (7, 8,  44, 45),  # L4D ↕ L3C
    "D": (14, 15, 9, 10),  # L3A ↕ L2A
    "E": (14, 15, 40, 41), # L3C ↕ L2B
    "F": (21, 22, 14, 15), # L2A ↕ L1A
    "G": (21, 22, 21, 22), # L2A ↕ L1B
    "H": (21, 22, 36, 37), # L2B ↕ L1C
}

for name, (r1, r2, c1, c2) in HOLES.items():
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            air(r, c)

# ─────────────────────────────────────────────
# FLATTEN TERRAIN → 1D data list
# ─────────────────────────────────────────────
terrain_data = [terrain[r][c] for r in range(ROWS) for c in range(COLS)]

# ─────────────────────────────────────────────
# LADDER OBJECTS
# Span from top of upper level through hole to bottom of lower level
# ─────────────────────────────────────────────
ladder_defs = [
    # HoleA: cols 5-6, L4A↕L3A → ladder spans rows 5-11
    ("LadderA",  5*TILE,  5*TILE, 2*TILE, 7*TILE),
    # HoleB: cols 29-30, L4C↕L3B
    ("LadderB", 29*TILE,  5*TILE, 2*TILE, 7*TILE),
    # HoleC: cols 44-45, L4D↕L3C
    ("LadderC", 44*TILE,  5*TILE, 2*TILE, 7*TILE),
    # HoleD: cols 9-10, L3A↕L2A → ladder spans rows 12-18
    ("LadderD",  9*TILE, 12*TILE, 2*TILE, 7*TILE),
    # HoleE: cols 40-41, L3C↕L2B
    ("LadderE", 40*TILE, 12*TILE, 2*TILE, 7*TILE),
    # HoleF: cols 14-15, L2A↕L1A → ladder spans rows 19-25
    ("LadderF", 14*TILE, 19*TILE, 2*TILE, 7*TILE),
    # HoleG: cols 21-22, L2A↕L1B
    ("LadderG", 21*TILE, 19*TILE, 2*TILE, 7*TILE),
    # HoleH: cols 36-37, L2B↕L1C
    ("LadderH", 36*TILE, 19*TILE, 2*TILE, 7*TILE),
]

ladder_objects = [
    {
        "height": float(h), "id": i + 1, "name": name,
        "rotation": 0, "type": "", "visible": True,
        "width": float(w), "x": float(x), "y": float(y)
    }
    for i, (name, x, y, w, h) in enumerate(ladder_defs)
]

# ─────────────────────────────────────────────
# SPAWN OBJECTS
# ─────────────────────────────────────────────
spawn_objects = [
    # ── Knight: L1A, col 3, standing on ground row 30 ──
    {
        "height": 64, "id": 100, "name": "knight", "rotation": 0,
        "type": "", "visible": True, "width": 64,
        "x": float(3 * TILE), "y": float(27 * TILE)
    },
    # ── Dragon 1: L4C, col 30 (guards last passage to EXIT) ──
    {
        "height": 48, "id": 101, "name": "dragon", "rotation": 0,
        "type": "", "visible": True, "width": 48,
        "x": float(30 * TILE), "y": float(4 * TILE)
    },
    # ── Dragon 2: L3B, col 24 (guards center of L3) ──
    {
        "height": 48, "id": 102, "name": "dragon", "rotation": 0,
        "type": "", "visible": True, "width": 48,
        "x": float(24 * TILE), "y": float(11 * TILE)
    },
    # ── Dragon 3: L2A, col 12 (slow zone, guards Ladder D) ──
    {
        "height": 48, "id": 103, "name": "dragon", "rotation": 0,
        "type": "", "visible": True, "width": 48,
        "x": float(12 * TILE), "y": float(18 * TILE)
    },
    # ── Dragon 4: L1B, col 24 (guards center of bottom level) ──
    {
        "height": 48, "id": 104, "name": "dragon", "rotation": 0,
        "type": "", "visible": True, "width": 48,
        "x": float(24 * TILE), "y": float(27 * TILE)
    },
    # ── Exit door (BGDoor): top-right of L4D, col 44-45, row 2-3 ──
    {
        "height": 64, "id": 105, "name": "BGDoor", "rotation": 0,
        "type": "", "visible": True, "width": 64,
        "x": float(44 * TILE), "y": float(2 * TILE)
    },
]

# ─────────────────────────────────────────────
# ASSEMBLE TMJ
# ─────────────────────────────────────────────
tmj = {
    "compressionlevel": -1,
    "editorsettings": {
        "export": {"format": "tmx", "target": "level5.tmx"}
    },
    "height": ROWS,
    "infinite": False,
    "layers": [
        {
            "data": bg_data,
            "height": ROWS, "id": 1, "locked": True,
            "name": "background", "opacity": 1,
            "type": "tilelayer", "visible": True,
            "width": COLS, "x": 0, "y": 0
        },
        {
            "data": terrain_data,
            "height": ROWS, "id": 6,
            "name": "map", "opacity": 1,
            "type": "tilelayer", "visible": True,
            "width": COLS, "x": 0, "y": 0
        },
        {
            "draworder": "topdown", "id": 7,
            "name": "ladder",
            "objects": ladder_objects,
            "opacity": 1,
            "type": "objectgroup", "visible": True,
            "x": 0, "y": 0
        },
        {
            "draworder": "topdown", "id": 8,
            "name": "objLV5",
            "objects": spawn_objects,
            "opacity": 0.76,
            "type": "objectgroup", "visible": True,
            "x": 0, "y": 0
        },
    ],
    "nextlayerid": 9,
    "nextobjectid": 110,
    "orientation": "orthogonal",
    "renderorder": "right-down",
    "tiledversion": "1.11.2",
    "tileheight": 16,
    "tilesets": [
        {"firstgid": 1,  "source": "../assets/sprites/background/Blue.tsx"},
        {"firstgid": 17, "source": "../assets/sprites/terrain/Terrain Sliced (16x16).tsx"},
    ],
    "tilewidth": 16,
    "type": "map",
    "version": "1.10",
    "width": COLS,
}

# ─────────────────────────────────────────────
# WRITE FILES
# ─────────────────────────────────────────────
out_dir = os.path.dirname(os.path.abspath(__file__))
out_path = os.path.join(out_dir, "level5.tmj")

with open(out_path, "w", encoding="utf-8") as f:
    json.dump(tmj, f, indent=1)

print(f"[OK] level5.tmj written -> {out_path}")
print(f"     Map: {COLS}x{ROWS} tiles  ({COLS*TILE}x{ROWS*TILE} px)")
print()

# ASCII map for quick verification
symbols = {T_WALL: "#", T_AIR: "."}
ladder_holes = set()
for name, (r1, r2, c1, c2) in HOLES.items():
    for r in range(r1, r2 + 1):
        for c in range(c1, c2 + 1):
            ladder_holes.add((r, c))

print("-" * (COLS + 5))
print("MAZE LAYOUT  (#=wall  .=air  L=ladder-hole)")
for r in range(ROWS):
    row_str = f"R{r:02d} "
    for c in range(COLS):
        if terrain[r][c] == T_WALL:
            row_str += "#"
        elif (r, c) in ladder_holes:
            row_str += "L"
        else:
            row_str += "."
    print(row_str)

print()
print("SECTIONS:")
print("  L4: A(c1-11) B(c13-23) C(c25-35) D(c37-48)  <- EXIT col44")
print("  L3: A(c1-15) B(c17-32) C(c34-48)")
print("  L2: A(c1-23) SLOW ZONE  B(c25-48)")
print("  L1: A(c1-15) START  B(c17-31)  C(c33-48)")
print()
print("LADDER HOLES:")
for name, (r1, r2, c1, c2) in HOLES.items():
    print(f"  Hole {name}: rows {r1}-{r2}, cols {c1}-{c2}")
print()
print("DRAGON SPAWNS:")
print("  D1: L4C col30 row4  (guards L4C->L4D passage)")
print("  D2: L3B col24 row11 (guards center L3)")
print("  D3: L2A col12 row18 (guards LadderD / slow zone)")
print("  D4: L1B col24 row27 (guards center bottom)")
