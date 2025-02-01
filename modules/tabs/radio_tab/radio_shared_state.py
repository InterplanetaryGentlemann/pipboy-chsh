# radio_tab/radio_shared_state.py

class RadioSharedState:
    def __init__(self):
        self.station_playing = False
        self.active_station_index = None
        self.previous_station_index = None
