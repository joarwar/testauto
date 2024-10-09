# -------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------
import pyvisa
import time
import os  # To create the folder
import numpy as np
import matplotlib.pyplot as plt
import subprocess  # For running rclone commands

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

    # Connect to the first resource in the list, or specify the correct address if multiple are available
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
        
        # Clean up the data string by removing unwanted characters
        signal = np.array([float(point) for point in data.split() if point.replace('.', '', 1).replace('-', '', 1).isdigit()])

        # Fetch the time base
        x_increment = float(oscilloscope.query(":WAVeform:XINCrement?"))
        x_origin = float(oscilloscope.query(":WAVeform:XORigin?"))
        num_points = len(signal)

        # Generate x-values based on the time base
        time_array = np.arange(num_points) * x_increment + x_origin

        return time_array, signal
    except Exception as e:
        print(f"Failed to fetch signal: {e}")
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
    timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
    folder_name = f'/var/lib/jenkins/jobs/testauto/images/signal_data_{timestamp}'
    
    # Create the folder if it doesn't already exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    return folder_name

# -------------------------------------------------------------
# Upload to Google Drive using rclone
# -------------------------------------------------------------
def upload_to_drive(folder_path):
    # Define the rclone command to upload the folder to Google Drive
    rclone_command = ['rclone', 'sync', folder_path, 'mydrive:']  # Adjust 'mydrive:' to your rclone remote name

    # Execute the rclone command
    try:
        subprocess.run(rclone_command, check=True)
        print(f"Uploaded {folder_path} to Google Drive successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error uploading to Google Drive: {e}")

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

    # Block 2: Measure frequency and save to list
    for i in range(3):
        try:
            channel = "CHANnel1"  # Specific channel 1
            frequency = measure(oscilloscope, channel=channel)  # Use channel 1 for frequency measurement
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

        # Save plot for channel 1
        save_path_channel1 = os.path.join(folder_path, f'sine_plot_{time.strftime("%Y%m%d_%H%M%S")}.png')
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
        save_path_channel2 = os.path.join(folder_path, f'pwm_plot_{time.strftime("%Y%m%d_%H%M%S")}.png')
        plt.savefig(save_path_channel2, dpi=300)
        print(f"PWM plot saved to: {save_path_channel2}")
        plt.close()

    # Upload the folder to Google Drive
    upload_to_drive(folder_path)

    # Block 4: Close the connection to the oscilloscope
    oscilloscope.close()

if __name__ == "__main__":
    main()
