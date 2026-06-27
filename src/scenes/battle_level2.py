import pygame
from src.scenes.battle_base import BattleBase
from src.components.music_manager import MusicManager
from src.entities.knight import Knight
from src.entities.ice_wolf import IceWolf
from src.ui.settings_menu import SettingsMenu
from src.ui.game_over import GameOverScreen
from src.components.level_manager import LevelLogicManager
from src.ui.game_victory import GameVictoryScreen
import os
import random
import math

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
        self.wolf_list = []
        self.logic_manager = LevelLogicManager(self.wolf_list)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicLV2.mp3')
        
        self.music_manager = MusicManager()
        self.music_manager.play_music(music_path)

        # Khởi tạo các đối tượng từ object layer
        bg_dir = os.path.join(project_root, 'assets', 'backgrounds')
        
        # Load and cache optimized background image once
        bg_path = os.path.join(bg_dir, "level2_improved.png")
        self.bg_image = pygame.image.load(bg_path).convert()
        self.bg_image = pygame.transform.smoothscale(self.bg_image, (800, 608))

        # Load and smoothscale level 2 scene pieces preserving aspect ratios
        self.BGDoor = pygame.image.load(os.path.join(bg_dir, "BGDoor_level2.png")).convert_alpha()
        self.BGDoor = pygame.transform.smoothscale(self.BGDoor, (380, 650))

        # Load custom platform, ground, and wall images
        self.custom_platform_img = pygame.image.load(os.path.join(bg_dir, "custom_platform_level2.png")).convert_alpha()
        self.custom_ground_img = pygame.image.load(os.path.join(bg_dir, "custom_ground_level2.png")).convert_alpha()
        self.custom_wall_img = pygame.image.load(os.path.join(bg_dir, "custom_wall_level2.png")).convert_alpha()
        self.left_wall_img = pygame.transform.smoothscale(self.custom_wall_img, (340, 650))

        self.cached_platforms = []
        for obj in self.ground_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            w = int(obj["width"])
            h = int(obj["height"])
            if y < 450:
                if x == 0:
                    continue  # Khong ve de vi vach da nen da co san hinh anh buc
                else:
                    img = pygame.transform.smoothscale(self.custom_platform_img, (w, h))
            else:
                if x < 32:
                    w += x
                    x = 0
                if x + w > 768:
                    w = 800 - x
                img = pygame.transform.smoothscale(self.custom_ground_img, (w, h))
            self.cached_platforms.append((img, x, y))

        # Khởi tạo particle systems
        self.snow_particles = []
        for _ in range(80):
            self.snow_particles.append({
                'x': random.uniform(0, 800),
                'y': random.uniform(-10, 608),
                'speed_y': random.uniform(1.0, 2.5),
                'speed_x': random.uniform(-0.5, 0.5),
                'size': random.randint(2, 4),
                'opacity': random.randint(100, 220)
            })
        self.portal_particles = []

        # Tên thuật toán cho từng Ice Wolf
        wolf_algo_names = ["wolf_astar", "wolf_greedy", "wolf_ida_star"]
        wolf_count = 0

        for obj in self.spawn_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            props = obj["properties"]
            
            if props.get("win") == "yes":
                self.door_pos = (580 + 129, -30 + 324)

            if props.get("player") == "yes":
                self.player = Knight(x, y, scale=0.35, speed=3, battle_base=self)
                self.player.flip = True
                self.player.direction = -1
                self.player_group = pygame.sprite.Group(self.player)

        # Spawn exactly 4 wolves on different platforms
        platforms = [
            {"x": 585, "y": 280, "w": 170},  # Platform 3 (Top Right)
            {"x": 215, "y": 326, "w": 130},  # Platform 4 (Middle Left)
            {"x": 380, "y": 385, "w": 185},  # Platform 5 (Middle Center)
            {"x": 583, "y": 444, "w": 150},  # Platform 6 (Lower Right)
        ]

        for p in platforms:
            platform_left = p["x"] - p["w"] // 2
            move_area = pygame.Rect(platform_left, p["y"] - 80, p["w"], 160)
            wolf = IceWolf(p["x"], p["y"], 0.5, 2, self, move_area=move_area)
            wolf.name = wolf_algo_names[wolf_count % len(wolf_algo_names)]
            wolf_count += 1
            self.wolf_list.append(wolf)


        if not self.player:
            raise ValueError("Không tìm thấy object 'player' trong map!")

        self.enemy_group = pygame.sprite.Group(self.wolf_list)
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
                        # Gây sát thương từ frame 1 trở đi (mở rộng window sát thương)
                        if self.player.attack_frame >= 1:
                            # Tạo vùng tấn công theo hướng nhân vật đang đối mặt (bao gồm cả thân người chơi)
                            attack_width = 60  # Tầm chém hợp lý trước mặt
                            if self.player.flip:
                                # Quay trái: bắt đầu từ phía trước mặt bên trái kéo dài qua hết thân người chơi
                                attack_x = self.player.rect.left - attack_width
                            else:
                                # Quay phải: bắt đầu từ rìa trái thân người chơi kéo dài ra phía trước bên phải
                                attack_x = self.player.rect.left
                            attack_range = pygame.Rect(
                                attack_x,
                                self.player.rect.top - 10,
                                self.player.rect.width + attack_width,
                                self.player.rect.height + 20
                            )
                            # Khởi tạo set theo dõi wolf đã bị đánh trong lượt attack này
                            if not hasattr(self, '_attacked_wolves'):
                                self._attacked_wolves = set()
                            for wolf in self.wolf_list:
                                if wolf.alive and id(wolf) not in self._attacked_wolves and attack_range.colliderect(wolf.rect):
                                    print(f">>> HIT! Attack range: {attack_range}, Wolf rect: {wolf.rect}")
                                    self._attacked_wolves.add(id(wolf))
                                    wolf.check_alive()  # Chết ngay sau một lần đánh
                                    print(f"[IceWolf] {wolf.name} đã chết!")
                    else:
                        # Các hành động khác
                        if self.player.attack and self.player.in_air:
                            self.player.update_action(10)
                        elif self.player.attack:
                            if self.player.action != 3:
                                self._attacked_wolves = set()  # Reset danh sách wolf đã bị đánh
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

                # Cập nhật Ice Wolf
                for wolf in self.wolf_list[:]:  # Sao chép danh sách để tránh lỗi khi xóa
                    if wolf.alive:
                        # 1) Run pathfinding / movement
                        if wolf.name == "wolf_astar":
                            wolf.update_astar(self.player, self.grid, self.margin_data)
                        elif wolf.name == "wolf_greedy":
                            wolf.update_greedy(self.player, self.grid, self.margin_data)
                        elif wolf.name == "wolf_ida_star":
                            wolf.update_ida_star(self.player, self.grid, self.margin_data)
                        else:
                            wolf.move()

                        # 2) Attack check
                        wolf.try_attack_player(self.player)

                        # 3) Decide animation based on current state (centralized)
                        wolf.decide_animation()
                    else:
                        if wolf.action != 3:
                            wolf.update_action(3)  # Đảm bảo chuyển sang Die
                        if wolf.death_animation_complete:
                            self.wolf_list.remove(wolf)
                            self.enemy_group.remove(wolf)
                            print(f"[IceWolf] {wolf.name} đã được xóa!")
                            continue

                    # 4) Update animation exactly once per frame
                    wolf.update_animation()

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
        # 1) Draw cached smoothscaled background
        self.screen.blit(self.bg_image, (-self.camera_offset[0], -self.camera_offset[1]))

        # 2) Draw tile layers (excluding ground/platform layers as in base class)
        for layer_idx, layer in enumerate(self.tile_layers):
            if layer_idx < len(self.tile_layers_visibility) and not self.tile_layers_visibility[layer_idx]:
                continue
            if layer_idx < len(self.tile_layers_names) and self.tile_layers_names[layer_idx] in ["ground", "platform"]:
                continue
            for idx, tile in enumerate(layer):
                tile = int(tile)
                if tile > 0:
                    col_idx = idx % self.map_width
                    row_idx = idx // self.map_width
                    img = self.tiles.get(tile)
                    if img:
                        self.screen.blit(
                            img,
                            (
                                col_idx * self.tile_width - self.camera_offset[0],
                                row_idx * self.tile_height - self.camera_offset[1]
                            )
                        )

        # 3) Draw left wall and right portal door (with natural aspect ratio and smooth scaling)
        self.screen.blit(self.left_wall_img, (-60 - self.camera_offset[0], -30 - self.camera_offset[1]))
        self.screen.blit(self.BGDoor, (520 - self.camera_offset[0], -30 - self.camera_offset[1]))

        # 4) Draw the custom platform, ground and wall images from cache
        for img, x, y in self.cached_platforms:
            draw_x = x - self.camera_offset[0]
            draw_y = y - self.camera_offset[1]
            self.screen.blit(img, (draw_x, draw_y))

        # 5) Draw portal vortex glowing particles
        vortex_x = 520 + 240 - self.camera_offset[0]
        vortex_y = -30 + 150 - self.camera_offset[1]
        
        # Update and draw portal particles
        if len(self.portal_particles) < 25:
            angle = random.uniform(0, math.pi * 2)
            dist = random.uniform(5, 45)
            self.portal_particles.append({
                'x': vortex_x + math.cos(angle) * dist,
                'y': vortex_y + math.sin(angle) * dist,
                'vx': -math.cos(angle) * random.uniform(0.2, 0.8) - math.sin(angle) * random.uniform(0.1, 0.4),
                'vy': -math.sin(angle) * random.uniform(0.2, 0.8) + math.cos(angle) * random.uniform(0.1, 0.4),
                'life': 1.0,
                'decay': random.uniform(0.015, 0.03),
                'size': random.randint(2, 4),
                'color': random.choice([
                    (0, 240, 255),    # cyan
                    (100, 255, 255),  # light cyan
                    (0, 150, 255)     # blue
                ])
            })
            
        for p in self.portal_particles[:]:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['life'] -= p['decay']
            if p['life'] <= 0:
                self.portal_particles.remove(p)
            else:
                alpha = int(p['life'] * 255)
                sparkle_surf = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
                pygame.draw.circle(sparkle_surf, p['color'] + (alpha,), (p['size'], p['size']), p['size'])
                self.screen.blit(sparkle_surf, (p['x'] - p['size'], p['y'] - p['size']))

        # 6) Draw sprites
        for sprite in self.player_group:
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.screen.blit(flipped_image, (sprite.rect.x - self.camera_offset[0], sprite.rect.y - self.camera_offset[1]))

        for sprite in self.enemy_group:
            if sprite.alive or sprite.action == 3:  # Vẽ Ice Wolf sống hoặc đang trong trạng thái Die
                draw_x = sprite.rect.centerx - sprite.image.get_width() // 2 - self.camera_offset[0]
                draw_y = sprite.rect.bottom - sprite.image.get_height() - self.camera_offset[1]
                flipped = pygame.transform.flip(sprite.image, sprite.flip, False)
                self.screen.blit(flipped, (draw_x, draw_y))
                if sprite.alive:
                    # Styled Cyberpunk HUD label capsule
                    font = pygame.font.SysFont("Consolas", 11, bold=True)
                    algo_name = sprite.name.replace("wolf_", "").upper()
                    text_surface = font.render(algo_name, True, (0, 255, 255))
                    text_rect = text_surface.get_rect(center=(sprite.rect.centerx - self.camera_offset[0], sprite.rect.top - 15 - self.camera_offset[1]))
                    
                    bg_rect = pygame.Rect(text_rect.x - 6, text_rect.y - 3, text_rect.width + 12, text_rect.height + 6)
                    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                    bg_surf.fill((10, 20, 30, 200))
                    pygame.draw.rect(bg_surf, (0, 200, 255), (0, 0, bg_rect.width, bg_rect.height), 1, border_radius=4)
                    self.screen.blit(bg_surf, bg_rect)
                    self.screen.blit(text_surface, text_rect)

        # 7) Draw falling snow particles
        for p in self.snow_particles:
            p['y'] += p['speed_y']
            p['x'] += p['speed_x']
            if p['y'] > 608:
                p['y'] = -10
                p['x'] = random.uniform(0, 800)
            snow_surf = pygame.Surface((p['size']*2, p['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(snow_surf, (255, 255, 255, p['opacity']), (p['size'], p['size']), p['size'])
            self.screen.blit(snow_surf, (p['x'] - p['size'], p['y'] - p['size']))

        # 8) Draw UI HUD
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
