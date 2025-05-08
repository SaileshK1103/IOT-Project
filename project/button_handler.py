from machine import Pin
import time

class ButtonHandler:
    def __init__(self, stop_pin, restart_pin, menu_back_pin):
        self.stop_button = Pin(stop_pin, Pin.IN, Pin.PULL_UP)
        self.restart_button = Pin(restart_pin, Pin.IN, Pin.PULL_UP)
        self.menu_back_button = Pin(menu_back_pin, Pin.IN, Pin.PULL_UP)
        self.last_press_time = time.ticks_ms()
        self.debounce_ms = 200

    def check_buttons(self):
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press_time) > self.debounce_ms:
            if self.stop_button.value() == 0:
                self.last_press_time = now
                return "stop"
            elif self.restart_button.value() == 0:
                self.last_press_time = now
                return "restart"
            elif self.menu_back_button.value() == 0:
                self.last_press_time = now
                return "menu_back"
        return None



