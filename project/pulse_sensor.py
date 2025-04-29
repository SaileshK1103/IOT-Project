from machine import ADC
from fifo import Fifo
from piotimer import Piotimer
from led import Led

class PulseSensor:
    def __init__(self, adc_pin, sample_rate=250):
        self.adc = ADC(adc_pin)
        self.samples = Fifo(500)
        self.sample_rate = sample_rate
        self.timer = None
        self.sample_index = 0
        self.ppi_intervals = []
        self.prev_value = 0
        self.threshold = 0
        self.th_factor = 0.80
        self.in_peak_area = False
        self.peak_found = False
        self.led = Led(22)  # Heartbeat LED
        self.led.off()
        self.current_hr = None

    def start(self):
        self.timer = Piotimer(mode=Piotimer.PERIODIC, freq=self.sample_rate, callback=self.handler)

    def stop(self):
        if self.timer:
            self.timer.deinit()
            self.timer = None

    def handler(self, tid):
        try:
            self.samples.put(self.adc.read_u16())
        except Exception:
            pass

    def process_sample(self):
        if not self.samples.empty():
            value = self.samples.get()
            self.sample_index += 1

            minimum = min(self.samples.data)
            maximum = max(self.samples.data)
            self.threshold = int(minimum + self.th_factor * (maximum - minimum))

            if not self.in_peak_area:
                if value > self.threshold:
                    self.in_peak_area = True
                    self.led.on()
            else:
                if value <= self.threshold:
                    self.in_peak_area = False
                    self.led.off()
                    self.peak_found = False

            if self.in_peak_area and not self.peak_found:
                if self.prev_value > value:
                    self.peak_found = True
                    ppi = self.sample_index - 1
                    ppi_ms = 4 * ppi
                    if ppi_ms < 250:
                        return
                    hr = int(60000 / ppi_ms)
                    if 30 < hr < 240:
                        print("HR:", hr)
                        self.ppi_intervals.append(ppi_ms)
                        self.current_hr = hr # Save latest HR here
                    self.sample_index = 9

            self.prev_value = value

