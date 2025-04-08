from machine import Pin
from fifo import Fifo
import time

# === Setup ===
led_pins = [20, 21, 22]
leds = [Pin(pin, Pin.OUT) for pin in led_pins]
led_states = [False, False, False]

menu_index = 0  # Start at LED1

fifo = Fifo(10)

# === Rotary Encoder Setup ===
class Encoder:
    def __init__(self, pin_a, pin_b, button_pin):
        self.a = Pin(pin_a, Pin.IN, Pin.PULL_UP)
        self.b = Pin(pin_b, Pin.IN, Pin.PULL_UP)
        self.btn = Pin(button_pin, Pin.IN, Pin.PULL_UP)

        self.last_press_time = 0

        self.a.irq(trigger=Pin.IRQ_RISING, handler=self.turn_handler)
        self.btn.irq(trigger=Pin.IRQ_FALLING, handler=self.button_handler)

    def turn_handler(self, pin):
        # Detects the direction of the rotary encoder
        if self.b.value():  # Clockwise
            fifo.put(1)  # Use 1 to represent "right"
        else:  # Counterclockwise
            fifo.put(-1)  # Use -1 to represent "left"

    def button_handler(self, pin):
        # Debounce handling for the button press
        now = time.ticks_ms()
        if time.ticks_diff(now, self.last_press_time) > 50:
            fifo.put(0)  # Use 0 to represent "press"
            self.last_press_time = now

# Init encoder (adjust pins if needed)
rot = Encoder(10, 11, 12)  # A, B, Button

# === Menu Display ===
def display_menu():
    for i in range(3):
        prefix = ">"
        if i == menu_index:
            line = f"[LED{i+1} – {'ON ' if led_states[i] else 'OFF'}]"
        else:
            line = f" LED{i+1} – {'ON ' if led_states[i] else 'OFF'}"
        print(line)
    print()  # Newline for spacing

# === Main Loop ===
while True:
    if fifo.has_data():
        event = fifo.get()

        if event == 1:  # Right turn
            menu_index = (menu_index + 1) % 3
        elif event == -1:  # Left turn
            menu_index = (menu_index - 1) % 3
        elif event == 0:  # Button press
            led_states[menu_index] = not led_states[menu_index]
            leds[menu_index].value(led_states[menu_index])

        # Refresh menu
        print("\033c", end="")  # Clear terminal (if supported)
        display_menu()

    time.sleep_ms(50)

