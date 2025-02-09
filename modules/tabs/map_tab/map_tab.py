import os
from threading import Thread, Lock
import pygame
import settings
from tab import ThreadHandler
from .world_tab import WorldMap, RealMap
from datetime import datetime
from util_functs import Utils






class MapTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.current_sub_tab_index = 0
        
        self.footer_font = tab_instance.footer_font
        self.date = Utils.get_date()
        self.time = Utils.get_time()
                
        self.tab_instance.init_footer(
            self, 
            (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 4), 
            self._init_footer_text()
        )
        
        # Initialize subtabs
        # self.world_map_subtab = WorldMap(self.screen, self.draw_space, settings.COMMONWEALTH_MAP)
        
        self.world_map_subtab = RealMap(self.screen, self.draw_space, api_zoom=settings.MAP_ZOOM)
 
        sub_tab_map = {
            0: self.world_map_subtab
        }
        
        self.footer_time_thread = Thread(target=self.update_footer_time, daemon=True)
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)
        
 
        self.datetime_lock = Lock
        self.footer_time_thread.start()



    def _blit_footer_time(self):
        time_surface = self.footer_font.render(self.time, True, settings.PIP_BOY_LIGHT)
        self.tab_instance.update_footer(self, time_surface,(settings.SCREEN_WIDTH // 4 + 4, 2))

        
        

    def _init_footer_text(self):
        """Create surface with map-related footer information"""
        
        date_surface = self.footer_font.render(self.date, True, settings.PIP_BOY_LIGHT)
        location_surface = self.footer_font.render(settings.LOCATION, True, settings.PIP_BOY_LIGHT)
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA)
        
        footer_surface.blit(date_surface, (2, 2))
        footer_surface.blit(location_surface, (settings.SCREEN_WIDTH - location_surface.width - 2, 2))
        
        
        return footer_surface

    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)

    def scroll(self, direction: bool):
        self.world_map_subtab.zoom(direction)

    def update_footer_time(self):
        while True:
            self.time = Utils.get_time()
            self._blit_footer_time()
            now = datetime.now()
            wait_time = 60 - now.second
            pygame.time.wait(wait_time * 1000)
            
    def navigate(self, direction: int):
        self.world_map_subtab.navigate(direction)

    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)


    def render(self):
        self.tab_instance.render_footer(self)
        match self.current_sub_tab_index:
            case 0:  # World Map
                self.world_map_subtab.render()