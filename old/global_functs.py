import pygame
import settings
import datetime
import random

current_date = None
current_year = None



datetime_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, 13)



def play_sfx(sound_file, volume=settings.VOLUME, repeat=0):
    """
    Play a sound file.
    """
    sound = pygame.mixer.Sound(sound_file)
    sound.set_volume(volume)
    sound.play(repeat)


def switch_sounds():
    i = str(random.randint(1, 17))
    if len(i) == 1:
        i = f"0{i}"
    play_sfx(f"sounds/pipboy/BurstStatic/UI_PipBoy_BurstStatic_{i}.ogg", settings.VOLUME / 3)





def bottom_tab_lines1(screen):
    bottom_bar_rect_left = pygame.Rect(75, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT, settings.BOTTOM_BAR_DIVIDER,
                                       settings.BOTTOM_BAR_HEIGHT)
    pygame.draw.rect(screen, settings.BACKGROUND, bottom_bar_rect_left)
    bottom_bar_rect_right = pygame.Rect(settings.SCREEN_WIDTH - 75 + settings.BOTTOM_BAR_DIVIDER, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT, settings.BOTTOM_BAR_DIVIDER,
                                        settings.BOTTOM_BAR_HEIGHT)
    pygame.draw.rect(screen, settings.BACKGROUND, bottom_bar_rect_right)

def bottom_tab_lines2(screen):
    bottom_bar_rect_left = pygame.Rect(75, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT, settings.BOTTOM_BAR_DIVIDER,
                                       settings.BOTTOM_BAR_HEIGHT)
    pygame.draw.rect(screen, settings.BACKGROUND, bottom_bar_rect_left)
    bottom_bar_rect_middle = pygame.Rect(settings.SCREEN_WIDTH // 2 + settings.BOTTOM_BAR_DIVIDER, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT, settings.BOTTOM_BAR_DIVIDER,
                                         settings.BOTTOM_BAR_HEIGHT)
    pygame.draw.rect(screen, settings.BACKGROUND, bottom_bar_rect_middle)


def get_date_and_year():
    global current_date, current_year
    now = datetime.datetime.now()
    current_date = now.strftime("%d.%m.")
    current_year = str(int(now.strftime("%Y")) + 263)

def date_time_render(screen):
    global current_date, current_year
    if current_date is None or current_year is None:
        get_date_and_year()

    # Get the current time
    now = datetime.datetime.now()

    current_date = now.strftime("%d.%m.")

    # Render date with updated day and year
    date_time = datetime_font.render(f"{current_date}{current_year}", True, settings.PIP_BOY_GREEN)
    date_time_rect = date_time.get_rect(bottomleft=(2, settings.SCREEN_HEIGHT - 2))
    screen.blit(date_time, date_time_rect)


    # Format the time as HH:MM:SS
    current_time = now.strftime("%I:%M%p")

    # Render the time
    time_surface = datetime_font.render(current_time, True, settings.PIP_BOY_GREEN)
    time_rect = time_surface.get_rect(bottomleft=(80, settings.SCREEN_HEIGHT - 2))
    screen.blit(time_surface, time_rect)


def draw_sub_tabs(screen, selected_sub_tab_index, sub_tab_texts):
    """Draw sub-tab headers at the top of the screen.

    Args:
        screen (pygame.Surface): The Pygame screen to draw on.
        selected_sub_tab_index (int): The index of the currently selected sub-tab.
        sub_tab_texts (list): List of sub-tab names.
    """

    font_size = 18

    regular_font = pygame.font.Font(settings.ROBOTO_PATH, font_size)
    bold_font = pygame.font.Font(settings.ROBOTO_BOLD_PATH, font_size)

    # Sub-tab area dimensions
    sub_tab_y = 50  # Sub-tabs are drawn 50px below the top
    sub_tab_area_height = 30

    # Calculate the center x-coordinate of the main tab
    main_tab_width = settings.SCREEN_WIDTH // len(settings.TAB_TEXTS)
    main_tab_center_x = main_tab_width * get_tab_index() + main_tab_width // 2

    # Calculate the width of all sub-tabs combined
    total_sub_tabs_width = sum(
        bold_font.size(text if i == selected_sub_tab_index else regular_font.size(text))[0] + settings.SUB_TAB_MARGIN
        for i, text in enumerate(sub_tab_texts)
    )
    total_sub_tabs_width -= settings.SUB_TAB_MARGIN  # Remove extra margin after the last sub-tab

    # Determine the starting x-coordinate to center sub-tabs
    start_x = main_tab_center_x - total_sub_tabs_width // 2

    # Draw the sub-tabs
    x_position = start_x
    for i, text in enumerate(sub_tab_texts):
        # Use bold font for the selected sub-tab
        font = bold_font if i == selected_sub_tab_index else regular_font
        text_surface = font.render(text, True, settings.PIP_BOY_GREEN)

        # Get text size and position
        text_width, text_height = text_surface.get_size()
        text_x = x_position
        text_y = sub_tab_y + (sub_tab_area_height - text_height) // 2

        # Draw the text
        screen.blit(text_surface, (text_x, text_y))

        # Update the x_position for the next sub-tab
        x_position += text_width + settings.SUB_TAB_MARGIN