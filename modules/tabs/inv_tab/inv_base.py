from threading import Thread, Lock
import pygame
import settings
from ui import GenericList, AnimatedImage
from items import Inventory
from util_functs import Utils
            
            
class InvBase:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect, category: str, enable_turntable: bool = True, enable_dot: bool = False):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.enable_turntable = enable_turntable
        
        self.inv_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 10)
        self.footer_font = tab_instance.footer_font               
        inventory = Inventory()
        self.inv_items = inventory.get_all_items(category)
        self.weight = sum(item.weight for item in inventory.get_all_items())
        self._init_icons()
        
        self.no_items = True if not self.inv_items else False
        if self.no_items:
            return
                
        self.item_selected = False
        self.active_item_index = None
        self.previous_item_index = None
        
        self.unique_items = inventory.get_unique_items(category)
        
        item_names = inventory.get_item_names(category)

           
        self.list_draw_space = pygame.Rect(
            self.draw_space.left,
            self.draw_space.top + 2 * settings.LIST_TOP_MARGIN,
            self.draw_space.centerx + (self.draw_space.centerx // 6),
            self.draw_space.height - 2 * settings.LIST_TOP_MARGIN
        )
        
        self.inv_list = GenericList(
            draw_space=self.list_draw_space,
            font=self.inv_font,
            items=item_names,
            enable_dot=enable_dot,
        )
        
        if self.enable_turntable:
            self._init_turntable()
        

    def _init_turntable(self):
        self.turntable_draw_space = pygame.Rect(
            self.list_draw_space.right + settings.TURNTABLE_LEFT_MARGIN,
            self.draw_space.top,
            self.draw_space.width - self.list_draw_space.width,
            self.list_draw_space.height // 2
        )
        
        self.turntable_lock = Lock
        self.item_turntable = None

    
    def _init_icons(self):
        self.big_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 4)
        self.small_icon_size = settings.BOTTOM_BAR_HEIGHT - (settings.BOTTOM_BAR_HEIGHT // 2)
        
        self.weight_icon = Utils.load_svg(self.big_icon_size, settings.WEIGHT_ICON)
        self.caps_icon = Utils.load_svg(self.big_icon_size, settings.CAPS_ICON)
        
        
        self.damage_icons = {
            dtype: Utils.load_svg(self.small_icon_size, path)
            for dtype, path in settings.DAMAGE_TYPES_ICONS.items()
        }        
        

    def select_item(self):    
        if self.no_items:
            return
        
        if self.inv_list.selected_index == self.active_item_index:
            self.item_selected = not self.item_selected
        else:
            self.item_selected = True  # Set to True for new selections
        self.active_item_index = self.inv_list.selected_index
        


    def scroll(self, direction: bool):
        if self.no_items:
            return
        prev_index = self.inv_list.change_selection(direction)

        if self.enable_turntable and self.inv_list.selected_index != prev_index:
            Thread(target=self.start_item_animation).start() 
        
    
    
    def init_footer_weight(self):
        
        weight_text= f"{self.weight}/{settings.MAX_CARRY_WEIGHT}"
        weight_surface = self.footer_font.render(weight_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        y_pos = settings.BOTTOM_BAR_HEIGHT // 2 - weight_surface.get_height() // 2
        
        footer_surface.blit(self.weight_icon, (y_pos, 3))
        
        footer_surface.blit(weight_surface, (self.weight_icon.get_width() + settings.BOTTOM_BAR_MARGIN, 2))

        return footer_surface

    
    def init_footer_caps(self):
        
        caps_text= f"{settings.CAPS}"
        caps_surface = self.footer_font.render(caps_text, True, settings.PIP_BOY_LIGHT)
        footer_surface = pygame.Surface((settings.SCREEN_WIDTH, settings.BOTTOM_BAR_HEIGHT), pygame.SRCALPHA).convert_alpha()
        
        y_pos = settings.BOTTOM_BAR_HEIGHT // 2 - caps_surface.get_height() // 2

        
        footer_surface.blit(self.caps_icon, (settings.SCREEN_WIDTH //4 + 4, y_pos))
        
        footer_surface.blit(caps_surface, (settings.SCREEN_WIDTH // 4 + self.caps_icon.get_width() + settings.BOTTOM_BAR_MARGIN, 2))

        return footer_surface

        
        

    def start_item_animation(self):
        
        if self.item_turntable:
            self.item_turntable.stop()
            self.item_turntable = None
        selected_item = self.unique_items[self.inv_list.selected_index]   
        if not selected_item.icons: 
            return  
        folder = f"{settings.ITEMS_BASE_FOLDER}/{selected_item.icons}"
        icons = Utils.load_images(folder) 
        if not icons:
            return
        
        icons = [Utils.scale_image_abs(image, height=self.turntable_draw_space.height) for image in icons]
     
        self.item_turntable = AnimatedImage(
            self.screen,
            icons,
            self.turntable_draw_space,
            settings.SPEED * 100
        )
        
        self.item_turntable.start()


    def handle_threads(self, tab_selected: bool):
        """ Handle the threads"""
        if self.no_items:
            return
        if tab_selected and self.enable_turntable:
            Thread(target=self.start_item_animation).start()
        elif not tab_selected and self.enable_turntable and self.item_turntable :
            self.item_turntable.stop()
            self.item_turntable = None
            
               
        
        
    def render(self):
        self.tab_instance.render_footer(self)
        if self.no_items:
            return
        self.inv_list.render(self.screen, self.active_item_index, self.item_selected)
        if self.enable_turntable and self.item_turntable:
            self.item_turntable.render()
            

