import os
import pygame
import settings
from threading import Thread
from ui import GenericList, AnimatedImage




class SpecialTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.special_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 12)
        self.description_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 9)
        
        list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top + 2 * settings.LIST_TOP_MARGIN,
            self.draw_space.centerx - 2 * settings.TAB_SIDE_MARGIN,
            self.draw_space.height - 2 * settings.LIST_TOP_MARGIN
        )

        
        self.special_list = GenericList(
            stats=settings.DEFAULT_SPECIAL_STATS,
            draw_space=list_draw_space,
            items=[settings.SPECIAL[i] for i in range(len(settings.SPECIAL))],
            font=self.special_font
        )
        
        self.selected_special_index = 0
        self.previous_special_index = 0
        
        self.special_text = self._init_special_text()
        
        self.special_images, self.frame_orders = self._init_images()
        
        
        self.animated_images = {}
        for special in settings.SPECIAL:
            image_width = self.special_images[special][0].get_width()

            self.animated_images[special] = AnimatedImage(
                self.screen,
                self.special_images[special],
                (self.draw_space.centerx + self.draw_space.width // 4 - image_width // 2,
                 self.draw_space.top + settings.LIST_TOP_MARGIN),
                settings.SPEED * 200,
                self.frame_orders[special],
                loop=True
            )
            # self.animated_images[special].start()
        
     
     
    def start(self):
        """Start the animation thread."""
        self.animated_images[settings.SPECIAL[self.selected_special_index]].start()
    
    def stop(self):
        """Stop the animation thread."""
        self.animated_images[settings.SPECIAL[self.selected_special_index]].stop()    
        
    
    def scroll_special(self, direction: bool):
        """Scroll through specials and restart animation if needed."""
        new_index = self.special_list.change_selection(direction)
        if new_index != self.previous_special_index:
            # Stop previous animation to avoid wasted threads
            self.animated_images[settings.SPECIAL[self.previous_special_index]].stop()

            # Restart the selected animation
            self.selected_special_index = new_index
            self.animated_images[settings.SPECIAL[self.selected_special_index]].reset()
            self.animated_images[settings.SPECIAL[self.selected_special_index]].start()

            self.previous_special_index = new_index
            
    
    def _init_special_text(self):
        
        special_discriptions = {}
        
        for description in settings.SPECIAL_DESCRIPTIONS:
            
            text = self.description_font.render(description, True, settings.PIP_BOY_LIGHT, wraplength=self.draw_space.centerx)
            surface = pygame.surface.Surface((self.draw_space.centerx, text.get_height()))
            surface.blit(text, (0, 0))
            
            special_discriptions[description.split(" ")[0]] = surface
            
        return special_discriptions
            
    
    def _init_images(self):
        special_images = {}
        frame_orders = {}
        for i, special in enumerate(settings.SPECIAL):
            
            path = f"{settings.SPECIAL_BASE_FOLDER}/{special}"
            

            images = []
            for file in os.listdir(path):
                if file.endswith(".png"):
                    images.append(self.tab_instance.scale_image(
                        self.tab_instance._tint_image(
                            pygame.image.load(os.path.join(path, file)).convert_alpha()
                        ),
                        settings.SPECIAL_IMAGE_SCALE
                    ))
                    
            if os.path.exists(os.path.join(path, "frameorder.ini")):
                with open(os.path.join(path, "frameorder.ini"), "r") as f:
                    frame_orders[settings.SPECIAL[i]] = [int(frame) for frame in (f.read().split(","))]
            else:
                frame_orders[settings.SPECIAL[i]] = list(range(0, len(images)))
                
            special_images[settings.SPECIAL[i]] = images
            

        return special_images, frame_orders
    
    

    def _render_special_images(self, selected_special):
        """Render animation safely."""
        self.animated_images[selected_special].render()
        
        
    def _render_special_text(self, selected_special):
 
        self.screen.blit(
            self.special_text[selected_special],
            (self.draw_space.centerx, self.draw_space.centery + (self.draw_space.centery // 4))
        )
        

        
    def render(self):
        """Render the entire tab UI."""
        if not self.special_images or not self.special_list or not self.special_text:
            return

        selected_special = settings.SPECIAL[self.selected_special_index]
        self.special_list.render(self.screen, selected_special)
        self._render_special_images(selected_special)
        self._render_special_text(selected_special)