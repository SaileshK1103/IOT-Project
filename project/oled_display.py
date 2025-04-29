from machine import Pin, I2C
from ssd1306 import SSD1306_I2C

class OledDisplay:
    def __init__(self, scl=15, sda=14):
        i2c = I2C(1, scl=Pin(scl), sda=Pin(sda), freq=400000)
        self.display = SSD1306_I2C(128, 64, i2c)

    def show_message(self, title, line2=""):
        self.display.fill(0)
        self.display.text(title, 0, 0)
        self.display.text(line2, 0, 20)
        self.display.show()

