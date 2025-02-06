import datetime
import os
import pygame
import settings
from threading import Thread
from typing import Callable, Dict, Optional

class ThreadHandler:
    """
    A generic handler that manages a mapping between tab indices and their
    associated thread functions, as well as tracking the current and previous
    tab indices. When the tab index is updated, the previous index is stored
    internally, and you can start threads for both tabs accordingly.
    """
    def __init__(self, tab_map: Dict[int, Callable[[bool], None]], initial_tab_index: Optional[int] = None):
        """
        :param tab_map: A dictionary mapping tab indices to a callable
                        that takes a boolean flag.
        :param initial_tab_index: Optionally, set an initial current tab index.
        """
        self.tab_map = tab_map
        self.current_tab_index = initial_tab_index
        self.previous_tab_index = None
        
        self.handle_current_tab()

    def update_tab_index(self, new_index: int):
        """
        Update the current tab index. The old current index becomes the previous tab index.
        
        :param new_index: The new current tab index.
        """
        self.previous_tab_index = self.current_tab_index
        self.current_tab_index = new_index

        if self.current_tab_index != self.previous_tab_index:
            self.handle_current_tab()
            self.handle_previous_tab()        

    def _start_thread(self, tab_index: int, flag: bool) -> None:
        """
        Internal method to start a thread for the tab associated with tab_index.
        
        :param tab_index: The index of the tab.
        :param flag: The boolean flag to pass to the thread function.
        """

        tab = self.tab_map.get(tab_index)
        if tab:
            func = getattr(tab, f"handle_threads", None)  # Get the start or stop method dynamically
            if func and callable(func):
                Thread(target=func, args=(flag,)).start()            

    def handle_current_tab(self) -> None:
        """
        Starts a thread for the current tab with flag True.
        """
        if self.current_tab_index is not None:
            self._start_thread(self.current_tab_index, True)

    def handle_previous_tab(self) -> None:
        """
        Starts a thread for the previous tab with flag False.
        """
        if self.previous_tab_index is not None:
            self._start_thread(self.previous_tab_index, False)



class Tab:
    def __init__(self, screen):
            self.footer_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 12)
            self.screen = screen
            
            now = datetime.datetime.now()
            self.current_date = now.strftime("%d.%m.")
            self.current_year = str(int(now.strftime("%Y")) + 263)
            
            self.tab_footers = {}

    def init_footer(self, object, margins=None, text_surface=None):
        key = object
        
        # Create a new surface for the footer
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT))
        footer_surface.fill(settings.PIP_BOY_DARK)
        
        if margins is not None:
            line = 0
            for margin in margins:
                line += margin - settings.BOTTOM_BAR_VERTICAL_MARGINS // 2
                pygame.draw.line(
                    footer_surface,
                    settings.BACKGROUND,
                    (line, 0),
                    (line, settings.BOTTOM_BAR_HEIGHT),
                    settings.BOTTOM_BAR_VERTICAL_MARGINS  # Line width
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
        
    def _tint_image(self, image, color: tuple=settings.PIP_BOY_LIGHT):
        """Tint image with specified color while preserving alpha"""
        tinted = image.copy()
        # Multiply RGB channels with color, preserve original alpha
        tinted.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGB_MULT)
        return tinted       
        
    def scale_image(self, image, scale: float):
        return pygame.transform.smoothscale_by(
            image, 
            scale
        )
        
        
    # scale image absolute but keep aspect ratio
    def scale_image_abs(self, image, width: float = None, height: float = None):
        
        if width is None and height is None:
            return image
        
        if width is None:
            width = image.get_width() * (height / image.get_height())
        elif height is None:
            height = image.get_height() * (width / image.get_width())
        
        
        return pygame.transform.smoothscale(
            image, 
            (height, width)
        )



    def load_images(self, folder: str, tint: tuple=settings.PIP_BOY_LIGHT):
        try:
            images = [
                self._tint_image(
                    pygame.image.load(os.path.join(folder, f)).convert_alpha(),
                    tint
                ) for f in os.listdir(folder) if f.endswith(".png")
            ]
            return images
        except FileNotFoundError:
            return []
        
        
        
    def load_svg(self, scale: int, path: str, tint: tuple=settings.PIP_BOY_LIGHT):
        
        if path.endswith(".svg"):
            return self._tint_image(
                pygame.image.load_sized_svg(path, (scale, scale)).convert_alpha(),
                tint
            )


    def play_sfx(self, sound_file, volume=settings.VOLUME, start=0):
        """
        Play a sound file.
        """
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            sound.play(start)