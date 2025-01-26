import pygame
from boot import Boot
import threading
import settings
import overlays
from tab_manager import TabManager



class PipBoy:
    def __init__(self, screen, clock):
        """
        Initialize the PipBoy object.
        """
        self.screen = screen
        self.clock = clock
        self.states = iter(["boot", "main"])
        self.current_sequence = "main"   
        self.hum_started = False
        
        self.tab_manager = TabManager(self.screen)

        if settings.BOOT_SCREEN:
            self.current_sequence = "boot"
            self.boot_instance = Boot(self.screen)
            self.boot_thread = threading.Thread(target=self.boot_instance.run)
            self.boot_thread.daemon = True
            self.boot_thread.start()


        if settings.SHOW_CRT:
            self.overlay_instance = overlays.Overlays(self.screen)
            self.crt_thread = threading.Thread(target=self.overlay_instance.crt_effect)
            self.crt_thread.daemon = True
            self.crt_thread.start()



    def play_hum(self, sound, volume, loops):
        pygame.mixer.music.load(sound)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(loops)

    
    def render(self):
        
        self.screen.fill(settings.BACKGROUND)
        
        match self.current_sequence:
            case "boot":
                self.boot_instance.render()
            case "main":
                self.tab_manager.render()
            case _:
                pass
        self.overlay_instance.render()
        
        pygame.display.flip()
        

    def run(self):
        # Main loop
        while True:    
            match self.current_sequence:
                case "boot":
                    self.boot_instance.start()
                    self.boot_thread.join()
                    # del self.boot_instance
                    self.current_sequence = next(self.states)
                case "main":
                    if not self.hum_started:
                        if settings.SOUND_ON:
                            self.play_hum(settings.BACKGROUND_HUM, settings.VOLUME / 10, -1)        
                    pass
                case _:
                    pass

            pygame.time.wait(settings.SPEED)




