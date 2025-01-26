import sys
import pygame
import settings
from pipboy import PipBoy
import threading
from render import Render




def main():
    """Main entry point for the Pip-Boy application."""
    # Main application loop
    pygame.init()
    pygame.mixer.init(frequency=44100, size=-16, channels=1)


    screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE)
    print(screen)
    pygame.display.set_caption("Pip-Boy")
    clock = pygame.time.Clock()

    pipboy = PipBoy(screen, clock)
    pipboy_thread = threading.Thread(target=pipboy.run)
    pipboy_thread.daemon = True
    pipboy_thread.start()
    pipboy_thread_lock = threading.Lock()
    

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
        
        with pipboy_thread_lock:
            pipboy.render()
        clock.tick(settings.FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()