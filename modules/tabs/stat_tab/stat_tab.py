import pygame
import settings
from .status_tab import StatusTab
from .special_tab import SpecialTab
from tab import ThreadHandler

class StatTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.current_sub_tab_index = 0
        
        
        self.dynamic_footer_text = [
            ("HP", settings.HP_CURRENT, settings.HP_MAX),
            ("LEVEL", settings.LEVEL),
            ("AP", settings.AP_CURRENT, settings.AP_MAX),
            ("XP", settings.XP_CURRENT)
        ]
        
        self.footer_font = tab_instance.footer_font
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 2), self.init_footer_text())
        
        self.status_tab = StatusTab(self.screen, self.tab_instance, self.draw_space)
        self.special_tab = SpecialTab(self.screen, self.tab_instance, self.draw_space)
        
        
        sub_tab_map = {
            0: self.status_tab,
            1: self.special_tab
        }
        
        self.sub_tab_thread_handler = ThreadHandler(sub_tab_map, self.current_sub_tab_index)
        

    
    def init_footer_text(self): 
        hp_string = f"{self.dynamic_footer_text[0][0]} {self.dynamic_footer_text[0][1]}/{self.dynamic_footer_text[0][2]}"
        level_string = f"{self.dynamic_footer_text[1][0]} {self.dynamic_footer_text[1][1]}"
        ap_string = f"{self.dynamic_footer_text[2][0]} {self.dynamic_footer_text[2][1]}/{self.dynamic_footer_text[2][2]}"
        
        hp_surface = self.footer_font.render(hp_string, True, settings.PIP_BOY_LIGHT)
        level_surface = self.footer_font.render(level_string, True, settings.PIP_BOY_LIGHT)
        ap_surface = self.footer_font.render(ap_string, True, settings.PIP_BOY_LIGHT)
        
        xp_rect_base = pygame.Rect(level_surface.width + settings.SCREEN_WIDTH // 3.6, (settings.BOTTOM_BAR_HEIGHT // 1.7) // 2, settings.SCREEN_WIDTH // 3.2, settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 1.8))
        xp_rect = xp_rect_base.copy()
        xp_rect.width = xp_rect.width * (settings.XP_CURRENT / 100)
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        footer_surface.blit(hp_surface, (2, 2))
        footer_surface.blit(level_surface, (settings.SCREEN_WIDTH // 3.8, 2))
        pygame.draw.rect(footer_surface, settings.PIP_BOY_LIGHT, xp_rect)
        pygame.draw.rect(footer_surface, settings.PIP_BOY_DARKER, xp_rect_base, 1)
        footer_surface.blit(ap_surface, (settings.SCREEN_WIDTH // 1.2, 2))
        
        return footer_surface
    
    
    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)


    def scroll(self, direction: bool):
        match self.current_sub_tab_index:
            case 0: # STATUS
                pass
            case 1: # SPECIAL
                self.special_tab.scroll_special(direction)
            case 2: # PERKS
                pass
            case _: # DEFAULT
                pass


    def handle_threads(self, tab_selected: bool):
        self.sub_tab_thread_handler.update_tab_index(self.current_sub_tab_index)
    

        

    def render(self):
        self.tab_instance.render_footer(self)
        match self.current_sub_tab_index:
            case 0: # Status
                self.status_tab.render()
            case 1: # Special
                self.special_tab.render()
            case 2: # Perks
                pass
            case _:
                pass
            
