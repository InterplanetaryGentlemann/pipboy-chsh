import os
from data_models import LimbPosition, IconConfig

# ==================================================
# Constants (Modify only if program structure changes)
# ==================================================
TABS = ("STAT", "INV", "DATA", "MAP", "RADIO")
SUBTABS = {
    "STAT": ("STATUS", "SPECIAL", "PERKS"),
    "INV": ("WEAPONS", "APPAREL", "AID", "MISC", "JUNK"),
    "DATA": ("QUESTS", "WORKSHOP", "MAP", "RADIO", "STATS"),
    "MAP": ("LOCAL", "WORLD"),
}

# ==================================================
# User Configuration (Adjust these for setup/preferences)
# ==================================================

# ------------------
# Screen Settings
# ------------------
SCREEN_WIDTH = 320
SCREEN_HEIGHT = 255
FPS = 24
SPEED = 1
BACKGROUND = (0, 0, 0)
PIP_BOY_LIGHT = (0, 255, 0)
PIP_BOY_MID = (0, 127, 0)
PIP_BOY_DARKER = (0, 63, 0)


# ------------------
# Audio Settings
# ------------------
SOUND_ON = True
VOLUME = 1
MUSIC_VOLUME = 1
SWITCH_SOUND_CHANCE = 90

# ------------------
# Visual Effects
# ------------------
SHOW_CRT = True
BLOOM_EFFECT = True
GLITCH_MOVE_CHANCE = 40
BOOT_SCREEN = False

# ------------------
# Path Configuration
# ------------------
# Fonts
MAIN_FONT_PATH = "../fonts/RobotoCondensed-Bold.ttf"
ROBOTO_BOLD_PATH = "../fonts/Roboto-Bold.ttf"
ROBOTO_PATH = "../fonts/Roboto-Regular.ttf"
ROBOTO_CONDENSED_PATH = "../fonts/RobotoCondensed-Regular.ttf"
ROBOTO_CONDENSED_BOLD_PATH = "../fonts/RobotoCondensed-Bold.ttf"
TECH_MONO_FONT_PATH = "../fonts/TechMono.ttf"

# Images
CRT_OVERLAY = "../images/overlay.png"
BLOOM_OVERLAY = "../images/dirt.png"
SCANLINE_OVERLAY = "../images/scanline.png"
SCANLINES_OVERLAY = "../images/scanlines.png"
CRT_STATIC = "../images/static"
BOOT_THUMBS = "../images/boot"
STAT_TAB_LEGS_BASE_FOLDER = "../images/stats/legs1"
STAT_TAB_HEAD_BASE_FOLDER = "../images/stats/head1"
STAT_TAB_GUN = "../images/stats/gun.png"
STAT_TAB_ARMOUR = "../images/stats/helmet.png"
STAT_TAB_RETICLE = "../images/stats/reticle.png"
STAT_TAB_SHIELD = "../images/stats/shield.png"
STAT_TAB_RADIATION = "../images/stats/radiation.png"
STAT_TAB_BOLT = "../images/stats/bolt.png"

# Sounds
BOOT_SOUND_A = "../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_A.ogg"
BOOT_SOUND_B = "../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_B.ogg"
BOOT_SOUND_C = "../sounds/pipboy/BootSequence/UI_PipBoy_BootSequence_C.ogg"
BACKGROUND_HUM = "../sounds/pipboy/UI_PipBoy_Hum_LP.ogg"
TAB_SWITCH_SOUND = "../sounds/pipboy/BurstStatic"
RADIO_BASE_FOLDER = "../sounds/radio"
RADIO_TURN_ON_SOUND = "../sounds/pipboy/Radio/UI_PipBoy_Radio_On.ogg"
RADIO_TURN_OFF_SOUND = "../sounds/pipboy/Radio/UI_PipBoy_Radio_Off.ogg"
DCR_INTERMISSIONS_BASE_FOLDER = "../sounds/radio/DCR_intermissions"
RADIO_STATIC_BURSTS_BASE_FOLDER = "../sounds/pipboy/Radio/StaticBursts"

# ------------------
# UI Layout
# ------------------
TAB_MARGIN = 20
TAB_VERTICAL_OFFSET = 1
TAB_VERTICAL_LINE_OFFSET = 10
TAB_HORIZONTAL_LINE_OFFSET = 8
TAB_SCREEN_EDGE_LENGTH = 4
TAB_HORIZONTAL_LENGTH = TAB_HORIZONTAL_LINE_OFFSET // 1.1
TAB_BOTTOM_MARGIN = 2
TAB_BOTTOM_VERTICAL_MARGINS = 3
BOTTOM_BAR_HEIGHT = 18
BOTTOM_BAR_MARGIN = 8
TAB_SIDE_MARGIN = 0
SUBTAB_SPACING = 5
SUBTAB_VERTICAL_OFFSET = 1


# ------------------
# Player Settings
# ------------------
PLAYER_NAME = "Kyran"
HP_MAX = 120
HP_CURRENT = 100
AP_MAX = 90
AP_CURRENT = 90
LEVEL = 28
XP_CURRENT = 39
LIMB_DAMAGE = [100, 14, 69, 24, 78, 100]
DEFAULT_STATS_DAMAGE = [
    IconConfig(STAT_TAB_RETICLE, 18),
    IconConfig(STAT_TAB_BOLT, 10)]
DEFAULT_STATS_ARMOR = [
    IconConfig(STAT_TAB_SHIELD, 5),
    IconConfig(STAT_TAB_RADIATION, 10)
]


# ------------------
# Stat Tab Settings
# ------------------

VAULTBOY_SCALE = 600
VAULT_BOY_OFFSETS = {'legs': (0, 12), 'head': (0, -17)}
LIMB_POSITIONS = [
    LimbPosition(0, 10, 'head'),
    LimbPosition(-50, 50, 'left_arm'),
    LimbPosition(50, 50, 'right_arm'),
    LimbPosition(-50, 95, 'left_leg'),
    LimbPosition(50, 95, 'right_leg'),
    LimbPosition(0, 130, 'torso')
]
DAMAGE_ARMOUR_MARGIN_SMALL = 2
DAMAGE_ARMOUR_ICON_SMALL_SIZE = 0.5
DAMAGE_ARMOUR_MARGIN_BIG = 8
DAMAGE_ARMOUR_ICON_BIG_SIZE = 0.45
DAMAGE_ARMOUR_ICON_ABSOLUTE_SIZE = 11.5
DAMAGE_ARMOUR_ICON_MARGIN = 7
LIMB_DAMAGE_WIDTH = 20


# ------------------
# Radio Tab Settings
# ------------------
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
RADIO_WAVE_VISUALIZER_SIZE_OFFSET = 50
RADIO_WAVE_VISUALIZER_GRID_LINES = 15
RADIO_WAVE_BATCH_SIZE = 10
RADIO_WAVE_SMOOTHING_FACTOR = 0.05
INTERMISSION_FREQUENCY = 50

# ------------------
# Map Tab Settings
# ------------------
GOOGLE_MAPS_API_KEY = "AIzaSyA0zWCW9-dRXlu1GSdl6Rq1MPSoFT1pm2Q"
MAP_TOP_EDGE = 25
MAP_SIDE_MARGIN = 4
LONGITUDE = 52.2619
LATITUDE = 4.9865
ZOOM = 8
ZOOM_SPEED = 0.1
MOVEMENT_SPEED = 15
EXTRA_RESOLUTION = 2


if os.path.exists("user_config.py"):
    from user_config import *