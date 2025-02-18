from time import sleep
from modules import ws2812

led = ws2812(8,1)

# the led is represented 0x00 to 0xFF in hexadecimal

def set_rgb(r,g,b):

    # Ensure the values are within the 0-255 range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    # Convert RGB values to hexadecimal
    r_hex = hex(r)  # Convert red to hexadecimal
    g_hex = hex(g)  # Convert green to hexadecimal
    b_hex = hex(b)  # Convert blue to hexadecimal

    # Set the color using the hexadecimal values (already fits WS2812 format)
    led.set_led(0, (r, g, b))
    led.display()


while True:
    set_rgb(0,0,100)
    sleep(1)
    set_rgb(0,100,0)
    sleep(1)
    set_rgb(100,0,0)
    sleep(1)
