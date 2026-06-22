from collections import deque
import heapq
import random

def bfs_path(start, goal, grid):
    """BFS với Early Goal Test - kiểm tra mục tiêu ngay khi sinh node con"""
    rows, cols = len(grid), len(grid[0])

    if not (0 <= start[0] < cols and 0 <= start[1] < rows and
            0 <= goal[0] < cols and 0 <= goal[1] < rows):
        print(f"[BFS ERROR] Invalid start or goal: start={start}, goal={goal}")
        return []

    if start == goal:
        return []

    visited = [[False for _ in range(cols)] for _ in range(rows)]
    prev = [[None for _ in range(cols)] for _ in range(rows)]

    queue = deque()
    queue.append(start)
    visited[start[1]][start[0]] = True

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    found = False

    while queue:
        x, y = queue.popleft()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx] and grid[ny][nx] == 0:
                visited[ny][nx] = True
                prev[ny][nx] = (x, y)
                if (nx, ny) == goal:  # Early Goal Test
                    found = True
                    break
                queue.append((nx, ny))
        if found:
            break

    if not found:
        return []

    path = []
    at = goal
    while at != start:
        if not (0 <= at[0] < cols and 0 <= at[1] < rows):
            return []
        path.append(at)
        at = prev[at[1]][at[0]]
        if at is None:
            return []
    path.reverse()
    return path


def dfs_path(start, goal, grid):
    """DFS với Early Goal Test - kiểm tra mục tiêu ngay khi sinh node con"""
    rows, cols = len(grid), len(grid[0])

    if not (0 <= start[0] < cols and 0 <= start[1] < rows and
            0 <= goal[0] < cols and 0 <= goal[1] < rows):
        return []

    if start == goal:
        return []

    visited = [[False for _ in range(cols)] for _ in range(rows)]
    prev = [[None for _ in range(cols)] for _ in range(rows)]

    stack = [start]
    visited[start[1]][start[0]] = True

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    found = False

    while stack:
        x, y = stack.pop()
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and not visited[ny][nx] and grid[ny][nx] == 0:
                visited[ny][nx] = True
                prev[ny][nx] = (x, y)
                if (nx, ny) == goal:  # Early Goal Test
                    found = True
                    break
                stack.append((nx, ny))
        if found:
            break

    if not found:
        return []

    path = []
    at = goal
    while at != start:
        if not (0 <= at[0] < cols and 0 <= at[1] < rows):
            return []
        path.append(at)
        at = prev[at[1]][at[0]]
        if at is None:
            return []
    path.reverse()
    return path


def ucs_path(start, goal, grid):
    """UCS - Uniform Cost Search với chi phí = số ô di chuyển"""
    rows, cols = len(grid), len(grid[0])

    if not (0 <= start[0] < cols and 0 <= start[1] < rows and
            0 <= goal[0] < cols and 0 <= goal[1] < rows):
        return []

    if start == goal:
        return []

    dist = {start: 0}
    prev = {}
    heap = [(0, start[0], start[1])]

    directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]

    while heap:
        cost, x, y = heapq.heappop(heap)
        state = (x, y)

        if cost > dist.get(state, float('inf')):
            continue

        if state == goal:  # Late Goal Test (UCS phải dùng late để đảm bảo tối ưu)
            break

        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            next_state = (nx, ny)
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                new_cost = cost + 1  # Chi phí mỗi bước = 1 ô di chuyển
                if new_cost < dist.get(next_state, float('inf')):
                    dist[next_state] = new_cost
                    prev[next_state] = state
                    heapq.heappush(heap, (new_cost, nx, ny))

    if goal not in prev:
        return []

    path = []
    at = goal
    while at != start:
        path.append(at)
        at = prev.get(at)
        if at is None:
            return []
    path.reverse()
    return path


def greedy_path(start, goal, grid):
    rows, cols = len(grid), len(grid[0])
    visited = set()
    parent = {}

    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])  # Manhattan distance

    heap = [(heuristic(start, goal), start)]
    visited.add(start)

    while heap:
        _, current = heapq.heappop(heap)
        if current == goal:
            break
        x, y = current
        for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
            nx, ny = x+dx, y+dy
            neighbor = (nx, ny)
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0 and neighbor not in visited:
                visited.add(neighbor)
                parent[neighbor] = current
                heapq.heappush(heap, (heuristic(neighbor, goal), neighbor))

    path = []
    current = goal
    while current != start:
        if current in parent:
            path.append(current)
            current = parent[current]
        else:
            return []  # không tìm được đường
    path.reverse()
    return path

def hill_climb_step(current, goal, grid):
    rows, cols = len(grid), len(grid[0])
    cx, cy = current
    gx, gy = goal

    best = current
    best_h = abs(cx - gx) + abs(cy - gy)

    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = cx + dx, cy + dy
        if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
            h = abs(nx - gx) + abs(ny - gy)
            if h < best_h:
                best = (nx, ny)
                best_h = h

    return best

def backtracking_path(start, goal, grid):
    path = []
    visited = set()

    def backtrack(pos):
        if pos == goal:
            path.append(pos)
            return True
        visited.add(pos)
        x, y = pos
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            next_pos = (nx, ny)
            if (0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and
                grid[ny][nx] == 0 and next_pos not in visited):
                if backtrack(next_pos):
                    path.append(pos)
                    return True
        return False

    if backtrack(start):
        path.reverse()
    return path

def q_learning_train(grid, start, goal, episodes=100, alpha=0.1, gamma=0.9, epsilon=0.1):
    rows, cols = len(grid), len(grid[0])
    q_table = {}
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    def get_max_q(state):
        return max(q_table.get(state, {}).values(), default=0)

    for ep in range(episodes):
        state = start
        while state != goal:
            if state not in q_table:
                q_table[state] = {a: 0 for a in actions}

            if random.random() < epsilon:
                action = random.choice(actions)
            else:
                action = max(q_table[state], key=q_table[state].get)

            nx, ny = state[0] + action[0], state[1] + action[1]
            next_state = (nx, ny)

            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                reward = 100 if next_state == goal else -1
                if next_state not in q_table:
                    q_table[next_state] = {a: 0 for a in actions}
                q_table[state][action] += alpha * (reward + gamma * get_max_q(next_state) - q_table[state][action])
                state = next_state
            else:
                q_table[state][action] += alpha * (-5 - q_table[state][action])  # Phạt nếu đi vào tường

    return q_table

def q_learning_step(q_table, current):
    if current not in q_table:
        return current
    best_action = max(q_table[current], key=q_table[current].get)
    return (current[0] + best_action[0], current[1] + best_action[1])

def and_or_search_probabilistic(start, goal, grid):
    rows, cols = len(grid), len(grid[0])
    explored = set()
    path = []

    def successors(state, action):
        """Trả về các kết quả có thể xảy ra với xác suất"""
        x, y = state
        dx, dy = action

        intended = (x + dx, y + dy)
        side = (x + dy, y + dx)  # lệch hướng (đơn giản hóa)

        results = []
        for (nx, ny), prob in [(intended, 0.7), (side, 0.3)]:
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                results.append(((nx, ny), prob))
        return results

    def search(state, current_path):
        if state == goal:
            path.append(state)
            return True
        if state in explored:
            return False
        explored.add(state)
        current_path.append(state)

        for action in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            outcomes = successors(state, action)

            if not outcomes:
                continue

            all_success = True
            for (next_state, _) in outcomes:
                if next_state in current_path:
                    continue
                if not search(next_state, current_path.copy()):
                    all_success = False
                    break

            if all_success:
                path.append(state)
                return True

        current_path.pop()
        return False

    if search(start, []):
        path.reverse()
        return path
    return []


# def and_or_search(start, goal, grid):
#     rows, cols = len(grid), len(grid[0])
#     explored = set()  # Tập hợp các trạng thái đã thăm
#     path = []

#     def search(state, current_path):
#         # Điều kiện dừng: nếu đã đến mục tiêu
#         if state == goal:
#             path.append(state)
#             return True
        
#         # Nếu trạng thái đã được thăm, bỏ qua để tránh vòng lặp
#         if state in explored:
#             return False
        
#         # Thêm trạng thái vào tập đã thăm
#         explored.add(state)
        
#         # Thêm trạng thái vào đường đi hiện tại
#         current_path.append(state)
        
#         # Thử tất cả các hành động có thể
#         for action in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
#             next_state = (state[0] + action[0], state[1] + action[1])
#             # Kiểm tra tính hợp lệ của trạng thái tiếp theo
#             if (0 <= next_state[0] < cols and 0 <= next_state[1] < rows and 
#                 grid[next_state[1]][next_state[0]] == 0 and 
#                 next_state not in current_path):  # Tránh chu trình
#                 if search(next_state, current_path):
#                     path.append(next_state)
#                     return True
        
#         # Loại bỏ trạng thái khỏi đường đi hiện tại nếu không tìm thấy đường
#         current_path.pop()
#         return False

#     # Gọi hàm tìm kiếm từ trạng thái bắt đầu
#     if search(start, []):
#         path.reverse()
#         return path
#     return []  # Trả về danh sách rỗng nếu không tìm thấy đường đi