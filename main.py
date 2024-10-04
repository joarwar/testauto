# -------------------------------------------------------------
# Importera bibliotek
# -------------------------------------------------------------
import pyvisa
import time
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------------------
# Block 1: Initialisera
# -------------------------------------------------------------
frekvens_lista = []

def initialisera():
    # Initialiserar anslutningen till oscilloskopet och returnerar instrumentobjektet
    rm = pyvisa.ResourceManager()

    # Hämta alla tillgängliga resurser för att identifiera oscilloskopet anslutet via USB
    resurser = rm.list_resources()
    print("Tillgängliga resurser:", resurser)

    # Kontrollera att resurser finns
    if not resurser:
        raise ValueError("Inga resurser hittades. Kontrollera anslutningen.")

    # Anslut till första resurser i listan, eller specificera rätt adress om flera finns
    instrument_adress = resurser[0]
    oscilloskop = rm.open_resource(instrument_adress)

    # Kontrollera att vi är anslutna till rätt instrument genom att fråga om ID
    idn = oscilloskop.query("*IDN?")
    print(f"Ansluten till: {idn}")

    # Ställ in timeout och avslutning för kommunikation
    oscilloskop.timeout = 5000
    oscilloskop.write_termination = "\n"
    oscilloskop.read_termination = "\n"

    return oscilloskop


# -------------------------------------------------------------
# Block 2: Mätning
# -------------------------------------------------------------


def mata(oscilloskop, kanal="CHANnel1"):
    # Mät frekvensen från en specifik kanal på oscilloskopets mätfunktion
    try:
        # set-kommando: specifik kanal
        oscilloskop.write(f":MEASure:FREQuency {kanal}")
        # query-kommando:
        frekvens = oscilloskop.query(f":MEASure:FREQuency? {kanal}")
        return float(frekvens)
    except Exception as e:
        print(f"Misslyckades med att mäta frekvens på {kanal}: {e}")
        return None


# -------------------------------------------------------------
# Block 3: Hämta signaldata
# -------------------------------------------------------------
def hamta_signal(oscilloskop, kanal="CHANnel1"):
    # Hämta signaldata från den specifika kanalen
    try:
        oscilloskop.write(f":WAVeform:FORMat ASCii")  # Sätt formatet till ASCII
        oscilloskop.write(f":WAVeform:SOURCE {kanal}")  # Välj kanal

        # Hämta waveform-data
        data = oscilloskop.query(":WAVeform:DATA?")
        
        # Clean the data string by removing unwanted characters
        signal = np.array([float(point) for point in data.split() if point.replace('.', '', 1).replace('-', '', 1).isdigit()])

        # Hämta tidsbasen
        x_increment = float(oscilloskop.query(":WAVeform:XINCrement?"))
        x_origin = float(oscilloskop.query(":WAVeform:XORigin?"))
        num_points = len(signal)

        # Generera x-värden baserat på tidsbasen
        time_array = np.arange(num_points) * x_increment + x_origin

        return time_array, signal
    except Exception as e:
        print(f"Misslyckades med att hämta signal: {e}")
        return None, None


# -------------------------------------------------------------
# Block 4: Analysera
# -------------------------------------------------------------
def analysera(frekvens):
    # Analysera den uppmätta frekvensen
    print("\n--- Analysera data ---")
    print(f"Uppmätt frekvens: {frekvens} Hz")


# -------------------------------------------------------------
# Huvudprogram
# -------------------------------------------------------------
import time

def main():
    # Block 1: Initialisera
    try:
        oscilloskop = initialisera()
    except Exception as e:
        print(f"Initialisering misslyckades: {e}")
        return

    for i in range(3):
        # Block 2: Mätning
        try:
            kanal = "CHANnel1"  # Specifik kanal 1
            frekvens = mata(oscilloskop, kanal=kanal)  # Använd kanal 1 för frekvensmätning
            if frekvens is not None:
                frekvens_lista.append(frekvens)
        except Exception as e:
            print(f"Mätning misslyckades: {e}")
            return
        time.sleep(1)

    print(frekvens_lista)

    # Block 3: Hämta och spara signal som bild
    time_array, signal = hamta_signal(oscilloskop, kanal)
    if signal is not None:
        plt.figure()
        plt.plot(time_array, signal)
        plt.title(f"Signal från {kanal}")
        plt.xlabel("Tid (s)")
        plt.ylabel("Amplitude")
        plt.grid()

        # Generate a unique filename using the current timestamp
        timestamp = time.strftime("%Y%m%d_%H%M%S")  # Format: YYYYMMDD_HHMMSS
        save_path = f'/var/lib/jenkins/jobs/testauto/images/signal_plot_{timestamp}.png'  # Unique filename
        
        # Print the save path for debugging
        print(f"Saving plot to: {save_path}")

        # Save the figure
        plt.savefig(save_path, dpi=300)  # Save as PNG file with 300 dpi
        plt.close()  # Close the plot to free up memory

    # Block 4: Analysera
    if frekvens is not None:
        analysera(frekvens)

    # Stäng anslutningen till oscilloskopet
    oscilloskop.close()
