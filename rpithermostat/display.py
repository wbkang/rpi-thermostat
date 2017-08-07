
import Adafruit_CharLCD as LCD
from rpithermostat import temphumids
from rpithermostat import sampler
from rpithermostat import oracle


status_message = ""

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


def set_status(msg):
    global status_message
    status_message = msg

def display():
    target_temp = oracle.get_target_temperature()
    current = temphumids.get_current_temphumid()
    current_temp = current['temperature']
    current_humidity = current['humidity']
    
    lcd.clear()
    lcd.show_cursor(True)
    lcd.blink(True)
    lcd.message("%.1fC@%d%%->%dC\n%s" % (current_temp, current_humidity, target_temp, status_message))

display_thread = None

def start_display():
    global display_thread
    lcd.set_backlight(1)
    display_thread = sampler.Sampler(1, display)
    display_thread.start()

