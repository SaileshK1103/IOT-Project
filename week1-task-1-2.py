import time
from machine import I2C, Pin
from ssd1306 import SSD1306_I2C

# OLED setup
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

lines = []  # Store text lines

while True:
    user_input = input("Enter text: ")  # Read from Thonny Shell
    lines.append(user_input)  # Store input

    # If more than 8 lines, scroll up
    if len(lines) > 8:
        lines.pop(0)

    # Clear and redraw screen
    oled.fill(0)
    for i, line in enumerate(lines):
        oled.text(line, 0, i * 8, 1)  # Draw each line
    oled.show()
