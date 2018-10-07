# -*- coding: utf-8 -*-
from enum import IntEnum
    
class LEDCntrl(IntEnum):
    NONE = 0
    START = 1
    STOP = 2

class LEDPattern(IntEnum):
    NONE = 0
    WIPE = 1
    STOP = 2