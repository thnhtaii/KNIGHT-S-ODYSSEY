import pygame
import sys
import os

class SettingsMenu:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        # Thu nhỏ khung menu
        self.menu_rect = pygame.Rect(0, 0, 150, 300)  # width, height (giảm kích thước)
        self.menu_rect.center = (screen.get_width() // 2, screen.get_height() // 2)  # Căn giữa màn hình

        # Tải icon cho các nút
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))

        self.home_icon = pygame.image.load(os.path.join(project_root, 'assets', 'icons', 'home_icon.png'))
        self.home_icon = pygame.transform.scale(self.home_icon, (50, 50))  # Resize icon Home (nhỏ hơn)

        self.volume_icon = pygame.image.load(os.path.join(project_root, 'assets', 'icons', 'volume_icon.png'))
        self.volume_icon = pygame.transform.scale(self.volume_icon, (50, 50))  # Resize icon Volume (nhỏ hơn)

        self.back_icon = pygame.image.load(os.path.join(project_root, 'assets', 'icons', 'back_icon.png'))
        self.back_icon = pygame.transform.scale(self.back_icon, (50, 50))  # Resize icon Back (nhỏ hơn)

        # Căn chỉnh lại vị trí các nút
        self.home_button = self.home_icon.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 70))
        self.volume_button = self.volume_icon.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 150))
        self.back_button = self.back_icon.get_rect(center=(self.menu_rect.centerx, self.menu_rect.top + 230))

        # Tạo nút "Back"
        self.back_button_rect = pygame.Rect(350, 500, 100, 40)  # Vị trí và kích thước nút Back
        self.font = pygame.font.Font(None, 36)  # Font chữ cho nút Back

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.home_button.collidepoint(event.pos):
                        return "menu"  # Quay lại menu chính
                    elif self.volume_button.collidepoint(event.pos):
                        print("Volume settings clicked!")  # Xử lý âm thanh (hiện tại chỉ in ra console)
                    elif self.back_button.collidepoint(event.pos):
                        return "back"  # Quay lại màn chơi
                    elif self.back_button_rect.collidepoint(event.pos):
                        return "back"  # Quay lại màn chơi

            # Vẽ menu cài đặt
            self.draw_menu()

            pygame.display.flip()

    def draw_menu(self):
        # Vẽ khung menu (bo góc và có viền)
        pygame.draw.rect(self.screen, (0, 0, 0), self.menu_rect, border_radius=15)  # Viền đen
        pygame.draw.rect(self.screen, (255, 255, 200), self.menu_rect.inflate(-8, -8), border_radius=15)  # Menu màu vàng nhạt

        # Vẽ icon Home
        self.screen.blit(self.home_icon, self.home_button.topleft)

        # Vẽ icon Volume
        self.screen.blit(self.volume_icon, self.volume_button.topleft)

        # Vẽ icon Back
        self.screen.blit(self.back_icon, self.back_button.topleft)

    

    def draw(self):
        self.screen.fill((200, 200, 200))  # Màu nền giao diện cài đặt

      

