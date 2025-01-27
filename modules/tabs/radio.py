import configparser
import random
import pygame
from tab import Tab
import settings
import os
from tinytag import TinyTag
from threading import Thread, Lock
from typing import Dict, Optional
from dataclasses import dataclass
from concurrent.futures import ThreadPoolExecutor

@dataclass
class StationData:
    ordered: bool
    music_files: Dict[str, int]  # path -> duration_ms

class RadioTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.radio_stations: Dict[str, StationData] = {}
        self.amount_of_stations = 0
        self.selected_station_index = 0
        
        # UI elements
        self.main_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 14)
        self.font_height = self.main_font.get_height()
        self.radio_station_surface: Optional[pygame.Surface] = None
        self.station_clip_rect = pygame.Rect(0, self.draw_space[0], 
                                           settings.SCREEN_WIDTH, 
                                           settings.SCREEN_HEIGHT - sum(self.draw_space))
        
        # Start loading stations in background
        Thread(target=self.load_radio_stations, daemon=True).start()

    def load_music_files(self, station_folder: str) -> Dict[str, int]:
        """Load music files and their durations from a folder."""
        music_files = {}
        for f in os.listdir(station_folder):
            if f.endswith(".ogg"):
                path = os.path.join(station_folder, f)
                try:
                    duration = round(TinyTag.get(path).duration * 1000)
                    music_files[path] = duration
                except Exception:
                    continue  # Skip files that can't be read
        return music_files

    def load_radio_stations(self):
        """Load all radio stations in parallel using a thread pool."""
        def load_station(folder_name: str) -> Optional[tuple]:
            folder_path = os.path.join(settings.RADIO_BASE_FOLDER, folder_name)
            ini_path = os.path.join(folder_path, "station.ini")
            
            if not os.path.isdir(folder_path) or not os.path.exists(ini_path):
                return None
                
            config = configparser.ConfigParser()
            config.read(ini_path)
            
            music_files = self.load_music_files(folder_path)
            if not music_files:
                return None
                
            return (
                config.get("metadata", "station_name", fallback=folder_name),
                StationData(
                    ordered=config.getboolean("metadata", "ordered", fallback=False),
                    music_files=music_files
                )
            )

        # Use a thread pool to load stations in parallel
        with ThreadPoolExecutor() as executor:
            stations = executor.map(load_station, os.listdir(settings.RADIO_BASE_FOLDER))
            
            # Filter out None values and update stations dict
            self.radio_stations = {
                name: data for result in stations 
                if result and (name := result[0]) and (data := result[1])
            }
            
        self.amount_of_stations = len(self.radio_stations)
        self.prepare_radio_station_surface()

    def prepare_radio_station_surface(self):
        """Pre-render the radio station list surface."""
        if not self.radio_stations:
            return
            
        height = self.font_height * self.amount_of_stations
        self.radio_station_surface = pygame.Surface((settings.SCREEN_WIDTH, height))
        
        for i, station_name in enumerate(self.radio_stations):
            text = self.main_font.render(station_name, True, settings.PIP_BOY_GREEN)
            self.radio_station_surface.blit(text, (0, i * self.font_height))

    def generate_playlist(self) -> list:
        """Generate a playlist for the selected station."""
        if not self.radio_stations:
            return []
            
        station_name = list(self.radio_stations.keys())[self.selected_station_index]
        station = self.radio_stations[station_name]
        playlist = list(station.music_files.keys())
        
        if not station.ordered:
            random.shuffle(playlist)
            
        return playlist

    def update(self):
        """Update the visible portion of the radio station list."""
        if not self.radio_station_surface:
            return
            
        # Calculate vertical position based on selected station
        y_pos = self.draw_space[0] - (self.font_height * self.selected_station_index)
        surface_height = self.radio_station_surface.get_height()
        
        # Calculate clipping for partial visibility
        if y_pos < self.draw_space[0]:
            clip_start = self.draw_space[0] - y_pos
            height = min(surface_height - clip_start, 
                        settings.SCREEN_HEIGHT - self.draw_space[1] - self.draw_space[0])
            self.station_clip_rect = pygame.Rect(0, clip_start, 
                                               settings.SCREEN_WIDTH, height)
            y_pos = self.draw_space[0]
        else:
            height = min(surface_height, 
                        settings.SCREEN_HEIGHT - self.draw_space[1] - y_pos)
            self.station_clip_rect = pygame.Rect(0, 0, 
                                               settings.SCREEN_WIDTH, height)
            
        self.draw_pos = (settings.TAB_SIDE_MARGIN, y_pos)

    def render(self):
        """Render the radio station list and footer."""
        if self.radio_station_surface:
            self.screen.blit(self.radio_station_surface, 
                           self.draw_pos, 
                           self.station_clip_rect)
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))

    def change_stations(self, direction: bool):
        """Change the selected station (True for next, False for previous)."""
        new_index = self.selected_station_index + (1 if direction else -1)
        if 0 <= new_index < self.amount_of_stations:
            self.selected_station_index = new_index