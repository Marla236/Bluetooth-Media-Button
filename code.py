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
a1 = time.time()
pressed_phase1 = False
double_click_phase1 = 0
a2 = time.time()
pressed_phase2 = False
double_click_phase2 = 0

# Knopf 1 ist blau, Einzelklick sendet perspective+1, Doppelklick wechselt das Fenster
# Knopf 2 ist rot, Einzelklick sendet Leerzeichen

def long_press(elapsed):
    if elapsed > long_pressed_treshold: # wenn der Knopf lange gedrückt wurde, soll dieser Knopfdruck nicht für einen Doppelklick gezählt werden
        return 0
    else: # gibt also nur 1 zurück, wenn der Knopf ein Mal kurz gedrückt wurde
        return 1


while True:
    while not ble.connected:
        pass
    print("start typing: ")
    while ble.connected:
        button1_pressed = not button1.value # button1.value ist standardmäßig True, wenn der Knopf gedrückt ist False
        button2_pressed = not button2.value
        if button1_pressed:  # wenn Knopf 1 gedrückt ist
            if not pressed_phase1:  # und vorher nicht gedrückt war
                a1 = time.time()  # Startzeit merken
                pressed_phase1 = True  # und merken, dass er jetzt gedrückt wurde
        else:  # wenn Knopf 1 nicht gedrückt ist
            if pressed_phase1:  # und vorher gedrückt war
                elapsed = time.time() - a  # abfragen, wie lange er vorher gedrückt war
                a1 = time.time()  # Zeit aktualisieren
                pressed_phase1 = False  # merken, dass er vorher nicht gedrückt war
                double_click_phase1 += long_press(
                    elapsed
                )  # und merken, wie oft er jetzt in kurzer Zeit gedrückt wurde
                if double_click_phase1 == 2:  # wenn Doppelklick vollständig ist
                    double_click_phase1 = 0  # Klickanzahl zurücksetzen
                    keyboard.send(Keycode.ALT, Keycode.TAB, Keycode.TAB) # und Fenster wechseln
            else:  # und vorher nicht gedrückt war
                elapsed = time.time() - a1  # Zeit abfragen, die er nicht gedrückt wurde
                if (
                    elapsed > allowed_pause_for_double and double_click_phase1 > 0
                ):  # Einzelklick erkennen
                    keyboard.send(Keycode.PAGE_UP) # und Watt steigern
                    double_click_phase1 = 0  # Klickanzahl zurücksetzen
            time.sleep(0.1)

        if button2_pressed: # wenn Knopf 2 gedrückt wurde
            if not pressed_phase2:  # und vorher nicht gedrückt war
                a2 = time.time()  # Startzeit merken
                pressed_phase2 = True  # und merken, dass er jetzt gedrückt wurde
        else:  # wenn Knopf 2 nicht gedrückt ist
            if pressed_phase2:  # und vorher gedrückt war
                elapsed = time.time() - a2  # abfragen, wie lange er vorher gedrückt war
                a2 = time.time()  # Zeit aktualisieren
                pressed_phase2 = False  # merken, dass er vorher nicht gedrückt war
                double_click_phase2 += long_press(
                    elapsed
                )  # und merken, wie oft er jetzt in kurzer Zeit gedrückt wurde
                if double_click_phase2 == 2:  # wenn Doppelklick vollständig ist
                    double_click_phase2 = 0  # Klickanzahl zurücksetzen
                    keyboard.send(Keycode.SPACE)  # Leerzeichen senden
            else:  # und vorher nicht gedrückt war
                elapsed = time.time() - a2  # Zeit abfragen, die er nicht gedrückt wurde
                if (
                    elapsed > allowed_pause_for_double and double_click_phase2 > 0
                ):  # Einzelklick erkennen
                    keyboard.send(Keycode.PAGE_DOWN) # und Watt senken
                    double_click_phase2 = 0  # Klickanzahl zurücksetzen
            time.sleep(0.1)
