class Camera:
    def __init__(self, screen_width, screen_height, map_width, map_height):
        self.offset_x = 0
        self.offset_y = 0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.map_width = map_width
        self.map_height = map_height

    def update(self, target_rect):
        # Theo dõi nhân vật (target_rect)
        self.offset_x = target_rect.centerx - self.screen_width // 2
        self.offset_y = target_rect.centery - self.screen_height // 2

        # Giới hạn camera trong bản đồ
        self.offset_x = max(0, min(self.offset_x, self.map_width - self.screen_width))
        self.offset_y = max(0, min(self.offset_y, self.map_height - self.screen_height))

    def apply(self, rect):
        # Dịch chuyển đối tượng theo camera
        return rect.move(-self.offset_x, -self.offset_y)