"""Shared enumerations for the domain model."""
from __future__ import annotations

from enum import Enum


class TrainType(str, Enum):
    EXPRESS = "express"      # Mail/Express/SF/Duronto/Humsafar/AC
    PASSENGER = "passenger"
    LOCAL = "local"          # Mumbai EMU
    MEMU = "memu"
    FREIGHT = "freight"
    YARD = "yard"            # shunting / stabling moves

    @property
    def is_high_priority(self) -> bool:
        return self in {TrainType.EXPRESS}


class Corridor(str, Enum):
    NORTH = "north"          # BSR–NSP–VR (towards Surat)
    WESTERN = "western"      # BSR–NIG–…–CCG (Mumbai)
    DIVA = "diva"            # BSR–JCNR–…–DIVA–PNVL
    YARD = "yard"
    FREIGHT = "freight"


class Direction(str, Enum):
    UP = "up"                # towards Mumbai / terminus
    DOWN = "down"            # away from Mumbai
    NORTH = "north"
    SOUTH = "south"


class OccupancyStatus(str, Enum):
    FREE = "free"
    OCCUPIED = "occupied"
    RESERVED = "reserved"    # route set / reserved, not yet occupied


class SignalAspect(str, Enum):
    RED = "red"
    YELLOW = "yellow"
    DOUBLE_YELLOW = "double_yellow"
    GREEN = "green"
