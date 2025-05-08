from machine import ADC
from fifo import Fifo
from piotimer import Piotimer
from led import Led


class PulseSensor:
    def __init__(self, adc_pin, sample_rate=250):
        self.adc = ADC(adc_pin)
        self.samples = Fifo(1000)
        self.sample_rate = sample_rate
        self.timer = None
        self.sample_index = 0
        self.ppi_intervals = []
        self.prev_value = 0
        self.threshold = 0
        self.th_factor = 0.5  # Made more sensitive
        self.th_counter = 0
        self.in_peak_area = False
        self.peak_found = False
        self.led = Led(22)
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
        except:
            pass

    def process_sample(self):
        if self.samples.empty():
            return

        value = self.samples.get()
        self.sample_index += 1

        if self.th_counter == 0:
            minimum = min(self.samples.data)
            maximum = max(self.samples.data)
            self.threshold = int(minimum + self.th_factor * (maximum - minimum))
            print(f"[DEBUG] Min: {minimum}, Max: {maximum}, Threshold: {self.threshold}")

        self.th_counter += 1
        if self.th_counter >= 250:
            self.th_counter = 0

        # Debug: print raw ADC value
        print(f"[DEBUG] ADC: {value}")

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
                ppi_ms = int((ppi * 1000) / self.sample_rate)
                hr = int(60000 / ppi_ms)
                print(f"[DEBUG] Peak found! PPI: {ppi_ms} ms, HR: {hr}")
                if 30 < hr < 240:
                    self.ppi_intervals.append(ppi_ms)
                    self.current_hr = hr
                self.sample_index = 0

        self.prev_value = value



