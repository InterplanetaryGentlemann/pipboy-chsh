import os

# Screen dimensions
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 255

FPS = 30
SPEED = 1

# Colors
BACKGROUND = (0, 0, 0)
PIP_BOY_GREEN = (0, 255, 0)
PIP_BOY_DARKER = (0, 40, 0)

# Sound
SOUND_ON = True
VOLUME = 1

MUSIC_VOLUME = 0.3

SWITCH_SOUND_CHANCE = 90

# Boot-up sequence
BOOT_SCREEN = False

# Crt effect
SHOW_CRT = True

## Paths
# Font
MAIN_FONT_PATH = "../fonts/RobotoCondensed-Bold.ttf"
ROBOTO_BOLD_PATH = "../fonts/Roboto-Bold.ttf"
ROBOTO_PATH = "../fonts/Roboto-Regular.ttf"
TECH_MONO_FONT_PATH = "../fonts/TechMono.ttf"

# Images
CRT_OVERLAY = "../images/overlay.png"
SCANLINE_OVERLAY = "../images/scanline.png"
SCANLINES_OVERLAY = "../images/scanlines.png"
CRT_STATIC = "../images/static"
BOOT_THUMBS = "../images/boot"

# Sounds
BOOT_SOUND_A = "../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_A.ogg"
BOOT_SOUND_B = "../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_B.ogg"
BOOT_SOUND_C = "../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_C.ogg"

BACKGROUND_HUM = "../sounds/pipboy/UI_PipBoy_Hum_LP.ogg"

TAB_SWITCH_SOUND = "../sounds/pipboy/BurstStatic"

RADIO_BASE_FOLDER = "../sounds/radio"

# Tab texts
TABS = ("STAT", "INV", "DATA", "MAP", "RADIO")

# Tab margins top
TAB_MARGIN = 20
TAB_VERTICAL_OFFSET = 1
TAB_VERTICAL_LINE_OFFSET = 10
TAB_HORIZONTAL_LINE_OFFSET = 8
TAB_SCREEN_EDGE_LENGTH = 4
TAB_HORIZONTAL_LENGTH  = TAB_HORIZONTAL_LINE_OFFSET // 1.1

TAB_BOTTOM_MARGIN = 30

# Tab margins bottom
BOTTOM_BAR_HEIGHT = 20
BOTTOM_BAR_MARGIN = 20

# Tab margins side
TAB_SIDE_MARGIN = 0

# Glitch effect
GLITCH_MOVE_CHANCE = 40

# RADIO TAB

RADIO_STATION_MARGIN = 10

RADIO_STATION_TEXT_MARGIN = 10
RADIO_STATION_SELECTION_MARGIN = 6

RADIO_STATION_SELECTION_DOT_SIZE = 4

RADIO_WAVE_POINTS = 12
RADIO_WAVE_VARIANCE = 5

RADIO_WAVE_SMOOTHING = 0.5

RADIO_WAVE_MAX = 10
RADIO_WAVE_MIN = 2

RADIO_WAVE_VISUALIZER_X_OFFSET = 10
RADIO_WAVE_VISUALIZER_Y_OFFSET = 10
RADIO_WAVE_VISUALIZER_SIZE_OFFSET = 80


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

RADIO_STATIONS = (
    "Diamond City Radio",
    "Classical Radio",
    "Radio Freedom"
)

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
