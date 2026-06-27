class AIStatsTracker:
    # { zombie_name: { "paths_found": 0, "player_reached": 0, "damage_dealt": 0 } }
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
    def log_pathfinding(cls, zombie_name):
        if zombie_name not in cls._stats:
            cls._stats[zombie_name] = {
                "paths_found": 0,
                "player_reached": 0,
                "damage_dealt": 0
            }
        cls._stats[zombie_name]["paths_found"] += 1

    @classmethod
    def log_attack(cls, zombie_name, damage):
        if zombie_name not in cls._stats:
            cls._stats[zombie_name] = {
                "paths_found": 0,
                "player_reached": 0,
                "damage_dealt": 0
            }
        cls._stats[zombie_name]["player_reached"] += 1
        cls._stats[zombie_name]["damage_dealt"] += damage
        print(f"[AIStatsTracker] {zombie_name} cắn player, damage_dealt={cls._stats[zombie_name]['damage_dealt']}")
