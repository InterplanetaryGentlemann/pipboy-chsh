# data_models.py
from dataclasses import dataclass
from typing import NamedTuple

@dataclass
class LimbPosition:
    x_offset: int
    y_position: int
    name: str

class IconConfig(NamedTuple):
    path: str
    value: int