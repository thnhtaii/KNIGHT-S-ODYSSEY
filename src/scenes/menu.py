import pygame
import os
import math
from src.components.settings_button import SettingsButton

class Menu:
    def __init__(self, screen, unlocked_levels=None):
        self.screen = screen
        self.running = True
        self.settings_button = SettingsButton(self.screen)

        self.font = pygame.font.SysFont("Stickyman-Battle/assets/fonts/CourierPrime-Regular.ttf", 100)

        self.load_background()

        self.arrow_left = pygame.Rect(0, 0, 50, 50)
        self.arrow_right = pygame.Rect(0, 0, 50, 50)

        self.levels = [
            {"id": 1, "unlocked": True},
            {"id": 2, "unlocked": False},
            {"id": 3, "unlocked": False},
            {"id": 4, "unlocked": False},
            {"id": 5, "unlocked": True},
            {"id": 6, "unlocked": True},
        ]
        if unlocked_levels:
            for level in self.levels:
                if level["id"] in unlocked_levels:
                    level["unlocked"] = True

        self.buttons = []
        self.update_layout()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        lock_path = os.path.join(project_root, 'assets', 'icons', 'lock.png')
        self.lock_image = pygame.image.load(lock_path).convert_alpha()

        self.button_image = pygame.Surface((140, 140), pygame.SRCALPHA)
        self.button_image.fill((0, 150, 255))

    def load_background(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        menu_path = os.path.join(project_root, 'assets', 'backgrounds', '6.png')
        self.original_bg_image = pygame.image.load(menu_path)
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 608
        self.bg_image = pygame.transform.scale(self.original_bg_image, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

    def update_layout(self):
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 608
        self.arrow_left.topleft = (50, self.WINDOW_HEIGHT // 2 - 25)
        self.arrow_right.topleft = (self.WINDOW_WIDTH - 100, self.WINDOW_HEIGHT // 2 - 25)
        self.create_buttons()

    def create_buttons(self):
        button_w, button_h = 140, 140
        gap = 20
        grid_cols, grid_rows = 3, 2

        total_width = grid_cols * button_w + (grid_cols - 1) * gap
        total_height = grid_rows * button_h + (grid_rows - 1) * gap

        start_x = (self.WINDOW_WIDTH - total_width) // 2
        start_y = (self.WINDOW_HEIGHT - total_height) // 2

        self.buttons.clear()
        for i in range(len(self.levels)):
            col = i % grid_cols
            row = i // grid_cols
            x = start_x + col * (button_w + gap)
            y = start_y + row * (button_h + gap)
            self.buttons.append(pygame.Rect(x, y, button_w, button_h))

    def draw_title(self):
        frame = pygame.time.get_ticks() / 100
        offset = int(5 * math.sin(frame))

        font_size = max(80, self.WINDOW_HEIGHT // 7)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        title_font_path = os.path.join(project_root, 'assets', 'fonts', 'RubikGlitch-Regular.ttf')
        title_font = pygame.font.Font(title_font_path, font_size)

        title_text = title_font.render("MENU", True, (255, 50, 50))
        shadow_text = title_font.render("MENU", True, (0, 0, 0))

        title_rect = title_text.get_rect(center=(self.WINDOW_WIDTH // 2, 70))
        shadow_rect = shadow_text.get_rect(center=(title_rect.centerx + 4, title_rect.centery + 4))

        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for i, rect in enumerate(self.buttons):
            level = self.levels[i]
            is_hover = rect.collidepoint(mouse_pos)

            if level["unlocked"]:
                color = (80, 220, 80) if not is_hover else (120, 255, 120)
                pygame.draw.rect(self.screen, color, rect, border_radius=10)
                text = self.font.render(str(level["id"]), True, (0, 0, 0))
                self.screen.blit(text, text.get_rect(center=rect.center))
            else:
                pygame.draw.rect(self.screen, (180, 180, 180), rect, border_radius=10)
                lock_scaled = pygame.transform.smoothscale(self.lock_image, (rect.width, rect.height))
                self.screen.blit(lock_scaled, rect.topleft)

        if self.buttons:
            margin = 20
            left = self.buttons[0].left - margin
            top = self.buttons[0].top - margin
            right = self.buttons[-1].right + margin
            bottom = self.buttons[-1].bottom + margin
            pygame.draw.rect(self.screen, (255, 255, 255), (left, top, right - left, bottom - top), width=3, border_radius=15)

        pygame.draw.polygon(self.screen, (255, 255, 255), [
            (self.arrow_left.right, self.arrow_left.top),
            (self.arrow_left.left, self.arrow_left.centery),
            (self.arrow_left.right, self.arrow_left.bottom)
        ])

        pygame.draw.polygon(self.screen, (255, 255, 255), [
            (self.arrow_right.left, self.arrow_right.top),
            (self.arrow_right.right, self.arrow_right.centery),
            (self.arrow_right.left, self.arrow_right.bottom)
        ])

        self.draw_title()
        self.settings_button.draw()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.settings_button.handle_event(event)
                    if result == "home":
                        return "background"

                    if not self.settings_button.settings_menu_open:
                        if self.arrow_left.collidepoint(event.pos):
                            return "background"

                        if self.arrow_right.collidepoint(event.pos):
                            print("→ Tiếp trang (chưa xử lý logic)")

                        for i, rect in enumerate(self.buttons):
                            if rect.collidepoint(event.pos):
                                if self.levels[i]["unlocked"]:
                                    return f"level{self.levels[i]['id']}"  # ✅ Trả về chuỗi như "level2"
                                else:
                                    print("Màn này chưa mở!")


            self.draw()
            pygame.display.flip()
            clock.tick(60)