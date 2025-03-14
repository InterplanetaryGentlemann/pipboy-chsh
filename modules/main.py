
import os
import sys
import pygame
import pygame.freetype
import traceback
import settings
from pipboy import PipBoy
import threading
from input_manager import InputManager



def main():
    """Main entry point for the Pip-Boy application."""
    if settings.RASPI:
        os.environ["SDL_VIDEODRIVER"] = "x11"
        os.environ["DISPLAY"] = ":0"
        os.environ["SDL_AUDIODRIVER"] = "alsa"

        
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=5)

    
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE, pygame.DOUBLEBUF, pygame.FULLSCREEN if settings.RASPI else False)
    pygame.mouse.set_visible(True)
    
    pygame.display.set_caption("Pip-Boy")
    clock = pygame.time.Clock()
    
    input_manager = InputManager()

    pipboy = PipBoy(screen, clock, input_manager)
    pipboy_thread = threading.Thread(target=pipboy.run)
    pipboy_thread.daemon = True
    pipboy_thread.start()
    pipboy_thread_lock = threading.Lock()
    
    

    running = True
    while running:
        
        input_manager.run()
        
        with pipboy_thread_lock:
            pipboy.render()
        clock.tick(settings.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()