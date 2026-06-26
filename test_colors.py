import pygame

def analyze_image():
    pygame.init()
    img = pygame.image.load('assets/sprites/ladder/ladder.png')
    w, h = img.get_size()
    cell_w = w // 6
    cell_h = h // 5
    
    cell = img.subsurface(pygame.Rect(0, 0, cell_w, cell_h))
    
    colors = {}
    for y in range(cell_h):
        for x in range(cell_w):
            c = cell.get_at((x, y))
            c_tup = (c.r, c.g, c.b, c.a)
            colors[c_tup] = colors.get(c_tup, 0) + 1
            
    sorted_colors = sorted(colors.items(), key=lambda x: x[1], reverse=True)
    
    print("Top 10 colors (RGBA, count):")
    for i in range(min(10, len(sorted_colors))):
        print(sorted_colors[i])
        
if __name__ == "__main__":
    analyze_image()
