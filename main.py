from gpiozero import LED
from time import sleep

my_red_led = LED(2)

for i in range(10):
    my_red_led.on()
    sleep(1)
    my_red_led.off()
    sleep(1)