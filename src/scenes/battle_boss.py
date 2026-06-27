from src.scenes.battle_base import BattleBase

class BattleBoss(BattleBase):
    def __init__(self, screen, health_bar=None, player_health=100):
        super().__init__(screen, level_name="boss_level")