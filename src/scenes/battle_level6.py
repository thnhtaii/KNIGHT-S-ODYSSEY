import pygame
import os
import time
import random
import math
from src.scenes.battle_base import BattleBase
from src.components.music_manager import MusicManager
from src.entities.knight import Knight
from src.entities.boss_robot import BossRobot
from src.ui.settings_menu import SettingsMenu
from src.ui.game_over import GameOverScreen
from src.ui.game_victory import GameVictoryScreen
from src.ai.adversarial_search import AdversarialSearch

class FallingRock:
    def __init__(self, col, tile_size):
        self.col = col
        self.tile_size = tile_size
        self.x = col * tile_size + tile_size // 2
        self.y = 0
        self.speed = 8
        self.state = "warning"  # "warning" or "falling"
        self.spawn_time = pygame.time.get_ticks()
        self.warning_duration = 1000  # 1 second warning
        self.size = 20
        self.beam_hit = False

    def update(self):
        now = pygame.time.get_ticks()
        if self.state == "warning":
            if now - self.spawn_time > self.warning_duration:
                self.state = "falling"
        elif self.state == "falling":
            self.y += self.speed

class BattleLevel6(BattleBase):
    def __init__(self, screen, health_bar, player_health):
        super().__init__(screen, level_name="level6")
        self.screen = screen
        self.health_bar = health_bar
        self.player_health = player_health
        self.running = True
        self.paused = False
        
        self.player = None
        self.boss = None
        
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        
        # --- WOW FACTOR: Custom Stone Brick Tiles for Castle Theme ---
        custom_tile_path = os.path.join(project_root, "assets", "sprites", "terrain", "castle_stone_brick.bmp")
        if os.path.exists(custom_tile_path) and 54 in getattr(self, 'tiles', {}):
            raw_brick = pygame.image.load(custom_tile_path).convert_alpha()
            scaled_brick = pygame.transform.scale(raw_brick, (self.tile_width, self.tile_height))
            self.tiles[54] = scaled_brick
        
        # Override background image to use assets/backgrounds/level6_bg.png
        bg_path = os.path.join(project_root, "assets", "backgrounds", "level6_bg.png")
        if os.path.exists(bg_path):
            bg_raw = pygame.image.load(bg_path).convert()
            map_pixel_w = self.map_width * self.tile_width
            map_pixel_h = self.map_height * self.tile_height
            self._bg_surface = pygame.transform.smoothscale(bg_raw, (map_pixel_w, map_pixel_h))
        else:
            self._bg_surface = None

        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicBoss.mp3')
        
        self.music_manager = MusicManager()
        self.music_manager.play_music(music_path)
        
        # Instantiate entities from spawn objects
        for obj in self.spawn_objects:
            x = int(obj["x"])
            y = int(obj["y"])
            name = obj.get("name", "")
            
            if name == "knight":
                self.player = Knight(x, y, scale=0.35, speed=4, battle_base=self)
                self.player_group = pygame.sprite.Group(self.player)
            elif name == "boss_robot":
                self.boss = BossRobot(x, y, scale=0.175, speed=3, battle_base=self)
                self.enemy_group = pygame.sprite.Group(self.boss)

        if not self.player:
            raise ValueError("Không tìm thấy object 'knight' trong map level6!")
        if not self.boss:
            raise ValueError("Không tìm thấy object 'boss_robot' trong map level6!")

        self.moving_left = False
        self.moving_right = False
        self.moving_up = False
        self.moving_down = False
        
        # Camera is fixed for level 6 arena, but offset remains [0, 0]
        self.camera_offset = [0, 0]
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # HUD assets
        icon_dir = os.path.join(project_root, 'assets', 'icons')
        self.settings_icon = pygame.transform.scale(pygame.image.load(os.path.join(icon_dir, "settings_icon.png")), (30, 30))
        self.settings_button = pygame.Rect(750, 10, 30, 30)
        self.pause_icon = pygame.transform.scale(pygame.image.load(os.path.join(icon_dir, "pause_icon.png")), (30, 30))
        self.pause_button = pygame.Rect(700, 10, 30, 30)
        self.continue_icon = pygame.transform.scale(pygame.image.load(os.path.join(icon_dir, "continue_icon.png")), (30, 30))
        self.continue_button = pygame.Rect(650, 10, 30, 30)
        
        # Load skill icon and apply circular mask
        raw_icon = pygame.image.load(os.path.join(icon_dir, "sword_skill.png")).convert_alpha()
        raw_icon = pygame.transform.scale(raw_icon, (60, 60))
        
        w, h = raw_icon.get_size()
        masked_icon = pygame.Surface((w, h), pygame.SRCALPHA)
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.circle(mask, (255, 255, 255, 255), (w // 2, h // 2), min(w, h) // 2)
        masked_icon.blit(raw_icon, (0, 0))
        masked_icon.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        
        self.sword_skill_icon = masked_icon
        self.player_cooldown = 0
        self.damage_popups = []

        # AI search variables
        self.grid = AdversarialSearch.get_bg_grid(self)
        self.last_ai_update = 0
        self.ai_update_interval = 300  # run search every 300ms
        
        # Replace floating square tiles with the new rock images
        rock_img_path1 = os.path.join(project_root, "assets", "sprites", "terrain", "floating_rock_1.png")
        rock_img_path2 = os.path.join(project_root, "assets", "sprites", "terrain", "floating_rock_2.png")
        
        self.floating_platforms = []
        if os.path.exists(rock_img_path1) and os.path.exists(rock_img_path2) and len(self.tile_layers) > 1:
            rock_imgs = [
                pygame.image.load(rock_img_path1).convert_alpha(),
                pygame.image.load(rock_img_path2).convert_alpha()
            ]
            layer = self.tile_layers[1]
            for row in range(self.map_height):
                col = 0
                while col < self.map_width:
                    idx = row * self.map_width + col
                    if layer[idx] == 54:
                        start_col = col
                        while col < self.map_width and layer[row * self.map_width + col] == 54:
                            layer[row * self.map_width + col] = 0 # Hide original tile
                            col += 1
                        span = col - start_col
                        pw = span * self.tile_width
                        
                        # Choose a random rock design
                        raw_rock = random.choice(rock_imgs)
                        
                        # Calculate height, reducing thickness by 50% to balance stretching
                        ph = int(pw * (raw_rock.get_height() / raw_rock.get_width()) * 0.5)
                        
                        scaled_rock = pygame.transform.smoothscale(raw_rock, (pw, ph))
                        
                        # Store to draw later
                        self.floating_platforms.append({
                            'x': start_col * self.tile_width,
                            'y': row * self.tile_height,
                            'img': scaled_rock
                        })
                    else:
                        col += 1
        
        # AI HUD Stats
        self.ai_brain_mode = "MINIMAX"
        self.ai_nodes_evaluated = 0
        self.ai_pruned_branches = 0
        self.ai_thinking_time = 0.0
        self.ai_depth = 3
        
        # Predictive player target position (for shadow rendering)
        self.pred_player_pos = (self.player.rect.centerx // self.tile_size, self.player.rect.bottom // self.tile_size - 1)
        
        # Stochastic hazards (Phase 3 Expectimax)
        self.hazards = []
        self.last_hazard_spawn = 0
        self.hazard_spawn_interval = 2000  # Spawn hazard every 2 seconds in Phase 3
        
        self.font_overlay = pygame.font.SysFont('Arial', 14, bold=True)
        self.font_large = pygame.font.SysFont('Arial', 18, bold=True)
        self.font_warning = pygame.font.SysFont('Arial', 24, bold=True)

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
                            if getattr(self, 'player_cooldown', 0) == 0:
                                # Determine player max cooldown based on boss health
                                if self.boss.health >= 70:
                                    max_cd = 240 # 4s
                                else:
                                    max_cd = 120 # 2s
                                    
                                self.player_cooldown = max_cd
                                self.player.update_action(3)
                                self.player.attack = True
                                
                                # Resolve combat
                                if self.player.alive and self.boss.alive:
                                    px = self.player.rect.centerx // self.tile_size
                                    py = self.player.rect.bottom // self.tile_size - 1
                                    bx = self.boss.rect.centerx // self.tile_size
                                    by = self.boss.rect.bottom // self.tile_size - 1
                                    
                                    same_height = abs(py - by) <= 1
                                    is_facing = (self.player.direction == 1 and bx >= px - 1) or \
                                                (self.player.direction == -1 and bx <= px + 1)
                                    in_range = abs(px - bx) <= 6
                                                
                                    can_fight = same_height and is_facing and in_range
                                                
                                    if can_fight:
                                        is_back = (px < bx and self.boss.direction > 0) or \
                                                  (px > bx and self.boss.direction < 0)
                                                  
                                        is_shielded = getattr(self.boss, 'shield_active', False) and not is_back
                                        if not is_shielded and not is_back and self.boss.health < 70 and getattr(self.boss, 'shield_cooldown', 1) <= 0:
                                            self.boss.trigger_shield()
                                            if px < bx:
                                                self.boss.direction = -1
                                                self.boss.flip = True
                                                self.boss.frame_index = 1 # frame thứ 2
                                            else:
                                                self.boss.direction = 1
                                                self.boss.flip = False
                                                self.boss.frame_index = 3 # frame thứ 4
                                            is_shielded = True
                                            
                                        if self.boss.health < 30: # Phase 3
                                            dmg = 5 if is_shielded else 15
                                        else: # Phase 1 & 2
                                            dmg = 2 if is_shielded else 10
                                            
                                        self.boss.health -= dmg
                                        
                                        # Create floating damage/block text popup
                                        popup_x = self.boss.rect.centerx - 40
                                        popup_y = self.boss.rect.y - 20
                                        if is_shielded:
                                            self.damage_popups.append({
                                                "text": f"BLOCKED (-{dmg} HP)",
                                                "x": popup_x,
                                                "y": popup_y,
                                                "color": (0, 180, 255),
                                                "timer": 60
                                            })
                                        else:
                                            txt = f"-{dmg} HP" if not is_back else f"BACKSTAB! -{dmg} HP"
                                            color = (255, 200, 0) if is_back else (255, 0, 0)
                                            self.damage_popups.append({
                                                "text": txt,
                                                "x": popup_x,
                                                "y": popup_y,
                                                "color": color,
                                                "timer": 60
                                            })
                                        
                                        if not is_shielded:
                                            self.boss.is_hurt = True
                                            self.boss.update_action(1) # React Walk/flinch
                                        self.boss.check_alive()
                        if event.key == pygame.K_b and self.player.alive:
                            self.player.block = True
                            self.player.update_action(4) # Block animation
                elif event.type == pygame.KEYUP:
                    if not self.paused:
                        if event.key == pygame.K_a: self.moving_left = False
                        if event.key == pygame.K_d: self.moving_right = False
                        if event.key == pygame.K_w: self.moving_up = False
                        if event.key == pygame.K_s: self.moving_down = False
                        if event.key == pygame.K_b:
                            self.player.block = False
                            self.player.update_action(0) # back to idle
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.pause_button.collidepoint(event.pos): self.paused = True
                    elif self.continue_button.collidepoint(event.pos): self.paused = False
                    elif self.settings_button.collidepoint(event.pos):
                        settings_menu = SettingsMenu(self.screen)
                        res = settings_menu.run()
                        if res == "menu": return "menu"
            
            if self.player.alive and not self.paused:
                self.player.move(self.moving_left, self.moving_right, self.moving_up, self.moving_down)
                
                # Check fall off map
                if self.player.rect.top > self.map_height * self.tile_height:
                    self.player.health = 0
                    self.player.check_alive()
                
                # Update player hurt animations
                if self.player.health < self.prev_health and not self.player.is_hurt:
                    self.player.is_hurt = True
                    self.player.update_action(8)
                    self.player.frame_index = 0
                self.prev_health = self.player.health

                if not self.player.is_hurt:
                    if self.player.attack:
                        if self.player.action != 3: self.player.update_action(3)
                    elif self.player.block:
                        if self.player.action != 4: self.player.update_action(4)
                    elif self.player.in_air and self.player.vel_y > 1: self.player.update_action(2)
                    elif self.moving_left or self.moving_right: self.player.update_action(1)
                    else: self.player.update_action(0)

                self.player.update_animation()

                if getattr(self, 'player_cooldown', 0) > 0:
                    self.player_cooldown -= 1
                    
                # Dynamically load red sword strike animation if Boss HP < 30%
                if self.boss.health < 30 and not getattr(self, 'red_sword_loaded', False):
                    self.red_sword_loaded = True
                    strike_list = []
                    current_dir = os.path.dirname(os.path.abspath(__file__))
                    project_root = os.path.dirname(os.path.dirname(current_dir))
                    strike_dir = os.path.join(project_root, "assets", "sprites", "knight files", "knight png", "Strike")
                    if os.path.exists(strike_dir):
                        for file in sorted(os.listdir(strike_dir)):
                            if file.endswith('.png'):
                                img_path = os.path.join(strike_dir, file)
                                img = pygame.image.load(img_path).convert_alpha()
                                img = pygame.transform.scale(img, (int(img.get_width() * self.player.scale), int(img.get_height() * self.player.scale)))
                                strike_list.append(img)
                        self.player.animation_list[3] = strike_list

                # Update Boss AI decision making periodically
                self.update_boss_ai()
                
                # Update Boss position and animation
                if self.boss.alive:
                    self.boss.update_states(self.player)
                    self.boss.update_movement()
                    self.boss.update_animation()
                else:
                    self.boss.update_animation()
                    if self.boss.frame_index >= len(self.boss.animation_list[4]) - 1:
                        # Boss died! Complete level with victory
                        victory_screen = GameVictoryScreen(self.screen)
                        res = victory_screen.run()
                        if res == "menu": return "win"
                        if res == "quit": return "quit"
                
                # Update stochastic hazards (Phase 3 Expectimax)
                if self.boss.health < 30:
                    self.update_hazards()
                    
                # Update floating popups
                for popup in self.damage_popups[:]:
                    popup["y"] -= 0.8  # float up slowly
                    popup["timer"] -= 1
                    if popup["timer"] <= 0:
                        self.damage_popups.remove(popup)
                    
            if not self.player.alive:
                self.health_bar.set_health(0)
                res = GameOverScreen(self.screen).run()
                return res

            self.health_bar.set_health(self.player.health)
            self.draw()
            pygame.display.flip()
            clock.tick(60)

    def update_boss_ai(self):
        now = pygame.time.get_ticks()
        current_interval = 150 if self.boss.health < 30 else self.ai_update_interval
        if now - self.last_ai_update < current_interval:
            return
            
        self.last_ai_update = now
        
        # Define current positions in grid cells
        px = self.player.rect.centerx // self.tile_size
        py = self.player.rect.bottom // self.tile_size - 1
        bx, by = self.boss.target_grid_pos
        
        # Safe bounds
        px = max(0, min(px, self.map_width - 1))
        py = max(0, min(py, self.map_height - 1))
        bx = max(0, min(bx, self.map_width - 1))
        by = max(0, min(by, self.map_height - 1))

        # Select algorithm phase based on health
        t0 = time.time()
        danger_cols = [h.col for h in self.hazards if h.state == "warning" or h.state == "falling"]
        
        if self.boss.health >= 70:
            # Phase 1: Minimax
            self.ai_brain_mode = "MINIMAX"
            self.ai_depth = 3
            self.ai_pruned_branches = 0
            best_act, eval_nodes = AdversarialSearch.minimax_decision(
                self.grid, (bx, by), (px, py), self.boss.health, self.player.health,
                player_action=self.player.action, boss_dir=self.boss.direction,
                combo_cooldown=self.boss.combo_cooldown, shield_cooldown=self.boss.shield_cooldown,
                normal_cooldown=self.boss.normal_cooldown, max_depth=self.ai_depth
            )
            self.ai_nodes_evaluated = eval_nodes
            
            # Log for debugging
            with open("boss_ai_debug.log", "a") as f:
                f.write(f"MINIMAX: Boss={(bx, by)}, Player={(px, py)}, Choice={best_act}\n")
        elif self.boss.health >= 30:
            # Phase 2: Alpha-Beta
            self.ai_brain_mode = "ALPHA-BETA"
            self.ai_depth = 6
            best_act, eval_nodes, pruned = AdversarialSearch.alphabeta_decision(
                self.grid, (bx, by), (px, py), self.boss.health, self.player.health,
                player_action=self.player.action, boss_dir=self.boss.direction,
                combo_cooldown=self.boss.combo_cooldown, shield_cooldown=self.boss.shield_cooldown,
                normal_cooldown=self.boss.normal_cooldown, max_depth=self.ai_depth
            )
            self.ai_nodes_evaluated = eval_nodes
            self.ai_pruned_branches = pruned
        else:
            # Phase 3: Expectimax
            self.ai_brain_mode = "EXPECTIMAX"
            self.ai_depth = 4
            self.ai_pruned_branches = 0
            best_act, eval_nodes = AdversarialSearch.expectimax_decision(
                self.grid, (bx, by), (px, py), self.boss.health, self.player.health,
                player_action=self.player.action, boss_dir=self.boss.direction,
                combo_cooldown=self.boss.combo_cooldown, shield_cooldown=self.boss.shield_cooldown,
                normal_cooldown=self.boss.normal_cooldown, danger_cols=danger_cols, max_depth=self.ai_depth
            )
            self.ai_nodes_evaluated = eval_nodes
            
        self.ai_thinking_time = (time.time() - t0) * 1000.0  # in ms
        
        # Apply AI action to Boss
        if best_act == "COMBO":
            self.boss.trigger_combo()
        elif best_act == "BLOCK":
            self.boss.trigger_shield()
        elif best_act == "ATTACK":
            self.boss.trigger_normal_attack()
        elif best_act == "WAIT":
            self.boss.update_action(0)
        elif isinstance(best_act, tuple) and best_act[0] == "MOVE":
            nx, ny = best_act[1]
            self.boss.set_target_grid_pos(nx, ny)
            self.pred_player_pos = (px + random.choice([-1, 0, 1]), py) # predictive target
            
    def update_hazards(self):
        now = pygame.time.get_ticks()
        
        # Spawn rock columns
        if now - self.last_hazard_spawn > self.hazard_spawn_interval:
            self.last_hazard_spawn = now
            # Choose 2 random columns
            cols = [random.randint(2, self.map_width - 3) for _ in range(2)]
            for col in cols:
                self.hazards.append(FallingRock(col, self.tile_size))
                
        # Update rocks
        for h in self.hazards[:]:
            h.update()
            
            # Beam damage during warning phase
            if h.state == "warning" and not getattr(h, 'beam_hit', False):
                px = self.player.rect.centerx // self.tile_size
                if px == h.col:
                    self.player.health -= 10
                    self.player.is_hurt = True
                    self.player.update_action(8)
                    self.player.frame_index = 0
                    self.player.check_alive()
                    h.beam_hit = True
            
            # Bounding box of falling rock
            if h.state == "falling":
                rock_rect = pygame.Rect(h.x - h.size // 2, h.y - h.size // 2, h.size, h.size)
                
                # Check collision with player
                if rock_rect.colliderect(self.player.rect):
                    self.player.health -= 8
                    self.player.is_hurt = True
                    self.player.update_action(8)
                    self.player.frame_index = 0
                    self.player.check_alive()
                    self.hazards.remove(h)
                    continue
                    
                # Check collision with boss
                if rock_rect.colliderect(self.boss.rect):
                    self.boss.health -= 4
                    self.boss.is_hurt = True
                    self.boss.check_alive()
                    self.hazards.remove(h)
                    continue
                    
                # Check collision with solid tiles/ground
                gy = int(h.y // self.tile_size)
                if gy >= self.map_height - 1 or self.grid[min(self.map_height - 1, gy)][h.col] > 0:
                    self.hazards.remove(h)

    def draw(self):
        # Clear and draw base map
        self.screen.fill((0, 0, 0))
        super().draw(self.camera_offset)
        
        # Draw the custom floating rock platforms
        for plat in getattr(self, 'floating_platforms', []):
            self.screen.blit(plat['img'], (plat['x'] - self.camera_offset[0], plat['y'] - self.camera_offset[1]))
        
        # --- Boss Attack Charging Indicator (Wow Factor 4 replacement) ---
        if self.boss.alive and getattr(self.boss, 'charge_active', False):
            bx = self.boss.rect.centerx
            by = self.boss.rect.bottom
            width = 5 * self.tile_size
            height = self.tile_size // 2
            warn_rect = pygame.Rect(bx - width // 2, by - height, width, height)
            pulse = int(127 + 128 * math.sin(pygame.time.get_ticks() / 50.0))
            
            # Draw semi-transparent warn floor rect
            warn_surf = pygame.Surface((width, height), pygame.SRCALPHA)
            warn_surf.fill((255, 0, 0, pulse // 4))
            self.screen.blit(warn_surf, warn_rect.topleft)
            
            # Outline
            pygame.draw.rect(self.screen, (255, 0, 0, pulse), warn_rect, 2, border_radius=4)
            
            # Text above head
            warn_txt = self.font_warning.render("ATTACK CHARGING!", True, (255, 0, 0))
            txt_rect = warn_txt.get_rect(center=(bx, self.boss.rect.y - 45))
            self.screen.blit(warn_txt, txt_rect)
            
        # --- Wow Factor 1 replaced by Robot Core Color (in BossRobot.draw) ---

        # --- Wow Factor 2: Draw Predictive Player Target Shadow (Ghost sprite) ---
        if self.boss.alive and self.player.alive:
            ghost_x = self.pred_player_pos[0] * self.tile_size
            ghost_y = (self.pred_player_pos[1] + 1) * self.tile_size - self.player.rect.height
            ghost_rect = pygame.Rect(ghost_x, ghost_y, self.player.rect.width, self.player.rect.height)
            pygame.draw.rect(self.screen, (0, 255, 100, 80), ghost_rect, 2, border_radius=3)
            label = self.font_overlay.render("Pred X", True, (0, 255, 100))
            self.screen.blit(label, (ghost_rect.x, ghost_rect.y - 15))

        # Draw hazards (Falling rocks & warning zones)
        for h in self.hazards:
            if h.state == "warning":
                alpha = int(127 + 128 * math.sin(pygame.time.get_ticks() / 100.0))
                line_surf = pygame.Surface((self.tile_size, self.screen_height), pygame.SRCALPHA)
                line_surf.fill((255, 0, 0, alpha // 4))
                self.screen.blit(line_surf, (h.col * self.tile_size, 0))
                
                warn_text = self.font_warning.render("!", True, (255, 0, 0))
                text_rect = warn_text.get_rect(center=(h.x, 30))
                self.screen.blit(warn_text, text_rect)
            elif h.state == "falling":
                pygame.draw.circle(self.screen, (150, 75, 0), (h.x, int(h.y)), h.size // 2)
                pygame.draw.circle(self.screen, (100, 50, 0), (h.x, int(h.y)), h.size // 2, 2)

        # Draw characters
        for sprite in self.player_group:
            flipped_image = pygame.transform.flip(sprite.image, sprite.flip, False)
            self.screen.blit(flipped_image, (sprite.rect.x, sprite.rect.y))

        for sprite in self.enemy_group:
            if sprite.alive or sprite.action == 4:
                sprite.draw(self.screen, self.camera_offset)

        # Interface Buttons & Health Bars
        self.health_bar.draw(self.screen)
        self.screen.blit(self.settings_icon, (self.settings_button.x, self.settings_button.y))
        self.screen.blit(self.pause_icon, (self.pause_button.x, self.pause_button.y))
        self.screen.blit(self.continue_icon, (self.continue_button.x, self.continue_button.y))
        
        # Draw Boss Health Bar above its head
        if self.boss.alive:
            bar_w = 60
            bar_h = 6
            bx = self.boss.rect.centerx - bar_w // 2
            by = self.boss.rect.y - 12
            pygame.draw.rect(self.screen, (50, 50, 50), (bx, by, bar_w, bar_h))
            pygame.draw.rect(self.screen, (255, 0, 0), (bx, by, int(bar_w * (self.boss.health / 100.0)), bar_h))
            hp_txt = self.font_overlay.render(f"Boss: {self.boss.health} HP", True, (255, 255, 255))
            self.screen.blit(hp_txt, (bx, by - 14))


        # --- Draw Player Skill Cooldown HUD Icon (Right of Health Bar) ---
        skill_center = (200, 30)
        skill_radius = 30
        
        # Blit skill icon
        icon_x = skill_center[0] - self.sword_skill_icon.get_width() // 2
        icon_y = skill_center[1] - self.sword_skill_icon.get_height() // 2
        self.screen.blit(self.sword_skill_icon, (icon_x, icon_y))
        
        # Render dark cooldown quạt slice overlay
        cooldown = getattr(self, 'player_cooldown', 0)
        if cooldown > 0:
            if self.boss.health >= 70:
                max_cd = 240.0
            else:
                max_cd = 120.0
                
            ratio = cooldown / max_cd
            overlay = pygame.Surface((skill_radius * 2, skill_radius * 2), pygame.SRCALPHA)
            cx, cy = skill_radius, skill_radius
            points = [(cx, cy)]
            start_angle = -math.pi / 2
            end_angle = start_angle + 2 * math.pi * ratio
            
            steps = 30
            for i in range(steps + 1):
                angle = start_angle + (end_angle - start_angle) * (i / steps)
                px_val = cx + skill_radius * math.cos(angle)
                py_val = cy + skill_radius * math.sin(angle)
                points.append((px_val, py_val))
            points.append((cx, cy))
            
            if len(points) > 2:
                pygame.draw.polygon(overlay, (0, 0, 0, 200), points)
            self.screen.blit(overlay, (skill_center[0] - skill_radius, skill_center[1] - skill_radius))
            
            # Cooldown text overlay
            cd_sec = cooldown / 60.0
            cd_txt = self.font_large.render(f"{cd_sec:.1f}s", True, (255, 255, 255))
            txt_rect = cd_txt.get_rect(center=skill_center)
            self.screen.blit(cd_txt, txt_rect)

        # --- Draw floating damage/block popups ---
        for popup in self.damage_popups:
            txt_surf = self.font_overlay.render(popup["text"], True, popup["color"])
            self.screen.blit(txt_surf, (popup["x"], int(popup["y"])))

        if self.paused:
            font = pygame.font.SysFont('Arial', 36, bold=True)
            pause_text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = pause_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2))
            self.screen.blit(pause_text, text_rect)
