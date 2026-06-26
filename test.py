import pygame
pygame.init()
img = pygame.image.load('assets/sprites/ladder/ladder.png')
print(f"Ladder sheet size: {img.get_size()}")
# Check pixel at various positions to understand grid
w, h = img.get_size()
print(f"Width: {w}, Height: {h}")
# Likely a spritesheet with 6 cols x 5 rows based on the visual
# Let's check: 6 cols, 5 rows
print(f"Cell size if 6x5: {w//6}x{h//5}")
print(f"Cell size if 6x6: {w//6}x{h//6}")
pygame.quit()
