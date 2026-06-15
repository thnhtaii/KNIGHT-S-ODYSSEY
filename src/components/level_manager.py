class LevelLogicManager:
    def __init__(self, slime_list):
        self.slime_list = slime_list
        self.door_unlocked = False

    def update(self):
        # Cập nhật trạng thái mở cửa nếu tất cả slime đã chết
        if all(not slime.alive for slime in self.slime_list):
            if not self.door_unlocked:
                print("All slimes defeated. Door is now unlocked!")
            self.door_unlocked = True

    def is_door_unlocked(self):
        return self.door_unlocked

    def check_victory(self, player_rect, door_rect):
        return player_rect.colliderect(door_rect)

    
