import os
import settings
import pygame
import random
import math
from threading import Thread, Lock
from tabs.radio_tab.radio_tab import RadioTab
from tabs.stat_tab.stat_tab import StatTab
from tabs.inv_tab.inv_tab import InvTab
from tabs.data_tab.data_tab import DataTab
from tab import Tab, ThreadHandler

class TabManager:
    def __init__(self, screen):
        self.screen = screen
        self.main_tab_font = pygame.font.Font(settings.MAIN_FONT_PATH, 14)
        self.tab_font_height = self.main_tab_font.get_height()
        self.tabs = settings.TABS
        self.current_tab_index = 0
        self.previous_tab_index = None
        
        self.current_sub_tab_index = [0] * len(self.tabs)
        self.previous_sub_tab_index = [0] * len(self.tabs)

        self.tab_x_offset = []
        self.glitch_thread = None
        self.render_blur = False
        self.switch_lock = Lock()

        self.tab_text_surface = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height))
        self.init_tab_text()
        
        draw_space = ((settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height * 2 + settings.TAB_BOTTOM_MARGIN),
                      settings.BOTTOM_BAR_HEIGHT + settings.BOTTOM_BAR_MARGIN)
        self.draw_space = pygame.Rect(0, draw_space[0], settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT - draw_space[1] - draw_space[0])
        
        self.tab_base = Tab(self.screen)
        self.radio_tab = RadioTab(self.screen, self.tab_base, self.draw_space)
        self.stat_tab = StatTab(self.screen, self.tab_base, self.draw_space)
        self.inv_tab = InvTab(self.screen, self.tab_base, self.draw_space)
        self.data_tab = DataTab(self.screen, self.tab_base, self.draw_space)
        
        tab_map = {
            0: self.stat_tab,
            1: self.inv_tab,
            2: self.data_tab,
            4: self.radio_tab,
        }

        self.subtab_surfaces = {}  # Pre-rendered text surfaces for all states
        self.subtab_total_widths = {}  # Pre-calculated total width for each tab's subtabs
        self.subtab_offsets = {}  # Pre-calculated positioning data
        self.init_subtab_data()
        
        self.tab_thread_handler = ThreadHandler(tab_map, self.current_tab_index)
                
    def play_sfx(self, sound_file: str, volume=settings.VOLUME):
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            sound.play(0)
            
    def switch_tab_sound(self):
        if settings.SOUND_ON:
            if self.current_tab_index > self.previous_tab_index:
                self.play_sfx(os.path.join(settings.ROTARY_VERTICAL_1), settings.VOLUME / 5)
            else:
                self.play_sfx(os.path.join(settings.ROTARY_VERTICAL_2), settings.VOLUME / 5)
            if random.randrange(100) < settings.SWITCH_SOUND_CHANCE:
                sound = random.choice(os.listdir(settings.BUZZ_SOUND_BASE_FOLDER))      
                self.play_sfx(os.path.join(settings.BUZZ_SOUND_BASE_FOLDER, sound), settings.VOLUME / 3)       
                
    def switch_sub_tab_sound(self):
        if settings.SOUND_ON:
            if self.current_sub_tab_index > self.previous_sub_tab_index:
                self.play_sfx(os.path.join(settings.ROTARY_HORIZONTAL_1), settings.VOLUME / 5)
            else:
                self.play_sfx(os.path.join(settings.ROTARY_HORIZONTAL_2), settings.VOLUME / 5)

    def init_subtab_data(self):
        """Pre-render all possible subtab states and calculate positioning data"""
        for tab_name, subtabs in settings.SUBTABS.items():
            # Store surfaces for both active and inactive states
            self.subtab_surfaces[tab_name] = []
            total_width = 0
            width_list = []
            
            for subtab in subtabs:
                # Pre-render both color states
                active_surf = self.main_tab_font.render(subtab, True, settings.PIP_BOY_LIGHT)
                inactive_surf = self.main_tab_font.render(subtab, True, settings.PIP_BOY_DARK)
                width = active_surf.get_width()
                
                self.subtab_surfaces[tab_name].append((active_surf, inactive_surf))
                width_list.append(width)
                total_width += width + settings.SUBTAB_SPACING
            
            # Store total width (minus last spacing)
            self.subtab_total_widths[tab_name] = total_width - settings.SUBTAB_SPACING
            
            # Pre-calculate all possible offset positions for centering
            self.subtab_offsets[tab_name] = []
            cumulative_width = 0
            
            for i, width in enumerate(width_list):
                # Calculate offset needed to center this subtab under main tab
                main_tab_center = self.tab_x_offset[self.tabs.index(tab_name)] + \
                                self.main_tab_font.size(tab_name)[0] / 2
                subtab_center = cumulative_width + (width / 2)
                required_offset = main_tab_center - subtab_center
                
                self.subtab_offsets[tab_name].append(required_offset)
                cumulative_width += width + settings.SUBTAB_SPACING
                
    def init_tab_text(self):
        total_tab_width = sum(self.main_tab_font.size(tab)[0] for tab in self.tabs)
        tab_spacing = (settings.SCREEN_WIDTH - total_tab_width - 2 * settings.TAB_MARGIN) // (len(self.tabs) + 1)
        self.tab_x_offset.append(settings.TAB_MARGIN + tab_spacing)
        
        for i, tab in enumerate(self.tabs):
            text_surface = self.main_tab_font.render(tab, True, settings.PIP_BOY_LIGHT)
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
  
    def switch_tab(self, direction: bool):
        with self.switch_lock:
            # Switch tab index
            self.previous_tab_index = self.current_tab_index
            self.current_tab_index = max(0, min((self.current_tab_index + (1 if direction else -1)) % len(self.tabs), len(self.tabs) - 1))
        
        if random.randrange(100) < settings.GLITCH_MOVE_CHANCE and (self.glitch_thread == None or not self.glitch_thread.is_alive()):
            self.glitch_thread = Thread(target=self.tab_switch_glitch, args=())            
            self.glitch_thread.start()
        else:
            self.render_blur = True
        
        self.tab_thread_handler.update_tab_index(self.current_tab_index)
        self.switch_tab_sound()

    def switch_sub_tab(self, direction: bool):
        current_main_index = self.current_tab_index
        current_sub_index = self.current_sub_tab_index[current_main_index]
        subtabs = settings.SUBTABS.get(self.tabs[current_main_index], [])
        
        if not subtabs:
            return
        
        new_index = current_sub_index + (1 if direction else -1)
        new_index = max(0, min(new_index, len(subtabs) - 1))
        self.current_sub_tab_index[current_main_index] = new_index
        
        if new_index != current_sub_index:
            self.switch_sub_tab_sound()
            match self.current_tab_index:
                case 0: # STAT
                    self.stat_tab.change_sub_tab(new_index)
                case 1: # INV
                    self.inv_tab.change_sub_tab(new_index)
                case 2: # DATA
                    self.data_tab.change_sub_tab(new_index)
                case 3: # MAP
                    pass
                case 4: # RADIO
                    pass
                case _:
                    pass
                
    def scroll_tab(self, direction: bool):
        match self.current_tab_index:
            case 0: # STAT
                self.stat_tab.scroll(direction)
            case 1: # INV
                self.inv_tab.scroll(direction)
            case 2: # DATA
                self.data_tab.scroll(direction)
            case 3: # MAP
                pass
            case 4: # RADIO
                self.radio_tab.scroll(direction)
            case _:
                pass

    def select_item(self):
        match self.current_tab_index:
            case 0: # STAT
                pass
            case 1: # INV
                self.inv_tab.select_item()
            case 2: # DATA
                self.data_tab.select_item()
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
        pygame.draw.line(self.screen, settings.PIP_BOY_LIGHT, (0, self.tab_font_height), (settings.SCREEN_WIDTH, self.tab_font_height), 1)
        
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
            settings.PIP_BOY_LIGHT, 
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET, self.tab_font_height), 
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET), 
            1)
        pygame.draw.line(
            self.screen, 
            settings.PIP_BOY_LIGHT, 
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH), self.tab_font_height), 
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH), self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        
        # Draw small horizontal lines next to the 2 vertical lines
        pygame.draw.line(
            self.screen,
            settings.PIP_BOY_LIGHT,
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            (self.tab_x_offset[self.current_tab_index] - settings.TAB_HORIZONTAL_LINE_OFFSET + settings.TAB_SCREEN_EDGE_LENGTH, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        pygame.draw.line(
            self.screen,
            settings.PIP_BOY_LIGHT,
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH), self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LENGTH) - settings.TAB_SCREEN_EDGE_LENGTH, self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        
        # Draw vertical lines at screen edges
        pygame.draw.line(self.screen, settings.PIP_BOY_LIGHT, (0, settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (0, self.tab_font_height), 1)
        pygame.draw.line(self.screen, settings.PIP_BOY_LIGHT, (settings.SCREEN_WIDTH - 1, settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (settings.SCREEN_WIDTH - 1, self.tab_font_height), 1)
        
    def render_sub_tabs(self):
        current_tab_name = self.tabs[self.current_tab_index]
        subtabs = settings.SUBTABS.get(current_tab_name, [])
        current_sub_index = self.current_sub_tab_index[self.current_tab_index]
        
        if not subtabs or current_sub_index >= len(subtabs):
            return

        # Get pre-calculated values
        surfaces = self.subtab_surfaces[current_tab_name]
        start_x = self.subtab_offsets[current_tab_name][current_sub_index]
        y_pos = self.tab_font_height + settings.TAB_SCREEN_EDGE_LENGTH + settings.SUBTAB_VERTICAL_OFFSET
        
        # Calculate render boundaries
        screen_width = settings.SCREEN_WIDTH
        
        # Only draw visible portions
        current_x = start_x
        for i, (active_surf, inactive_surf) in enumerate(surfaces):
            width = active_surf.get_width()
            
            # Only draw if visible (simple culling)
            if current_x + width > 0 and current_x < screen_width:
                surface = active_surf if i == current_sub_index else inactive_surf
                self.screen.blit(surface, (current_x, y_pos))
            
            current_x += width + settings.SUBTAB_SPACING

    def render_tab(self):
        match self.current_tab_index:
            case 0: # STAT
                self.stat_tab.render()
            case 1: # INV
                self.inv_tab.render()
            case 2: # DATA
                self.data_tab.render()
            case 3: # MAP
                pass
            case 4: # RADIO
                self.radio_tab.render()
            case _:
                pass
                           
    def crt_glitch_effect(self):
        """
        Applies a quick CRT glitch effect to the current screen by randomly shifting horizontal slices 
        and overlaying some noise. This effect is meant to be occasional and subtle.
        """
        # Make a copy of the current screen
        glitch_surface = self.screen.copy()
        screen_rect = self.screen.get_rect()
        
        # Apply horizontal slice glitches
        for _ in range(random.randint(1, 15)):
            slice_height = random.randint(5, 20)
            y = random.randint(0, screen_rect.height - slice_height)
            x_offset = random.randint(-20, 20)
            slice_rect = pygame.Rect(0, y, screen_rect.width, slice_height)
            self.screen.blit(glitch_surface, (x_offset, y), slice_rect)
        
        # Overlay random noise dots/lines
        for _ in range(random.randint(2, 5)):
            x = random.randint(0, screen_rect.width)
            y = random.randint(0, screen_rect.height)
            
            pygame.draw.line(
                self.screen, settings.PIP_BOY_LIGHT,
                (x, y),
                (x + random.randint(-2, 2), y + random.randint(-2, 2)),
                1
            )

    def render(self):
        self.render_header()
        self.render_sub_tabs()
        self.render_tab()  
                    
        if self.render_blur:
            self.tab_blur()
            self.render_blur = False

        # Occasionally apply a CRT glitch effect (roughly 1% chance per frame)
        if random.random() < 0.001:
            self.crt_glitch_effect()
