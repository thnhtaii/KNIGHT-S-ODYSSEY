import pygame
import pygame.gfxdraw
import os
import math
from src.components.settings_button import SettingsButton

class Menu:
    def __init__(self, screen, unlocked_levels=None):
        self.screen = screen
        self.running = True
        self.settings_button = SettingsButton(self.screen)

        self.font = pygame.font.SysFont("Arial", 22, bold=True)

        self.load_background()

        self.arrow_left = pygame.Rect(0, 0, 50, 50)
        self.arrow_right = pygame.Rect(0, 0, 50, 50)

        self.levels = [
            {"id": 1, "unlocked": True},
            {"id": 2, "unlocked": False},
            {"id": 3, "unlocked": False},
            {"id": 4, "unlocked": False},
            {"id": 5, "unlocked": False},
            {"id": 6, "unlocked": False},
        ]
        if unlocked_levels:
            for level in self.levels:
                if level["id"] in unlocked_levels:
                    level["unlocked"] = True

        self.buttons = []
        self.update_layout()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        self.title_font_path = os.path.join(project_root, 'assets', 'fonts', 'dpcomic.ttf')
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
        # Định nghĩa các vị trí map pin đè chính xác lên tâm các vùng địa hình
        positions = [
            (100, 310), # Màn 1: Rừng cây
            (290, 150), # Màn 2: Núi tuyết
            (325, 390), # Màn 3: Trong lâu đài cũ (Điều chỉnh sát vào trung tâm cổng thành)
            (500, 300), # Màn 4: Nghĩa địa (Điều chỉnh sát vào chính giữa nghĩa địa và nhà thờ)
            (650, 420), # Màn 5: Hang rồng/Núi lửa (Điều chỉnh dịch sang phải sát vào lòng núi lửa)
            (705, 160)  # Màn 6: Tòa tháp cuối cùng cứu công chúa
        ]
        button_size = 50
        self.buttons.clear()
        for x, y in positions:
            self.buttons.append(pygame.Rect(x - button_size // 2, y - button_size // 2, button_size, button_size))

    def draw_title(self):
        font_size = 38
        try:
            # Sử dụng font chữ pixel đặc trưng của game
            font = pygame.font.Font(self.title_font_path, font_size)
        except:
            font = pygame.font.SysFont('Arial', font_size - 6, bold=True)
            
        title_text = font.render("WORLD MAP", True, (210, 255, 255))
        shadow_text = font.render("WORLD MAP", True, (10, 15, 25))
        
        # Căn giữa chữ tại vùng biển phía dưới
        title_rect = title_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT - 43))
        shadow_rect = shadow_text.get_rect(center=(title_rect.centerx + 2, title_rect.centery + 2))
        
        # Vẽ banner nền mờ (Glassmorphism) ở vùng biển phía dưới
        banner_rect = pygame.Rect(self.WINDOW_WIDTH // 2 - 110, self.WINDOW_HEIGHT - 66, 220, 46)
        banner_surf = pygame.Surface((banner_rect.width, banner_rect.height), pygame.SRCALPHA)
        banner_surf.fill((15, 20, 30, 200)) # Nền xanh đen mờ trong suốt
        self.screen.blit(banner_surf, banner_rect.topleft)
        
        # Vẽ viền phát sáng màu xanh ngọc / Cyan mượt mà sắc nét
        pygame.gfxdraw.rectangle(self.screen, banner_rect, (0, 220, 220))
        # Viền chỉ tinh xảo bên trong
        inner_rect = banner_rect.inflate(-4, -4)
        pygame.gfxdraw.rectangle(self.screen, inner_rect, (30, 75, 110))
        
        self.screen.blit(shadow_text, shadow_rect)
        self.screen.blit(title_text, title_rect)

    def draw(self):
        self.screen.blit(self.bg_image, (0, 0))
        mouse_pos = pygame.mouse.get_pos()

        for i, rect in enumerate(self.buttons):
            level = self.levels[i]
            is_hover = rect.collidepoint(mouse_pos)

            radius = rect.width // 2
            
            # 1. Vẽ bóng đổ màu đen bên dưới Pin tròn (chống răng cưa)
            pygame.gfxdraw.filled_circle(self.screen, rect.centerx + 2, rect.centery + 2, radius, (10, 10, 15))
            pygame.gfxdraw.aacircle(self.screen, rect.centerx + 2, rect.centery + 2, radius, (10, 10, 15))

            if level["unlocked"]:
                # Nút xanh đen mờ khi mở khóa (Vẽ mượt mà bằng gfxdraw)
                fill_color = (25, 35, 55) if is_hover else (15, 20, 30)
                pygame.gfxdraw.filled_circle(self.screen, rect.centerx, rect.centery, radius, fill_color)
                pygame.gfxdraw.aacircle(self.screen, rect.centerx, rect.centery, radius, fill_color)

                # Viền tròn xanh ngọc / Cyan phát sáng
                border_color = (0, 255, 255) if is_hover else (0, 200, 200)
                pygame.gfxdraw.aacircle(self.screen, rect.centerx, rect.centery, radius, border_color)
                pygame.gfxdraw.aacircle(self.screen, rect.centerx, rect.centery, radius - 1, border_color)
                
                # Số thứ tự màn chơi
                text = self.font.render(str(level["id"]), True, (210, 255, 255))
                self.screen.blit(text, text.get_rect(center=rect.center))
            else:
                # Nút xám mờ khi bị khóa
                pygame.gfxdraw.filled_circle(self.screen, rect.centerx, rect.centery, radius, (40, 40, 50))
                pygame.gfxdraw.aacircle(self.screen, rect.centerx, rect.centery, radius, (40, 40, 50))
                
                pygame.gfxdraw.aacircle(self.screen, rect.centerx, rect.centery, radius, (80, 80, 90))
                pygame.gfxdraw.aacircle(self.screen, rect.centerx, rect.centery, radius - 1, (80, 80, 90))
                
                # Ổ khóa đỏ nhỏ ở giữa
                lock_w, lock_h = 24, 24
                lock_scaled = pygame.transform.smoothscale(self.lock_image, (lock_w, lock_h))
                lock_rect = lock_scaled.get_rect(center=rect.center)
                self.screen.blit(lock_scaled, lock_rect)

        self.draw_title()
        self.settings_button.draw()

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"

                elif event.type == pygame.KEYDOWN:
                    # Nhấn ESC để quay lại màn hình chào mừng chính
                    if event.key == pygame.K_ESCAPE:
                        return "background"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    result = self.settings_button.handle_event(event)
                    if result == "home":
                        return "background"

                    if not self.settings_button.settings_menu_open:
                        for i, rect in enumerate(self.buttons):
                            if rect.collidepoint(event.pos):
                                if self.levels[i]["unlocked"]:
                                    return f"level{self.levels[i]['id']}"  # ✅ Trả về chuỗi như "level2"
                                else:
                                    print("Màn này chưa mở!")

            self.draw()
            pygame.display.flip()
            clock.tick(60)