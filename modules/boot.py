import os

import pygame
import settings
import time
import threading
from timer import Timer


class BaseBootSequence:
    def __init__(self):
        # Load fonts or other shared resources

        self.timer = Timer()

    def play_sfx(self, sound_file, volume=settings.VOLUME):
        """
        Play a sound file.
        """
        sound = pygame.mixer.Sound(sound_file)
        sound.set_volume(volume)
        sound.play(0)




class BootText(BaseBootSequence):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 8)
        self.font_height = self.font.get_height()
        self.boot_text_start = ("* 1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0 \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4 \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009 \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0 \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4 \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000 \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014 \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000  \n"
                                "1 0 0x0000A4 0x00000000000000000 start memory discovery 0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000014 0x00000000000000000 CPUO starting cell  \n"
                                "relocation0 0x0000A4 0x00000000000000000 1 0 0x000009  \n"
                                "0x00000000000000000 CPUO launch EFI0 0x0000A4 0x00000000000000000 1 0  \n"
                                "0x000009 0x000000000000E003D CPUO starting EFI0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x0000A4 0x00000000000000000 start memory  \n"
                                "discovery0 0x0000A4 0x00000000000000000 1 0 0x0000A4 0x00000000000000000  \n"
                                "start memory discovery 0 0x0000A4 0x00000000000000000 1 0 0x000014  \n"
                                "0x00000000000000000 CPUO starting cell relocation0 0x0000A4  \n"
                                "0x00000000000000000 1 0 0x000009 0x00000000000000000 CPUO launch EFI0  \n"
                                "0x0000A4 0x00000000000000000 1 0 0x000009 0x000000000000E003D CPUO  \n"
                                "starting EFI0 0x0000A4 0x00000000000000000 1 0 0x0000A4  \n"
                                "0x00000000000000000 start memory discovery0 0x0000A4 0x00000000000000000 END\n")
        self.boot_text_lines = self.boot_text_start.split("\n")
        self.visible_lines_count = settings.SCREEN_HEIGHT // self.font_height
        self.first_iteration = True


        self.start_y = settings.SCREEN_HEIGHT
        self.y_offset = self.start_y

        # Create a surface large enough to contain all the text
        self.full_text_surface = pygame.Surface(((settings.SCREEN_WIDTH), len(self.boot_text_lines) * self.font_height))

        # Render each line of text into the surface
        for i, line in enumerate(self.boot_text_lines):
            line_surface = self.font.render(line, True, settings.PIP_BOY_GREEN)
            self.full_text_surface.blit(line_surface, (0, i * self.font_height))
            


    def display_text_sequence(self, render):
        """Display text sequence with scrolling effect"""
        
        if self.first_iteration:
            if settings.SOUND_ON:
                self.play_sfx(settings.BOOT_SOUND_A)
            self.first_iteration = False
        
        render.add_blit(self.full_text_surface, (0, self.y_offset))  # Draw the text at the current y_offset
        if self.timer.update(28):
            self.y_offset -= self.font_height  # Scroll the text upward
            if self.y_offset < -len(self.boot_text_lines) * self.font_height:
                return True  # Stop the sequence if the text has scrolled off the screen
            return False  

    

class BootCopyright(BaseBootSequence):
    def __init__(self):
        super().__init__()
        self.font = pygame.font.Font(settings.TECH_MONO_FONT_PATH, 12)
        self.font_height = self.font.get_height()
        self.copyright_text = ("*************** PIP-05 (R) V7 .1.0.8 **************\n"
                            "\n"
                            "\n"
                            "\n"
                            "COPYRIGHT 2075 ROBCO(R)\n"
                            "LOADER VI.1\n"
                            "EXEC VERSION 41.10\n"
                            "264k RAM SYSTEM\n"
                            "38911 BYTES FREE\n"
                            "NO HOLOTAPE FOUND\n"
                            "LOAD ROM(1): DEITRIX 303").split('\n')
        self.copyright_text_rendered = []
        self.states = iter(["lines", "cursor", "scroll"])
        self.current_state = next(self.states)
        self.cursor_surface = self.font.render("▮", True, settings.PIP_BOY_GREEN)
        self.current_line = 0
        self.current_char = 0
        self.text_surface = None
        self.cursor_blink_count = 0  # Track blink cycles
        self.cursor_blink_state = False
        self.text_scroll_y = 0
        self.first_iteration = True
        self.pause_timer = Timer()


    def render_copyright_text(self, render, y_offset=0): 
        for line in range(len(self.copyright_text_rendered)):
            self.text_surface = self.font.render(self.copyright_text_rendered[line], True, settings.PIP_BOY_GREEN)
            render.add_blit(self.text_surface, (0, (line * self.font_height) + y_offset))
            
    def display_copyright_text(self, render):

        if self.first_iteration:
            if settings.SOUND_ON:
                self.play_sfx(settings.BOOT_SOUND_B)
            self.first_iteration = False           

        match self.current_state:
            case "lines":
                if self.timer.update(17):
                    if self.current_line >= len(self.copyright_text):
                        self.current_state = next(self.states)
                        return False
                    line = self.copyright_text[self.current_line]

                    # Ensure the current line exists in the rendered list
                    while len(self.copyright_text_rendered) <= self.current_line:
                        self.copyright_text_rendered.append("")

                    if self.current_char < len(line):
                        self.copyright_text_rendered[self.current_line] += line[self.current_char]
                        self.current_char += 1
                    else:
                        self.current_line += 1
                        self.current_char = 0

                self.render_copyright_text(render)
            
            case "cursor":
                self.render_copyright_text(render)

                if not self.pause_timer.check_and_pause("cursor", 50):
                    self.timer.reset()
                    return False
                
                if self.cursor_blink_count > 3:
                    self.current_state = next(self.states)
                    return False
                
                if self.timer.update(200):
                    self.cursor_blink_state = not self.cursor_blink_state
                    self.cursor_blink_timer = 0
                    self.cursor_blink_count += 1
                    
                if self.cursor_blink_state:
                    render.add_blit(self.cursor_surface, (self.text_surface.get_width(), (self.current_line * self.font_height) - self.font_height))                   
               
            case "scroll":
                self.render_copyright_text(render, self.text_scroll_y)
                
                if not self.pause_timer.check_and_pause("scroll", 400):
                    self.timer.reset()
                    return False
                
                if self.timer.update(20):
                    self.text_scroll_y -= 5
                    if self.text_scroll_y < -len(self.copyright_text) * self.font_height:
                        return True
                    

class BootThumbs(BaseBootSequence):
    def __init__(self):
        super().__init__()
               

class Boot:
    def __init__(self, render):
        self.render = render
        self.states = iter(["text", "copyright", "done"])
        self.current_sequence = next(self.states)        
        self.boot_text = BootText()
        self.copyright_text = BootCopyright()   
        self.pause_timer = Timer()
        self.copyright_pause = False
        self.text_pause = False
        self.running = False

    def start(self):
        self.running = True
        
    def run(self):
        while self.running:
            match self.current_sequence:
                case "text":
                    if not self.pause_timer.check_and_pause("text", 100):
                        return False
                    if self.boot_text.display_text_sequence(self.render):
                        self.current_sequence = next(self.states)
                case "copyright":
                    if not self.pause_timer.check_and_pause("copyright", 500):
                        return False
                    if self.copyright_text.display_copyright_text(self.render):
                        self.current_sequence = next(self.states)
                case "done":
                    return True
                    
                    

# class Boot:
#     def __init__(self):
#
#         # Boot-up text
#
#         self.boot_text_copyright = ("*************** PIP-05 (R) V7 .1.0.8 **************\n"
#                                "\n"
#                                "\n"
#                                "\n"
#                                "COPYRIGHT 2075 ROBCO(R)\n"
#                                "LOADER VI.1\n"
#                                "EXEC VERSION 41.10\n"
#                                "264k RAM SYSTEM\n"
#                                "38911 BYTES FREE\n"
#                                "NO HOLOTAPE FOUND\n"
#                                "LOAD ROM(1): DEITRIX 303")
#
#         self.current_sequence = "text"
#         self.boot_text_lines = []
#         self.font_height = 0
#         self.visible_lines_count = 0
#         self.setup_done = False
#
#
#
#
#     # def display_text_sequence(self, screen):
#     #     """
#     #     Display the boot-up sequence.
#     #     """
#     #     boot_text_lines = self.split_text_into_lines(self.boot_text_start, self.boot_font, settings.SCREEN_WIDTH)
#     #
#     #     # Calculate the number of lines that can fit on the screen
#     #     font_height = self.boot_font.get_height()
#     #     visible_lines_count = settings.SCREEN_HEIGHT // font_height
#     #
#     #     current_line_index = 0  # Index to keep track of the current line being displayed
#     #     rendered_lines = []  # List to store rendered surfaces of each line
#     #
#     #     if settings.SOUND_ON:
#     #         self.play_sfx(settings.BOOT_SOUND_A)
#     #
#     #     booting_up = True
#     #     while booting_up:
#     #         screen.fill(settings.BACKGROUND)
#     #
#     #         # Calculate the y-coordinate for each rendered line and blit it onto the screen
#     #         total_height = len(rendered_lines) * font_height
#     #         start_y = settings.SCREEN_HEIGHT - total_height
#     #
#     #         for i, rendered_line in enumerate(rendered_lines):
#     #             line_y = start_y + i * font_height
#     #             boot_text_rect = rendered_line.get_rect(topleft=(0, line_y))
#     #             screen.blit(rendered_line, boot_text_rect)
#     #
#     #         # Check if there are more lines to display
#     #         if current_line_index < len(boot_text_lines):
#     #             line = boot_text_lines[current_line_index]
#     #             rendered_line = self.boot_font.render(line, True, settings.PIP_BOY_GREEN)
#     #             rendered_lines.append(rendered_line)
#     #             current_line_index += 1
#     #
#     #             # Limit the rendered lines to the visible area on the screen
#     #             if len(rendered_lines) > visible_lines_count:
#     #                 rendered_lines.pop(0)  # Remove the oldest line
#     #
#     #         else:
#     #             # If we've reached the end of the lines, show a blank line and stop
#     #             rendered_line = self.boot_font.render("", True, settings.PIP_BOY_GREEN)
#     #             rendered_lines.append(rendered_line)
#     #             current_line_index += 1
#     #
#     #         # Check if we've completed the sequence
#     #         if current_line_index >= len(boot_text_lines) + (settings.SCREEN_HEIGHT // self.boot_font.get_height()) + 2:
#     #             booting_up = False
#     #
#     #         pygame.display.update()
#     #         time.sleep((settings.BOOT_SPEED * 1.15) / 1000)
#     #
#     #     screen.fill(settings.BACKGROUND)
#
#
#
#     def display_copyright_text(self, screen):
#         """
#         Display the copyright text.
#         """
#         lines = self.boot_text_copyright.split('\n')
#         y_offset = 0
#         x_scale = 1.04
#         cursor_surface = self.boot_font.render("▮", True, settings.PIP_BOY_GREEN)
#
#         if settings.SOUND_ON:
#             self.play_sfx(settings.BOOT_SOUND_B)
#
#         for line in lines:
#             x_offset = 0
#             for char in line:
#                 text_surface = self.boot_font.render(char, True, settings.PIP_BOY_GREEN)
#                 screen.blit(text_surface, (int(x_offset * x_scale), y_offset))  # Scale x_offset
#                 pygame.display.update()
#                 time.sleep((settings.BOOT_SPEED / 9) / 1000)
#                 x_offset += text_surface.get_width()
#
#                 screen.blit(cursor_surface, (int(x_offset * x_scale), y_offset))  # Scale x_offset
#                 pygame.display.update()
#                 time.sleep((settings.BOOT_SPEED / 6)/ 1000)
#
#                 pygame.draw.rect(screen, settings.BACKGROUND, (
#                 int(x_offset * x_scale), y_offset, int(cursor_surface.get_width() * x_scale),
#                 self.boot_font.get_height()))  # Scale x_offset and cursor_surface width
#                 pygame.display.update()
#                 x_offset += 1
#
#             y_offset += self.boot_font.get_height()
#
#         for _ in range(3):
#             screen.blit(cursor_surface, (int(x_offset * x_scale), y_offset - self.boot_font.get_height()))  # Scale x_offset
#             pygame.display.update()
#             time.sleep((settings.BOOT_SPEED / 90) / 1000)
#
#             pygame.draw.rect(screen, settings.BACKGROUND, (
#             int(x_offset * x_scale), y_offset - self.boot_font.get_height(), int(cursor_surface.get_width() * x_scale),
#             self.boot_font.get_height()))  # Scale x_offset and cursor_surface width
#             pygame.display.update()
#             time.sleep((settings.BOOT_SPEED / 90) / 1000)
#
#         for i in range(y_offset):
#             screen.scroll(0, -1)
#             pygame.display.update()
#             time.sleep((settings.BOOT_SPEED * 45) / 1000)
#
#
#     def thumbs(self, screen):
#         frameorder = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 3, 4, 5, 6, 7, 7, 7, 7, 7, 7, 7, 7,
#                       7,
#                       7, 7, 7, 7, 7, 7, 7, 7, 7]
#         frameorder = [frame for frame in frameorder for _ in range(2)]
#         images = []  # Initialize an empty list to store images
#         for filename in sorted(os.listdir(settings.BOOT_THUMBS)):
#             if filename.endswith(".png"):
#                 original_image = pygame.image.load(os.path.join(settings.BOOT_THUMBS, filename)).convert_alpha()
#                 scaled_image = pygame.transform.scale(original_image, (
#                 original_image.get_width() // 2, original_image.get_height() // 2))
#                 images.append(scaled_image)
#
#         if settings.SOUND_ON:
#             self.play_sfx(settings.BOOT_SOUND_C)
#
#         # Text blinking
#         text_surface = self.boot_font.render("INITIATING...", True, settings.PIP_BOY_GREEN)
#         alpha_values = (list(range(0, 150)) + list(range(150, 0, -1))) * 6
#         text_y = screen.get_rect().center[1] + images[
#             0].get_rect().height // 2 + 20  # Y-coordinate for the blinking text
#         current_blink = 0
#         blink_range = int(len(alpha_values) / len(frameorder))
#
#         for i in range(len(frameorder)):
#             screen.fill(settings.BACKGROUND)
#             # Adjust image position
#             image = images[frameorder[i]]
#             image_rect = image.get_rect(center=(screen.get_rect().centerx - 10, screen.get_rect().centery))
#             # Blit image
#             screen.blit(image, image_rect)
#             # Calculate alpha value index based on frame and blink range
#             alpha_index = min((current_blink + i * blink_range), len(alpha_values) - 1)
#             # Adjust text position
#             text_rect = text_surface.get_rect(midtop=(screen.get_rect().centerx, text_y))
#             # Blit text
#             text_surface.set_alpha(alpha_values[alpha_index])
#             screen.blit(text_surface, text_rect)
#             pygame.display.update()
#             # Adjust frame rate
#             time.sleep((settings.BOOT_SPEED / 2.5) / 1000)
#             # Adjust alpha increment for smoother animation
#             alpha_values[alpha_index] += 1
#
#
#     def boot_up_sequence(self, screen):
#         """Boot-up sequence for the Pip-boy."""
#         # Draw boot-up text
#         self.display_text_sequence(screen)
#         time.sleep((settings.BOOT_SPEED * 25) / 1000)
#         self.display_copyright_text(screen)
#         time.sleep((settings.BOOT_SPEED * 10) / 1000)
#         self.thumbs(screen)
#         screen.fill(settings.BACKGROUND)
#         return True
#
#
#
#     def run(self, screen):
#         match self.current_sequence:
#             case "text":
#                 self.display_text_sequence(screen)
#             case "copyright":
#                 self.display_copyright_text(screen)
#             case "thumbs":
#                 self.thumbs(screen)
#             case _:
#                 print("Invalid sequence")
#                 return False
