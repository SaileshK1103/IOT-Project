from pulse_sensor import PulseSensor
from menu_manager import MenuManager
from oled_display import OledDisplay
from button_handler import ButtonHandler
from hrv_calculator import HRVCalculator

from machine import Pin
import time

class MainController:
    def __init__(self):
        # Setup OLED
        self.oled = OledDisplay()

        # Setup Menu
        menu_items = ["Heart Rate", "HRV Analysis", "History", "Kubios Upload"]
        self.menu = MenuManager(self.oled.display, menu_items)

        # Setup Buttons
        self.buttons = ButtonHandler(stop_pin=7, restart_pin=9, menu_back_pin=8)

        # Setup Pulse Sensor
        self.pulse = None

        # HRV Calculator
        self.hrv = HRVCalculator()

        # Rotary encoder
        self.rot_a = Pin(10, Pin.IN, Pin.PULL_UP)
        self.rot_b = Pin(11, Pin.IN, Pin.PULL_UP)
        self.encoder_button = Pin(12, Pin.IN, Pin.PULL_UP)
        self.last_rot_a = self.rot_a.value()

    def handle_menu_selection(self, selection):
        self.oled.show_message("Selected:", selection)
        time.sleep(0.5)

        if self.pulse:
            self.pulse.stop()
            self.pulse = None

        if selection == "Heart Rate":
            self.pulse = PulseSensor(adc_pin=27)
            self.pulse.start()

        elif selection == "HRV Analysis":
            valid_ppis = [p for p in self.hrv.ppi_list if 300 < p < 1500]
            print("Valid HRV PPIs:", valid_ppis)
            
            if len(valid_ppis) >= 2:
                result = self.hrv.calculate_hrv()
                self.oled.display.fill(0)
                self.oled.display.text("HRV Result", 0, 0)
                self.oled.display.text(f"HR:{int(result['mean_hr'])}", 0, 10)
                self.oled.display.text(f"RMSSD:{int(result['rmssd'])}", 0, 20)
                self.oled.display.text(f"Samples: {result['sample_count']}", 0, 30)
                self.oled.display.show()
                print(result)
            else:
                self.oled.show_message("Not enough clean HRV data")

        elif selection == "History":
            self.oled.show_message("History", "Coming soon")

        elif selection == "Kubios Upload":
            self.oled.show_message("Uploading...", "Coming soon")

    def run(self):
        """Main program loop"""
        while True:
            # Rotary encoder turn
            new_rot_a = self.rot_a.value()
            if self.last_rot_a == 0 and new_rot_a == 1:
                if self.rot_b.value():
                    self.menu.move_down()
                else:
                    self.menu.move_up()
            self.last_rot_a = new_rot_a

            # Encoder button press
            if self.encoder_button.value() == 0:
                now = time.ticks_ms()
                if time.ticks_diff(now, self.menu.last_button_press) > self.menu.button_debounce_time:
                    selection = self.menu.select()
                    self.handle_menu_selection(selection)
                    self.menu.last_button_press = now

            # Switches (stop/restart/menu_back)
            button_action = self.buttons.check_buttons()
            if button_action == "stop":
                if self.pulse:
                    while self.pulse.ppi_intervals:
                        latest_ppi = self.pulse.ppi_intervals.pop(0)
                        if 300 < ppi < 1500:
                            print("Saving leftover PPI:", latest_ppi)
                            self.hrv.add_ppi(latest_ppi)
                        else:
                            print("Reject noisy leftouver PPI:", latest_ppi)
                        
                    self.pulse.stop()
                    self.pulse = None
                    
                self.oled.show_message("Stopped", "")

            elif button_action == "restart":
                if self.pulse is None:
                    self.pulse = PulseSensor(adc_pin=27)
                    self.pulse.start()
                    self.oled.show_message("Restarted", "")

            elif button_action == "menu_back":
                self.oled.show_message("Back to Menu", "")
                time.sleep(0.5)
                self.menu.show_menu()

            # Process pulse data
            if self.pulse:
                self.pulse.process_sample()
                
                # move ppi data to hrv calculator
                if self.pulse.ppi_intervals:
                    latest_ppi = self.pulse.ppi_intervals.pop(0)  # get the first unprocessed ppi
                    #only save realistic intervals
                    if 300 <latest_ppi < 1500:
                        print("Saving valid PPI to HRV:", latest_ppi)
                        self.hrv.add_ppi(latest_ppi)
                    else:
                        print("Rejected noisy PPI", latest_ppi)
                    
                    if self.pulse.current_hr:
                        if 40 <= self.pulse.current_hr >= 180:
                            self.oled.display.fill(0)
                            self.oled.display.text("Heart Rate", 0, 0)
                            self.oled.display.text(f"{self.pulse.current_hr} BPM", 0, 20)
                            self.oled.display.show()
                    
                # OLED live HR display
                if self.pulse.current_hr:
                    self.oled.display.fill(0)
                    self.oled.display.text("Heart Rate", 0, 0)
                    self.oled.display.text(f"{self.pulse.current_hr} BPM", 0, 20)
                    self.oled.display.show()

            time.sleep(0.01)


