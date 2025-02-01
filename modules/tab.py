import datetime
import pygame
import settings

class Tab:
    def __init__(self, screen):
            self.footer_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 13)
            self.screen = screen
            
            now = datetime.datetime.now()
            self.current_date = now.strftime("%d.%m.")
            self.current_year = str(int(now.strftime("%Y")) + 263)


    def render_footer(self, margins):
        
        for i in range(len(margins)):
            pygame.draw.rect(self.screen, settings.PIP_BOY_DARKER, (margins[i][0], settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT, margins[i][1], settings.BOTTOM_BAR_HEIGHT))


    def play_sfx(self, sound_file, volume=settings.VOLUME, start=0):
        """
        Play a sound file.
        """
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            sound.play(start)