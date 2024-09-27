# -------------------------------------------------------------
# Programskelett och kod för att mäta frekvens med oscilloskop.
# Koden mäter frekvens och kontrolelrar om den ligger inom ett
# visst intervall. Resultat skrivs till terminal.
# Yrgo, 2024-09-27
# Henrik Hallenberg
# Kod genererad med ChatGPT4o
#
# OBS! Kod/kommentarer är på svenska, vilket bör undvikas!
# -------------------------------------------------------------


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
    # OBS! Instrumentadressen kan förstås hårdkodas med sin adress
    instrument_adress = resurser[0]
    oscilloskop = rm.open_resource(instrument_adress)

    # Kontrollera att vi är anslutna till rätt instrument genom att fråga om ID
    idn = oscilloskop.query("*IDN?")
    print(f"Ansluten till: {idn}")

    # Ställ in timeout och avslutning för kommunikation
    oscilloskop.timeout = 5000
    oscilloskop.write_termination = "\n"
    oscilloskop.read_termination = "\n"

    # Ofta behövs mer kod för att ställa in instrumentet inför mätning.
    # Exempel på ytterligare inställningar för oscilloskop är trig, kanal, tidsbas, ...
    # VIssa av dessa inställningar kan göras här, men man kan också behöva justera under mätningen.

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
        #print(f"Frekvens på {kanal}: {frekvens} Hz")
    except Exception as e:
        print(f"Misslyckades med att mäta frekvens på {kanal}: {e}")

    # Returnera den uppmätta frekvensen
    return float(frekvens)


# -------------------------------------------------------------
# Block 3: Analysera
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
            # Ange kanal (t.ex., "CHANnel1", "CHANnel2", etc.)
            kanal = "CHANnel1"  # Kan justeras beroende på vilken kanal du vill mäta från
            frekvens = mata(oscilloskop, kanal=kanal)
        except Exception as e:
            print(f"Mätning misslyckades: {e}")
            return
        time.sleep(1)
        
        frekvens_lista.append(frekvens)
    print(frekvens_lista)

    # Block 3: Analysera
    analysera(frekvens)

    # Stäng anslutningen till oscilloskopet
    oscilloskop.close()

if __name__ == "__main__":
    main()
