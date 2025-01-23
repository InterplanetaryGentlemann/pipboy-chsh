import pygame
import settings
from global_functs import bottom_tab_lines1, draw_sub_tabs

sub_tab_text = ['STATUS', 'SPECIAL', 'PERKS']
selected_sub_tab_index = 0


def draw_status_tab(screen):
    """Draw the content for the STATUS sub-tab"""
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # Example player status
    status_items = [
        ("Health", "85/100"),
        ("Radiation", "Low"),
        ("Fatigue", "Rested"),
        ("Limb Status", "All Fine")
    ]

    # Draw tab title
    title = font.render("STATUS", True, (0, 255, 0))
    screen.blit(title, (20, 20))

    # Draw status items
    y_offset = 70
    for item, value in status_items:
        text = small_font.render(f"{item}: {value}", True, (0, 255, 0))
        screen.blit(text, (40, y_offset))
        y_offset += 40

def draw_special_tab(screen):
    """Draw the content for the SPECIAL sub-tab"""
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # Example SPECIAL stats
    special_stats = {
        "Strength": 5,
        "Perception": 4,
        "Endurance": 6,
        "Charisma": 3,
        "Intelligence": 7,
        "Agility": 5,
        "Luck": 2
    }

    # Draw tab title
    title = font.render("SPECIAL", True, (0, 255, 0))
    screen.blit(title, (20, 20))

    # Draw SPECIAL stats
    y_offset = 70
    for stat, value in special_stats.items():
        text = small_font.render(f"{stat}: {value}", True, (0, 255, 0))
        screen.blit(text, (40, y_offset))
        y_offset += 40

def draw_perks_tab(screen):
    """Draw the content for the PERKS sub-tab"""
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)

    # Example perks list
    perks = [
        "Gunslinger: Increased pistol accuracy",
        "Lead Belly: Reduced radiation from food and water",
        "Iron Fist: Increased unarmed damage"
    ]

    # Draw tab title
    title = font.render("PERKS", True, (0, 255, 0))
    screen.blit(title, (20, 20))

    # Draw perks
    y_offset = 70
    for perk in perks:
        text = small_font.render(perk, True, (0, 255, 0))
        screen.blit(text, (40, y_offset))
        y_offset += 40


def draw_stat_tab(screen, event):
    global selected_sub_tab_index

    # Handle sub-tab navigation events
    if event == 'sub_tab_left':
        # Decrease the index only if it's not already at the beginning
        if selected_sub_tab_index > 0:
            selected_sub_tab_index -= 1
    elif event == 'sub_tab_right':
        # Increase the index only if it's not already at the end
        if selected_sub_tab_index < len(sub_tab_text) - 1:
            selected_sub_tab_index += 1

    # Draw sub-tab headers
    draw_sub_tabs(screen, selected_sub_tab_index, sub_tab_text)
    #
    # # Draw the content for the selected sub-tab
    # if selected_sub_tab_index == 0:
    #     draw_status_tab(screen)
    # elif selected_sub_tab_index == 1:
    #     draw_special_tab(screen)
    # elif selected_sub_tab_index == 2:
    #     draw_perks_tab(screen)

    # Bottom tab lines
    bottom_tab_lines1(screen)

