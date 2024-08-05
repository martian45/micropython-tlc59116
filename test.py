import tlc59116


disp_1 = tlc59116.TLC59116()
disp_2 = tlc59116.TLC59116(i2c_addr=0x61)
disp_1.brightness = 250
disp_2.brightness = 250

a = input('Text: ')
disp_1.led_write(a)
a = input('Text: ')
disp_2.led_write(a)

s = input('Segment No.: ')
disp_1.set_segment(int(s), 255)

s = input('Segment No.: ')
disp_2.set_segment(int(s), 255)
