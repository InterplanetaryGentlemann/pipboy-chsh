import pygame
import settings
from threading import Thread
from data_models import IconConfig  # Changed import
from typing import Dict, List
from util_functs import Utils


class StatusTab:    

    def __init__(self, screen, tab_instance, draw_space: pygame.Rect):
        self.screen = screen
        self.tab_instance = tab_instance
        self.draw_space = draw_space
        self.vaultboy_thread = None
        self.vaultboy_thread_running = False
        self.small_font = pygame.font.Font(settings.ROBOTO_CONDENSED_BOLD_PATH, 12)
        
        # Initialize components
        self._init_vault_boy()
        self._init_player_name()
        
        self.setup_limb_damage(settings.DEFAULT_LIMB_DAMAGE)

        self.setup_stats_display(settings.DEFAULT_STATS_DAMAGE, settings.DEFAULT_STATS_ARMOR)

    def _init_vault_boy(self):
        """Initialize vault boy animation components"""
        self.vaultboy_legs = Utils.load_images(settings.STAT_TAB_LEGS_BASE_FOLDER)
        self.vaultboy_heads = Utils.load_images(settings.STAT_TAB_HEAD_BASE_FOLDER)
        
        self.vaultboy_legs_index = 0
        self.vaultboy_heads_index = 0
        
        vaultboy_scale = settings.SCREEN_HEIGHT / settings.VAULTBOY_SCALE 
        self._setup_vault_boy_positions(vaultboy_scale)
        
        # Create animation step sequence: 0->3, 3->0
        self.vaultboy_steps = (0.0, 0.0), (0.5, 1.8), (0.8, 3.0), (1.0, 1.8), (1.5, 0.1), (1.1, 1.3), (1.0, 3.0), (0.7, 2.3)
        
    def _init_player_name(self):
        self.player_surface = self.small_font.render(settings.PLAYER_NAME, True, settings.PIP_BOY_LIGHT)
 

    def _setup_vault_boy_positions(self, scale: float):
        """Set up vault boy animation positions and scaling"""
        self.scaled_legs = [Utils.scale_image(img, scale) for img in self.vaultboy_legs]
        self.scaled_heads = [Utils.scale_image(img, scale) for img in self.vaultboy_heads]

        self.vaultboy_surface = pygame.Surface(
            (self.draw_space.width, self.draw_space.height), 
            pygame.SRCALPHA
        )
        
        # Calculate centered positions
        self.positions = {}
        for part in ("legs", "head"):
            images = self.scaled_legs if part == 'legs' else self.scaled_heads
            x_center = (self.vaultboy_surface.get_width() // 2 - 
                       images[0].get_width() // 2)
            y_pos = self.draw_space.top + (settings.VAULT_BOY_OFFSET if part == 'legs' else -(settings.VAULT_BOY_OFFSET * 1.5))
            self.positions[part] = (x_center, y_pos)

        # Center animation surface
        self.screen_position = self.vaultboy_surface.get_rect(
            center=(self.draw_space.x + self.draw_space.width // 2,
                   self.draw_space.y + self.draw_space.height // 2)
        )
    def _calculate_stats_width(self, big_rect_size: int, small_rect_size: int, 
                                num_damage_icons: int, num_armor_icons: int) -> int:
            """Calculate total width needed for stats display"""
            # Calculate margins
            total_margins = (
                settings.DAMAGE_ARMOUR_MARGIN_BIG +  # Space between damage and armor sections
                (num_damage_icons * settings.DAMAGE_ARMOUR_MARGIN_SMALL) +  # Spaces between damage icons
                (num_armor_icons * settings.DAMAGE_ARMOUR_MARGIN_SMALL)     # Spaces between armor icons
            )
            
            # Calculate icon spaces
            total_icon_space = (
                (big_rect_size * 2) +  # Space for big damage and armor icons
                (num_damage_icons * small_rect_size) +  # Space for small damage icons
                (num_armor_icons * small_rect_size)     # Space for small armor icons
            )
        
            return total_icon_space + total_margins

    def _render_stats_icons(self, icons: Dict, big_rect_size: int, small_rect_size: int):
        """Render damage and armor icons with their values"""
        margin = 0
        
        # Helper function for icon rendering
        def render_icon_section(icon_type: str):
            nonlocal margin
            
            # Render big icon
            big_icon = Utils.scale_image(
                pygame.image.load(icons[icon_type]['big']).convert_alpha(),
                settings.DAMAGE_ARMOUR_ICON_BIG_SIZE
            )
            
            big_icon = Utils.tint_image(big_icon)
            
            # Draw background rectangle
            pygame.draw.rect(
                self.stats_surface,
                settings.PIP_BOY_DARK,
                (margin, 0, big_rect_size, big_rect_size)
            )
            
            # Center and draw big icon
            self.stats_surface.blit(
                big_icon,
                (margin + (big_rect_size // 2 - big_icon.get_width() // 2),
                 big_rect_size // 2 - big_icon.get_height() // 2)
            )
            margin += big_rect_size
            
            # Render small icons
            for small_icon_path, value in zip(icons[icon_type]['small'], icons[icon_type]['values']):
                margin += settings.DAMAGE_ARMOUR_MARGIN_SMALL
                
                # Scale and load small icon
                small_icon = Utils.scale_image(
                    pygame.image.load(small_icon_path).convert_alpha(),
                    settings.DAMAGE_ARMOUR_ICON_SMALL_SIZE
                )
                
                small_icon = Utils.tint_image(small_icon)
                
                # Draw background rectangle
                pygame.draw.rect(
                    self.stats_surface,
                    settings.PIP_BOY_DARK,
                    (margin, 0, small_rect_size, big_rect_size)
                )
                
                # Center and draw small icon
                self.stats_surface.blit(
                    small_icon,
                    (margin + (small_rect_size // 2 - small_icon.get_width() // 2),
                     big_rect_size // 4 - small_icon.get_height() // 2)
                )
                
                # Render value text
                text_surface = self.small_font.render(str(value), True, settings.PIP_BOY_LIGHT)
                self.stats_surface.blit(
                    text_surface,
                    (margin + (small_rect_size // 2 - text_surface.get_width() // 2),
                     big_rect_size - text_surface.get_height() - (settings.DAMAGE_ARMOUR_ICON_MARGIN // 4))
                )
                
                margin += small_rect_size
        
        # Render damage section
        render_icon_section('damage')
        
        # Add margin between damage and armor sections
        margin += settings.DAMAGE_ARMOUR_MARGIN_BIG
        
        # Render armor section
        render_icon_section('armor')
        
    def setup_limb_damage(self, limb_damages: List[int]):
        """Initialize limb damage display with given damage values"""
        if len(limb_damages) != len(settings.LIMB_POSITIONS):
            raise ValueError("Number of damage values must match number of limb positions")
            
        width = settings.LIMB_DAMAGE_WIDTH
        height = width // 4
        center_x = self.draw_space.width // 2
        
        self.limb_damage_surface = pygame.Surface(
            (self.draw_space.width, self.draw_space.height), 
            pygame.SRCALPHA
        ).convert_alpha()
        
        for damage, pos in zip(limb_damages, settings.LIMB_POSITIONS):
            # Calculate rectangle positions
            rect = pygame.Rect(
                center_x - width // 2 + pos.x_offset,
                pos.y_position,
                width,
                height
            )
            
            # Draw damage fill
            damage_rect = rect.copy()
            damage_rect.width = int(damage_rect.width * (damage / 100))
            pygame.draw.rect(self.limb_damage_surface, settings.PIP_BOY_LIGHT, damage_rect)
            
            # Draw outline
            pygame.draw.rect(self.limb_damage_surface, settings.PIP_BOY_LIGHT, rect, 1)

    def setup_stats_display(self, damage_icons: List[IconConfig], armor_icons: List[IconConfig]):
        """Setup damage and armor statistics display"""
        icons = {
            'damage': {
                'big': settings.STAT_TAB_GUN,
                'small': [icon.path for icon in damage_icons],
                'values': [icon.value for icon in damage_icons]
            },
            'armor': {
                'big': settings.STAT_TAB_ARMOUR,
                'small': [icon.path for icon in armor_icons],
                'values': [icon.value for icon in armor_icons]
            }
        }
        
        self._create_stats_surface(icons)

    def _create_stats_surface(self, icons):
        """Create the surface for displaying damage and armor stats"""
        # Calculate dimensions        
        big_rect_size = self.draw_space.width // settings.DAMAGE_ARMOUR_ICON_ABSOLUTE_SIZE
        small_rect_size = big_rect_size // 2
        
        # Calculate total width
        total_width = self._calculate_stats_width(
            big_rect_size, small_rect_size,
            len(icons['damage']['small']), len(icons['armor']['small'])
        )
        
        self.stats_surface = pygame.Surface((total_width, big_rect_size), pygame.SRCALPHA).convert_alpha()
        self._render_stats_icons(icons, big_rect_size, small_rect_size)




    def update_vaultboy(self):
        """Update vault boy animation frame"""
        while self.vaultboy_thread_running:
            
            step_offset_y = self.vaultboy_steps[self.vaultboy_legs_index][1]
            step_offset_x = self.vaultboy_steps[self.vaultboy_legs_index][0]
            self.vaultboy_surface.fill((0, 0, 0, 0))
            
            for part, pos in self.positions.items():
                images = self.scaled_legs if part == 'legs' else self.scaled_heads
                index = self.vaultboy_legs_index if part == 'legs' else self.vaultboy_heads_index
                
                self.vaultboy_surface.blit(
                    images[index],
                    (pos[0] + step_offset_x, pos[1] + step_offset_y)
                )
            self.vaultboy_legs_index = (self.vaultboy_legs_index + 1) % len(self.scaled_legs)
            pygame.time.wait(settings.SPEED * 150)
    
    def handle_threads(self, tab_selected: bool):
        """ Handle the threads"""
        if tab_selected and not self.vaultboy_thread_running:
            self.vaultboy_thread_running = True
            self.vaultboy_thread = Thread(target=self.update_vaultboy, daemon=True)
            self.vaultboy_thread.start()
        elif not tab_selected and self.vaultboy_thread_running:
            self.vaultboy_thread_running = False
            self.vaultboy_thread.join()
            

    def render(self):
        """Render all components to the screen"""
        self.render_vaultboy()
        self.render_player_name()
        if hasattr(self, 'stats_surface'):
            self.render_stats()
        if hasattr(self, 'limb_damage_surface'):
            self.render_limb_damage()

    def render_vaultboy(self):
        self.screen.blit(self.vaultboy_surface, self.screen_position)

    def render_player_name(self):
        player_pos = (
            self.draw_space.x + self.draw_space.width // 2 - self.player_surface.get_width() // 2,
            self.draw_space.y + self.draw_space.height - self.player_surface.get_height()
        )
        self.screen.blit(self.player_surface, player_pos)

    def render_stats(self):
        stats_pos = (
            self.draw_space.x + self.draw_space.width // 2 - self.stats_surface.get_width() // 2,
            self.draw_space.y + self.draw_space.height - (self.stats_surface.get_height() * 1.7)
        )
        self.screen.blit(self.stats_surface, stats_pos)

    def render_limb_damage(self):
        self.screen.blit(self.limb_damage_surface, self.draw_space)