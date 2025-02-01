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
        # Performance optimization: Pre-calculate constants and reduce object creation
        self.SCREEN_HALF_WIDTH = settings.SCREEN_WIDTH // 2
        self.VISUALIZER_SIZE = self.SCREEN_HALF_WIDTH - (settings.TAB_SIDE_MARGIN * 2) - settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET
        self.WAVE_POINTS_LENGTH = 128  # Reduced from 256 for better performance
        
        # Use numpy arrays instead of deque for better performance
        self.wave_points = np.zeros(self.WAVE_POINTS_LENGTH)
        self.wave_point_lock = Lock()
        
        # Pre-calculate x positions and store as integer array
        self.x_positions = np.linspace(0, self.VISUALIZER_SIZE, self.WAVE_POINTS_LENGTH).astype(np.int32)
        
        # Optimize wave parameters using numpy arrays for vectorized operations
        self.waves = np.array([
            # freq, amp, phase, target_freq, target_amp
            [1.0, 0.5, 0.0, 1.0, 0.5],
            [2.0, 0.3, 0.0, 2.0, 0.3],
            [3.0, 0.2, 0.0, 3.0, 0.2]
        ])
        
        # Cache frequently used values
        self.smoothing_factor = 0.05
        self.vis_x = self.SCREEN_HALF_WIDTH + (settings.RADIO_WAVE_VISUALIZER_SIZE_OFFSET // 2)
        self.vis_y = self.draw_space[0]
        self.midpoint_y = self.vis_y + self.VISUALIZER_SIZE // 2
        
        # Wave patterns as numpy arrays for faster access
        self.wave_patterns = {
            'idle': np.array([[0.2, 0.8], [0.05, 0.2]]),
            'playing': np.array([[1.0, 4.0], [0.4, 1.5]]),
            'changing': np.array([[2.0, 6.0], [0.1, 0.6]])
        }
        
        # Thread control
        self.visualizer_thread_running = False
        self.visualizer_thread = None
        
        # State tracking
        self.change_station_wave_counter = 0
        
        # Pre-allocate surface for double buffering
        self.wave_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.SRCALPHA)
        
                

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
        """Set wave parameters using vectorized operations."""
        pattern = self.wave_patterns[pattern_name]
        random_values = np.random.uniform(
            pattern[:, 0],
            pattern[:, 1],
            size=(len(self.waves), 2)
        )
        self.waves[:, 3] = random_values[:, 0]  # target_freq
        self.waves[:, 4] = random_values[:, 1]  # target_amp
    
    def change_visualizer_wave(self):
        """Generate complex waveform using vectorized operations."""
        # Vectorized parameter transitions
        self.waves[:, 0:2] += (self.waves[:, 3:5] - self.waves[:, 0:2]) * self.smoothing_factor
        
        # Update phases
        self.waves[:, 2] = (self.waves[:, 2] + self.waves[:, 0] * 0.08) % (2 * np.pi)
        
        # Calculate total wave using vectorized operations
        total_wave = np.sum(np.sin(self.waves[:, 2]) * self.waves[:, 1]) / len(self.waves)
        
        # State-based pattern selection with optimized conditions
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
            # Roll the array instead of using deque
            self.wave_points = np.roll(self.wave_points, -1)
            self.wave_points[-1] = total_wave

                

    # -------------------- Threads --------------------
        
    def update_visualiser(self):
        """Optimized visualizer update loop."""
        while self.visualizer_thread_running:
            self.change_visualizer_wave()
            pygame.time.wait(settings.SPEED * 3)  # Ensure minimum delay of 1ms


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


    def render_visualizer_waves(self):
        """Render the visualiser waves."""
        with self.wave_point_lock:
            points = self.wave_points.copy()
        
        # Clear the wave surface
        self.wave_surface.fill((0, 0, 0, 0))
        
        # Calculate coordinates using vectorized operations
        x_coords = self.vis_x + self.x_positions
        y_coords = self.midpoint_y + (points * (self.VISUALIZER_SIZE // 2)).astype(np.int32)
        
        # Create points array efficiently
        points_array = np.column_stack((x_coords, y_coords))
        
        # Draw the wave
        pygame.draw.lines(
            self.wave_surface,
            settings.PIP_BOY_GREEN,
            False,
            points_array,
            1
        )
        
        # Blit the wave surface to the main screen
        self.screen.blit(self.wave_surface, (0, 0))


    def render(self):
        """Render the radio tab."""
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))
        self.render_station_list()
        self.render_visualizer_waves()
