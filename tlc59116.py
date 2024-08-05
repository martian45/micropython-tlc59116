"""
Micropython TCL59116 dual 7-segment LED display driver
"""

__version__ = '0.1'

from machine import Pin, I2C

chars = {' ': 0x00, '-': 0x40, '=': 0x48, '°': 0x63, '"': 0x22, "'": 0x20, '|': 0x30, '_': 0x08,
         '0': 0x3F, '1': 0x06, '2': 0x5B, '3': 0x4F, '4': 0x66, '5': 0x6D,
         '6': 0x7D, '7': 0x07, '8': 0x7F, '9': 0x6F,
         'A': 0x77, 'B': 0x7F, 'C': 0x39, 'D': 0x3F, 'E': 0x79, 'F': 0x71, 'G': 0x7D, 'H': 0x76, 'I': 0x30,
         'J': 0x1E, 'K': 0x76, 'L': 0x38, 'M': 0x76, 'N': 0x37, 'O': 0x3F, 'P': 0x73, 'Q': 0x3F, 'R': 0x77,
         'S': 0x6D, 'T': 0x78, 'U': 0x3E, 'V': 0x3E, 'W': 0x3E, 'X': 0x76, 'Y': 0x72, 'Z': 0x5B,
         'a': 0x5F, 'b': 0x7C, 'c': 0x58, 'd': 0x5E, 'e': 0x7B, 'f': 0x71, 'g': 0x6F, 'h': 0x74, 'i': 0x10,
         'j': 0x1E, 'k': 0x74, 'l': 0x38, 'm': 0x54, 'n': 0x54, 'o': 0x5C, 'p': 0x73, 'q': 0x67, 'r': 0x50,
         's': 0x6D, 't': 0x78, 'u': 0x1C, 'v': 0x1C, 'w': 0x1C, 'x': 0x76, 'y': 0x72, 'z': 0x5B}
dots = {'.': 0x1, ',': 0x1, ':': 0x1, ';': 0x1}


# pwm_list = [(6, 5), (7, 6), (10, 7), (15, 9), (20, 11), (30, 15),
#            (40, 22), (50,  35), (60, 40), (100, 60), (200, 150), (256, 200)]


def _text_norm(txt):
    is_char = False
    txt_sp = ''
    for n in txt:
        if n != '.':
            txt_sp += n
            is_char = True
        elif is_char:
            txt_sp += '.'
            is_char = False
        else:
            txt_sp += (' ' + '.')
    for n in range(len(txt_sp), 4):
        txt_sp = ' ' + txt_sp
    char_count = 0
    trimmed = ''
    for n in reversed(txt_sp):
        if n != '.':
            trimmed = n + trimmed
            char_count += 1
            if char_count == 2:
                break
        else:
            trimmed = n + trimmed
    return trimmed


def _char_to_bin(char):
    if char in chars:
        bin_char = bin(chars[char])[2:]
        for n in range(len(bin_char), 7):
            bin_char = '0' + bin_char  # Always max 7 bits
        bin_char_r = ''
        for n in reversed(bin_char):
            bin_char_r += n
    elif char in dots:
        bin_char_r = '1'
    else:
        bin_char_r = '1001001'  # 3 horizontal lines if char does not exist in chars
    return bin_char_r


class TLC59116:
    def __init__(self, sda=21, scl=22, i2c_addr=0x60):  # I2C GPIO numbers, I2C address
        #  I2C hardware address = 1 1 0 A3 A2 A1 A0, 0x60 = 110 0000 (A0-A3 set to low)
        self.sda = sda
        self.scl = scl
        self.i2c_addr = i2c_addr
        self.i2c = I2C(0, sda=Pin(sda), scl=Pin(scl))  # ESP32 has two hardware I2C with identifiers 0 and 1.
        self.brightness = 200  # Default brightness (0-255)

        self.i2c.writeto(self.i2c_addr,
                         bytearray([0x80,  # Writes from register 00
                                    0x00, 0x00,  # Reg 0x00 Mode 1, Reg 0x01 Mode 2
                                    # Reg 0x02 - 0x11: LED segment 1 - 16 brightness
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                                    0xFF, 0x00,  # Reg 0x12 Group duty cycle control, Reg 0x13 Group frequency
                                    0xAA, 0xAA, 0xAA, 0xAA,  # Reg 0x14 - 0x15 LED output state 0 - 3
                                    0x00, 0x00, 0x00,  # Reg 0x18 - 0x1A I2C bus sub address 1 - 3
                                    0x00,  # Reg 0x1B all call I2C bus address
                                    0xFF]))  # Reg 0x1C IREF configuration

        self.led_empty()

    def _set_all(self, brightness):  # Switch on all segments on entered brightness
        data = bytearray([0x82] + [brightness] * 16)  # 0x82 starts writing from register 0x02
        self.i2c.writeto(self.i2c_addr, data)

    def led_empty(self):
        self._set_all(0x00)

    def led_test(self):
        self._set_all(0xFF)

    def set_segment(self, pin, brightness):
        data = bytearray([0x01 + pin, brightness])  # Switch on selected (1 - 16)segment on entered brightness
        self.i2c.writeto(self.i2c_addr, data)

    def led_write(self, txt):
        data = bytearray([0x82])  # Writes for, register 0x02
        txt = _text_norm(txt)
        dot = '0'
        for char in reversed(txt):
            bin_char = _char_to_bin(char)
            if bin_char == '1':
                dot = bin_char
            else:
                bin_char += dot
                dot = '0'
                for n in bin_char:
                    if n == '1':
                        data.append(self.brightness)
                    else:
                        data.append(0x00)
        self.i2c.writeto(self.i2c_addr, data)
