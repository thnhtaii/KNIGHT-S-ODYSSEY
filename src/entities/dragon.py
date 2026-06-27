import pygame
import os
import math
from src.entities.boss_knight import BossKnight

class Dragon(BossKnight):
    def __init__(self, x, y, scale, speed, battle_base, algo_name=""):
        self.algo_name = algo_name
        self.scale = scale
        self.font = pygame.font.SysFont('Arial', 12, bold=True)
        # Khởi tạo qua class cha BossKnight (tạm thời load sprite boss_knight)
        super().__init__(x, y, scale, speed, battle_base)
        self.name = "dragon"
        self.health = 30
        self.attack_cooldown = 2000

        # Scan down to find the floor tile
        tile_x = int(x) // battle_base.tile_width
        tile_y = int(y) // battle_base.tile_height
        layer_width = battle_base.map_width
        
        while tile_y < battle_base.map_height:
            # We access the collision map layer (index 1)
            tile_id = battle_base.tile_layers[1][tile_y * layer_width + tile_x]
            if tile_id > 0:
                break
            tile_y += 1
            
        floor_level = tile_y * battle_base.tile_height
        self.rect.bottom = floor_level + int(20 * scale)

    def load_sprites(self, scale):
        self.animation_list = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        sprite_dir = os.path.join(project_root, 'assets', 'sprites', 'dragon')
        
        frame_w, frame_h = 100, 100
        # Tên animation theo list_types của cha: ['idle', 'walk', 'attack', 'death']
        for animation in self.animation_types:
            temp_list = []
            if animation == 'death':
                # Không có death anim, dùng idle làm tạm
                anim_file = "dragon_idle.png"
            else:
                anim_file = f"dragon_{animation}.png"
                
            img_path = os.path.join(sprite_dir, anim_file)
            if os.path.exists(img_path):
                sheet = pygame.image.load(img_path).convert_alpha()
                w, h = sheet.get_size()
                cols = w // frame_w
                rows = h // frame_h
                for row in range(rows):
                    for col in range(cols):
                        rect = pygame.Rect(col * frame_w, row * frame_h, frame_w, frame_h)
                        frame = sheet.subsurface(rect)
                        # Tránh nạp các ô trống ở cuối sprite sheet gây biến mất khung hình
                        mask = pygame.mask.from_surface(frame)
                        if mask.count() > 0:
                            img = pygame.transform.scale(frame, (int(frame_w * scale), int(frame_h * scale)))
                            temp_list.append(img)
            else:
                surf = pygame.Surface((48, 48))
                surf.fill((255, 0, 0))
                temp_list.append(surf)
            
            if not temp_list:
                surf = pygame.Surface((48, 48))
                surf.fill((255, 0, 0))
                temp_list.append(surf)
                
            self.animation_list.append(temp_list)

    def draw(self, surface, offset=(0, 0)):
        # Vẽ hình rồng
        img = pygame.transform.flip(self.image, self.flip, False)
        draw_x = self.rect.x - offset[0]
        draw_y = self.rect.y - offset[1]
        surface.blit(img, (draw_x, draw_y))
        
        # Vẽ tên thuật toán phía trên
        if self.algo_name and self.alive:
            text = self.font.render(self.algo_name, True, (210, 180, 140))
            text_rect = text.get_rect(center=(draw_x + self.rect.width // 2, draw_y + int(25 * self.scale) - 8))
            surface.blit(text, text_rect)
