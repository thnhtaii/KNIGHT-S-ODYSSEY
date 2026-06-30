import sys
import os
import time
import random
import subprocess

# Tự động kiểm tra và cài đặt các thư viện nếu thiếu
try:
    import matplotlib.pyplot as plt
    import numpy as np
except ImportError:
    print("[System] Thu vien matplotlib hoac numpy chua duoc cai dat. Dang tu dong cai dat...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "matplotlib", "numpy"])
        import matplotlib.pyplot as plt
        import numpy as np
        print("[System] Cai dat cac thu vien thanh cong!")
    except Exception as e:
        print(f"[Error] Khong the tu dong cai dat thu vien: {e}")
        print("Vui long tu chay lenh: pip install matplotlib numpy")
        sys.exit(1)

# Thêm thư mục gốc vào path để import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    # Level 1 & 2 pathfinding algorithms
    from src.ai.algorithms import (
        bfs_path, dfs_path, ucs_path, greedy_path, astar_path, ida_star_path
    )
    # Level 3 local search algorithms
    from src.ai.algorithms import (
        random_restart_hill_climbing_path, simulated_annealing_path, local_beam_path
    )
    # Level 4 uncertainty algorithms
    from src.ai.algorithms import (
        and_or_graph_search, belief_a_star, belief_a_star_goals
    )
    # Level 5 constraint satisfaction problem (CSP)
    from src.ai.csp_surround import CSPSurround
    # Level 6 adversarial search
    from src.ai.adversarial_search import AdversarialSearch
except ImportError as e:
    print(f"[Error] Khong the import cac thuat toan tu codebase: {e}")
    sys.exit(1)

# Thư mục lưu biểu đồ kết quả
OUTPUT_DIR = os.path.join("assets", "benchmarks")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Tự động dọn dẹp các file ảnh cũ đã sinh trước đó
for f in os.listdir(OUTPUT_DIR):
    if f.endswith(".png"):
        try:
            os.remove(os.path.join(OUTPUT_DIR, f))
        except Exception:
            pass

# ----------------- BẢN ĐỒ LƯỚI ĐỂ TEST (Grid Map 25x10) -----------------
grid = [
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
]

start_pos = (1, 1)
goal_pos = (23, 8)

# ----------------- LEVEL 1: UNINFORMED SEARCH (BFS, DFS, UCS) -----------------
def benchmark_level1():
    print("\n--- BENCHMARK LEVEL 1: BFS, DFS, UCS (Dijkstra) ---")
    algos = {
        "BFS": bfs_path,
        "DFS": dfs_path,
        "UCS": ucs_path
    }
    results = {}
    all_runs_times = []
    for name, func in algos.items():
        times = []
        path_len = 0
        for _ in range(50):
            t0 = time.perf_counter()
            path = func(start_pos, goal_pos, grid)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
            all_runs_times.append((t1 - t0) * 1000.0)
            if path:
                path_len = len(path)
        avg_time = np.mean(times)
        results[name] = {"time": avg_time, "length": path_len}
        print(f"[{name}] Time: {avg_time:6.4f} ms | Path Length: {path_len} steps")

    # Vẽ biểu đồ
    names = list(results.keys())
    times = [results[n]["time"] for n in names]
    lengths = [results[n]["length"] for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color = '#2980b9'
    ax1.set_xlabel('Thuat toan Uninformed Search', fontweight='bold')
    ax1.set_ylabel('Thoi gian thuc thi (ms)', color=color, fontweight='bold')
    bars1 = ax1.bar(x - width/2, times, width, label='Thoi gian (ms)', color='#2980b9', edgecolor='grey')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontweight='bold')
    
    ax2 = ax1.twinx()
    color = '#c0392b'
    ax2.set_ylabel('Do dai duong di (so o)', color=color, fontweight='bold')
    bars2 = ax2.bar(x + width/2, lengths, width, label='Do dai duong di', color='#e74c3c', edgecolor='grey')
    ax2.tick_params(axis='y', labelcolor=color)

    # Them label so lieu
    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}ms", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', fontsize=9)
        
    plt.title('SO SANH HIEU SUAT LEVEL 1: UNINFORMED PATHFINDING', fontsize=11, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "comparison_level1_classic.png"), dpi=300)
    plt.close()
    
    return np.mean(all_runs_times)

# ----------------- LEVEL 2: INFORMED SEARCH (Greedy, A*, IDA*) -----------------
def benchmark_level2():
    print("\n--- BENCHMARK LEVEL 2: Greedy, A*, IDA* ---")
    algos = {
        "Greedy BFS": greedy_path,
        "A* Search": astar_path,
        "IDA* Search": ida_star_path
    }
    results = {}
    all_runs_times = []
    for name, func in algos.items():
        times = []
        path_len = 0
        runs = 20 if "IDA*" in name else 50
        for _ in range(runs):
            t0 = time.perf_counter()
            path = func(start_pos, goal_pos, grid)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
            all_runs_times.append((t1 - t0) * 1000.0)
            if path:
                path_len = len(path)
        avg_time = np.mean(times)
        results[name] = {"time": avg_time, "length": path_len}
        print(f"[{name}] Time: {avg_time:6.4f} ms | Path Length: {path_len} steps")

    names = list(results.keys())
    times = [results[n]["time"] for n in names]
    lengths = [results[n]["length"] for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color = '#2980b9'
    ax1.set_xlabel('Thuat toan Informed Search', fontweight='bold')
    ax1.set_ylabel('Thoi gian thuc thi (ms)', color=color, fontweight='bold')
    bars1 = ax1.bar(x - width/2, times, width, label='Thoi gian (ms)', color='#2980b9', edgecolor='grey')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontweight='bold')
    
    ax2 = ax1.twinx()
    color = '#d35400'
    ax2.set_ylabel('Do dai duong di (so o)', color=color, fontweight='bold')
    bars2 = ax2.bar(x + width/2, lengths, width, label='Do dai duong di', color='#e67e22', edgecolor='grey')
    ax2.tick_params(axis='y', labelcolor=color)

    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}ms", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', fontsize=9)
        
    plt.title('SO SANH HIEU SUAT LEVEL 2: INFORMED PATHFINDING (DUNG HEURISTIC)', fontsize=11, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "comparison_level2_heuristic.png"), dpi=300)
    plt.close()
    
    return np.mean(all_runs_times)

# ----------------- LEVEL 3: LOCAL SEARCH (Hill Climbing, Simulated Annealing, Local Beam) -----------------
def benchmark_level3():
    print("\n--- BENCHMARK LEVEL 3: Hill Climbing, Simulated Annealing, Local Beam Search ---")
    algos = {
        "Hill Climbing": random_restart_hill_climbing_path,
        "Simulated Annealing": simulated_annealing_path,
        "Local Beam (k=3)": local_beam_path
    }
    results = {}
    all_runs_times = []
    for name, func in algos.items():
        success = 0
        times = []
        lengths = []
        for _ in range(100):
            t0 = time.perf_counter()
            path = func(start_pos, goal_pos, grid)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
            all_runs_times.append((t1 - t0) * 1000.0)
            if path and path[-1] == goal_pos:
                success += 1
                lengths.append(len(path))
        success_rate = (success / 100.0) * 100.0
        avg_time = np.mean(times)
        avg_len = np.mean(lengths) if lengths else 0
        results[name] = {"rate": success_rate, "time": avg_time, "length": avg_len}
        print(f"[{name}] Success Rate: {success_rate:5.1f}% | Avg Time: {avg_time:6.4f} ms | Avg Length: {avg_len:.1f} steps")

    names = list(results.keys())
    rates = [results[n]["rate"] for n in names]
    times = [results[n]["time"] for n in names]
    lengths = [results[n]["length"] for n in names]

    x = np.arange(len(names))
    width = 0.25
    fig, ax = plt.subplots(figsize=(9, 5.5))
    
    bars1 = ax.bar(x - width, rates, width, label='Ty le thanh cong (%)', color='#e74c3c', edgecolor='grey')
    bars2 = ax.bar(x, times, width, label='Thoi gian (ms)', color='#f1c40f', edgecolor='grey')
    bars3 = ax.bar(x + width, lengths, width, label='Do dai trung binh', color='#9b59b6', edgecolor='grey')
    
    ax.set_ylabel('Gia tri do luong', fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, fontweight='bold')
    ax.legend()
    
    for bar in bars1:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.1f}%", ha='center', va='bottom', fontsize=8)
    for bar in bars2:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}ms", ha='center', va='bottom', fontsize=8)
    for bar in bars3:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.1f}", ha='center', va='bottom', fontsize=8)

    plt.title('SO SANH HIEU SUAT LEVEL 3: LOCAL SEARCH (TIM KIEM CUC BO)', fontsize=11, fontweight='bold', pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "comparison_level3_local_search.png"), dpi=300)
    plt.close()
    
    return np.mean(all_runs_times)

# ----------------- LEVEL 4: SEARCH UNDER UNCERTAINTY (BFS, And-Or Graph Search, Belief A*) -----------------
def benchmark_level4():
    print("\n--- BENCHMARK LEVEL 4: Search under Uncertainty ---")
    
    def run_bfs(s1, s2, g, grid):
        return bfs_path(s1, g, grid)
        
    def run_and_or(s1, s2, g, grid):
        return and_or_graph_search(s1, g, grid)
        
    def run_belief(s1, s2, g, grid):
        return belief_a_star(s1, s2, g, grid)
        
    def run_belief_goals(s1, s2, g, grid):
        return belief_a_star_goals(s1, s1, [g], grid)

    algos = {
        "BFS (Standard)": run_bfs,
        "And-Or Search": run_and_or,
        "Belief State A*": run_belief,
        "Belief State + Goals": run_belief_goals
    }
    
    results = {}
    s1, s2 = (1, 1), (1, 2)
    g = (23, 8)
    all_runs_times = []
    
    for name, func in algos.items():
        times = []
        plan_complexity = 0
        for _ in range(30):
            t0 = time.perf_counter()
            plan = func(s1, s2, g, grid)
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
            all_runs_times.append((t1 - t0) * 1000.0)
            if plan:
                plan_complexity = len(plan)
        avg_time = np.mean(times)
        results[name] = {"time": avg_time, "complexity": plan_complexity}
        print(f"[{name}] Time: {avg_time:6.4f} ms | Plan Complexity: {plan_complexity} elements")

    names = list(results.keys())
    times = [results[n]["time"] for n in names]
    complexities = [results[n]["complexity"] for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    fig, ax1 = plt.subplots(figsize=(9, 5))
    
    color = '#d35400'
    ax1.set_xlabel('Thuat toan trong moi truong bat dinh (Level 4)', fontweight='bold')
    ax1.set_ylabel('Thoi gian lap ke hoach (ms)', color=color, fontweight='bold')
    bars1 = ax1.bar(x - width/2, times, width, label='Thoi gian (ms)', color='#d35400', edgecolor='grey')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontweight='bold')
    
    ax2 = ax1.twinx()
    color = '#2c3e50'
    ax2.set_ylabel('Do phuc tap / So buoc cua ke hoach', color=color, fontweight='bold')
    bars2 = ax2.bar(x + width/2, complexities, width, label='So buoc ke hoach', color='#7f8c8d', edgecolor='grey')
    ax2.tick_params(axis='y', labelcolor=color)

    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}ms", ha='center', va='bottom', fontsize=8)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', fontsize=8)
        
    plt.title('SO SANH LEVEL 4: TIM KIEM TRONG MOI TRUONG BAT DINH (UNCERTAINTY)', fontsize=11, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "comparison_level4_uncertainty.png"), dpi=300)
    plt.close()
    
    return np.mean(all_runs_times)

# ----------------- LEVEL 5: CSP - CONSTRAINT SATISFACTION PROBLEM (Backtracking, AC-3, Min-Conflicts) -----------------
def benchmark_level5():
    print("\n--- BENCHMARK LEVEL 5: Constraint Satisfaction Problem (CSP) ---")
    csp = CSPSurround(25, 10, grid)
    player_pos = (12, 5)
    boss_positions = [(10, 5), (14, 5), (12, 3)]
    
    results = {}
    all_runs_times = []
    
    # 1. Backtracking CSP
    bt_times = []
    bt_iters = []
    for _ in range(50):
        _, t_ms, iters = csp.solve_backtracking(player_pos, boss_positions)
        bt_times.append(t_ms)
        all_runs_times.append(t_ms)
        bt_iters.append(iters)
    results["Backtracking"] = {"time": np.mean(bt_times), "iterations": np.mean(bt_iters)}
    
    # 2. AC-3 + Backtracking CSP
    ac3_times = []
    ac3_iters = []
    for _ in range(50):
        _, t_ms, iters = csp.solve_ac3(player_pos, boss_positions)
        ac3_times.append(t_ms)
        all_runs_times.append(t_ms)
        ac3_iters.append(iters)
    results["AC-3 + BT"] = {"time": np.mean(ac3_times), "iterations": np.mean(ac3_iters)}
    
    # 3. Min-Conflicts CSP
    mc_times = []
    mc_iters = []
    for _ in range(50):
        _, t_ms, iters = csp.solve_min_conflicts(player_pos, boss_positions)
        mc_times.append(t_ms)
        all_runs_times.append(t_ms)
        mc_iters.append(iters)
    results["Min-Conflicts"] = {"time": np.mean(mc_times), "iterations": np.mean(mc_iters)}

    for name, data in results.items():
        print(f"[{name}] Time: {data['time']:6.4f} ms | Iterations/Conflicts: {data['iterations']:.1f}")

    names = list(results.keys())
    times = [results[n]["time"] for n in names]
    iters = [results[n]["iterations"] for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    fig, ax1 = plt.subplots(figsize=(8, 5))
    
    color = '#8e44ad'
    ax1.set_xlabel('Giai thuat CSP (Mieu ta bao vay nguoi choi)', fontweight='bold')
    ax1.set_ylabel('Thoi gian giai quyet (ms)', color=color, fontweight='bold')
    bars1 = ax1.bar(x - width/2, times, width, label='Thoi gian (ms)', color='#9b59b6', edgecolor='grey')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontweight='bold')
    
    ax2 = ax1.twinx()
    color = '#d35400'
    ax2.set_ylabel('So vong lap / So lan xung dot', color=color, fontweight='bold')
    bars2 = ax2.bar(x + width/2, iters, width, label='So vong lap', color='#e67e22', edgecolor='grey')
    ax2.tick_params(axis='y', labelcolor=color)

    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}ms", ha='center', va='bottom', fontsize=9)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.1f}", ha='center', va='bottom', fontsize=9)
        
    plt.title('SO SANH LEVEL 5: THOA MAN RANG BUOC (CSP) TRONG DIEU HUONG QUAI VAT', fontsize=11, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "comparison_level5_csp.png"), dpi=300)
    plt.close()
    
    return np.mean(all_runs_times)

# ----------------- LEVEL 6: ADVERSARIAL SEARCH (Minimax, Alpha-Beta, Expectimax) -----------------
def benchmark_level6():
    print("\n--- BENCHMARK LEVEL 6: Adversarial Search (Doi khang Boss) ---")
    sim_grid = [[0]*25 for _ in range(19)]
    boss_pos = (12, 9)
    player_pos = (14, 9)
    boss_hp = 100
    player_hp = 100
    player_action = 0
    boss_direction = -1
    
    configs = {
        "Minimax (D=3)": lambda: AdversarialSearch.minimax_decision(
            sim_grid, boss_pos, player_pos, boss_hp, player_hp, player_action, boss_direction, max_depth=3
        ),
        "Alpha-Beta (D=3)": lambda: AdversarialSearch.alphabeta_decision(
            sim_grid, boss_pos, player_pos, boss_hp, player_hp, player_action, boss_direction, max_depth=3
        ),
        "Alpha-Beta (D=5)": lambda: AdversarialSearch.alphabeta_decision(
            sim_grid, boss_pos, player_pos, boss_hp, player_hp, player_action, boss_direction, max_depth=5
        ),
        "Expectimax (D=3)": lambda: AdversarialSearch.expectimax_decision(
            sim_grid, boss_pos, player_pos, boss_hp, player_hp, player_action, boss_direction, max_depth=3
        )
    }
    
    results = {}
    all_runs_times = []
    for name, dec_func in configs.items():
        times = []
        nodes_list = []
        for _ in range(15):
            t0 = time.perf_counter()
            res = dec_func()
            t1 = time.perf_counter()
            times.append((t1 - t0) * 1000.0)
            all_runs_times.append((t1 - t0) * 1000.0)
            nodes_list.append(res[1])
            
        avg_time = np.mean(times)
        avg_nodes = np.mean(nodes_list)
        results[name] = {"time": avg_time, "nodes": avg_nodes}
        print(f"[{name}] Time: {avg_time:8.4f} ms | Evaluated Nodes: {int(avg_nodes)}")

    names = ["Minimax (D=3)", "Alpha-Beta (D=3)", "Expectimax (D=3)"]
    nodes = [results[n]["nodes"] for n in names]
    times = [results[n]["time"] for n in names]
    
    x = np.arange(len(names))
    width = 0.35
    fig, ax1 = plt.subplots(figsize=(8.5, 5))
    
    color = '#c0392b'
    ax1.set_xlabel('Thuat toan doi khang (Do sau 3)', fontweight='bold')
    ax1.set_ylabel('So nut da duyet (Cang it cang tot)', color=color, fontweight='bold')
    bars1 = ax1.bar(x - width/2, nodes, width, label='So nut duyet', color='#e74c3c', edgecolor='grey')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(x)
    ax1.set_xticklabels(names, fontweight='bold')
    
    ax2 = ax1.twinx()
    color = '#2980b9'
    ax2.set_ylabel('Thoi gian dua ra quyet dinh (ms)', color=color, fontweight='bold')
    bars2 = ax2.bar(x + width/2, times, width, label='Thoi gian (ms)', color='#3498db', edgecolor='grey')
    ax2.tick_params(axis='y', labelcolor=color)

    for bar in bars1:
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{int(bar.get_height())}", ha='center', va='bottom', fontsize=8)
    for bar in bars2:
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height(), f"{bar.get_height():.2f}ms", ha='center', va='bottom', fontsize=8)
        
    plt.title('SO SANH LEVEL 6: TIM KIEM DOI KHANG (DECISION MAKING)', fontsize=11, fontweight='bold', pad=15)
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, "comparison_level6_adversarial.png"), dpi=300)
    plt.close()
    
    return np.mean(all_runs_times)

# ----------------- OVERALL COMPARISON: ALL 6 ALGORITHM GROUPS (LEVEL 1-6) -----------------
def benchmark_groups_overall(t1, t2, t3, t4, t5, t6):
    print("\n--- BENCHMARK OVERALL: COMPARING ALL 6 ALGORITHM GROUPS ---")
    groups = [
        "L1: Uninformed\n(BFS/DFS/UCS)",
        "L2: Informed\n(Greedy/A*/IDA*)",
        "L3: Local Search\n(Hill/SA/Beam)",
        "L4: Uncertainty\n(And-Or/Belief)",
        "L5: CSP\n(Backtrack/AC3/MC)",
        "L6: Adversarial\n(Minimax/AB/Exp)"
    ]
    times = [t1, t2, t3, t4, t5, t6]
    
    x = np.arange(len(groups))
    fig, ax = plt.subplots(figsize=(11, 6))
    
    # Bảng màu đẹp mắt không có màu xanh lá
    colors = ['#3498db', '#e67e22', '#9b59b6', '#d35400', '#8e44ad', '#c0392b']
    
    bars = ax.bar(x, times, color=colors, edgecolor='grey', width=0.5)
    
    ax.set_ylabel('Thoi gian thuc thi trung binh (ms) - Thang do Log', fontweight='bold')
    # Sử dụng thang đo logarit vì chênh lệch thời gian giữa tìm đường đơn giản (<0.5ms) và Minimax (>50ms) là cực lớn
    ax.set_yscale('log')
    ax.set_title('SO SANH TONG QUAN HIEU SUAT GIUA 6 NHOM THUAT TOAN AI (LEVEL 1 - 6)', fontsize=12, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(groups, fontweight='bold', fontsize=9)
    ax.grid(axis='y', linestyle='--', alpha=0.5, which="both")
    
    # Ghi chú giá trị số cụ thể trên đầu cột
    for bar in bars:
        yval = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2.0, yval, f"{yval:.2f} ms", ha='center', va='bottom', fontsize=9, fontweight='bold')
        
    plt.tight_layout()
    chart_path = os.path.join(OUTPUT_DIR, "comparison_groups_overall.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[Success] Bieu do tong quan 6 nhom da duoc luu tai: {chart_path}")

# ----------------- CHẠY TẤT CẢ BENCHMARK -----------------
if __name__ == "__main__":
    print("=================================================================")
    print("   AI ALGORITHMS BENCHMARK TOOL FOR KNIGHT'S ODYSSEY GAME")
    print("=================================================================")
    
    t1 = benchmark_level1()
    t2 = benchmark_level2()
    t3 = benchmark_level3()
    t4 = benchmark_level4()
    t5 = benchmark_level5()
    t6 = benchmark_level6()
    
    # Tạo biểu đồ so sánh tổng quan cả 6 nhóm thuật toán
    benchmark_groups_overall(t1, t2, t3, t4, t5, t6)
    
    print("\n=================================================================")
    print("   BENCHMARK COMPLETED SUCCESSFULLY!")
    print(f"   Each Level (1-6) now has its own dedicated comparison chart!")
    print(f"   Overall comparison chart for all 6 groups generated!")
    print(f"   Charts saved in: {os.path.abspath(OUTPUT_DIR)}")
    print("=================================================================")
