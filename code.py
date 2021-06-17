import time

import board
import digitalio
import usb_hid
import rotaryio

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

encoder = rotaryio.IncrementalEncoder(board.A0, board.A4)
last_position = None

keypress_pins = [
    board.A1,
    board.A2,
    board.A3
]

key_pin_array = []
mic_hot = False
video_hot = False
time.sleep(1)
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

for pin in keypress_pins:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.UP
    key_pin_array.append(key_pin)

led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
print("Waiting for key pin...")

def toggle_mute():
    global mic_hot
    keyboard.press(Keycode.COMMAND, Keycode.SHIFT, Keycode.A)
    keyboard.release_all()
    mic_hot = not mic_hot
    led.value = mic_hot
    print('toggle mute, value: %d' % mic_hot)

def toggle_video():
    global video_hot
    keyboard.press(Keycode.COMMAND, Keycode.SHIFT, Keycode.V)
    keyboard.release_all()
    video_hot = not video_hot
    # led.value = mic_hot
    print('toggle video, value: %d' % video_hot)

def leave_call():
    keyboard.press(Keycode.COMMAND, Keycode.W)
    keyboard.release_all()
    keyboard.send(Keycode.ENTER)
    print('leaving call')

while True:
    # Check each pin
    for key_pin in key_pin_array:
        if not key_pin.value:
            i = key_pin_array.index(key_pin)
            print("Pin #%d is grounded." % i)

            while not key_pin.value:
                pass
            if i == 0:
                leave_call()
            elif i == 1:
                toggle_video()
            else:
                toggle_mute()


    position = encoder.position
    if last_position is None or position != last_position:
        print(position)
    last_position = position
    time.sleep(0.1)
