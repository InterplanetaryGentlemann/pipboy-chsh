import os
import pygame
import sys
import random
import settings
import threading
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init(frequency=44100, size=-16, channels=1)

# Importing tab functions
from stat_tab import draw_stat_tab
from inv_tab import draw_inv_tab
from data_tab import draw_data_tab
from radio_tab import draw_radio_tab #, play_radio_music
from map_tab import draw_map_tab, load_map_image
from bootup import boot_up_sequence  # Importing boot-up sequence function
import global_functs
import event_handler


# Set up the display
infoObject = pygame.display.Info()
screen = pygame.display.set_mode((infoObject.current_w, infoObject.current_h), pygame.FULLSCREEN)
pygame.display.set_caption("Pip-Boy")
pygame.mouse.set_visible(False)
clock = pygame.time.Clock()

# Fonts
main_tab_font = pygame.font.Font(settings.MAIN_FONT_PATH, 17)
fps_font = pygame.font.Font(None, 12)


# Calculate tab positions dynamically
TOTAL_TAB_WIDTH = sum(main_tab_font.size(text)[0] for text in settings.TAB_TEXTS)
TAB_SPACING = (settings.SCREEN_WIDTH - TOTAL_TAB_WIDTH - (2 * settings.TAB_MARGIN)) // (len(settings.TAB_TEXTS) + 1)
TAB_POSITIONS = [
    (settings.TAB_MARGIN + TAB_SPACING * (i + 1) + sum(main_tab_font.size(text)[0] for text in settings.TAB_TEXTS[:i]), settings.TAB_VERTICAL_OFFSET)
    for i, text in enumerate(settings.TAB_TEXTS)
]
TAB_SURFACES = [main_tab_font.render(text, True, settings.PIP_BOY_GREEN) for text in settings.TAB_TEXTS]
TAB_RECTS = [surface.get_rect(topleft=pos) for surface, pos in zip(TAB_SURFACES, TAB_POSITIONS)]

# Bottom bar rectangle
bottom_bar_rect = pygame.Rect(0, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT, settings.SCREEN_WIDTH,
                              settings.BOTTOM_BAR_HEIGHT)

# Selected tab index
SELECTED_TAB_INDEX = 0

# CRT overlay
if settings.SHOW_STATIC:
    overlay_image = pygame.image.load(settings.CRT_OVERLAY).convert_alpha()
    overlay_image.set_alpha(80)
    scanline_image = pygame.image.load(settings.SCANLINE_OVERLAY).convert_alpha()
    scanline_image.set_alpha(10)
    scanline_y = -scanline_image.get_height()

    crt_overlay = [
        pygame.image.load(os.path.join(settings.CRT_STATIC, filename)).convert_alpha()
        for filename in os.listdir(settings.CRT_STATIC) if filename.endswith(".png")
    ]
    current_crt_image = 0


def render_fps(screen, fps):
    # Render and display FPS on the screen.
    fps_text = fps_font.render(f"{fps:.0f}", True, settings.PIP_BOY_GREEN)
    screen.blit(fps_text, (5, 5))

def glitch_effect(screen):
    # Glitch effect
    if random.randrange(100) < settings.GLITCH_MOVE_CHANCE:
        for _ in range(20):
            # Define the spring motion parameters
            time = pygame.time.get_ticks()  # Get current time

            jump_offset = int(6 * math.sin(time))

            screen.blit(screen, (0, -jump_offset))
            pygame.time.wait(settings.FPS // 3)
    else:
        screen_copy = screen.copy()
        for i in range(1, 12, 6):
            blur = pygame.transform.box_blur(screen_copy, i)
            blur.set_alpha(180)
            screen.blit(blur, (0, 0), special_flags=pygame.BLEND_ADD)

# Draw tabs
def draw_tabs():
    """Draw the tabs on the screen."""
    for i, (text_surface, text_rect) in enumerate(zip(TAB_SURFACES, TAB_RECTS)):
        # Blit the pre-rendered text surface
        screen.blit(text_surface, text_rect)

        if i == SELECTED_TAB_INDEX:
            # Draw a rectangle for the tab
            tab_rect = pygame.Rect(1, text_rect.height, settings.SCREEN_WIDTH - 4, settings.LINE_THICKNESS)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, tab_rect)

            tab_rect_left_line = pygame.Rect(tab_rect.left, text_rect.height, settings.LINE_THICKNESS, 7)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, tab_rect_left_line)

            tab_rect_right_line = pygame.Rect(tab_rect.right - settings.LINE_THICKNESS, text_rect.height, settings.LINE_THICKNESS, 7)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, tab_rect_right_line)

            # Draw two vertical lines on the left and right of the tab
            left_line_rect = pygame.Rect(TAB_POSITIONS[i][0] - settings.TEXT_TAB_MARGIN, TAB_POSITIONS[i][1] * 8,
                                         settings.LINE_THICKNESS,
                                         text_rect.height - 8)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, left_line_rect)
            right_line_rect = pygame.Rect(TAB_POSITIONS[i][0] + text_rect.width + settings.TEXT_TAB_MARGIN,
                                          TAB_POSITIONS[i][1] * 8,
                                          settings.LINE_THICKNESS,
                                          text_rect.height - 8)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, right_line_rect)

            left_horizontal_line_rect = pygame.Rect(left_line_rect.left, left_line_rect.top - settings.LINE_THICKNESS, settings.TEXT_TAB_MARGIN / 1.5, settings.LINE_THICKNESS)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, left_horizontal_line_rect)

            right_horizontal_line_rect = pygame.Rect(right_line_rect.right - (settings.TEXT_TAB_MARGIN / 1.5), left_line_rect.top - settings.LINE_THICKNESS, settings.TEXT_TAB_MARGIN / 1.5, settings.LINE_THICKNESS)
            pygame.draw.rect(screen, settings.PIP_BOY_GREEN, right_horizontal_line_rect)

            # Draw a horizontal line at the bottom of the tab
            horizontal_line_rect1 = pygame.Rect(left_line_rect.left + settings.LINE_THICKNESS, tab_rect.bottom - settings.LINE_THICKNESS,
                                                right_line_rect.right - left_line_rect.left - (
                                                            settings.LINE_THICKNESS * 2),
                                                settings.LINE_THICKNESS)
            pygame.draw.rect(screen, settings.BACKGROUND, horizontal_line_rect1)

# Boot-up sequence
if settings.BOOT_SCREEN:
    boot_up_sequence(screen, clock)

# Background sound
if settings.SOUND_ON:
    global_functs.play_sfx("../sounds/pipboy/UI_PipBoy_Hum_LP.ogg", settings.VOLUME / 10, -1)

# Load map image
threading.Thread(target=load_map_image, args=(str(settings.LONGITUDE), str(settings.LATITUDE), settings.ZOOM)).start()

# Main loop
running = True
tab_switch = False
while running:
    screen.fill(settings.BACKGROUND)

    # Handle events
    event = event_handler.handle_events()
    if event == 'left':
        SELECTED_TAB_INDEX = (SELECTED_TAB_INDEX - 1) % len(settings.TAB_TEXTS)
        tab_switch = True
    if event == 'right':
        SELECTED_TAB_INDEX = (SELECTED_TAB_INDEX + 1) % len(settings.TAB_TEXTS)
        tab_switch = True

    # Draw UI elements
    draw_tabs()
    pygame.draw.rect(screen, settings.PIP_BOY_DARKER, bottom_bar_rect)

    # Draw content based on selected tab
    if SELECTED_TAB_INDEX == 0:
        draw_stat_tab(screen, event)
    elif SELECTED_TAB_INDEX == 1:
        draw_inv_tab(screen)
    elif SELECTED_TAB_INDEX == 2:
        draw_data_tab(screen)
    elif SELECTED_TAB_INDEX == 3:
        draw_map_tab(screen, event)
    elif SELECTED_TAB_INDEX == 4:
        draw_radio_tab(screen, event)

    if tab_switch:
        tab_switch = False
        if settings.SOUND_ON:
            global_functs.switch_sounds()
        threading.Thread(target=glitch_effect, args=(screen,)).start()

    # Static overlay and scanline
    if settings.SHOW_STATIC:
        screen.blit(overlay_image, (0, 0))
        screen.blit(crt_overlay[current_crt_image], (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        current_crt_image = (current_crt_image + 1) % len(crt_overlay)
        screen.blit(scanline_image, (0, scanline_y))
        scanline_y = (scanline_y + 4) % settings.SCREEN_HEIGHT

    # Calculate FPS
    fps = clock.get_fps()
    render_fps(screen, fps)

    pygame.display.flip()
    clock.tick(settings.FPS)

# Quit Pygame
pygame.quit()
sys.exit()

