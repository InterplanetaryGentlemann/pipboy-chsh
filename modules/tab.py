import datetime
import pygame
import settings

class Tab:
    def __init__(self, screen):
            self.footer_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 14)
            self.screen = screen
            
            now = datetime.datetime.now()
            self.current_date = now.strftime("%d.%m.")
            self.current_year = str(int(now.strftime("%Y")) + 263)
            
            self.tab_footers = {}

    def init_footer(self, object, margins=None, text_surface=None):
        key = object
        
        # Create a new surface for the footer
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT))
        footer_surface.fill(settings.PIP_BOY_DARKER)
        
        if margins is not None:
            line = 0
            for margin in margins:
                line += margin - settings.TAB_BOTTOM_VERTICAL_MARGINS // 2
                pygame.draw.line(
                    footer_surface,
                    settings.BACKGROUND,
                    (line, 0),
                    (line, settings.BOTTOM_BAR_HEIGHT),
                    settings.TAB_BOTTOM_VERTICAL_MARGINS  # Line width
                )
                
        if text_surface is not None:
            footer_surface.blit(
                text_surface,
                (0, 0)
            )
            
            
        # Store the surface in the dictionary
        self.tab_footers[key] = footer_surface
        
    def render_footer(self, object):
        # Blit the pre-rendered footer to the screen
        self.screen.blit(
            self.tab_footers[object],
            (0, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT)
        )
        
        
        



    def play_sfx(self, sound_file, volume=settings.VOLUME, start=0):
        """
        Play a sound file.
        """
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            sound.play(start)