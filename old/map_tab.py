import pygame
import requests
import io
import settings
import numpy as np
from global_functs import bottom_tab_lines2, date_time_render
import json
import os
import hashlib

map_surf = None
render_rect = pygame.Rect(settings.MAP_SIDE_MARGIN, settings.MAP_TOP_EDGE, settings.SCREEN_WIDTH - (
            settings.MAP_SIDE_MARGIN * 2) - settings.LINE_THICKNESS, settings.SCREEN_HEIGHT - settings.BOTTOM_BAR_HEIGHT - settings.MAP_TOP_EDGE - 2)  # Define your render rectangle here

map_position = [0, 0]  # Initial position of the map image

zoom_level = 1
original_map_size = None
original_map_surf = None

CACHE_FOLDER = "cache"
map_initialized = False

def save_settings(settings_data):
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
    with open(os.path.join(CACHE_FOLDER, 'settings.json'), 'w') as f:
        json.dump(settings_data, f)

def load_settings():
    settings_file = os.path.join(CACHE_FOLDER, 'settings.json')
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    return None

def save_image(cache_key, image_data):
    if not os.path.exists(CACHE_FOLDER):
        os.makedirs(CACHE_FOLDER)
    with open(os.path.join(CACHE_FOLDER, cache_key + '.png'), 'wb') as f:
        f.write(image_data)

def load_image(cache_key):
    image_file = os.path.join(CACHE_FOLDER, cache_key + '.png')
    if os.path.exists(image_file):
        with open(image_file, 'rb') as f:
            return f.read()
    return None

def generate_cache_key(url):
    return hashlib.md5(url.encode()).hexdigest()

def load_settings_from_cache(url):
    cache_key = generate_cache_key(url)
    cached_settings = load_settings()
    if cached_settings and 'cache_key' in cached_settings and cached_settings['cache_key'] == cache_key:
        return cached_settings
    return None


def save_settings_to_cache(url, settings_data):
    cache_key = generate_cache_key(url)
    settings_data['cache_key'] = cache_key
    save_settings(settings_data)

def load_image_from_cache(url):
    cache_key = generate_cache_key(url)
    image_data = load_image(cache_key)
    return image_data

def save_image_to_cache(url, image_data):
    cache_key = generate_cache_key(url)
    save_image(cache_key, image_data)


def process_image_data(image_data):
    global map_surf, original_map_size, original_map_surf, map_position, map_initialized
    map_surf = pygame.image.load(io.BytesIO(image_data)).convert_alpha()

    # Crop the bottom part of the image
    cropped_surf = pygame.Surface((map_surf.get_width(), map_surf.get_height() - settings.BOTTOM_BAR_HEIGHT))
    cropped_surf.blit(map_surf, (0, 0),
                      pygame.Rect((0, 0), (map_surf.get_width(), map_surf.get_height() - settings.BOTTOM_BAR_HEIGHT)))

    map_surf = cropped_surf
    pygame.transform.scale(map_surf, render_rect.size)  # Scale the map surface to the render rectangle size
    original_map_size = map_surf.get_size()  # Store original size
    arr = pygame.surfarray.pixels3d(map_surf)
    mean_arr = np.dot(arr[:, :, :], [0.216, 0.587, 0.144])
    mean_arr3d = mean_arr[..., np.newaxis]
    new_arr = np.repeat(mean_arr3d[:, :, :], 3, axis=2)
    map_surf = pygame.surfarray.make_surface(new_arr.copy())  # Create a copy of the transformed surface
    map_surf.fill(settings.PIP_BOY_GREEN, None, pygame.BLEND_RGBA_MULT)
    original_map_surf = map_surf.copy()

    # Set initial map position to center
    map_position[0] = (original_map_size[0] * zoom_level - render_rect.width) / 2
    map_position[1] = (original_map_size[1] * zoom_level - render_rect.height) / 2
    map_initialized = True


def load_map_image(long, lat, zoom):
    global map_surf, original_map_size, zoom_level, original_map_surf
    url = ("https://maps.googleapis.com/maps/api/staticmap?center=" + long + "," + lat +
           "&zoom=" + str(zoom) + "&size="
           + str(render_rect.size[0] * settings.EXTRA_RESOLUTION) + "x" + str(render_rect.size[1] * settings.EXTRA_RESOLUTION + settings.BOTTOM_BAR_HEIGHT)  # Include extra height
           + "&scale=2"
           + "&key=" + settings.GOOGLE_MAPS_API_KEY
           + "&map_id=f0ee02b2af98e010"
           + "&style=fallout"
           )
    # Load cached settings
    cached_settings = load_settings_from_cache(url)

    # Check if settings have changed
    if cached_settings:
        # Load cached map image
        image_data = load_image_from_cache(url)
        if image_data:
            process_image_data(image_data)
            return

    # Settings have changed or not cached
    print("Loading map image from:", url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            process_image_data(r.content)
            # Save settings and image to cache
            save_settings_to_cache(url, {'cache_key': generate_cache_key(url)})
            save_image_to_cache(url, r.content)
        else:
            print("Failed to load map image - Status code:", r.status_code)
    except Exception as e:
        print("Failed to load map image:", e)


def scale_map_surface():
    global map_surf
    scaled_size = (int(original_map_size[0] * zoom_level), int(original_map_size[1] * zoom_level))
    map_surf = pygame.transform.scale(original_map_surf, scaled_size)

def move_map(event):
    global map_position
    if event == 'w':
        map_position[1] -= settings.MOVEMENT_SPEED  # Move up
    elif event == 's':
        map_position[1] += settings.MOVEMENT_SPEED  # Move down
    elif event == 'a':
        map_position[0] -= settings.MOVEMENT_SPEED  # Move left
    elif event == 'd':
        map_position[0] += settings.MOVEMENT_SPEED  # Move right

def update_zoom(event):
    global zoom_level
    if event == 'zoomin':
        zoom_level = max(zoom_level + settings.ZOOM_SPEED, 0.2)
    elif event == 'zoomout':
        print(zoom_level)
        zoom_level = max(zoom_level - settings.ZOOM_SPEED, 0.7)  # Adjust minimum zoom level here
    scale_map_surface()


def draw_map_tab(screen, event):
    global map_surf, map_position, render_rect, zoom_level, original_map_size

    if map_surf and map_initialized:
        if event in ('w', 's', 'a', 'd'):  # Only update map position for movement keys
            move_map(event)
        if event in ('zoomin', 'zoomout'):  # Only update zoom level for zoom keys
            update_zoom(event)

        # Ensure zoom level doesn't go below a certain threshold
        zoom_level = max(zoom_level, 0.2)

        # Ensure map position stays within bounds
        max_map_position_x = max(original_map_size[0] * zoom_level - render_rect.width, 0)
        max_map_position_y = max(original_map_size[1] * zoom_level - render_rect.height, 0)
        map_position[0] = min(max(0, map_position[0]), max_map_position_x)
        map_position[1] = min(max(0, map_position[1]), max_map_position_y)

        # Calculate the visible area of the original map surface within render_rect
        visible_area = pygame.Rect(map_position[0] / zoom_level, map_position[1] / zoom_level, render_rect.width / zoom_level, render_rect.height / zoom_level)

        # Create a subsurface of the original map surface representing the visible area within render_rect
        try:
            visible_map_surf = map_surf.subsurface(visible_area)
        except ValueError:
            # Handle case where visible area is outside the bounds of map_surf
            visible_map_surf = map_surf.subsurface(map_surf.get_rect())

        # Scale the visible map surface to match the size of render_rect
        scaled_visible_map_surf = pygame.transform.scale(visible_map_surf, render_rect.size)

        screen.blit(scaled_visible_map_surf, render_rect.topleft)  # Blit the visible map surface to the screen

    bottom_tab_lines2(screen)
    date_time_render(screen)

