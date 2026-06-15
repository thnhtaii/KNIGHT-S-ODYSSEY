import pygame

class HealthBar:
    def __init__(self, x, y, width, height, max_health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health
        self.current_health = max_health

        # Font chữ cho thanh máu
        self.font = pygame.font.SysFont('Arial', int(height * 0.8), bold=True)

        # Tạo icon trái tim
        self.heart_surface = pygame.Surface((height, height), pygame.SRCALPHA)
        pygame.draw.polygon(self.heart_surface, (220, 20, 60), [
            (height // 2, height - 4),
            (4, height // 2),
            (height // 2, 4),
            (height - 4, height // 2)
        ])
        pygame.draw.circle(self.heart_surface, (220, 20, 60), (height // 3, height // 3), height // 3)
        pygame.draw.circle(self.heart_surface, (220, 20, 60), (2 * height // 3, height // 3), height // 3)

    def set_health(self, health):
        self.current_health = max(0, min(self.max_health, health))  # Giới hạn giá trị máu trong khoảng [0, max_health]

    def draw(self, surface):
        # Vẽ viền ngoài
        outer_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, (0, 0, 0), outer_rect, border_radius=8)

        # Vẽ nền thanh máu
        inner_rect = pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)
        pygame.draw.rect(surface, (40, 40, 40), inner_rect, border_radius=6)

        # Vẽ thanh máu
        health_ratio = self.current_health / self.max_health
        health_width = int((self.width - 4) * health_ratio)
        health_rect = pygame.Rect(self.x + 2, self.y + 2, health_width, self.height - 4)
        pygame.draw.rect(surface, (220, 20, 60), health_rect, border_radius=6)

        # Vẽ text hiển thị máu
        text = f"{int(self.current_health)}/{int(self.max_health)}"
        text_surf = self.font.render(text, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text_surf, text_rect)
