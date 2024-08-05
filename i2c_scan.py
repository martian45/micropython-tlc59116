from machine import Pin, I2C

# ESP32 pin assignment
i2c = I2C(0, scl=Pin(22), sda=Pin(21))
devs = i2c.scan()
if len(devs) == 0:
    print('No I2C device found')
else:
    print('I2C devices:', len(devs))
    for dev in devs:
        print('Device address:', hex(dev))
