import os

COLS = 50
ROWS = 38
TILE = 16

T_AIR = 0
T_WALL = 54

with open("levels/level6_design.txt", "r") as f:
    lines = [line.rstrip("\n").ljust(COLS) for line in f.readlines()]

if len(lines) != ROWS:
    print(f"Error: expected {ROWS} rows, got {len(lines)}")
    exit(1)

terrain = [[T_AIR for _ in range(COLS)] for _ in range(ROWS)]
spawns = []

def add_spawn(obj_id, name, width, height, c, r, align_bottom=True):
    y_px = (r + 1) * TILE - height if align_bottom else r * TILE
    x_px = c * TILE
    
    props = ""
    if name == "knight":
        props = '<property name="player" value="yes"/>'
    elif name == "boss_robot":
        props = '<property name="enemy" value="yes"/>'

    spawns.append(f'''  <object id="{obj_id}" name="{name}" x="{x_px}" y="{y_px}" width="{width}" height="{height}">
   <properties>
    {props}
   </properties>
  </object>''')

for r in range(ROWS):
    for c in range(COLS):
        char = lines[r][c]
        if char == '#':
            terrain[r][c] = T_WALL
        elif char == 'P':
            add_spawn(100, "knight", 64, 64, c, r)
        elif char == 'B':
            add_spawn(200, "boss_robot", 64, 64, c, r)

# Generate collision objects (gnd & wall)
coll_objects = []
for r in range(ROWS):
    c = 0
    while c < COLS:
        if terrain[r][c] == T_WALL:
            start_c = c
            while c < COLS and terrain[r][c] == T_WALL:
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
bg_csv = ",\n".join(",".join("0" for c in range(COLS)) for r in range(ROWS))

xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<map version="1.10" tiledversion="1.11.2" orientation="orthogonal" renderorder="right-down" width="50" height="38" tilewidth="16" tileheight="16" infinite="0" nextlayerid="9" nextobjectid="210">
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
{chr(10).join(spawns)}
 </objectgroup>
</map>'''

out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "level6.tmx")
with open(out_path, "w", encoding="utf-8") as f:
    f.write(xml)

print(f"[OK] level6.tmx compiled from level6_design.txt -> {out_path}")
print(f"     Found {len(spawns)} entities.")
