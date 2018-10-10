# -*- coding: utf-8 -*-
from enum import IntEnum
    
class LEDCntrl(IntEnum):
    NONE = 0
    START = 1
    STOP = 2

class LEDPattern(IntEnum):
    NONE = 0
    WIPE = 1
    BRIGHT = 2

class ServCntrl(IntEnum):
    NONE = 0
    START = 1
    STOP = 2

class ServPattern(IntEnum):
    NONE = 0
    CENTER = 1
    SCAN = 2

