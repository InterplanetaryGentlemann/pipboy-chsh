import pygame
from threading import Thread
import settings
import os

class StatTab:
    def __init__(self, screen, tab_instance, draw_space):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space

        
        self.dynamic_footer_text = [
            ("HP", settings.HP_CURRENT, settings.HP_MAX),
            ("LEVEL", settings.LEVEL),
            ("AP", settings.AP_CURRENT, settings.AP_MAX),
            ("XP", settings.XP_CURRENT)
        ]
        
        self.footer_font = tab_instance.footer_font
        self.tab_instance.init_footer(self, (settings.SCREEN_WIDTH // 4, settings.SCREEN_WIDTH // 2), self.init_footer_text())

    
    def init_footer_text(self): 
        hp_string = f"{self.dynamic_footer_text[0][0]} {self.dynamic_footer_text[0][1]}/{self.dynamic_footer_text[0][2]}"
        level_string = f"{self.dynamic_footer_text[1][0]} {self.dynamic_footer_text[1][1]}"
        ap_string = f"{self.dynamic_footer_text[2][0]} {self.dynamic_footer_text[2][1]}/{self.dynamic_footer_text[2][2]}"
        
        hp_surface = self.footer_font.render(hp_string, True, settings.PIP_BOY_GREEN)
        level_surface = self.footer_font.render(level_string, True, settings.PIP_BOY_GREEN)
        ap_surface = self.footer_font.render(ap_string, True, settings.PIP_BOY_GREEN)
        
        xp_rect_base = pygame.Rect(settings.SCREEN_WIDTH // 2.25, 6, settings.SCREEN_WIDTH // 3.5, settings.BOTTOM_BAR_HEIGHT - 12)
        xp_rect = xp_rect_base.copy()
        xp_rect.width = xp_rect.width * (settings.XP_CURRENT / 100)
        
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        footer_surface.blit(hp_surface, (2, 2))
        footer_surface.blit(level_surface, (settings.SCREEN_WIDTH // 3.8, 2))
        pygame.draw.rect(footer_surface, settings.PIP_BOY_GREEN, xp_rect)
        pygame.draw.rect(footer_surface, settings.PIP_BOY_GREEN, xp_rect_base, 1)
        footer_surface.blit(ap_surface, (settings.SCREEN_WIDTH // 1.2, 2))
        
        return footer_surface
    


    def render(self):
        self.tab_instance.render_footer(self)
        pass
