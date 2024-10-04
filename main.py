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
    except Exception as e:
        print(f"Misslyckades med att mäta frekvens på {kanal}: {e}")

    # Returnera den uppmätta frekvensen
    return float(frekvens)


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
        signal = np.array(data.split(','), dtype=float)

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

    # Kontrollera om frekvensen ligger inom ett förväntat intervall
    if frekvens < 50 or frekvens > 60:
        print(
            "Varning: Frekvensen ligger utanför det förväntade intervallet (50-60 Hz)."
        )
    else:
        print(f"Frekvensen ligger inom förväntat intervall: {frekvens} Hz")


# -------------------------------------------------------------
# Huvudprogram
# -------------------------------------------------------------
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
            kanal = "CHANnel1"  # Kan justeras beroende på vilken kanal du vill mäta från
            frekvens = mata(oscilloskop, kanal=kanal)
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
        
        # Save the figure instead of displaying it
        plt.savefig('signal_plot.png', dpi=300)  # Save as PNG file with 300 dpi
        plt.close()  # Close the plot to free up memory

    # Block 4: Analysera
    analysera(frekvens)

    # Stäng anslutningen till oscilloskopet
    oscilloskop.close()

if __name__ == "__main__":
    main()
