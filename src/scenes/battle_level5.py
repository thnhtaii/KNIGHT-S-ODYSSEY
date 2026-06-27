import pygame
import os
from collections import deque
from src.scenes.battle_base import BattleBase
from src.components.music_manager import MusicManager
from src.entities.knight import Knight
from src.entities.dragon import Dragon
from src.ui.settings_menu import SettingsMenu
from src.ui.game_over import GameOverScreen
from src.ui.game_victory import GameVictoryScreen

class BattleLevel5(BattleBase):
    def __init__(self, screen, health_bar, player_health):
        super().__init__(screen, level_name="level5")
        self.screen = screen
        self.health_bar = health_bar
        self.player_health = player_health
        self.running = True
        self.paused = False
        self.door_pos = None
        self.player = None
        self.boss_list = []

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        # Tải và thiết lập phông nền hang rồng (concept dragon cave)
        bg_path = os.path.join(project_root, "assets", "sprites", "dragon", "bg.png")
        if os.path.exists(bg_path):
            bg_raw = pygame.image.load(bg_path).convert()
            map_pixel_w = self.map_width * self.tile_width
            map_pixel_h = self.map_height * self.tile_height
            self._bg_surface = pygame.transform.smoothscale(bg_raw, (map_pixel_w, map_pixel_h))

        # 2. Thiết lập gạch sàn đi chậm (Tile 30) là dung nham đỏ rực tạo tự động (lava_floor.png)
        #    và gạch tường biên (Tile 54) là đá bazan ấm áp không tím (warm_basalt.png)
        lava_path = os.path.join(project_root, "assets", "sprites", "terrain", "lava_floor.png")
        wall_path = os.path.join(project_root, "assets", "sprites", "terrain", "warm_basalt.png")
        
        if os.path.exists(lava_path):
            floor_sheet = pygame.image.load(lava_path).convert_alpha()
            floor_tile = pygame.transform.smoothscale(floor_sheet.subsurface(pygame.Rect(384, 384, 256, 256)), (16, 16))
            self.tiles[30] = floor_tile

        if os.path.exists(wall_path):
            wall_sheet = pygame.image.load(wall_path).convert_alpha()
            border_tile = pygame.transform.smoothscale(wall_sheet.subsurface(pygame.Rect(384, 384, 256, 256)), (16, 16))
            self.tiles[54] = border_tile

        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicLV1.mp3') # Reuse music for now
        
        self.music_manager = MusicManager()
        self.music_manager.play_music(music_path)

        BGDoor_dir = os.path.join(project_root, 'assets', 'backgrounds')
        self.BGDoor = pygame.image.load(os.path.join(BGDoor_dir, "BGDoor.png")).convert_alpha()
        self.BGDoor = pygame.transform.scale(self.BGDoor, (96, 96))
        
        # 3. Nạp và xử lý cầu thang xương tự động (bone_ladder_final.png) được tạo mới
        self.ladder_top = None
        self.ladder_mid = None
        self.ladder_bot = None
        
        bone_ladder_path = os.path.join(project_root, "assets", "sprites", "terrain", "bone_ladder_final.png")
        if os.path.exists(bone_ladder_path):
            bone_ladder_src = pygame.image.load(bone_ladder_path).convert_alpha()
            
            # Áp dụng bộ lọc màu cho xương rồng kem nhạt nhã nhặn, không quá sáng/trắng
            w, h = bone_ladder_src.get_size()
            for y in range(h):
                for x in range(w):
                    r, g, b, a = bone_ladder_src.get_at((x, y))
                    if a > 0:
                        lum = 0.299 * r + 0.587 * g + 0.114 * b
                        if lum > 130:  # Vân đón sáng -> Màu vàng kem/ngà tối
                            nr, ng, nb = 215, 208, 185
                        elif lum > 60:  # Thân xương cốt -> Màu xám kem trầm
                            nr, ng, nb = 175, 170, 155
                        else:  # Khe tối
                            nr, ng, nb = 65, 63, 60
                        bone_ladder_src.set_at((x, y), (nr, ng, nb, a))
            
            # Scale nguồn xương rồng về độ rộng 18px để có tỷ lệ đẹp, không quá to
            scaled_h = int(h * (18 / w))
            scaled_ladder = pygame.transform.smoothscale(bone_ladder_src, (18, scaled_h))
            
            # Cắt thành 3 phần đại diện: đỉnh, thân, đáy để lặp tuần hoàn (tránh méo/giãn ảnh khi thang quá dài/ngắn)
            self.ladder_top = scaled_ladder.subsurface(pygame.Rect(0, 0, 18, 32)).copy()
            self.ladder_mid = scaled_ladder.subsurface(pygame.Rect(0, 56, 18, 32)).copy()
            self.ladder_bot = scaled_ladder.subsurface(pygame.Rect(0, 112, 18, 32)).copy()

        for obj in self.spawn_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            name = obj.get("name", "")
            
            if name == "BGDoor":
                self.door_pos = (x, y)
            elif name == "knight":
                self.player = Knight(x, y, scale=0.35, speed=4, battle_base=self)
                self.player_group = pygame.sprite.Group(self.player)
            elif name == "dragon":
                # Lấy thuật toán theo thứ tự
                if not hasattr(self, 'dragon_count'): self.dragon_count = 0
                algos = ["Backtracking", "AC-3", "Min-Conflicts"]
                algo = algos[self.dragon_count % 3]
                self.dragon_count += 1
                boss = Dragon(x, y, scale=0.6, speed=2, battle_base=self, algo_name=algo)
                self.boss_list.append(boss)

        if not self.player:
            raise ValueError("Không tìm thấy object 'knight' trong map!")

        self.enemy_group = pygame.sprite.Group(self.boss_list)
        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False

        self.camera_offset = [0, 0]
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        icon_dir = os.path.join(project_root, 'assets', 'icons')
        self.settings_icon = pygame.transform.scale(pygame.image.load(os.path.join(icon_dir, "settings_icon.png")), (30, 30))
        self.settings_button = pygame.Rect(750, 10, 30, 30)
        self.pause_icon = pygame.transform.scale(pygame.image.load(os.path.join(icon_dir, "pause_icon.png")), (30, 30))
        self.pause_button = pygame.Rect(700, 10, 30, 30)
        self.continue_icon = pygame.transform.scale(pygame.image.load(os.path.join(icon_dir, "continue_icon.png")), (30, 30))
        self.continue_button = pygame.Rect(650, 10, 30, 30)

        # Build grid for pathfinding & BFS
        self.grid = []
        for row in range(self.map_height):
            line = []
            for col in range(self.map_width):
                tile_id = self.tile_layers[1][row * self.map_width + col]
                # If tile_id > 0, it's a wall or slow zone. We need to know if it's solid.
                # In level5.tmj, 54 is wall, 30 is slow zone (we made 30 solid for walking on, but air is 0)
                # Wait! We set slow zone as solid floor blocks.
                line.append(tile_id)
            self.grid.append(line)

        # Base speed
        self.player_base_speed = self.player.speed

        # Damage logic
        self.last_trapped_damage_time = 0
        self.TRAP_DAMAGE_INTERVAL = 1000 # 1 second
        self.TRAPPED_MAX_DEPTH = 20 # Bán kính giới hạn BFS = 20 ô
        self.is_trapped = False
        self.font_warning = pygame.font.SysFont('Arial', 24, bold=True)

        # Load ảnh pop-up cảnh báo bị bao vây (đã được tách nền hoàn hảo)
        popup_path = os.path.join(project_root, 'assets', 'sprites', 'dragon', 'pop-up_clean.png')
        if os.path.exists(popup_path):
            self.warning_popup = pygame.image.load(popup_path).convert_alpha()
        else:
            self.warning_popup = None

    def run(self):
        clock = pygame.time.Clock()
        self.prev_health = self.player.health

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE: return "menu"
                    if event.key == pygame.K_p: self.paused = not self.paused
                    if not self.paused:
                        if event.key == pygame.K_a: self.moving_left = True
                        if event.key == pygame.K_d: self.moving_right = True
                        if event.key == pygame.K_w:
                            self.moving_up = True
                            if self.player.alive: self.player.jump = True
                        if event.key == pygame.K_s: self.moving_down = True
                        if event.key == pygame.K_SPACE and self.player.alive:
                            self.player.update_action(3)
                            self.player.attack = True
                elif event.type == pygame.KEYUP:
                    if not self.paused:
                        if event.key == pygame.K_a: self.moving_left = False
                        if event.key == pygame.K_d: self.moving_right = False
                        if event.key == pygame.K_w: self.moving_up = False
                        if event.key == pygame.K_s: self.moving_down = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_button.collidepoint(event.pos): self.paused = True
                    elif self.continue_button.collidepoint(event.pos): self.paused = False
                    elif self.settings_button.collidepoint(event.pos):
                        settings_menu = SettingsMenu(self.screen)
                        res = settings_menu.run()
                        if res == "menu": return "menu"
            
            if self.player.alive and not self.paused:
                self.process_slow_zone()
                self.player.move(self.moving_left, self.moving_right, self.moving_up, self.moving_down)
                
                # Check fall off map
                if self.player.rect.top > self.map_height * self.tile_height:
                    self.player.health = 0
                    self.player.check_alive()
                
                # Camera
                target_x = self.player.rect.centerx - self.screen_width // 2
                target_y = self.player.rect.centery - self.screen_height // 2
                self.camera_offset[0] = max(0, min(target_x, self.map_width * self.tile_width - self.screen_width))
                self.camera_offset[1] = max(0, min(target_y, self.map_height * self.tile_height - self.screen_height))

                # Hurt animation
                if self.player.health < self.prev_health and not self.player.is_hurt:
                    self.player.is_hurt = True
                    self.player.update_action(8)
                    self.player.frame_index = 0
                self.prev_health = self.player.health

                if not self.player.is_hurt:
                    if self.player.attack and self.player.action == 3 and self.player.frame_index == 2: # Attack frame
                        attack_rect = pygame.Rect(
                            self.player.rect.left - 30 if self.player.flip else self.player.rect.right,
                            self.player.rect.top, 30, self.player.rect.height)
                        for d in self.boss_list:
                            if d.alive and attack_rect.colliderect(d.rect):
                                d.health = 0 # One hit kills it!
                                d.check_alive()
                                self.player.attack = False # Single hit per click
                    else:
                        if self.player.attack:
                            if self.player.action != 3: self.player.update_action(3)
                        elif self.player.in_air and self.player.vel_y > 1: self.player.update_action(2)
                        elif self.moving_left or self.moving_right: self.player.update_action(1)
                        else: self.player.update_action(0)

                self.player.update_animation()

                # Dragons
                for d in self.boss_list[:]:
                    if d.alive:
                        d.try_attack_player(self.player)
                        d.move_along_path()
                    else:
                        if d.action != 3: d.update_action(3)
                        d.update_animation()
                        if d.frame_index >= len(d.animation_list[3]) - 1:
                            self.boss_list.remove(d)
                            self.enemy_group.remove(d)
                    if d.alive:
                        d.update_animation()

                self.check_if_trapped()
                self.update_enemy_paths()

                # Check Win
                if self.door_pos:
                    # Tạo hitbox nhỏ gọn ngay giữa tâm cổng để người chơi phải vào hẳn bên trong
                    hitbox_x = self.door_pos[0] + 32
                    hitbox_y = self.door_pos[1] + 16
                    door_rect = pygame.Rect(hitbox_x, hitbox_y, 32, 32)
                    if self.player.rect.colliderect(door_rect):
                        res = GameVictoryScreen(self.screen).run()
                        if res == "menu": return "win"
                        if res == "quit": return "quit"

            if not self.player.alive:
                self.health_bar.set_health(0)
                res = GameOverScreen(self.screen).run()
                return res

            self.health_bar.set_health(self.player.health)
            self.draw()
            pygame.display.flip()
            clock.tick(60)

    def is_ladder(self, px, py):
        # Kiểm tra xem ô (px, py) có chạm vào ladder object không
        rect = pygame.Rect(px * self.tile_width, py * self.tile_height, self.tile_width, self.tile_height)
        for lad in self.ladder_objects:
            lad_rect = pygame.Rect(lad["x"], lad["y"], lad["width"], lad["height"])
            if rect.colliderect(lad_rect):
                return True
        return False

    def is_walkable(self, x, y):
        if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height:
            return False
        # Nếu là khí và không có thang thì phải kiểm tra xem bên dưới có sàn không hoặc là thang
        if self.grid[y][x] == 0 and not self.is_ladder(x, y):
            if y + 1 < self.map_height:
                if self.grid[y+1][x] > 0 or self.is_ladder(x, y+1):
                    return True
            return False
        # Nếu là thang thì luôn đi được
        if self.is_ladder(x, y):
            return True
        # Nếu là gạch cứng (không phải khí và không phải thang) thì không đi xuyên được
        return False

    def get_neighbors(self, px, py):
        neighbors = []
        # Đi ngang
        for nx in [px - 1, px + 1]:
            if self.is_walkable(nx, py):
                neighbors.append((nx, py))
                
        # Đi dọc (lên/xuống)
        # Đi xuống nếu ô hiện tại là thang hoặc ô dưới là thang
        if self.is_ladder(px, py) or (py + 1 < self.map_height and self.is_ladder(px, py + 1)):
            if self.is_walkable(px, py + 1):
                neighbors.append((px, py + 1))
        # Đi lên nếu ô hiện tại là thang
        if self.is_ladder(px, py):
            if self.is_walkable(px, py - 1):
                neighbors.append((px, py - 1))
        return neighbors

    def update_enemy_paths(self):
        current_time = pygame.time.get_ticks()
        if not hasattr(self, 'last_path_update'):
            self.last_path_update = 0
            
        # Cập nhật đường đi liên tục mỗi nửa giây để rồng dí nhạy hơn
        if current_time - self.last_path_update < 500:
            return
            
        self.last_path_update = current_time
        
        target_x = self.player.rect.centerx // self.tile_width
        target_y = self.player.rect.bottom // self.tile_height - 1 # Chân người chơi
        
        active_bosses = [b for b in self.boss_list if b.alive]
        if not active_bosses: return
        
        boss_positions = [(b.rect.centerx // self.tile_width, b.rect.bottom // self.tile_height - 1) for b in active_bosses]
        
        # Gọi CSP logic
        from src.ai.csp_surround import CSPSurround
        csp = CSPSurround(self.map_width, self.map_height, self.grid, self.is_walkable)
        
        target_positions = []
        bt_targets = csp.solve_backtracking((target_x, target_y), boss_positions)
        ac3_targets = csp.solve_ac3((target_x, target_y), boss_positions)
        mc_targets = csp.solve_min_conflicts((target_x, target_y), boss_positions)
        
        claimed_targets = set()
        for i, boss in enumerate(active_bosses):
            if boss.algo_name == "Backtracking":
                target = bt_targets[i] if i < len(bt_targets) else boss_positions[i]
            elif boss.algo_name == "AC-3":
                target = ac3_targets[i] if i < len(ac3_targets) else boss_positions[i]
            else: # Min-Conflicts
                target = mc_targets[i] if i < len(mc_targets) else boss_positions[i]
                
            if target in claimed_targets:
                target = boss_positions[i]
            claimed_targets.add(target)
            target_positions.append(target)
            
        for i, boss in enumerate(active_bosses):
            if i < len(target_positions):
                tx, ty = target_positions[i]
                if boss.path:
                    tx_p, ty_p = boss.path[0]
                    start_x = int(tx_p) // self.tile_width
                    start_y = int(ty_p + boss.height // 2 - int(20 * boss.scale)) // self.tile_height - 1
                else:
                    start_x = boss.rect.centerx // self.tile_width
                    start_y = boss.rect.bottom // self.tile_height - 1
                    tx_p, ty_p = None, None
                
                queue = deque([((start_x, start_y), [])])
                visited = set([(start_x, start_y)])
                
                # Tránh các rồng khác để không đi đè lên nhau
                for j, other_boss in enumerate(active_bosses):
                    if i != j:
                        ox = other_boss.rect.centerx // self.tile_width
                        oy = other_boss.rect.bottom // self.tile_height - 1
                        visited.add((ox, oy))
                        if other_boss.path:
                            nx, ny = other_boss.path[0]
                            visited.add((int(nx) // self.tile_width, int(ny + other_boss.height // 2 - int(20 * boss.scale)) // self.tile_height - 1))

                path_found = []
                best_dist = float('inf')
                best_path = []
                
                while queue:
                    (cx, cy), path = queue.popleft()
                    
                    dist = abs(cx - tx) + abs(cy - ty)
                    if dist < best_dist:
                        best_dist = dist
                        best_path = path

                    if cx == tx and cy == ty:
                        path_found = path
                        break
                        
                    if len(path) > 400:
                        continue
                        
                    for nx, ny in self.get_neighbors(cx, cy):
                        if (nx, ny) not in visited:
                            visited.add((nx, ny))
                            queue.append(((nx, ny), path + [(nx, ny)]))
                
                # Nếu không tìm được đường chính xác đến đích do bị chặn, hãy đi con đường gần nhất có thể
                if not path_found and best_path:
                    path_found = best_path
                
                pixel_path = []
                if tx_p is not None and ty_p is not None:
                    pixel_path.append((tx_p, ty_p))
                    
                for px, py in path_found:
                    pixel_path.append((px * self.tile_width + self.tile_width // 2, py * self.tile_height + self.tile_height - boss.height // 2 + int(20 * boss.scale)))
                    
                boss.path = pixel_path
    def process_slow_zone(self):
        px = self.player.rect.centerx // self.tile_width
        py = self.player.rect.bottom // self.tile_height
        
        # Look directly below player for floor tile
        if 0 <= px < self.map_width and 0 <= py < self.map_height:
            tile_id = self.grid[py][px]
            if tile_id == 30: # Slow zone tile
                self.player.speed = self.player_base_speed * 0.5
            else:
                self.player.speed = self.player_base_speed

    def check_if_trapped(self):
        """
        BFS từ vị trí player đến đích (cửa).
        Chỉ bị tính là bao vây khi ĐƯỜNG TỚI ĐÍCH BỊ CHẶN HOÀN TOÀN bởi rồng hoặc tường.
        """
        current_time = pygame.time.get_ticks()
        
        # Mô phỏng map bằng mê cung 2D cứ mỗi 1s (1000ms) để xác định bị bao vây
        if not hasattr(self, 'last_trap_eval_time'):
            self.last_trap_eval_time = 0
            
        if current_time - self.last_trap_eval_time < 1000 and hasattr(self, 'is_trapped'):
            # Dùng lại kết quả của lần đánh giá trước
            pass
        else:
            self.last_trap_eval_time = current_time
            px = self.player.rect.centerx // self.tile_width
            py = self.player.rect.bottom // self.tile_height - 1

            if not self.door_pos:
                return
                
            # Đích đến là các ô SÀN (y = 7) nằm bên dưới cánh cổng (x từ 44 đến 50)
            target_ty = (self.door_pos[1] + 64) // self.tile_height - 1
            target_tx_min = self.door_pos[0] // self.tile_width
            target_tx_max = (self.door_pos[0] + 100) // self.tile_width

            # Lấy tập hợp ô mà lính đang chiếm
            boss_cells = set()
            for d in self.boss_list:
                if d.alive:
                    min_x = d.rect.left // self.tile_width
                    max_x = d.rect.right // self.tile_width
                    min_y = d.rect.top // self.tile_height
                    max_y = d.rect.bottom // self.tile_height
                    for bx in range(min_x, max_x + 1):
                        for by in range(min_y, max_y + 1):
                            boss_cells.add((bx, by))

            def is_escape_walkable(x, y):
                if x < 0 or x >= self.map_width or y < 0 or y >= self.map_height:
                    return False
                if self.grid[y][x] == 0 and not self.is_ladder(x, y):
                    if y + 1 < self.map_height:
                        if self.grid[y+1][x] > 0 or self.is_ladder(x, y+1):
                            return True
                    return False
                if self.is_ladder(x, y):
                    return True
                return False

            def get_escape_neighbors(px, py):
                neighbors = []
                for nx in [px - 1, px + 1]:
                    if is_escape_walkable(nx, py):
                        neighbors.append((nx, py))
                if self.is_ladder(px, py) or (py + 1 < self.map_height and self.is_ladder(px, py + 1)):
                    if is_escape_walkable(px, py + 1):
                        neighbors.append((px, py + 1))
                if self.is_ladder(px, py):
                    if is_escape_walkable(px, py - 1):
                        neighbors.append((px, py - 1))
                # Add jump simulation: if gap is 1 or 2 tiles wide, player can jump across
                for jump_dx in [-2, -3, 2, 3]:
                    nx = px + jump_dx
                    if is_escape_walkable(nx, py) and self.grid[py][min(px, nx):max(px, nx)].count(0) > 0:
                        neighbors.append((nx, py))
                return neighbors

            # BFS từ player để tìm đường tới cửa
            visited = set()
            queue = deque([(px, py)])
            visited.add((px, py))
            escaped = False

            while queue:
                cx, cy = queue.popleft()

                # Kiểm tra xem có đến được khu vực sàn gần cánh cổng chưa
                if cy == target_ty and target_tx_min <= cx <= target_tx_max:
                    escaped = True
                    break

                for nx, ny in get_escape_neighbors(cx, cy):
                    if (nx, ny) not in visited:
                        if (nx, ny) not in boss_cells:
                            visited.add((nx, ny))
                            queue.append((nx, ny))

            self.is_trapped = not escaped

        # Nếu bị chặn hoàn toàn đường tới đích -> bị bao vây -> mất máu
        if self.is_trapped:
            if current_time - self.last_trapped_damage_time >= self.TRAP_DAMAGE_INTERVAL:
                self.player.health -= 10
                self.player.is_hurt = True
                self.player.update_action(8)
                self.player.frame_index = 0
                self.last_trapped_damage_time = current_time
                if self.player.health <= 0:
                    self.player.check_alive()

    def draw(self):
        self.screen.fill((0, 0, 0))
        super().draw(self.camera_offset)

        # Draw ladders visually — Vẽ cầu thang xương rồng thanh mảnh được ghép từ các khúc xương tuần hoàn
        for lad in self.ladder_objects:
            lx = lad["x"] - self.camera_offset[0]
            ly = lad["y"] - self.camera_offset[1]
            lw = lad["width"]
            lh = lad["height"]
            
            if self.ladder_mid:
                seg_h = 32
                num_segments = max(1, int(lh) // seg_h)
                offset_x = (int(lw) - 18) // 2
                lx_centered = lx + offset_x
                for i in range(num_segments):
                    y_pos = ly + i * seg_h
                    if i == 0 and self.ladder_top:
                        self.screen.blit(self.ladder_top, (lx_centered, y_pos))
                    elif i == num_segments - 1 and self.ladder_bot:
                        self.screen.blit(self.ladder_bot, (lx_centered, y_pos))
                    else:
                        self.screen.blit(self.ladder_mid, (lx_centered, y_pos))
            else:
                # Fallback: vẽ thang bằng hình học
                pygame.draw.rect(self.screen, (139, 69, 19), (lx + 2, ly, 4, lh))
                pygame.draw.rect(self.screen, (139, 69, 19), (lx + lw - 6, ly, 4, lh))
                for rung_y in range(int(ly), int(ly + lh), 12):
                    pygame.draw.rect(self.screen, (100, 50, 10), (lx + 2, rung_y, lw - 4, 3))

        if self.door_pos:
            door_x = self.door_pos[0] - self.camera_offset[0]
            # Offset +16px downwards so the vortex visually touches the floor
            door_y = self.door_pos[1] + 64 - self.BGDoor.get_height() - self.camera_offset[1] + 16
            self.screen.blit(self.BGDoor, (door_x, door_y))

        for sprite in self.player_group:
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.screen.blit(flipped_image, (sprite.rect.x - self.camera_offset[0], sprite.rect.y - self.camera_offset[1]))

        for sprite in self.enemy_group:
            if sprite.alive or sprite.action == 3:
                sprite.draw(self.screen, self.camera_offset)

        self.health_bar.draw(self.screen)
        self.screen.blit(self.settings_icon, (self.settings_button.x, self.settings_button.y))
        self.screen.blit(self.pause_icon, (self.pause_button.x, self.pause_button.y))
        self.screen.blit(self.continue_icon, (self.continue_button.x, self.continue_button.y))

        if getattr(self, 'is_trapped', False):
            if hasattr(self, 'warning_popup') and self.warning_popup:
                # Vẽ pop-up cảnh báo ở góc trên chính giữa màn hình (y = 20px)
                popup_rect = self.warning_popup.get_rect(center=(self.screen_width // 2, 20 + self.warning_popup.get_height() // 2))
                self.screen.blit(self.warning_popup, popup_rect)
            else:
                warning_text = self.font_warning.render("Bạn đang bị rồng bao vây !", True, (255, 0, 0))
                text_rect = warning_text.get_rect(center=(self.screen_width // 2, 30))
                self.screen.blit(warning_text, text_rect)

        if self.paused:
            font = pygame.font.SysFont('Arial', 36, bold=True)
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)
