import time

class MenuManager:
    def __init__(self, display, items):
        self.display = display
        self.items = items
        self.current_index = 0
        self.last_button_press = time.ticks_ms()
        self.button_debounce_time = 200  # milliseconds

        self.show_menu()

    def show_menu(self):
        self.display.fill(0)
        for i, item in enumerate(self.items):
            prefix = ">" if i == self.current_index else " "
            self.display.text(f"{prefix} {item}", 0, i * 10)
        self.display.show()

    def move_up(self):
        self.current_index = (self.current_index - 1) % len(self.items)
        self.show_menu()

    def move_down(self):
        self.current_index = (self.current_index + 1) % len(self.items)
        self.show_menu()

    def select(self):
        return self.items[self.current_index]

