import pygame  # Thư viện game
import sys     # Để thoát chương trình
import os      # Để xử lý đường dẫn

# Reconfigure stdout/stderr to support UTF-8 characters on Windows console
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')


# Import các lớp từ thư mục src/scenes
from src.scenes.background import Background
from src.scenes.menu import Menu
from src.scenes.battle_level1 import BattleLevel1
from src.scenes.battle_level2 import BattleLevel2
from src.scenes.battle_level3 import BattleLevel3
from src.scenes.battle_boss import BattleBoss
from src.ui.health_bar import HealthBar  


def main():
    pygame.init()
    pygame.mixer.init()
    screen = pygame.display.set_mode((800, 608))
    pygame.display.set_caption("STICKY MAN")

    # Khởi tạo thanh máu và danh sách màn mở khóa
    player_health = 100
    unlocked_levels = [1, 2]  # Chỉ mở khóa level 1 ban đầu
    health_bar = HealthBar(20, 20, 140, 20, player_health)

    current_scene = "background"
    while True:
        if current_scene == "background":
            background = Background(screen)
            current_scene = background.run()

        elif current_scene == "menu":
            menu_scene = Menu(screen, unlocked_levels=unlocked_levels)  # Truyền danh sách mở khóa
            current_scene = menu_scene.run()

        elif current_scene == "level1":
            battle = BattleLevel1(screen, health_bar, player_health)
            result = battle.run()
            if result == "win":
                if 2 not in unlocked_levels:
                    unlocked_levels.append(2)
                current_scene = "menu"
            elif result == "menu":
                current_scene = "menu"
            elif result == "quit":
                current_scene = "quit"

        elif current_scene == "level2":
            battle = BattleLevel2(screen, health_bar, player_health)
            result = battle.run()
            if result == "win":
                if 3 not in unlocked_levels:
                    unlocked_levels.append(3)
                current_scene = "menu"
            elif result == "menu":
                current_scene = "menu"
            elif result == "quit":
                current_scene = "quit"

        elif current_scene == "level3":
            battle = BattleLevel3(screen, health_bar, player_health)
            result = battle.run()
            if result == "win":
                if 4 not in unlocked_levels:
                    unlocked_levels.append(4)
                current_scene = "menu"
            elif result == "menu":
                current_scene = "menu"
            elif result == "quit":
                current_scene = "quit"
            else:
                current_scene = result

        elif current_scene == "boss":
            battle = BattleBoss(screen, health_bar, player_health)
            result = battle.run()
            current_scene = result

        elif current_scene == "quit":
            pygame.quit()
            sys.exit()


if __name__ == "__main__":
    main()