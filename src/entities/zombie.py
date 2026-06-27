import pygame
import os
import math
from src.entities.slime import Slime

class Zombie(Slime):
    def __init__(self, x, y, scale, speed, battle_base, move_area=None):
        super().__init__(x, y, scale, speed, battle_base, move_area)
        self.name = "zombie"
        self.scale = scale
        self.health = 40  # Zombie trâu hơn Slime một chút
        
        # Nạp hoạt ảnh Zombie từ assets/sprites/zombie/zombie.png
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        zombie_sheet_path = os.path.join(project_root, 'assets', 'sprites', 'zombie', 'zombie.png')
        
        try:
            sheet = pygame.image.load(zombie_sheet_path).convert_alpha()
        except Exception as e:
            print(f"[ERROR] Failed to load zombie spritesheet: {e}")
            sheet = pygame.Surface((1024, 1024), pygame.SRCALPHA)
            sheet.fill((0, 255, 0, 128))

        self.animation_list = []
        
        # Action 0: Idle (Row 2 in sheet, 4 frames)
        self.animation_list.append(self.slice_sheet_row(sheet, scale, row=2, col_count=4))
        
        # Action 1: Walk (Row 0 in sheet, 8 frames)
        self.animation_list.append(self.slice_sheet_row(sheet, scale, row=0, col_count=8))
        
        # Action 2: Hurt (Row 3 in sheet, 4 frames)
        self.animation_list.append(self.slice_sheet_row(sheet, scale, row=3, col_count=4))
        
        # Action 3: Death (Row 4 in sheet, 5 frames)
        self.animation_list.append(self.slice_sheet_row(sheet, scale, row=4, col_count=5))
        
        # Action 4: Attack (Row 1 in sheet, 5 frames)
        self.animation_list.append(self.slice_sheet_row(sheet, scale, row=1, col_count=5))
        
        # Gán lại image và rect ban đầu
        self.image = self.animation_list[self.action][self.frame_index]
        # Định nghĩa kích thước hộp va chạm cố định (rộng 44, cao 60)
        # để Zombie có thể đi qua khe hẹp dưới bệ đỡ (khe hẹp cao 64px)
        self.rect = pygame.Rect(x, y - 60, 44, 60)
        
        # Biến điều khiển di chuyển AI
        self.bfs_path = []
        self.path_index = 0
        self.last_goal_tile = None
        self.is_attacking = False

        # Các biến hỗ trợ And-Or Search, Belief State và Belief Goal
        self.andor_plan = None
        self.belief_states = []
        self.belief_actions = []
        self.belief_action_index = 0
        self.is_calibrated = False
        self.target_pos = None

    def slice_sheet_row(self, sheet, scale, row, col_count):
        # Chiều rộng khung hình thực tế của từng hàng trong zombie.png để không bị cắt nửa hoặc lộ ảnh khác
        row_widths = [128, 170, 160, 170, 204]
        frame_width = row_widths[row]
        row_starts = [10, 220, 430, 625, 830]
        row_height = 190
        
        y_start = row_starts[row]
        frames = []
        for c in range(col_count):
            rect = pygame.Rect(c * frame_width, y_start, frame_width, row_height)
            sub = sheet.subsurface(rect)
            
            # Không sử dụng get_bounding_rect để tránh làm lệch trọng tâm/kích thước chân của hoạt ảnh
            scaled_frame = pygame.transform.scale(sub, (int(frame_width * scale), int(row_height * scale)))
            frames.append(scaled_frame)
        return frames

    def try_attack_player(self, player):
        current_time = pygame.time.get_ticks()

        if self.rect.colliderect(player.rect):
            if current_time - getattr(player, 'last_hurt_time', 0) > 1000 and \
               current_time - self.last_attack_time > self.attack_cooldown:
                
                # Gây sát thương
                player.health -= 15  # Zombie cắn đau hơn (15 sát thương)
                player.is_hurt = True
                player.update_action(8)  # Hurt animation
                player.last_hurt_time = current_time

                print(f"[{self.name}] Zombie tấn công! Knight còn {player.health} máu")
                self.last_attack_time = current_time
                from src.components.ai_stats_tracker import AIStatsTracker
                AIStatsTracker.log_attack(self.name, 15)
                
                # Kích hoạt hoạt ảnh tấn công (Action 4)
                self.action = 4
                self.frame_index = 0
                self.update_time = current_time

                if player.health <= 0:
                    player.check_alive()

    def move(self):
        if not self.alive:
            return
        dx = self.speed * self.direction
        dy = 0
        self.vel_y += 0.75
        if self.vel_y > 10:
            self.vel_y = 10
        dy += self.vel_y
        temp_rect = self.rect.move(dx, dy)
        if self.move_area and not self.move_area.contains(temp_rect):
            if temp_rect.left < self.move_area.left or temp_rect.right > self.move_area.right:
                self.direction *= -1
                dx = self.speed * self.direction
            temp_rect = self.rect.move(dx, dy)
        
        prev_x = self.rect.x
        self.rect.x += dx
        self.check_collision('horizontal', dx)
        if self.rect.x == prev_x:
            self.direction *= -1
            self.flip = (self.direction == -1)
            
        self.rect.y += dy
        self.check_collision('vertical', dy)
        
        if self.move_area:
            if self.rect.left < self.move_area.left:
                self.rect.left = self.move_area.left
                self.direction *= -1
                self.flip = (self.direction == -1)
            if self.rect.right > self.move_area.right:
                self.rect.right = self.move_area.right
                self.direction *= -1
                self.flip = (self.direction == -1)

    def update_bfs(self, player, grid, margin_data):
        if not self.alive:
            return

        # Khoảng cách phát hiện (300 pixel)
        detection_range = 300
        dist = abs(self.rect.centerx - player.rect.centerx)

        if dist < detection_range:
            self.follow_player = True
            
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                         player.rect.centery // self.battle_base.tile_height)

            # Đảm bảo các ô nằm trong phạm vi bản đồ
            if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                    0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
                self.bfs_path = []
                return

            # Tìm đường BFS mới nếu không có đường hoặc mục tiêu thay đổi
            if not self.bfs_path or self.path_index >= len(self.bfs_path) or self._is_target_changed(goal_tile):
                from src.ai.algorithms import bfs_path
                self.bfs_path = bfs_path(current_tile, goal_tile, grid)
                self.path_index = 0
                self.last_goal_tile = goal_tile
                from src.components.ai_stats_tracker import AIStatsTracker
                AIStatsTracker.log_pathfinding(self.name)

            if self.bfs_path and self.path_index < len(self.bfs_path):
                tx, ty = self.bfs_path[self.path_index]
                target_x = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2

                if self.move_area:
                    target_x = max(self.move_area.left, min(target_x, self.move_area.right))

                if (0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width):
                    margin_index = ty * self.battle_base.map_width + tx
                    if margin_index < len(margin_data) and margin_data[margin_index] != 0:
                        self.direction *= -1
                        self.rect.x += self.direction * self.speed
                    else:
                        if abs(self.rect.centerx - target_x) > self.speed:
                            prev_x = self.rect.x
                            if self.rect.centerx < target_x:
                                self.rect.x += self.speed
                                self.flip = False
                                self.direction = 1
                            else:
                                self.rect.x -= self.speed
                                self.flip = True
                                self.direction = -1
                            self.check_collision('horizontal', self.speed * self.direction)
                            if self.rect.x == prev_x:
                                self.path_index += 1
                        else:
                            self.rect.centerx = target_x
                            self.path_index += 1
                self.update_action(1 if self.in_air or abs(self.rect.centerx - target_x) > self.speed else 0)
        else:
            # Nếu người chơi ngoài tầm, đi tuần tra qua lại (đi bộ loanh quanh)
            self.follow_player = False
            self.bfs_path = []
            self.path_index = 0
            self.move()
            self.flip = (self.direction == -1)
            self.update_action(1)  # Chạy hoạt ảnh đi bộ

    def update_andor(self, player, grid, margin_data):
        if not self.alive:
            return

        detection_range = 300
        dist = abs(self.rect.centerx - player.rect.centerx)

        if dist < detection_range:
            self.follow_player = True
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                         player.rect.centery // self.battle_base.tile_height)

            if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                    0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
                self.andor_plan = None
                self.current_step_target_tile = None
                return

            # Nếu chưa có plan hoặc mục tiêu thay đổi, tính toán And-Or plan mới
            if not self.andor_plan or self.last_goal_tile != goal_tile:
                from src.ai.algorithms import and_or_graph_search
                self.andor_plan = and_or_graph_search(current_tile, goal_tile, grid)
                self.last_goal_tile = goal_tile
                self.current_step_target_tile = None
                from src.components.ai_stats_tracker import AIStatsTracker
                AIStatsTracker.log_pathfinding(self.name)
                
            if self.andor_plan and len(self.andor_plan) == 2:
                action, plans_dict = self.andor_plan
                
                # Nếu chưa xác định mục tiêu bước hiện tại, tính toán ngẫu nhiên 1 lần
                if not getattr(self, 'current_step_target_tile', None):
                    import random
                    r = random.random()
                    intended = action
                    side = (action[1], action[0])
                    
                    actual_action = intended if r < 0.7 else side
                    
                    tx = current_tile[0] + actual_action[0]
                    ty = current_tile[1] + actual_action[1]
                    
                    if 0 <= tx < len(grid[0]) and 0 <= ty < len(grid) and grid[ty][tx] == 0:
                        self.current_step_target_tile = (tx, ty)
                    else:
                        self.current_step_target_tile = current_tile
                
                next_tile = self.current_step_target_tile
                target_x = next_tile[0] * self.battle_base.tile_width + self.battle_base.tile_width // 2
                
                if self.move_area:
                    target_x = max(self.move_area.left, min(target_x, self.move_area.right))
                    
                if abs(self.rect.centerx - target_x) > self.speed:
                    prev_x = self.rect.x
                    if self.rect.centerx < target_x:
                        self.rect.x += self.speed
                        self.flip = False
                        self.direction = 1
                    else:
                        self.rect.x -= self.speed
                        self.flip = True
                        self.direction = -1
                    self.check_collision('horizontal', self.speed * self.direction)
                    if self.rect.x == prev_x:
                        self.andor_plan = None
                        self.current_step_target_tile = None
                else:
                    self.rect.centerx = target_x
                    # Đã đến ô tiếp theo, cập nhật plan tiếp theo
                    if isinstance(plans_dict, dict) and next_tile in plans_dict:
                        self.andor_plan = plans_dict[next_tile]
                    else:
                        self.andor_plan = None
                    self.current_step_target_tile = None
                
                self.update_action(1 if self.in_air or abs(self.rect.centerx - target_x) > self.speed else 0)
            else:
                self.update_action(0)
                self.current_step_target_tile = None
        else:
            self.follow_player = False
            self.andor_plan = None
            self.move()
            self.flip = (self.direction == -1)
            self.update_action(1)

    def update_belief_state(self, player, grid, margin_data):
        if not self.alive:
            return

        current_tile = (self.rect.centerx // self.battle_base.tile_width,
                        self.rect.centery // self.battle_base.tile_height)
        goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                     player.rect.centery // self.battle_base.tile_height)

        if not self.is_calibrated:
            # Khởi tạo Belief State ban đầu gồm 2 vị trí nghi ngờ của zombie
            if not self.belief_states:
                s1 = current_tile
                s2 = (current_tile[0] - 2, current_tile[1])
                if s2[0] < 0 or grid[s2[1]][s2[0]] != 0:
                    s2 = (current_tile[0] + 2, current_tile[1])
                if s2[0] >= len(grid[0]) or grid[s2[1]][s2[0]] != 0:
                    s2 = current_tile
                
                self.belief_states = [s1, s2]
                
                from src.ai.algorithms import belief_a_star
                self.belief_actions = belief_a_star(s1, s2, goal_tile, grid)
                self.belief_action_index = 0
                from src.components.ai_stats_tracker import AIStatsTracker
                AIStatsTracker.log_pathfinding(self.name)

            # Thực thi chuỗi hành động định vị
            if self.belief_actions and self.belief_action_index < len(self.belief_actions):
                action = self.belief_actions[self.belief_action_index]
                
                from src.ai.algorithms import result
                ns1 = result(self.belief_states[0], action, grid)
                ns2 = result(self.belief_states[1], action, grid)
                self.belief_states = list(set([ns1, ns2]))
                
                if len(self.belief_states) == 1:
                    self.is_calibrated = True

                target_x = ns1[0] * self.battle_base.tile_width + self.battle_base.tile_width // 2
                if self.move_area:
                    target_x = max(self.move_area.left, min(target_x, self.move_area.right))
                if abs(self.rect.centerx - target_x) > self.speed:
                    prev_x = self.rect.x
                    if self.rect.centerx < target_x:
                        self.rect.x += self.speed
                        self.flip = False
                        self.direction = 1
                    else:
                        self.rect.x -= self.speed
                        self.flip = True
                        self.direction = -1
                    self.check_collision('horizontal', self.speed * self.direction)
                    if self.rect.x == prev_x:
                        self.belief_action_index += 1
                else:
                    self.rect.centerx = target_x
                    self.belief_action_index += 1
                self.update_action(1)
            else:
                self.is_calibrated = True
                self.belief_states = [current_tile]
        else:
            self.belief_states = [current_tile]
            self.update_bfs(player, grid, margin_data)

    def update_belief_state_and_goal(self, player, grid, margin_data):
        if not self.alive:
            return

        current_tile = (self.rect.centerx // self.battle_base.tile_width,
                        self.rect.centery // self.battle_base.tile_height)
        
        # Lấy tập hợp các ô nghi ngờ vị trí của Player từ BattleLevel4
        player_beliefs = getattr(self.battle_base, 'player_beliefs', [])
        if not player_beliefs:
            player_beliefs = [(player.rect.centerx // self.battle_base.tile_width,
                               player.rect.centery // self.battle_base.tile_height)]
            
        self.belief_states = list(player_beliefs)

        # Tìm chuỗi phím di chuyển ngắn nhất để zombie đến bất kỳ ô nào trong player_beliefs
        from src.ai.algorithms import belief_a_star_goals
        self.belief_actions = belief_a_star_goals(current_tile, current_tile, self.belief_states, grid)
        from src.components.ai_stats_tracker import AIStatsTracker
        AIStatsTracker.log_pathfinding(self.name)
        
        if self.belief_actions:
            action = self.belief_actions[0]
            tx = current_tile[0] + action[0]
            ty = current_tile[1] + action[1]
            
            target_x = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2
            
            if self.move_area:
                target_x = max(self.move_area.left, min(target_x, self.move_area.right))
            if abs(self.rect.centerx - target_x) > self.speed:
                prev_x = self.rect.x
                if self.rect.centerx < target_x:
                    self.rect.x += self.speed
                    self.flip = False
                    self.direction = 1
                else:
                    self.rect.x -= self.speed
                    self.flip = True
                    self.direction = -1
                self.check_collision('horizontal', self.speed * self.direction)
                if self.rect.x == prev_x:
                    self.belief_actions = []
            else:
                self.rect.centerx = target_x
            self.update_action(1)
        else:
            self.update_action(0)

    def draw_belief_state(self, screen, camera_offset):
        if not self.alive or not self.belief_states:
            return
            
        if "belief_state_and_goal" not in self.name and "Belief + Goal" not in self.name and getattr(self, 'algo', '') != "belief_state_and_goal":
            return
            
        color = (255, 100, 0, 90) # Cam mờ cho vị trí player nghi ngờ
            
        for tile in self.belief_states:
            tx, ty = tile
            rect_x = tx * self.battle_base.tile_width - camera_offset[0]
            rect_y = ty * self.battle_base.tile_height - camera_offset[1]
            
            surf = pygame.Surface((self.battle_base.tile_width, self.battle_base.tile_height), pygame.SRCALPHA)
            surf.fill(color)
            screen.blit(surf, (rect_x, rect_y))
            
            pygame.draw.rect(screen, (color[0], color[1], color[2], 200),
                             (rect_x, rect_y, self.battle_base.tile_width, self.battle_base.tile_height), 1)

    def update_animation(self):
        cooldown = 100
        
        if self.frame_index >= len(self.animation_list[self.action]):
            self.frame_index = 0
            
        self.image = self.animation_list[self.action][self.frame_index]

        self.apply_gravity()
        
        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:  # Death completed
                    self.frame_index = len(self.animation_list[self.action]) - 1
                    self.death_animation_complete = True
                elif self.action == 4:  # Attack completed
                    # Nếu vẫn tiếp cận và người chơi còn sống, đứng giữ nguyên đòn tấn công (giơ tay)
                    player = getattr(self.battle_base, 'player', None)
                    if player and self.rect.colliderect(player.rect) and player.alive:
                        self.frame_index = len(self.animation_list[self.action]) - 1
                    else:
                        self.frame_index = 0
                        self.update_action(0)  # Quay lại Idle
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        # Chỉ khóa hành động khi đang tấn công (action == 4) và vẫn va chạm với người chơi còn sống
        player = getattr(self.battle_base, 'player', None)
        is_touching = player and self.rect.colliderect(player.rect) and player.alive
        if self.action == 4 and is_touching and new_action not in [0, 2, 3]:
            return
        super().update_action(new_action)

    def check_collision(self, direction, move_value):
        tile_width = self.battle_base.tile_width
        tile_height = self.battle_base.tile_height
        layer = self.battle_base.tile_layers[1]
        map_width = self.battle_base.map_width
        col_left = max(0, (self.rect.left - tile_width) // tile_width)
        col_right = min(self.battle_base.map_width - 1, (self.rect.right + tile_width) // tile_width)
        row_top = max(0, (self.rect.top - tile_height) // tile_height)
        row_bottom = min(self.battle_base.map_height - 1, (self.rect.bottom + tile_height) // tile_height)
        for row in range(row_top, row_bottom + 1):
            for col in range(col_left, col_right + 1):
                idx = row * map_width + col
                if idx < len(layer):
                    tile = layer[idx]
                    if tile > 0:
                        tile_rect = pygame.Rect(col * tile_width, row * tile_height, tile_width, tile_height)
                        if self.rect.colliderect(tile_rect):
                            if direction == 'horizontal':
                                if move_value > 0:
                                    self.rect.right = tile_rect.left
                                elif move_value < 0:
                                    self.rect.left = tile_rect.right
                            elif direction == 'vertical':
                                if move_value > 0:
                                    # Chỉ tiếp đất nếu chân thực sự nằm trên hoặc sát bề mặt trên của gạch trước khi di chuyển
                                    if self.rect.bottom - move_value <= tile_rect.top + 6:
                                        self.rect.bottom = tile_rect.top
                                        self.vel_y = 0
                                        self.in_air = False
                                elif move_value < 0:
                                    self.rect.top = tile_rect.bottom
                                    self.vel_y = 0
