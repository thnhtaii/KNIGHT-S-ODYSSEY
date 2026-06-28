class AIStatsTracker:
    # { enemy_name: { "paths_found": 0, "player_reached": 0, "damage_dealt": 0, "total_path_len": 0, "total_time_ms": 0.0 } }
    _stats = {}
    _current_stage = ""

    @classmethod
    def reset(cls, stage_name=""):
        cls._stats = {}
        cls._current_stage = stage_name
        print(f"[AIStatsTracker] Reset statistics for {stage_name}")

    @classmethod
    def get_stats(cls):
        return cls._stats

    @classmethod
    def log_pathfinding(cls, enemy_name, path_len=0, time_ms=0.0):
        if enemy_name not in cls._stats:
            cls._stats[enemy_name] = {
                "paths_found": 0,
                "player_reached": 0,
                "damage_dealt": 0,
                "total_path_len": 0,
                "total_time_ms": 0.0
            }
        cls._stats[enemy_name]["paths_found"] += 1
        cls._stats[enemy_name]["total_path_len"] += path_len
        cls._stats[enemy_name]["total_time_ms"] += time_ms

    @classmethod
    def log_attack(cls, enemy_name, damage):
        if enemy_name not in cls._stats:
            cls._stats[enemy_name] = {
                "paths_found": 0,
                "player_reached": 0,
                "damage_dealt": 0,
                "total_path_len": 0,
                "total_time_ms": 0.0
            }
        cls._stats[enemy_name]["player_reached"] += 1
        cls._stats[enemy_name]["damage_dealt"] += damage
        print(f"[AIStatsTracker] {enemy_name} tấn công, damage_dealt={cls._stats[enemy_name]['damage_dealt']}")
