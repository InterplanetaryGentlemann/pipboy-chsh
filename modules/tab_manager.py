import os
import settings
import pygame
import random
import math
from threading import Thread, Lock
from tabs.radio import RadioTab
from tab import Tab



class TabManager:
    def __init__(self, screen):
        self.screen = screen
        self.main_tab_font = pygame.font.Font(settings.MAIN_FONT_PATH, 15)
        self.tab_font_height = self.main_tab_font.get_height()
        self.tabs = settings.TABS
        self.current_tab_index = 0
        self.previous_tab_index = 0
        self.tab_x_offset = []
        self.glitch_thread = None
        self.render_blur = False
        self.switch_lock = Lock()

        self.tab_text_surface = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height))
        self.init_tab_text()
        
        self.draw_space = ((settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height + settings.TAB_BOTTOM_MARGIN), settings.BOTTOM_BAR_HEIGHT + settings.BOTTOM_BAR_MARGIN)
        
        self.tab_base = Tab(self.screen)
        self.radio_tab = RadioTab(self.screen, self.tab_base, self.draw_space)
        
        
    def play_sfx(self, sound_file, volume=settings.VOLUME):
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            sound.play(0)
            
    def switch_tab_sound(self):
        sound = random.choice(os.listdir(settings.TAB_SWITCH_SOUND))      
        self.play_sfx(os.path.join(settings.TAB_SWITCH_SOUND, sound), settings.VOLUME / 3)                
            
    def init_tab_text(self):
    
        total_tab_width = sum(self.main_tab_font.size(tab)[0] for tab in self.tabs)
        tab_spacing = (settings.SCREEN_WIDTH - total_tab_width - 2 * settings.TAB_MARGIN) // (len(self.tabs) + 1)
        self.tab_x_offset.append(settings.TAB_MARGIN + tab_spacing)
        
        for i, tab in enumerate(self.tabs):
            text_surface = self.main_tab_font.render(tab, True, settings.PIP_BOY_GREEN)
            self.tab_text_surface.blit(text_surface, (self.tab_x_offset[i], settings.TAB_VERTICAL_OFFSET))
            self.tab_x_offset.append((self.main_tab_font.size(tab)[0] + tab_spacing) + self.tab_x_offset[i])

    def tab_switch_glitch(self):
        for _ in range(20):
            time = pygame.time.get_ticks()

            jump_offset = int(20 * math.sin(time))

            self.screen.blit(self.screen, (0, -jump_offset))
            pygame.time.wait(settings.SPEED * 100)

                
    def tab_blur(self):
        screen_copy = self.screen.copy()
        for i in range(1, 18, 6):
            blur = pygame.transform.box_blur(screen_copy, i)
            blur.set_alpha(180)
            self.screen.blit(blur, (0, 0), special_flags=pygame.BLEND_ADD)        
  

    def handle_tab_threads(self):
        match self.current_tab_index:
            case 0: # STAT
                pass
            case 1: # INV
                pass
            case 2: # DATA
                pass
            case 3: # MAP
                pass
            case 4: # RADIO
                Thread(target=self.radio_tab.handle_threads, args=(True,)).start()
        match self.previous_tab_index:
            case 0: # STAT
                pass
            case 1: # INV
                pass
            case 2: # DATA
                pass
            case 3: # MAP
                pass
            case 4: # RADIO
                Thread(target=self.radio_tab.handle_threads, args=(False,)).start()
            case _:
                pass
            
                                    

    def switch_tab(self, direction):

        with self.switch_lock:
            # Switch tab index
            self.previous_tab_index = self.current_tab_index
            self.current_tab_index = max(0, min((self.current_tab_index + (1 if direction else -1)) % len(self.tabs), len(self.tabs) - 1))
        
        if random.randrange(100) < settings.GLITCH_MOVE_CHANCE and (self.glitch_thread == None or not self.glitch_thread.is_alive()):
            self.glitch_thread = Thread(target=self.tab_switch_glitch, args=())            
            self.glitch_thread.start()
        else:
            self.render_blur = True
        
        self.handle_tab_threads()
        self.switch_tab_sound()
            

    def scroll_tab(self, direction):
        match self.current_tab_index:
            case 0: # STAT
                pass
            case 1: # INV
                pass
            case 2: # DATA
                pass
            case 3: # MAP
                pass
            case 4: # RADIO
                self.radio_tab.change_stations(direction)
            case _:
                pass

    def select_item(self):
        match self.current_tab_index:
            case 0: # STAT
                pass
            case 1: # INV
                pass
            case 2: # DATA
                pass
            case 3: # MAP
                pass
            case 4: # RADIO
                self.radio_tab.select_station()
            case _:
                pass


    def render_header(self):
        """Draw the tabs on the screen."""
        # Draw the tab text surface
        self.screen.blit(self.tab_text_surface, (0, 0))
        
        # Draw the line below the tabs
        pygame.draw.line(self.screen, settings.PIP_BOY_GREEN, (0, self.tab_font_height), (settings.SCREEN_WIDTH, self.tab_font_height), 1)
        
        # Block line below the selected tab
        pygame.draw.line(
            self.screen, 
            settings.BACKGROUND, 
            ((self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET), self.tab_font_height), 
            ((self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH)), self.tab_font_height), 
            1)
        
        # Draw vertical lines next to the 2 sides of the selected tab
        pygame.draw.line(
            self.screen, 
            settings.PIP_BOY_GREEN, 
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET, self.tab_font_height), 
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), 
            1)
        pygame.draw.line(
            self.screen, 
            settings.PIP_BOY_GREEN, 
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH), self.tab_font_height), 
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH), self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        
        # Draw small horizontal lines next to the 2 vertical lines
        pygame.draw.line(
            self.screen,
            settings.PIP_BOY_GREEN,
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET + settings.TAB_SCREEN_EDGE_LENGTH, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        pygame.draw.line(
            self.screen,
            settings.PIP_BOY_GREEN,
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH), self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH) - settings.TAB_SCREEN_EDGE_LENGTH, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        
        # Draw vertical lines at screen edges
        pygame.draw.line(self.screen, settings.PIP_BOY_GREEN, (0, settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (0, self.tab_font_height), 1)
        pygame.draw.line(self.screen, settings.PIP_BOY_GREEN, (settings.SCREEN_WIDTH - 1,settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (settings.SCREEN_WIDTH - 1, self.tab_font_height ), 1)
        


    def render_tab(self):
        match self.current_tab_index:
            case 0: # STAT
                pass
            case 1: # INV
                pass
            case 2: # DATA
                pass
            case 3: # MAP
                pass
            case 4: # RADIO
                self.radio_tab.render()
            case _:
                pass
            

    # def update_tabs(self):
    #     match self.current_tab_index:
    #         case 0: # STAT
    #             pass
    #         case 1: # INV
    #             pass
    #         case 2: # DATA
    #             pass
    #         case 3: # MAP
    #             pass
    #         case 4: # RADIO
    #             self.radio_tab.update()
    #         case _:
    #             pass
                            


    def render(self):
        self.render_header()
        self.render_tab()
        
        if self.render_blur:
            self.tab_blur()
            self.render_blur = False