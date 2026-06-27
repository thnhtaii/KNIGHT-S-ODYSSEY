import pygame
import os

class CSPMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont('Arial', 36, bold=True)
        self.small_font = pygame.font.SysFont('Arial', 24)
        self.options = ["backtracking", "ac-3", "min-conflicts"]
        self.selected_index = 0
        self.running = True

    def run(self):
        clock = pygame.time.Clock()
        while self.running:
            self.screen.fill((30, 30, 30))
            
            title_text = self.font.render("Select CSP Algorithm for Enemy AI", True, (255, 255, 255))
            self.screen.blit(title_text, (100, 100))

            for i, opt in enumerate(self.options):
                color = (255, 255, 0) if i == self.selected_index else (200, 200, 200)
                text = self.font.render(f"{i+1}. {opt.upper()}", True, color)
                self.screen.blit(text, (150, 200 + i * 50))
                
            inst_text = self.small_font.render("Use UP/DOWN arrows to select, ENTER to confirm.", True, (150, 150, 150))
            self.screen.blit(inst_text, (100, 400))

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(self.options)
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        return self.options[self.selected_index]
                    elif event.key == pygame.K_ESCAPE:
                        return "menu"
            
            clock.tick(60)
        return None
