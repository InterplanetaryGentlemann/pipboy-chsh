# settings.py
# MAIN
import os

# Screen dimensions
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 255

FPS = 10

# Colors
BACKGROUND = (0, 0, 0)
PIP_BOY_GREEN = (0, 255, 0)
PIP_BOY_DARKER = (0, 40, 0)

# Sound
SOUND_ON = True
VOLUME = 1

MUSIC_VOLUME = 0.3

SWITCH_SOUND_CHANCE = 90

BOOT_SCREEN = False
BOOT_SPEED = 40

SHOW_STATIC = True

# Font path
MAIN_FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/RobotoCondensed-Bold.ttf")
ROBOTO_BOLD_PATH = os.path.join(os.path.dirname(__file__), "fonts/Roboto-Bold.ttf")
ROBOTO_PATH = os.path.join(os.path.dirname(__file__), "fonts/Roboto-Regular.ttf")
TECH_MONO_FONT_PATH = os.path.join(os.path.dirname(__file__), "fonts/TechMono.ttf")

CRT_OVERLAY = os.path.join(os.path.dirname(__file__), "images/overlay.png")
SCANLINE_OVERLAY = os.path.join(os.path.dirname(__file__), "images/scanline.png")
CRT_STATIC = os.path.join(os.path.dirname(__file__), "images/static")


# Tab texts
TAB_TEXTS = ["STAT", "INV", "DATA", "MAP", "RADIO"]

# Tab margins
TAB_MARGIN = 20
TAB_VERTICAL_OFFSET = 1

# Line thickness
LINE_THICKNESS = 1

# Text tab margin
TEXT_TAB_MARGIN = 6

# Glitch effect
GLITCH_MOVE_CHANCE = 15

BOTTOM_BAR_HEIGHT = 20
BOTTOM_BAR_DIVIDER = 2

SUB_TAB_MARGIN = 10

# RADIO TAB

LIST_START_Y = 50
LIST_OFFSET = 25

GRAPH_LEFT_MARGIN = SCREEN_WIDTH / 2 + 40
GRAPH_TOP_MARGIN = LIST_START_Y
GRAPH_SIZE = SCREEN_WIDTH / 2 - 50

LINES_OFFSET_OUT = 8
LINES_OFFSET_IN = 10
TOTAL_LINES = int(round(GRAPH_SIZE / 8))  # Total number of lines (including the big line)
BIG_LINE_SIZE = GRAPH_SIZE / 30  # Size of the big line
SMALL_LINE_SIZE = GRAPH_SIZE / 40  # Size of the small lines

WAVES = 15

RADIO_STATIONS = [
    "Diamond City Radio",
    "Classical Radio",
    "Radio Freedom"
]

TIMES_TO_PLAY = 2

INTERMISSIONS = True
INTERMISSION_FREQUENCY = 10

# MAP TAB

GOOGLE_MAPS_API_KEY = "AIzaSyA0zWCW9-dRXlu1GSdl6Rq1MPSoFT1pm2Q"

MAP_TOP_EDGE = 25
MAP_SIDE_MARGIN = 4

LONGITUDE = 52.2619
LATITUDE = 4.9865
ZOOM = 8

ZOOM_SPEED = 0.1

MOVEMENT_SPEED = 15

EXTRA_RESOLUTION = 2
