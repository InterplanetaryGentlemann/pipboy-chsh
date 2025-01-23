import pygame
import os
import settings
import queue
import time

class Overlays:
    def __init__(self, render_queue):
        self.render_queue = render_queue  # Store the queue for later use

        self.overlays = []
        self.current_crt_image = 0
        self.overlay_image = pygame.image.load(settings.CRT_OVERLAY).convert_alpha()
        self.overlay_image.set_alpha(80)
        self.scanline_image = pygame.image.load(settings.SCANLINE_OVERLAY).convert_alpha()
        self.scanline_image.set_alpha(10)
        self.scanline_y = -self.scanline_image.get_height()

        self.crt_overlay = [
            pygame.image.load(os.path.join(settings.CRT_STATIC, filename)).convert_alpha()
            for filename in os.listdir(settings.CRT_STATIC) if filename.endswith(".png")
        ]

    def crt_effect(self):
        """CRT effect using the queue"""
        while True:
            # Push the overlay image to the queue
            self.render_queue.put((self.overlay_image, (0, 0), 80))

            # Push the current CRT overlay image to the queue with blending mode
            self.render_queue.put((self.crt_overlay[self.current_crt_image], (0, 0), 80))
            self.current_crt_image = (self.current_crt_image + 1) % len(self.crt_overlay)

            # Push the scanline image to the queue
            self.render_queue.put((self.scanline_image, (0, self.scanline_y), 10))
            self.scanline_y = (self.scanline_y + 4) % settings.SCREEN_HEIGHT
            time.sleep(settings.FPS / 1000)  # Sleep for a while to control the speed


