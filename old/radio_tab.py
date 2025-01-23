import pygame
import settings
import numpy as np
import random
from scipy.interpolate import CubicSpline
from global_functs import bottom_tab_lines2
import yappi
playlist = {}
music_files = {}

# Font for radio station names
radio_font = pygame.font.Font(settings.ROBOTO_PATH, 15)
selected_station_index = 0


previous_values = []

yappi.start()



# for wave in range(settings.WAVES):
#     new = random.randint(1, 6)
#     # Remove the oldest value if the list has reached its maximum length
#     # Check if the list is not empty and the last number is positive
#     if previous_values and previous_values[-1] > 0:
#         # Make the new number negative
#         new = -new
#     previous_values.append(new)
#
# def load_music_files(station_folder):
#     # Modified to return a dictionary of music files with their lengths
#     music_files = {}
#     for file_name in os.listdir(station_folder):
#         if file_name.endswith(".ogg"):
#             file_path = os.path.join(station_folder, file_name)
#             if os.path.isfile(file_path):
#                 tag = TinyTag.get(file_path)
#                 song_length = round(tag.duration * 1000)
#                 music_files[file_path] = song_length
#     return music_files
#
# def load_intermission_files(intermission_folder):
#     intermission_files = {}
#     # Traverse the folder and its subfolders
#     for root, _, files in os.walk(intermission_folder):
#         for file_name in files:
#             if file_name.endswith(".ogg"):
#                 file_path = os.path.join(root, file_name)
#                 # Load the file only if it is a file (not a directory)
#                 if os.path.isfile(file_path):
#                     tag = TinyTag.get(file_path)
#                     song_length = round(tag.duration * 1000)
#                     intermission_files[file_path] = song_length
#     return intermission_files
#
#
# def load_music():
#     radio_stations = {}
#     config_cache = {}
#     radio_folder = "sounds/radio"
#     intermission_folder = "sounds/radio/DCR_intermissions"
#
#     for folder_name in os.listdir(radio_folder):
#         folder_path = os.path.join(radio_folder, folder_name)
#
#         if not os.path.isdir(folder_path):
#             continue
#
#         ini_file_path = os.path.join(folder_path, "station.ini")
#
#         # Load configuration from cache or file
#         if ini_file_path in config_cache:
#             config = config_cache[ini_file_path]
#         elif os.path.exists(ini_file_path):
#             config = configparser.ConfigParser()
#             with open(ini_file_path) as ini_file:
#                 config.read_file(ini_file)
#             config_cache[ini_file_path] = config
#         else:
#             continue
#
#         # Parse configuration data
#         station_name = config.get("metadata", "station_name", fallback=folder_name)
#         ordered = config.getboolean("metadata", "ordered", fallback=False)
#
#         # Load music files
#         music_files = load_music_files(folder_path)
#
#         # Skip if no music files or station not in settings
#         if not music_files or station_name not in settings.RADIO_STATIONS:
#             continue
#
#         # Random selection for initial song and position
#
#         # Store station information
#         radio_stations[station_name] = {
#             "folder": folder_path,
#             "ordered": ordered,
#             "music_files": music_files,
#             "last_played_time": 0,
#         }
#         if folder_name == "03_DCR":
#             intermission_files = load_intermission_files(intermission_folder)
#             radio_stations[station_name]["intermission_files"] = intermission_files
#
#     return radio_stations
#
#
# def play_song(current_song, position):
#     position = position / 1000
#     pygame.mixer.music.stop()  # Stop the current music
#     pygame.mixer.music.load(current_song)
#     print(current_song, position)
#     try:
#         if position > 0:
#             pygame.mixer.music.play(start=position)
#         else:
#             pygame.mixer.music.play()
#     except pygame.error:
#         return
#     pygame.mixer.music.set_volume(settings.MUSIC_VOLUME)
#
# def add_intermissions(playlist):
#     intermission_songs = [playlist[i] for i in sorted(random.sample(range(len(playlist)), random.randint(settings.INTERMISSION_FREQUENCY, len(playlist) // 2)))]
#     intermissions_base_path = "sounds/radio/DCR_intermissions"
#     intermission_choices_dict = {}
#
#
#     for song in intermission_songs:
#         # Split the song name to get artist and song name
#         file_name = song.rsplit('.', 1)[0]
#         parts = file_name.split('_')
#         artist = parts[-2]
#         song_name = parts[-1]
#
#         # Determine file paths for pre and post intermissions
#         base_intermission_path = os.path.join(intermissions_base_path, artist)
#
#         # Collect pre and after intermission choices
#         intermission_choices_dict[song] = {
#             "pre": [],
#             "after": []
#         }
#
#         if os.path.exists(base_intermission_path):
#             for file in os.listdir(base_intermission_path):
#                 if file.endswith(".ogg"):
#                     intermission_choices_dict[song]["pre"].append(os.path.join(base_intermission_path, file))
#                     intermission_choices_dict[song]["after"].append(os.path.join(base_intermission_path, file))
#         if os.path.exists(os.path.join(base_intermission_path, "pre")):
#             for file in os.listdir(os.path.join(base_intermission_path, "pre")):
#                 if file.endswith(".ogg"):
#                     intermission_choices_dict[song]["pre"].append(os.path.join(base_intermission_path, "pre"))
#         if os.path.exists(os.path.join(base_intermission_path, "after")):
#             for file in os.listdir(os.path.join(base_intermission_path, "after")):
#                 if file.endswith(".ogg"):
#                     intermission_choices_dict[song]["after"].append(os.path.join(base_intermission_path, "after"))
#         if os.path.exists(os.path.join(base_intermission_path, song_name)):
#             for file in os.listdir(os.path.join(base_intermission_path, song_name)):
#                 if file.endswith(".ogg"):
#                     intermission_choices_dict[song]["pre"].append(os.path.join(base_intermission_path, song_name))
#                     intermission_choices_dict[song]["after"].append(os.path.join(base_intermission_path, song_name))
#             if os.path.exists(os.path.join(base_intermission_path, song_name, "pre")):
#                 for file in os.listdir(os.path.join(base_intermission_path, song_name, "pre")):
#                     if file.endswith(".ogg"):
#                         intermission_choices_dict[song]["pre"].append(os.path.join(base_intermission_path, song_name, "pre"))
#             if os.path.exists(os.path.join(base_intermission_path, song_name, "after")):
#                 for file in os.listdir(os.path.join(base_intermission_path, song_name, "after")):
#                     if file.endswith(".ogg"):
#                         intermission_choices_dict[song]["after"].append(os.path.join(base_intermission_path, song_name, "after", file))
#
#         if intermission_choices_dict[song]["pre"]:
#             intermission_choices_dict[song]["pre"] = random.choice(intermission_choices_dict[song]["pre"])
#         if intermission_choices_dict[song]["after"]:
#             intermission_choices_dict[song]["after"] = random.choice(intermission_choices_dict[song]["after"])
#
#     for (song, choices) in intermission_choices_dict.items():
#         current_song_index = playlist.index(song)
#         if choices["pre"]:
#             playlist.insert(current_song_index, choices["pre"])
#             current_song_index -= 1
#         if playlist[current_song_index] in intermission_songs and current_song_index > 0:
#             playlist.insert(current_song_index + 1, intermission_choices_dict[playlist[current_song_index]]["after"])
#             playlist.pop(current_song_index - 1)
#
#     return playlist
#
# def generate_playlist(music_files, station):
#     playlist = list(music_files[station]["music_files"].keys())
#     if not music_files[station]["ordered"]:
#         random.shuffle(playlist)
#     if station == "Diamond City Radio" and settings.INTERMISSIONS:
#         playlist = add_intermissions(playlist)
#     return playlist
#
# def handle_music_end():
#     global playlist, selected_station_index, music_files
#     if pygame.mixer.music.get_busy():
#         return
#     selected_station = settings.RADIO_STATIONS[selected_station_index]
#     if len(playlist[selected_station]) == 0:
#         playlist[selected_station] = generate_playlist(music_files, selected_station)
#         current_song = playlist[selected_station][0]
#     else:
#         playlist[selected_station].pop(0)
#         current_song = playlist[selected_station][0]
#     play_song(current_song, 0)
#
# def play_radio_music():
#     global selected_station_index, playlist, music_files
#
#     for station in music_files:
#         playlist[station] = generate_playlist(music_files, station)
#
#     for station in playlist:
#         if station == "Diamond City Radio" and "/DCR_intermissions/" in playlist[station][0]:
#             print(playlist[station][0])
#             first_song_length = list(music_files[station]["intermission_files"].values())[0]
#         else:
#             first_song_length = list(music_files[station]["music_files"].values())[0]
#         music_files[station]["last_played_time"] = random.randint(0, first_song_length)
#
#     temp_index = selected_station_index
#     print(playlist)
#
#     while True:
#         if temp_index != selected_station_index:
#             selected_station = settings.RADIO_STATIONS[selected_station_index]
#             time_difference = max(0, pygame.time.get_ticks() - music_files[selected_station]["last_played_time"])
#             playing_song = playlist[selected_station][0]
#             print(playing_song)
#             if selected_station == "Diamond City Radio" and "/DCR_intermissions/" in playing_song:
#                 print(playing_song)
#                 if time_difference < music_files[selected_station]["intermission_files"][playing_song]:
#                     current_song = playing_song
#                     position = music_files[selected_station]["last_played_time"]
#                 else:
#                     for song in playlist[selected_station]:
#                         if time_difference < music_files[selected_station]["intermission_files"][song]:
#                             current_song = song
#                             position = time_difference - music_files[selected_station]["intermission_files"][song]
#                             break
#                         else:
#                             if len(playlist[selected_station]) == 0:
#                                 playlist[selected_station] = generate_playlist(music_files, selected_station)
#                             (k := next(iter(playlist)), playlist.pop(k))
#                             time_difference -= music_files[selected_station]["intermission_files"][song]
#             else:
#                 if time_difference < music_files[selected_station]["music_files"][playing_song]:
#                     current_song = playing_song
#                     position = music_files[selected_station]["last_played_time"]
#                 else:
#                     for song in playlist[selected_station]:
#                         if time_difference < music_files[selected_station]["music_files"][song]:
#                             current_song = song
#                             position = time_difference - music_files[selected_station]["music_files"][song]
#                             break
#                         else:
#                             if len(playlist[selected_station]) == 0:
#                                 playlist[selected_station] = generate_playlist(music_files, selected_station)
#                             (k := next(iter(playlist)), playlist.pop(k))
#                             time_difference -= music_files[selected_station]["music_files"][song]
#             temp_station = settings.RADIO_STATIONS[temp_index]
#             music_files[temp_station]["last_played_time"] = pygame.time.get_ticks()
#             temp_index = selected_station_index
#             play_song(current_song, position)
#         pygame.time.wait(10)
#
#
# music_files = load_music()

def draw_radio_tab(screen, event):
    global selected_station_index
    """
    This function is responsible for drawing the radio tab content on the screen.
    """

    for _ in range(settings.WAVES):
        generate_random_numbers()

    y_position = settings.LIST_START_Y
    # Index to keep track of the selected station

    if event == "down":
        selected_station_index = (selected_station_index + 1) % len(settings.RADIO_STATIONS)
    elif event == "up":
        selected_station_index = (selected_station_index - 1) % len(settings.RADIO_STATIONS)


    # Draw radio stations list
    for i, station in enumerate(settings.RADIO_STATIONS):
        # Render text with different color based on selection
        if i == selected_station_index:
            station_text_color = settings.BACKGROUND  # Change text color to background color if selected
            cursor_color = settings.PIP_BOY_GREEN
        else:
            station_text_color = settings.PIP_BOY_GREEN  # Keep text color as green if not selected
            cursor_color = settings.BACKGROUND

        station_text = radio_font.render(station, True, station_text_color)
        station_rect = station_text.get_rect(topleft=(10, y_position))

        # Draw cursor for selected station
        if i == selected_station_index:
            cursor_rect = pygame.Rect(0, y_position, settings.SCREEN_WIDTH / 2, station_rect.height)
            pygame.draw.rect(screen, cursor_color, cursor_rect)
            cursor_dot_size = station_rect.height / 4
            cursor_dot_rect = pygame.Rect(3, y_position + (station_rect.height - cursor_dot_size) / 2, cursor_dot_size, cursor_dot_size)
            pygame.draw.rect(screen, station_text_color, cursor_dot_rect)

        screen.blit(station_text, station_rect)

        y_position += settings.LIST_OFFSET # Increase Y position for the next station

    # Calculate square dimensions for the graph
    graph_rect = pygame.Rect(settings.GRAPH_LEFT_MARGIN, settings.GRAPH_TOP_MARGIN, settings.GRAPH_SIZE, settings.GRAPH_SIZE)

    # Draw lines for right and bottom borders
    pygame.draw.line(screen, settings.PIP_BOY_GREEN, (graph_rect.right, graph_rect.top), (graph_rect.right, graph_rect.bottom))
    pygame.draw.line(screen, settings.PIP_BOY_GREEN, (graph_rect.left, graph_rect.bottom), (graph_rect.right, graph_rect.bottom))

    # Draw lines coming out of the axes
    for x in range(graph_rect.left + settings.LINES_OFFSET_OUT, graph_rect.right - settings.LINES_OFFSET_OUT, settings.TOTAL_LINES):  # Adjusted step size for x-axis lines
        pygame.draw.line(screen, settings.PIP_BOY_GREEN, (x, graph_rect.bottom), (x, graph_rect.bottom - settings.BIG_LINE_SIZE))
        # Draw three small lines between the big lines
        for i in range(1, 4):
            small_line_x = x + (settings.TOTAL_LINES // 3) * i - settings.SMALL_LINE_SIZE // 2
            pygame.draw.line(screen, settings.PIP_BOY_GREEN, (small_line_x, graph_rect.bottom), (small_line_x, graph_rect.bottom - settings.SMALL_LINE_SIZE))

    # Draw lines coming out of the axes for the y-axis
    for y in range(graph_rect.top + settings.LINES_OFFSET_OUT, graph_rect.bottom - settings.LINES_OFFSET_OUT, settings.TOTAL_LINES):  # Adjusted step size for y-axis lines
        pygame.draw.line(screen, settings.PIP_BOY_GREEN, (graph_rect.right, y), (graph_rect.right - settings.BIG_LINE_SIZE, y))
        # Draw three small lines between the big lines
        for i in range(1, 4):
            small_line_y = y + (settings.TOTAL_LINES // 3) * i - settings.SMALL_LINE_SIZE // 2
            pygame.draw.line(screen, settings.PIP_BOY_GREEN, (graph_rect.right, small_line_y), (graph_rect.right - settings.SMALL_LINE_SIZE, small_line_y))
    draw_smooth_waveform(screen, graph_rect)
    bottom_tab_lines2(screen)


def generate_random_numbers():
    global previous_values, selected_station_index

    if selected_station_index == 0:
        new_number = random.randint(0, 2)
    else:
        new_number = random.randint(1, 6)
    # Remove the oldest value if the list has reached its maximum length
    # Check if the list is not empty and the last number is positive
    if previous_values and previous_values[-1] > 0:
        # Make the new number negative
        new_number = -new_number
    if len(previous_values) >= settings.WAVES:
        previous_values.pop(0)
    # Append the new number to the list
    previous_values.append(new_number)
    return previous_values


def draw_smooth_waveform(screen, graph_rect):
    global previous_values

    # Generate the array of random numbers less frequently
    generate_random_numbers()

    scaling_factor = graph_rect.height / 20

    # Draw the smooth waveform using cubic spline interpolation
    x_values = np.linspace(-15, graph_rect.width, len(previous_values))
    y_values = [graph_rect.centery - value * scaling_factor for value in previous_values]

    # Perform cubic spline interpolation
    cs = CubicSpline(x_values, y_values)

    # Generate interpolated points
    num_points = 50  # Increase this value for smoother curves
    interpolated_x = np.linspace(-15, graph_rect.width, num_points)
    interpolated_y = cs(interpolated_x)

    # Draw the smooth line
    smooth_points = [(graph_rect.left + x, y) for x, y in zip(interpolated_x, interpolated_y)]
    pygame.draw.aalines(screen, settings.PIP_BOY_GREEN, False, smooth_points)

    # Draw a rectangle to obscure the portion of the waveform that is over the -15 mark
    obscuring_rect = pygame.Rect(graph_rect.left - 15, graph_rect.top, graph_rect.width * 15 / graph_rect.width, graph_rect.height)
    pygame.draw.rect(screen, settings.BACKGROUND, obscuring_rect)
