import io
import json
import math
import os
import random
import requests
import pygame
import settings
from util_functs import Utils
from PIL import Image



class BaseMap:
    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, map_image: pygame.Surface, initial_zoom: float = 0.5):
        """
        Initialize the base map handler.
        
        :param screen: Pygame display surface.
        :param draw_space: Rect defining the map's drawing area.
        :param map_image: Surface containing the map image.
        :param initial_zoom: Initial zoom factor (clamped between min and max zoom).
        """
        self.screen = screen
        self.draw_space = draw_space
        self.map_image = map_image
        self.map_surface = self.map_image.copy()

        # Calculate zoom constraints and set initial zoom
        self.min_zoom = self._calculate_min_zoom()
        self.max_zoom = settings.MIN_MAP_ZOOM
        self.map_zoom = settings.INITIAL_MAP_ZOOM
        
        self.zoomed_map_surface = self._update_zoomed_surface()
        self.map_offset = self._calculate_initial_offset()

        # Define movement directions (right, down, up, left)
        self.directions = [
            (settings.MAP_MOVE_SPEED, 0),   # Right
            (0, settings.MAP_MOVE_SPEED),   # Down
            (0, -settings.MAP_MOVE_SPEED),  # Up
            (-settings.MAP_MOVE_SPEED, 0)   # Left
        ]

    def _calculate_initial_offset(self) -> tuple[float, float]:
        """Calculate initial offset to center the map."""
        return (
            (self.zoomed_map_surface.get_width() - self.draw_space.width) / 2,
            (self.zoomed_map_surface.get_height() - self.draw_space.height) / 2
        )

    def _update_zoomed_surface(self) -> pygame.Surface:
        """Update the zoomed surface based on current zoom level."""
        new_size = (int(self.map_surface.get_width() * self.map_zoom),
                    int(self.map_surface.get_height() * self.map_zoom))
        return pygame.transform.smoothscale(self.map_surface, new_size)

    def _calculate_min_zoom(self) -> float:
        """Calculate minimum zoom to fit image within draw space."""
        img_w, img_h = self.map_surface.get_size()
        draw_w, draw_h = self.draw_space.size
        return max(draw_w / img_w, draw_h / img_h)


    def clamp_offset(self):
        """Ensure map stays within bounds during panning."""
        zoomed_w, zoomed_h = self.zoomed_map_surface.get_size()
        draw_w, draw_h = self.draw_space.size

        # Horizontal clamping
        max_x = max(zoomed_w - draw_w, 0)
        new_x = max(0, min(self.map_offset[0], max_x)) if zoomed_w > draw_w else (zoomed_w - draw_w) / 2

        # Vertical clamping
        max_y = max(zoomed_h - draw_h, 0)
        new_y = max(0, min(self.map_offset[1], max_y)) if zoomed_h > draw_h else (zoomed_h - draw_h) / 2
        

        self.map_offset = (new_x, new_y)

    def zoom(self, zoom_in: bool):
        """Zoom while maintaining view center."""
        old_zoom = self.map_zoom
        zoom_step = old_zoom * settings.MAP_ZOOM_SPEED
        new_zoom = old_zoom + (zoom_step if zoom_in else -zoom_step)
        new_zoom = max(self.min_zoom, min(self.max_zoom, new_zoom))

        if new_zoom != old_zoom:
            # Calculate view center in original coordinates
            view_center = (self.draw_space.width / 2, self.draw_space.height / 2)
            orig_x = (self.map_offset[0] + view_center[0]) / old_zoom
            orig_y = (self.map_offset[1] + view_center[1]) / old_zoom

            # Update zoom and recalculate offset
            self.map_zoom = new_zoom
            self.zoomed_map_surface = self._update_zoomed_surface()
            new_offset = (
                orig_x * new_zoom - view_center[0],
                orig_y * new_zoom - view_center[1]
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
        """Draw the visible portion of the map."""
        src_rect = pygame.Rect(*self.map_offset, *self.draw_space.size)
        src_rect.clamp(self.zoomed_map_surface.get_rect())
        self.screen.blit(self.zoomed_map_surface, self.draw_space.topleft, src_rect)


class WorldMap(BaseMap):
    """Custom world map with markers toggle."""
    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, initial_zoom: float = 0.5):
        map_path = (settings.COMMONWEALTH_MAP_MARKERS if settings.SHOW_ALL_MARKERS 
                    else settings.COMMONWEALTH_MAP)
        map_image = pygame.image.load(map_path).convert_alpha()
        map_image = Utils.tint_image(map_image)
        super().__init__(screen, draw_space, map_image, initial_zoom)


class RealMap(BaseMap):
    """Dynamic real-world map using OSM static map and Overpass API data."""
    _cache  = {}
    _places_cache = {}
    
    type_limits = {
        "water": 5,  # Limit water locations to 5
        "military": 3,
        "ruins": 4,
        "industrial": 4,
        "city": 10,
        "village": 8,
        "default": 6
    }


    def __init__(self, screen: pygame.Surface, draw_space: pygame.Rect, api_zoom: int = 13, initial_zoom: float = 0.5):
        # For OSM, no API key is needed.
        self.lat, self.lon = settings.LATITUDE, settings.LONGITUDE
        self.api_zoom = api_zoom
        self.draw_space = draw_space

        # Load marker icons (your utility remains the same)
        self.icons = Utils.load_svgs_dict(settings.MAP_ICONS_BASE_FOLDER, settings.MAP_ICON_SIZE)
        # Fetch map image from OSM static map service
        self.map_image = self._fetch_map_image()
        # Fetch POI data for the entire area using Overpass API (one call over a bounding box)
        self.places = self._fetch_places(self.lat, self.lon)
        self.rendered_map = self._draw_markers()

        super().__init__(screen, draw_space, self.rendered_map, initial_zoom)

    def get_icon_for_place(self, types):
        for typ in types:
            # Print type for debugging if desired
            print(typ)
            if typ in self.icons and typ != "default":
                return self.icons[typ]
        return self.icons["default"]

    def lat_lon_to_pixel(self, lat, lon, zoom):
        """Convert lat/lon to pixel coordinates using the same tile scheme as OSM (similar to Google's)."""
        lat_rad = math.radians(lat)
        n = 2.0 ** zoom
        x = (lon + 180.0) / 360.0 * n * 256  # 256 pixels per tile
        y = (1.0 - math.log(math.tan(lat_rad) + 1.0 / math.cos(lat_rad)) / math.pi) / 2.0 * n * 256
        return x, y

    def _zoom_to_radius(self, zoom, latitude):
        """
        Convert a Geoapify (OSM) zoom level to an Overpass API radius in meters.

        :param zoom: Zoom level (0-20).
        :param latitude: Latitude in degrees.
        :return: Approximate radius in meters.
        """
        meters_per_pixel = (156543.03 * math.cos(math.radians(latitude))) / (2 ** zoom)
        radius = (settings.MAP_SIZE * meters_per_pixel) / 2  # Use half a tile width
        return int(radius)  # Overpass API expects an integer


    def _fetch_places(self, lat, lon):
        """
        Uses the Overpass API to fetch points of interest (cities, towns, villages, lakes, ruins,
        industrial, and military features) over a given radius. After fetching, it filters the results
        to ensure a minimum distance between nodes.
        """
        
        radius = self._zoom_to_radius(self.api_zoom, lat)
        cache_key = f"{lat:.6f}_{lon:.6f}_{self.api_zoom}_{radius}"
        places_cache = f"{settings.MAP_PLACES_CACHE}.{cache_key}.json"
        
        if cache_key in self._places_cache:
            return self._places_cache[cache_key]

        if os.path.exists(places_cache):
            with open(places_cache, "r") as f:
                try:
                    cached_data = json.load(f)
                    if isinstance(cached_data, dict) and cache_key in cached_data:
                        return cached_data[cache_key]  # Return the cached places
                except json.JSONDecodeError:
                    print("Error reading cached places data.")


        # Build the Overpass QL query.
        query = settings.get_places_map_url(radius, lat, lon)

        # Fetch data from the Overpass API
        try:
            response = requests.post(settings.OVERPASS_URL, data={'data': query})
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching Overpass data: {e}")
            return []

        data = response.json()
        elements = data.get("elements", [])

        # Helper function to extract a list of 'types' from an element's tags.
        def get_types(tags):
            types = []
            if "place" in tags:
                types.append(tags["place"])
            if "water" in tags:
                types.append(tags["water"])
            if tags.get("natural") == "water":
                types.append("water")
            if "historic" in tags:
                types.append(tags["historic"])
            if "landuse" in tags:
                types.append(tags["landuse"])
            if "military" in tags:
                types.append("military")
            if not types:
                types.append("default")
            return types

        # Process the raw elements into a list of places with lat, lon, and types.
        raw_places = []
        for element in elements:
            if "lat" in element and "lon" in element:
                lat_val = element["lat"]
                lon_val = element["lon"]
            elif "center" in element:
                lat_val = element["center"]["lat"]
                lon_val = element["center"]["lon"]
            else:
                continue

            tags = element.get("tags", {})
            types = get_types(tags)
            raw_places.append({"lat": lat_val, "lon": lon_val, "types": types})

        # Filter out nodes that are too close together.

        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371000  # Earth radius in meters
            phi1 = math.radians(lat1)
            phi2 = math.radians(lat2)
            delta_phi = math.radians(lat2 - lat1)
            delta_lambda = math.radians(lon2 - lon1)
            a = math.sin(delta_phi / 2) ** 2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
            return R * c

        random.shuffle(raw_places)
        type_counts = {key: 0 for key in self.type_limits}
        selected_places = []
        for place in raw_places:
            too_close = False
            random_factor = random.uniform(0.4, 2.4)  # Randomly vary distance by ±20%
            min_distance = settings.MAP_MIN_NODE_DISTANCE * random_factor  # Apply randomness
            place_types = place["types"]
            dominant_type = next((t for t in place_types if t in self.type_limits), "default")

            # Check if the type has reached its limit
            if type_counts[dominant_type] >= self.type_limits[dominant_type]:
                continue           
            for sel in selected_places:
                if haversine_distance(place["lat"], place["lon"], sel["lat"], sel["lon"]) < min_distance:
                    too_close = True
                    break
            
            if not too_close:
                selected_places.append(place)
                type_counts[dominant_type] += 1
                    
        if os.path.exists(places_cache):
            with open(places_cache, "r") as f:
                cache_data = json.load(f)
        else:
            cache_data = {}

        cache_data[cache_key] = selected_places
        
        json_data = json.dumps(cache_data, indent=4)
        
        with open(places_cache, "w") as f:
            f.write(json_data)
        return selected_places

    def _draw_markers(self):
        """Place markers on the map image based on the fetched POI data."""
        map_surface = self.map_image.copy()
        map_width, map_height = map_surface.get_size()
        center_pixel = self.lat_lon_to_pixel(self.lat, self.lon, self.api_zoom)

        for place in self.places:
            print(place)
            icon = self.get_icon_for_place(place.get("types", []))
            icon_w, icon_h = icon.get_size()
            marker_pixel = self.lat_lon_to_pixel(place["lat"], place["lon"], self.api_zoom)
            screen_x = (marker_pixel[0] - center_pixel[0]) + (map_width // 2) - icon_w // 2
            screen_y = (marker_pixel[1] - center_pixel[1]) + (map_height // 2) - icon_h // 2

            if 0 <= screen_x <= map_width - icon_w and 0 <= screen_y <= map_height - icon_h:
                map_surface.blit(icon, (screen_x, screen_y))
        return map_surface

    def _fetch_map_image(self) -> pygame.Surface:
        """
        Retrieves the map image from an OSM static map service.
        This version caches the image on disk to save bandwidth.
        """
        size = settings.MAP_SIZE
        cache_key = (round(self.lat, 6), round(self.lon, 6), self.api_zoom, size)
        
        if cached := self._cache.get(cache_key):
            return cached.copy()

        os.makedirs(settings.MAP_CACHE, exist_ok=True)
        filename = f"{self.lat:.6f}_{self.lon:.6f}_{self.api_zoom}_{size}.png"
        cache_path = os.path.join(settings.MAP_CACHE, filename)

        if os.path.exists(cache_path):
            img = pygame.image.load(cache_path).convert()
            self._cache[cache_key] = img
            return Utils.tint_image(img)


        url = settings.get_static_map_url(size, settings.GEOAPIFY_API_KEY, self.lon, self.lat, self.api_zoom)
        print(f"Fetching map image from {url}")
        response = requests.get(url)
        if response.status_code != 200:
            raise ConnectionError(f"OSM Static Map API failed: {response.status_code}")

        img = pygame.image.load(io.BytesIO(response.content)).convert()
        original_width = img.get_width()
        original_height = img.get_height()
        min_size = min(original_width, original_height)
        cropped_img = pygame.Surface((min_size, min_size))
        cropped_img.blit(img, (0, 0), (0, 0, min_size, min_size))
        cropped_img = cropped_img.convert()

        pygame.image.save(cropped_img, cache_path)
        self._cache[cache_key] = cropped_img
        return Utils.tint_image(cropped_img)