import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import pygame
pygame.init()
screen = pygame.display.set_mode((800, 608))

class DummyBar:
    def set_health(self, x): pass
    def draw(self, x): pass

try:
    from src.scenes.battle_level5 import BattleLevel5
    b = BattleLevel5(screen, DummyBar(), 100)
    print("Level 5 initialized successfully.")
    
    # Run a few logic frames
    for _ in range(5):
        b.update_enemy_paths()
        for d in b.boss_list:
            if d.alive:
                d.move_along_path()
    print("Pathfinding and movement logic run successfully.")
except Exception as e:
    import traceback
    traceback.print_exc()
