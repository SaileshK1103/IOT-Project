# IOT-Project
# Oled : Task 1.1
Implement a program that uses the two development board buttons to control a “UFO”. The UFO is
shown at the bottom of the screen with characters “<=>”. SW0 and SW2 are used to move the UFO left
and right. The program must stop the UFO at the edges of the screen so that it is completely visible.
When UFO is at left edge it must only be possible to move the UFO right and vice versa.

# Task 1.2
Implement a program that reads user input from the keyboard in an infinite loop. The input is typed in
Thonny Shell window while the program is running. The user input is drawn to the OLED screen starting
from the top of the screen. Each input is drawn below the previous one. When the screen is full the
display is scrolled up by one line and then new text is drawn at the bottom of the screen.

# Task 1.3
Implement a program that uses the three development board buttons to control line drawing. When the
program starts, it starts to draw pixels from the left side of the screen halfway between top and bottom
of the screen and constantly moves towards the right edge of the screen. When the drawing reaches the
right edge of the screen, the drawing is wrapped back to the left side. Buttons SW0 and SW2 are used to
move the pixels towards the top or bottom of the screen, so that by pressing buttons you can draw lines
at different heights. Pressing SW1 clears the screen and continues drawing from middle left side.