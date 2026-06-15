import pygame
import os

class SettingsButton:
    def __init__(self, screen):
        self.screen = screen
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = screen.get_size()
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        # Load icon setting
        settings_path = os.path.join(project_root, 'assets', 'icons', 'settings_icon.png')
        home_icon_path = os.path.join(project_root, 'assets', 'icons', 'home_icon.png')
        volume_icon_path = os.path.join(project_root, 'assets', 'icons', 'volume_icon.png')
        mute_icon_path = os.path.join(project_root, 'assets', 'icons', 'mute_icon.png')

        try:
            self.original_settings_image = pygame.image.load(settings_path).convert_alpha()
        except FileNotFoundError:
            print(f"Could not find settings icon at: {settings_path}")
            self.original_settings_image = pygame.Surface((32, 32))
            self.original_settings_image.fill((0, 255, 255))

        try:
            self.home_icon = pygame.image.load(home_icon_path).convert_alpha()
        except FileNotFoundError:
            print(f"Could not find home icon at: {home_icon_path}")
            self.home_icon = pygame.Surface((64, 64))
            self.home_icon.fill((255, 0, 0))

        try:
            self.volume_icon = pygame.image.load(volume_icon_path).convert_alpha()
        except FileNotFoundError:
            print(f"Could not find volume icon at: {volume_icon_path}")
            self.volume_icon = pygame.Surface((64, 64))
            self.volume_icon.fill((0, 0, 255))

        try:
            self.mute_icon = pygame.image.load(mute_icon_path).convert_alpha()
        except FileNotFoundError:
            print(f"Could not find mute icon at: {mute_icon_path}")
            self.mute_icon = pygame.Surface((64, 64))
            self.mute_icon.fill((128, 128, 128))

        self.is_muted = False
        self.settings_menu_open = False
        self.update_button()

    def update_button(self):
        size = (32, 32)
        self.settings_button_image = pygame.transform.scale(self.original_settings_image, size)
        self.settings_button_rect = self.settings_button_image.get_rect(topright=(self.WINDOW_WIDTH - 20, 20))

    def draw(self):
        self.screen.blit(self.settings_button_image, self.settings_button_rect)
        if self.settings_menu_open:
            self.draw_settings_menu()

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.settings_button_rect.collidepoint(event.pos):
                self.settings_menu_open = not self.settings_menu_open
                return None
            if self.settings_menu_open:
                if hasattr(self, 'home_button_rect') and self.home_button_rect.collidepoint(event.pos):
                    print("Clicked Home button!")
                    return "home"
                if hasattr(self, 'volume_button_rect') and self.volume_button_rect.collidepoint(event.pos):
                    self.is_muted = not self.is_muted
                if self.is_muted:
                    pygame.mixer.music.pause()
                else:
                    pygame.mixer.music.unpause()
        return None
    
    def update_position(self, screen):
        self.screen = screen
        self.WINDOW_WIDTH, self.WINDOW_HEIGHT = self.screen.get_size()

        # Đặt lại vị trí nút Setting
        self.settings_button_rect.width = 32
        self.settings_button_rect.height = 32
        self.settings_button_rect.topright = (self.WINDOW_WIDTH - 20, 20)


        # (Nếu popup mở thì cũng tính lại center popup ở giữa màn hình)
        if self.settings_menu_open:
            popup_width, popup_height = 300, 200
            self.popup_rect = pygame.Rect(
                (self.WINDOW_WIDTH - popup_width) // 2,
                (self.WINDOW_HEIGHT - popup_height) // 2,
                popup_width,
                popup_height
            )


    def draw_settings_menu(self):
        popup_width, popup_height = 200, 300
        popup_rect = pygame.Rect(
            (self.WINDOW_WIDTH - popup_width) // 2,
            (self.WINDOW_HEIGHT - popup_height) // 2,
            popup_width,
            popup_height
        )
        pygame.draw.rect(self.screen, (255, 255, 153), popup_rect, border_radius=15)
        pygame.draw.rect(self.screen, (50, 50, 50), popup_rect, width=4, border_radius=15)

        # Home button
        home_icon_scaled = pygame.transform.scale(self.home_icon, (64, 64))
        self.home_button_rect = home_icon_scaled.get_rect(center=(popup_rect.centerx, popup_rect.top + 100))
        self.screen.blit(home_icon_scaled, self.home_button_rect)

        # Volume or Mute button
        if self.is_muted:
            volume_icon_scaled = pygame.transform.scale(self.mute_icon, (64, 64))
        else:
            volume_icon_scaled = pygame.transform.scale(self.volume_icon, (64, 64))
        self.volume_button_rect = volume_icon_scaled.get_rect(center=(popup_rect.centerx, popup_rect.top + 200))
        self.screen.blit(volume_icon_scaled, self.volume_button_rect)
