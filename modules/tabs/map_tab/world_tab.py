import hashlib
import io
import json
import math
import os
import random
from threading import Lock, Thread
import requests
import pygame
from typing import Tuple, List, Dict, Optional
from pygame.math import Vector2
from PIL import Image

import settings
from util_functs import Utils




class BaseMap:
    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, 
                 map_image: pygame.Surface):
        self.screen = screen
        self.draw_space = draw_space
        self.map_image = map_image
        self.map_surface = map_image.copy()

        # Zoom configuration
        self.min_zoom = self._calculate_min_zoom()
        self.max_zoom = settings.MIN_MAP_ZOOM
        self.map_zoom = max(min(settings.INITIAL_MAP_ZOOM, self.max_zoom), self.min_zoom)

        # Navigation state
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = Vector2(self._calculate_initial_offset())
        self.directions = [
            (settings.MAP_MOVE_SPEED, 0),   # Right
            (0, settings.MAP_MOVE_SPEED),   # Down
            (0, -settings.MAP_MOVE_SPEED),  # Up
            (-settings.MAP_MOVE_SPEED, 0)   # Left
        ]
        
        self.is_initialized = True

    def _calculate_initial_offset(self) -> Vector2:
        """Calculate initial offset to center the map."""
        return Vector2(
            (self.zoomed_map_surface.get_width() - self.draw_space.width) / 2,
            (self.zoomed_map_surface.get_height() - self.draw_space.height) / 2
        )

    def _update_zoomed_surface(self) -> pygame.Surface:
        """Update zoomed surface using smooth scaling."""
        new_size = Vector2(self.map_surface.get_size()) * self.map_zoom
        return pygame.transform.smoothscale(self.map_surface, new_size.xy)

    def _calculate_min_zoom(self) -> float:
        """Calculate minimum zoom to fit image within draw space."""
        img_size = Vector2(self.map_surface.get_size())
        draw_size = Vector2(self.draw_space.size)
        return max(draw_size.x / img_size.x, draw_size.y / img_size.y)

    def clamp_offset(self):
        """Keep map offset within valid bounds."""
        zoomed_size = Vector2(self.zoomed_map_surface.get_size())
        draw_size = Vector2(self.draw_space.size)
        max_offset = zoomed_size - draw_size

        # Ensure map_offset is a Vector2
        if not isinstance(self.map_offset, Vector2):
            self.map_offset = Vector2(self.map_offset)

        # Clamp the offset
        for axis in [0, 1]:  # 0 for x, 1 for y
            if zoomed_size[axis] < draw_size[axis]:
                self.map_offset[axis] = (zoomed_size[axis] - draw_size[axis]) / 2
            else:
                self.map_offset[axis] = max(0, min(self.map_offset[axis], max_offset[axis]))

    def zoom(self, zoom_in: bool):
        """Zoom while maintaining view center."""
        old_zoom = self.map_zoom
        zoom_step = old_zoom * settings.MAP_ZOOM_SPEED
        new_zoom = old_zoom + zoom_step if zoom_in else old_zoom - zoom_step
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        if new_zoom == old_zoom:
            return

        # Calculate original center position
        view_center = Vector2(self.draw_space.center) - Vector2(self.draw_space.topleft)
        orig_center = (Vector2(self.map_offset) + view_center) / old_zoom

        # Update zoom state
        self.map_zoom = new_zoom
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = orig_center * new_zoom - view_center
        self.clamp_offset()

    def navigate(self, direction: int):
        """
        Move the map view in one of four directions.
        :param direction: 0: right, 1: down, 2: up, 3: left.
        """
        if 0 <= direction < 4:
            if not isinstance(self.map_offset, Vector2):
                self.map_offset = Vector2(self.map_offset)
            dx, dy = self.directions[direction]
            self.map_offset += Vector2(dx, dy)
            self.clamp_offset()


    def render(self):
        """Draw the visible portion of the map."""
        src_rect = pygame.Rect(*self.map_offset, *self.draw_space.size)
        src_rect.clamp(self.zoomed_map_surface.get_rect())
        self.screen.blit(self.zoomed_map_surface, self.draw_space.topleft, src_rect)


class WorldMap(BaseMap):
    """World map with toggleable markers."""
    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect):
        map_path = (settings.COMMONWEALTH_MAP_MARKERS if settings.SHOW_ALL_MARKERS 
                    else settings.COMMONWEALTH_MAP)
        map_image = Utils.tint_image(pygame.image.load(map_path).convert_alpha())
        super().__init__(screen, draw_space, map_image)


class RealMap(BaseMap):
    """Dynamic real-world map using OSM and Overpass API."""    

    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, 
                 api_zoom: int = 13):
        
        self.screen = screen
        self.lat, self.lon = settings.LATITUDE, settings.LONGITUDE
        self.api_zoom = api_zoom
        self.draw_space = draw_space
        self.icons = Utils.load_svgs_dict(settings.MAP_ICONS_BASE_FOLDER, settings.MAP_ICON_SIZE)

        self._cache_lock = Lock()
        self._places_cache_lock = Lock()
        self.rendered_map_lock = Lock()
        
        self.is_initialized = False
        Thread(target=self.init_map, daemon=True).start()


    def init_map(self):
        image = self._fetch_map_image()
        places = self._fetch_places(image)
        rendered_map = self._draw_markers(image, places)
        super().__init__(self.screen, self.draw_space, rendered_map)


    def _fetch_map_image(self) -> pygame.Surface:
        """Retrieve map image with caching."""

        # Try disk cache
        os.makedirs(settings.MAP_CACHE, exist_ok=True)
        filename = f"{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{settings.MAP_SIZE}.png"
        cache_path = os.path.join(settings.MAP_CACHE, filename)

        if os.path.exists(cache_path):
            map_img = pygame.image.load(cache_path).convert()
            return map_img


        # Fetch new image
        url = settings.get_static_map_url(settings.MAP_SIZE, settings.EXTRA_MAP_SIZE, settings.GEOAPIFY_API_KEY,
                                         self.lon, self.lat, self.api_zoom)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Map API failed: {e}") from e

        map_img = pygame.image.load(io.BytesIO(response.content)).convert()
        width, height = map_img.get_size()
        min_dimension = min(width, height)
        # Calculate the top-left coordinates for a centered crop.
        x = (width - min_dimension) // 2
        y = (height - min_dimension) // 2
        cropped_img = pygame.Surface((min_dimension, min_dimension)).convert()
        cropped_img.blit(map_img, (0, 0), (x, y, min_dimension, min_dimension))
        
        pygame.image.save(cropped_img, cache_path)
            
        return cropped_img



    def _fetch_places(self, map_img: pygame.Surface) -> List[dict]:
        """Fetch and filter POI data with caching."""
        radius = self._calculate_search_radius()
        os.makedirs(settings.MAP_PLACES_CACHE, exist_ok=True)
        cache_file = os.path.join(settings.MAP_PLACES_CACHE, f"{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{radius}.json")


        # Try disk cache
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                filtered_places = json.load(f)
            return filtered_places

        # Fetch new data
        query = settings.get_places_map_url(radius, self.lat, self.lon)
        
        try:
            response = requests.post(settings.OVERPASS_URL, data={'data': query}, timeout=25)
            response.raise_for_status()
        except requests.RequestException as e:
            return []

        raw_places = self._process_response_data(response.json())
        random.shuffle(raw_places)
        filtered_places = self._filter_places(raw_places, map_img)

        with open(cache_file, "w") as f:
            json.dump(filtered_places, f, indent=2)


        return filtered_places

    def _process_response_data(self, data: dict) -> List[dict]:
        """Process Overpass API response into place data."""
        places = []
        for element in data.get("elements", []):
            if coords := self._extract_coordinates(element):
                types = self._extract_types(element.get("tags", {}))
                places.append({"lat": coords[0], "lon": coords[1], "types": types})
        return places

    def _extract_coordinates(self, element: dict) -> Optional[Tuple[float, float]]:
        """Extract coordinates from API element."""
        if "lat" in element and "lon" in element:
            return element["lat"], element["lon"]
        if "center" in element:
            return element["center"]["lat"], element["center"]["lon"]
        return None

    def _extract_types(self, tags: dict) -> List[str]:
        """Extract place types from OSM tags."""
        # Get the valid types from settings.MAP_TYPE_PRIORITY (excluding the fallback "default")
        
        map_types = list(settings.MAP_TYPE_PRIORITY.keys())
        valid_types = set(map_types)
        types_found = set()
        
        # For these OSM tag keys, check if the tag's value is one of our valid types.
        for osm_key in settings.OSM_KEYS:
            tag_value = tags.get(osm_key)
            if tag_value in valid_types:
                types_found.add(tag_value)
        
        
        sorted_types = sorted(
            types_found, 
            key=lambda t: map_types.index(t) if t in map_types else len(map_types)
        )
        return sorted_types


    def _filter_places(self, raw_places: List[dict], map_img: pygame.Surface) -> List[dict]:
        """Filter places using dynamic radii based on icon size and priority."""
        # Sort by priority (highest first) to ensure they are placed first
        sorted_places = sorted(raw_places, 
            key=lambda x: self._get_type_priority(x["types"]), 
            reverse=True  # Process higher priority markers first
        )
        
        filtered = []
        occupied_positions = []  # Tracks placed markers' centers and radii
        type_counts = {t: 0 for t in settings.MAP_TYPE_PRIORITY}
        
        for place in sorted_places:
            # Get the primary type of the place (highest priority type)
            place_type = place["types"][0] if place["types"] else "default"

            # Skip if the type is not in the limits or the limit has been reached
            if place_type not in settings.MAP_TYPE_PRIORITY or \
            type_counts[place_type] >= settings.MAP_TYPE_PRIORITY[place_type]:
                continue

            icon = self._get_icon(place["types"])
            if icon is None:
                continue

            icon_size = Vector2(icon.get_size())
            map_size = Vector2(map_img.get_size())
            screen_pos = self._get_marker_screen_position(place, icon_size, map_size)
            icon_center = screen_pos + icon_size / 2

            # Ensure marker is within map bounds
            if not (0 <= screen_pos.x <= map_size.x - icon_size.x and
                    0 <= screen_pos.y <= map_size.y - icon_size.y):
                continue

            # Calculate radius as half-diagonal of the icon
            radius = (icon_size / 2).length()

            # Check against existing markers using icon-based radii
            too_close = any(
                (icon_center - existing['center']).length() < (radius + existing['radius'])
                for existing in occupied_positions
            )
            if too_close:
                continue

            # Add the place to the filtered list
            filtered.append(place)
            occupied_positions.append({'center': icon_center, 'radius': radius})
            type_counts[place_type] += 1  # Increment the count for this type

        return filtered
    
    def _get_marker_screen_position(self, place: dict, icon_size: Vector2, map_size: Vector2) -> Vector2:
        marker_pos = Vector2(self.lat_lon_to_pixel(place["lat"], place["lon"], self.api_zoom))
        center_pixel = Vector2(self.lat_lon_to_pixel(self.lat, self.lon, self.api_zoom))
        map_center = map_size / 2
        return marker_pos - center_pixel + map_center - icon_size / 2



    def _get_type_priority(self, types: List[str]) -> int:
        """Get the highest priority score from a place's types."""
        map_types = list(settings.MAP_TYPE_PRIORITY.keys())
        for t in map_types:
            if t in types:
                return len(map_types) - map_types.index(t)
        return 0  # default priority



    def _calculate_search_radius(self) -> int:
        """Convert zoom level to search radius in meters."""
        meters_per_pixel = (156543.03 * math.cos(math.radians(self.lat))) / (2 ** self.api_zoom)
        return int((settings.MAP_SIZE * meters_per_pixel * math.sqrt(2)) / 2)


    def _draw_markers(self, map_image: pygame.Surface, places) -> pygame.Surface:
        """Draw markers on the map surface."""
        map_surface = Utils.tint_image(map_image.copy())
        map_size = Vector2(map_surface.get_size())

        for place in places:
            icon = self._get_icon(place["types"])
            if icon is None:
                continue
            icon_size = Vector2(icon.get_size())
            screen_pos = self._get_marker_screen_position(place, icon_size, map_size)

            # Check if the marker is within the map bounds
            if (0 <= screen_pos.x <= map_size.x - icon_size.x and
                0 <= screen_pos.y <= map_size.y - icon_size.y):
                map_surface.blit(icon, screen_pos.xy)

        return map_surface

    @staticmethod
    def lat_lon_to_pixel(lat: float, lon: float, zoom: int) -> Tuple[float, float]:
        """Convert geographic coordinates to pixel coordinates with scale factor."""
        lat_rad = math.radians(lat)
        n = 2 ** zoom
        tile_size = settings.MAP_TILE_SIZE
        x = (lon + 180) / 360 * n * tile_size
        y = (1 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2 * n * tile_size
        return x, y

    def _get_icon(self, types: List[str]) -> pygame.Surface:
        for t in types:
            if t in self.icons:
                return self.icons[t]
        # Return a default icon if available
        return self.icons.get("default", None)