#!/home/pi/pipboy/pipboy-pi/pipboy-venv/bin/python

import os
import sys
import pygame
import settings
from pipboy import PipBoy
import threading
from input_manager import InputManager




def main():
    """Main entry point for the Pip-Boy application."""
    # Main application loop
    if settings.RASPI:
        os.environ["SDL_VIDEODRIVER"] = "kmsdrm"
        os.environ["SDL_VIDEO_KMSDRM_MODE"] = "320x240"
        os.environ["SDL_VIDEO_KMSDRM_REFRESH"] = "30"
        os.environ["SDL_VIDEO_KMSDRM_VSYNC"] = "0" 

        
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=5)

    pygame.mouse.set_visible(False)

    
    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.FULLSCREEN if settings.FULLSCREEN else 0)
    modes = pygame.display.list_modes()
    print(f"Available modes: {modes}") 
    print(pygame.display.Info())
    
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