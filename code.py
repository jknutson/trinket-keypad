"""CircuitPython Essentials HID Keyboard example"""
import time

import board
import digitalio
import usb_hid
import neopixel
import rotaryio
import adafruit_dotstar

KEYBOARD_ENABLED = False

if KEYBOARD_ENABLED:
  from adafruit_hid.keyboard import Keyboard
  from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
  from adafruit_hid.keycode import Keycode

DEBUG = True

OFF = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

vu_colors = [
    GREEN,
    GREEN,
    GREEN,
    YELLOW,
    YELLOW,
    YELLOW,
    RED,
    RED,
    ]
# TODO: figure out why this seems to always have a "base" of 1 green led...
#       cardinal vs ordinal im guessing
def show_vu(pixels, level, offset=0):
  if level > len(vu_colors):
    return
  for idx, color in enumerate(vu_colors):
    if idx <= level:
      pixels[idx + offset] = vu_colors[idx]
      pixels.show()
    else:
      pixels[idx + offset] = OFF
      pixels.show()

def colorwheel(pos):
  # Input a value 0 to 255 to get a color value.
  # The colours are a transition r - g - b - back to r.
  if pos < 0 or pos > 255:
    return (0, 0, 0)
  if pos < 85:
    return (255 - pos * 3, pos * 3, 0)
  if pos < 170:
    pos -= 85
    return (0, 255 - pos * 3, pos * 3)
  pos -= 170
  return (pos * 3, 0, 255 - pos * 3)

modes = [
    {
      'name': 'zoom',
      'color': BLUE,
      },
    {
      'name': 'chrome',
      'color': YELLOW,
      },
    {
      'name': 'osx',
      'color': PURPLE,
      },
    {
      'name': 'lightroom',
      'color': CYAN,
      }
    ]
modes_index = 0

# The pins we'll use, each will have an internal pullup
keypress_pins = [board.A1, board.A2]
# Our array of key objects
key_pin_array = []

encoder = rotaryio.IncrementalEncoder(board.D1, board.D4)
last_position = None

# NeoPixels
pixel_pin = board.A3
num_pixels = 10
pixels = neopixel.NeoPixel(pixel_pin, num_pixels, brightness=0.5, auto_write=False)
# pixels.fill(BLUE)
pixels[0] = BLUE
pixels[1] = BLUE
pixels.show()

# onboard DotStar
dotstar = adafruit_dotstar.DotStar(board.APA102_SCK, board.APA102_MOSI, 1, brightness=0.1, auto_write=False)

# onboard LED
led = digitalio.DigitalInOut(board.D13)
led.direction = digitalio.Direction.OUTPUT
led.value = 1

# inital mic/mute state
mic_hot = False

if KEYBOARD_ENABLED:
  time.sleep(1)  # Sleep for a bit to avoid a race condition on some systems
  keyboard = Keyboard(usb_hid.devices)
  keyboard_layout = KeyboardLayoutUS(keyboard)

# Make all pin objects inputs with pullups
for pin in keypress_pins:
  key_pin = digitalio.DigitalInOut(pin)
  key_pin.direction = digitalio.Direction.INPUT
  key_pin.pull = digitalio.Pull.UP
  key_pin_array.append(key_pin)

print("waiting for input...")

def toggle_mute():
  print('toggle_mute')
  if DEBUG:
    return
  global mic_hot
  keyboard.press(Keycode.COMMAND, Keycode.SHIFT, Keycode.A)
  keyboard.release_all()
  mic_hot = not mic_hot

def leave_call():
  print('leave_call')
  if DEBUG:
    return
  keyboard.press(Keycode.COMMAND, Keycode.W)
  keyboard.release_all()
  keyboard.send(Keycode.ENTER)

while True:
  # check encoder
  position = encoder.position
  if last_position is None or position != last_position:
    # print("rotary position: %s" % (position))
    # TODO: using abs isn't perfect, esp around -1, 0, 1
    modes_index = abs(position) % len(modes)
    print(modes[modes_index]['name'])
    # dotstar[0] = modes[modes_index]['color']
    # dotstar.show()
  last_position = position

  # just for fun
  dotstar[0] = colorwheel(abs(position * 3))
  dotstar.show()
  show_vu(pixels, abs(position), 2)

  # Check each pin
  for key_pin in key_pin_array:
    if not key_pin.value:  # Is it grounded?
      i = key_pin_array.index(key_pin)
      print("Pin #%d is grounded." % i)

      pixels[i] = WHITE
      pixels.show()
      while not key_pin.value:
        pass  # Wait for it to be ungrounded!
      pixels[i] = BLUE
      pixels.show()
      if i == 0:
        leave_call()
      else:
        toggle_mute()
  # time.sleep(0.1) # try speeding this up...
  time.sleep(0.05)
