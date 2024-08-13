# Example of use TLC59116.py
# Digital clock with automatic brightness and time sync with ntp time server
# Uses 2 TLC59116 each with 2 digit 7-segment LED display with dots (8 segments including dot)
# ESP32 syncs time on start and each 24 hours with ntp
# I2C pins used: sda = 25, scl = 26
# Wi-fi is switched off every night
# Brightness of LEDs depends on voltage on pin 32, where is photo resistor installed
# Brightness of dot between numbers is reduced to 80 % of other segments brightness

import tlc59116
import gc, network, time, ntptime
from machine import ADC

TIME_OFFSET = 2


def display_text(t):
    disp_h.led_write(t[0:2])
    disp_m.led_write(t[2:4])


def dot_blink(ms=1000):
    disp_h.set_segment(8, None)  # None = sensor adjusted brightness
    time.sleep_ms(ms)
    disp_h.set_segment(8, 0)
    time.sleep_ms(ms)


def wlan_connect():
    SSID = 'fve'
    PASSWORD = 'APfve2020goodwe2%FlowerPower'
    display_text('Conn')
    wlan.active(True)
    if not wlan.isconnected():
        wlan.connect(SSID, PASSWORD)
        while not wlan.isconnected():
            dot_blink()
    display_text('yES ')
    time.sleep(1)


def ntp_sync():
    try:
        ntptime.settime()
        return True
    except OSError:
        return False


def set_brightness():
    light = adc.read()
    if light > 3000:
        brightness = 90  # max. brightness (0-255)
    elif light < 500:
        brightness = 7  # min. brightness (0-255)
    else:
        brightness = int(round(light*0.032)) - 9
    disp_h.brightness = brightness
    disp_m.brightness = brightness

gc.enable()
wlan = network.WLAN(network.STA_IF)
adc = ADC(32)
adc.atten(ADC.ATTN_11DB)
disp_h = tlc59116.TLC59116(sda=25, scl=26)
disp_m = tlc59116.TLC59116(sda=25, scl=26, i2c_addr=0x61)
synced = False
disp_h.dot_brightness_percent = 80

time.sleep(5)  # wait for init I2C

wlan_connect()

while True:
    set_brightness()
    t = list(time.localtime())
    if t[3] > 21:
        t[3] = t[3] + TIME_OFFSET - 24
    else:
        t[3] += TIME_OFFSET
    disp_h.led_write('{:1d}.'.format(t[3]))
    disp_m.led_write('{:02d}'.format(t[4]))
    if not synced:
        synced = ntp_sync()
    elif t[3] == 12:
        synced = False
    if wlan.active():
        if t[3] ==22:
            wlan.active(False)
    elif t[3] == 9:
        wlan_connect()
    if synced:
        time.sleep(1)
    else:
        dot_blink(500)
