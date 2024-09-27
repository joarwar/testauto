from time import sleep
from gpiozero import LED

my_red_led = LED(17)

for i in range(50):
    my_red_led.on()
    sleep(1)
    my_red_led.off()
    sleep(1)
