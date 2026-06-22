import pygame
import os
from src.ai.algorithms import bfs_path, dfs_path, ucs_path, greedy_path, hill_climb_step, backtracking_path, q_learning_train, q_learning_step, and_or_search_probabilistic
import random

class Slime(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, battle_base, move_area=None, custom_img_path=None):
        pygame.sprite.Sprite.__init__(self)
        self.alive = True
        self.speed = speed
        self.direction = -1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0
        self.update_time = pygame.time.get_ticks()
        self.health = 30  # Giữ để tương thích, nhưng không dùng
        self.battle_base = battle_base
        self.move_area = move_area
        self.name = "slime_normal"
        self.q_table = None
        self.andor_path = []
        self.andor_index = 0
        self.bfs_path = []
        self.path_index = 0
        self.follow_player = False
        self.last_goal_tile = None
        self.frame_counts = {
            'Idle': 7,
            'Jump': 6,
            'Hurt': 11,
            'Death': 14
        }
        self.q_table_trained = False
        self.hill_stuck_counter = 0
        self.update_counter = 0
        self.is_attacking = False
        self.last_attack_time = 0
        self.attack_cooldown = 2000
        self.death_animation_complete = False  # Biến mới để theo dõi trạng thái animation Death

        self.custom_image = None
        if custom_img_path:
            try:
                loaded_img = pygame.image.load(custom_img_path).convert_alpha()
                w_orig, h_orig = loaded_img.get_size()
                h_new = 36
                w_new = int(h_new * w_orig / h_orig)
                self.custom_image = pygame.transform.scale(loaded_img, (w_new, h_new))
            except Exception as e:
                print(f"[ERROR] Failed to load custom slime image: {e}")

        self.animation_types = ['Idle', 'Jump', 'Hurt', 'Death']
        for animation in self.animation_types:
            temp_list = []
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            sprite_path = os.path.join(project_root, 'assets', 'sprites', 'slime', animation.lower())
            frame_count = self.frame_counts[animation]
            for i in range(frame_count):
                img_path = os.path.join(sprite_path, f"{animation.capitalize()}_{i}.png")
                if animation.lower() == 'jump':
                    img_path = os.path.join(sprite_path, f"Jump_Land_{i}.png")
                if os.path.exists(img_path):
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
                    temp_list.append(img)
            self.animation_list.append(temp_list if temp_list else [pygame.Surface((32, 32))])

        if self.custom_image:
            self.image = self.custom_image
        else:
            self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)

    def _is_target_changed(self, new_goal_tile):
        if not hasattr(self, 'last_goal_tile'):
            return True
        return abs(new_goal_tile[0] - self.last_goal_tile[0]) > 1 or abs(new_goal_tile[1] - self.last_goal_tile[1]) > 1
    
    def try_attack_player(self, player):
        current_time = pygame.time.get_ticks()

        if self.rect.colliderect(player.rect):
            if current_time - getattr(player, 'last_hurt_time', 0) > 1000 and \
            current_time - self.last_attack_time > self.attack_cooldown:

                # Gây sát thương
                player.health -= 10
                player.is_hurt = True
                player.update_action(8)  # Hurt animation
                player.last_hurt_time = current_time

                print(f"[{self.name}] Slime tấn công! Knight còn {player.health} máu")

                self.last_attack_time = current_time

                if player.health <= 0:
                    player.check_alive()

    def update_bfs(self, player, grid, margin_data):
        if not self.alive:
            return

        # Kiểm tra khoảng cách đến người chơi
        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            self.bfs_path = []
            self.path_index = 0
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            # Kiểm tra tile nằm trong bản đồ trước khi tìm đường
            if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                    0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
                print(f"[BFS] Knight rơi khỏi bản đồ! goal_tile={goal_tile}, current_tile={current_tile}")
                self.bfs_path = []
                return

            if not self.bfs_path or self.path_index >= len(self.bfs_path) or self._is_target_changed(goal_tile):
                self.bfs_path = bfs_path(current_tile, goal_tile, grid)
                self.path_index = 0
                self.last_goal_tile = goal_tile

            if self.bfs_path and self.path_index < len(self.bfs_path):
                tx, ty = self.bfs_path[self.path_index]
                target_x = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2
                if self.move_area and (target_x < self.move_area.left or target_x > self.move_area.right):
                    return

                if (0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width):
                    margin_index = ty * self.battle_base.map_width + tx
                    if margin_index < len(margin_data) and margin_data[margin_index] != 0:
                        self.direction *= -1
                        self.rect.x += self.direction * self.speed
                        print(f"[DEBUG] Slime at {self.rect.centerx}, {self.rect.centery} hit margin at {tx}, {ty}")
                    else:
                        if abs(self.rect.centerx - target_x) > self.speed:
                            if self.rect.centerx < target_x:
                                self.rect.x += self.speed
                                self.flip = False
                                self.direction = 1
                            else:
                                self.rect.x -= self.speed
                                self.flip = True
                                self.direction = -1
                            self.check_collision('horizontal', self.speed * self.direction)
                        else:
                            self.path_index += 1
                self.update_action(1 if self.in_air or abs(self.rect.centerx - target_x) > self.speed else 0)

    def update_dfs(self, player, grid, margin_data):
        """Di chuyển Slime theo thuật toán DFS (Early Goal Test)"""
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            self.bfs_path = []
            self.path_index = 0
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                    0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
                self.bfs_path = []
                return

            if not self.bfs_path or self.path_index >= len(self.bfs_path) or self._is_target_changed(goal_tile):
                self.bfs_path = dfs_path(current_tile, goal_tile, grid)
                self.path_index = 0
                self.last_goal_tile = goal_tile

            if self.bfs_path and self.path_index < len(self.bfs_path):
                tx, ty = self.bfs_path[self.path_index]
                target_x = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2
                if self.move_area and (target_x < self.move_area.left or target_x > self.move_area.right):
                    return

                if (0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width):
                    margin_index = ty * self.battle_base.map_width + tx
                    if margin_index < len(margin_data) and margin_data[margin_index] != 0:
                        self.direction *= -1
                        self.rect.x += self.direction * self.speed
                    else:
                        if abs(self.rect.centerx - target_x) > self.speed:
                            if self.rect.centerx < target_x:
                                self.rect.x += self.speed
                                self.flip = False
                                self.direction = 1
                            else:
                                self.rect.x -= self.speed
                                self.flip = True
                                self.direction = -1
                            self.check_collision('horizontal', self.speed * self.direction)
                        else:
                            self.path_index += 1
                self.update_action(1 if self.in_air or abs(self.rect.centerx - target_x) > self.speed else 0)

    def update_ucs(self, player, grid, margin_data):
        """Di chuyển Slime theo thuật toán UCS (Uniform Cost Search)"""
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            self.bfs_path = []
            self.path_index = 0
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                    0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
                self.bfs_path = []
                return

            if not self.bfs_path or self.path_index >= len(self.bfs_path) or self._is_target_changed(goal_tile):
                self.bfs_path = ucs_path(current_tile, goal_tile, grid)
                self.path_index = 0
                self.last_goal_tile = goal_tile

            if self.bfs_path and self.path_index < len(self.bfs_path):
                tx, ty = self.bfs_path[self.path_index]
                target_x = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2
                if self.move_area and (target_x < self.move_area.left or target_x > self.move_area.right):
                    return

                if (0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width):
                    margin_index = ty * self.battle_base.map_width + tx
                    if margin_index < len(margin_data) and margin_data[margin_index] != 0:
                        self.direction *= -1
                        self.rect.x += self.direction * self.speed
                    else:
                        if abs(self.rect.centerx - target_x) > self.speed:
                            if self.rect.centerx < target_x:
                                self.rect.x += self.speed
                                self.flip = False
                                self.direction = 1
                            else:
                                self.rect.x -= self.speed
                                self.flip = True
                                self.direction = -1
                            self.check_collision('horizontal', self.speed * self.direction)
                        else:
                            self.path_index += 1
                self.update_action(1 if self.in_air or abs(self.rect.centerx - target_x) > self.speed else 0)

    def update_greedy(self, player, grid, margin_data):
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            if not self.bfs_path or self.path_index >= len(self.bfs_path) or self._is_target_changed(goal_tile):
                self.bfs_path = greedy_path(current_tile, goal_tile, grid)
                self.path_index = 0
                self.last_goal_tile = goal_tile

            if self.bfs_path and self.path_index < len(self.bfs_path):
                tx, ty = self.bfs_path[self.path_index]
                target_x = tx * self.battle_base.tile_width
                if self.move_area and (target_x < self.move_area.left or target_x > self.move_area.right):
                    return

                if (0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width):
                    margin_index = ty * self.battle_base.map_width + tx
                    if margin_index < len(margin_data) and margin_data[margin_index] != 0:
                        self.direction *= -1
                        self.rect.x += self.direction * self.speed
                    else:
                        if abs(self.rect.centerx - target_x) > 2:
                            if self.rect.centerx < target_x:
                                self.rect.x += self.speed
                                self.flip = False
                            elif self.rect.centerx > target_x:
                                self.rect.x -= self.speed
                                self.flip = True
                        else:
                            self.path_index += 1

    def update_hill_climb(self, player, grid, margin_data):
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            if not hasattr(self, 'hill_stuck_counter'):
                self.hill_stuck_counter = 0

            next_tile = hill_climb_step(current_tile, goal_tile, grid)
            current_h = abs(current_tile[0] - goal_tile[0]) + abs(current_tile[1] - goal_tile[1])
            next_h = abs(next_tile[0] - goal_tile[0]) + abs(next_tile[1] - goal_tile[1])

            if next_h >= current_h:
                self.hill_stuck_counter += 1
            else:
                self.hill_stuck_counter = 0

            if self.hill_stuck_counter > 10:
                valid_moves = []
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = current_tile[0] + dx, current_tile[1] + dy
                    if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 0:
                        valid_moves.append((nx, ny))
                if valid_moves:
                    next_tile = random.choice(valid_moves)
                self.hill_stuck_counter = 0

            tx_center = next_tile[0] * self.battle_base.tile_width + self.battle_base.tile_width // 2

            if self.move_area and (tx_center < self.move_area.left or tx_center > self.move_area.right):
                return

            if abs(self.rect.centerx - tx_center) > self.speed:
                if self.rect.centerx < tx_center:
                    self.rect.x += self.speed
                    self.flip = False
                    self.direction = 1
                else:
                    self.rect.x -= self.speed
                    self.flip = True
                    self.direction = -1
                self.check_collision('horizontal', self.speed * self.direction)

            self.update_action(1 if self.in_air or abs(self.rect.centerx - tx_center) > self.speed else 0)

    def update_backtracking(self, player, grid, margin_data):
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            if not self.bfs_path or self.path_index >= len(self.bfs_path):
                full_path = backtracking_path(current_tile, goal_tile, grid)

                if self.move_area:
                    filtered_path = []
                    for (tx, ty) in full_path:
                        tx_center = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2
                        if self.move_area.left <= tx_center <= self.move_area.right:
                            filtered_path.append((tx, ty))
                    self.bfs_path = filtered_path
                else:
                    self.bfs_path = full_path

                self.path_index = 0

            if self.bfs_path and self.path_index < len(self.bfs_path):
                tx, ty = self.bfs_path[self.path_index]
                target_x = tx * self.battle_base.tile_width

                if (0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width):
                    margin_index = ty * self.battle_base.map_width + tx
                    if margin_index < len(margin_data) and margin_data[margin_index] != 0:
                        self.direction *= -1
                        self.rect.x += self.direction * self.speed
                    else:
                        if abs(self.rect.centerx - target_x) > 2:
                            if self.rect.centerx < target_x:
                                self.rect.x += self.speed
                                self.flip = False
                            elif self.rect.centerx > target_x:
                                self.rect.x -= self.speed
                                self.flip = True
                        else:
                            self.path_index += 1

    def update_q_learning(self, player, grid, margin_data):
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            return

        current_tile = (self.rect.centerx // self.battle_base.tile_width,
                        self.rect.centery // self.battle_base.tile_height)
        goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                    player.rect.centery // self.battle_base.tile_height)

        if not hasattr(self, 'last_goal_tile') or self.last_goal_tile != goal_tile:
            self.q_table = q_learning_train(grid, current_tile, goal_tile, episodes=100)
            self.q_table_trained = True
            self.last_goal_tile = goal_tile

        next_tile = q_learning_step(self.q_table, current_tile)
        target_x = next_tile[0] * self.battle_base.tile_width + self.battle_base.tile_width // 2

        if self.move_area:
            if target_x < self.move_area.left or target_x > self.move_area.right:
                return

        if abs(self.rect.centerx - target_x) > self.speed:
            if self.rect.centerx < target_x:
                self.rect.x += self.speed
                self.flip = False
                self.direction = 1
            else:
                self.rect.x -= self.speed
                self.flip = True
                self.direction = -1
            self.check_collision('horizontal', self.speed * self.direction)

        self.update_action(1 if self.in_air or abs(self.rect.centerx - target_x) > self.speed else 0)

    def _is_goal_changed(self, new_goal_tile):
        if self.last_goal_tile is None:
            return True
        dx = abs(new_goal_tile[0] - self.last_goal_tile[0])
        dy = abs(new_goal_tile[1] - self.last_goal_tile[1])
        return dx > 1 or dy > 1

    def update_andor(self, player, grid, margin_data):
        if not self.alive:
            return

        if abs(self.rect.centerx - player.rect.centerx) < 150:
            self.follow_player = True
        else:
            self.follow_player = False
            self.andor_path = []
            self.andor_index = 0
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                        player.rect.centery // self.battle_base.tile_height)

            if not self.andor_path or self.andor_index >= len(self.andor_path) or self._is_goal_changed(goal_tile):
                self.andor_path = and_or_search_probabilistic(current_tile, goal_tile, grid)
                self.andor_index = 0
                self.last_goal_tile = goal_tile

            if self.andor_path and self.andor_index < len(self.andor_path):
                next_tile = self.andor_path[self.andor_index]
                target_x = next_tile[0] * self.battle_base.tile_width + self.battle_base.tile_width // 2

                if self.move_area and (target_x < self.move_area.left or target_x > self.move_area.right):
                    return

                if abs(self.rect.centerx - target_x) > self.speed:
                    if self.rect.centerx < target_x:
                        self.rect.x += self.speed
                        self.flip = False
                    else:
                        self.rect.x -= self.speed
                        self.flip = True
                    self.check_collision('horizontal', self.speed * self.direction)
                else:
                    self.andor_index += 1

            self.update_action(1 if self.in_air or self.andor_index < len(self.andor_path) else 0)

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
        self.rect.x += dx
        self.check_collision('horizontal', dx)
        self.rect.y += dy
        self.check_collision('vertical', dy)
        if self.move_area:
            if self.rect.left < self.move_area.left:
                self.rect.left = self.move_area.left
                self.direction *= -1
                self.flip = not self.flip
            if self.rect.right > self.move_area.right:
                self.rect.right = self.move_area.right
                self.direction *= -1
                self.flip = not self.flip
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.vel_y = 0
            self.in_air = False

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
                                self.rect.bottom = tile_rect.top
                                self.vel_y = 0
                                self.in_air = False
                            elif move_value < 0:
                                self.rect.top = tile_rect.bottom
                                self.vel_y = 0

    def update_animation(self):
        cooldown = 100
        old_bottomleft = self.rect.bottomleft
        if self.custom_image and self.action in [0, 1]:  # Idle or Jump
            self.image = self.custom_image
        else:
            self.image = self.animation_list[self.action][self.frame_index]
            
        self.rect = self.image.get_rect()
        self.rect.bottomleft = old_bottomleft

        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:  # Death
                    self.frame_index = len(self.animation_list[self.action]) - 1
                    self.death_animation_complete = True  # Đánh dấu animation Death hoàn thành
                    print(f"[Slime] {self.name} completed Death animation")
                else:
                    self.frame_index = 0
            print(f"[Slime] {self.name} action={self.action}, frame={self.frame_index}")

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.death_animation_complete = False  # Reset khi chuyển hành động
            print(f"[Slime] {self.name} updated action to {new_action}")

    def check_alive(self):
        self.health = 0
        self.speed = 0
        self.alive = False
        self.update_action(3)  # Death
        print(f"[Slime] {self.name} triggered check_alive, switching to Death")

    def draw(self, screen):
        if self.alive or self.action == 3:  # Vẽ cả khi đang trong trạng thái Death
            screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
            print(f"[Slime] {self.name} drawn at {self.rect.x}, {self.rect.y}, action={self.action}")