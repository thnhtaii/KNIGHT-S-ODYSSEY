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

class BattleLevel1(BattleBase):
    def __init__(self, screen, health_bar, player_health):
        super().__init__(screen, level_name="level1")
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
        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicLV1.mp3')
        
        self.music_manager = MusicManager()
        self.music_manager.play_music(music_path)

        # Khởi tạo các đối tượng từ object layer
        BGDoor_dir = os.path.join(project_root, 'assets', 'backgrounds')
        self.BGDoor = pygame.image.load(os.path.join(BGDoor_dir, "BGDoor.png")).convert_alpha()
        self.BGDoor = pygame.transform.scale(self.BGDoor, (96, 89))

        slime_count = 0
        for obj in self.spawn_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            props = obj["properties"]
            
            if props.get("win") == "yes":
                self.door_pos = (obj["x"], obj["y"])

            if props.get("player") == "yes":
                self.player = Knight(x, y, scale=0.35, speed=3, battle_base=self)
                self.player_group = pygame.sprite.Group(self.player)
            elif props.get("enemy") == "yes":
                # Xác định tên và chỉ số luân phiên ban đầu trước khi lọc bỏ để tránh lệch tên
                names = ["slime_bfs", "slime_dfs", "slime_ucs"]
                current_slime_name = names[slime_count % 3]
                slime_count += 1

                if len(self.slime_list) >= 5:
                    continue

                move_area = pygame.Rect(x - 100, y - 50, 200, 100)
                slime_dir = os.path.join(project_root, 'assets', 'sprites', 'slime')
                custom_img_name = "custom_slime1.png" if len(self.slime_list) % 2 == 0 else "custom_slime2.png"
                custom_img_path = os.path.join(slime_dir, custom_img_name)
                
                # Biến đổi màu nước văng/hiệu ứng bị chém từ xanh dương sang xanh lục nhạt
                color_swap = {
                    (20, 52, 100): (20, 70, 40),      # Outline xanh dương -> Outline xanh lục đậm
                    (40, 92, 196): (60, 180, 100),    # Thân xanh dương -> Thân xanh lục
                    (36, 159, 222): (120, 230, 150),  # Highlight xanh dương -> Highlight xanh lục nhạt
                    (32, 214, 199): (166, 252, 219)   # Chi tiết cyan -> Chi tiết xanh lục nhạt/bạc hà
                }
                
                slime = Slime(x, y, 1.0, 2, self, move_area=move_area, custom_img_path=custom_img_path, color_swap=color_swap)
                slime.name = current_slime_name
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

        # Load and cache custom platform and ground images (with transparent backgrounds)
        bg_dir = os.path.join(project_root, 'assets', 'backgrounds')
        self.custom_platform_img = pygame.image.load(os.path.join(bg_dir, "custom_platform.png")).convert_alpha()
        self.custom_ground_img = pygame.image.load(os.path.join(bg_dir, "custom_ground.png")).convert_alpha()

        self.cached_platforms = []
        for obj in self.ground_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            w = int(obj["width"])
            h = int(obj["height"])
            if obj["y"] < 450:
                img = pygame.transform.scale(self.custom_platform_img, (w, h))
            else:
                # Kéo giãn sát viền trái/phải nếu là mặt đất chính
                if x < 32:
                    w += x
                    x = 0
                if x + w > 768:
                    w = 800 - x
                img = pygame.transform.scale(self.custom_ground_img, (w, h))
            self.cached_platforms.append((img, x, y))

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
                    if self.player.action == 3:
                        print(f"[DEBUG ATTACK] action=3, frame_index={self.player.frame_index}, attack_frame={self.player.attack_frame}, anim_len={len(self.player.animation_list[3])}, flip={self.player.flip}")
                    if self.player.action == 3 and self.player.frame_index < len(self.player.animation_list[3]) - 1:
                        # Gây sát thương từ frame 1 trở đi (mở rộng window sát thương)
                        if self.player.attack_frame >= 1:
                            # Tạo vùng tấn công rộng, bao phủ từ người chơi ra phía trước
                            attack_width = 80  # Tầm chém rộng hơn
                            if self.player.flip:
                                # Quay trái: vùng tấn công từ trái người chơi
                                attack_x = self.player.rect.left - attack_width
                            else:
                                # Quay phải: vùng tấn công từ bên phải người chơi
                                attack_x = self.player.rect.left
                            attack_range = pygame.Rect(
                                attack_x,
                                self.player.rect.top - 30,
                                self.player.rect.width + attack_width,
                                self.player.rect.height + 60
                            )
                            # Khởi tạo set theo dõi slime đã bị đánh trong lượt attack này
                            if not hasattr(self, '_attacked_slimes'):
                                self._attacked_slimes = set()
                            for slime in self.slime_list:
                                if slime.alive:
                                    print(f"[DEBUG HIT CHECK] attack_range={attack_range}, slime '{slime.name}' rect={slime.rect}, collide={attack_range.colliderect(slime.rect)}, already_hit={id(slime) in self._attacked_slimes}")
                                if slime.alive and id(slime) not in self._attacked_slimes and attack_range.colliderect(slime.rect):
                                    print(f">>> HIT! Attack range: {attack_range}, Slime rect: {slime.rect}")
                                    self._attacked_slimes.add(id(slime))
                                    slime.check_alive()  # Chết ngay sau một lần đánh
                                    print(f"[Slime] {slime.name} đã chết!")
                    else:
                        # Các hành động khác
                        if self.player.attack and self.player.in_air:
                            self.player.update_action(10)
                        elif self.player.attack:
                            if self.player.action != 3:
                                self._attacked_slimes = set()  # Reset danh sách slime đã bị đánh
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
                        elif slime.name == "slime_dfs":
                            slime.update_dfs(self.player, self.grid, self.margin_data)
                        elif slime.name == "slime_ucs":
                            slime.update_ucs(self.player, self.grid, self.margin_data)
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
        super().draw(self.camera_offset)

        # Vẽ các platform và ground custom từ cache (đã được lọc trong suốt)
        for img, x, y in self.cached_platforms:
            draw_x = x - self.camera_offset[0]
            draw_y = y - self.camera_offset[1]
            self.screen.blit(img, (draw_x, draw_y))

        if self.door_pos:
            door_x = self.door_pos[0] - self.camera_offset[0]
            door_y = self.door_pos[1] - self.BGDoor.get_height() - self.camera_offset[1]
            # pygame.draw.rect(self.screen, (255, 0, 0), pygame.Rect(door_x, door_y, 64, 64), 2)
            self.screen.blit(self.BGDoor, (door_x, door_y))

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
                    text_rect = text_surface.get_rect(center=(draw_x + sprite.rect.width // 2, draw_y - 12))
                    # Draw a small dark background box for high legibility
                    bg_rect = pygame.Rect(text_rect.x - 4, text_rect.y - 2, text_rect.width + 8, text_rect.height + 4)
                    bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                    bg_surface.fill((0, 0, 0, 160))
                    self.screen.blit(bg_surface, bg_rect)
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