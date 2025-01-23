import pygame
import settings
import datetime
import random

class SoundManager:
    def __init__(self, volume=settings.VOLUME):
        self.volume = volume

    def play_sfx(self, sound_file, repeat=0):
        """Play a sound file."""
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(self.volume)
        sound.play(repeat)

    def switch_sounds(self):
        """Play a random static burst sound."""
        i = str(random.randint(1, 17)).zfill(2)
        self.play_sfx(f"sounds/pipboy/BurstStatic/UI_PipBoy_BurstStatic_{i}.ogg", self.volume / 3)


class DateTimeRenderer:
    def __init__(self, font_path, screen_height, pip_boy_green):
        self.datetime_font = pygame.font.Font(font_path, 13)
        self.screen_height = screen_height
        self.pip_boy_green = pip_boy_green
        self.current_date = None
        self.current_year = None

    def get_date_and_year(self):
        """Update the current date and year."""
        now = datetime.datetime.now()
        self.current_date = now.strftime("%d.%m.")
        self.current_year = str(int(now.strftime("%Y")) + 263)

    def render(self, screen):
        """Render the date and time on the screen."""
        if self.current_date is None or self.current_year is None:
            self.get_date_and_year()

        now = datetime.datetime.now()
        current_time = now.strftime("%I:%M%p")
        date_time = self.datetime_font.render(
            f"{self.current_date}{self.current_year}", True, self.pip_boy_green
        )
        time_surface = self.datetime_font.render(current_time, True, self.pip_boy_green)

        date_time_rect = date_time.get_rect(bottomleft=(2, self.screen_height - 2))
        time_rect = time_surface.get_rect(bottomleft=(80, self.screen_height - 2))

        screen.blit(date_time, date_time_rect)
        screen.blit(time_surface, time_rect)


class UIRenderer:
    def __init__(self, screen_width, bottom_bar_height, divider, background_color):
        self.screen_width = screen_width
        self.bottom_bar_height = bottom_bar_height
        self.divider = divider
        self.background_color = background_color

    def draw_bottom_tab_lines(self, screen, with_middle=False):
        """Draw bottom tab divider lines."""
        left_rect = pygame.Rect(
            75, settings.SCREEN_HEIGHT - self.bottom_bar_height, self.divider, self.bottom_bar_height
        )
        pygame.draw.rect(screen, self.background_color, left_rect)

        if with_middle:
            middle_rect = pygame.Rect(
                self.screen_width // 2 + self.divider,
                settings.SCREEN_HEIGHT - self.bottom_bar_height,
                self.divider,
                self.bottom_bar_height,
            )
            pygame.draw.rect(screen, self.background_color, middle_rect)

    def draw_sub_tabs(self, screen, selected_index, sub_tab_texts, tab_index_func, main_tab_texts, font_paths, sub_tab_margin, pip_boy_green):
        """Draw sub-tabs on the screen."""
        regular_font = pygame.font.Font(font_paths["regular"], 18)
        bold_font = pygame.font.Font(font_paths["bold"], 18)

        main_tab_width = self.screen_width // len(main_tab_texts)
        main_tab_center_x = main_tab_width * tab_index_func() + main_tab_width // 2

        total_width = sum(
            bold_font.size(text if i == selected_index else regular_font.size(text))[0] + sub_tab_margin
            for i, text in enumerate(sub_tab_texts)
        ) - sub_tab_margin

        start_x = main_tab_center_x - total_width // 2
        x_position = start_x

        for i, text in enumerate(sub_tab_texts):
            font = bold_font if i == selected_index else regular_font
            text_surface = font.render(text, True, pip_boy_green)
            screen.blit(text_surface, (x_position, 50))
            x_position += text_surface.get_size()[0] + sub_tab_margin
