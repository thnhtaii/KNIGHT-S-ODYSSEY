import math
import random

class AdversarialSearch:
    @staticmethod
    def get_bg_grid(battle_base):
        # Build binary grid (0 = air/walkable, 1 = solid)
        grid = []
        for r in range(battle_base.map_height):
            line = []
            for c in range(battle_base.map_width):
                tile = battle_base.tile_layers[1][r * battle_base.map_width + c]
                # Solid floor tiles are tile > 0
                line.append(1 if tile > 0 else 0)
            grid.append(line)
        return grid

    @staticmethod
    def is_on_solid_ground(pos, grid):
        gx, gy = pos
        rows = len(grid)
        if gy + 1 < rows and grid[gy + 1][gx] == 1:
            return True
        return False

    @staticmethod
    def get_shortest_path_step(start, target, grid):
        cols = len(grid[0])
        rows = len(grid)
        # Sanitize target to ensure it is walkable
        tx, ty = target
        while ty >= 0 and grid[ty][tx] == 1:
            ty -= 1
        if ty < 0:
            ty = 0
        target = (tx, ty)
        
        if start == target:
            return start
            
        queue = [[start]]
        visited = {start}
        
        while queue:
            path = queue.pop(0)
            node = path[-1]
            if node == target:
                return path[1] if len(path) > 1 else start
                
            x, y = node
            # Boss moves in 8 directions (with safe cols)
            for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                nx, ny = x + dx, y + dy
                if 1 <= nx < cols - 1 and 0 <= ny < rows:
                    if grid[ny][nx] == 0 and (nx, ny) not in visited:
                        visited.add((nx, ny))
                        queue.append(path + [(nx, ny)])
        return start

    @staticmethod
    def get_valid_actions(pos, is_boss, grid, other_pos=None, combo_cooldown=0, shield_cooldown=0, normal_cooldown=0, boss_hp=100):
        x, y = pos
        cols = len(grid[0])
        rows = len(grid)
        actions = []
        
        # Combat actions are only valid if other_pos is in range
        if other_pos is not None:
            in_range = AdversarialSearch.is_in_range(pos, other_pos)
            if is_boss:
                if in_range:
                    if boss_hp < 70:
                        # Phase 2 & 3: prioritize combo and block
                        if combo_cooldown <= 0:
                            actions.append("COMBO")
                        if shield_cooldown <= 0:
                            actions.append("BLOCK")
                        # Only use charged/normal attack if both combo and block are on cooldown
                        if combo_cooldown > 0 and shield_cooldown > 0 and normal_cooldown <= 0:
                            actions.append("ATTACK")
                    else:
                        # Phase 1: only normal attack
                        if normal_cooldown <= 0:
                            actions.append("ATTACK")
                actions.append("WAIT")
            else:
                if in_range:
                    actions.append("ATTACK")
                    actions.append("BLOCK")
                actions.append("WAIT")
        else:
            actions.extend(["ATTACK", "BLOCK", "WAIT"])
            
        if is_boss:
            if other_pos is not None:
                # If not in range, use BFS pathfinder to move towards player
                if not AdversarialSearch.is_in_range(pos, other_pos):
                    bfs_step = AdversarialSearch.get_shortest_path_step(pos, other_pos, grid)
                    if bfs_step != pos:
                        actions.append(("MOVE", bfs_step))
                else:
                    # In range, allow small reposition moves (adjacent 8 cells)
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                        nx, ny = x + dx, y + dy
                        if 1 <= nx < cols - 1 and 0 <= ny < rows:
                            if grid[ny][nx] == 0:
                                actions.append(("MOVE", (nx, ny)))
            else:
                # Fallback: Boss can fly in 8 directions
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1), (-1, -1), (1, -1), (-1, 1), (1, 1)]:
                    nx, ny = x + dx, y + dy
                    if 1 <= nx < cols - 1 and 0 <= ny < rows:
                        if grid[ny][nx] == 0:
                            actions.append(("MOVE", (nx, ny)))
        else:
            # Player is subject to gravity (stands on solid blocks)
            # Walk left/right
            for dx in [-1, 1]:
                nx = x + dx
                if 0 <= nx < cols and 0 <= y < rows:
                    if grid[y][nx] == 0:
                        actions.append(("MOVE", (nx, y)))
            
            # Jump (if there is ground below player)
            on_ground = False
            if y + 1 < rows and grid[y+1][x] > 0:
                on_ground = True
            
            if on_ground:
                # Jump straight up, up-left, up-right
                for dx, dy in [(0, -3), (-2, -3), (2, -3)]:
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < cols and 0 <= ny < rows:
                        # Make sure path or landing is clear
                        if grid[ny][nx] == 0:
                            actions.append(("JUMP", (nx, ny)))
                            
        return actions

    @staticmethod
    def is_in_range(pos1, pos2):
        # Combat range: X distance <= 2, Y distance <= 1
        return abs(pos1[0] - pos2[0]) <= 2 and abs(pos1[1] - pos2[1]) <= 1

    @staticmethod
    def simulate_state(boss_pos, player_pos, boss_hp, player_hp, boss_act, player_act, grid, boss_dir=-1):
        # Resolve positions
        next_b_pos = boss_pos
        next_p_pos = player_pos
        
        if isinstance(boss_act, tuple) and boss_act[0] in ("MOVE", "JUMP"):
            next_b_pos = boss_act[1]
        if isinstance(player_act, tuple) and player_act[0] in ("MOVE", "JUMP"):
            next_p_pos = player_act[1]
            
        # Resolve combat
        next_b_hp = boss_hp
        next_p_hp = player_hp
        
        # Height-restricted combat check with 1-tile tolerance
        can_fight = abs(next_p_pos[1] - next_b_pos[1]) <= 1
        
        if can_fight:
            # Check if player is behind boss (backstab)
            is_back = (next_p_pos[0] < next_b_pos[0] and boss_dir > 0) or \
                      (next_p_pos[0] > next_b_pos[0] and boss_dir < 0)
                      
            # Player attacks Boss
            if player_act == "ATTACK" and AdversarialSearch.is_in_range(next_p_pos, next_b_pos):
                is_shielding = (boss_act == "BLOCK") and not is_back
                # Damage depends on boss phase (health-based)
                if boss_hp < 30: # Phase 3: red sword damage
                    if is_shielding:
                        next_b_hp -= 5
                    else:
                        next_b_hp -= 20
                else: # Phase 1 & 2
                    if is_shielding:
                        next_b_hp -= 2
                    else:
                        next_b_hp -= 10
                        
            # Boss attacks Player
            if AdversarialSearch.is_in_range(next_b_pos, next_p_pos):
                player_shielding = (player_act == "BLOCK")
                if boss_act == "COMBO": # Consecutive slams (5 slams of 10 HP each)
                    dmg = 50 if not player_shielding else 15
                    next_p_hp -= dmg
                elif boss_act == "ATTACK": # Normal attack
                    dmg = 15 if not player_shielding else 3
                    next_p_hp -= dmg
                
        return next_b_pos, next_p_pos, max(0, next_b_hp), max(0, next_p_hp)

    @staticmethod
    def evaluate(boss_pos, player_pos, boss_hp, player_hp, boss_act, player_act, danger_cols=None):
        # Base evaluation: prioritize health differential
        score = 10 * (boss_hp - player_hp)
        
        # Distance penalty (encourages boss to close in)
        dist = math.hypot(boss_pos[0] - player_pos[0], boss_pos[1] - player_pos[1])
        score -= 2 * dist
        
        # Tactical rewards
        if boss_act == "BLOCK" and player_act == "ATTACK" and AdversarialSearch.is_in_range(boss_pos, player_pos):
            score += 25  # Good defense
        if (boss_act == "ATTACK" or boss_act == "COMBO") and player_act != "BLOCK" and AdversarialSearch.is_in_range(boss_pos, player_pos):
            score += 30  # Good hit
            
        # Expectimax environmental hazard penalties
        if danger_cols and boss_pos[0] in danger_cols:
            score -= 50  # Boss should avoid danger columns
            
        return score

    # --- 1. Minimax ---
    @staticmethod
    def minimax_decision(grid, boss_pos, player_pos, boss_hp, player_hp, player_action=0, 
                         boss_dir=-1, combo_cooldown=0, shield_cooldown=0, normal_cooldown=0, max_depth=3):
        best_act = "WAIT"
        best_val = -float('inf')
        
        b_actions = AdversarialSearch.get_valid_actions(
            boss_pos, is_boss=True, grid=grid, other_pos=player_pos, 
            combo_cooldown=combo_cooldown, shield_cooldown=shield_cooldown, normal_cooldown=normal_cooldown, boss_hp=boss_hp
        )
        
        for b_act in b_actions:
            # Simulate boss move (player waits)
            next_b_pos, next_p_pos, next_b_hp, next_p_hp = AdversarialSearch.simulate_state(
                boss_pos, player_pos, boss_hp, player_hp, b_act, "WAIT", grid, boss_dir=boss_dir
            )
            # Pass turn to player (is_max_turn=False)
            val = AdversarialSearch._minimax_value(
                grid, next_b_pos, next_p_pos, next_b_hp, next_p_hp, 
                depth=1, is_max_turn=False, player_action=player_action, boss_dir=boss_dir, max_depth=max_depth
            )
            if val > best_val:
                best_val = val
                best_act = b_act
                
        return best_act, len(b_actions)

    @staticmethod
    def _minimax_value(grid, boss_pos, player_pos, boss_hp, player_hp, depth, is_max_turn, player_action, boss_dir, max_depth):
        if depth >= max_depth or boss_hp <= 0 or player_hp <= 0:
            return AdversarialSearch.evaluate(boss_pos, player_pos, boss_hp, player_hp, "WAIT", "WAIT")
            
        if is_max_turn:
            val = -float('inf')
            b_actions = AdversarialSearch.get_valid_actions(boss_pos, is_boss=True, grid=grid, other_pos=player_pos, boss_hp=boss_hp)
            for b_act in b_actions:
                nb_pos, np_pos, nb_hp, np_hp = AdversarialSearch.simulate_state(
                    boss_pos, player_pos, boss_hp, player_hp, b_act, "WAIT", grid, boss_dir=boss_dir
                )
                v = AdversarialSearch._minimax_value(grid, nb_pos, np_pos, nb_hp, np_hp, depth + 1, False, player_action, boss_dir, max_depth)
                if v > val: val = v
            return val
        else:
            val = float('inf')
            if depth == 1 and player_action in (3, 4):
                p_actions = ["ATTACK"] if player_action == 3 else ["BLOCK"]
            else:
                p_actions = AdversarialSearch.get_valid_actions(player_pos, is_boss=False, grid=grid, other_pos=boss_pos)
                
            for p_act in p_actions:
                nb_pos, np_pos, nb_hp, np_hp = AdversarialSearch.simulate_state(
                    boss_pos, player_pos, boss_hp, player_hp, "WAIT", p_act, grid, boss_dir=boss_dir
                )
                v = AdversarialSearch._minimax_value(grid, nb_pos, np_pos, nb_hp, np_hp, depth + 1, True, player_action, boss_dir, max_depth)
                if v < val: val = v
            return val

    # --- 2. Alpha-Beta Pruning ---
    @staticmethod
    def alphabeta_decision(grid, boss_pos, player_pos, boss_hp, player_hp, player_action=0, 
                           boss_dir=-1, combo_cooldown=0, shield_cooldown=0, normal_cooldown=0, max_depth=6):
        best_act = "WAIT"
        best_val = -float('inf')
        alpha = -float('inf')
        beta = float('inf')
        
        b_actions = AdversarialSearch.get_valid_actions(
            boss_pos, is_boss=True, grid=grid, other_pos=player_pos, 
            combo_cooldown=combo_cooldown, shield_cooldown=shield_cooldown, normal_cooldown=normal_cooldown, boss_hp=boss_hp
        )
        
        nodes_evaluated = 0
        pruned_branches = 0

        for b_act in b_actions:
            next_b_pos, next_p_pos, next_b_hp, next_p_hp = AdversarialSearch.simulate_state(
                boss_pos, player_pos, boss_hp, player_hp, b_act, "WAIT", grid, boss_dir=boss_dir
            )
            val, nodes, pruned = AdversarialSearch._alphabeta_value(
                grid, next_b_pos, next_p_pos, next_b_hp, next_p_hp, 
                depth=1, is_max_turn=False, alpha=alpha, beta=beta, player_action=player_action, boss_dir=boss_dir, max_depth=max_depth
            )
            nodes_evaluated += nodes
            pruned_branches += pruned
            
            if val > best_val:
                best_val = val
                best_act = b_act
            alpha = max(alpha, best_val)
            
        return best_act, nodes_evaluated, pruned_branches

    @staticmethod
    def _alphabeta_value(grid, boss_pos, player_pos, boss_hp, player_hp, depth, is_max_turn, alpha, beta, player_action, boss_dir, max_depth):
        if depth >= max_depth or boss_hp <= 0 or player_hp <= 0:
            return AdversarialSearch.evaluate(boss_pos, player_pos, boss_hp, player_hp, "WAIT", "WAIT"), 1, 0
            
        total_nodes = 0
        total_pruned = 0

        if is_max_turn:
            val = -float('inf')
            b_actions = AdversarialSearch.get_valid_actions(boss_pos, is_boss=True, grid=grid, other_pos=player_pos, boss_hp=boss_hp)
            for b_act in b_actions:
                nb_pos, np_pos, nb_hp, np_hp = AdversarialSearch.simulate_state(
                    boss_pos, player_pos, boss_hp, player_hp, b_act, "WAIT", grid, boss_dir=boss_dir
                )
                v, n, p = AdversarialSearch._alphabeta_value(
                    grid, nb_pos, np_pos, nb_hp, np_hp, depth + 1, False, alpha, beta, player_action, boss_dir, max_depth
                )
                total_nodes += n
                total_pruned += p
                if v > val: val = v
                alpha = max(alpha, val)
                if beta <= alpha:
                    total_pruned += 1
                    break
            return val, total_nodes, total_pruned
        else:
            val = float('inf')
            if depth == 1 and player_action in (3, 4):
                p_actions = ["ATTACK"] if player_action == 3 else ["BLOCK"]
            else:
                p_actions = AdversarialSearch.get_valid_actions(player_pos, is_boss=False, grid=grid, other_pos=boss_pos)
                
            for p_act in p_actions:
                nb_pos, np_pos, nb_hp, np_hp = AdversarialSearch.simulate_state(
                    boss_pos, player_pos, boss_hp, player_hp, "WAIT", p_act, grid, boss_dir=boss_dir
                )
                v, n, p = AdversarialSearch._alphabeta_value(
                    grid, nb_pos, np_pos, nb_hp, np_hp, depth + 1, True, alpha, beta, player_action, boss_dir, max_depth
                )
                total_nodes += n
                total_pruned += p
                if v < val: val = v
                beta = min(beta, val)
                if beta <= alpha:
                    total_pruned += 1
                    break
            return val, total_nodes, total_pruned

    # --- 3. Expectimax ---
    @staticmethod
    def expectimax_decision(grid, boss_pos, player_pos, boss_hp, player_hp, player_action=0, 
                            boss_dir=-1, combo_cooldown=0, shield_cooldown=0, normal_cooldown=0, danger_cols=None, max_depth=4):
        best_act = "WAIT"
        best_val = -float('inf')
        
        b_actions = AdversarialSearch.get_valid_actions(
            boss_pos, is_boss=True, grid=grid, other_pos=player_pos, 
            combo_cooldown=combo_cooldown, shield_cooldown=shield_cooldown, normal_cooldown=normal_cooldown, boss_hp=boss_hp
        )
        p_actions = AdversarialSearch.get_valid_actions(player_pos, is_boss=False, grid=grid, other_pos=boss_pos)
        
        # Probabilistic player evaluation helper
        sim_scores = []
        for p_act in p_actions:
            next_b_pos, next_p_pos, next_b_hp, next_p_hp = AdversarialSearch.simulate_state(
                boss_pos, player_pos, boss_hp, player_hp, "WAIT", p_act, grid, boss_dir=boss_dir
            )
            score = AdversarialSearch.evaluate(next_b_pos, next_p_pos, next_b_hp, next_p_hp, "WAIT", p_act, danger_cols)
            sim_scores.append((score, p_act))
            
        sim_scores.sort(key=lambda x: x[0])
        best_p_act = sim_scores[0][1] if sim_scores else "WAIT"

        for b_act in b_actions:
            next_b_pos, next_p_pos, next_b_hp, next_p_hp = AdversarialSearch.simulate_state(
                boss_pos, player_pos, boss_hp, player_hp, b_act, "WAIT", grid, boss_dir=boss_dir
            )
            val = AdversarialSearch._expectimax_value(
                grid, next_b_pos, next_p_pos, next_b_hp, next_p_hp, 
                depth=1, is_max_turn=False, best_p_act=best_p_act, player_action=player_action,
                boss_dir=boss_dir, danger_cols=danger_cols, max_depth=max_depth
            )
            if val > best_val:
                best_val = val
                best_act = b_act
                
        return best_act, len(b_actions) * len(p_actions)

    @staticmethod
    def _expectimax_value(grid, boss_pos, player_pos, boss_hp, player_hp, depth, is_max_turn, best_p_act, player_action, boss_dir, danger_cols, max_depth):
        if depth >= max_depth or boss_hp <= 0 or player_hp <= 0:
            return AdversarialSearch.evaluate(boss_pos, player_pos, boss_hp, player_hp, "WAIT", "WAIT", danger_cols)
            
        if is_max_turn:
            val = -float('inf')
            b_actions = AdversarialSearch.get_valid_actions(boss_pos, is_boss=True, grid=grid, other_pos=player_pos, boss_hp=boss_hp)
            for b_act in b_actions:
                nb_pos, np_pos, nb_hp, np_hp = AdversarialSearch.simulate_state(
                    boss_pos, player_pos, boss_hp, player_hp, b_act, "WAIT", grid, boss_dir=boss_dir
                )
                v = AdversarialSearch._expectimax_value(
                    grid, nb_pos, np_pos, nb_hp, np_hp, depth + 1, False, best_p_act, player_action, boss_dir, danger_cols, max_depth
                )
                if v > val: val = v
            return val
        else:
            expected_val = 0.0
            if depth == 1 and player_action in (3, 4):
                p_actions = ["ATTACK"] if player_action == 3 else ["BLOCK"]
            else:
                p_actions = AdversarialSearch.get_valid_actions(player_pos, is_boss=False, grid=grid, other_pos=boss_pos)
                
            for p_act in p_actions:
                nb_pos, np_pos, nb_hp, np_hp = AdversarialSearch.simulate_state(
                    boss_pos, player_pos, boss_hp, player_hp, "WAIT", p_act, grid, boss_dir=boss_dir
                )
                v = AdversarialSearch._expectimax_value(
                    grid, nb_pos, np_pos, nb_hp, np_hp, depth + 1, True, best_p_act, player_action, boss_dir, danger_cols, max_depth
                )
                
                if p_act == best_p_act:
                    prob = 0.6 + (0.4 / len(p_actions))
                else:
                    prob = 0.4 / len(p_actions)
                expected_val += prob * v
            return expected_val
