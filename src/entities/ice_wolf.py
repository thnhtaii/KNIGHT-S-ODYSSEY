import pygame
import os
import math
from src.ai.algorithms import astar_path, greedy_path, ida_star_path
import random


class IceWolf(pygame.sprite.Sprite):
    """Ice Wolf enemy entity for Level 2.
    Uses informed search algorithms: A*, Greedy Best-First Search, IDA*.
    Loads sprite frames from assets/sprites/ice_wolf/ directory.

    Animation actions:
        0 = Idle
        1 = Run
        2 = Hurt
        3 = Die
        4 = Attack
        5 = Walk
        6 = Jump
    """

    def __init__(self, x, y, scale, speed, battle_base, move_area=None):
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
        self.health = 30
        self.battle_base = battle_base
        self.move_area = move_area
        self.name = "wolf_normal"
        self.scale = scale

        # Movement tracking — used to decide which animation to play
        self.is_moving = False

        # Pathfinding state
        self.current_path = []
        self.path_index = 0
        self.follow_player = False
        self.last_goal_tile = None

        # Attack state
        self.is_attacking = False
        self.last_attack_time = 0
        self.attack_cooldown = 2000

        # Death state
        self.death_animation_complete = False

        # Animation frame counts per action
        # Actions: 0=Idle, 1=Run, 2=Hurt, 3=Die, 4=Attack, 5=Walk, 6=Jump
        self.animation_types = ['idle', 'run', 'hurt', 'die', 'attack', 'walk', 'jump']

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        sprite_base = os.path.join(project_root, 'assets', 'sprites', 'ice_wolf')

        for anim_name in self.animation_types:
            temp_list = []
            anim_dir = os.path.join(sprite_base, anim_name)
            if os.path.isdir(anim_dir):
                # Count PNG files in directory
                files = sorted([f for f in os.listdir(anim_dir) if f.endswith('.png')])
                for f in files:
                    img_path = os.path.join(anim_dir, f)
                    img = pygame.image.load(img_path).convert_alpha()
                    img = pygame.transform.smoothscale(img, (
                        int(img.get_width() * scale),
                        int(img.get_height() * scale)
                    ))
                    temp_list.append(img)

            if not temp_list:
                # Fallback: create a placeholder surface
                temp_list = [pygame.Surface((64, 64), pygame.SRCALPHA)]

            self.animation_list.append(temp_list)

        self.image = self.animation_list[0][0]
        # Custom tight collision bounding box (independent of the padded image size)
        rect_w = int(75 * scale)
        rect_h = int(45 * scale)
        self.rect = pygame.Rect(0, 0, rect_w, rect_h)
        self.rect.bottomleft = (x, y)

    def _is_target_changed(self, new_goal_tile):
        """Check if the pathfinding goal has changed significantly."""
        if self.last_goal_tile is None:
            return True
        return (abs(new_goal_tile[0] - self.last_goal_tile[0]) > 1 or
                abs(new_goal_tile[1] - self.last_goal_tile[1]) > 1)

    def try_attack_player(self, player):
        """Attempt to attack the player if in range."""
        current_time = pygame.time.get_ticks()

        if self.rect.colliderect(player.rect):
            if (current_time - getattr(player, 'last_hurt_time', 0) > 1000 and
                    current_time - self.last_attack_time > self.attack_cooldown):
                player.health -= 10
                player.is_hurt = True
                player.update_action(8)  # Hurt animation
                player.last_hurt_time = current_time
                print(f"[{self.name}] Ice Wolf tấn công! Knight còn {player.health} máu")
                self.last_attack_time = current_time
                # Play attack animation on the wolf
                self.update_action(4)  # Attack animation
                self.is_attacking = True
                from src.components.ai_stats_tracker import AIStatsTracker
                AIStatsTracker.log_attack(self.name, 10)
                if player.health <= 0:
                    player.check_alive()

    def _follow_path(self, player, grid, margin_data, pathfind_func):
        """Generic path following logic used by all search algorithms."""
        if not self.alive:
            return

        # Reset movement flag — will be set to True if wolf actually moves
        self.is_moving = False

        # Check distance to player
        if abs(self.rect.centerx - player.rect.centerx) < 200:
            self.follow_player = True
        else:
            self.follow_player = False
            self.current_path = []
            self.path_index = 0
            return

        if self.follow_player:
            current_tile = (self.rect.centerx // self.battle_base.tile_width,
                            self.rect.centery // self.battle_base.tile_height)
            goal_tile = (player.rect.centerx // self.battle_base.tile_width,
                         player.rect.centery // self.battle_base.tile_height)

            # Validate tiles are in bounds
            if not (0 <= goal_tile[0] < len(grid[0]) and 0 <= goal_tile[1] < len(grid) and
                    0 <= current_tile[0] < len(grid[0]) and 0 <= current_tile[1] < len(grid)):
                self.current_path = []
                return

            # Recalculate path if needed
            if (not self.current_path or
                    self.path_index >= len(self.current_path) or
                    self._is_target_changed(goal_tile)):
                import time
                start_t = time.perf_counter()
                self.current_path = pathfind_func(current_tile, goal_tile, grid)
                duration_ms = (time.perf_counter() - start_t) * 1000
                self.path_index = 0
                self.last_goal_tile = goal_tile
                from src.components.ai_stats_tracker import AIStatsTracker
                AIStatsTracker.log_pathfinding(self.name, path_len=len(self.current_path), time_ms=duration_ms)

            # Follow path
            if self.current_path and self.path_index < len(self.current_path):
                self.is_moving = True
                tx, ty = self.current_path[self.path_index]
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

    def update_astar(self, player, grid, margin_data):
        """Move using A* Search algorithm."""
        self._follow_path(player, grid, margin_data, astar_path)
        self.apply_gravity()

    def update_greedy(self, player, grid, margin_data):
        """Move using Greedy Best-First Search algorithm."""
        self._follow_path(player, grid, margin_data, greedy_path)
        self.apply_gravity()

    def update_ida_star(self, player, grid, margin_data):
        """Move using IDA* (Iterative Deepening A*) algorithm."""
        self._follow_path(player, grid, margin_data, ida_star_path)
        self.apply_gravity()

    def move(self):
        """Default movement (patrol)."""
        if not self.alive:
            return
        self.is_moving = True
        dx = self.speed * self.direction
        temp_rect = self.rect.move(dx, 0)
        if self.move_area and not self.move_area.contains(temp_rect):
            if temp_rect.left < self.move_area.left or temp_rect.right > self.move_area.right:
                self.direction *= -1
                dx = self.speed * self.direction
        self.rect.x += dx
        self.check_collision('horizontal', dx)
        if self.move_area:
            if self.rect.left < self.move_area.left:
                self.rect.left = self.move_area.left
                self.direction *= -1
                self.flip = not self.flip
            if self.rect.right > self.move_area.right:
                self.rect.right = self.move_area.right
                self.direction *= -1
                self.flip = not self.flip

        # Set flip based on direction
        self.flip = self.direction < 0

        # Áp dụng trọng lực động để giữ ổn định Y
        self.apply_gravity()

    def check_collision(self, direction, move_value):
        """Check collision with ground and wall objects."""
        # Vertical collision (falling down or jumping up)
        if direction == 'vertical':
            for obj in self.battle_base.ground_objects + self.battle_base.wall_objects:
                rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                if self.rect.colliderect(rect):
                    if move_value > 0:  # Falling down
                        self.rect.bottom = rect.top
                        self.vel_y = 0
                        self.in_air = False
                    elif move_value < 0:  # Jumping up
                        self.rect.top = rect.bottom
                        self.vel_y = 0
        # Horizontal collision (moving left or right)
        elif direction == 'horizontal':
            for obj in self.battle_base.wall_objects:
                rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
                if self.rect.colliderect(rect):
                    if move_value > 0:  # Moving right
                        self.rect.right = rect.left
                    elif move_value < 0:  # Moving left
                        self.rect.left = rect.right

    def apply_gravity(self):
        """Apply gravity to the wolf."""
        if not self.alive:
            return
        
        # Kiểm tra xem có nền ngay dưới chân không (dung sai 1 pixel)
        temp_rect = self.rect.move(0, 1)
        on_ground = False
        for obj in self.battle_base.ground_objects + self.battle_base.wall_objects:
            rect = pygame.Rect(obj["x"], obj["y"], obj["width"], obj["height"])
            if temp_rect.colliderect(rect):
                on_ground = True
                break
        
        if on_ground:
            self.in_air = False
            self.vel_y = 0
        else:
            self.in_air = True
            self.vel_y += 0.75
            if self.vel_y > 10:
                self.vel_y = 10
            self.rect.y += self.vel_y
            self.check_collision('vertical', self.vel_y)
            
        if self.rect.bottom > 600:
            self.rect.bottom = 600
            self.vel_y = 0
            self.in_air = False

    def decide_animation(self):
        """Decide which animation to play based on current state.
        Called once per frame AFTER movement logic, BEFORE update_animation().
        This prevents jitter by centralizing animation decisions.
        """
        if not self.alive:
            self.update_action(3)  # Die
            return

        # If currently playing attack animation, let it finish
        if self.is_attacking:
            if self.action == 4 and self.frame_index < len(self.animation_list[4]) - 1:
                return  # Don't interrupt attack animation
            else:
                self.is_attacking = False

        # Choose animation based on state
        if self.in_air:
            self.update_action(6)  # Jump
        elif self.is_moving:
            self.update_action(1)  # Run (chasing player)
        else:
            if self.follow_player:
                self.update_action(0)  # Idle (near player but not moving)
            else:
                self.update_action(5)  # Walk (patrolling)

    def update_animation(self):
        """Update the current animation frame."""
        cooldown = 100

        self.image = self.animation_list[self.action][self.frame_index]

        if pygame.time.get_ticks() - self.update_time > cooldown:
            self.update_time = pygame.time.get_ticks()
            self.frame_index += 1
            if self.frame_index >= len(self.animation_list[self.action]):
                if self.action == 3:  # Die
                    self.frame_index = len(self.animation_list[3]) - 1
                    self.death_animation_complete = True
                elif self.action == 4:  # Attack finished
                    self.is_attacking = False
                    self.frame_index = 0
                else:
                    self.frame_index = 0

    def update_action(self, new_action):
        """Change the current animation action."""
        if new_action != self.action:
            self.action = new_action
            self.frame_index = 0
            self.update_time = pygame.time.get_ticks()
            self.death_animation_complete = False

    def check_alive(self):
        """Mark the wolf as dead."""
        self.health = 0
        self.speed = 0
        self.alive = False
        self.update_action(3)  # Die animation
        print(f"[IceWolf] {self.name} đã chết!")

    def draw(self, screen):
        """Draw the wolf on screen."""
        if self.alive or self.action == 3:
            draw_x = self.rect.centerx - self.image.get_width() // 2
            draw_y = self.rect.bottom - self.image.get_height()
            screen.blit(pygame.transform.flip(self.image, self.flip, False), (draw_x, draw_y))
