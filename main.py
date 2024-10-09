# -------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------
import RPi.GPIO as GPIO
from time import sleep
import math
import pyvisa
import time
import os  # To create the folder
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# Block 1: Initialize
# -------------------------------------------------------------
frequency_list = []

def initialize():
    # Initializes the connection to the oscilloscope and returns the instrument object
    rm = pyvisa.ResourceManager()

    # Fetch all available resources to identify the oscilloscope connected via USB
    resources = rm.list_resources()
    print("Available resources:", resources)

    # Check that resources are available
    if not resources:
        raise ValueError("No resources found. Check the connection.")

    # Connect to the first resource in the list
    instrument_address = resources[0]
    oscilloscope = rm.open_resource(instrument_address)

    # Verify we are connected to the correct instrument by asking for its ID
    idn = oscilloscope.query("*IDN?")
    print(f"Connected to: {idn}")

    # Set timeout and termination for communication
    oscilloscope.timeout = 5000
    oscilloscope.write_termination = "\n"
    oscilloscope.read_termination = "\n"

    return oscilloscope


# -------------------------------------------------------------
# Block 2: Measurement
# -------------------------------------------------------------
def measure(oscilloscope, channel="CHANnel1"):
    # Measure the frequency from a specific channel using the oscilloscope's measurement function
    try:
        # Set command: specific channel
        oscilloscope.write(f":MEASure:FREQuency {channel}")
        # Query command:
        frequency = oscilloscope.query(f":MEASure:FREQuency? {channel}")
        return float(frequency)
    except Exception as e:
        print(f"Failed to measure frequency on {channel}: {e}")
        return None


# -------------------------------------------------------------
# Block 3: Fetch signal data
# -------------------------------------------------------------
def fetch_signal(oscilloscope, channel="CHANnel1"):
    # Fetch signal data from the specified channel
    try:
        oscilloscope.write(f":WAVeform:FORMat ASCii")  # Set format to ASCII
        oscilloscope.write(f":WAVeform:SOURCE {channel}")  # Select channel

        # Fetch waveform data
        data = oscilloscope.query(":WAVeform:DATA?")
        
        if not data:
            print(f"No data received from {channel}.")
            return None, None
        else:
            print(f"Data received from {channel}: {data[:100]}...")  # Print first 100 characters for debugging

        # Clean up the data string by removing unwanted characters
        signal = np.array([float(point) for point in data.split() if point.replace('.', '', 1).replace('-', '', 1).isdigit()])

        if len(signal) == 0:
            print(f"Parsed signal is empty for {channel}")
            return None, None

        # Fetch the time base
        x_increment = float(oscilloscope.query(":WAVeform:XINCrement?"))
        x_origin = float(oscilloscope.query(":WAVeform:XORigin?"))
        num_points = len(signal)

        # Generate x-values based on the time base
        time_array = np.linspace(0, num_points * x_increment, num_points) + x_origin

        return time_array, signal
    except Exception as e:
        print(f"Failed to fetch signal from {channel}: {e}")
        return None, None


# -------------------------------------------------------------
# Block 4: Analyze
# -------------------------------------------------------------
def analyze(frequency):
    # Analyze the measured frequency
    print("\n--- Analyze data ---")
    print(f"Measured frequency: {frequency} Hz")


# -------------------------------------------------------------
# Create dynamic folder
# -------------------------------------------------------------
def create_folder():
    timestamp = time.strftime("%Y%m%d_%H%M")  # Format: YYYYMMDD_HHMM
    folder_name = f'/var/lib/jenkins/jobs/testauto/images/signal_data_{timestamp}'

    # Create the folder if it doesn't already exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    return folder_name


# -------------------------------------------------------------
# Main program
# -------------------------------------------------------------
def main():
    # Block 1: Initialize
    try:
        oscilloscope = initialize()
    except Exception as e:
        print(f"Initialization failed: {e}")
        return

    # Create a folder to save the images
    folder_path = create_folder()

    # -------------------------------------------------------------
    # Block 2: PWM Generation
    # -------------------------------------------------------------
    ledpin = 12  # PWM pin connected to LED
    GPIO.setwarnings(False)  # Disable warnings
    GPIO.setmode(GPIO.BOARD)  # Set pin numbering system
    GPIO.setup(ledpin, GPIO.OUT)
    pi_pwm = GPIO.PWM(ledpin, 2000)  # Create PWM instance with frequency
    pi_pwm.start(0)  # Start PWM with required Duty Cycle

    try:
        # Generate PWM signal for a set duration
        for x in range(1000):
            for angle in range(0, 360, 5):  # Loop through angles from 0 to 360 degrees in 5-degree increments
                # Calculate the sine value and convert it to duty cycle (0-100%)
                duty = (math.sin(math.radians(angle)) + 1) * 50  # Scale to 0-100%
                pi_pwm.ChangeDutyCycle(duty)  # Set the PWM duty cycle
                sleep(0.000027778)  # Sleep for approximately 0.27778 ms for 5 degrees

        # Add a delay to ensure the PWM signal stabilizes
        sleep(1)  # Wait for a second before fetching the signal

    except KeyboardInterrupt:
        pass  # Exit the loop if interrupted

    finally:
        pi_pwm.stop()  # Stop PWM
        GPIO.cleanup()  # Clean up GPIO settings

    # Block 2: Measure frequency and save to list
    for i in range(3):
        try:
            channel = "CHANnel1"  # Specific channel 1
            frequency = measure(oscilloscope, channel)  # Use channel 1 for frequency measurement
            if frequency is not None:
                frequency_list.append(frequency)
        except Exception as e:
            print(f"Measurement failed: {e}")
            return
        time.sleep(1)

    print(frequency_list)

    # Block 3: Fetch and save signal from channel 1 (sine wave)
    time_array_channel1, signal_channel1 = fetch_signal(oscilloscope, "CHANnel1")
    if signal_channel1 is not None:
        plt.figure()
        plt.plot(time_array_channel1, signal_channel1)
        plt.title("Sine wave from Channel 1")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid()
        # Debug: Print the first few time and signal values
        print("First few time values:", time_array_channel1[:5])
        print("First few signal values:", signal_channel1[:5])

        # Save plot for channel 1
        save_path_channel1 = os.path.join(folder_path, f'sine_plot_{time.strftime("%Y%m%d_%H%M")}.png')
        plt.savefig(save_path_channel1, dpi=300)
        print(f"Sine plot saved to: {save_path_channel1}")
        plt.close()

    # Block 3: Fetch and save signal from channel 2 (PWM signal)
    time_array_channel2, signal_channel2 = fetch_signal(oscilloscope, "CHANnel2")
    if signal_channel2 is not None:
        plt.figure()
        plt.plot(time_array_channel2, signal_channel2)
        plt.title("PWM signal from Channel 2")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid()

        # Save plot for channel 2
        save_path_channel2 = os.path.join(folder_path, f'pwm_plot_{time.strftime("%Y%m%d_%H%M")}.png')
        plt.savefig(save_path_channel2, dpi=300)
        print(f"PWM plot saved to: {save_path_channel2}")
        plt.close()

    # Block 5: Close the connection to the oscilloscope
    oscilloscope.close()


if __name__ == "__main__":
    main()
