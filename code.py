import board
import digitalio
import time
import adafruit_ble
from adafruit_ble.advertising import Advertisement
from adafruit_ble.advertising.standard import ProvideServicesAdvertisement
from adafruit_ble.services.standard.hid import HIDService
from adafruit_ble.services.standard.device_info import DeviceInfoService
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

button1 = digitalio.DigitalInOut(board.D5)
button1.direction = digitalio.Direction.INPUT
button2 = digitalio.DigitalInOut(board.D6)
button2.direction = digitalio.Direction.INPUT

hid = HIDService()

device_info = DeviceInfoService(
    software_revision=adafruit_ble.__version__, manufacturer="Marla Industries"
)

advertisement = ProvideServicesAdvertisement(hid)
advertisement.appearance = 961
scan_response = Advertisement()
scan_response.complete_name = "Zwift Remote"

ble = adafruit_ble.BLERadio()

if not ble.connected:
    print("advertising")
    ble.start_advertising(advertisement, scan_response)
else:
    print("already connected")
    print(ble.connections)
keyboard = Keyboard(hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)

perspective = 1

while True:
    while not ble.connected:
        pass
    print("start typing: ")
    while ble.connected:
        button1_pressed = not button1.value
        button2_pressed = not button2.value
        if button1_pressed:
            keyboard.send(Keycode.SPACE)
        if button2_pressed:
            perspective = (perspective + 1) % 10
            keyboard_layout.write(f"{perspective}")
        if button1_pressed or button2_pressed:
            time.sleep(0.3)
