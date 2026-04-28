
import digitalio
import board
import time


class KeyMatrix:

    def __init__(self, row_gpios, col_gpios, key_map, debounce_ms=5):
        self._rows = []
        for gp in row_gpios:
            pin = digitalio.DigitalInOut(getattr(board, f"GP{gp}"))
            pin.direction = digitalio.Direction.OUTPUT
            pin.value = True
            self._rows.append(pin)

        self._cols = []
        for gp in col_gpios:
            pin = digitalio.DigitalInOut(getattr(board, f"GP{gp}"))
            pin.direction = digitalio.Direction.INPUT
            pin.pull = digitalio.Pull.UP
            self._cols.append(pin)

        self._key_map = key_map
        self._debounce_tks = debounce_ms / 1000.0

        nrows = len(row_gpios)
        ncols = len(col_gpios)

        
        self._state = [[False] * ncols for _ in range(nrows)]
        self._raw   = [[False] * ncols for _ in range(nrows)]
        self._changed_at = [[0.0] * ncols for _ in range(nrows)]

    def scan(self):
        pressed  = set()
        released = set()
        now = time.monotonic()

        for r, row_pin in enumerate(self._rows):
            row_pin.value = False 
            time.sleep(0.000002) 

            for c, col_pin in enumerate(self._cols):
                raw_now = not col_pin.value
                note = self._key_map[r][c]

                if note is None:
                    continue

                if raw_now != self._raw[r][c]:
                    
                    self._raw[r][c]        = raw_now
                    self._changed_at[r][c] = now
                else:
                    
                    if raw_now != self._state[r][c]:
                        if (now - self._changed_at[r][c]) >= self._debounce_tks:
                            self._state[r][c] = raw_now
                            if raw_now:
                                pressed.add(note)
                            else:
                                released.add(note)

            row_pin.value = True

        return pressed, released

    def all_released(self):
        return all(
            not self._state[r][c]
            for r in range(len(self._rows))
            for c in range(len(self._cols))
            if self._key_map[r][c] is not None
        )