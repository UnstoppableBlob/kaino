
# Encoder short-press = cycle through channels
#Encoder long-press = octave up
# Encoder rotation = volume 

import time
import usb_midi
import adafruit_midi
from adafruit_midi.note_on import NoteOn
from adafruit_midi.note_off import NoteOff
from adafruit_midi.control_change import ControlChange

import config
from matrix import KeyMatrix
from encoder import RotaryEncoder
from display_ui import KeyboardDisplay

print("booting")

midi = adafruit_midi.MIDI(
    midi_out=usb_midi.ports[1],
    out_channel=config.MIDI_CHANNEL,
)

matrix  = KeyMatrix(
    row_gpios  = config.ROW_GPIO,
    col_gpios  = config.COL_GPIO,
    key_map    = config.KEY_MAP,
    debounce_ms= config.DEBOUNCE_MS,
)

enc = RotaryEncoder(
    a_gpio   = config.ENC_A_GPIO,
    b_gpio   = config.ENC_B_GPIO,
    btn_gpio = config.ENC_BTN_GPIO,
    min_val  = 0,
    max_val  = 127,
    initial  = config.DEFAULT_VOLUME,
)

display = KeyboardDisplay(config)


volume        = config.DEFAULT_VOLUME
octave_shift  = 0
midi_channel  = config.MIDI_CHANNEL
active_notes  = set()
OCTAVE_RANGE  = (-3, 3)


midi.send(ControlChange(7, volume))

print("Boot complete — entering main loop")
display.update(active_notes, volume, octave_shift)



def shifted(note):
    return max(0, min(127, note + octave_shift * 12))


def all_notes_off():
    for n in list(active_notes):
        midi.send(NoteOff(n, 0))
    active_notes.clear()


display_dirty = True

while True:

    pressed_raw, released_raw = matrix.scan()

    for raw_note in pressed_raw:
        note = shifted(raw_note)
        if note not in active_notes:
            midi.send(NoteOn(note, volume))
            active_notes.add(note)
            display_dirty = True
            print(f"NoteOn  {note}  vel={volume}")

    for raw_note in released_raw:
        note = shifted(raw_note)
        if note in active_notes:
            midi.send(NoteOff(note, 0))
            active_notes.discard(note)
            display_dirty = True
            print(f"NoteOff {note}")

    vol_delta, short_press, long_press = enc.tick(step=config.VOLUME_STEP)

    if vol_delta != 0:
        volume = enc.value
        midi.send(ControlChange(7, volume))
        display_dirty = True
        print(f"Volume → {volume}")


    if short_press:
        all_notes_off()
        midi_channel = (midi_channel + 1) % 16
        midi = adafruit_midi.MIDI(
            midi_out=usb_midi.ports[1],
            out_channel=midi_channel,
        )
        midi.send(ControlChange(7, volume))
        display_dirty = True
        print(f"MIDI channel → {midi_channel + 1}")


    if long_press:
        all_notes_off()
        lo, hi = OCTAVE_RANGE
        octave_shift = lo if octave_shift >= hi else octave_shift + 1
        display_dirty = True
        print(f"Octave shift → {octave_shift:+d}")


    if display_dirty:
        display.update(active_notes, volume, octave_shift)
        display_dirty = False


    time.sleep(0.001)