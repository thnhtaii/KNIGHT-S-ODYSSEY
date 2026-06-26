import os

COLS = 50
ROWS = 38
TILE = 16

T_AIR = 0
T_WALL = 54
T_SLOW = 30 

with open("map_design.txt", "r") as f:
    lines = [line.rstrip("\n").ljust(COLS) for line in f.readlines()]

if len(lines) != ROWS:
    print(f"Error: expected {ROWS} rows, got {len(lines)}")
    exit(1)

terrain = [[T_AIR for _ in range(COLS)] for _ in range(ROWS)]
ladders = []
spawns = []

def add_spawn(obj_id, name, width, height, c, r, align_bottom=True):
    y_px = (r + 1) * TILE - height if align_bottom else r * TILE
    x_px = c * TILE
    
    props = ""
    if name == "knight":
        props = '<property name="player" value="yes"/>'
    elif name in ["dragon", "boss_knight"]:
        props = '<property name="enemy" value="yes"/>'
    elif name == "BGDoor":
        props = '<property name="win" value="yes"/>'

    spawns.append(f'''  <object id="{obj_id}" name="{name}" x="{x_px}" y="{y_px}" width="{width}" height="{height}">
   <properties>
    {props}
   </properties>
  </object>''')

ladder_cols = set()
for r in range(ROWS):
    for c in range(COLS):
        char = lines[r][c]
        if char == '#':
            terrain[r][c] = T_WALL
        elif char == 'L':
            terrain[r][c] = T_AIR
            ladder_cols.add((r, c))
        elif char == 'P':
            add_spawn(100, "knight", 64, 64, c, r)
        elif char == 'E':
            add_spawn(105, "BGDoor", 64, 64, c, r)
            ladder_cols.add((r, c)) # Cho phép leo trực tiếp lên vị trí cổng
        elif char in '123':
            add_spawn(100 + int(char), "dragon", 48, 48, c, r)

visited_L = set()
ladder_objects = []
lad_id = 1
for r in range(ROWS):
    for c in range(COLS):
        if lines[r][c] == 'L' and (r, c) not in visited_L:
            start_r = r
            end_r = r
            while end_r + 1 < ROWS and lines[end_r + 1][c] == 'L':
                end_r += 1
            for ir in range(start_r, end_r + 1):
                visited_L.add((ir, c))
                if c + 1 < COLS and lines[ir][c+1] == 'L':
                    visited_L.add((ir, c+1))
            
            w_cols = 1
            while c + w_cols < COLS and lines[r][c + w_cols] == 'L':
                w_cols += 1
                
            x_px = c * TILE
            y_px = start_r * TILE
            width = w_cols * TILE
            height = (end_r - start_r + 1) * TILE
            
            ladder_objects.append(f'''  <object id="{lad_id}" name="ladder" x="{x_px}" y="{y_px}" width="{width}" height="{height}">
   <properties>
    <property name="ladder" value="yes"/>
   </properties>
  </object>''')
            lad_id += 1

# Slow zone
for r in range(16, 26):
    for c in range(1, 21):
        if terrain[r][c] == T_WALL:
            terrain[r][c] = T_SLOW

# Generate collision objects (gnd & wall)
coll_objects = []
for r in range(ROWS):
    c = 0
    while c < COLS:
        if terrain[r][c] in (T_WALL, T_SLOW):
            start_c = c
            while c < COLS and terrain[r][c] in (T_WALL, T_SLOW):
                c += 1
            w = (c - start_c) * TILE
            h = TILE
            x = start_c * TILE
            y = r * TILE
            # Ground object
            coll_objects.append(f'''  <object name="gnd" x="{x}" y="{y}" width="{w}" height="{h}">
   <properties>
    <property name="blockers" value="tlrb"/>
   </properties>
  </object>''')
            # Wall object
            coll_objects.append(f'''  <object name="wall" x="{x}" y="{y}" width="{w}" height="{h}">
   <properties>
    <property name="blockers" value="tlrb"/>
   </properties>
  </object>''')
        else:
            c += 1

terrain_csv = ",\n".join(",".join(str(terrain[r][c]) for c in range(COLS)) for r in range(ROWS))

# Background layer: toàn bộ là 0 (trong suốt) để hiện ảnh nền 8.jpg
bg_csv = ",\n".join(",".join("0" for c in range(COLS)) for r in range(ROWS))

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.11.2" orientation="orthogonal" renderorder="right-down" width="50" height="38" tilewidth="16" tileheight="16" infinite="0" nextlayerid="9" nextobjectid="110">
 <tileset firstgid="1" source="../assets/sprites/background/Blue.tsx"/>
 <tileset firstgid="17" source="../assets/sprites/terrain/Terrain Sliced (16x16).tsx"/>
 <layer id="1" name="background" width="50" height="38">
  <data encoding="csv">
{bg_csv}
  </data>
 </layer>
 <layer id="2" name="map" width="50" height="38">
  <data encoding="csv">
{terrain_csv}
  </data>
 </layer>
 <objectgroup id="3" name="triggers">
{chr(10).join(coll_objects)}
{chr(10).join(ladder_objects)}
{chr(10).join(spawns)}
 </objectgroup>
</map>'''

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "level5.tmx")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(xml)

print(f"[OK] level5.tmx compiled from map_design.txt -> {out_path}")
print(f"     Found {len(ladder_objects)} ladders and {len(spawns)} entities.")
