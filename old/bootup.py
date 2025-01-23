import pygame
import settings
import global_functs
import os

pygame.init()

# Load font
boot_font1 = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 9)
boot_font2 = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 9)

# Boot-up text
boot_text_start = ("* 1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4 "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0 "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4 "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  "
             "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  "
             "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  "
             "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  "
             "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  "
             "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  "
             "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  "
             "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  "
             "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  "
             "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  "
             "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  "
             "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  "
             "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  "
             "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 END")
boot_text_copyright = ("*************** PIP-05 (R) V7 .1.0.8 **************\n"
             "\n"
             "\n"
             "\n"
             "COPYRIGHT 2075 ROBCO(R)\n"
             "LOADER VI.1\n"
             "EXEC VERSION 41.10\n"
             "264k RAM SYSTEM\n"
             "38911 BYTES FREE\n"
             "NO HOLOTAPE FOUND\n"
             "LOAD ROM(1): DEITRIX 303")
boot_text_color = settings.PIP_BOY_GREEN

# Load images dynamically from a directory
image_folder = "images/boot"  # Adjust this to the directory where your images are located
image_rects = []




def split_text_into_lines(text, font, max_width):
    """
    Split text into lines that fit within the screen width.
    """
    words = text.split()
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + ' ' + word if current_line else word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    lines.append(current_line)
    return lines


def display_text_sequence(screen, clock):
    """
    Display the boot-up sequence.
    """
    boot_text_lines = split_text_into_lines(boot_text_start, boot_font1, settings.SCREEN_WIDTH)

    # Calculate the number of lines that can fit on the screen
    font_height = boot_font1.get_height()
    visible_lines_count = settings.SCREEN_HEIGHT // font_height

    current_line_index = 0  # Index to keep track of the current line being displayed
    rendered_lines = []  # List to store rendered surfaces of each line

    if settings.SOUND_ON:
        global_functs.play_sfx("../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_A.ogg")

    booting_up = True
    while booting_up:
        screen.fill(settings.BACKGROUND)

        # Calculate the y-coordinate for each rendered line and blit it onto the screen
        total_height = len(rendered_lines) * font_height
        start_y = settings.SCREEN_HEIGHT - total_height

        for i, rendered_line in enumerate(rendered_lines):
            line_y = start_y + i * font_height
            boot_text_rect = rendered_line.get_rect(topleft=(0, line_y))
            screen.blit(rendered_line, boot_text_rect)

        # Check if there are more lines to display
        if current_line_index < len(boot_text_lines):
            line = boot_text_lines[current_line_index]
            rendered_line = boot_font1.render(line, True, boot_text_color)
            rendered_lines.append(rendered_line)
            current_line_index += 1

            # Limit the rendered lines to the visible area on the screen
            if len(rendered_lines) > visible_lines_count:
                rendered_lines.pop(0)  # Remove the oldest line

        else:
            # If we've reached the end of the lines, show a blank line and stop
            rendered_line = boot_font1.render("", True, boot_text_color)
            rendered_lines.append(rendered_line)
            current_line_index += 1

        # Check if we've completed the sequence
        if current_line_index >= len(boot_text_lines) + (settings.SCREEN_HEIGHT // boot_font1.get_height()) + 2:
            booting_up = False

        pygame.display.flip()
        clock.tick(settings.BOOT_SPEED / 1.15)

    screen.fill(settings.BACKGROUND)


def display_copyright_text(screen, clock):
    """
    Display copyright text with typewriter effect.
    """
    lines = boot_text_copyright.split('\n')
    y_offset = 0
    x_scale = 1.04
    cursor_surface = boot_font2.render("▮", True, settings.PIP_BOY_GREEN)

    if settings.SOUND_ON:
        global_functs.play_sfx("../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_B.ogg")

    for line in lines:
        x_offset = 0
        for char in line:
            text_surface = boot_font2.render(char, True, settings.PIP_BOY_GREEN)
            screen.blit(text_surface, (int(x_offset * x_scale), y_offset))  # Scale x_offset
            pygame.display.flip()
            clock.tick(settings.BOOT_SPEED * 3)
            x_offset += text_surface.get_width()

            screen.blit(cursor_surface, (int(x_offset * x_scale), y_offset))  # Scale x_offset
            pygame.display.flip()
            clock.tick(settings.BOOT_SPEED * 2)

            pygame.draw.rect(screen, settings.BACKGROUND, (int(x_offset * x_scale), y_offset, int(cursor_surface.get_width() * x_scale), boot_font2.get_height()))  # Scale x_offset and cursor_surface width
            pygame.display.flip()
            x_offset += 1

        y_offset += boot_font2.get_height()

    for _ in range(3):
        screen.blit(cursor_surface, (int(x_offset * x_scale), y_offset - boot_font2.get_height()))  # Scale x_offset
        pygame.display.flip()
        clock.tick(settings.BOOT_SPEED / 9)

        pygame.draw.rect(screen, settings.BACKGROUND, (int(x_offset * x_scale), y_offset - boot_font2.get_height(), int(cursor_surface.get_width() * x_scale), boot_font2.get_height()))  # Scale x_offset and cursor_surface width
        pygame.display.flip()
        clock.tick(settings.BOOT_SPEED / 9)

    for i in range(y_offset):
        screen.scroll(0, -1)
        pygame.display.flip()
        clock.tick(settings.BOOT_SPEED * 4.5)


def thumbs(screen, clock):
    frameorder = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7, 7,
                  7, 7, 7, 7, 7, 7, 7, 7, 7]
    frameorder = [frame for frame in frameorder for _ in range(2)]
    path = "../images/boot"
    images = []  # Initialize an empty list to store images
    for filename in sorted(os.listdir(path)):
        if filename.endswith(".png"):
            original_image = pygame.image.load(os.path.join(path, filename)).convert_alpha()
            scaled_image = pygame.transform.scale(original_image, (original_image.get_width() // 2, original_image.get_height() // 2))
            images.append(scaled_image)

    if settings.SOUND_ON:
        global_functs.play_sfx("../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_C.ogg")

    # Text blinking
    text_surface = boot_font2.render("INITIATING...", True, boot_text_color)
    alpha_values = (list(range(0, 150)) + list(range(150, 0, -1))) * 6
    text_y = screen.get_rect().center[1] + images[0].get_rect().height // 2 + 20  # Y-coordinate for the blinking text
    current_blink = 0
    blink_range = int(len(alpha_values) / len(frameorder))

    for i in range(len(frameorder)):
        screen.fill(settings.BACKGROUND)
        # Adjust image position
        image = images[frameorder[i]]
        image_rect = image.get_rect(center=(screen.get_rect().centerx - 10, screen.get_rect().centery))
        # Blit image
        screen.blit(image, image_rect)
        # Calculate alpha value index based on frame and blink range
        alpha_index = min((current_blink + i * blink_range), len(alpha_values) - 1)
        # Adjust text position
        text_rect = text_surface.get_rect(midtop=(screen.get_rect().centerx, text_y))
        # Blit text
        text_surface.set_alpha(alpha_values[alpha_index])
        screen.blit(text_surface, text_rect)
        pygame.display.flip()
        # Adjust frame rate
        clock.tick(settings.BOOT_SPEED / 2.5)
        # Adjust alpha increment for smoother animation
        alpha_values[alpha_index] += 1


def boot_up_sequence(screen, clock):
    display_text_sequence(screen, clock)
    pygame.time.wait(settings.BOOT_SPEED * 25)
    display_copyright_text(screen, clock)
    pygame.time.wait(settings.BOOT_SPEED * 10)
    thumbs(screen, clock)


