import xml.etree.ElementTree as ET

tree = ET.parse('levels/level5.tmx')
root = tree.getroot()
triggers = root.find(".//objectgroup[@name='triggers']")

print('Total objects:', len(triggers.findall('object')))
gnds = [o for o in triggers.findall('object') if o.get('name') == 'gnd']
print('Ground objects:', len(gnds))

knight = [o for o in triggers.findall('object') if o.get('name') == 'knight'][0]
print('Knight y_px:', knight.get('y'))

nearest = None
min_dy = 9999
knight_x = float(knight.get('x'))
knight_bottom = float(knight.get('y')) + 64

for g in gnds:
    x = float(g.get('x'))
    w = float(g.get('width'))
    y = float(g.get('y'))
    
    if x <= knight_x <= x + w:
        if y >= knight_bottom:
            dy = y - knight_bottom
            if dy < min_dy:
                min_dy = dy
                nearest = g

print("Nearest ground below knight:", nearest.attrib if nearest else None)
print("Distance to ground:", min_dy)

