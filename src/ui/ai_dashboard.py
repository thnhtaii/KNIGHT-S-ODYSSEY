import pygame
import os
import math
import time

class AIDashboard:
    def __init__(self, screen, stats, stage_name=""):
        self.screen = screen
        self.stats = stats
        self.stage_name = stage_name
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()

        # Dùng font hệ thống Arial sắc nét, hỗ trợ tiếng Việt hoàn hảo và không bị lỗi ký tự
        self.title_font = pygame.font.SysFont('Arial', 24, bold=True)
        self.header_font = pygame.font.SysFont('Arial', 18, bold=True)
        self.text_font = pygame.font.SysFont('Arial', 16)
        self.prompt_font = pygame.font.SysFont('Arial', 14, italic=True)

    def draw(self):
        # 1. Vẽ lớp phủ tối làm mờ nền sau (Glassmorphism)
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((10, 10, 15, 230))  # Độ trong suốt tối màu
        self.screen.blit(overlay, (0, 0))

        # 2. Vẽ khung Popup chính ở trung tâm
        popup_width, popup_height = 700, 450
        px = (self.screen_width - popup_width) // 2
        py = (self.screen_height - popup_height) // 2
        popup_rect = pygame.Rect(px, py, popup_width, popup_height)

        # Nền popup xám đậm sang trọng
        pygame.draw.rect(self.screen, (24, 24, 32), popup_rect, border_radius=15)
        # Viền đỏ rực cá tính
        pygame.draw.rect(self.screen, (255, 80, 80), popup_rect, width=3, border_radius=15)

        # 3. Vẽ Tiêu đề
        title_text = "AI PERFORMANCE STATS"
        if self.stage_name:
            title_text += f" - {self.stage_name.upper()}"
        title_surf = self.title_font.render(title_text, True, (255, 80, 80))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, py + 40))
        self.screen.blit(title_surf, title_rect)

        # 4. Vẽ bảng thống kê dữ liệu các quái vật
        # Cấu hình các cột: Tên quái vật, Số lần tìm đường, Số lần chạm, Sát thương
        is_level1 = self.stage_name and "level 1" in self.stage_name.lower()
        is_level2 = self.stage_name and "level 2" in self.stage_name.lower()

        if is_level1:
            headers = ["Slime (Thuat toan)", "Luot tim duong", "Do dai duong (o)", "Sat thuong"]
            col_widths = [260, 150, 130, 100]
        elif is_level2:
            headers = ["Ice Wolf (Thuat toan)", "Do dai duong (o)", "Thoi gian (ms)", "Sat thuong"]
            col_widths = [260, 150, 130, 100]
        else:
            # Tự động điều chỉnh tiêu đề cột theo loại quái
            enemy_type = "Binh si"
            if self.stats:
                first_key = next(iter(self.stats.keys()))
                if "Zombie" in first_key:
                    enemy_type = "Zombie"
            headers = [f"{enemy_type} (Thuat toan)", "Luot tim duong", "Luot tiep can", "Sat thuong"]
            col_widths = [260, 150, 130, 100]

        col_x = [
            px + 30,
            px + 30 + col_widths[0],
            px + 30 + col_widths[0] + col_widths[1],
            px + 30 + col_widths[0] + col_widths[1] + col_widths[2]
        ]
        row_y_start = py + 90
        row_height = 36

        # Vẽ Header của bảng
        pygame.draw.rect(self.screen, (40, 40, 50), (px + 15, row_y_start, popup_width - 30, row_height), border_radius=5)
        
        for i, text in enumerate(headers):
            surf = self.header_font.render(text, True, (255, 255, 255))
            rect = surf.get_rect()
            if i > 0: # Căn giữa các cột số liệu
                rect.center = (col_x[i] + col_widths[i] // 2, row_y_start + row_height // 2)
            else: # Căn lề trái cột tên
                rect.midleft = (col_x[i], row_y_start + row_height // 2)
            self.screen.blit(surf, rect)

        # Lấy danh sách thống kê đã sắp xếp theo tên quái vật
        sorted_stats = sorted(self.stats.items())

        # Vẽ từng hàng dữ liệu của Zombie
        for idx, (name, data) in enumerate(sorted_stats):
            ry = row_y_start + row_height + 10 + idx * (row_height + 8)
            
            # Tô màu xen kẽ cho các dòng để dễ quan sát
            bg_color = (32, 32, 42) if idx % 2 == 0 else (28, 28, 36)
            pygame.draw.rect(self.screen, bg_color, (px + 15, ry, popup_width - 30, row_height), border_radius=5)

            # 1. Cột Tên quái vật (Định dạng lại cho đẹp mắt)
            display_name = name
            suffix = ""
            base_name = name
            if "_" in name:
                parts = name.split("_")
                if parts[-1].isdigit():
                    suffix = f" {parts[-1]}"
                    base_name = "_".join(parts[:-1])

            if base_name.startswith("slime_"):
                algo = base_name.replace("slime_", "").upper()
                display_name = f"Slime ({algo}{suffix})"
            elif base_name.startswith("wolf_"):
                algo = base_name.replace("wolf_", "").upper()
                if algo == "ASTAR":
                    algo = "A*"
                elif algo == "GREEDY":
                    algo = "Greedy"
                elif algo == "IDA_STAR":
                    algo = "IDA*"
                display_name = f"Ice Wolf ({algo}{suffix})"

            name_surf = self.text_font.render(display_name, True, (230, 230, 255))
            name_rect = name_surf.get_rect(midleft=(col_x[0], ry + row_height // 2))
            self.screen.blit(name_surf, name_rect)

            # Lấy các chỉ số tương ứng theo từng level
            if is_level1:
                # 2. Luot tim duong
                val1_text = str(data.get("paths_found", 0))
                # 3. Do dai duong trung binh (o)
                paths = data.get("paths_found", 0)
                tot_len = data.get("total_path_len", 0)
                avg_len = tot_len / paths if paths > 0 else 0
                val2_text = f"{avg_len:.1f}"
                # 4. Sat thuong
                val3_text = f"{data.get('damage_dealt', 0)} HP"
            elif is_level2:
                # 2. Do dai duong trung binh (o)
                paths = data.get("paths_found", 0)
                tot_len = data.get("total_path_len", 0)
                avg_len = tot_len / paths if paths > 0 else 0
                val1_text = f"{avg_len:.1f}"
                # 3. Thoi gian trung binh (ms)
                tot_time = data.get("total_time_ms", 0.0)
                avg_time = tot_time / paths if paths > 0 else 0.0
                val2_text = f"{avg_time:.3f} ms"
                # 4. Sat thuong
                val3_text = f"{data.get('damage_dealt', 0)} HP"
            else:
                # Mac dinh (Zombie Level 4)
                val1_text = str(data.get("paths_found", 0))
                val2_text = str(data.get("player_reached", 0))
                val3_text = f"{data.get('damage_dealt', 0)} HP"

            # 2. Cột giá trị 1
            val1_surf = self.text_font.render(val1_text, True, (150, 255, 150))
            val1_rect = val1_surf.get_rect(center=(col_x[1] + col_widths[1] // 2, ry + row_height // 2))
            self.screen.blit(val1_surf, val1_rect)

            # 3. Cột giá trị 2
            val2_surf = self.text_font.render(val2_text, True, (255, 200, 100))
            val2_rect = val2_surf.get_rect(center=(col_x[2] + col_widths[2] // 2, ry + row_height // 2))
            self.screen.blit(val2_surf, val2_rect)

            # 4. Cột giá trị 3
            val3_surf = self.text_font.render(val3_text, True, (255, 100, 100))
            val3_rect = val3_surf.get_rect(center=(col_x[3] + col_widths[3] // 2, ry + row_height // 2))
            self.screen.blit(val3_surf, val3_rect)

        # 5. Vẽ gợi ý bấm phím ở dưới cùng (Nhấp nháy mờ dần)
        pulse = int(127 + 128 * math.sin(time.time() * 6))
        prompt_color = (pulse, pulse, pulse)
        prompt_surf = self.prompt_font.render("[ Nhan phim ENTER hoac Click chuot de tiep tuc ]", True, prompt_color)
        prompt_rect = prompt_surf.get_rect(center=(self.screen_width // 2, py + popup_height - 35))
        self.screen.blit(prompt_surf, prompt_rect)

    def run(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE, pygame.K_ESCAPE]:
                        running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    running = False

            self.draw()
            pygame.display.flip()
            clock.tick(60)
        return "continue"
