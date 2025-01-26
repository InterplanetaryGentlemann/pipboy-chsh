import pygame
import settings


class Timer:
    def __init__(self):
        self.last_update_time = pygame.time.get_ticks()
        self.pause_states = {}

    def update(self, interval = 1):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_update_time > settings.SPEED * interval:
            self.last_update_time = current_time
            return True
        return False
    
    
    def reset(self):
        self.last_update_time = pygame.time.get_ticks()


    def check_and_pause(self, state, pause):
        if state not in self.pause_states:
            self.pause_states[state] = False
            self.reset()
            print(state)
        if not self.pause_states[state] and not self.update(pause):
            return False
        self.pause_states[state] = True
        return True