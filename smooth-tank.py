import pigpio
import time
import sys

# --- CONFIGURAZIONE PIN E MOTORI ---
PIN_X, PIN_Y = 17, 18  # Ingressi RC
STANDBY = 24

# MOTORE A (Sinistro)
AIN1, AIN2 = 4, 25     # PIN_UP e PIN_DOWN
PWMA = 8

# MOTORE B (Destro)
BIN1, BIN2 = 7, 27     # PIN_LEFT e PIN_RIGHT
PWMB = 11

# --- CONFIGURAZIONE FLUIDITA' (SMOOTH) ---
SMOOTH_TIME_MS = 350   # Millisecondi per passare da 0 alla velocità massima (es. 800ms)
# SMOOT_TIME_MS minimo: 300 ms, sotto i 300 ms si accappotta su superfice piana
LOOP_DELAY = 0.05      # Tempo di ciclo del while (50ms)

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

pi.set_mode(STANDBY, pigpio.OUTPUT)
pi.write(STANDBY, 1)

# Inizializzazione Lettori RC
ch_x = RC_Reader(pi, PIN_X)
ch_y = RC_Reader(pi, PIN_Y)

# Gestione Velocità Massima
try:
    MAX_SPEED = int(sys.argv[1]) if len(sys.argv) > 1 else 255
    MAX_SPEED = max(0, min(255, MAX_SPEED))
except ValueError:
    print("Metti un numero, fenomeno! Uso la velocità di default: 200")
    MAX_SPEED = 200

# Calcolo dello step di accelerazione per ogni ciclo di loop
if SMOOTH_TIME_MS > 0:
    # Quanta velocità aggiungere ogni 50ms per raggiungere il MAX_SPEED nel tempo richiesto
    SPEED_STEP = MAX_SPEED / (SMOOTH_TIME_MS / (LOOP_DELAY * 1000))
else:
    SPEED_STEP = MAX_SPEED

# Variabili di stato per lo Smooth
current_speed = 0.0
current_state = "STOP    "

print(f"Emiglio-Tank Operativo. Max Speed: {MAX_SPEED} | Smooth Time: {SMOOTH_TIME_MS}ms")

try:
    while True:
        if ch_x.is_alive() and ch_y.is_alive():
            rx, ry = ch_x.width, ch_y.width

            # 1. LEGGI LA VOLONTA' DEL PILOTA (Desired State)
            if ry < 1470: desired_state = "AVANTI  "
            elif ry > 1650: desired_state = "INDIETRO"
            elif rx < 1430: desired_state = "RUOTA SX"
            elif rx > 1700: desired_state = "RUOTA DX"
            else: desired_state = "STOP    "

            # 2. GESTIONE DELLA TRANSIZIONE (Smooth In / Smooth Out)
            if desired_state == current_state:
                # Se continuiamo nella stessa direzione, il target è la velocità massima
                target_speed = MAX_SPEED if desired_state != "STOP    " else 0
            else:
                # Se vogliamo cambiare direzione (o fermarci), dobbiamo prima frenare
                target_speed = 0
                if current_speed == 0:
                    # Solo quando i motori sono fermi a 0, cambiamo direzione fisica
                    current_state = desired_state

            # 3. APPLICA L'ACCELERAZIONE / DECELERAZIONE
            if current_speed < target_speed:
                current_speed += SPEED_STEP
                if current_speed > target_speed: current_speed = target_speed # Limite superiore
            elif current_speed > target_speed:
                current_speed -= SPEED_STEP
                if current_speed < target_speed: current_speed = 0 # Limite inferiore

            # 4. INVIA I COMANDI ALL'HARDWARE
            # Scrive il PWM calcolato
            pi.set_PWM_dutycycle(PWMA, int(current_speed))
            pi.set_PWM_dutycycle(PWMB, int(current_speed))

            # Scrive i pin di direzione in base allo stato ATTUALE (non quello desiderato)
            if current_state == "AVANTI  ":
                pi.write(AIN1, 0); pi.write(AIN2, 1)
                pi.write(BIN1, 1); pi.write(BIN2, 0)
            elif current_state == "INDIETRO":
                pi.write(AIN1, 1); pi.write(AIN2, 0)
                pi.write(BIN1, 0); pi.write(BIN2, 1)
            elif current_state == "RUOTA SX":
                pi.write(AIN1, 1); pi.write(AIN2, 0)
                pi.write(BIN1, 1); pi.write(BIN2, 0)
            elif current_state == "RUOTA DX":
                pi.write(AIN1, 0); pi.write(AIN2, 1)
                pi.write(BIN1, 0); pi.write(BIN2, 1)
            elif current_state == "STOP    ":
                pi.write(AIN1, 0); pi.write(AIN2, 0)
                pi.write(BIN1, 0); pi.write(BIN2, 0)

            print(f"POWER: ON  | STATO: {current_state} | SPD: {int(current_speed):3d} | Y:{ry} X:{rx}      ", end='\r')

        else:
            # Sicurezza: Spegni tutto IMMEDIATAMENTE se perdi il segnale (niente smooth qui)
            print(f"POWER: OFF | Segnale assente...                                     ", end='\r')
            for p in [AIN1, AIN2, BIN1, BIN2, PWMA, PWMB]: pi.write(p, 0)
            current_speed = 0
            current_state = "STOP    "

        time.sleep(LOOP_DELAY)

except KeyboardInterrupt:
    for p in [AIN1, AIN2, BIN1, BIN2, PWMA, PWMB]: pi.write(p, 0)
    pi.stop()
