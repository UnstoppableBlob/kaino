import rotaryio
import digitalio
import board
import time


class RotaryEncoder:

    def __init__(self, a_gpio, b_gpio, btn_gpio,
                 min_val=0, max_val=127, initial=100,
                 btn_debounce_ms=30, long_press_ms=600):

        self._enc = rotaryio.IncrementalEncoder(
            getattr(board, f"GP{a_gpio}"),
            getattr(board, f"GP{b_gpio}"),
        )
        self._enc.position = 0

        self._btn = digitalio.DigitalInOut(getattr(board, f"GP{btn_gpio}"))
        self._btn.direction = digitalio.Direction.INPUT
        self._btn.pull = digitalio.Pull.UP

        self._min = min_val
        self._max = max_val
        self._value = initial
        self._last_pos = 0

        self._btn_debounce  = btn_debounce_ms / 1000.0
        self._long_press_ms = long_press_ms / 1000.0

        self._btn_raw_last = True
        self._btn_state = True
        self._btn_changed_at = 0.0
        self._btn_pressed_at = 0.0
        self._long_reported = False
        
        
        
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, v):
        self._value = max(self._min, min(self._max, int(v)))



    def tick(self, step=1):
      
        delta = 0
        short_press = False
        long_press  = False
        now = time.monotonic()

        pos = self._enc.position
        d = pos - self._last_pos
        if d != 0:
            self._last_pos = pos
            new_val = max(self._min, min(self._max, self._value + d * step))
            delta = new_val - self._value
            self._value = new_val


        raw = self._btn.value
        if raw != self._btn_raw_last:
            self._btn_raw_last   = raw
            self._btn_changed_at = now

        if raw != self._btn_state:
            if (now - self._btn_changed_at) >= self._btn_debounce:
                self._btn_state = raw
                if not raw:
                    
                    self._btn_pressed_at = now
                    self._long_reported  = False
                else:
                    
                    held = now - self._btn_pressed_at
                    if held < self._long_press_ms and not self._long_reported:
                        short_press = True


        if (not self._btn_state and not self._long_reported and
                (now - self._btn_pressed_at) >= self._long_press_ms):
            long_press          = True
            self._long_reported = True

        return delta, short_press, long_press