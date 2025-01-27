import configparser
import random
import pygame
import settings
import os
from tinytag import TinyTag
from threading import Thread
from typing import Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.radio_stations = {}
        self.amount_of_stations = 0
        self.selected_station_index = 0
        
        # Pre-calculate constants
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 14)
        self.font_height = self.main_font.get_height()
        self.screen_height_minus_draws = settings.SCREEN_HEIGHT - sum(self.draw_space)
        
        # Cache rendered text surfaces
        self.text_cache = {}
        
        # Minimal UI state
        self.radio_station_surface = None
        self.current_draw_params = None
        
        # Start loading in background with minimal priority
        thread = Thread(target=self.load_radio_stations, daemon=True)
        thread.start()

    @lru_cache(maxsize=32)
    def _render_text(self, text: str) -> pygame.Surface:
        """Cache rendered text surfaces to avoid repeated rendering."""
        return self.main_font.render(text, True, settings.PIP_BOY_GREEN)

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
        """Load stations with minimal memory and CPU usage."""
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
            except:
                return None

        # Use scandir for more efficient directory iteration
        with os.scandir(settings.RADIO_BASE_FOLDER) as entries:
            # Use a small thread pool to avoid overwhelming the Pi
            with ThreadPoolExecutor(max_workers=2) as executor:
                stations = executor.map(load_single_station, entries)
                self.radio_stations = {
                    name: data for result in stations 
                    if result and (name := result[0]) and (data := result[1])
                }

        self.amount_of_stations = len(self.radio_stations)
        self._prepare_radio_station_surface()

    def _prepare_radio_station_surface(self):
        """Pre-render station list with minimal surface operations."""
        if not self.radio_stations:
            return

        # Create surface in system memory
        height = self.font_height * self.amount_of_stations
        self.radio_station_surface = pygame.Surface(
            (settings.SCREEN_WIDTH, height),
            flags=pygame.SRCALPHA
        )
        
        # Render all station names at once
        for i, station_name in enumerate(self.radio_stations):
            text_surface = self._render_text(station_name)
            self.radio_station_surface.blit(
                text_surface,
                (0, i * self.font_height)
            )

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


    def update_station_list_surface(self):
        """Update station list surface with minimal operations."""
        if not self.radio_station_surface:
            return
        
        # Calculate vertical position
        y_pos = self.draw_space[0] - (self.font_height * self.selected_station_index)
        
        # Fast clipping calculation
        if y_pos < self.draw_space[0]:
            clip_y = self.draw_space[0] - y_pos
            height = min(
                self.radio_station_surface.get_height() - clip_y,
                self.screen_height_minus_draws
            )
            y_pos = self.draw_space[0]
        else:
            clip_y = 0
            height = min(
                self.radio_station_surface.get_height(),
                self.screen_height_minus_draws - (y_pos - self.draw_space[0])
            )
        
        # Store drawing parameters
        self.current_draw_params = (
            (settings.TAB_SIDE_MARGIN, y_pos),
            pygame.Rect(0, clip_y, settings.SCREEN_WIDTH, height)
        )

    def update(self):
        """Update the radio tab."""
        self.update_station_list_surface()


    def render_station_list(self):
        """Minimal station list rendering."""
        if self.radio_station_surface and self.current_draw_params:
            self.screen.blit(self.radio_station_surface, 
                           self.current_draw_params[0],
                           self.current_draw_params[1])

    def render(self):
        """Render the radio tab."""
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))
        self.render_station_list()

    def change_stations(self, direction: bool):
        """Fast station change."""
        new_index = self.selected_station_index + (1 if direction else -1)
        if 0 <= new_index < self.amount_of_stations:
            self.selected_station_index = new_index