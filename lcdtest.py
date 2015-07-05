import time
import lcddriver

lcd = lcddriver.lcd()

lcd.lcd_display_string("The quick brown fox jumped over the lazy dog",1)
lcd.lcd_write(0x08,0x04)