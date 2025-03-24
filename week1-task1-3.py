import time
from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

# OLED setup
i2c = I2C(1, scl=Pin(15), sda=Pin(14), freq=400000)
oled = SSD1306_I2C(128, 64, i2c)

# Button setup
sw0 = Pin(9, Pin.IN, Pin.PULL_UP)  # Move up
sw2 = Pin(7, Pin.IN, Pin.PULL_UP)  # Move down
sw1 = Pin(8, Pin.IN, Pin.PULL_UP)  # Clear and restart

# Initial position
x = 0
y = 32  # Start in the middle

while True:
    # Move UP as long as SW0 is held
    if not sw0.value() and y > 0:
        while not sw0.value() and y > 0:  # Keep moving up
            y -= 1
            oled.pixel(x, y, 1)
            oled.show()
            time.sleep(0.02)  # Small delay for smooth movement

    # Move DOWN as long as SW2 is held
    elif not sw2.value() and y < 63:
        while not sw2.value() and y < 63:  # Keep moving down
            y += 1
            oled.pixel(x, y, 1)
            oled.show()
            time.sleep(0.02)  # Small delay for smooth movement

    # Move RIGHT when no vertical movement is needed
    x += 1
    if x >= 128:  # Wrap back to left if reaching the right edge
        x = 0
        oled.fill(0)  # Clear screen for new signal wave

    oled.pixel(x, y, 1)  # Draw horizontal line segment
    oled.show()

    # If SW1 is pressed, clear the screen and restart
    if not sw1.value():
        x = 0
        y = 32
        oled.fill(0)
        oled.show()
        time.sleep(0.5)

    time.sleep(0.02)  # Small delay for smooth movement
