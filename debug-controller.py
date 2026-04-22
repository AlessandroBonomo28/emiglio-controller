import pigpio
import time

# --- CONFIGURAZIONE ---
# Usiamo la numerazione BCM (quella del chip)
PIN_CH1 = 17  # Pin fisico 11
PIN_CH2 = 18  # Pin fisico 12

class PWM_Reader:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.pulse_width = 0
        self.tick_start = None
        # Crea un "callback" che scatta ad ogni cambio di stato (da 0 a 1 e da 1 a 0)
        self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, gpio, level, tick):
        if level == 1: # Inizio impulso
            self.tick_start = tick
        elif level == 0: # Fine impulso
            if self.tick_start is not None:
                # Calcola la differenza di tempo tra inizio e fine
                self.pulse_width = pigpio.tickDiff(self.tick_start, tick)

    def get_width(self):
        return self.pulse_width

    def stop(self):
        self.cb.cancel()

# Inizializzazione
pi = pigpio.pi()
if not pi.connected:
    print("Errore: pigpiod non è attivo! Digita 'sudo pigpiod' nel terminale.")
    exit()

ch1 = PWM_Reader(pi, PIN_CH1)
ch2 = PWM_Reader(pi, PIN_CH2)

print(f"Lettura canali avviata sui GPIO {PIN_CH1} e {PIN_CH2}...")
print("Valori attesi tra 1000 (min) e 2000 (max). 1500 è il centro.")

try:
    while True:
        v1 = ch1.get_width()
        v2 = ch2.get_width()

        print(f"CH1: {v1:4} µs | CH2: {v2:4} µs", end='\r')
        time.sleep(0.1) # Aggiorna lo schermo 10 volte al secondo

except KeyboardInterrupt:
    print("\nChiusura in corso...")
    ch1.stop()
    ch2.stop()
    pi.stop()