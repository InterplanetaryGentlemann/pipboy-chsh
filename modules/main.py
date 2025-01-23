import sys
import pygame
import settings
from pipboy import PipBoy
import threading

pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

screen = pygame.display.set_mode((settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Pip-Boy")
clock = pygame.time.Clock()


def main():
    """Main entry point for the Pip-Boy application."""
    # Main application loop
    running = True

    pipboy_instance = PipBoy(screen, clock)
    pipboy_thread = threading.Thread(target=pipboy_instance.run)
    pipboy_thread.daemon = True
    pipboy_thread.start()


    while running:

        # pipboy_instance.run()
        # pygame.display.flip()
        # clock.tick(settings.FPS)

        # Handle global quit events
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False



    # Cleanup
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()