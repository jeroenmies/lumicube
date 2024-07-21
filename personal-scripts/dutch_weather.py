import datetime
import traceback
from pathlib import Path
import pyttsx3

import requests

show_rain = True
show_full_msg = False

display.set_all(black)

try:
    while True:
        if buttons.top_pressed:
            show_full_msg = not show_full_msg
        if buttons.middle_pressed:
            show_rain = not show_rain

        time.sleep(refresh_rate)
except Exception:
    print(traceback.format_exc())
    screen.draw_rectangle(0, 0, 320, 240, black)
    screen.write_text(0, 0, traceback.format_exc(), 1, black, white)
