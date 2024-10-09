from gpiozero import LED
from time import sleep

my_led = LED(3)
off_time = 1
on_time = 0

for i in range(5):
    for j in range(1,1001):
        my_led.on()
        sleep(on_time)
        on_time += 0.0010
        my_led.off()
        sleep(off_time)
        off_time += 0.001