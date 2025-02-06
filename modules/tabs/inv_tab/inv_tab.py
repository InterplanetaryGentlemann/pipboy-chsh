import pygame
import settings
from .weapons_tab import WeaponsTab


class InvTab:
    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        
        self.current_sub_tab_index = 0  # 0-Weapons, 1-Apparel, 2-Aid, 3-Misc, 4-Junk, 5-Mods, 6-Ammo#
        
        self.footer_font = tab_instance.footer_font
        
        self.weapons_tab = WeaponsTab(self.screen, self.tab_instance, self.draw_space)
        # self.apparel_tab = ApparelTab(self.screen, self.tab_instance, self.draw_space)
        # self.aid_tab = AidTab(self.screen, self.tab_instance, self.draw_space)
        # self.misc_tab = MiscTab(self.screen, self.tab_instance, self.draw_space)
        # self.junk_tab = JunkTab(self.screen, self.tab_instance, self.draw_space)
        # self.mods_tab = ModsTab(self.screen, self.tab_instance, self.draw_space)
        # self.ammo_tab = AmmoTab(self.screen, self.tab_instance, self.draw_space)


    def change_sub_tab(self, sub_tab: int):
        self.current_sub_tab_index = sub_tab


    def scroll(self, direction: bool):
        match self.current_sub_tab_index:
            case 0: # Weapons
                self.weapons_tab.scroll(direction)
            case 1: # Apparel
                pass
            case 2: # Aid
                pass
            case 3: # Misc
                pass
            case 4: # Junk
                pass
            case 5: # Mods
                pass
            case 6: # Ammo
                pass
            case _: # DEFAULT
                pass


    def select_item(self):
        match self.current_sub_tab_index:
            case 0: # Weapons
                self.weapons_tab.select_item()
            case 1: # Apparel
                pass
            case 2: # Aid
                pass
            case 3: # Misc
                pass
            case 4: # Junk
                pass
            case 5: # Mods
                pass
            case 6: # Ammo
                pass
            case _: # DEFAULT
                pass


    def handle_threads(self, tab_selected: bool):
        if tab_selected:
            self.weapons_tab.start()
        else:
            self.weapons_tab.stop()


    def render(self):
        match self.current_sub_tab_index:
            case 0: # Weapons
                self.weapons_tab.render()
            case 1: # Apparel
                pass
            case 2: # Aid
                pass
            case 3: # Misc
                pass
            case 4: # Junk
                pass
            case 5: # Mods
                pass
            case 6: # Ammo
                pass
            case _: # DEFAULT
                pass
        
