import pygame
import sys

class AIStatsLevel6Screen:
    def __init__(self, screen, stats):
        self.screen = screen
        self.stats = stats # Dictionary of stats
        self.font_title = pygame.font.SysFont("Arial", 40, bold=True)
        self.font_header = pygame.font.SysFont("Arial", 22, bold=True)
        self.font_text = pygame.font.SysFont("Arial", 20)
        self.font_small = pygame.font.SysFont("Arial", 16, italic=True)
        
        self.width = 740
        self.height = 400
        self.rect = pygame.Rect(
            (screen.get_width() - self.width) // 2,
            (screen.get_height() - self.height) // 2,
            self.width,
            self.height
        )

    def draw(self):
        # Semi-transparent background
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Border box
        pygame.draw.rect(self.screen, (25, 25, 30), self.rect, border_radius=15)
        pygame.draw.rect(self.screen, (255, 60, 60), self.rect, 3, border_radius=15)
        
        # Title
        title = self.font_title.render("AI PERFORMANCE STATS - LEVEL 6", True, (255, 60, 60))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, self.rect.y + 40))
        self.screen.blit(title, title_rect)
        
        # Columns
        col_x = [self.rect.x + 30, self.rect.x + 280, self.rect.x + 460, self.rect.x + 620]
        headers = ["Thuật toán", "Tổng số Node", "Nhánh bị cắt", "Sát thương"]
        
        # Draw Headers
        header_y = self.rect.y + 100
        pygame.draw.line(self.screen, (100, 100, 100), (self.rect.x + 20, header_y - 10), (self.rect.x + self.rect.width - 20, header_y - 10), 1)
        for i, text in enumerate(headers):
            surf = self.font_header.render(text, True, (200, 200, 200))
            if i > 0:
                surf_rect = surf.get_rect(centerx=col_x[i] + 40, y=header_y)
                self.screen.blit(surf, surf_rect)
            else:
                self.screen.blit(surf, (col_x[i], header_y))
                
        pygame.draw.line(self.screen, (100, 100, 100), (self.rect.x + 20, header_y + 40), (self.rect.x + self.rect.width - 20, header_y + 40), 1)
        
        # Draw Rows
        rows = [
            ("Phase 1 (Minimax)", str(self.stats.get("total_minimax_nodes", 0)), "N/A", f"{self.stats.get('damage_phase1', 0)} HP"),
            ("Phase 2 (Alpha-Beta)", str(self.stats.get("total_alphabeta_nodes", 0)), str(self.stats.get("total_alphabeta_pruned", 0)), f"{self.stats.get('damage_phase2', 0)} HP"),
            ("Phase 3 (Expectimax)", str(self.stats.get("total_expectimax_nodes", 0)), "N/A", f"{self.stats.get('damage_phase3', 0)} HP")
        ]
        
        start_y = header_y + 60
        for r_idx, row in enumerate(rows):
            # Row background
            row_rect = pygame.Rect(self.rect.x + 20, start_y + r_idx * 50 - 10, self.rect.width - 40, 45)
            if r_idx % 2 == 0:
                pygame.draw.rect(self.screen, (40, 40, 45), row_rect, border_radius=5)
            else:
                pygame.draw.rect(self.screen, (30, 30, 35), row_rect, border_radius=5)
                
            for c_idx, text in enumerate(row):
                color = (255, 255, 255)
                if c_idx == 0: color = (200, 200, 200) # Name
                elif c_idx == 1: color = (100, 255, 100) # Nodes
                elif c_idx == 2: color = (255, 200, 100) # Pruned
                elif c_idx == 3: color = (255, 100, 100) # Damage
                
                surf = self.font_text.render(text, True, color)
                # Center align for columns 1, 2, 3
                if c_idx > 0:
                    surf_rect = surf.get_rect(centerx=col_x[c_idx] + 40, centery=row_rect.centery)
                    self.screen.blit(surf, surf_rect)
                else:
                    self.screen.blit(surf, (col_x[c_idx], row_rect.centery - surf.get_height() // 2))
                    
        # Footer
        footer = self.font_small.render("[ Nhan phim ENTER hoac Click chuot de tiep tuc ]", True, (150, 150, 150))
        footer_rect = footer.get_rect(center=(self.screen.get_width() // 2, self.rect.bottom - 30))
        self.screen.blit(footer, footer_rect)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            self.draw()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                        return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return
