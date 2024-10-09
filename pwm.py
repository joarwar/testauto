import RPi.GPIO as GPIO
from time import sleep
import math

ledpin = 12  # PWM pin connected to LED
GPIO.setwarnings(False)  # Disable warnings
GPIO.setmode(GPIO.BOARD)  # Set pin numbering system
GPIO.setup(ledpin, GPIO.OUT)
pi_pwm = GPIO.PWM(ledpin, 2000)  # Create PWM instance with frequency
pi_pwm.start(0)  # Start PWM with required Duty Cycle

# try:
#     for x in range(10000):
#         for angle in range(0, 360, 5):  # Loop through angles from 0 to 360 degrees in 5-degree increments
#             # Calculate the sine value and convert it to duty cycle (0-100%)
#             duty = (math.sin(math.radians(angle)) + 1) * 50  # Scale to 0-100%
#             pi_pwm.ChangeDutyCycle(duty)  # Set the PWM duty cycle
#             sleep(0.000027778)  # Sleep for approximately 0.27778 ms for 5 degrees
# except KeyboardInterrupt:
#     pass  # Exit the loop if interrupted

# finally:
#     pi_pwm.stop()  # Stop PWM
#     GPIO.cleanup()  # Clean up GPIO settings

# #fixed code
try:
    # Generate PWM signal for a set duration
    for x in range(1000):
        for angle in range(0, 360, 5):  # Loop through angles from 0 to 360 degrees in 5-degree increments
            # Calculate the sine value and convert it to duty cycle (0-100%)
            duty = (math.sin(math.radians(angle)) + 1) * 50  # Scale to 0-100%
            pi_pwm.ChangeDutyCycle(duty)  # Set the PWM duty cycle
            sleep(0.01)  # Increase sleep time to see if it stabilizes

        # Add a delay to ensure the PWM signal stabilizes
        print(f"PWM running, iteration {x}")  # Print debug statement to ensure loop is running
        sleep(1)  # Wait for a second before fetching the signal
except KeyboardInterrupt:
    pass  # Exit the loop if interrupted
finally:
    pi_pwm.stop()  # Stop PWM
    GPIO.cleanup()  # Clean up GPIO settings
