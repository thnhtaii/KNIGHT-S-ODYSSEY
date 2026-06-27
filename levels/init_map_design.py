import json, os

COLS = 50
ROWS = 38
TILE = 16

def create_template():
    lines = []
    lines.append("#" * COLS)
    for i in range(ROWS - 2):
        if i % 6 == 4:
            lines.append("#" * COLS) # floor
        else:
            lines.append("#" + "." * (COLS - 2) + "#")
    lines.append("#" * COLS)
    return "\n".join(lines)

if not os.path.exists("map_design.txt"):
    with open("map_design.txt", "w") as f:
        f.write(create_template())
