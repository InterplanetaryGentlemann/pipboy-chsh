import configparser
import random
import numpy as np
import pygame
import settings
import os
from tinytag import TinyTag
from threading import Thread, Lock
from typing import Dict, Optional, List, Tuple
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache

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
        self.wave_points = []
        for point in range(settings.RADIO_WAVE_POINTS):
            if point % 2 == 0:
                self.wave_points.append(random.randint(settings.RADIO_WAVE_MIN, settings.RADIO_WAVE_MAX))
            else:
                self.wave_points.append(-self.wave_points[-1]) # Add negative of previous value
                
        self.wave_xy = [[]]
        self.wave_alternator = True
        
        self.wave_point_lock = Lock()
        
        self.visualizer_size = (settings.SCREEN_WIDTH  // 2) - (settings.TAB_SIDE_MARGIN * 2)
        
        self.visualizer_thread = None
        self.visualizer_thread_running = False
        
        self.waveform = []     
        
                

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


    # -------------------- Threads --------------------
        
    def update_visualiser(self):
        while self.visualizer_thread_running:
            if self.wave_alternator:
                # Generate a new random value
                new_point = random.randint(settings.RADIO_WAVE_MIN, settings.RADIO_WAVE_MAX)
            else:
                # Alternate with the negative of the previous value
                new_point = -self.wave_points[-1]
            
            self.wave_points.append(new_point)
            self.wave_alternator = not self.wave_alternator

            # Limit the length of the wave points
            max_length = random.randint(
                settings.RADIO_WAVE_POINTS,
                settings.RADIO_WAVE_POINTS + settings.RADIO_WAVE_VARIANCE
            )
            if len(self.wave_points) > max_length:
                self.wave_points.pop(0)
            
            with self.wave_point_lock:    
                self.wave_xy = []
                for i, point in enumerate(self.wave_points):
                    self.wave_xy.append(
                        (i * (self.visualizer_size // len(self.wave_points)) + settings.SCREEN_WIDTH // 2, 
                        settings.SCREEN_HEIGHT //2  - (point * settings.RADIO_WAVE_MAX))
                    )
                
            
            pygame.time.wait(settings.SPEED * 100)



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
        if not self.radio_stations or not self.wave_xy:
            return

        # xy = [[]]
        # for i in range(len(self.wave_points)):
        #     xy[i].append((self.visualizer_size // len(self.wave_points), self.wave_points[i]))
            
        # pygame.draw.lines(self.screen, settings.PIP_BOY_GREEN, False, self.wave_xy, 2)


    def render(self):
        """Render the radio tab."""
        self.tab_instance.render_footer(((0, settings.SCREEN_WIDTH),))
        self.render_station_list()
        self.render_visualiser_waves()

# class Animation(game.Entity):
#
#     def __init__(self):
#         super(Animation, self).__init__()
#
#         self.width, self.height = 250, 250
#         self.center = [self.width / 2, self.height / 2]
#         self.image = pygame.Surface((self.width, self.height))
#         self.animation_time = 0.04  # 25 fps
#         self.prev_time = 0
#         self.index = 0
#         self.prev_song = None
#
#     def render(self, *args, **kwargs):
#         global self.waveform
#         self.current_time = time.time()
#         self.delta_time = self.current_time - self.prev_time
#
#         if self.delta_time >= self.animation_time:
#             self.prev_time = self.current_time
#
#             if not song:
#                 self.image.fill((0, 0, 0))
#                 pygame.draw.line(self.image, [0, 255, 0], [0, self.height / 2], [self.width, self.height / 2], 2)
#
#             elif song:
#                 self.image.fill((0, 0, 0))
#                 self.index += 3
#
#                 if song != self.prev_song:
#                     self.prev_song = song
#
#                     if self.waveform:
#                         print("Loading cached self.waveform for", song, "Waveform length =", len(self.waveform))
#                     else:
#                         print("Generating self.waveform from", song, "Waveform length =", len(self.waveform))
#                         frame_skip = int(48000 / 75)
#                         amplitude = pygame.sndarray.array(pygame.mixer.Sound(song))  # Load the sound file)
#                         amplitude = amplitude[:, 0] + amplitude[:, 1]
#
#                         amplitude = amplitude[::frame_skip]
#
#                         # scale the amplitude to 1/4th of the frame height and translate it to height/2(central line)
#                         max_amplitude = max(amplitude)
#                         for i in range(len(amplitude)):
#                             amplitude[i] = float(amplitude[i]) / max_amplitude * int(
#                                 self.height / 2.5) + self.height / 2
#
#                         self.waveform = [int(self.height / 2)] * self.width + list(amplitude)
#                         for x in range(125):  # Add end frames
#                             self.waveform.append(125)
#
#                     # print("new start position = ",settings.START_POS)
#                     if not start_pos == 0:
#                         self.index = int(start_pos * 75)  # Adjust for new start position
#                     else:
#                         self.index = 5
#                     # print("New index=", self.index)
#                 length = len(self.waveform)
#                 if self.index >= length - 5:
#                     self.index = 0
#
#                 if length > 0:
#                     prev_x, prev_y = 0, self.waveform[self.index]
#                     for x, y in enumerate(self.waveform[self.index + 1:self.index + 1 + self.width][::1]):
#                         pygame.draw.line(self.image, [0, 255, 0], [prev_x, prev_y], [x, y], 2)
#                         prev_x, prev_y = x, y
#
#                 # Credit to https://github.com/prtx/Music-Visualizer-in-Python/blob/master/music_visualizer.py
#
#