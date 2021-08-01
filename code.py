"""CircuitPython Essentials HID Keyboard example"""
import time
 
import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
 
# The pins we'll use, each will have an internal pullup
keypress_pins = [board.A1, board.A2]
# Our array of key objects
key_pin_array = []
# The Keycode sent for each button, will be paired with a control key

# inital mic/mute state
mic_hot = False
 
# The keyboard object!
time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # We're in the US :)
 
# Make all pin objects inputs with pullups
for pin in keypress_pins:
    key_pin = digitalio.DigitalInOut(pin)
    key_pin.direction = digitalio.Direction.INPUT
    key_pin.pull = digitalio.Pull.UP
    key_pin_array.append(key_pin)
 
# For most CircuitPython boards:
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
 
print("Waiting for key pin...")

def toggle_mute():
    global mic_hot
    keyboard.press(Keycode.COMMAND, Keycode.SHIFT, Keycode.A)
    keyboard.release_all()
    mic_hot = not mic_hot
    led.value = mic_hot

def leave_call():
    keyboard.press(Keycode.COMMAND, Keycode.W)
    keyboard.release_all()
    keyboard.send(Keycode.ENTER)
 
while True:
    # Check each pin
    for key_pin in key_pin_array:
        if not key_pin.value:  # Is it grounded?
            i = key_pin_array.index(key_pin)
            print("Pin #%d is grounded." % i)
 
            while not key_pin.value:
                pass  # Wait for it to be ungrounded!
            if i == 0:
                leave_call()
            else:
                toggle_mute()
    time.sleep(0.1)
