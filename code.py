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
allowed_pause_for_double = 0.1
long_pressed_treshold = 1
a = time.time()
pressed_phase = False
double_click_phase = 0


def long_press(elapsed):
    if elapsed > long_pressed_treshold:
        return 0
    else:
        return 1


while True:
    while not ble.connected:
        pass
    print("start typing: ")
    while ble.connected:
        button1_pressed = not button1.value
        button2_pressed = not button2.value
        if button1_pressed:  # wenn Knopf 1 gedrückt ist
            if not pressed_phase:  # und vorher nicht gedrückt war
                a = time.time()  # Startzeit merken
                pressed_phase = True  # und merken, dass er jetzt gedrückt wurde
        else:  # wenn Knopf 1 nicht gedrückt ist
            if pressed_phase:  # und vorher gedrückt war
                elapsed = time.time() - a  # abfragen, wie lange er vorher gedrückt war
                a = time.time()  # Zeit aktualisieren
                pressed_phase = False  # merken, dass er vorher nicht gedrückt war
                double_click_phase += long_press(
                    elapsed
                )  # und merken, wie oft er jetzt in kurzer Zeit gedrückt wurde
                if double_click_phase == 2:  # wenn Doppelklick vollständig ist
                    double_click_phase = 0  # Klickanzahl zurücksetzen
                    keyboard.send(Keycode.ALT, Keycode.TAB, Keycode.TAB) # und Fenster wechseln
            else:  # und vorher nicht gedrückt war
                elapsed = time.time() - a  # Zeit abfragen, die er nicht gedrückt wurde
                if (
                    elapsed > allowed_pause_for_double and double_click_phase > 0
                ):  # Einzelklick erkennen
                    perspective = (perspective + 1) % 10 # für die Perspektive zwischen 0 und 9 jeweils um 1 weiter sprinegn
                    keyboard_layout.write(f"{perspective}") # und senden
                    double_click_phase = 0  # Klickanzahl zurücksetzen
            time.sleep(0.1)
        if button2_pressed: # wenn Knopf 2 gedrückt wurde
            keyboard.send(Keycode.SPACE)  # Leerzeichen senden
            time.sleep(0.3) # und kurz pausieren, sonst wird ein Knopfdruck als mehrere erfasst 
