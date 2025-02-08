import io
import requests
import pygame
import settings
from util_functs import Utils


class BaseMap:
    """
    A base class that implements common map functionality:
    panning, zooming, and rendering the visible area.
    """
    def __init__(self, screen, draw_space, map_image, initial_zoom=0.5):
        """
        :param screen: The pygame display surface.
        :param draw_space: A rect-like object (with .width, .height, .topleft, .size)
                           that defines the area where the map is drawn.
        :param map_image: A pygame.Surface containing the base map image.
        :param initial_zoom: Initial zoom scaling factor.
        """
        self.screen = screen
        self.draw_space = draw_space
        self.map_image = map_image  # Base image loaded from file or API.
        self.map_surface = self.map_image.copy()

        self.map_zoom = initial_zoom
        self.zoomed_map_surface = self._update_zoomed_surface()

        # Center the initial view on the map image.
        self.map_offset = (
            (self.zoomed_map_surface.get_width() - self.draw_space.width) // 2,
            (self.zoomed_map_surface.get_height() - self.draw_space.height) // 2
        )

        # Define movement directions (right, down, up, left)
        self.directions = [
            (settings.MAP_MOVE_SPEED, 0),   # Right
            (0, settings.MAP_MOVE_SPEED),   # Down
            (0, -settings.MAP_MOVE_SPEED),  # Up
            (-settings.MAP_MOVE_SPEED, 0)   # Left
        ]

    def _update_zoomed_surface(self):
        """Update the zoomed surface based on the current zoom factor."""
        orig_width, orig_height = self.map_surface.get_size()
        new_width = int(orig_width * self.map_zoom)
        new_height = int(orig_height * self.map_zoom)
        return pygame.transform.smoothscale(self.map_surface, (new_width, new_height))

    def clamp_offset(self):
        """
        Clamp (or center) the map offset so that the drawn area does not exceed
        the bounds of the zoomed image.
        """
        zoomed_width, zoomed_height = self.zoomed_map_surface.get_size()
        draw_width, draw_height = self.draw_space.width, self.draw_space.height

        # Horizontal clamping or centering.
        if zoomed_width <= draw_width:
            new_offset_x = (zoomed_width - draw_width) / 2
        else:
            max_offset_x = zoomed_width - draw_width
            new_offset_x = max(0, min(self.map_offset[0], max_offset_x))

        # Vertical clamping or centering.
        if zoomed_height <= draw_height:
            new_offset_y = (zoomed_height - draw_height) / 2
        else:
            max_offset_y = zoomed_height - draw_height
            new_offset_y = max(0, min(self.map_offset[1], max_offset_y))

        self.map_offset = (new_offset_x, new_offset_y)

    def zoom(self, zoom_in: bool):
        """
        Adjust the zoom level while keeping the current view center in the same
        location relative to the original map.
        :param zoom_in: If True, zoom in (i.e. increase scale); otherwise zoom out.
        """
        old_zoom = self.map_zoom
        # Adjust zoom using a constant speed from settings.
        new_zoom = self.map_zoom + (settings.MAP_ZOOM_SPEED if zoom_in else -settings.MAP_ZOOM_SPEED)
        new_zoom = max(settings.MIN_MAP_ZOOM, min(1, new_zoom))

        if new_zoom != old_zoom:
            # Determine the current view center.
            view_center = (self.draw_space.width / 2, self.draw_space.height / 2)
            # Get the center in the original image coordinates.
            center_in_original = (
                (self.map_offset[0] + view_center[0]) / old_zoom,
                (self.map_offset[1] + view_center[1]) / old_zoom
            )

            # Update the zoom level and regenerate the zoomed map surface.
            self.map_zoom = new_zoom
            self.zoomed_map_surface = self._update_zoomed_surface()
            # Recalculate offset to keep the center fixed.
            new_offset = (
                center_in_original[0] * new_zoom - view_center[0],
                center_in_original[1] * new_zoom - view_center[1]
            )
            self.map_offset = new_offset
            self.clamp_offset()

    def navigate(self, direction: int):
        """
        Move the map view in one of four directions.
        :param direction: 0: right, 1: down, 2: up, 3: left.
        """
        if 0 <= direction < 4:
            dx, dy = self.directions[direction]
            self.map_offset = (self.map_offset[0] + dx, self.map_offset[1] + dy)
            self.clamp_offset()

    def render(self):
        """
        Render the visible portion of the map to the screen.
        """
        src_rect = pygame.Rect(*self.map_offset, *self.draw_space.size)
        src_rect.clamp(self.zoomed_map_surface.get_rect())
        self.screen.blit(self.zoomed_map_surface, self.draw_space.topleft, area=src_rect)


class WorldMap(BaseMap):
    """
    A map that uses a pre-rendered fake world map image.
    This replicates the behavior of your original WorldTab code.
    """
    def __init__(self, screen, draw_space, map_image, initial_zoom=0.5):
        # Choose the appropriate image path based on whether markers should be shown.
        map_path = settings.COMMONWEALTH_MAP if not settings.SHOW_ALL_MARKERS else settings.COMMONWEALTH_MAP_MARKERS
        # Load the fake world map image from a file.
        map_image = pygame.image.load(map_path)
        map_image = Utils.tint_image(map_image)
        super().__init__(screen, draw_space, map_image, initial_zoom)



class RealMap(BaseMap):
    """
    A map that loads a 'real' map image of the current (or specified) location
    using an online static map service.
    """
    def __init__(self, screen, draw_space, lat=None, lon=None, api_zoom=13, initial_zoom=0.5):
        """
        :param lat: Latitude for the map center (if None, use current location).
        :param lon: Longitude for the map center (if None, use current location).
        :param api_zoom: Zoom level for the static map API (typically an integer, e.g., 13).
        :param initial_zoom: Initial scaling factor used for internal panning/zooming.
        """
        if lat is None or lon is None:
            lat, lon = self.get_current_location()
        self.lat = lat
        self.lon = lon
        self.api_zoom = api_zoom

        # Fetch the map image from an online service.
        map_image = self.fetch_map_image(lat, lon, api_zoom, draw_space.size)
        # Optionally, you could tint or process the image as in your original code:
        # map_image = Utils.tint_image(map_image)
        super().__init__(screen, draw_space, map_image, initial_zoom)

    def get_current_location(self):
        """
        Get the current location.
        In a real application, this could use a geolocation API.
        Here, we return a default location (e.g., New York City).
        """
        return 40.7128, -74.0060

    def fetch_map_image(self, lat, lon, zoom, size):
        """
        Fetch a static map image from an online service (here using OpenStreetMap).
        :param lat: Latitude of the map center.
        :param lon: Longitude of the map center.
        :param zoom: API zoom level.
        :param size: A tuple (width, height) defining the requested image size.
        :return: A pygame.Surface with the map image.
        """
        # Construct the URL for a static map from OpenStreetMap.
        # (For more options, consult the service’s documentation.)
        url = (
            f"http://staticmap.openstreetmap.de/staticmap.php?"
            f"center={lat},{lon}&zoom={zoom}&size={size[0]}x{size[1]}&maptype=mapnik"
        )
        response = requests.get(url)
        if response.status_code == 200:
            image_bytes = io.BytesIO(response.content)
            map_image = pygame.image.load(image_bytes)
            return map_image.convert()  # convert for faster blitting
        else:
            raise Exception(f"Failed to fetch map image. Status code: {response.status_code}")
