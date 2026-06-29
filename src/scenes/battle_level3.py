import pygame
from src.scenes.battle_base import BattleBase
from src.components.music_manager import MusicManager
from src.entities.knight import Knight
from src.entities.soldier import Soldier
from src.ui.settings_menu import SettingsMenu
from src.ui.game_over import GameOverScreen
from src.components.level_manager import LevelLogicManager
from src.ui.game_victory import GameVictoryScreen
import os

class BattleLevel3(BattleBase):
    def __init__(self, screen, health_bar, player_health):
        super().__init__(screen, level_name="level3")
        self.screen = screen
        self.health_bar = health_bar
        self.player_health = player_health
        self.running = True
        self.paused = False
        self.door_pos = None
        self.player = None
        self.slime_list = [] # Lưu binh sĩ để LevelLogicManager tương thích
        self.logic_manager = LevelLogicManager(self.slime_list)
        from src.components.ai_stats_tracker import AIStatsTracker
        AIStatsTracker.reset("Level 3")

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicLV3.mp3')
        
        self.music_manager = MusicManager()
        self.music_manager.play_music(music_path)

        # Khởi tạo cửa qua màn
        BGDoor_dir = os.path.join(project_root, 'assets', 'backgrounds')
        self.BGDoor = pygame.image.load(os.path.join(BGDoor_dir, "level3_door.png")).convert_alpha()
        self.BGDoor = pygame.transform.scale(self.BGDoor, (96, 96))

        # Khởi tạo đối tượng từ object layer của map
        for obj in self.spawn_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            props = obj["properties"]
            
            if props.get("win") == "yes":
                self.door_pos = (obj["x"], obj["y"])

            if props.get("player") == "yes":
                self.player = Knight(x, y, scale=0.35, speed=3, battle_base=self)
                self.player_group = pygame.sprite.Group(self.player)
                
            if props.get("enemy") == "yes":
                algo_name = props.get("algo", "hill_climb")
                # Xác định vùng di chuyển (move_area) dựa trên độ cao spawn và vị trí x
                if y < 250:  # Tầng 3 (y=224)
                    if x < 400:  # Left Top Floor
                        move_area = pygame.Rect(16, y - 50, 224, 100)
                    else:        # Right Top Floor (nếu có)
                        move_area = pygame.Rect(720, y - 50, 64, 100)
                elif y < 400:  # Tầng 2 (y=320 hoặc y=368)
                    if x < 450:  # Left Mid-floor (y=320)
                        move_area = pygame.Rect(288, y - 50, 112, 100)
                    else:        # Right Mid-floor (y=368)
                        move_area = pygame.Rect(576, y - 50, 112, 100)
                else:  # Tầng 1 (y=528)
                    if x < 400:  # Bottom Left Floor
                        move_area = pygame.Rect(16, y - 50, 304, 100)
                    else:        # Bottom Right Floor
                        move_area = pygame.Rect(480, y - 50, 304, 100)
                
                soldier = Soldier(x, y, scale=0.5, speed=2, battle_base=self, move_area=move_area)
                soldier.algo = algo_name
                display_algo = "Hill Climbing" if "hill_climb" in algo_name else (
                    "Simulated Annealing" if "simulated_annealing" in algo_name else (
                        "Local Beam" if "local_beam" in algo_name else algo_name
                    )
                )
                soldier.name = f"Binh si {len(self.slime_list) + 1} ({display_algo})"
                self.slime_list.append(soldier)

        if not self.player:
            raise ValueError("Không tìm thấy object 'player' trong map Màn 3!")

        self.enemy_group = pygame.sprite.Group(self.slime_list)
        self.moving_left = False
        self.moving_right = False

        # Khởi tạo camera offset
        self.camera_offset = [0, 0]
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Khởi tạo các nút icon
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

        # Tạo lưới grid cho tìm kiếm
        self.grid = []
        for row in range(self.map_height):
            line = []
            for col in range(self.map_width):
                tile = self.tile_layers[1][row * self.map_width + col]
                line.append(1 if tile > 0 else 0)
            self.grid.append(line)

        # Ẩn layer gạch nền gốc của Tiled để tránh hiển thị chồng chéo
        if "ground" in self.tile_layers_names:
            ground_idx = self.tile_layers_names.index("ground")
            if ground_idx < len(self.tile_layers_visibility):
                self.tile_layers_visibility[ground_idx] = False

        # Tải ảnh custom cho Màn 3
        bg_dir = os.path.join(project_root, 'assets', 'backgrounds')
        self.custom_platform_img = pygame.image.load(os.path.join(bg_dir, "level3_platform.png")).convert_alpha()
        self.custom_ground_img = pygame.image.load(os.path.join(bg_dir, "level3_ground.png")).convert_alpha()

        self.cached_platforms = []
        map_width_px = self.map_width * self.tile_width
        for obj in self.ground_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            w = int(obj["width"])
            h = int(obj["height"])
            
            if y < 450:
                img = self.create_tiled_surface(self.custom_platform_img, w, h)
            else:
                # Kéo giãn sát viền theo chiều rộng bản đồ
                if x < 32:
                    w += x
                    x = 0
                if x + w > map_width_px - 32:
                    w = map_width_px - x
                img = self.create_tiled_surface(self.custom_ground_img, w, h)
            self.cached_platforms.append((img, x, y))

    def create_tiled_surface(self, tile_img, w, h):
        """Tạo một Surface lặp lại (tiled) từ tile_img sắc nét."""
        tile_h = h
        scale_ratio = h / tile_img.get_height()
        tile_w = int(tile_img.get_width() * scale_ratio)
        if tile_w <= 0:
            tile_w = h
        
        scaled_tile = pygame.transform.scale(tile_img, (tile_w, tile_h))
        tiled_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for tx in range(0, w, tile_w):
            tiled_surf.blit(scaled_tile, (tx, 0))
        return tiled_surf


    def run(self):
        clock = pygame.time.Clock()
        self.prev_health = self.player.health

        while self.running:
            self.logic_manager.update()

            if self.door_pos:
                door_rect = pygame.Rect(self.door_pos[0], self.door_pos[1] - 64, 64, 64)
                if self.logic_manager.is_door_unlocked() and self.logic_manager.check_victory(self.player.rect, door_rect):
                    victory_screen = GameVictoryScreen(self.screen)
                    result = victory_screen.run()

                    from src.ui.ai_dashboard import AIDashboard
                    from src.components.ai_stats_tracker import AIStatsTracker
                    dashboard = AIDashboard(self.screen, AIStatsTracker.get_stats())
                    dashboard.run()

                    if result == "menu":
                        return "win"
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
                    print("[Knight] Rơi khỏi bản đồ Màn 3!")

                # Cập nhật camera
                map_width_px = self.map_width * self.tile_width
                map_height_px = self.map_height * self.tile_height
                target_x = self.player.rect.centerx - self.screen_width // 2
                target_y = self.player.rect.centery - self.screen_height // 2
                self.camera_offset[0] = max(0, min(target_x, map_width_px - self.screen_width))
                self.camera_offset[1] = max(0, min(target_y, map_height_px - self.screen_height))

                # Kích hoạt trạng thái bị thương (Hurt)
                if self.player.health < self.prev_health and not self.player.is_hurt:
                    self.player.is_hurt = True
                    self.player.update_action(8)
                    self.player.frame_index = 0

                self.prev_health = self.player.health

                if not self.player.is_hurt:
                    if self.player.action in [3, 10] and self.player.frame_index < len(self.player.animation_list[self.player.action]) - 1:
                        if self.player.attack_frame == 2:
                            attack_range = pygame.Rect(
                                self.player.rect.left - 50 if self.player.flip else self.player.rect.right,
                                self.player.rect.top - 20,
                                50,
                                self.player.rect.height + 20
                            )
                            for slime in self.slime_list:
                                if slime.alive and attack_range.colliderect(slime.rect):
                                    slime.check_alive() # Tiêu diệt binh sĩ ngay
                    else:
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

                # Cập nhật chuyển động của binh sĩ (Soldier)
                for slime in self.slime_list[:]:
                    if slime.alive:
                        if "hill_climb" in slime.algo:
                            slime.update_hill_climb(self.player, self.grid, self.margin_data)
                        elif "simulated_annealing" in slime.algo:
                            slime.update_simulated_annealing(self.player, self.grid, self.margin_data)
                        elif "local_beam" in slime.algo:
                            slime.update_local_beam(self.player, self.grid, self.margin_data)
                        else:
                            slime.move()
                            
                        slime.try_attack_player(self.player)
                    else:
                        if slime.action != 3:
                            slime.update_action(3)
                        slime.update_animation()
                        if getattr(slime, 'death_animation_complete', False) or slime.frame_index >= len(slime.animation_list[3]) - 1:
                            self.slime_list.remove(slime)
                            self.enemy_group.remove(slime)
                            print(f"[Soldier] {slime.name} đã được dọn dẹp!")

                    slime.update_animation()

            if not self.player.alive:
                self.player_health = 0
                self.health_bar.set_health(self.player_health)
                
                game_over_screen = GameOverScreen(self.screen)
                result = game_over_screen.run()

                from src.ui.ai_dashboard import AIDashboard
                from src.components.ai_stats_tracker import AIStatsTracker
                dashboard = AIDashboard(self.screen, AIStatsTracker.get_stats())
                dashboard.run()
                
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

    def draw(self):
        self.screen.fill((0, 0, 0))
        bg_filename = f"{self.level_name}.jpg"
        bg_path = os.path.join(self.project_root, "assets", "backgrounds", bg_filename)
        if os.path.exists(bg_path):
            bg = pygame.image.load(bg_path).convert()
            bg = pygame.transform.scale(bg, (self.screen_width, self.screen_height))
            self.screen.blit(bg, (-self.camera_offset[0], -self.camera_offset[1]))
            
        super().draw(self.camera_offset)

        # Vẽ các platform và ground custom từ cache (đã xếp lát sắc nét)
        for img, x, y in self.cached_platforms:
            draw_x = x - self.camera_offset[0]
            draw_y = y - self.camera_offset[1]
            self.screen.blit(img, (draw_x, draw_y))


        if self.door_pos:
            door_x = self.door_pos[0] - self.camera_offset[0]
            door_y = self.door_pos[1] - self.BGDoor.get_height() - self.camera_offset[1]
            self.screen.blit(self.BGDoor, (door_x, door_y))

        for sprite in self.player_group:
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.screen.blit(flipped_image, (sprite.rect.x - self.camera_offset[0], sprite.rect.y - self.camera_offset[1]))

        for sprite in self.enemy_group:
            if sprite.alive or sprite.action == 3:
                draw_x = sprite.rect.x - self.camera_offset[0]
                draw_y = sprite.rect.y - self.camera_offset[1]
                self.screen.blit(pygame.transform.flip(sprite.image, sprite.flip, False), (draw_x, draw_y))
                
                # Hiển thị tên và số thứ tự của binh sĩ
                if sprite.alive:
                    font = pygame.font.SysFont("Arial", 10, bold=True)
                    display_name = sprite.name.upper()
                    text_surface = font.render(display_name, True, (255, 255, 255))
                    text_surface.set_alpha(150)
                    # Binh sĩ tỉ lệ 0.5 (75x75px) có khoảng không trong suốt phía trên, draw_y + 15 sẽ đặt chữ sát trên đầu lính
                    text_rect = text_surface.get_rect(center=(draw_x + sprite.rect.width // 2, draw_y + 15))
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
