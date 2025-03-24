import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# OLED setup
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# Button setup
sw0 = Pin(9, Pin.IN, Pin.PULL_UP)  # Move right
sw2 = Pin(7, Pin.IN, Pin.PULL_UP)  # Move left

# UFO initial position (center-bottom)
ufo_x = 48  # Start in the middle of the screen
ufo_y = 56  # Near the bottom

def draw_ufo(x, y):
    oled.fill(0)  # Clear screen
    oled.text("<=>", x, y, 1)  # Draw UFO
    oled.show()

# Initial UFO drawing
draw_ufo(ufo_x, ufo_y)

while True:
    if not sw0.value() and ufo_x < 104:  # Move right, limit to screen width
        ufo_x += 8  # Move step
        draw_ufo(ufo_x, ufo_y)
        time.sleep(0.2)  # Prevent button spamming
    
    if not sw2.value() and ufo_x > 0:  # Move left, limit to 0
        ufo_x -= 8
        draw_ufo(ufo_x, ufo_y)
        time.sleep(0.2)
