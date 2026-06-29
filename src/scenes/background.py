import pygame
import os
from src.scenes.menu import Menu
from src.components.settings_button import SettingsButton
from src.components.music_manager import MusicManager

class Background:
    def __init__(self, screen):
        self.screen = screen
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 608
        self.running = True
        self.button_pressed = False
        self.settings_button = SettingsButton(self.screen)
        self.music_manager = MusicManager()

        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        bg_path = os.path.join(project_root, 'assets', 'backgrounds', '1.png')
        button_path = os.path.join(project_root, 'assets', 'icons', 'start_button.png')

        music_path = os.path.join(project_root, 'assets', 'audio', 'music_theme', 'MusicMenu.mp3')
        self.music_manager.play_music(music_path)

        try:
            self.original_bg_image = pygame.image.load(bg_path)
            self.update_background_size()
        except FileNotFoundError:
            print(f"Could not find background image at: {bg_path}")
            raise

        try:
            self.original_button_image = pygame.image.load(button_path).convert_alpha()
        except FileNotFoundError:
            print(f"Could not find button image at: {button_path}")
            self.original_button_image = pygame.Surface((250, 200))
            self.original_button_image.fill((0, 255, 0))

        self.update_button_image()

        self.title_font_path = os.path.join(project_root, 'assets', 'fonts', 'RubikGlitch-Regular.ttf')
        self.text_font_path = os.path.join(project_root, 'assets', 'fonts', 'dpcomic.ttf')
        self.update_font_size()

    def update_background_size(self):
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = 800, 608
        self.bg_image = pygame.transform.scale(self.original_bg_image, (self.WINDOW_WIDTH, self.WINDOW_HEIGHT))

    def update_font_size(self):
        title_size = max(65, self.WINDOW_HEIGHT // 7)
        text_size = max(20, self.WINDOW_HEIGHT // 18)
        try:
            self.title_font = pygame.font.Font(self.title_font_path, title_size)
            self.text_font = pygame.font.Font(self.text_font_path, text_size)
        except:
            self.title_font = pygame.font.Font(None, title_size)
            self.text_font = pygame.font.Font(None, text_size)

    def update_button_image(self):
        size = (90, 30) if self.button_pressed else (110, 38)
        self.start_button_image = pygame.transform.scale(self.original_button_image, size)
        self.start_button_rect = self.start_button_image.get_rect(center=(self.WINDOW_WIDTH // 2 , self.WINDOW_HEIGHT - 100))

    def draw_background(self):
        self.screen.blit(self.bg_image, (0, 0))

    def draw_text(self):
        pass # The title "KNIGHT'S ODYSSEY" is already drawn directly on the new background image!

    def draw_button(self):
        rect = self.start_button_rect
        
        # 1. Vẽ bóng đổ màu đen bên dưới (tạo chiều sâu 3D)
        pygame.draw.rect(self.screen, (5, 5, 10), (rect.x + 3, rect.y + 3, rect.width, rect.height), border_radius=4)
        
        # 2. Màu nền nút (Màu xanh đen/navy mờ sang trọng khớp với tuyết/bóng tối)
        fill_color = (15, 20, 30) if self.button_pressed else (22, 28, 42)
        pygame.draw.rect(self.screen, fill_color, rect, border_radius=4)
        
        # 3. Viền nút màu xanh ngọc / Cyan phát sáng
        border_color = (0, 180, 180) if self.button_pressed else (0, 240, 240)
        pygame.draw.rect(self.screen, border_color, rect, width=2, border_radius=4)
        
        # Viền nhỏ bên trong tạo cảm giác ma thuật
        inner_rect = rect.inflate(-6, -6)
        pygame.draw.rect(self.screen, (30, 60, 80), inner_rect, width=1, border_radius=2)
        
        # 4. Vẽ chữ START với màu xanh băng tuyết (Ice Blue) tương phản cực cao
        text_color = (0, 240, 240) if self.button_pressed else (210, 255, 255)
        text = self.text_font.render("START", True, text_color)
        text_rect = text.get_rect(center=rect.center)
        self.screen.blit(text, text_rect)

    def run(self):
        clock = pygame.time.Clock()
        next_scene = None

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    next_scene = "quit"

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.settings_button.settings_menu_open:
                        result = self.settings_button.handle_event(event)
                        if result == "home":
                            self.running = False
                            next_scene = "menu"
                        continue

                    if self.start_button_rect.collidepoint(event.pos):
                        self.button_pressed = True
                        self.update_button_image()

                elif event.type == pygame.MOUSEBUTTONUP:
                    if not self.settings_button.settings_menu_open:
                        if self.button_pressed and self.start_button_rect.collidepoint(event.pos):
                            self.running = False
                            next_scene = "menu"
                        self.button_pressed = False
                        self.update_button_image()

                result = self.settings_button.handle_event(event)
                if result == "home":
                    self.running = False
                    next_scene = "menu"

            self.draw_background()
            self.draw_button()
            self.draw_text()
            self.settings_button.draw()
            pygame.display.flip()
            clock.tick(60)

        return next_scene