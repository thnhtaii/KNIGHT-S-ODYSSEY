import pygame
import os

class GameOverScreen:
    def __init__(self, screen):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # ✅ Load custom font từ file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(current_dir, '..', '..'))
        font_path = os.path.join(project_root, 'assets', 'fonts', 'RubikGlitch-Regular.ttf')

        self.font = pygame.font.Font(font_path, 72)
        self.button_font = pygame.font.Font(font_path, 36)

        # Game Over text
        self.text = self.font.render("GAME OVER", True, (255, 0, 0))
        self.text_rect = self.text.get_rect(center=(self.screen_width // 2, self.screen_height // 3))

        # Back button
        self.button_text = self.button_font.render("Back", True, (0, 0, 0))
        self.button_bg = pygame.Rect(self.screen_width // 2 - 75, self.screen_height // 2, 150, 60)
        self.button_text_rect = self.button_text.get_rect(center=self.button_bg.center)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if self.button_bg.collidepoint(event.pos):
                        return "menu"

            self.draw()
            pygame.display.flip()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.text, self.text_rect)

        pygame.draw.rect(self.screen, (255, 255, 102), self.button_bg, border_radius=10)
        pygame.draw.rect(self.screen, (0, 0, 0), self.button_bg, 3, border_radius=10)
        self.screen.blit(self.button_text, self.button_text_rect)
