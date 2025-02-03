import pygame
import settings
from .status_tab import StatusTab

class StatTab:
    def __init__(self, screen, tab_instance, draw_space: tuple):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = pygame.Rect(0, draw_space[0], settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - draw_space[1] - draw_space[0])
        self.current_sub_tab = 0
        
        
        self.dynamic_footer_text = [
            ("HP", settings.HP_CURRENT, settings.HP_MAX),
            ("LEVEL", settings.LEVEL),
            ("AP", settings.AP_CURRENT, settings.AP_MAX),
            ("XP", settings.XP_CURRENT)
        ]
        
        self.footer_font = tab_instance.footer_font
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 2), self.init_footer_text())
        
        self.status_tab = StatusTab(self.screen, self.tab_instance, self.draw_space)

    
    def init_footer_text(self): 
        hp_string = f"{self.dynamic_footer_text[0][0]} {self.dynamic_footer_text[0][1]}/{self.dynamic_footer_text[0][2]}"
        level_string = f"{self.dynamic_footer_text[1][0]} {self.dynamic_footer_text[1][1]}"
        ap_string = f"{self.dynamic_footer_text[2][0]} {self.dynamic_footer_text[2][1]}/{self.dynamic_footer_text[2][2]}"
        
        hp_surface = self.footer_font.render(hp_string, True, settings.PIP_BOY_LIGHT)
        level_surface = self.footer_font.render(level_string, True, settings.PIP_BOY_LIGHT)
        ap_surface = self.footer_font.render(ap_string, True, settings.PIP_BOY_LIGHT)
        
        xp_rect_base = pygame.Rect(settings.SCREEN_WIDTH // 2.25, (settings.BOTTOM_BAR_HEIGHT // 2.5) // 2, settings.SCREEN_WIDTH // 3.5, settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 2.5))
        xp_rect = xp_rect_base.copy()
        xp_rect.width = xp_rect.width * (settings.XP_CURRENT / 100)
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        footer_surface.blit(hp_surface, (2, 2))
        footer_surface.blit(level_surface, (settings.SCREEN_WIDTH // 3.8, 2))
        pygame.draw.rect(footer_surface, settings.PIP_BOY_LIGHT, xp_rect)
        pygame.draw.rect(footer_surface, settings.PIP_BOY_MID, xp_rect_base, 1)
        footer_surface.blit(ap_surface, (settings.SCREEN_WIDTH // 1.2, 2))
        
        return footer_surface
    
    
    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab = sub_tab


    def handle_threads(self, tab_selected: bool):
        if tab_selected:
            self.status_tab.start()
        else:
            self.status_tab.stop()
        

    def render(self):
        self.tab_instance.render_footer(self)
        match self.current_sub_tab:
            case 0: # Status
                self.status_tab.render()
            case 1: # Special
                pass
            case 2: # Perks
                pass
            case _:
                pass
            
