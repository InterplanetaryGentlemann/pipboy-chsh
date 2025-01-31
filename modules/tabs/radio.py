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


class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        """Initialize station list."""
        self.radio_stations = {}
        self.amount_of_stations = 0
        self.selected_station_index = 0
        self.active_station_index = None
        self.previous_station_index = None
        self.station_playing = False

        # Pre-calculate constants
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        self.font_height = self.main_font.get_height()
                     
        self.selected_station_rect = pygame.Rect(0, self.draw_space[0], (settings.SCREEN_WIDTH // 2) - (settings.TAB_SIDE_MARGIN * 2), self.font_height)
        
        self.selected_station_dot = pygame.Surface((settings.RADIO_STATION_SELECTION_DOT_SIZE, settings.RADIO_STATION_SELECTION_DOT_SIZE), pygame.SRCALPHA)
        self.selected_station_dot.fill(settings.PIP_BOY_GREEN)
        self.selected_station_dot_darker = pygame.Surface((settings.RADIO_STATION_SELECTION_DOT_SIZE, settings.RADIO_STATION_SELECTION_DOT_SIZE), pygame.SRCALPHA)
        self.selected_station_dot_darker.fill(settings.PIP_BOY_DARKER)  
        # Minimal UI state
        self.radio_station_surface = None     
        self.selected_station_text = None
          
        # Start loading in background with minimal priority
        Thread(target=self.load_radio_stations, daemon=True).start()
        
        """Initialize visualiser."""
        self.wave_points = deque(maxlen=256)
        self.wave_point_lock = Lock()
        
        # Optimized visualizer parameters
        self.visualizer_size = (settings.SCREEN_WIDTH // 2) - (settings.TAB_SIDE_MARGIN * 2) - settings.RADIO_WAVE_VISUALISER_SIZE_OFFSET
        # Pre-calculated x positions
        self.x_positions = np.linspace(0, self.visualizer_size, 256)
        
        # Wave generation parameters
        self.phase = 0.0
        self.frequency = 1.0
        self.amplitude = 1.0
        self.target_frequency = 1.0
        self.target_amplitude = 1.0
        
        self.change_station_wave_counter = 0
        
        # Thread control
        self.visualizer_thread_running = False
        self.visualizer_thread = None
        
        
        # Multi-wave parameters
        self.waves = [
            {"phase": 0.0, "freq": 1.0, "amp": 0.5, "target_freq": 1.0, "target_amp": 0.5},
            {"phase": 0.0, "freq": 2.0, "amp": 0.3, "target_freq": 2.0, "target_amp": 0.3},
            {"phase": 0.0, "freq": 3.0, "amp": 0.2, "target_freq": 3.0, "target_amp": 0.2}
        ]
        
        self.smoothing_factor = 0.05  # Slower smoothing for more natural transitions
        
        # Different wave patterns
        self.wave_patterns = {
            'idle': {'freq_range': (0.2, 0.8), 'amp_range': (0.05, 0.2)},
            'playing': {'freq_range': (0.4, 1.0), 'amp_range': (0.4, 1.5)},
            'changing': {'freq_range': (2.0, 5.0), 'amp_range': (0.1, 0.6)}
        }
        
        self.vis_x = settings.SCREEN_WIDTH // 2 + (settings.RADIO_WAVE_VISUALISER_SIZE_OFFSET // 2)
        self.vis_y = self.draw_space[0]
                

    @lru_cache(maxsize=32)
    def _render_text(self, text: str) -> pygame.Surface:
        """Cache rendered text surfaces to avoid repeated rendering."""
        return self.main_font.render(text, True, settings.PIP_BOY_GREEN)

    # -------------------- File and Station Loading --------------------


    def load_music_files(self, station_folder: str) -> Dict[str, int]:
        """Load music files with minimal memory usage."""
        music_files = {}
        try:
            for f in os.scandir(station_folder):  # More efficient than listdir
                if f.name.endswith('.ogg'):
                    try:
                        tag = TinyTag.get(f.path)
                        music_files[f.path] = int(tag.duration * 1000)
                    except:
                        continue
        except:
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

                return (
                    config.get("metadata", "station_name", fallback=entry.name),
                    {
                        "ordered": config.getboolean("metadata", "ordered", fallback=False),
                        "music_files": music_files
                    }
                )
            except Exception:
                return None

        try:
            with os.scandir(settings.RADIO_BASE_FOLDER) as entries:
                with ThreadPoolExecutor(max_workers=2) as executor:
                    stations = executor.map(load_single_station, entries)
                    self.radio_stations = {
                        name: data for result in stations
                        if result and (name := result[0]) and (data := result[1])
                    }
        except Exception:
            self.radio_stations = {}

        self.amount_of_stations = len(self.radio_stations)
        self._prepare_radio_station_surface()
        self.update_station_list()


    def _prepare_radio_station_surface(self):
        """Pre-render all station names onto a single surface."""
        if not self.radio_stations:
            return

        height = self.font_height * self.amount_of_stations
        self.radio_station_surface = pygame.Surface((settings.SCREEN_WIDTH, height), pygame.SRCALPHA)

        for i, station_name in enumerate(self.radio_stations):
            text_surface = self._render_text(station_name)
            self.radio_station_surface.blit(text_surface, (settings.RADIO_STATION_TEXT_MARGIN, i * self.font_height))

    # -------------------- Playlist and State --------------------

    def generate_playlist(self) -> list:
        """Generate playlist with minimal operations."""
        if not self.radio_stations:
            return []
            
        stations = list(self.radio_stations.keys())
        if self.selected_station_index >= len(stations):
            return []
            
        station = self.radio_stations[stations[self.selected_station_index]]
        playlist = list(station["music_files"].keys())
        
        if not station["ordered"]:
            random.shuffle(playlist)
            
        return playlist

    def change_stations(self, direction: bool):
        """Fast station change."""
        new_index = self.selected_station_index + (-1 if direction else 1)
        if 0 <= new_index < self.amount_of_stations:
            self.selected_station_index = new_index
            self.update_station_list()

    def select_station(self):
        """Select the current station."""
        if self.selected_station_index == self.active_station_index:
            self.station_playing = not self.station_playing
        else:
            self.station_playing = True
        self.active_station_index = self.selected_station_index

    def update_station_list(self):
        """Update the precomputed surfaces and state for the station list."""
        if not self.radio_stations:
            return
        # Highlighted station position
        self.selected_station_rect.y = self.selected_station_index * self.font_height

        # Pre-render the selected station text with a darker color
        selected_station_name = list(self.radio_stations.keys())[self.selected_station_index]
                
        self.selected_station_text = self.main_font.render(selected_station_name, True, settings.PIP_BOY_DARKER)


    # -------------------- Visualiser --------------------
    def set_wave_pattern(self, pattern_name):
        """Set wave parameters based on predefined patterns."""
        pattern = self.wave_patterns[pattern_name]
        for wave in self.waves:
            wave["target_freq"] = np.random.uniform(*pattern['freq_range'])
            wave["target_amp"] = np.random.uniform(*pattern['amp_range'])
    
    def change_visualizer_wave(self):
        """Generate complex waveform from multiple sine waves."""
        total_wave = 0
        
        for wave in self.waves:
            # Smooth parameter transitions
            wave["freq"] += (wave["target_freq"] - wave["freq"]) * self.smoothing_factor
            wave["amp"] += (wave["target_amp"] - wave["amp"]) * self.smoothing_factor
            
            # Update phase with smooth wrapping
            wave["phase"] = (wave["phase"] + wave["freq"] * 0.08) % (2 * math.pi)
            
            # Add this wave component
            total_wave += np.sin(wave["phase"]) * wave["amp"]
        
        # Normalize the combined wave
        total_wave /= len(self.waves)
        
        # State-based pattern selection
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
        elif abs(total_wave) < 0.05 and np.random.random() < 0.1:
            self.set_wave_pattern('playing')
        
        with self.wave_point_lock:
            self.wave_points.append(total_wave)
                

    # -------------------- Threads --------------------
        
    def update_visualiser(self):
        """Generate and update smoother sine wave points for the visualizer."""
        # Pre-allocate wave points array
        wave_buffer = np.zeros(self.visualizer_size)

        # Generate smoother sine wave points over the entire buffer
        phase_values = np.linspace(0, 2 * np.pi, self.visualizer_size) + self.phase
        wave_buffer = np.sin(phase_values) * self.amplitude

        with self.wave_point_lock:
            # Append newly generated points to the existing wave
            self.wave_points.extend(wave_buffer)
        
        for _ in range(self.visualizer_size * 2):
            self.change_visualizer_wave()

        while self.visualizer_thread_running:
            self.change_visualizer_wave()
            pygame.time.wait(settings.SPEED * 2)


    def handle_threads(self, tab_selected: bool):
        """Start or stop threads based on the current state."""
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
                
    # -------------------- Rendering --------------------


    def render_station_list(self):
        """Render the station list and highlight the selected station."""
        if not self.radio_station_surface or not self.selected_station_text:
            return

        # Create a view surface to render the visible area
        view_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - self.draw_space[0]),
            pygame.SRCALPHA)

        # Blit the full station list
        view_surface.blit(self.radio_station_surface, (0, 0))

        # Draw the highlight rectangle
        pygame.draw.rect(
            view_surface,
            settings.PIP_BOY_GREEN,
            self.selected_station_rect)

        # Blit the darker text for the selected station
        view_surface.blit(self.selected_station_text,(settings.RADIO_STATION_TEXT_MARGIN, self.selected_station_rect.y))
        
        # Blit the selection dot
        if self.active_station_index is not None and self.station_playing:
            dot = self.selected_station_dot_darker if self.active_station_index == self.selected_station_index else self.selected_station_dot
            view_surface.blit(dot, (settings.RADIO_STATION_TEXT_MARGIN - settings.RADIO_STATION_SELECTION_MARGIN, (self.active_station_index * self.font_height) + (self.font_height // 2) - (settings.RADIO_STATION_SELECTION_DOT_SIZE // 2)))


        # Blit the view surface onto the screen
        self.screen.blit(view_surface, (settings.TAB_SIDE_MARGIN, self.draw_space[0]))


    def render_visualiser_waves(self):
        """Render the visualiser waves."""
        with self.wave_point_lock:
            if len(self.wave_points) < 2:
                return
            # Convert to numpy array once
            points = np.array(self.wave_points)
            

        midpoint_y = self.vis_y + self.visualizer_size // 2
        
        # Calculate smooth curves using interpolation
        x_coords = self.vis_x + self.x_positions[:len(points)]
        y_coords = midpoint_y + points * (self.visualizer_size // 2)
        
        # Create point pairs for the main wave
        points = np.column_stack((x_coords, y_coords))
        
        
        # Draw main wave
        pygame.draw.lines(
            self.screen,
            settings.PIP_BOY_GREEN,
            False,
            points.astype(int),
            1
        )


    def render(self):
        """Render the radio tab."""
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))
        self.render_station_list()
        self.render_visualiser_waves()
