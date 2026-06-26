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


def random_restart_hill_climbing_path(start, goal, grid, max_restarts=10):
    rows, cols = len(grid), len(grid[0])
    
    def value(state):
        # VALUE(n) = -h(n) để chuyển đổi bài toán tìm cực đại sang giảm khoảng cách Manhattan
        return -(abs(state[0] - goal[0]) + abs(state[1] - goal[1]))
        
    for r in range(max_restarts):
        current = start
        path = [current]
        visited = set([current])
        
        while True:
            if current == goal:
                return path
                
            x, y = current
            neighbors = []
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = x + dx, y + dy
                if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                    neighbors.append((nx, ny))
            
            # Better_Neighbors = { n in Neighbor_States | VALUE(n) > VALUE(Current_State) }
            better_neighbors = [n for n in neighbors if value(n) > value(current) and n not in visited]
            
            if not better_neighbors:
                # Không còn lân cận nào tốt hơn -> Đạt cực trị địa phương (break ra để restart)
                break
                
            next_state = random.choice(better_neighbors)
            current = next_state
            path.append(current)
            visited.add(current)
            
    return []  # failure


def simulated_annealing_path(start, goal, grid, T0=10.0, Tmin=0.05, alpha=0.98):
    import math
    
    def h(state):
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])
        
    current = start
    path = [current]
    T = T0
    rows, cols = len(grid), len(grid[0])
    
    while T > Tmin:
        if current == goal:
            return path
            
        x, y = current
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                neighbors.append((nx, ny))
                
        if not neighbors:
            break
            
        next_state = random.choice(neighbors)
        delta = h(next_state) - h(current)
        
        if delta < 0:
            current = next_state
            path.append(current)
        else:
            p = math.exp(-delta / T)
            if random.random() < p:
                current = next_state
                path.append(current)
                
        T = alpha * T
        
    if current == goal:
        return path
    return []


def local_beam_path(start, goal, grid, k=3):
    rows, cols = len(grid), len(grid[0])
    
    def value(state):
        return -(abs(state[0] - goal[0]) + abs(state[1] - goal[1]))
        
    parent = {start: None}
    
    # Khởi tạo chùm tia ban đầu RANDOM_K_STATES(Start)
    start_neighbors = []
    x, y = start
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        nx, ny = x + dx, y + dy
        if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
            start_neighbors.append((nx, ny))
            parent[(nx, ny)] = start
            
    current_state_set = [start] + start_neighbors
    current_state_set = current_state_set[:k]
    
    visited = set(current_state_set)
    max_steps = 200
    step = 0
    best_state = start
    
    while step < max_steps:
        neighbor_states = []
        
        for state in current_state_set:
            sx, sy = state
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                nx, ny = sx + dx, sy + dy
                if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                    neighbor = (nx, ny)
                    if neighbor not in visited:
                        neighbor_states.append(neighbor)
                        parent[neighbor] = state
                        visited.add(neighbor)
                        
        if not neighbor_states:
            current_state_set.sort(key=value, reverse=True)
            best_state = current_state_set[0]
            break
            
        found_goal = False
        for neighbor in neighbor_states:
            if neighbor == goal:
                found_goal = True
                best_state = goal
                break
        if found_goal:
            break
            
        neighbor_states.sort(key=value, reverse=True)
        current_state_set = neighbor_states[:k]
        step += 1
        
    path = []
    curr = best_state
    while curr is not None:
        path.append(curr)
        curr = parent.get(curr)
    path.reverse()
    
    if path and path[0] == start:
        return path
    return []


def and_or_graph_search(start, goal, grid):
    rows, cols = len(grid), len(grid[0])
    explored = set()
    
    def goal_test(state):
        return state == goal
        
    def actions(state):
        return [(-1, 0), (1, 0), (0, -1), (0, 1)] # LEFT, RIGHT, UP, DOWN
        
    def results(state, action):
        x, y = state
        dx, dy = action
        intended = (x + dx, y + dy)
        side = (x + dy, y + dx) # Di chuyển chệch hướng vuông góc do trượt
        
        outcomes = []
        for nx, ny in [intended, side]:
            if 0 <= nx < cols and 0 <= ny < rows and grid[ny][nx] == 0:
                outcomes.append((nx, ny))
            else:
                outcomes.append(state) # Chạm tường đứng yên
        return list(set(outcomes))
        
    def or_search(state, path):
        if goal_test(state):
            return []
        if state in path:
            return "failure"
        if state in explored:
            return "failure"
        explored.add(state)
            
        for action in actions(state):
            result_states = results(state, action)
            plan = and_search(result_states, path + [state])
            if plan != "failure":
                return [action, plan]
        return "failure"
        
    def and_search(states, path):
        plans = {}
        for s in states:
            plan_s = or_search(s, path)
            if plan_s == "failure":
                return "failure"
            plans[s] = plan_s
        return plans

    plan = or_search(start, [])
    return plan if plan != "failure" else []


def belief_a_star(start1, start2, goal, grid):
    import heapq
    
    def manhattan(state, goal):
        return abs(state[0] - goal[0]) + abs(state[1] - goal[1])

    def result(state, action):
        x, y = state
        dx, dy = action
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 0:
            return (nx, ny)
        return state

    start_node = (start1, start2)
    frontier = []
    
    g_score = {start_node: 0}
    h_start = (manhattan(start1, goal) + manhattan(start2, goal)) / 2
    f_start = h_start
    
    counter = 0
    heapq.heappush(frontier, (f_start, g_score[start_node], counter, start_node, []))
    
    reached = {start_node}
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # LEFT, RIGHT, UP, DOWN
    
    while frontier:
        f_val, g_val, _, current, path = heapq.heappop(frontier)
        s1, s2 = current
        
        if s1 == goal and s2 == goal:
            return path
            
        for action in actions:
            if s1 != goal:
                ns1 = result(s1, action)
            else:
                ns1 = s1
                
            if s2 != goal:
                ns2 = result(s2, action)
            else:
                ns2 = s2
                
            child = (ns1, ns2)
            child_g = g_val + 1
            
            if child not in reached or child_g < g_score.get(child, float('inf')):
                g_score[child] = child_g
                h_child = (manhattan(ns1, goal) + manhattan(ns2, goal)) / 2
                f_child = child_g + h_child
                counter += 1
                heapq.heappush(frontier, (f_child, child_g, counter, child, path + [action]))
                reached.add(child)
                
    return [] # failure


def belief_a_star_goals(start1, start2, goals, grid):
    import heapq
    
    def min_manhattan(state, goals):
        return min(abs(state[0] - g[0]) + abs(state[1] - g[1]) for g in goals)

    def result(state, action):
        x, y = state
        dx, dy = action
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 0:
            return (nx, ny)
        return state

    start_node = (start1, start2)
    frontier = []
    
    g_score = {start_node: 0}
    h_start = (min_manhattan(start1, goals) + min_manhattan(start2, goals)) / 2
    f_start = h_start
    
    counter = 0
    heapq.heappush(frontier, (f_start, g_score[start_node], counter, start_node, []))
    
    reached = {start_node}
    actions = [(-1, 0), (1, 0), (0, -1), (0, 1)] # LEFT, RIGHT, UP, DOWN
    
    while frontier:
        f_val, g_val, _, current, path = heapq.heappop(frontier)
        s1, s2 = current
        
        if s1 in goals and s2 in goals:
            return path
            
        for action in actions:
            if s1 in goals:
                ns1 = s1
            else:
                ns1 = result(s1, action)
                
            if s2 in goals:
                ns2 = s2
            else:
                ns2 = result(s2, action)
                
            child = (ns1, ns2)
            child_g = g_val + 1
            
            if child not in reached or child_g < g_score.get(child, float('inf')):
                g_score[child] = child_g
                h_child = (min_manhattan(ns1, goals) + min_manhattan(ns2, goals)) / 2
                f_child = child_g + h_child
                counter += 1
                heapq.heappush(frontier, (f_child, child_g, counter, child, path + [action]))
                reached.add(child)
                
    return [] # failure


def result(state, action, grid):
    x, y = state
    dx, dy = action
    nx, ny = x + dx, y + dy
    if 0 <= nx < len(grid[0]) and 0 <= ny < len(grid) and grid[ny][nx] == 0:
        return (nx, ny)
    return state