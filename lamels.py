# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
import rp2

# Configure the number of WS2812 LEDs.
NUM_LEDS = 150
PIN_NUM = 0
brightness = 1

@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=24)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on pin
sm = rp2.StateMachine(1, ws2812, freq=8_000_000, sideset_base=Pin(1))
sm_nl = 149
sm2 = rp2.StateMachine(2, ws2812, freq=8_000_000, sideset_base=Pin(2))
sm2_nl = 148
sm3 = rp2.StateMachine(3, ws2812, freq=8_000_000, sideset_base=Pin(3))
sm3_nl = 150
sm4 = rp2.StateMachine(4, ws2812, freq=8_000_000, sideset_base=Pin(4))
sm4_nl = 149
sm5 = rp2.StateMachine(5, ws2812, freq=8_000_000, sideset_base=Pin(5))
sm5_nl = 148

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)
sm2.active(2)
sm3.active(3)
sm4.active(4)
sm5.active(5)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

##########################################################################
def pixels_show():
    dimmer_ar = array.array("I", [0 for _ in range(NUM_LEDS)])
    for i,c in enumerate(ar):
        r = int(((c >> 8) & 0xFF) * brightness)
        g = int(((c >> 16) & 0xFF) * brightness)
        b = int((c & 0xFF) * brightness)
        dimmer_ar[i] = (g<<16) + (r<<8) + b
    sm.put(dimmer_ar, 8)
    sm2.put(dimmer_ar, 8)
    sm3.put(dimmer_ar, 8)
    sm4.put(dimmer_ar, 8)
    sm5.put(dimmer_ar, 8)
    #time.sleep_ms(1)

def pixels_set(i, color):
    ar[i] = (color[1]<<16) + (color[0]<<8) + color[2]

def pixels_fill(color):
    for i in range(len(ar)):
        pixels_set(i, color)

def color_chase(color, wait):
    for i in range(NUM_LEDS):
        pixels_set(i, color)
#         time.sleep(wait)
        pixels_show()
#     time.sleep(0.1)

def wheel(pos):
    # Input a value 0 to 255 to get a color value.
    # The colours are a transition r - g - b - back to r.
    if pos < 0 or pos > 255:
        return (0, 0, 0)
    if pos < 85:
        return (255 - pos * 3, pos * 3, 0)
    if pos < 170:
        pos -= 85
        return (0, 255 - pos * 3, pos * 3)
    pos -= 170
    return (pos * 3, 0, 255 - pos * 3)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(NUM_LEDS):
            rc_index = (i * 256 // NUM_LEDS) + j
            pixels_set(i, wheel(rc_index & 255))
        pixels_show()
        #time.sleep(0.2)

BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)
WHITE = (255, 255, 255)
COLORS = (RED, YELLOW, GREEN, CYAN, BLUE, PURPLE, WHITE)

# print("fills")
# for color in COLORS:
#     pixels_fill(color)
#     pixels_show()
#     time.sleep(0.2)
# 
# print("chases")
while True:
    for color in COLORS:
        color_chase(color, 0.01)

print("rainbow")
while True:
    rainbow_cycle(0)




