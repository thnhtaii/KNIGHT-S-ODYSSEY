import pygame
import os

class CustomHealthBar:
    def __init__(self, x, y, width, height, max_health):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = max_health
        self.current_health = max_health

        # Font cho text hiển thị lượng máu
        self.font = pygame.font.SysFont('Arial', int(height * 0.38), bold=True)

        # Load file frame custom (đã được cắt viền trắng)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(os.path.dirname(current_dir))
        frame_path = os.path.join(project_root, 'assets', 'backgrounds', 'custom_health_bar_frame.png')
        
        try:
            self.original_frame = pygame.image.load(frame_path).convert_alpha()
            # Scale frame theo kích thước mong muốn
            self.frame_image = pygame.transform.scale(self.original_frame, (width, height))
        except Exception as e:
            print(f"[ERROR] Failed to load custom health bar frame: {e}")
            self.frame_image = None

    def set_health(self, health):
        self.current_health = max(0, min(self.max_health, health))

    def draw(self, surface):
        if self.frame_image is None:
            # Fallback nếu hình ảnh lỗi không load được
            outer_rect = pygame.Rect(self.x, self.y, self.width, self.height)
            pygame.draw.rect(surface, (0, 0, 0), outer_rect, border_radius=8)
            inner_rect = pygame.Rect(self.x + 2, self.y + 2, self.width - 4, self.height - 4)
            pygame.draw.rect(surface, (40, 40, 40), inner_rect, border_radius=6)
            health_ratio = self.current_health / self.max_health
            health_width = int((self.width - 4) * health_ratio)
            health_rect = pygame.Rect(self.x + 2, self.y + 2, health_width, self.height - 4)
            pygame.draw.rect(surface, (220, 20, 60), health_rect, border_radius=6)
            text = f"{int(self.current_health)}/{int(self.max_health)}"
            text_surf = self.font.render(text, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
            surface.blit(text_surf, text_rect)
            return

        # Tính tỷ lệ scale dựa trên ảnh gốc (893x235)
        scale_x = self.width / 893.0
        scale_y = self.height / 235.0

        # Tọa độ vùng thanh đỏ trong ảnh gốc: left=58, top=67, width=776, height=98
        fill_left = int(58 * scale_x)
        fill_top = int(67 * scale_y)
        fill_max_width = int(776 * scale_x)
        fill_height = int(98 * scale_y)

        # Tính chiều rộng hiện tại của thanh đỏ theo tỷ lệ máu
        health_ratio = self.current_health / self.max_health
        current_fill_width = int(fill_max_width * health_ratio)

        # Tạo surface phụ có hỗ trợ alpha để vẽ toàn bộ thanh máu
        temp_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # Vẽ thanh máu đỏ lên surface phụ (tọa độ tương đối từ 0)
        if current_fill_width > 0:
            red_bar_rect = pygame.Rect(fill_left, fill_top, current_fill_width, fill_height)
            # Màu đỏ giống trong ảnh mẫu: (231, 28, 62)
            pygame.draw.rect(temp_surface, (231, 28, 62), red_bar_rect)

        # Vẽ frame đè lên trên thanh đỏ trên surface phụ
        temp_surface.blit(self.frame_image, (0, 0))

        # Vẽ text "máu/máu tối đa" căn giữa thanh máu đỏ trên surface phụ
        text = f"{int(self.current_health)}/{int(self.max_health)}"
        text_surf = self.font.render(text, True, (255, 255, 255))
        
        # Căn chính giữa vùng hiển thị của thanh máu
        center_x = fill_left + fill_max_width // 2
        center_y = fill_top + fill_height // 2
        text_rect = text_surf.get_rect(center=(center_x, center_y))
        temp_surface.blit(text_surf, text_rect)

        # Thiết lập độ trong suốt cho surface phụ (160/255 ~ 63% opacity)
        # Để chìm chìm vừa đủ, hài hòa với bối cảnh game rừng cây
        temp_surface.set_alpha(160)

        # Vẽ surface phụ lên màn hình game chính
        surface.blit(temp_surface, (self.x, self.y))
