# radio_tab/radio_tab.py
import random
import time
import pygame
from threading import Thread
import settings
import os

from .radio_shared_state import RadioSharedState
from .radio_station_loader import RadioStationLoader
from .playlist_manager import PlaylistManager
from .visualizer import Visualizer

class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        self.tab_instance.init_footer(self)
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        self.font_height = self.main_font.get_height()
        self.selected_station_rect = pygame.Rect(
            0,
            self.draw_space[0],
            (settings.SCREEN_WIDTH // 2) - (settings.TAB_SIDE_MARGIN * 2),
            self.font_height
        )
        size = settings.RADIO_STATION_SELECTION_DOT_SIZE
        self.selected_station_dot = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        self.selected_station_dot.fill(settings.PIP_BOY_GREEN)
        self.selected_station_dot_darker = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        self.selected_station_dot_darker.fill(settings.PIP_BOY_DARKER)
        self.radio_station_surface = None
        self.selected_station_text = None

        self.selected_station_index = 0

        self.shared_state = RadioSharedState()
        self.shared_state.station_playing = False
        self.shared_state.active_station_index = None

        self.current_song = None
        self.radio_music_thread_running = True

        self.loader = RadioStationLoader(settings.RADIO_BASE_FOLDER,
                                         settings.DCR_INTERMISSIONS_BASE_FOLDER)
        self.playlist_manager = PlaylistManager()
        self.visualizer = Visualizer(self.draw_space, self.screen, self.shared_state)

        Thread(target=self.load_radio_stations, daemon=True).start()
        Thread(target=self.update_radio_music, daemon=True).start()

    def _render_text(self, text: str):
        return self.main_font.render(text, True, settings.PIP_BOY_GREEN)

    def load_radio_stations(self):
        self.loader.load_radio_stations()
        self._prepare_radio_station_surface()
        self.update_station_list()

    def _prepare_radio_station_surface(self):
        if not self.loader.radio_stations:
            return
        height = self.font_height * len(self.loader.radio_stations)
        self.radio_station_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, height), pygame.SRCALPHA
        ).convert_alpha()
        for i, station_name in enumerate(self.loader.radio_stations):
            text_surface = self._render_text(station_name)
            self.radio_station_surface.blit(
                text_surface, (settings.RADIO_STATION_TEXT_MARGIN, i * self.font_height)
            )

    def update_station_list(self):
        if not self.loader.radio_stations:
            return
        self.selected_station_rect.y = self.selected_station_index * self.font_height
        selected_station_name = list(self.loader.radio_stations.keys())[self.selected_station_index]
        self.selected_station_text = self.main_font.render(
            selected_station_name, True, settings.PIP_BOY_DARKER
        )

    def play_station_switch_sound(self):
        sound = random.choice(os.listdir(settings.RADIO_STATIC_BURSTS_BASE_FOLDER))
        self.tab_instance.play_sfx(
            os.path.join(settings.RADIO_STATIC_BURSTS_BASE_FOLDER, sound),
            settings.VOLUME
        )

    def change_stations(self, direction: bool):
        new_index = self.selected_station_index + (-1 if direction else 1)
        if 0 <= new_index < len(self.loader.radio_stations):
            self.selected_station_index = new_index
            self.update_station_list()

    def select_station(self):
        if self.selected_station_index == self.shared_state.active_station_index:
            self.shared_state.station_playing = not self.shared_state.station_playing
        else:
            self.shared_state.station_playing = True

        if not self.shared_state.station_playing:
            self.tab_instance.play_sfx(settings.RADIO_TURN_OFF_SOUND)
        else:
            self.play_station_switch_sound()

        self.shared_state.active_station_index = self.selected_station_index

    def update_radio_music(self):
        while self.radio_music_thread_running:
            if (self.shared_state.active_station_index is not None and 
                self.shared_state.station_playing and 
                self.loader.radio_stations):
                station_names = list(self.loader.radio_stations.keys())
                if self.shared_state.active_station_index >= len(station_names):
                    pygame.time.wait(1000)
                    continue

                station_name = station_names[self.shared_state.active_station_index]
                station = self.loader.radio_stations[station_name]

                if station_name not in self.playlist_manager.station_playlists:
                    self.playlist_manager.station_playlists[station_name] = {
                        "playlist": self.playlist_manager.generate_station_playlist_for_station(
                            station, station_name
                        ),
                        "index": 0,
                        "song_start_time": None,
                        "initialized": False
                    }
                playlist_data = self.playlist_manager.station_playlists[station_name]
                playlist = playlist_data["playlist"]
                index = playlist_data["index"]

                if index >= len(playlist):
                    playlist_data["playlist"] = self.playlist_manager.generate_station_playlist_for_station(
                        station, station_name
                    )
                    playlist_data["index"] = 0
                    playlist_data["song_start_time"] = None
                    playlist_data["initialized"] = False
                    index = 0
                    playlist = playlist_data["playlist"]

                current_song = playlist[index]
                if settings.DCR_INTERMISSIONS_BASE_FOLDER in current_song:
                    duration_ms = self.loader.intermissions.get(current_song, 0)
                else:
                    duration_ms = station["music_files"].get(current_song, 0)
                duration_sec = duration_ms / 1000.0

                if playlist_data["song_start_time"] is None:
                    if not playlist_data["initialized"]:
                        random_offset = random.uniform(0, max(0, duration_sec - 1))
                        playlist_data["song_start_time"] = time.time() - random_offset
                        playlist_data["initialized"] = True
                    else:
                        playlist_data["song_start_time"] = time.time()

                song_offset = time.time() - playlist_data["song_start_time"]

                if song_offset < duration_sec:
                    if self.current_song != current_song:
                        try:
                            pygame.mixer.music.load(current_song)
                            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
                            pygame.mixer.music.play(start=song_offset)
                            self.current_song = current_song
                        except Exception as e:
                            print(f"Error playing {current_song}: {e}")
                            playlist_data["index"] += 1
                            playlist_data["song_start_time"] = None
                            self.current_song = None
                    else:
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(start=song_offset)
                else:
                    playlist_data["index"] += 1
                    playlist_data["song_start_time"] = None
                    self.current_song = None
                    pygame.mixer.music.stop()
            else:
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                self.current_song = None

            wait_time = 500 if self.shared_state.active_station_index is not None else 1000
            pygame.time.wait(wait_time)

    def handle_threads(self, tab_selected: bool):
        if tab_selected:
            self.visualizer.start()
        else:
            self.visualizer.stop()

    def render_station_list(self):
        if not self.radio_station_surface or not self.selected_station_text:
            return

        view_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - self.draw_space[0]),
            pygame.SRCALPHA
        ).convert_alpha()

        view_surface.blit(self.radio_station_surface, (0, 0))
        pygame.draw.rect(view_surface, settings.PIP_BOY_GREEN, self.selected_station_rect)
        view_surface.blit(self.selected_station_text,
                          (settings.RADIO_STATION_TEXT_MARGIN, self.selected_station_rect.y))

        if self.shared_state.active_station_index is not None and self.shared_state.station_playing:
            dot = (self.selected_station_dot_darker
                   if self.shared_state.active_station_index == self.selected_station_index
                   else self.selected_station_dot)
            dot_y = (self.shared_state.active_station_index * self.font_height +
                     (self.font_height // 2) -
                     (settings.RADIO_STATION_SELECTION_DOT_SIZE // 2))
            view_surface.blit(dot,
                              (settings.RADIO_STATION_TEXT_MARGIN - settings.RADIO_STATION_SELECTION_MARGIN, dot_y))

        self.screen.blit(view_surface, (settings.TAB_SIDE_MARGIN, self.draw_space[0]))

    def render_visualizer_waves(self):
        self.visualizer.render()

    def render(self):
        self.tab_instance.render_footer(self)
        self.render_station_list()
        self.render_visualizer_waves()
