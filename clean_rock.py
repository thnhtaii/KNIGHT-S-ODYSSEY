import pygame
import sys
import collections

def clean_image(input_path, output_path):
    pygame.init()
    try:
        img = pygame.image.load(input_path).convert_alpha()
    except Exception as e:
        print(f"Failed to load {input_path}: {e}")
        return

    w, h = img.get_size()
    
    # We will find the main rock mass using BFS (connected component)
    # The rock should be the largest connected component of non-transparent pixels.
    
    visited = set()
    components = []
    
    for y in range(h):
        for x in range(w):
            if (x, y) not in visited:
                color = img.get_at((x, y))
                if color.a > 0:
                    # Found a new component, BFS to find all connected pixels
                    comp = []
                    q = collections.deque([(x, y)])
                    visited.add((x, y))
                    
                    while q:
                        cx, cy = q.popleft()
                        comp.append((cx, cy))
                        
                        for dx, dy in [(-1,0), (1,0), (0,-1), (0,1), (-1,-1), (-1,1), (1,-1), (1,1)]:
                            nx, ny = cx + dx, cy + dy
                            if 0 <= nx < w and 0 <= ny < h:
                                if (nx, ny) not in visited:
                                    ncolor = img.get_at((nx, ny))
                                    if ncolor.a > 0:
                                        visited.add((nx, ny))
                                        q.append((nx, ny))
                    components.append(comp)

    if not components:
        print(f"No pixels found in {input_path}")
        return
        
    # The rock should be the largest component by far
    components.sort(key=len, reverse=True)
    main_rock = set(components[0])
    
    # Create a new surface and only copy the main rock pixels
    clean_img = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(h):
        for x in range(w):
            if (x, y) in main_rock:
                clean_img.set_at((x, y), img.get_at((x, y)))
                
    pygame.image.save(clean_img, output_path)
    print(f"Cleaned {input_path} -> {output_path} (kept {len(main_rock)} pixels, removed {sum(len(c) for c in components[1:])})")

if __name__ == "__main__":
    clean_image("assets/sprites/terrain/floating_rock_1.png", "assets/sprites/terrain/floating_rock_1.png")
    clean_image("assets/sprites/terrain/floating_rock_2.png", "assets/sprites/terrain/floating_rock_2.png")
