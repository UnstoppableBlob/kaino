
MIDI_CHANNEL = 0       
DEFAULT_VELOCITY = 100 
DEFAULT_VOLUME = 100 
VOLUME_STEP = 3  
BASE_OCTAVE = 4 


ROW_GPIO = [0, 1, 2, 3]


COL_GPIO = [4, 5, 6, 7, 8, 9, 10]


#   row0 = first-octave  black keys  =  C#4 D#4  –  F#4 G#4 A#4  –
#   row1 = first-octave  white keys  =  C4  D4  E4  F4  G4  A4  B4
#   row2 = second-octave black keys  =  C#5 D#5  –  F#5 G#5 A#5  C6
#   row3 = second-octave white keys  =  C5  D5  E5  F5  G5  A5  B5
#
#         col0  col1  col2  col3  col4  col5  col6
KEY_MAP = [
    [61,   63,   None, 66,   68,   70,   None],
    [60,   62,   64,   65,   67,   69,   71  ],
    [73,   75,   None, 78,   80,   82,   84  ],
    [72,   74,   76,   77,   79,   81,   83  ],
]


ENC_A_GPIO   = 11
ENC_B_GPIO   = 12
ENC_BTN_GPIO = 15



LCD_DC_GPIO   = 13  # GP13 - data
LCD_RST_GPIO  = 14  # GP14 - reset
LCD_BL_GPIO   = 16  # GP16 - backlight
LCD_CS_GPIO   = 17  # GP17 - chip select
LCD_SCK_GPIO  = 18  # GP18 - SPI clock
LCD_MOSI_GPIO = 19  # GP19 - SPI data


LCD_WIDTH     = 128
LCD_HEIGHT    = 160   
LCD_ROTATION  = 0
LCD_BGR       = True 


DEBOUNCE_MS   = 5   