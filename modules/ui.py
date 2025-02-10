# generic_list.py
from threading import Thread, Event, Lock
import pygame
import settings
from util_functs import Utils

###############################################
# Generic UI elements for the Pip-OS project #
###############################################

# Generic list class for displaying items with selection
# Supports stats display and selection dot rendering

class GenericList:
    def __init__(self, draw_space, font, items=["",], enable_dot=False,
                 selection_rect_color=settings.PIP_BOY_LIGHT,
                 text_color=settings.PIP_BOY_LIGHT,
                 selected_text_color=settings.PIP_BOY_DARK,
                 stats=None,
                 stats_color=settings.PIP_BOY_LIGHT,
                 selected_stats_color=settings.PIP_BOY_DARK,
                 dot_color=settings.PIP_BOY_LIGHT,
                 dot_darker_color=settings.PIP_BOY_DARK,
                 dot_size=settings.RADIO_STATION_SELECTION_DOT_SIZE,
                 text_margin=settings.RADIO_STATION_TEXT_MARGIN,
                 selection_dot_margin=settings.RADIO_STATION_SELECTION_MARGIN):
        self.draw_space = draw_space
        self.font = font
        self.enable_dot = enable_dot
        self.font_height = self.font.get_height()
        self.selection_rect_width = draw_space.width
        self.selection_rect_color = selection_rect_color
        self.text_color = text_color
        self.selected_text_color = selected_text_color
        self.text_margin = text_margin

        # Stats-related properties
        self.stats = stats
        if self.stats is not None:
            if len(self.stats) != len(items):
                raise ValueError("Length of stats must match the number of items")
            self.stats_color = stats_color
            self.selected_stats_color = selected_stats_color
            self.max_stat_width = max([self.font.size(str(stat))[0] for stat in self.stats])

        
        # Dot-related properties (only initialized if needed)
        self.dot = None
        self.dot_darker = None
        self.dot_size = dot_size
        self.selection_dot_margin = selection_dot_margin
        self.dot_color = dot_color
        self.dot_darker_color = dot_darker_color


        self.list_surface = None
        self.selected_text = None
        self.selected_stat = None
        
        self.view_surface = pygame.Surface((self.draw_space.width, self.draw_space.height), pygame.SRCALPHA)

        self._init_selection_rect()
           
        self.selected_index = 0
        self.previously_selected_index = 0
        self.items = items
        
        if len(self.items) > 0:
            if self.selected_index >= len(self.items):
                self.selected_index = max(0, len(self.items) - 1)
        
        self._prepare_list_surface()
        # Only create dots if enabled
        if self.enable_dot:
            self._create_dots()

    def _prepare_list_surface(self):
        if not self.items:
            self.list_surface = pygame.Surface((self.draw_space.width, 0), pygame.SRCALPHA)
            return
        height = self.font_height * len(self.items)
        self.list_surface = pygame.Surface((self.draw_space.width, height), pygame.SRCALPHA)
        
        if self.stats is not None:
            stats_column_center_x = self.selection_rect_width - self.max_stat_width
        for i, item in enumerate(self.items):
            # Render item label
            text_surface = self.font.render(item, True, self.text_color)
            self.list_surface.blit(text_surface, (self.text_margin, i * self.font_height))
            # Render stat if enabled
            if self.stats is not None:
                stat = str(self.stats[i])
                stat_surface = self.font.render(stat, True, self.stats_color)
                stat_x = stats_column_center_x - (stat_surface.get_width() // 2)
                self.list_surface.blit(stat_surface, (stat_x, i * self.font_height))
        self.update_list()

    def _create_dots(self):
        """Initialize dot surfaces only if enabled"""
        self.dot = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot.fill(self.dot_color)
        self.dot_darker = pygame.Surface((self.dot_size, self.dot_size), pygame.SRCALPHA)
        self.dot_darker.fill(self.dot_darker_color)

    def _init_selection_rect(self):
        self.selection_rect = pygame.Rect(
            0, 0, self.selection_rect_width, self.font_height
        )

    def set_items(self, items, stats=None):
        self.items = items
        if stats is not None:
            if len(stats) != len(items):
                raise ValueError("Length of stats must match the number of items")
            self.stats = stats
        else:
            self.stats = None
        if self.selected_index >= len(self.items):
            self.selected_index = max(0, len(self.items) - 1)
        self._prepare_list_surface()
        

    def update_list(self):
        if not self.items:
            self.selected_text = None
            return
        self.selection_rect.y = self.selected_index * self.font_height
        selected_item = self.items[self.selected_index]
        self.selected_text = self.font.render(selected_item, True, self.selected_text_color)
        if self.stats is not None:
            stat = str(self.stats[self.selected_index])
            self.selected_stat = self.font.render(stat, True, self.selected_stats_color)


    def change_selection(self, direction: bool):
        new_index = self.selected_index + (-1 if direction else 1)

        prev_index = self.selected_index
        if 0 <= new_index < len(self.items):
            self.selected_index = new_index
            self.update_list()    
        return prev_index

    def render(self, screen, active_index=None, was_selected=False):
        if not self.list_surface or not self.selected_text:
            return

        self.view_surface.fill(settings.BACKGROUND)
        self.view_surface.blit(self.list_surface, (0, 0))

        # Draw selection rectangle
        pygame.draw.rect(self.view_surface, self.selection_rect_color, self.selection_rect)
        self.view_surface.blit(self.selected_text, (self.text_margin, self.selection_rect.y))
        
        if self.stats is not None:
            stat_x = self.selection_rect_width - self.max_stat_width- (self.selected_stat.get_width() // 2)
            self.view_surface.blit(self.selected_stat, (stat_x, self.selection_rect.y))

        # Conditional dot rendering
        if self.enable_dot and active_index is not None and was_selected:
            dot = (self.dot_darker if (active_index == self.selected_index)
                   else self.dot)
            dot_y = (active_index * self.font_height + 
                    (self.font_height // 2) - 
                    (self.dot_size // 2))
            self.view_surface.blit(dot, (self.text_margin - self.selection_dot_margin, dot_y))

        screen.blit(self.view_surface, (self.draw_space.x, self.draw_space.y))






# Generic grid class for displaying items with labels and values
# Supports vertical dividers and highlighting of entries


class ItemGrid:
    def __init__(self, draw_space, font, padding=5, text_margin=0.5):
        self.draw_space = draw_space
        self.font = font
        self.line_height = self.font.get_height()
        self.padding = padding
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None  # Only one divider per grid
        self.top_margin = text_margin
        self.bottom_margin = text_margin * 2
        self.text_cache = {}  # New surface cache
        


    def _get_rendered_text(self, text, color):
        key = (text, color)
        if key not in self.text_cache:
            self.text_cache[key] = self.font.render(text, True, color)
        return self.text_cache[key]


    def update(self, entries):
        """Prepare all rendering elements with proper alignment, adding a vertical divider if needed."""
        self.precomputed_bg = []
        self.precomputed_text = []
        self.precomputed_divider = None  # Reset divider each update
        current_y = self.draw_space.bottom - settings.GRID_BOTTOM_MARGIN

        total_height = sum(
            (
                self.top_margin +
                self.line_height +
                (max(0, len(entry.get("lines", [])) - 1) * self.line_height) +
                self.bottom_margin
            ) + self.padding
            for entry in entries
        )

        current_y -= total_height
        current_y = max(current_y, self.draw_space.top)  # Clamp to top boundary

        label_x = self.draw_space.left + self.padding

        for entry in entries:
            if current_y >= self.draw_space.bottom:
                break  # Stop if no space left

            bg_color = settings.PIP_BOY_DARKER if entry.get("highlight") else settings.PIP_BOY_DARK
            entry_lines = []
            label_y = current_y + self.top_margin
            icon_x = label_x
            icon_front_x = label_x
            value_x = self.draw_space.right - self.padding
            
            if entry.get("icon_front") and "icon" in entry:
                icon_surface = entry["icon"]
                entry_lines.append(("icon", icon_surface, (icon_x, label_y + 1)))
                # Move label to the right of the icon
                icon_front_x += icon_surface.get_width() + self.padding

            label_surface = self._get_rendered_text(entry["label"], settings.PIP_BOY_LIGHT)
            label_pos = (icon_front_x, label_y)
            entry_lines.append(("label", label_surface, label_pos))

            value_y = label_y        


            if "lines" in entry:
                for i, line in enumerate(entry["lines"]):
                    if i > 0:
                        value_y += self.line_height
                    components = []
                    line_width = 0

                    if "icon" in line:
                        icon_x = value_x - (line["icon"].get_width() // 2)
                        components.append(line["icon"])
                        line_width += line["icon"].get_width() + self.padding

                    text_surface = self.font.render(str(line["value"]), True, settings.PIP_BOY_LIGHT)
                    components.append(text_surface)
                    line_width += text_surface.get_width()

                    # Right-align components
                    current_x = value_x - line_width
                    for component in components:
                        y_pos = value_y + (1 if component == line.get("icon") else 0)
                        entry_lines.append(("component", component, (current_x, y_pos)))
                        icon_x -= component.get_width()
                        current_x += component.get_width() + self.padding
                        

                
            if "value" in entry:
                text_surface = self._get_rendered_text(str(entry["value"]), settings.PIP_BOY_LIGHT)
                text_width = text_surface.get_width()
                entry_lines.append(("value", text_surface, (value_x - text_width, value_y)))
                
            if not entry.get("icon_front") and "icon" in entry:
                icon_surface = entry["icon"]
                icon_x = value_x - icon_surface.get_width() - text_width - (self.padding * 2)
                entry_lines.append(("icon", icon_surface, (icon_x, value_y + 1)))

            # Entry height calculation
            additional_lines = max(0, len(entry.get("lines", [])) - 1)
            entry_height = int(self.top_margin) + self.line_height + additional_lines * self.line_height + int(self.bottom_margin)

            # Store background rectangle
            self.precomputed_bg.append((
                pygame.Rect(
                    self.draw_space.left,
                    current_y,
                    self.draw_space.width,
                    entry_height
                ),
                bg_color
            ))

            # Store text elements
            for element in entry_lines:
                self.precomputed_text.append((element[1], element[2]))

            # Add vertical divider if needed (only one per grid)
            if self.precomputed_divider is None and entry.get("split") and icon_x is not None:
                self.precomputed_divider = pygame.Rect(
                    icon_x,  # Position divider left of the icon
                    current_y,
                    self.padding,
                    entry_height
                )

            current_y += entry_height
            if entry != entries[-1]:  # Only add padding if it's not the last entry
                current_y += self.padding


    def render(self, surface):
        # Draw backgrounds first
        for rect, bg_color in self.precomputed_bg:
            pygame.draw.rect(surface, bg_color, rect)

        # Draw text and icons
        for text_surface, pos in self.precomputed_text:
            surface.blit(text_surface, pos)

        # Draw the vertical divider if it exists
        if self.precomputed_divider is not None:
            pygame.draw.rect(surface, settings.BACKGROUND, self.precomputed_divider)








# Animated image class for displaying sequences of images
# Supports looping and stopping the animation

        
class AnimatedImage:
    def __init__(self, screen, images, position: tuple, frame_duration: int, frame_order: list=None, loop: bool = True, sound_path: str = None):
        self.screen = screen
        self.images = images
        self.position = position
        self.frame_duration = frame_duration / 1000  # Convert to seconds
        self.frame_order = frame_order or list(range(len(images)))
        self.loop = loop
        self.sound_path = sound_path

        self.current_frame_index = 0
        self.done = False
        self.running = False  # Flag for controlling the thread
        self.stop_event = Event()  # Event to stop the thread
        self.lock = Lock()  # Lock to prevent race conditions in render()
        self.thread = None  # The update thread

    def _update_loop(self):
        """Thread function for updating frames."""
        while not self.stop_event.is_set() and not self.done:
            with self.lock:  # Ensure thread safety for frame updates
                if self.done:
                    break

                self.current_frame_index += 1
                if self.current_frame_index >= len(self.frame_order):
                    if self.loop:
                        self.current_frame_index = 0
                        self.play_sound()
                    else:
                        self.done = True
                        break

            # Instead of sleep, wait with the option to interrupt instantly
            self.stop_event.wait(timeout=self.frame_duration)


    def play_sound(self):
        """Play the sound effect if provided."""
        if self.sound_path:
            Utils.play_sfx(self.sound_path, settings.VOLUME / 8, channel=5)

    def start(self):
        """Start the animation thread."""
        if self.thread is None or not self.thread.is_alive():
            self.done = False
            self.stop_event.clear()
            self.thread = Thread(target=self._update_loop, daemon=True)
            self.play_sound()
            self.thread.start()

    def stop(self):
        """Stop the animation instantly."""
        self.stop_event.set()  # Signal thread to exit
        self.thread = None  # Allow restarting without blocking

    def render(self):
        """Render the current frame (thread-safe)."""
        with self.lock:
            self.screen.blit(self.images[self.frame_order[self.current_frame_index]], self.position)

    def reset(self):
        """Reset the animation and restart it."""
        self.stop()
        self.current_frame_index = 0
        self.done = False
        self.start()
