# -------------------------------------------------------------
# Import libraries
# -------------------------------------------------------------
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
def measure(oscilloscope, channel):
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
def fetch_signal(oscilloscope, channel):
    # Fetch signal data from the specified channel
    try:
        oscilloscope.write(f":WAVeform:FORMat ASCii")  # Set format to ASCII
        oscilloscope.write(f":WAVeform:SOURCE {channel}")  # Select channel

        # Fetch waveform data
        data = oscilloscope.query(":WAVeform:DATA?")

        if not data:
            print(f"No data received from {channel}.")
            return None, None

        # Clean up the data string by splitting and removing unwanted characters
        signal_data = data.split()

        # Check if the first element is a metadata header, and skip it if so
        if signal_data[0].startswith('#'):
            signal_data = signal_data[1:]  # Ignore the first element

        # Remove any unwanted characters from each point, such as commas
        cleaned_signal_data = [point.strip().rstrip(',') for point in signal_data]

        # Convert remaining parts to floats
        try:
            signal = np.array([float(point) for point in cleaned_signal_data])
        except ValueError as e:
            print(f"Error converting signal data to float for {channel}: {e}")
            return None, None

        if len(signal) == 0:
            print(f"Parsed signal is empty for {channel}")
            return None, None

        # If channel is CHANnel1, perform sine wave analysis
        if channel == "CHANnel1":
            total_sum = np.sum(signal)
            average = np.mean(signal)  # Calculate the average to check for DC offset
            print(f"The sum of all points in {channel} is: {total_sum}")
            print(f"The average of all points in {channel} is: {average}")
            sum_sinus_number = average - total_sum
            print(f"The sum of the sinus is {sum_sinus_number} after removing the DC offset.")
            # Analyze if the sine wave is good based on the average value
            if abs(average) < 0.1:  # Set a tolerance level for offset
                print(f"{channel} signal appears to be centered around zero, indicating a good sine wave.")
            else:
                print(f"{channel} signal has a DC offset of {average}. This may indicate an issue.")

            # Check if the amplitude is reasonable (e.g., if the max value is significantly above zero)
            if np.max(signal) > 0:  # You can adjust this condition based on expected signal behavior
                print(f"{channel} signal has positive amplitude, indicating potential offset.")

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
# Create dynamic folder
# -------------------------------------------------------------
def create_folder():
    timestamp = time.strftime("%Y%m%d_%H%M")  # Format: YYYYMMDD_HHMM
    folder_name = f'/var/lib/jenkins/jobs/testauto/images/signal_data_{timestamp}'

    # Create the folder if it doesn't already exist
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")  # Debugging line
    else:
        print(f"Folder already exists: {folder_name}")  # Debugging line

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

    # Define channels to measure
    channels = ["CHANnel1", "CHANnel2"]

    # Block 2: Measure frequency and save to list
    for channel in channels:
        try:
            frequency = measure(oscilloscope, channel)  # Use specific channel for frequency measurement
            if frequency is not None:
                frequency_list.append(frequency)
        except Exception as e:
            print(f"Measurement failed: {e}")
            return
        time.sleep(1)

    print(f"Frequencies measured: {frequency_list}")

    # Block 3: Fetch and save signals for each channel
    for channel in channels:
        time_array, signal = fetch_signal(oscilloscope, channel)
        if signal is not None and len(signal) > 0:
            plt.figure()
            plt.plot(time_array, signal)
            plt.title(f"Signal from {channel}")
            plt.xlabel("Time (s)")
            plt.ylabel("Amplitude")
            plt.grid()

            # Save plot for each channel
            save_path = os.path.join(folder_path, f'plot_{channel}_{time.strftime("%Y%m%d_%H%M")}.png')
            try:
                plt.savefig(save_path, dpi=300)
                print(f"Plot saved to: {save_path}")
            except Exception as e:
                print(f"Failed to save plot for {channel}: {e}")
            plt.close()
        else:
            print(f"No valid signal data for {channel}.")

    # Block 5: Close the connection to the oscilloscope
    oscilloscope.close()


if __name__ == "__main__":
    main()
