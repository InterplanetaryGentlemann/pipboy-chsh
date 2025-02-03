import configparser
import random
import pygame
import settings
import os
from tinytag import TinyTag
from threading import Thread, Lock
from typing import Dict
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import numpy as np
import time  


# =============================================================================
# Shared State: Contains data that both the RadioTab and Visualizer need to read
# =============================================================================
class RadioSharedState:
    def __init__(self):
        self.station_playing = False
        self.active_station_index = None
        self.previous_station_index = None


# =============================================================================
# Data Loader: Loads radio station files and intermission files from disk
# =============================================================================
class RadioStationLoader:
    def __init__(self, base_folder, intermissions_base_folder):
        self.base_folder = base_folder
        self.intermissions_base_folder = intermissions_base_folder
        self.radio_stations = {}
        self.intermissions = {}

    def load_music_files(self, station_folder: str) -> Dict[str, int]:
        music_files = {}
        try:
            for entry in os.scandir(station_folder):
                if entry.name.endswith('.ogg'):
                    try:
                        tag = TinyTag.get(entry.path)
                        music_files[entry.path] = int(tag.duration * 1000)
                    except Exception:
                        continue
        except Exception:
            pass
        return music_files

    def load_intermissions(self, base_path=None) -> Dict[str, int]:
        intermissions = {}
        intermissions_path = base_path or self.intermissions_base_folder
        if not os.path.exists(intermissions_path):
            return intermissions

        for entry in os.scandir(intermissions_path):
            if entry.is_dir():
                intermissions.update(self.load_intermissions(entry.path))  # recursive call
            elif entry.is_file() and entry.name.endswith('.ogg'):
                try:
                    tag = TinyTag.get(entry.path)
                    intermissions[entry.path] = int(tag.duration * 1000)
                except Exception:
                    continue

        return intermissions

    def load_radio_stations(self):
        def load_single_station(entry):
            if not entry.is_dir():
                return None
            ini_path = os.path.join(entry.path, "station.ini")
            if not os.path.exists(ini_path):
                return None
            try:
                config = configparser.ConfigParser()
                with open(ini_path) as f:
                    config.read_file(f)
                music_files = self.load_music_files(entry.path)
                if not music_files:
                    return None
                station_name = config.get("metadata", "station_name", fallback=entry.name)
                station_data = {
                    "ordered": config.getboolean("metadata", "ordered", fallback=False),
                    "music_files": music_files,
                    "start_timestamp": time.time()  # radio timeline starts now
                }
                return station_name, station_data
            except Exception:
                return None

        try:
            with os.scandir(self.base_folder) as entries:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    self.radio_stations = {
                        name: data
                        for result in executor.map(load_single_station, entries)
                        if result
                        for name, data in [result]
                    }
        except Exception:
            self.radio_stations = {}

        try:
            self.intermissions = self.load_intermissions()
        except Exception:
            self.intermissions = {}


# =============================================================================
# Playlist Manager: Handles playlist generation and intermission insertion
# =============================================================================
class PlaylistManager:
    def __init__(self):
        self.station_playlists = {}

    def add_intermissions_to_playlist(self, playlist: list) -> list:
        if not playlist:
            return playlist

        freq = settings.INTERMISSION_FREQUENCY
        max_count = min(freq * 2, len(playlist) // 3)
        count = random.randint(1, max_count) if max_count >= 1 else 0
        if count == 0:
            return playlist

        indices = random.sample(range(len(playlist)), count)
        intermission_choices = {}
        base_path = settings.DCR_INTERMISSIONS_BASE_FOLDER

        for i in indices:
            song = playlist[i]
            file_name = os.path.splitext(os.path.basename(song))[0]
            parts = file_name.split('_')
            if len(parts) < 2:
                continue

            artist = parts[-2]
            song_name = parts[-1]
            artist_path = os.path.join(base_path, artist)

            pre_options = []
            after_options = []

            def gather_ogg_files(path):
                if os.path.exists(path):
                    for entry in os.scandir(path):
                        if entry.is_file() and entry.name.endswith('.ogg'):
                            yield entry.path

            pre_options.extend(gather_ogg_files(artist_path))
            after_options.extend(gather_ogg_files(artist_path))

            pre_dir = os.path.join(artist_path, 'pre')
            pre_options.extend(gather_ogg_files(pre_dir))

            after_dir = os.path.join(artist_path, 'after')
            after_options.extend(gather_ogg_files(after_dir))

            song_dir = os.path.join(artist_path, song_name)
            pre_options.extend(gather_ogg_files(song_dir))
            after_options.extend(gather_ogg_files(song_dir))

            song_pre_dir = os.path.join(song_dir, 'pre')
            pre_options.extend(gather_ogg_files(song_pre_dir))

            song_after_dir = os.path.join(song_dir, 'after')
            after_options.extend(gather_ogg_files(song_after_dir))

            has_pre = len(pre_options) > 0
            has_after = len(after_options) > 0

            if not (has_pre or has_after):
                continue

            choice = random.choice(['pre', 'after']) if has_pre and has_after else ('pre' if has_pre else 'after')
            if choice == 'pre':
                selected = random.choice(pre_options)
                intermission_choices.setdefault(song, {})['pre'] = selected
            else:
                selected = random.choice(after_options)
                intermission_choices.setdefault(song, {})['after'] = selected

        new_playlist = []
        for song in playlist:
            if song in intermission_choices and 'pre' in intermission_choices[song]:
                new_playlist.append(intermission_choices[song]['pre'])
            new_playlist.append(song)
            if song in intermission_choices and 'after' in intermission_choices[song]:
                new_playlist.append(intermission_choices[song]['after'])

        return new_playlist

    def generate_station_playlist_for_station(self, station, station_name=None) -> list:
        playlist = list(station["music_files"].keys())
        if not station["ordered"]:
            random.shuffle(playlist)
        if station_name and station_name == "Diamond City Radio":
            playlist = self.add_intermissions_to_playlist(playlist)
        return playlist


# =============================================================================
# Visualizer: Manages wave data, updating, and rendering.
# Uses shared state for the current station playing and active station index.
# =============================================================================
class Visualizer:
    def __init__(self, draw_space, screen, shared_state: RadioSharedState):
        self.draw_space = draw_space
        self.screen = screen
        self.shared_state = shared_state

        self.visualizer_size = (settings.SCREEN_WIDTH // 2 -
                                settings.TAB_SIDE_MARGIN * 2 -
                                settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET)
        self.vis_x = settings.SCREEN_WIDTH // 2 + settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET // 2
        self.vis_y = self.draw_space[0]
        self.midpoint_y = self.vis_y + self.visualizer_size // 2

        self.wave_points = np.zeros(64, dtype=np.float32)
        self.wave_point_lock = Lock()
        self.x_positions = np.linspace(0, self.visualizer_size, 64, dtype=np.int32)

        self.waves = np.array([
            [1.0, 0.5, 0.0, 1.0, 0.5],
            [2.0, 0.3, 0.0, 2.0, 0.3],
            [3.0, 0.2, 0.0, 3.0, 0.2]
        ], dtype=np.float32)

        self.wave_patterns = {
            'idle': np.array([[0.2, 0.8], [0.05, 0.2]], dtype=np.float32),
            'playing': np.array([[1.0, 4.0], [0.4, 1.5]], dtype=np.float32),
            'changing': np.array([[5.0, 10.0], [0.1, 0.6]], dtype=np.float32)
        }

        self.visualizer_thread = None
        self.visualizer_thread_running = False
        self.change_station_wave_counter = 0

        self.wave_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

    def _prepare_wave_pattern(self, pattern_name):
        pattern = self.wave_patterns[pattern_name]
        random_values = np.random.uniform(pattern[:, 0], pattern[:, 1],
                                          size=(len(self.waves), 2)).astype(np.float32)
        self.waves[:, 3:5] = random_values

    def change_visualizer_wave(self):
        # Always get the current state from shared_state
        station_playing = self.shared_state.station_playing
        active_station_index = self.shared_state.active_station_index

        # Smoothly transition frequency and amplitude toward target values.
        self.waves[:, 0:2] += (self.waves[:, 3:5] - self.waves[:, 0:2]) * settings.RADIO_WAVE_SMOOTHING_FACTOR
        self.waves[:, 2] = (self.waves[:, 2] + self.waves[:, 0] * 0.08) % (2 * np.pi)
        total_wave = np.sum(np.sin(self.waves[:, 2]) * self.waves[:, 1]) / len(self.waves)

        # Decide which wave pattern to use based on state.
        if not station_playing and abs(total_wave) < 0.05:
            self._prepare_wave_pattern('idle')
            self.change_station_wave_counter = 0
        elif (self.shared_state.previous_station_index is None or
              active_station_index != self.shared_state.previous_station_index):
            self._prepare_wave_pattern('changing')
            self.change_station_wave_counter = random.randint(40, 150)
            self.shared_state.previous_station_index = active_station_index
        elif self.change_station_wave_counter > 0:
            self.change_station_wave_counter -= 1
            if self.change_station_wave_counter == 1:
                self._prepare_wave_pattern('playing')
        elif abs(total_wave) < 0.05 and random.random() < 0.1:
            self._prepare_wave_pattern('playing')

        with self.wave_point_lock:
            self.wave_points = np.roll(self.wave_points, -1)
            self.wave_points[-1] = total_wave

    def update_visualiser(self):
        while self.visualizer_thread_running:
            self.change_visualizer_wave()
            pygame.time.wait(settings.SPEED * 8)

    def start(self):
        if not self.visualizer_thread or not self.visualizer_thread.is_alive():
            self.visualizer_thread_running = True
            self.visualizer_thread = Thread(
                target=self.update_visualiser,
                daemon=True
            )
            self.visualizer_thread.start()

    def stop(self):
        if self.visualizer_thread and self.visualizer_thread.is_alive():
            self.visualizer_thread_running = False
            self.visualizer_thread.join()
            self.visualizer_thread = None

    def render(self):
        with self.wave_point_lock:
            points = self.wave_points.copy()
        self.wave_surface.fill((0, 0, 0, 0))
        x_coords = self.vis_x + self.x_positions
        y_coords = self.midpoint_y + (points * (self.visualizer_size // 2)).astype(np.int32)
        points_array = np.column_stack((x_coords, y_coords))
        pygame.draw.lines(self.wave_surface, settings.PIP_BOY_LIGHT, False, points_array, 1)
        self.screen.blit(self.wave_surface, (0, 0))


# =============================================================================
# Main RadioTab Class: Coordinates UI, station state, playlist, and visualizer.
# =============================================================================
class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        # Initialize UI elements.
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
        self.selected_station_dot.fill(settings.PIP_BOY_LIGHT)
        self.selected_station_dot_darker = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        self.selected_station_dot_darker.fill(settings.PIP_BOY_DARKER)
        self.radio_station_surface = None
        self.selected_station_text = None

        # Radio station state.
        self.selected_station_index = 0

        # Create shared state and initialize its values.
        self.shared_state = RadioSharedState()
        self.shared_state.station_playing = False
        self.shared_state.active_station_index = None

        # Current song and playback management.
        self.current_song = None
        self.radio_music_thread_running = True

        # Create helper instances.
        self.loader = RadioStationLoader(settings.RADIO_BASE_FOLDER,
                                         settings.DCR_INTERMISSIONS_BASE_FOLDER)
        self.playlist_manager = PlaylistManager()
        self.visualizer = Visualizer(self.draw_space, self.screen, self.shared_state)

        # Load radio stations in a background thread.
        Thread(target=self.load_radio_stations, daemon=True).start()

        # Start background thread to manage radio music playback.
        Thread(target=self.update_radio_music, daemon=True).start()

    def _render_text(self, text: str) -> pygame.Surface:
        return self.main_font.render(text, True, settings.PIP_BOY_LIGHT)

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
            os.path.join(settings.RADIO_STATIC_BURSTS_BASE_FOLDER, sound), settings.VOLUME
        )

    def change_stations(self, direction: bool):
        new_index = self.selected_station_index + (-1 if direction else 1)
        if 0 <= new_index < len(self.loader.radio_stations):
            self.selected_station_index = new_index
            self.update_station_list()

    def select_station(self):
        # Toggle play/pause if the same station is selected.
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
        # Start or stop the visualizer thread based on tab state.
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
        pygame.draw.rect(view_surface, settings.PIP_BOY_LIGHT, self.selected_station_rect)
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
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))
        self.render_station_list()
        self.render_visualizer_waves()
