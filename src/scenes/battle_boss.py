from src.scenes.battle_base import BattleBase

class BattleBoss(BattleBase):
    def __init__(self, screen):
        super().__init__(screen, level_name="boss_level")