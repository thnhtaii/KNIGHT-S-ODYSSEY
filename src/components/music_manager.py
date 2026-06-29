import pygame
import os

class MusicManager:
    is_muted = False  # Lưu trạng thái tắt nhạc toàn cục

    def __init__(self):
        pygame.mixer.init()
        self.current_music = None

    def play_music(self, music_path, volume=0.5):
        if self.current_music == music_path:
            if MusicManager.is_muted:
                pygame.mixer.music.pause()
            else:
                pygame.mixer.music.unpause()
            return  # Nếu đang phát đúng bài đó rồi thì không cần load lại

        pygame.mixer.music.stop()
        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(volume)
            pygame.mixer.music.play(-1)
            self.current_music = music_path
            if MusicManager.is_muted:
                pygame.mixer.music.pause()
        except Exception as e:
            print(f"Error loading music: {e}")

    def mute_music(self):
        MusicManager.is_muted = True
        pygame.mixer.music.pause()

    def unmute_music(self):
        MusicManager.is_muted = False
        pygame.mixer.music.unpause()

    def toggle_mute(self):
        if MusicManager.is_muted:
            self.unmute_music()
        else:
            self.mute_music()
