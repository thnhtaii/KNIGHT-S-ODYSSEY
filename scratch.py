import pygame
import os
import sys

# Add project root to sys.path
sys.path.append(os.path.abspath('.'))

from src.scenes.battle_level5 import BattleLevel5

pygame.init()
screen = pygame.display.set_mode((800, 608))
level = BattleLevel5(screen)

print(f"Door pos: {level.door_pos}")
px = level.player.rect.centerx // 16
py = level.player.rect.bottom // 16 - 1
print(f"Player pos: {px}, {py}")

# Flood fill from player without dragons
from collections import deque
visited = set()
q = deque([(px, py)])
visited.add((px, py))
while q:
    cx, cy = q.popleft()
    for nx, ny in level.get_neighbors(cx, cy):
        if (nx, ny) not in visited:
            visited.add((nx, ny))
            q.append((nx, ny))

print(f"Total reachable tiles: {len(visited)}")
print("Are there any tiles with y=7 in visited?")
print([ (x, y) for x, y in visited if y == 7 ])
