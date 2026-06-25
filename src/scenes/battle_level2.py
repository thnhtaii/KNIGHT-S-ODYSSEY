import pygame
from src.scenes.battle_base import BattleBase
from src.components.music_manager import MusicManager
from src.entities.knight import Knight
from src.entities.slime import Slime
from src.ui.settings_menu import SettingsMenu
from src.ui.game_over import GameOverScreen
from src.components.level_manager import LevelLogicManager
from src.ui.game_victory import GameVictoryScreen
import os

class BattleLevel2(BattleBase):
    def __init__(self, screen, health_bar, player_health):
        super().__init__(screen, level_name="level2")
        self.screen = screen
        self.health_bar = health_bar
        self.player_health = player_health
        self.running = True
        self.paused = False
        self.door_pos = None
        self.player = None
        self.slime_list = []
        self.logic_manager = LevelLogicManager(self.slime_list)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicLV2.mp3')
        
        self.music_manager = MusicManager()
        self.music_manager.play_music(music_path)

        # Khởi tạo các đối tượng từ object layer
        bg_dir = os.path.join(project_root, 'assets', 'backgrounds')
        
        # Load and scale level 2 scene pieces.
        self.BGDoor = pygame.image.load(os.path.join(bg_dir, "BGDoor_level2.png")).convert_alpha()
        self.BGDoor = pygame.transform.scale(self.BGDoor, (489, 600))

        # Load custom platform, ground, and wall images
        self.custom_platform_img = pygame.image.load(os.path.join(bg_dir, "custom_platform_level2.png")).convert_alpha()
        self.custom_platform_chunky = pygame.image.load(os.path.join(bg_dir, "custom_platform_chunky.png")).convert_alpha()
        self.custom_ground_img = pygame.image.load(os.path.join(bg_dir, "custom_ground_level2.png")).convert_alpha()
        self.custom_wall_img = pygame.image.load(os.path.join(bg_dir, "custom_wall_level2.png")).convert_alpha()
        self.left_wall_img = pygame.transform.scale(self.custom_wall_img, (260, 608))

        self.cached_platforms = []
        for obj in self.ground_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            w = int(obj["width"])
            h = int(obj["height"])
            if y < 450:
                if x == 0:
                    h_draw = int(w * 481 / 623)
                    img = pygame.transform.scale(self.custom_platform_chunky, (w, h_draw))
                else:
                    img = pygame.transform.scale(self.custom_platform_img, (w, h))
            else:
                if x < 32:
                    w += x
                    x = 0
                if x + w > 768:
                    w = 800 - x
                img = pygame.transform.scale(self.custom_ground_img, (w, h))
            self.cached_platforms.append((img, x, y))

        for obj in self.spawn_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            props = obj["properties"]
            
            if props.get("win") == "yes":
                self.door_pos = (obj["x"], obj["y"])

            if props.get("player") == "yes":
                self.player = Knight(x, y, scale=0.35, speed=3, battle_base=self)
                self.player.flip = True
                self.player.direction = -1
                self.player_group = pygame.sprite.Group(self.player)
            if props.get("enemy") == "yes":
                move_area = pygame.Rect(x - 100, y - 50, 200, 100)
                slime = Slime(x, y, 1.0, 2, self, move_area=move_area)
                
                if len(self.slime_list) == 0:
                    slime.name = "slime_bfs"
                elif len(self.slime_list) == 1:
                    slime.name = "slime_andor"

                self.slime_list.append(slime)

        if not self.player:
            raise ValueError("Không tìm thấy object 'player' trong map!")

        self.enemy_group = pygame.sprite.Group(self.slime_list)
        self.moving_left = False
        self.moving_right = False

        # Khởi tạo camera offset
        self.camera_offset = [0, 0]
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Khởi tạo các icon
        icon_dir = os.path.join(project_root, 'assets', 'icons')
        self.settings_icon = pygame.image.load(os.path.join(icon_dir, "settings_icon.png"))
        self.settings_icon = pygame.transform.scale(self.settings_icon, (30, 30))
        self.settings_button = pygame.Rect(750, 10, 30, 30)

        self.pause_icon = pygame.image.load(os.path.join(icon_dir, "pause_icon.png"))
        self.pause_icon = pygame.transform.scale(self.pause_icon, (30, 30))
        self.pause_button = pygame.Rect(700, 10, 30, 30)

        self.continue_icon = pygame.image.load(os.path.join(icon_dir, "continue_icon.png"))
        self.continue_icon = pygame.transform.scale(self.continue_icon, (30, 30))
        self.continue_button = pygame.Rect(650, 10, 30, 30)

        # Tạo lưới grid một lần duy nhất
        self.grid = []
        for row in range(self.map_height):
            line = []
            for col in range(self.map_width):
                tile = self.tile_layers[1][row * self.map_width + col]
                line.append(1 if tile > 0 else 0)
            self.grid.append(line)

    def run(self):
        clock = pygame.time.Clock()
        self.prev_health = self.player.health  # Khởi tạo máu ban đầu

        while self.running:
            self.logic_manager.update()

            if self.door_pos:
                door_rect = pygame.Rect(self.door_pos[0], self.door_pos[1] - 64, 64, 64)
                player_rect = self.player.rect.move(-self.camera_offset[0], -self.camera_offset[1])
                if self.logic_manager.check_victory(player_rect, door_rect):
                    victory_screen = GameVictoryScreen(self.screen)
                    result = victory_screen.run()
                    if result == "menu":
                        return "win"  # báo rõ là đã thắng, không phải chỉ về menu
                    elif result == "quit":
                        return "quit"

                

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return "menu"
                    if event.key == pygame.K_p:
                        self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_a:
                            self.moving_left = True
                        if event.key == pygame.K_d:
                            self.moving_right = True
                        if event.key == pygame.K_w and self.player.alive:
                            self.player.jump = True
                        if event.key == pygame.K_SPACE and self.player.alive:
                            self.player.update_action(3)
                            self.player.attack = True
                        if event.key == pygame.K_b:
                            self.player.block = True
                        if event.key == pygame.K_c:
                            self.player.cast = True
                        if event.key == pygame.K_s:
                            self.player.crouch = True
                        if event.key == pygame.K_e:
                            self.player.dash = True
                elif event.type == pygame.KEYUP:
                    if not self.paused:
                        if event.key == pygame.K_a:
                            self.moving_left = False
                        if event.key == pygame.K_d:
                            self.moving_right = False
                        if event.key == pygame.K_b:
                            self.player.block = False
                        if event.key == pygame.K_c:
                            self.player.cast = False
                        if event.key == pygame.K_s:
                            self.player.crouch = False
                        if event.key == pygame.K_e:
                            self.player.dash = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_button.collidepoint(event.pos):
                        self.paused = True
                    elif self.continue_button.collidepoint(event.pos):
                        self.paused = False
                    elif self.settings_button.collidepoint(event.pos):
                        settings_menu = SettingsMenu(self.screen)
                        result = settings_menu.run()
                        if result == "menu":
                            return "menu"
                        elif result == "back":
                            continue

            if self.player.alive and not self.paused:
                self.player.move(self.moving_left, self.moving_right)
                map_height_px = self.map_height * self.tile_height
                if self.player.rect.top > map_height_px:
                    self.player.health = 0
                    self.player.check_alive()
                    print("[Knight] Rơi khỏi bản đồ!")


                # Cập nhật camera
                map_width_px = self.map_width * self.tile_width
                map_height_px = self.map_height * self.tile_height
                target_x = self.player.rect.centerx - self.screen_width // 2
                target_y = self.player.rect.centery - self.screen_height // 2
                self.camera_offset[0] = max(0, min(target_x, map_width_px - self.screen_width))
                self.camera_offset[1] = max(0, min(target_y, map_height_px - self.screen_height))

                # Nếu máu giảm và chưa trong trạng thái hurt thì kích hoạt
                if self.player.health < self.prev_health and not self.player.is_hurt:
                    self.player.is_hurt = True
                    self.player.update_action(8)
                    self.player.frame_index = 0
                    print("[Knight] Bị thương!")

                self.prev_health = self.player.health

                # Nếu đang hurt thì không làm gì thêm
                if self.player.is_hurt:
                    pass
                else:
                    # Kiểm tra nếu đang trong animation Attack
                    if self.player.action == 3 and self.player.frame_index < len(self.player.animation_list[3]) - 1:
                        # Gây sát thương ở frame thứ 2 của Attack
                        if self.player.attack_frame == 2:
                            attack_range = pygame.Rect(
                                self.player.rect.left - 50 if self.player.flip else self.player.rect.right,
                                self.player.rect.top - 20,
                                50,
                                self.player.rect.height + 20
                            )
                            for slime in self.slime_list:
                                if slime.alive and attack_range.colliderect(slime.rect):
                                    print(f"Attack range: {attack_range}, Slime rect: {slime.rect}")
                                    slime.check_alive()  # Chết ngay sau một lần đánh
                                    print(f"[Slime] {slime.name} đã chết!")
                    else:
                        # Các hành động khác
                        if self.player.attack and self.player.in_air:
                            self.player.update_action(10)
                        elif self.player.attack:
                            if self.player.action != 3:
                                self.player.update_action(3)
                        elif self.player.block:
                            self.player.update_action(4)
                        elif self.player.cast:
                            self.player.update_action(5)
                        elif self.player.crouch:
                            self.player.update_action(6)
                        elif self.player.dash:
                            self.player.update_action(7)
                        elif self.player.in_air and self.player.vel_y > 1:
                            self.player.update_action(2)
                        elif self.moving_left or self.moving_right:
                            self.player.update_action(1)
                        else:
                            self.player.update_action(0)

                self.player.update_animation()

                # Cập nhật slime
                for slime in self.slime_list[:]:  # Sao chép danh sách để tránh lỗi khi xóa
                    if slime.alive:
                        if slime.name == "slime_bfs":
                            slime.update_bfs(self.player, self.grid, self.margin_data)
                        elif slime.name == "slime_andor":
                            slime.update_andor(self.player, self.grid, self.margin_data)
                        else:
                            slime.move()
                        slime.try_attack_player(self.player)

                        if slime.in_air:
                            slime.update_action(1)
                        else:
                            slime.update_action(0)
                    else:
                        if slime.action != 3:
                            slime.update_action(3)  # Đảm bảo chuyển sang Death
                        slime.update_animation()
                        if slime.frame_index >= len(slime.animation_list[3]) - 1:  # Đã hoàn thành animation Death
                            self.slime_list.remove(slime)
                            self.enemy_group.remove(slime)
                            print(f"[Slime] {slime.name} đã được xóa!")

                    slime.update_animation()

            if not self.player.alive:
                self.player_health = 0
                self.health_bar.set_health(self.player_health)
                game_over_screen = GameOverScreen(self.screen)
                result = game_over_screen.run()
                if result == "restart":
                    return "restart"
                elif result == "menu":
                    return "menu"
                elif result == "quit":
                    self.running = False
            else:
                self.player_health = self.player.health
                self.health_bar.set_health(self.player_health)

            self.draw()
            pygame.display.flip()
            clock.tick(60)
            print(f"FPS: {clock.get_fps()}")

    def draw(self):
        self.screen.fill((0, 0, 0))
        bg_filename = f"{self.level_name}.jpg"
        bg_path = os.path.join(self.project_root, "assets", "backgrounds", bg_filename)
        if os.path.exists(bg_path):
            bg = pygame.image.load(bg_path).convert()
            self.screen.blit(bg, (-self.camera_offset[0], -self.camera_offset[1]))
        super().draw(self.camera_offset)

        # Large scenic pieces for level 2 only. These are visual backdrops; wall
        # collision still comes from the object layer in level2.tmx.
        self.screen.blit(self.left_wall_img, (-22 - self.camera_offset[0], 0 - self.camera_offset[1]))
        self.screen.blit(self.BGDoor, (380 - self.camera_offset[0], -2 - self.camera_offset[1]))

        # Draw the custom platform, ground and wall images from cache
        for img, x, y in self.cached_platforms:
            draw_x = x - self.camera_offset[0]
            draw_y = y - self.camera_offset[1]
            self.screen.blit(img, (draw_x, draw_y))

        for sprite in self.player_group:
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.screen.blit(flipped_image, (sprite.rect.x - self.camera_offset[0], sprite.rect.y - self.camera_offset[1]))

        for sprite in self.enemy_group:
            if sprite.alive or sprite.action == 3:  # Vẽ Slime sống hoặc đang trong trạng thái Death
                draw_x = sprite.rect.x - self.camera_offset[0]
                draw_y = sprite.rect.y - self.camera_offset[1]
                self.screen.blit(sprite.image, (draw_x, draw_y))
                if sprite.alive:
                    font = pygame.font.SysFont("Arial", 10, bold=True)
                    algo_name = sprite.name.replace("slime_", "").upper()
                    text_surface = font.render(algo_name, True, (255, 255, 255))
                    text_rect = text_surface.get_rect(center=(draw_x + sprite.rect.width // 2, draw_y + sprite.rect.height // 2 + 2))
                    self.screen.blit(text_surface, text_rect)

        self.health_bar.draw(self.screen)

        self.screen.blit(self.settings_icon, (self.settings_button.x, self.settings_button.y))
        self.screen.blit(self.pause_icon, (self.pause_button.x, self.pause_button.y))
        self.screen.blit(self.continue_icon, (self.continue_button.x, self.continue_button.y))

        if self.paused:
            font = pygame.font.SysFont('Arial', 36, bold=True)
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)

        # pygame.draw.rect(self.screen, (0, 255, 255), (
        #     self.player.rect.x - self.camera_offset[0],
        #     self.player.rect.y - self.camera_offset[1],
        #     self.player.rect.width,
        #     self.player.rect.height
        # ), 2)
