import settings
import pygame

class TabManager:
    def __init__(self, screen):
        self.screen = screen
        self.main_tab_font = pygame.font.Font(settings.MAIN_FONT_PATH, 17)
        self.tab_font_height = self.main_tab_font.get_height()
        self.tabs = settings.TABS
        self.current_tab_index = 0
        self.tab_x_offset = []

        self.tab_text_surface = pygame.Surface((settings.SCREEN_WIDTH, self.tab_font_height))
        self.init_tab_text()
        
    def init_tab_text(self):
    
        total_tab_width = sum(self.main_tab_font.size(tab)[0] for tab in self.tabs)
        tab_spacing = (settings.SCREEN_WIDTH - total_tab_width - 2 * settings.TAB_MARGIN) // (len(self.tabs) + 1)
        self.tab_x_offset.append(settings.TAB_MARGIN + tab_spacing)
        
        for i, tab in enumerate(self.tabs):
            text_surface = self.main_tab_font.render(tab, True, settings.PIP_BOY_GREEN)
            self.tab_text_surface.blit(text_surface, (self.tab_x_offset[i], settings.TAB_VERTICAL_OFFSET))
            self.tab_x_offset.append((self.main_tab_font.size(tab)[0] + tab_spacing) + self.tab_x_offset[i])

        print(self.tab_x_offset)
            

    def switch_tab(self, direction):
        if direction:
            self.current_tab = self.tabs[(self.current_tab_index + 1) % len(self.tabs)]
        else:
            self.current_tab = self.tabs[(self.current_tab_index - 1) % len(self.tabs)]

    def draw_tabs(self):
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
            ((self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LINE_OFFSET // 2)), self.tab_font_height), 
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
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LINE_OFFSET // 2), self.tab_font_height), 
            (self.main_tab_font.size(self.tabs[self.current_tab_index])[0] + self.tab_x_offset[self.current_tab_index] + (settings.TAB_HORIZONTAL_LINE_OFFSET // 2), self.tab_font_height - settings.TAB_VERTICAL_LINE_OFFSET),
            1)
        
        # Draw vertical lines at screen edges
        pygame.draw.line(self.screen, settings.PIP_BOY_GREEN, (0, settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (0, self.tab_font_height), 1)
        pygame.draw.line(self.screen, settings.PIP_BOY_GREEN, (settings.SCREEN_WIDTH - 1,settings.TAB_SCREEN_EDGE_LENGTH + self.tab_font_height), (settings.SCREEN_WIDTH - 1, self.tab_font_height ), 1)
        
        
        


    def render(self):
        self.draw_tabs()