"""Run on K10 MicroPython vendor firmware. USB serial JSON events at 115200.

Native QR identification is spatially resolved by a surveyed target table on
host. Cat/dog mode is a classification demo, never a grasp target.
"""
import ai
import time
import json
from unihiker_k10 import screen
MODE = "qr"  # "qr" or "catdog"; do not enable WiFi alongside AI on firmware 0.9.8.
ai.init_ai()
ai.camera_start()
if MODE == "qr":
    ai.code_scanner()
else:
    ai.cat_detect()
screen.init()
last_emit = time.ticks_ms()
try:
    while True:
        screen.show_camera_img(ai.camera_capture())
        if ai.is_ai_data_updated():
            result = ai.get_ai_data()
            if time.ticks_diff(time.ticks_ms(), last_emit) >= 250:
                last_emit = time.ticks_ms()
                if MODE == "qr" and result.get("code_data"):
                    print(json.dumps({"kind": "qr", "code": result["code_data"]}))
                elif MODE == "catdog":
                    print(json.dumps({"kind": "classification", "cat_flag": bool(result.get("cat_flag", False))}))
        time.sleep_ms(10)
finally:
    ai.deinit_ai()
