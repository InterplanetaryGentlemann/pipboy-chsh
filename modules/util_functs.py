import datetime
import pygame
import settings
import os

class Utils:
         
    @staticmethod
    def tint_image(image, color=settings.PIP_BOY_LIGHT):
        """Tint image with specified color while preserving alpha"""
        tinted = image.copy()
        # Multiply RGB channels with color, preserve original alpha
        tinted.fill(color[:3] + (0,), special_flags=pygame.BLEND_RGB_MULT)
        return tinted       
    
    @staticmethod
    def scale_image(image, scale: float):
        return pygame.transform.smoothscale_by(image, scale)
        
    @staticmethod
    def scale_image_abs(image, width: float = None, height: float = None):
        """
        Scale image absolutely but keep aspect ratio.
        """
        if width is None and height is None:
            return image
        
        if width is None:
            width = image.get_width() * (height / image.get_height())
        elif height is None:
            height = image.get_height() * (width / image.get_width())
        
        # Ensure width and height are integers
        return pygame.transform.smoothscale(
            image, 
            (int(width), int(height))
        )
    
    @staticmethod
    def load_images(folder: str, tint=settings.PIP_BOY_LIGHT):
        """
        Load and tint all PNG images in the specified folder.
        """
        try:
            images = [
                Utils.tint_image(
                    pygame.image.load(os.path.join(folder, f)).convert_alpha(),
                    tint
                ) for f in sorted(os.listdir(folder)) if f.endswith(".png")
            ]
            return images
        except FileNotFoundError:
            return []
        

    @staticmethod        
    def load_svgs_dict(folder: str, scale: int, tint=settings.PIP_BOY_LIGHT):
        """
        Load and tint all SVG images in the specified folder.
        """
        try:
            images = {
                f: Utils.tint_image(
                    pygame.image.load_sized_svg(os.path.join(folder, f), (scale, scale)).convert_alpha(),
                    tint
                ) for f in sorted(os.listdir(folder)) if f.endswith(".svg")
            }
            images= {k.replace(".svg", ""): v for k, v in images.items()}
            return images
        except FileNotFoundError:
            return {}
        
        
    @staticmethod
    def load_svgs(folder: str, scale: float, tint=settings.PIP_BOY_LIGHT):
        """
        Load and tint all SVG images in the specified folder.
        """
        try:
            images = [
                Utils.tint_image(
                    pygame.image.load_sized_svg(os.path.join(folder, f), (scale, scale)).convert_alpha(),
                    tint
                ) for f in sorted(os.listdir(folder)) if f.endswith(".svg")
            ]
            return images
        except FileNotFoundError:
            return []
        
    
    @staticmethod
    def load_svg(scale: int, path: str, tint=settings.PIP_BOY_LIGHT):
        """
        Load an SVG file, scale it, and apply a tint.
        """
        if path.endswith(".svg"):
            # Assuming pygame.image.load_sized_svg exists
            return Utils.tint_image(
                pygame.image.load_sized_svg(path, (scale, scale)).convert_alpha(),
                tint
            )



    
    @staticmethod
    def play_sfx(sound_file, volume=settings.VOLUME, start=0, channel=None):
        """
        Play a sound file.
        """
        if settings.SOUND_ON:
            sound = pygame.mixer.Sound(sound_file)
            sound.set_volume(volume)
            if channel is None:
                sound.play(start)
            else:
                # Get the channel object once and reuse it
                ch = pygame.mixer.Channel(channel)
                ch.stop()  # Stops any sound currently on this channel
                ch.play(sound)
                
    @staticmethod
    def lerp(start, end, start_range, end_range, value):
        """
        Linear interpolation between two values.
        """
        return start + (end - start) * ((value - start_range) / (end_range - start_range))
    
    
    @staticmethod
    def get_date():
        now = datetime.datetime.now()
        current_date = f"{now.day}.{now.month}"
        current_year = str(int(now.strftime("%Y")) + settings.YEARS_ADDED)
        date = f"{current_date}.{current_year}"
        return date


    @staticmethod
    def get_time():
        now = datetime.datetime.now()    
        current_time = now.strftime("%I:%M%p")
        return current_time
