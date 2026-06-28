import random
from collections import deque

class CSPSurround:
    def __init__(self, map_width, map_height, grid, is_walkable_func=None):
        self.map_width = map_width
        self.map_height = map_height
        self.grid = grid
        self.is_walkable_func = is_walkable_func
        
    def get_valid_neighbors(self, px, py):
        """Lấy các vị trí hợp lệ xung quanh người chơi (ko phải tường)."""
        valid = []
        for nx, ny in [(px-1, py), (px+1, py), (px, py-1), (px, py+1), (px-2, py), (px+2, py)]:
            if 0 <= nx < self.map_width and 0 <= ny < self.map_height:
                if self.is_walkable_func:
                    if self.is_walkable_func(nx, ny):
                        valid.append((nx, ny))
                else:
                    if self.grid[ny][nx] == 0: # Fallback
                        valid.append((nx, ny))
        return valid

    def solve_backtracking(self, player_pos, boss_positions):
        """Thuật toán Backtracking thuần tuý. Trả về (targets, time_ms, iterations)"""
        import time
        start_time = time.perf_counter()
        iterations = 0

        px, py = player_pos
        base_domain = self.get_valid_neighbors(px, py)
        if len(base_domain) < len(boss_positions):
            base_domain.append((px, py))
            
        assignment = {}
        def backtrack(boss_idx):
            nonlocal iterations
            iterations += 1
            if boss_idx == len(boss_positions):
                return True
            
            # Ưu tiên các ô gần boss hiện tại nhất
            bx, by = boss_positions[boss_idx]
            sorted_domain = sorted(base_domain, key=lambda p: abs(p[0] - bx) + abs(p[1] - by))
            
            for val in sorted_domain:
                if val not in assignment.values():
                    assignment[boss_idx] = val
                    if backtrack(boss_idx + 1):
                        return True
                    del assignment[boss_idx]
            return False
            
        backtrack(0)
        targets = [assignment.get(i, boss_positions[i]) for i in range(len(boss_positions))]
        time_ms = (time.perf_counter() - start_time) * 1000
        return targets, time_ms, iterations

    def solve_ac3(self, player_pos, boss_positions):
        """Sử dụng AC-3 để rút gọn domain. Trả về (targets, time_ms, iterations)"""
        import time
        start_time = time.perf_counter()
        iterations = 0

        px, py = player_pos
        base_domain = self.get_valid_neighbors(px, py)
        if len(base_domain) < len(boss_positions):
            base_domain.append((px, py))
            
        domains = {i: list(base_domain) for i in range(len(boss_positions))}
        
        # Tạo danh sách các ràng buộc AllDiff (các boss không được trùng vị trí)
        arcs = []
        for i in range(len(boss_positions)):
            for j in range(len(boss_positions)):
                if i != j:
                    arcs.append((i, j))
                    
        from collections import deque
        queue = deque(arcs)
        
        def revise(xi, xj):
            revised = False
            for x in domains[xi][:]:
                # Cần tồn tại ít nhất 1 giá trị y trong domains[xj] khác x
                if not any(y != x for y in domains[xj]):
                    domains[xi].remove(x)
                    revised = True
            return revised
            
        while queue:
            iterations += 1
            xi, xj = queue.popleft()
            if revise(xi, xj):
                if not domains[xi]:
                    break
                for xk in range(len(boss_positions)):
                    if xk != xi and xk != xj:
                        queue.append((xk, xi))
                        
        # Gán theo domain đã rút gọn (đơn giản hoá bằng cách lấy phần tử hợp lệ gần nhất)
        assignment = {}
        for i in range(len(boss_positions)):
            bx, by = boss_positions[i]
            sorted_domain = sorted(domains[i], key=lambda p: abs(p[0] - bx) + abs(p[1] - by))
            for val in sorted_domain:
                if val not in assignment.values():
                    assignment[i] = val
                    break
            if i not in assignment:
                assignment[i] = boss_positions[i] # Fallback
                
        targets = [assignment[i] for i in range(len(boss_positions))]
        time_ms = (time.perf_counter() - start_time) * 1000
        return targets, time_ms, iterations

    def solve_min_conflicts(self, player_pos, boss_positions, max_steps=100):
        """Thuật toán Min-Conflicts. Trả về (targets, time_ms, iterations)"""
        import time
        start_time = time.perf_counter()
        iterations = 0

        px, py = player_pos
        domain = self.get_valid_neighbors(px, py)
        if len(domain) < len(boss_positions):
            domain.append((px, py))
            
        # Khởi tạo ngẫu nhiên nhưng ưu tiên gần boss
        assignment = {}
        for i in range(len(boss_positions)):
            bx, by = boss_positions[i]
            sorted_domain = sorted(domain, key=lambda p: abs(p[0] - bx) + abs(p[1] - by))
            assignment[i] = sorted_domain[0]
        
        def count_conflicts(boss_idx, val):
            return sum(1 for j in range(len(boss_positions)) if j != boss_idx and assignment[j] == val)
            
        for _ in range(max_steps):
            iterations += 1
            conflicted_vars = [i for i in range(len(boss_positions)) if count_conflicts(i, assignment[i]) > 0]
            if not conflicted_vars:
                break # Đã giải xong
                
            import random
            var = random.choice(conflicted_vars)
            
            # Tìm giá trị giảm thiểu conflict
            min_c = float('inf')
            best_vals = []
            for val in domain:
                c = count_conflicts(var, val)
                if c < min_c:
                    min_c = c
                    best_vals = [val]
                elif c == min_c:
                    best_vals.append(val)
                    
            bx, by = boss_positions[var]
            sorted_best_vals = sorted(best_vals, key=lambda p: abs(p[0] - bx) + abs(p[1] - by))
            assignment[var] = sorted_best_vals[0]
            
        targets = [assignment[i] for i in range(len(boss_positions))]
        time_ms = (time.perf_counter() - start_time) * 1000
        return targets, time_ms, iterations

