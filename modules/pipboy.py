import pygame
import os
import boot
import threading
import settings
import random
import math
import overlays
import queue


class PipBoy:
    def __init__(self, screen, clock):
        """
        Initialize the PipBoy object.
        """
        self.screen = screen
        self.clock = clock
        self.render_queue = queue.Queue()

        if settings.BOOT_SCREEN:
            self.boot_instance = boot.Boot()
            self.boot_thread = threading.Thread(target=self.boot_instance.boot_up_sequence, args=(self.screen, self.clock))
            self.boot_thread.daemon = True
            self.boot_thread.start()
            self.boot_thread.join()
            del self.boot_instance

        if settings.SHOW_CRT:
            self.overlay_instance = overlays.Overlays(self.render_queue)
            self.crt_thread = threading.Thread(target=self.overlay_instance.crt_effect)
            self.crt_thread.daemon = True
            self.crt_thread.start()



    def play_hum(self, sound, volume, loops):
        pygame.mixer.music.load(sound)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)


    def run(self):

        if settings.SOUND_ON:
            self.play_hum(settings.BACKGROUND_HUM, settings.VOLUME / 10, -1)

        # Main loop
        running = True
        tab_switch = False

        while running:
            while not self.render_queue.empty():
                item = self.render_queue.get()  # Get the blit instruction from the queue
                image = item[0]  # Get the image
                pos = item[1]
                try:
                    alpha = item[2]
                    image.set_alpha(alpha)  # Set alpha value
                except IndexError:
                    pass
                self.screen.blit(image, pos)  # Perform the blit



            pygame.display.flip()  # Update the display
            self.clock.tick(settings.FPS)  # Control the frame rate






