
import Adafruit_CharLCD as LCD
from rpithermostat import sampler


status_message1 = ""
status_message2 = ""

lcd_rs        = 14 
lcd_en        = 15
lcd_d4        = 18
lcd_d5        = 23 
lcd_d6        = 24 
lcd_d7        = 25 
lcd_backlight = 19

# Define LCD column and row size for 16x2 LCD.
lcd_columns = 16
lcd_rows    = 2

# Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7,
                           lcd_columns, lcd_rows, lcd_backlight, invert_polarity=False, enable_pwm=True)


def set_status1(msg):
    global status_message1
    status_message1 = msg

def set_status2(msg):
    global status_message2
    status_message2 = msg

def display():
    lcd.clear()
    lcd.show_cursor(True)
    lcd.blink(True)
    lcd.message("%s\n%s" % (status_message1, status_message2))

display_thread = None

def start_display():
    global display_thread
    lcd.set_backlight(1)
    display_thread = sampler.Sampler(1, display)
    display_thread.start()

