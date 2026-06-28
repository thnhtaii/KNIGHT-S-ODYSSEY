import pygame
import os

class Knight(pygame.sprite.Sprite):
    def __init__(self, x, y, scale, speed, battle_base):
        super().__init__()
        self.rect = pygame.Rect(x, y, 49, 61)
        self.scale = scale
        self.speed = speed
        self.battle_base = battle_base
        self.flip = False
        self.direction = 1
        self.vel_y = 0
        self.jump = False
        self.in_air = True
        self.attack = False
        self.block = False
        self.cast = False
        self.crouch = False
        self.dash = False
        self.alive = True
        self.health = 100
        self.is_hurt = False
        self.action = 0
        self.frame_index = 0
        self.animation_types = ['Idle', 'Walk', 'Jump', 'Attack', 'Block', 'Cast', 'Crouch', 'Dash', 'Dizzy', 'Hurt', 'JumpAttack']
        self.animation_list = []
        self.update_time = pygame.time.get_ticks()
        self.attack_frame = 0
        self.jump_start_y = y
        self.jump_count = 0
        self.max_jumps = 2

        for action in self.animation_types:
            sprite_list = []
            action_folder = os.path.join('assets', 'sprites', 'knight files', 'knight png', action)
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(os.path.dirname(current_dir))
            sprite_path = os.path.join(project_root, action_folder)
            for file in os.listdir(sprite_path):
                if file.endswith('.png'):
                    img_path = os.path.join(sprite_path, file)
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                    sprite_list.append(img)
            self.animation_list.append(sprite_list)

        self.image = self.animation_list[self.action][self.frame_index]
        self.rect = self.image.get_rect()
        self.rect.x = round(x / self.battle_base.tile_width) * self.battle_base.tile_width
        self.rect.y = round(y / self.battle_base.tile_height) * self.battle_base.tile_height
        self.adjust_to_ground()  # Căn chỉnh vị trí khởi tạo

    def adjust_to_ground(self):
        on_ground = False
        for obj in self.battle_base.ground_objects:
            rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
            if rect.collidepoint(self.rect.centerx, self.rect.bottom):
                self.rect.bottom = rect.top
                self.vel_y = 0
                self.in_air = False
                on_ground = True
                print(f"[Knight] Đặt trên nền gnd tại y={rect.top}")
                break

        if not on_ground:
            self.in_air = True
            print("[Knight] No gnd found, knight will fall")

    def load_sprite(self, action):
        action_folder = action
        sprite_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        sprite_path = os.path.join(project_root, 'assets', 'sprites', 'knight', action_folder)

        for file in os.listdir(sprite_path):
            if file.endswith('.png'):
                img_path = os.path.join(sprite_path, file)
                img = pygame.image.load(img_path).convert_alpha()
                img = pygame.transform.scale(img, (int(img.get_width() * self.scale), int(img.get_height() * self.scale)))
                sprite_list.append(img)

        action_index = self.animation_types.index(action)
        self.animation_list[action_index] = sprite_list
        self.frame_index = 0

    def move(self, left, right, up=False, down=False):
        map_width_px = self.battle_base.map_width * self.battle_base.tile_width
        map_height_px = self.battle_base.map_height * self.battle_base.tile_height

        dx = 0
        dy = 0
        if left:
            dx = -self.speed
            self.flip = True
            self.direction = -1
        if right:
            dx = self.speed
            self.flip = False
            self.direction = 1

        # Check ladder collision
        on_ladder = False
        if hasattr(self.battle_base, "ladder_objects"):
            for lad in self.battle_base.ladder_objects:
                lad_rect = pygame.Rect(lad["x"], lad["y"], lad["width"], lad["height"])
                if self.rect.colliderect(lad_rect):
                    on_ladder = True
                    break

        if on_ladder:
            if up:
                dy = -self.speed
                self.vel_y = 0
            elif down:
                dy = self.speed
                self.vel_y = 0
            else:
                dy = 0
                self.vel_y = 0
            self.in_air = False
            self.jump_count = 0
        else:
            if not self.in_air:
                self.jump_count = 0
            
            if self.jump:
                if self.jump_count < self.max_jumps:
                    self.vel_y = -13
                    self.in_air = True
                    self.jump_count += 1
                    self.jump_start_y = self.rect.y
                self.jump = False

            self.vel_y += 0.75
            if self.vel_y > 10:
                self.vel_y = 10
            dy += self.vel_y

        prev_x = self.rect.x
        self.rect.x += dx
        self.check_collision('horizontal', dx)

        self.rect.y += dy
        if on_ladder:
            on_ground = False
        else:
            on_ground = self.check_collision('vertical', dy)

        # Kiểm tra va chạm trần khi nhảy
        if self.vel_y < 0:
            map_width = self.battle_base.map_width
            layer_ground = self.battle_base.tile_layers[1]
            center_col = self.rect.centerx // self.battle_base.tile_width
            hit_ceiling = False
            for row in [13, 19, 25]:
                idx = row * map_width + center_col
                if idx < len(layer_ground) and layer_ground[idx] >= 229:
                    tile_rect = pygame.Rect(center_col * self.battle_base.tile_width, row * self.battle_base.tile_height, self.battle_base.tile_width, self.battle_base.tile_height)
                    if self.rect.colliderect(tile_rect):
                        self.rect.top = tile_rect.bottom
                        self.vel_y = 0
                        hit_ceiling = True
                        break
            if not hit_ceiling:
                for layer in self.battle_base.object_layers:
                    for obj in layer:
                        if obj.get("name") == "objGround":
                            obj_rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                            if self.rect.colliderect(obj_rect) and obj_rect.left < self.rect.centerx < obj_rect.right:
                                self.rect.top = obj_rect.bottom
                                self.vel_y = 0
                                hit_ceiling = True
                                break
                    if hit_ceiling:
                        break

        if not on_ground and prev_x // self.battle_base.tile_width != self.rect.x // self.battle_base.tile_width:
            self.in_air = True

        # Giới hạn vị trí không cho rơi khỏi màn hình
        self.rect.x = max(0, min(self.rect.x, map_width_px - self.rect.width))
        
        if self.rect.top < 0:
            self.rect.top = 0
            self.vel_y = 0

        print(f"Knight pos: {self.rect.x}, {self.rect.y}, vel_y={self.vel_y}, rect.bottom={self.rect.bottom}")

    def check_collision(self, direction, value):
        tile_width = self.battle_base.tile_width
        tile_height = self.battle_base.tile_height
        on_ground = False

        # Va chạm theo hướng dọc (rơi xuống)
        if direction == 'vertical':
            for obj in self.battle_base.ground_objects + self.battle_base.wall_objects:
                rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                if self.rect.colliderect(rect):
                    if value > 0:  # Đang rơi xuống
                        self.rect.bottom = rect.top
                        self.vel_y = 0
                        self.in_air = False
                        on_ground = True
                        # print(f"[Knight] Hit ground/wall at y={rect.top}")
                    elif value < 0:  # Đang nhảy lên
                        if rect.left < self.rect.centerx < rect.right:
                            self.rect.top = rect.bottom
                            self.vel_y = 0
                            print(f"[Knight] Đụng trần tại y={rect.bottom}")
                    break

            if value > 0 and not on_ground:
                self.in_air = True
                print(f"[Knight] Không có nền, đang rơi ở y={self.rect.y}")

        # Va chạm theo hướng ngang (đi trái/phải)
        elif direction == 'horizontal':
            for obj in self.battle_base.wall_objects + self.battle_base.ground_objects:
                rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                if self.rect.colliderect(rect):
                    if value > 0:  # Đi sang phải
                        if rect.left >= self.rect.left:
                            self.rect.right = rect.left
                            break
                    elif value < 0:  # Đi sang trái
                        if rect.right <= self.rect.right:
                            self.rect.left = rect.right
                            break

        return on_ground

    def update_animation(self):
        cooldown = 100
        if self.action < 0 or self.action >= len(self.animation_list):
            print(f"Error: Invalid action index {self.action}, resetting to Idle (0)")
            self.action = 0

        if self.frame_index >= len(self.animation_list[self.action]):
            if self.action in [3, 10]:  # Attack hoặc JumpAttack
                self.attack = False
                self.attack_frame = 0
                self.update_action(0)  # Chuyển về Idle sau khi hoàn thành Attack
            elif self.action == 8:  # Hurt
                self.is_hurt = False
                self.update_action(0)  # Về Idle
            self.frame_index = 0
            print(f"Resetting frame index to 0 for action {self.action}")

        self.image = self.animation_list[self.action][self.frame_index]
        print(f"Animation: action={self.action}, frame={self.frame_index}")

        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1

            if self.action in [3, 10]:
                self.attack_frame += 1
                print(f"Attack frame: {self.attack_frame}")
            print(f"Updating frame to {self.frame_index}")

    def update_action(self, new_action):
        if self.action in [3, 10] and self.frame_index < len(self.animation_list[self.action]) - 1:
            return  # Không cho phép đổi hành động nếu Attack hoặc JumpAttack chưa hoàn thành
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            print(f"Updated action to {new_action}")
            if new_action in [3, 10]:
                self.attack = False
                self.attack_frame = 0

    def check_alive(self):
        if self.health <= 0:
            self.health = 0
            self.speed = 0
            self.alive = False
            self.update_action(3)  # Death

    def draw(self, screen):
        screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)