import pygame
import os
import math

class BossKnight(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, battle_base, csp_controller=None):
        super().__init__()
        self.alive = True
        self.speed = speed
        self.scale = scale
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.flip = False
        self.animation_list = []
        self.frame_index = 0
        self.action = 0 # 0: Idle, 1: Walk, 2: Attack, 3: Death
        self.update_time = pygame.time.get_ticks()
        self.health = 30
        self.battle_base = battle_base
        self.name = "boss_knight"
        self.csp_controller = csp_controller

        # Pathfinding state
        self.path = []
        self.target_node = None

        self.animation_types = ['idle', 'walk', 'attack', 'death']
        self.load_sprites(scale)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.width = self.rect.width
        self.height = self.rect.height

        self.is_attacking = False
        self.last_attack_time = 0
        self.attack_cooldown = 2000

    def load_sprites(self, scale):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        sprite_dir = os.path.join(project_root, 'assets', 'sprites', 'boss')
        
        frame_w, frame_h = 150, 150
        for animation in self.animation_types:
            temp_list = []
            if animation == 'death':
                # No death anim yet, use idle
                anim_file = "knight_idle.png"
            else:
                anim_file = f"knight_{animation}.png"
                
            img_path = os.path.join(sprite_dir, anim_file)
            if os.path.exists(img_path):
                sheet = pygame.image.load(img_path).convert_alpha()
                w, h = sheet.get_size()
                cols = w // frame_w
                rows = h // frame_h
                for row in range(rows):
                    for col in range(cols):
                        rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                        # Avoid empty frames if any, but let's assume all are valid.
                        frame = sheet.subsurface(rect)
                        # Scale down slightly so it's not huge
                        img = pygame.transform.scale(frame, (int(frame_w * scale), int(frame_h * scale)))
                        temp_list.append(img)
            else:
                surf = pygame.Surface((48, 48))
                surf.fill((0, 0, 255))
                temp_list.append(surf)
            
            # If for some reason temp_list is empty, add a fallback
            if not temp_list:
                surf = pygame.Surface((48, 48))
                surf.fill((0, 0, 255))
                temp_list.append(surf)
                
            self.animation_list.append(temp_list)

    def update_action(self, new_action):
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()

    def update_animation(self):
        ANIMATION_COOLDOWN = 100
        self.image = self.animation_list[self.action][self.frame_index]
        if pygame.time.get_ticks() - self.update_time > ANIMATION_COOLDOWN:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3: # death
                    self.frame_index = len(self.animation_list[self.action]) - 1
                else:
                    self.frame_index = 0

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)

    def try_attack_player(self, player):
        if not self.alive: return
        current_time = pygame.time.get_ticks()
        if self.rect.colliderect(player.rect):
            if current_time - getattr(player, 'last_hurt_time', 0) > 1000 and \
               current_time - self.last_attack_time > self.attack_cooldown:
                player.health -= 15
                player.is_hurt = True
                player.update_action(8)
                player.last_hurt_time = current_time
                self.last_attack_time = current_time
                self.update_action(2) # attack
                if player.health <= 0:
                    player.check_alive()

    def move_along_path(self):
        # Move towards the next node in self.path
        if not self.path:
            self.update_action(0)
            return

        target_x, target_y = self.path[0]
        # target_x, target_y are pixel coordinates (center of tile)
        
        dx = target_x - self.rect.centerx
        dy = target_y - self.rect.centery

        dist = math.hypot(dx, dy)
        if dist < self.speed:
            self.rect.centerx = target_x
            self.rect.centery = target_y
            self.path.pop(0)
        else:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed
            self.direction = 1 if dx > 0 else -1
            self.flip = (self.direction == -1)
            self.update_action(1)

    def draw(self, surface, offset=(0, 0)):
        img = pygame.transform.flip(self.image, self.flip, False)
        surface.blit(img, (self.rect.x - offset[0], self.rect.y - offset[1]))
