import settings
import pygame
from threading import Lock


class Render:
    def __init__(self, screen):
        self.screen = screen
        self.queue = {}
        self.lock = Lock()

    def add_blit(self, source, dest, area=None, special_flags=0, clear=False):
        with self.lock:  # Lock the queue during modification
            if str(source) not in self.queue:
                self.queue[str(source)] = (source, dest, area, special_flags)
            else:
                self.queue[str(source)] = (source, dest, area, special_flags)
                        
            
    def render(self):
        self.screen.fill(settings.BACKGROUND)
        self.screen.blits([(source, dest, area, special_flags) for source, dest, area, special_flags in self.queue.values()])
        pygame.display.flip()
