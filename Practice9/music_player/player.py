import pygame
import os

class MusicPlayer:
    def __init__(self, music_folder):
        pygame.mixer.init()
        self.music_folder = music_folder
        self.playlist = [f for f in os.listdir(music_folder) if f.endswith(('.mp3', '.wav'))]
        self.current_index = 0
        self.is_playing = False

    def play(self):
        if not self.playlist:
            return
        
        path = os.path.join(self.music_folder, self.playlist[self.current_index])
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        self.is_playing = True

    def stop(self):
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def prev_track(self):
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def get_current_track_name(self):
        if not self.playlist:
            return "No Music Found"
        return self.playlist[self.current_index]

    def get_progress(self):
        """Returns elapsed time in seconds."""
        if not self.is_playing:
            return 0
        return pygame.mixer.music.get_pos() // 1000 