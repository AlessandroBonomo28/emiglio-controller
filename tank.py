import pigpio
import time

# --- CONFIGURAZIONE PIN ---
PIN_X, PIN_Y = 17, 18  # Ingressi RC

# MOTORE A (Sinistro)
AIN1, AIN2 = 25, 4     # PIN_UP e PIN_DOWN
PWMA = 8

# MOTORE B (Destro)
BIN1, BIN2 = 7, 27     # PIN_LEFT e PIN_RIGHT
PWMB = 11

class RC_Reader:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.width = 0
        self.last_tick = None
        self.last_update_time = time.time()
        self.last_width = 0
        self.stable_since = time.time()
        self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, g, l, t):
        if l == 1:
            self.last_tick = t
        elif l == 0 and self.last_tick is not None:
            new_width = pigpio.tickDiff(self.last_tick, t)
            if new_width != self.last_width:
                self.stable_since = time.time()
                self.last_width = new_width
            self.width = new_width
            self.last_update_time = time.time()

    def is_alive(self):
        now = time.time()
        return (now - self.last_update_time) < 0.5 and (now - self.stable_since) < 2.0

# Setup pigpio
pi = pigpio.pi()
if not pi.connected:
    exit()

# Inizializzazione Pin
pins_output = [AIN1, AIN2, BIN1, BIN2, PWMA, PWMB]
for p in pins_output:
    pi.set_mode(p, pigpio.OUTPUT)
    pi.write(p, 0)

# Inizializzazione Lettori RC
ch_x = RC_Reader(pi, PIN_X)
ch_y = RC_Reader(pi, PIN_Y)

# Velocità fissa (0-255)
import sys  # Aggiungi questa in alto insieme agli altri import

# --- SOSTITUISCI LA PARTE DELLA VELOCITÀ CON QUESTA ---
try:
    # Prende il primo argomento dopo il nome dello script, se manca usa 200
    SPEED = int(sys.argv[1]) if len(sys.argv) > 1 else 200
    # Limitiamo il range per sicurezza (0-255)
    SPEED = max(0, min(255, SPEED))
except ValueError:
    print("Metti un numero, fenomeno! Uso la velocità di default: 200")
    SPEED = 200
pi.set_PWM_dutycycle(PWMA, SPEED)
pi.set_PWM_dutycycle(PWMB, SPEED)

print(f"Emiglio-Tank Operativo. Speed: {SPEED}.")

try:
    while True:
        if ch_x.is_alive() and ch_y.is_alive():
            rx, ry = ch_x.width, ch_y.width

            # --- LOGICA DI MOVIMENTO ---

            if ry > 1650: # AVANTI (Entrambi i motori avanti)
                state = "AVANTI  "
                # Motore A
                pi.write(AIN1, 0); pi.write(AIN2, 1)
                # Motore B
                pi.write(BIN1, 1); pi.write(BIN2, 0)

            elif ry < 1470: # INDIETRO (Entrambi i motori indietro)
                state = "INDIETRO"
                # Motore A
                pi.write(AIN1, 1); pi.write(AIN2, 0)
                # Motore B
                pi.write(BIN1, 0); pi.write(BIN2, 1)

            elif rx > 1700: # SINISTRA (Gira sul posto a sx)
                state = "RUOTA SX"
                # Motore A (Indietro)
                pi.write(AIN1, 1); pi.write(AIN2, 0)
                # Motore B (Avanti)
                pi.write(BIN1, 1); pi.write(BIN2, 0)

            elif rx < 1430: # DESTRA (Gira sul posto a dx)
                state = "RUOTA DX"
                # Motore A (Avanti)
                pi.write(AIN1, 0); pi.write(AIN2, 1)
                # Motore B (Indietro)
                pi.write(BIN1, 0); pi.write(BIN2, 1)

            else: # STOP (Nessun comando o stick al centro)
                state = "STOP    "
                pi.write(AIN1, 0); pi.write(AIN2, 0)
                pi.write(BIN1, 0); pi.write(BIN2, 0)

            print(f"POWER: ON  | STATO: {state} | Y:{ry} X:{rx}      ", end='\r')
        else:
            # Sicurezza: Spegni tutto se perdi il segnale
            print(f"POWER: OFF | Segnale assente...                     ", end='\r')
            for p in [AIN1, AIN2, BIN1, BIN2]: pi.write(p, 0)

        time.sleep(0.05)

except KeyboardInterrupt:
    for p in [AIN1, AIN2, BIN1, BIN2, PWMA, PWMB]: pi.write(p, 0)
    pi.stop()
