import io
import json
import math
import os
import random
from threading import Lock
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
    _cache: Dict[tuple, pygame.Surface] = {}
    _places_cache: Dict[str, list] = {}
    


    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, 
                 api_zoom: int = 13):
        self.lat, self.lon = settings.LATITUDE, settings.LONGITUDE
        self.api_zoom = api_zoom
        self.draw_space = draw_space
        self.icons = Utils.load_svgs_dict(settings.MAP_ICONS_BASE_FOLDER, settings.MAP_ICON_SIZE)

        self._cache_lock = Lock()
        self._places_cache_lock = Lock()
        # Initialize map components
        self.map_image = self._fetch_map_image()
        self.places = self._fetch_places()
        self.rendered_map = self._draw_markers()
        
        super().__init__(screen, draw_space, self.rendered_map)

    def _fetch_map_image(self) -> pygame.Surface:
        """Retrieve map image with caching."""
        cache_key = (round(self.lat, 6), round(self.lon, 6), self.api_zoom, settings.MAP_SIZE)
        
        if cached := self._cache.get(cache_key):
            return cached.copy()

        # Try disk cache
        os.makedirs(settings.MAP_CACHE, exist_ok=True)
        filename = f"{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{settings.MAP_SIZE}.png"
        cache_path = os.path.join(settings.MAP_CACHE, filename)

        if os.path.exists(cache_path):
            img = pygame.image.load(cache_path).convert()
            with self._cache_lock:
                self._cache[cache_key] = img
            return Utils.tint_image(img)

        # Fetch new image
        url = settings.get_static_map_url(settings.MAP_SIZE, settings.EXTRA_MAP_SIZE, settings.GEOAPIFY_API_KEY,
                                         self.lon, self.lat, self.api_zoom)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.RequestException as e:
            raise ConnectionError(f"Map API failed: {e}") from e

        img = pygame.image.load(io.BytesIO(response.content)).convert()
        width, height = img.get_size()
        min_dimension = min(width, height)
        # Calculate the top-left coordinates for a centered crop.
        x = (width - min_dimension) // 2
        y = (height - min_dimension) // 2
        cropped_img = pygame.Surface((min_dimension, min_dimension)).convert()
        cropped_img.blit(img, (0, 0), (x, y, min_dimension, min_dimension))
        
        pygame.image.save(cropped_img, cache_path)
        with self._cache_lock:
            self._cache[cache_key] = cropped_img
        return Utils.tint_image(cropped_img)

    def _fetch_places(self) -> List[dict]:
        """Fetch and filter POI data with caching."""
        radius = self._calculate_search_radius()
        cache_key = f"{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{radius}"
        cache_file = f"{settings.MAP_PLACES_CACHE}.{cache_key}.json"

        if cached := self._places_cache.get(cache_key):
            return cached

        # Try disk cache
        if os.path.exists(cache_file):
            with open(cache_file, "r") as f:
                data = json.load(f)
                filtered_places = data.get(cache_key, [])
                with self._places_cache_lock:
                    self._places_cache[cache_key] = filtered_places  # Update in-memory cache
                return filtered_places


        # Fetch new data
        query = settings.get_places_map_url(radius, self.lat, self.lon)
        
        try:
            response = requests.post(settings.OVERPASS_URL, data={'data': query}, timeout=15)
            response.raise_for_status()
        except requests.RequestException as e:
            return []

        raw_places = self._process_response_data(response.json())
        filtered_places = self._filter_places(raw_places)
        # filtered_places = raw_places
        
        # Update cache

        with open(cache_file, "w") as f:
            json.dump({cache_key: filtered_places}, f, indent=2)

        with self._places_cache_lock:
            self._places_cache[cache_key] = filtered_places

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
        # Get the valid types from MAP_NODE_TYPE_LIMITS (excluding the fallback "default")
        valid_types = set(settings.MAP_NODE_TYPE_LIMITS.keys())
        types_found = set()
        
        # For these OSM tag keys, check if the tag's value is one of our valid types.
        for osm_key in ["place", "water", "historic", "landuse", "military"]:
            tag_value = tags.get(osm_key)
            if tag_value in valid_types:
                types_found.add(tag_value)
        
        
        sorted_types = sorted(
            types_found, 
            key=lambda t: settings.MAP_TYPE_PRIORITY.index(t) if t in settings.MAP_TYPE_PRIORITY else len(settings.MAP_TYPE_PRIORITY)
        )
        return sorted_types

    def _filter_places(self, raw_places: List[dict]) -> List[dict]:
        """Filter places with priority-based selection when conflicts occur,
        and remove any markers that would be drawn outside the visible map."""
        # Sort places by priority (highest first)
        sorted_places = sorted(raw_places, 
            key=lambda x: self._get_type_priority(x["types"]), 
            reverse=False
        )
        # # shuffel the places of each type
        # for place_type in settings.MAP_NODE_TYPE_LIMITS:
        #     type_places = [p for p in sorted_places if place_type in p["types"]]
        #     random.shuffle(type_places)
        #     sorted_places = [p for p in sorted_places if p not in type_places] + type_places
        
        # Setup values for bounds checking.
        # Use the fetched map image as the reference (the full image that markers are drawn on).
        map_surface = self.map_image
        map_size = Vector2(map_surface.get_size())
        # Compute the pixel coordinates for the center (the current focal point of the map)
        center_pixel = Vector2(self.lat_lon_to_pixel(self.lat, self.lon, self.api_zoom))
        map_center = map_size / 2

        filtered = []
        type_counts = {k: 0 for k in settings.MAP_NODE_TYPE_LIMITS}

        for place in sorted_places:
            try:
                place_type = place["types"][0]
            except IndexError:
                continue
            
            # Enforce the type limit.
            if type_counts[place_type] >= settings.MAP_NODE_TYPE_LIMITS[place_type]:
                continue
                
            # Skip if the place is too close to an already-selected higher priority marker.
            # if self._is_too_close_to_higher_priority(place, filtered):
            #     continue

            # Determine if the marker for this place would be drawn within the map bounds.
            icon = self._get_icon(place["types"])
            if icon is None:
                continue  # or you might choose to include it if you want a fallback behavior

            icon_size = Vector2(icon.get_size())
            # Convert the place's geographic coordinates to a pixel coordinate on the map.
            marker_pos = Vector2(self.lat_lon_to_pixel(place["lat"], place["lon"], self.api_zoom))
            # Calculate where the icon would be drawn relative to the map image.
            screen_pos = marker_pos - center_pixel + map_center - icon_size / 2

            # Only include the place if its marker is fully within the map surface.
            if not (0 <= screen_pos.x <= map_size.x - icon_size.x and
                    0 <= screen_pos.y <= map_size.y - icon_size.y):
                continue
                
            # Passed all checks: add this place.
            filtered.append(place)
            type_counts[place_type] += 1

        return filtered

    def _get_type_priority(self, types: List[str]) -> int:
        """Get the highest priority score from a place's types."""
        for t in settings.MAP_TYPE_PRIORITY:
            if t in types:
                return len(settings.MAP_TYPE_PRIORITY) - settings.MAP_TYPE_PRIORITY.index(t)
        return 0  # default priority



    def _haversine(self, coords1: Tuple[float, float], coords2: Tuple[float, float]) -> float:
            R = 6371000  # Earth radius in meters
            phi1 = math.radians(coords1[0])
            phi2 = math.radians(coords2[0])
            delta_phi = math.radians(coords2[0] - coords1[0])
            delta_lambda = math.radians(coords2[1] - coords1[1])
            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

    def _is_too_close_to_higher_priority(self, new_place: dict, existing_places: List[dict]) -> bool:
        """Check if place is too close to existing places of equal or higher priority."""
        new_priority = self._get_type_priority(new_place["types"])
        new_coords = (new_place["lat"], new_place["lon"])
        
        for existing in existing_places:
            existing_priority = self._get_type_priority(existing["types"])
            
            # Only compare with existing places of equal or higher priority
            if existing_priority >= new_priority:
                distance = self._haversine(new_coords, (existing["lat"], existing["lon"]))
                min_distance = settings.MAP_MIN_NODE_DISTANCE * random.uniform(0.5, 1.5)
                
                if distance < min_distance:
                    return True
                    
        return False

    def _calculate_search_radius(self) -> int:
        """Convert zoom level to search radius in meters."""
        meters_per_pixel = (156543.03 * math.cos(math.radians(self.lat))) / (2 ** self.api_zoom)
        return int((settings.MAP_SIZE * meters_per_pixel * math.sqrt(2)) / 2)


    def _draw_markers(self) -> pygame.Surface:
        """Draw markers on the map surface."""
        map_surface = self.map_image.copy()
        center_pixel = self.lat_lon_to_pixel(self.lat, self.lon, self.api_zoom)
        map_center = Vector2(map_surface.get_size()) / 2
        map_size = Vector2(map_surface.get_size())

        for place in self.places:
            icon = self._get_icon(place["types"])
            if icon is None:
                continue
            icon_size = Vector2(icon.get_size())
            marker_pos = Vector2(self.lat_lon_to_pixel(place["lat"], place["lon"], self.api_zoom))
            screen_pos = marker_pos - Vector2(center_pixel) + map_center - icon_size / 2

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
                print(t)
                return self.icons[t]
        # Return a default icon if available
        return self.icons.get("default", None)