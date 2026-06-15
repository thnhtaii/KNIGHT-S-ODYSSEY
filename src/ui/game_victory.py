import pygame
import os

class GameVictoryScreen:
    def __init__(self, screen):
        self.screen = screen
        self.running = True

        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Tải font Rubik Glitch hoặc mặc định nếu thiếu
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        font_path = os.path.join(project_root, "assets", "fonts", "RubikGlitch-Regular.ttf")

        if os.path.exists(font_path):
            self.font_win = pygame.font.Font(font_path, 72)
            self.font_button = pygame.font.Font(font_path, 32)
        else:
            self.font_win = pygame.font.SysFont('Arial', 72, bold=True)
            self.font_button = pygame.font.SysFont('Arial', 32, bold=True)

        self.win_text = self.font_win.render("YOU WIN!", True, (0, 255, 0))
        self.win_rect = self.win_text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))

        # Nút back đơn giản
        self.back_button_rect = pygame.Rect(0, 0, 140, 50)
        self.back_button_rect.center = (self.screen_width // 2, self.screen_height // 2 + 100)
        self.back_button_text = self.font_button.render("Back", True, (0, 0, 0))
        self.back_button_text_rect = self.back_button_text.get_rect(center=self.back_button_rect.center)

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_button_rect.collidepoint(event.pos):
                        self.running = False
                        return "menu"

            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill((0, 0, 0))

        # Vẽ dòng chữ YOU WIN!
        self.screen.blit(self.win_text, self.win_rect)

        # Vẽ nút Back
        pygame.draw.rect(self.screen, (255, 255, 0), self.back_button_rect, border_radius=12)         # Viền
        pygame.draw.rect(self.screen, (255, 255, 200), self.back_button_rect.inflate(-6, -6), border_radius=12)  # Nền
        self.screen.blit(self.back_button_text, self.back_button_text_rect)