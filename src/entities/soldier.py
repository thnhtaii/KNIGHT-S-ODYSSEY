import pygame
import os
import math
import random
from src.entities.slime import Slime
from src.ai.algorithms import random_restart_hill_climbing_path, simulated_annealing_path, local_beam_path

class Soldier(Slime):
    def __init__(self, x, y, scale, speed, battle_base, move_area=None):
        super().__init__(x, y, scale, speed, battle_base, move_area)
        self.name = "soldier"
        self.scale = scale
        
        # Nạp hoạt ảnh Binh sĩ từ assets/sprites/boss
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        boss_dir = os.path.join(project_root, 'assets', 'sprites', 'boss')
        
        self.animation_list = []
        
        # Action 0: Idle
        idle_sheet = pygame.image.load(os.path.join(boss_dir, 'knight_idle.png')).convert_alpha()
        idle_frames = self.slice_sheet(idle_sheet, scale)
        self.animation_list.append(idle_frames)
        
        # Action 1: Walk
        walk_sheet = pygame.image.load(os.path.join(boss_dir, 'knight_walk.png')).convert_alpha()
        walk_frames = self.slice_sheet(walk_sheet, scale)
        self.animation_list.append(walk_frames)
        
        # Action 2: Hurt (Tái sử dụng Idle)
        self.animation_list.append(idle_frames.copy())
        
        # Action 3: Death (Tạo 10 frame placeholder để phục vụ việc xoay và mờ dần trong update_animation)
        self.animation_list.append(idle_frames.copy()[:10] if len(idle_frames) >= 10 else (idle_frames.copy() * 2)[:10])
        
        # Gán lại image và rect
        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.bottomleft = (x, y)
        
        # Khởi tạo đường đi và mục tiêu cho AI
        self.path = []
        self.path_index = 0
        self.last_goal_tile = None

    def slice_sheet(self, sheet, scale):
        w, h = sheet.get_size()
        if w == 750 and h == 750:
            frame_width = 150
            frame_height = 150
            cols = 5
            rows = 5
        else:
            frame_width = h
            frame_height = h
            cols = w // frame_width
            rows = 1
            
        frames = []
        for r in range(rows):
            for c in range(cols):
                rect = pygame.Rect(c * frame_width, r * frame_height, frame_width, frame_height)
                sub = sheet.subsurface(rect)
                mask = pygame.mask.from_surface(sub)
                if mask.count() > 0:
                    scaled_frame = pygame.transform.scale(sub, (int(frame_width * scale), int(frame_height * scale)))
                    frames.append(scaled_frame)
        return frames

    def update_animation(self):
        cooldown = 100
        
        # Xử lý hoạt ảnh Chết bằng xoay nghiêng 90 độ và mờ dần về 0
        if self.action == 3:
            total_death_frames = 10
            progress = self.frame_index / (total_death_frames - 1) if total_death_frames > 1 else 1.0
            
            # Lấy frame đứng yên Idle đầu tiên làm ảnh gốc xoay
            base_image = self.animation_list[0][0]
            
            # Xoay nghiêng: ngã về trước hoặc sau tùy theo hướng đối mặt self.flip
            angle = -90 * progress if self.flip else 90 * progress
            rotated_image = pygame.transform.rotate(base_image, angle)
            
            # Giảm độ mờ (alpha)
            alpha = int(255 * (1.0 - progress))
            rotated_image.set_alpha(alpha)
            
            self.image = rotated_image
            
            # Giữ nguyên tâm của rect để tránh nhân vật bị giật lệch vị trí khi xoay
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center
            
            # Vẫn áp dụng trọng lực khi ngã
            self.apply_gravity()
            
            if pygame.time.get_ticks() - self.update_time > cooldown:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= total_death_frames:
                    self.frame_index = total_death_frames - 1
                    self.death_animation_complete = True
        else:
            # Hoạt ảnh đi/đứng bình thường
            if self.frame_index >= len(self.animation_list[self.action]):
                self.frame_index = 0
                
            self.image = self.animation_list[self.action][self.frame_index]
            self.apply_gravity()
            
            if pygame.time.get_ticks() - self.update_time > cooldown:
                self.update_time = pygame.time.get_ticks()
                self.frame_index += 1
                if self.frame_index >= len(self.animation_list[self.action]):
                    self.frame_index = 0

    def update_hill_climb(self, player, grid, margin_data):
        if not self.alive:
            return
            
        current_tile = (self.rect.centerx // self.battle_base.tile_width,
                        self.rect.centery // self.battle_base.tile_height)
        goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                    player.rect.centery // self.battle_base.tile_height)
                    
        if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
            self.path = []
            return

        if not self.path or self.path_index >= len(self.path) or self._is_target_changed(goal_tile):
            self.path = random_restart_hill_climbing_path(current_tile, goal_tile, grid)
            self.path_index = 0
            self.last_goal_tile = goal_tile
            
        self.follow_path(margin_data)

    def update_simulated_annealing(self, player, grid, margin_data):
        if not self.alive:
            return
            
        current_tile = (self.rect.centerx // self.battle_base.tile_width,
                        self.rect.centery // self.battle_base.tile_height)
        goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                    player.rect.centery // self.battle_base.tile_height)
                    
        if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
            self.path = []
            return

        if not self.path or self.path_index >= len(self.path) or self._is_target_changed(goal_tile):
            self.path = simulated_annealing_path(current_tile, goal_tile, grid)
            self.path_index = 0
            self.last_goal_tile = goal_tile
            
        self.follow_path(margin_data)

    def update_local_beam(self, player, grid, margin_data):
        if not self.alive:
            return
            
        current_tile = (self.rect.centerx // self.battle_base.tile_width,
                        self.rect.centery // self.battle_base.tile_height)
        goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                    player.rect.centery // self.battle_base.tile_height)
                    
        if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
            self.path = []
            return

        if not self.path or self.path_index >= len(self.path) or self._is_target_changed(goal_tile):
            self.path = local_beam_path(current_tile, goal_tile, grid)
            self.path_index = 0
            self.last_goal_tile = goal_tile
            
        self.follow_path(margin_data)

    def follow_path(self, margin_data):
        if self.path and self.path_index < len(self.path):
            tx, ty = self.path[self.path_index]
            target_x = tx * self.battle_base.tile_width + self.battle_base.tile_width // 2
            
            if self.move_area and (target_x < self.move_area.left or target_x > self.move_area.right):
                return
                
            if 0 <= ty < self.battle_base.map_height and 0 <= tx < self.battle_base.map_width:
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
            
            # Action 1 là chạy/di chuyển, Action 0 là đứng yên
            self.update_action(1 if abs(self.rect.centerx - target_x) > self.speed else 0)
        else:
            self.update_action(0)
