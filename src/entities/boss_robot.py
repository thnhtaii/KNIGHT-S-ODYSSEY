import pygame
import os
import math
import numpy as np
import pygame.surfarray as surfarray

class BossRobot(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, battle_base):
        super().__init__()
        self.alive = True
        self.speed = speed
        self.original_speed = speed
        self.scale = scale
        self.direction = -1  # Starts facing left (towards player)
        self.flip = True
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0: Idle, 1: Walk, 2: Attack, 3: Block/Defense, 4: Death
        self.update_time = pygame.time.get_ticks()
        self.health = 100
        self.battle_base = battle_base
        self.name = "boss_robot"
        
        self.animation_types = ['walk', 'walk', 'attack', 'defense', 'walk']  # Map actions to sheet files
        self.load_sprites(scale)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

        # Scan down to find the floor row
        col = int(x) // battle_base.tile_width
        row = int(y) // battle_base.tile_height
        layer_width = battle_base.map_width
        
        while row < battle_base.map_height:
            tile_id = battle_base.tile_layers[1][row * layer_width + col]
            if tile_id > 0:
                break
            row += 1
            
        self.target_grid_pos = (col, row - 1)
        self.feet_offset = 0
        
        aligned_x = col * battle_base.tile_width + battle_base.tile_width // 2 - self.width // 2
        aligned_y = row * battle_base.tile_height - self.height + self.feet_offset
        
        min_x = battle_base.tile_width
        max_x = battle_base.map_width * battle_base.tile_width - battle_base.tile_width - self.width
        aligned_x = max(min_x, min(aligned_x, max_x))
        
        self.current_px_pos = [float(aligned_x), float(aligned_y)]
        self.rect.x = int(aligned_x)
        self.rect.y = int(aligned_y)

        # Skill cooldown tracking times
        self.last_combo_cooldown_time = 0
        self.last_shield_cooldown_time = 0
        self.last_normal_cooldown_time = 0

        # State flags
        self.charge_active = False
        self.charge_start_time = 0
        self.shield_active = False
        self.shield_start_time = 0
        self.combo_active = False
        self.combo_start_time = 0
        self.combo_hits_done = 0

    @property
    def combo_cooldown(self):
        now = pygame.time.get_ticks()
        max_cd = 6000 if self.health < 30 else 8000
        elapsed = now - self.last_combo_cooldown_time
        return max(0.0, (max_cd - elapsed) / 1000.0)

    @property
    def shield_cooldown(self):
        now = pygame.time.get_ticks()
        max_cd = 5000 if self.health < 30 else 8000
        elapsed = now - self.last_shield_cooldown_time
        return max(0.0, (max_cd - elapsed) / 1000.0)

    @property
    def normal_cooldown(self):
        now = pygame.time.get_ticks()
        max_cd = 4000
        elapsed = now - self.last_normal_cooldown_time
        return max(0.0, (max_cd - elapsed) / 1000.0)

    def load_sprites(self, scale):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        sprite_dir = os.path.join(project_root, 'assets', 'sprites', 'robot')
        
        frame_w, frame_h = 567, 560
        start_y = 200
        cols, rows = 5, 2
        self.animations_by_color = {'blue': [], 'yellow': [], 'red': []}
        colors = ['blue', 'yellow', 'red']
        
        for color in colors:
            sheet_files = {
                'walk': f'robot_walk_{color}.png',
                'attack': f'robot_attack_{color}.png',
                'defense': f'robot_defense_{color}.png'
            }
            
            actions_map = ['walk', 'walk', 'attack', 'defense', 'walk']
            
            for act_name in actions_map:
                temp_list = []
                filename = sheet_files.get(act_name, f'robot_walk_{color}.png')
                img_path = os.path.join(sprite_dir, filename)
                
                if os.path.exists(img_path):
                    sheet = pygame.image.load(img_path).convert_alpha()
                    current_frame_w = sheet.get_width() // cols
                    for row in range(rows):
                        for col in range(cols):
                            clip_w = current_frame_w - 35
                            rect = pygame.Rect(col * current_frame_w, start_y + row * frame_h, clip_w, frame_h)
                            frame = sheet.subsurface(rect).copy()
                            
                            rgb = surfarray.pixels3d(frame).astype(np.int32)
                            alpha = surfarray.pixels_alpha(frame)
                            is_gray = (np.abs(rgb[:, :, 0] - rgb[:, :, 1]) < 8) & (np.abs(rgb[:, :, 1] - rgb[:, :, 2]) < 8)
                            r = rgb[:, :, 0]
                            bg_mask = is_gray & (r >= 28) & (r <= 155)
                            alpha[bg_mask] = 0
                            
                            del rgb
                            del alpha
                            
                            scaled_frame = pygame.transform.smoothscale(frame, (int(frame_w * scale), int(frame_h * scale)))
                            temp_list.append(scaled_frame)
                else:
                    for _ in range(10):
                        surf = pygame.Surface((80, 80))
                        surf.fill((255, 100, 0))
                        temp_list.append(surf)
                
                self.animations_by_color[color].append(temp_list)
                
        self.animation_list = self.animations_by_color['blue']

    def update_action(self, new_action):
        if not self.alive:
            new_action = 4 # Death action
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update_animation(self):
        # Update animation list based on current phase
        if self.health >= 70:
            self.animation_list = self.animations_by_color['blue']
        elif self.health >= 30:
            self.animation_list = self.animations_by_color['yellow']
        else:
            self.animation_list = self.animations_by_color['red']
            
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            # Freeze animation for Shield Block
            if self.action == 3:
                return
            
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 4: # death
                    self.frame_index = len(self.animation_list[self.action]) - 1
                elif self.action == 2: # attack complete
                    self.frame_index = 0
                else:
                    self.frame_index = 0

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(4)

    def try_attack_player(self, player):
        # Stubbed: combat calculations resolved in update_states
        pass

    def trigger_combo(self):
        if not self.alive: return
        if self.shield_active:
            self.shield_active = False
        now = pygame.time.get_ticks()
        self.combo_active = True
        self.combo_start_time = now
        self.combo_hits_done = 0
        self.last_combo_cooldown_time = now
        self.update_action(2)

    def trigger_shield(self):
        if not self.alive: return
        if self.combo_active: return
        now = pygame.time.get_ticks()
        self.shield_active = True
        self.shield_start_time = now
        self.last_shield_cooldown_time = now
        self.update_action(3)

    def trigger_normal_attack(self):
        if not self.alive: return
        now = pygame.time.get_ticks()
        self.charge_active = True
        self.charge_start_time = now
        self.last_normal_cooldown_time = now
        self.normal_hit_done = 0
        self.update_action(2)

    def update_states(self, player):
        if not self.alive: return
        current_time = pygame.time.get_ticks()
        
        # 1. Normal Attack charge
        if self.charge_active:
            charge_duration = 1000 if self.health < 30 else 1500
            elapsed = current_time - self.charge_start_time
            if elapsed >= charge_duration:
                self.charge_active = False
                if self.action == 2:
                    self.update_action(0)
            else:
                self.update_action(2)
                # Hold the hammer raised (frame 4) during charge
                if elapsed < charge_duration - 500:
                    if self.frame_index > 4:
                        self.frame_index = 4
                else:
                    # Strike once!
                    if getattr(self, 'normal_hit_done', 0) == 0:
                        self.perform_normal_attack(player)
                        self.normal_hit_done = 1
        # 2. Shield Block
        if self.shield_active:
            shield_duration = 1500
            if current_time - self.shield_start_time >= shield_duration:
                self.shield_active = False
                if self.action == 3:
                    self.update_action(0)
            else:
                self.update_action(3)
                return
                
        # 3. Combo Attack (Continuous chasing strikes)
        if self.combo_active:
            combo_duration = 2000
            elapsed = current_time - self.combo_start_time
            if elapsed >= combo_duration:
                self.combo_active = False
                if self.action == 2:
                    self.update_action(0)
            else:
                self.update_action(2)
                # Vừa đập vừa rượt theo player (Chase player while striking)
                px = player.rect.centerx // self.battle_base.tile_width
                py = player.rect.bottom // self.battle_base.tile_height - 1
                self.set_target_grid_pos(px, py)
                
                # Đánh liên tục mỗi 400ms
                expected_hits = int(elapsed // 400) + 1
                expected_hits = min(expected_hits, 5)
                if expected_hits > self.combo_hits_done:
                    self.perform_combo_hit(player)
                    self.combo_hits_done = expected_hits

    def perform_normal_attack(self, player):
        current_time = pygame.time.get_ticks()
        from src.ai.adversarial_search import AdversarialSearch
        px = player.rect.centerx // self.battle_base.tile_size
        py = player.rect.bottom // self.battle_base.tile_size - 1
        bx = self.rect.centerx // self.battle_base.tile_size
        by = self.rect.bottom // self.battle_base.tile_size - 1
        
        same_height = abs(py - by) <= 1
        is_facing = (self.direction == 1 and px >= bx - 1) or \
                    (self.direction == -1 and px <= bx + 1)
        can_fight = same_height and is_facing
                    
        if can_fight and AdversarialSearch.is_in_range((bx, by), (px, py)):
            if current_time - getattr(player, 'last_hurt_time', 0) > 500:
                if player.action == 4: # Knight Block
                    dmg = 3
                else:
                    dmg = 15
                player.health -= dmg
                if self.health >= 70: self.battle_base.damage_phase1 += dmg
                elif self.health >= 30: self.battle_base.damage_phase2 += dmg
                else: self.battle_base.damage_phase3 += dmg
                player.is_hurt = True
                player.update_action(8)
                player.last_hurt_time = current_time
                player.check_alive()

    def perform_combo_hit(self, player):
        current_time = pygame.time.get_ticks()
        from src.ai.adversarial_search import AdversarialSearch
        px = player.rect.centerx // self.battle_base.tile_size
        py = player.rect.bottom // self.battle_base.tile_size - 1
        bx = self.rect.centerx // self.battle_base.tile_size
        by = self.rect.bottom // self.battle_base.tile_size - 1
        
        same_height = abs(py - by) <= 1
        is_facing = (self.direction == 1 and px >= bx - 1) or \
                    (self.direction == -1 and px <= bx + 1)
        can_fight = same_height and is_facing
                    
        if can_fight and AdversarialSearch.is_in_range((bx, by), (px, py)):
            if player.action == 4:
                dmg = 3
            else:
                dmg = 10
            player.health -= dmg
            if self.health >= 70: self.battle_base.damage_phase1 += dmg
            elif self.health >= 30: self.battle_base.damage_phase2 += dmg
            else: self.battle_base.damage_phase3 += dmg
            player.is_hurt = True
            player.update_action(8)
            player.last_hurt_time = current_time
            player.check_alive()

    def set_target_grid_pos(self, col, row):
        if not self.alive: return
        self.target_grid_pos = (col, row)

    def update_movement(self):
        if not self.alive: return
        
        if self.health < 30:
            self.speed = self.original_speed * 2.0
        else:
            self.speed = self.original_speed
            
        target_x = self.target_grid_pos[0] * self.battle_base.tile_size + self.battle_base.tile_size // 2 - self.width // 2
        target_y = (self.target_grid_pos[1] + 1) * self.battle_base.tile_size - self.height + self.feet_offset
        
        min_x = self.battle_base.tile_size
        max_x = self.battle_base.map_width * self.battle_base.tile_size - self.battle_base.tile_size - self.width
        target_x = max(min_x, min(target_x, max_x))
        
        dx = target_x - self.current_px_pos[0]
        dy = target_y - self.current_px_pos[1]
        dist = math.hypot(dx, dy)
        
        if dist > self.speed:
            self.current_px_pos[0] += (dx / dist) * self.speed
            self.current_px_pos[1] += (dy / dist) * self.speed
            self.rect.x = int(self.current_px_pos[0])
            self.rect.y = int(self.current_px_pos[1])
            
            if dx < 0:
                self.flip = True
                self.direction = -1
            elif dx > 0:
                self.flip = False
                self.direction = 1
                
            if self.action not in (2, 3) and not self.charge_active:
                self.update_action(1)
        else:
            self.current_px_pos[0] = target_x
            self.current_px_pos[1] = target_y
            self.rect.x = int(self.current_px_pos[0])
            self.rect.y = int(self.current_px_pos[1])
            if self.action not in (2, 3) and not self.charge_active:
                self.update_action(0)

    def draw(self, surface, offset=(0, 0)):
        img = pygame.transform.flip(self.image, self.flip, False)
        
        draw_y = self.rect.y - offset[1]
        # Lift up the boss during the attack animation to prevent the feet/hammer from sinking
        if self.action == 2:
            draw_y -= 18
            
        surface.blit(img, (self.rect.x - offset[0], draw_y))

