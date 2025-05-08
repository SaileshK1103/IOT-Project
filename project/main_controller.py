from machine import Pin
import time
import ujson
from umqtt.simple import MQTTClient
from pulse_sensor import PulseSensor
from menu_manager import MenuManager
from oled_display import OledDisplay
from button_handler import ButtonHandler
from hrv_calculator import HRVCalculator
from kubios_uploader import KubiosUploader
from history_manager import HistoryManager

class MainController:
    def __init__(self):
        self.oled = OledDisplay()
        menu_items = ["Heart Rate", "HRV Analysis", "History", "Kubios Upload"]
        self.menu = MenuManager(self.oled.display, menu_items)
        self.buttons = ButtonHandler(stop_pin=7, restart_pin=9, menu_back_pin=8)

        self.pulse = None
        self.hrv = HRVCalculator()
        self.kubios_intervals = []
        self.history = HistoryManager()
        self.last_displayed_hr = None

        self.rot_a = Pin(10, Pin.IN, Pin.PULL_UP)
        self.rot_b = Pin(11, Pin.IN, Pin.PULL_UP)
        self.encoder_button = Pin(12, Pin.IN, Pin.PULL_UP)
        self.last_rot_a = self.rot_a.value()

        self.kubios = KubiosUploader(
            ssid="KMD757_Group_6",
            password="group6-challenger",
            broker_ip="192.168.6.253"
        )

        self.mode = "menu"
        self.sample_start_time = None
        self.hrv_tick_counter = 0
        self.last_tick_time = time.ticks_ms()

    def start_hrv_mode(self):
        self.oled.show_message("HRV Analysis", "Wait 30s")
        self.hrv.clear()
        self.pulse = PulseSensor(adc_pin=27)
        self.pulse.start()
        self.sample_start_time = time.ticks_ms()
        self.hrv_tick_counter = 0
        self.last_tick_time = time.ticks_ms()
        self.mode = "hrv_analysis"

    def start_heart_rate_mode(self):
        self.oled.show_message("Measuring HR", "Wait 5s")
        self.last_displayed_hr = None
        self.pulse = PulseSensor(adc_pin=27)
        self.pulse.start()
        self.sample_start_time = time.ticks_ms()
        self.last_tick_time = time.ticks_ms()
        self.mode = "heart_rate"

    def start_kubios_upload_mode(self):
        self.oled.show_message("Kubios Upload", "Sampling PPI")
        self.kubios_intervals = []
        self.pulse = PulseSensor(adc_pin=27)
        self.pulse.start()
        self.sample_start_time = time.ticks_ms()
        self.mode = "kubios_upload"

    def view_history(self):
        records = self.history.load_all()

        if not records:
            self.oled.show_message("No History", "Found")
            time.sleep(2)
            self.menu.show_menu()
            self.mode = "menu"
            return

        index = 0
        self.oled.show_message("History", f"{len(records)} record(s)")
        time.sleep(1)

        while True:
            record = records[index]
            self.oled.display.fill(0)
            self.oled.display.text(record["timestamp"][11:16], 0, 0)
            self.oled.display.text(f"HR: {record.get('mean_hr', '-')}", 0, 10)
            self.oled.display.text(f"PPI: {record.get('mean_ppi', '-')}", 0, 20)
            self.oled.display.text(f"SDNN: {record.get('sdnn', '-')}", 0, 30)
            self.oled.display.text(f"RMSSD: {record.get('rmssd', '-')}", 0, 40)
            self.oled.display.show()

            time.sleep(2)
            index = (index + 1) % len(records)

            if self.encoder_button.value() == 0:
                while self.encoder_button.value() == 0:
                    time.sleep(0.05)
                self.oled.show_message("Back to Menu", "")
                self.menu.show_menu()
                self.mode = "menu"
                break

    def handle_menu_selection(self, selection):
        if self.pulse:
            self.pulse.stop()
            self.pulse = None
        if selection == "Heart Rate":
            self.start_heart_rate_mode()
        elif selection == "HRV Analysis":
            self.start_hrv_mode()
        elif selection == "History":
            self.view_history()
        elif selection == "Kubios Upload":
            self.start_kubios_upload_mode()

    def run(self):
        while True:
            if self.pulse:
                self.pulse.process_sample()

                if self.pulse.ppi_intervals:
                    latest_ppi = self.pulse.ppi_intervals.pop(0)
                    if 250 < latest_ppi < 1500:
                        if self.mode == "hrv_analysis":
                            self.hrv.add_ppi(latest_ppi)
                        elif self.mode == "kubios_upload":
                            self.kubios_intervals.append(latest_ppi)

            if self.mode == "hrv_analysis":
                elapsed = time.ticks_diff(time.ticks_ms(), self.sample_start_time)

                if time.ticks_diff(time.ticks_ms(), self.last_tick_time) >= 1000:
                    self.hrv_tick_counter += 1
                    self.last_tick_time = time.ticks_ms()
                    self.oled.display.fill(0)
                    self.oled.display.text("HRV Sampling", 0, 0)
                    self.oled.display.text(f"Time: {self.hrv_tick_counter}s", 0, 20)
                    self.oled.display.show()

                if elapsed >= 30000:
                    if self.pulse:
                        self.pulse.stop()
                        self.pulse = None
                    result = self.hrv.calculate_hrv()
                    if result:
                        self.history.save_record(result)
                        self.oled.display.fill(0)
                        self.oled.display.text("HRV Result", 0, 0)
                        self.oled.display.text(f"HR:{int(result['mean_hr'])}", 0, 10)
                        self.oled.display.text(f"RMSSD:{int(result['rmssd'])}", 0, 20)
                        self.oled.display.text(f"SDNN:{int(result['sdnn'])}", 0, 30)
                        self.oled.display.show()
                    else:
                        self.oled.show_message("Not enough", "data")
                    self.mode = "menu"

            elif self.mode == "heart_rate":
                elapsed = time.ticks_diff(time.ticks_ms(), self.sample_start_time)
                if time.ticks_diff(time.ticks_ms(), self.last_tick_time) >= 1000:
                    self.last_tick_time = time.ticks_ms()
                    seconds_passed = elapsed // 1000
                    self.oled.display.fill(0)
                    self.oled.display.text("Measuring HR", 0, 0)
                    self.oled.display.text(f"Time: {seconds_passed}s", 0, 10)
                    if self.pulse.current_hr and 40 <= self.pulse.current_hr <= 240:
                        self.oled.display.text(f"{self.pulse.current_hr} BPM", 0, 30)
                    self.oled.display.show()

                if elapsed >= 5000:
                    self.sample_start_time = time.ticks_ms()
                    hr = self.pulse.current_hr
                    if hr and 40 <= hr <= 240:
                        self.oled.display.fill(0)
                        self.oled.display.text("Pulse Reading", 0, 0)
                        self.oled.display.text(f"{hr} BPM", 0, 20)
                        self.oled.display.show()
                    else:
                        self.oled.show_message("No HR found", "")

            elif self.mode == "kubios_upload":
                elapsed = time.ticks_diff(time.ticks_ms(), self.sample_start_time)
                if elapsed >= 30000:
                    if self.pulse:
                        self.pulse.stop()
                        self.pulse = None
                    if self.kubios_intervals:
                        self.oled.show_message("Uploading to", "Kubios Cloud")
                        success = self.kubios.upload_ppis(self.kubios_intervals)
                        if success:
                            wait_start = time.ticks_ms()
                            self.oled.show_message("Waiting for", "Kubios Result")

                            while time.ticks_diff(time.ticks_ms(), wait_start) < 10000:
                                self.kubios.check_for_response()
                                if self.kubios.analysis_result:
                                    result = self.kubios.analysis_result
                                    self.oled.display.fill(0)
                                    self.oled.display.text("Kubios Result", 0, 0)
                                    self.oled.display.text(f"HR: {int(result.get('mean_hr_bpm', 0))}", 0, 10)
                                    self.oled.display.text(f"RMSSD: {int(result.get('rmssd_ms', 0))}", 0, 20)
                                    self.oled.display.text(f"SDNN: {int(result.get('sdnn_ms', 0))}", 0, 30)
                                    self.oled.display.show()
                                    break
                            else:
                                self.oled.show_message("No Result", "from Kubios")
                        else:
                            self.oled.show_message("Upload", "Failed")
                    else:
                        self.oled.show_message("No PPI", "data")
                    self.mode = "menu"

            new_rot_a = self.rot_a.value()
            if self.last_rot_a == 0 and new_rot_a == 1:
                if self.rot_b.value():
                    self.menu.move_down()
                else:
                    self.menu.move_up()
            self.last_rot_a = new_rot_a

            if self.encoder_button.value() == 0:
                now = time.ticks_ms()
                if time.ticks_diff(now, self.menu.last_button_press) > self.menu.button_debounce_time:
                    selection = self.menu.select()
                    self.handle_menu_selection(selection)
                    self.menu.last_button_press = now

            button_action = self.buttons.check_buttons()
            if button_action == "stop":
                self.mode = "menu"
                if self.pulse:
                    self.pulse.stop()
                    self.pulse = None
                self.oled.show_message("Stopped", "")
            elif button_action == "menu_back":
                self.mode = "menu"
                self.oled.show_message("Back to Menu", "")
                self.menu.show_menu()



