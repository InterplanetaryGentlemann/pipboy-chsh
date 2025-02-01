from collections import deque
import configparser
import math
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


class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        # Radio Station State
        self.radio_stations = {}
        self.intermissions = {}  # Cache for intermission track durations

        self.selected_station_index = 0
        self.active_station_index = None
        self.previous_station_index = None
        self.station_playing = False
        self.station_playing_prev = False
        self.tab_selected = False


        # For background music playback management
        self.current_song = None
        self.radio_music_thread_running = True
        self.station_playlists = {}  # { station_name: {"playlist": [...], "index": int } }

        # Precompute font and UI elements
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        self.font_height = self.main_font.get_height()
        self.selected_station_rect = pygame.Rect(
            0,
            self.draw_space[0],
            (settings.SCREEN_WIDTH // 2) - (settings.TAB_SIDE_MARGIN * 2),
            self.font_height
        )

        self._prepare_selection_dots()
        self.radio_station_surface = None
        self.selected_station_text = None

        # Load radio stations in background
        Thread(target=self.load_radio_stations, daemon=True).start()

        # Visualizer Setup
        self._initialize_visualizer()
        self.wave_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT),
            pygame.SRCALPHA
        ).convert_alpha()

        # Start the background radio music thread
        Thread(target=self.update_radio_music, daemon=True).start()
        

    def _prepare_selection_dots(self):
        """Pre-create selection dot surfaces for performance."""
        size = settings.RADIO_STATION_SELECTION_DOT_SIZE
        self.selected_station_dot = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        self.selected_station_dot.fill(settings.PIP_BOY_GREEN)
        self.selected_station_dot_darker = pygame.Surface((size, size), pygame.SRCALPHA).convert_alpha()
        self.selected_station_dot_darker.fill(settings.PIP_BOY_DARKER)

    def _initialize_visualizer(self):
        """Set up visualizer parameters with precomputed values."""
        self.visualizer_size = settings.SCREEN_WIDTH // 2 - settings.TAB_SIDE_MARGIN * 2 - settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET
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

    @lru_cache(maxsize=32)
    def _render_text(self, text: str) -> pygame.Surface:
        """Cache rendered text surfaces to optimize performance."""
        return self.main_font.render(text, True, settings.PIP_BOY_GREEN)

    # -------------------- File and Station Loading --------------------
    def load_music_files(self, station_folder: str) -> Dict[str, int]:
        """Load music files efficiently. Returns a dict mapping file paths to durations (in ms)."""
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

    def load_radio_stations(self):
        """Load all radio stations asynchronously."""
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
                # Each station gets a start timestamp so that its “radio clock” advances continuously.
                station_data = {
                    "ordered": config.getboolean("metadata", "ordered", fallback=False),
                    "music_files": music_files,
                    "start_timestamp": time.time()  # radio timeline starts now
                }
                return station_name, station_data
            except Exception:
                return None
            
        def load_intermissions(base_path=None):
            intermissions = {}
            intermissions_path = base_path or settings.DCR_INTERMISSIONS_BASE_FOLDER
            
            if not os.path.exists(intermissions_path):
                return intermissions
            
            for entry in os.scandir(intermissions_path):
                if entry.is_dir():
                    intermissions.update(load_intermissions(entry.path))  # Recursive call for subdirectories
                elif entry.is_file() and entry.name.endswith('.ogg'):
                    try:
                        tag = TinyTag.get(entry.path)
                        intermissions[entry.path] = int(tag.duration * 1000)
                    except Exception:
                        continue
            
            return intermissions

        try:
            with os.scandir(settings.RADIO_BASE_FOLDER) as entries:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    self.radio_stations = {name: data for result in executor.map(load_single_station, entries) if result for name, data in [result]}
        except Exception:
            self.radio_stations = {}
        
        try:
            self.intermissions = load_intermissions()
        except Exception:
            self.intermissions = {}
                
        self._prepare_radio_station_surface()
        self.update_station_list()

    def _prepare_radio_station_surface(self):
        """Pre-render station names onto a single surface."""
        if not self.radio_stations:
            return
        height = self.font_height * len(self.radio_stations)
        self.radio_station_surface = pygame.Surface((settings.SCREEN_WIDTH, height), pygame.SRCALPHA).convert_alpha()
        for i, station_name in enumerate(self.radio_stations):
            text_surface = self._render_text(station_name)
            self.radio_station_surface.blit(text_surface, (settings.RADIO_STATION_TEXT_MARGIN, i * self.font_height))

    # -------------------- Playlist and State --------------------
    

    def add_intermissions_to_playlist(self, playlist: list) -> list:
        """
        Inserts intermissions before or after randomly selected songs, ensuring each song 
        has at most one intermission. Intermissions are chosen from appropriate directories.
        """
        if not playlist:
            return playlist

        # Determine the number of songs to add intermissions to, ensuring it's not too frequent
        freq = settings.INTERMISSION_FREQUENCY
        max_count = min(freq * 2, len(playlist) // 3)  # Adjust to limit frequency
        count = random.randint(1, max_count) if max_count >= 1 else 0
        if count == 0:
            return playlist  # No intermissions to add

        # Select unique songs to possibly add intermissions
        indices = random.sample(range(len(playlist)), count)
        intermission_choices = {}
        base_path = settings.DCR_INTERMISSIONS_BASE_FOLDER

        for i in indices:
            song = playlist[i]
            file_name = os.path.splitext(os.path.basename(song))[0]
            parts = file_name.split('_')
            if len(parts) < 2:
                continue  # Skip if filename format is incorrect

            artist = parts[-2]
            song_name = parts[-1]
            artist_path = os.path.join(base_path, artist)

            # Collect possible intermissions
            pre_options = []
            after_options = []

            # Helper to gather OGG files from a directory
            def gather_ogg_files(path):
                if os.path.exists(path):
                    for entry in os.scandir(path):
                        if entry.is_file() and entry.name.endswith('.ogg'):
                            yield entry.path

            # Check base artist directory
            pre_options.extend(gather_ogg_files(artist_path))
            after_options.extend(gather_ogg_files(artist_path))

            # Check 'pre' subdirectory
            pre_dir = os.path.join(artist_path, 'pre')
            pre_options.extend(gather_ogg_files(pre_dir))

            # Check 'after' subdirectory
            after_dir = os.path.join(artist_path, 'after')
            after_options.extend(gather_ogg_files(after_dir))

            # Check song-specific directories
            song_dir = os.path.join(artist_path, song_name)
            pre_options.extend(gather_ogg_files(song_dir))
            after_options.extend(gather_ogg_files(song_dir))

            song_pre_dir = os.path.join(song_dir, 'pre')
            pre_options.extend(gather_ogg_files(song_pre_dir))

            song_after_dir = os.path.join(song_dir, 'after')
            after_options.extend(gather_ogg_files(song_after_dir))

            # Randomly choose to add either pre or after if available
            has_pre = len(pre_options) > 0
            has_after = len(after_options) > 0

            if not (has_pre or has_after):
                continue  # No intermissions available for this song

            # Choose type ensuring we only add one per song
            choice = None
            if has_pre and has_after:
                choice = random.choice(['pre', 'after'])
            elif has_pre:
                choice = 'pre'
            else:
                choice = 'after'

            if choice == 'pre':
                selected = random.choice(pre_options)
                intermission_choices.setdefault(song, {})['pre'] = selected
            else:
                selected = random.choice(after_options)
                intermission_choices.setdefault(song, {})['after'] = selected

        # Build new playlist with intermissions
        new_playlist = []
        for song in playlist:
            # Add pre-intermission if exists
            if song in intermission_choices and 'pre' in intermission_choices[song]:
                new_playlist.append(intermission_choices[song]['pre'])
            # Add the song
            new_playlist.append(song)
            # Add after-intermission if exists
            if song in intermission_choices and 'after' in intermission_choices[song]:
                new_playlist.append(intermission_choices[song]['after'])

        return new_playlist

        
    
    
    def generate_station_playlist_for_station(self, station, station_name=None) -> list:
        """
        Generates a playlist for a given station.
        If the station is not ordered, the list will be randomly shuffled.
        If station_name is provided and matches Diamond City Radio,
        intermissions are added.
        """
        playlist = list(station["music_files"].keys())
        if not station["ordered"]:
            random.shuffle(playlist)
        if station_name and station_name == "Diamond City Radio":
            playlist = self.add_intermissions_to_playlist(playlist)
        return playlist


    def play_station_switch_sound(self):
        """Play the station switch sound effect."""
        sound = random.choice(os.listdir(settings.RADIO_STATIC_BURSTS_BASE_FOLDER))      
        self.tab_instance.play_sfx(os.path.join(settings.RADIO_STATIC_BURSTS_BASE_FOLDER, sound), settings.VOLUME)
        pass


    def change_stations(self, direction: bool):
        """Change stations with bounds checking."""
        new_index = self.selected_station_index + (-1 if direction else 1)
        if 0 <= new_index < len(self.radio_stations):
            self.selected_station_index = new_index
            self.update_station_list()


    def select_station(self):
        """Select the current station.
        If the station is already active, toggle play/pause.
        Otherwise, set the new station as active.
        """
        if self.selected_station_index == self.active_station_index:
            self.station_playing = not self.station_playing
        else:
            self.station_playing = True
            
        if not self.station_playing:
            self.tab_instance.play_sfx(settings.RADIO_TURN_OFF_SOUND)
        else:
            self.play_station_switch_sound()
        
        self.active_station_index = self.selected_station_index

    def update_station_list(self):
        """Update the precomputed surfaces and state for the station list."""
        if not self.radio_stations:
            return
        # Update highlighted station rectangle position
        self.selected_station_rect.y = self.selected_station_index * self.font_height

        # Pre-render the selected station text with a darker color
        selected_station_name = list(self.radio_stations.keys())[self.selected_station_index]
        self.selected_station_text = self.main_font.render(selected_station_name, True, settings.PIP_BOY_DARKER)

    # -------------------- Visualiser --------------------
    def set_wave_pattern(self, pattern_name):
        """Update wave pattern using vectorized operations."""
        pattern = self.wave_patterns[pattern_name]
        random_values = np.random.uniform(pattern[:, 0], pattern[:, 1], size=(len(self.waves), 2)).astype(np.float32)
        self.waves[:, 3:5] = random_values  # Update target frequency and amplitude

    def change_visualizer_wave(self):
        """Generate complex waveform using vectorized operations."""
        # Smoothly transition frequency and amplitude toward target values
        self.waves[:, 0:2] += (self.waves[:, 3:5] - self.waves[:, 0:2]) * settings.RADIO_WAVE_SMOOTHING_FACTOR

        # Update phases and wrap them to [0, 2*pi)
        self.waves[:, 2] = (self.waves[:, 2] + self.waves[:, 0] * 0.08) % (2 * np.pi)

        # Calculate total wave from all sine waves
        total_wave = np.sum(np.sin(self.waves[:, 2]) * self.waves[:, 1]) / len(self.waves)

        # Adjust wave pattern based on state and simple conditions
        if not self.station_playing and abs(total_wave) < 0.05:
            self.set_wave_pattern('idle')
            self.change_station_wave_counter = 0
        elif self.active_station_index != self.previous_station_index:
            self.set_wave_pattern('changing')
            self.change_station_wave_counter = random.randint(40, 150)
            self.previous_station_index = self.active_station_index
        elif self.change_station_wave_counter > 0:
            self.change_station_wave_counter -= 1
            if self.change_station_wave_counter == 1:
                self.set_wave_pattern('playing')
        elif abs(total_wave) < 0.05 and random.random() < 0.1:
            self.set_wave_pattern('playing')

        with self.wave_point_lock:
            # Use numpy roll to shift the waveform and insert new value
            self.wave_points = np.roll(self.wave_points, -1)
            self.wave_points[-1] = total_wave

    # -------------------- Threads --------------------
    def update_visualiser(self):
        """Optimized visualizer update loop using a sleep delay."""
        while self.visualizer_thread_running:
            self.change_visualizer_wave()
            pygame.time.wait(settings.SPEED * 8)  # adjust delay if necessary

    def handle_threads(self, tab_selected: bool):
        """Start or stop the visualizer thread based on current tab state."""
        self.tab_selected = tab_selected
        if tab_selected:
            if not self.visualizer_thread or not self.visualizer_thread.is_alive():
                self.visualizer_thread_running = True
                self.visualizer_thread = Thread(target=self.update_visualiser, daemon=True)
                self.visualizer_thread.start()
        else:
            if self.visualizer_thread and self.visualizer_thread.is_alive():
                self.visualizer_thread_running = False
                self.visualizer_thread.join()
                self.visualizer_thread = None

    def update_radio_music(self):
        """
        Background thread that continuously manages playback for the active station.
        Each station maintains its own playlist state (the current list of songs, the current index,
        and the start time of the current song). When a station’s current song is playing, the code
        computes the current offset from that start time. Once the song is finished, it advances to the
        next song (regenerating the playlist if necessary).
        """
        while self.radio_music_thread_running:
            if self.active_station_index is not None and self.station_playing and self.radio_stations:
                station_names = list(self.radio_stations.keys())
                if self.active_station_index >= len(station_names):
                    pygame.time.wait(1000)
                    continue

                station_name = station_names[self.active_station_index]
                station = self.radio_stations[station_name]

                # Get (or initialize) the persistent playlist for this station.
                if station_name not in self.station_playlists:
                    self.station_playlists[station_name] = {
                        "playlist": self.generate_station_playlist_for_station(station, station_name),
                        "index": 0,
                        "song_start_time": None,
                        "initialized": False  # Track if the first song has been randomized
                    }
                playlist_data = self.station_playlists[station_name]
                playlist = playlist_data["playlist"]
                index = playlist_data["index"]

                # If we have reached the end of the playlist, regenerate it.
                if index >= len(playlist):
                    playlist_data["playlist"] = self.generate_station_playlist_for_station(station, station_name)
                    playlist_data["index"] = 0
                    playlist_data["song_start_time"] = None
                    playlist_data["initialized"] = False  # Reset for new playlist
                    index = 0
                    playlist = playlist_data["playlist"]
                    
                current_song = playlist[index]
                # Get the song's duration (in ms)
                if settings.DCR_INTERMISSIONS_BASE_FOLDER in current_song:
                    duration_ms = self.intermissions.get(current_song, 0)
                else:
                    duration_ms = station["music_files"].get(current_song, 0)
                duration_sec = duration_ms / 1000.0

                # Only apply a random offset for the first song after startup
                if playlist_data["song_start_time"] is None:
                    if not playlist_data["initialized"]:
                        random_offset = random.uniform(0, max(0, duration_sec - 1))  # Avoid negative values
                        playlist_data["song_start_time"] = time.time() - random_offset
                        playlist_data["initialized"] = True  # Mark as initialized
                    else:
                        playlist_data["song_start_time"] = time.time()

                # Compute the current offset into the song.
                song_offset = time.time() - playlist_data["song_start_time"]

                if song_offset < duration_sec:
                    # The current song is still playing.
                    if self.current_song != current_song:
                        try:
                            pygame.mixer.music.load(current_song)
                            pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
                            # Start playing from the current offset.
                            pygame.mixer.music.play(start=song_offset)
                            self.current_song = current_song
                        except Exception as e:
                            print(f"Error playing {current_song}: {e}")
                            # Skip to the next song if an error occurs.
                            playlist_data["index"] += 1
                            playlist_data["song_start_time"] = None
                            self.current_song = None
                    else:
                        # If playback stopped unexpectedly, resume it.
                        if not pygame.mixer.music.get_busy():
                            pygame.mixer.music.play(start=song_offset)
                else:
                    # The current song has finished.
                    playlist_data["index"] += 1
                    playlist_data["song_start_time"] = None
                    self.current_song = None
                    pygame.mixer.music.stop()
            else:
                # No active station or radio is turned off.
                if pygame.mixer.music.get_busy():
                    pygame.mixer.music.stop()
                self.current_song = None

            wait_time = 500 if self.tab_selected else 1000
            pygame.time.wait(wait_time)

    # -------------------- Rendering --------------------
    def render_station_list(self):
        """Render the station list and highlight the selected station."""
        if not self.radio_station_surface or not self.selected_station_text:
            return

        # Create a view surface for the station list area (reuse if possible)
        view_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - self.draw_space[0]),
            pygame.SRCALPHA
        ).convert_alpha()

        # Blit the pre-rendered full station list
        view_surface.blit(self.radio_station_surface, (0, 0))

        # Draw the highlight rectangle over the selected station
        pygame.draw.rect(view_surface, settings.PIP_BOY_GREEN, self.selected_station_rect)

        # Blit the darker text for the selected station
        view_surface.blit(self.selected_station_text, (settings.RADIO_STATION_TEXT_MARGIN, self.selected_station_rect.y))

        # Blit the selection dot if a station is active and playing
        if self.active_station_index is not None and self.station_playing:
            dot = (self.selected_station_dot_darker if self.active_station_index == self.selected_station_index
                   else self.selected_station_dot)
            dot_y = (self.active_station_index * self.font_height) + (self.font_height // 2) - (settings.RADIO_STATION_SELECTION_DOT_SIZE // 2)
            view_surface.blit(dot, (settings.RADIO_STATION_TEXT_MARGIN - settings.RADIO_STATION_SELECTION_MARGIN, dot_y))

        # Finally, blit the view surface onto the main screen
        self.screen.blit(view_surface, (settings.TAB_SIDE_MARGIN, self.draw_space[0]))

    def render_visualizer_waves(self):
        """Render the visualiser waves using pre-allocated surfaces and vectorized coordinates."""
        with self.wave_point_lock:
            points = self.wave_points.copy()

        # Clear the wave surface without reallocating it
        self.wave_surface.fill((0, 0, 0, 0))

        # Vectorized computation for x and y coordinates
        x_coords = self.vis_x + self.x_positions
        # Scale points to fit the visualizer height and convert to int
        y_coords = self.midpoint_y + (points * (self.visualizer_size // 2)).astype(np.int32)

        # Combine x and y coordinates into a 2D points array
        points_array = np.column_stack((x_coords, y_coords))

        # Draw the wave as connected lines
        pygame.draw.lines(self.wave_surface, settings.PIP_BOY_GREEN, False, points_array, 1)

        # Blit the wave surface onto the main screen
        self.screen.blit(self.wave_surface, (0, 0))

    def render(self):
        """Render the radio tab UI including footer, station list, and visualizer."""
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))
        self.render_station_list()
        self.render_visualizer_waves()
