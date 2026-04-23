import pigpio
import time

# --- CONFIGURAZIONE ---
PIN_X, PIN_Y = 17, 18 # collegati rispettivamente a CH4 e CH2
PIN_LEFT, PIN_RIGHT, PIN_UP, PIN_DOWN = 7,27,25,4
class RC_Reader:
    def __init__(self, pi, gpio):
        self.pi = pi
        self.gpio = gpio
        self.width = 0
        self.last_tick = None
        self.last_update_time = time.time() # Tempo dell'ultimo impulso ricevuto
        self.last_width = 0
        self.stable_since = time.time()    # Da quanto tempo il valore è identico

        self.cb = pi.callback(gpio, pigpio.EITHER_EDGE, self._cbf)

    def _cbf(self, g, l, t):
        if l == 1:
            self.last_tick = t
        elif l == 0 and self.last_tick is not None:
            new_width = pigpio.tickDiff(self.last_tick, t)

            # Se il valore cambia (anche di poco), resettiamo il timer di stabilità
            if new_width != self.last_width:
                self.stable_since = time.time()
                self.last_width = new_width

            self.width = new_width
            self.last_update_time = time.time() # Segnale ricevuto ora!

    def is_alive(self):
        now = time.time()
        # 1. Controlliamo se arrivano impulsi (almeno uno ogni 0.5s)
        receiving = (now - self.last_update_time) < 0.5
        # 2. Controlliamo se il valore è "congelato" (stabile da più di 2s)
        flickering = (now - self.stable_since) < 2.0

        # È "acceso" solo se riceve impulsi E il valore sta minimamente fluttuando
        return receiving and flickering

# Setup
pi = pigpio.pi()
ch_x = RC_Reader(pi, PIN_X)
ch_y = RC_Reader(pi, PIN_Y)
pi.set_mode(PIN_LEFT, pigpio.OUTPUT)
pi.set_mode(PIN_RIGHT, pigpio.OUTPUT)
pi.set_mode(PIN_UP, pigpio.OUTPUT)
pi.set_mode(PIN_DOWN, pigpio.OUTPUT)

pi.write(PIN_LEFT, 0)
pi.write(PIN_RIGHT, 0)
pi.write(PIN_UP, 0)
pi.write(PIN_DOWN, 0)
print("Monitoraggio con Watchdog Hardware...")

try:
    while True:
        # La potenza è ON solo se entrambi i canali sono vivi
        powered = ch_x.is_alive() and ch_y.is_alive()

        if powered:
            rx, ry = ch_x.width, ch_y.width

            # Calcolo degli stati (Logica parallela)
            state_y = "CENTRO"
            if ry > 1600:
                state_y = "SU    "
                pi.write(PIN_UP, 1)
                pi.write(PIN_DOWN, 0)
            elif ry < 1470:
                state_y = "GIU   "
                pi.write(PIN_UP, 0)
                pi.write(PIN_DOWN, 1)
            else:
                pi.write(PIN_UP, 0)
                pi.write(PIN_DOWN, 0)

            state_x = "CENTRO"
            if rx < 1430:
                state_x = "DX    "
                pi.write(PIN_RIGHT, 1)
                pi.write(PIN_LEFT, 0)
            elif rx > 1700:
                state_x = "SX    "
                pi.write(PIN_RIGHT, 0)
                pi.write(PIN_LEFT, 1)
            else:
                pi.write(PIN_RIGHT, 0)
                pi.write(PIN_LEFT, 0)
            print(f"POWER: ON  | Y: {state_y} ({ry}) | X: {state_x} ({rx})      ", end='\r')
        else:
            print(f"POWER: OFF | Segnale assente o congelato...               ", end='\r')
            pi.write(PIN_LEFT, 0)
            pi.write(PIN_RIGHT, 0)
            pi.write(PIN_UP, 0)
            pi.write(PIN_DOWN, 0)
        time.sleep(0.1)

except KeyboardInterrupt:
    pi.stop()
