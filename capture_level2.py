import pygame
import sys
import os

# Set paths
project_root = r"d:\ky 2 nam 2\AI_cuoiky\Stickyman-Battle"
sys.path.insert(0, project_root)

from src.scenes.battle_level2 import BattleLevel2
from src.ui.health_bar import HealthBar

def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 608))
    pygame.display.set_caption("TEST LEVEL 2 CAPTURE")

    player_health = 100
    health_bar = HealthBar(20, 20, 140, 20, player_health)

    # Initialize level 2
    battle = BattleLevel2(screen, health_bar, player_health)

    # Run for 60 frames to let the knight land
    clock = pygame.time.Clock()
    for frame in range(90):
        # Handle events so window doesn't freeze
        for event in pygame.event.get():
            pass
        
        # Update player and scene
        battle.player.move(False, False) # just let player fall
        
        # We need to simulate the updates that battle.run() does
        # Let's check if the player falls and lands
        battle.player.update_animation()
        
        # Draw everything
        battle.draw()
        pygame.display.flip()
        clock.tick(60)

    # Save screenshot
    screenshot_path = r"C:\Users\dotai\.gemini\antigravity\brain\9f8dbed2-40a8-48e6-b01f-4daa6cbbf7df\level2_capture.png"
    pygame.image.save(screen, screenshot_path)
    print("Screenshot saved successfully to", screenshot_path)
    pygame.quit()

if __name__ == '__main__':
    main()
