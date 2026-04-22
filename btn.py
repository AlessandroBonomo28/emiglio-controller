from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from subprocess import check_call
from signal import pause

# Forza l'uso del driver moderno per Kernel 6.12
factory = LGPIOFactory()

# Configura il pulsante sul GPIO 22
# hold_time=2.0 imposta il ritardo richiesto
btn = Button(22, hold_time=1.0, pin_factory=factory)

def shutdown():
    print("Pulsante premuto. Spegnimento...")
    check_call(['sudo', 'halt'])

# Associa l'azione alla pressione prolungata
btn.when_held = shutdown

print("in ascolto sul GPIO 22 (tieni premuto 1s per spegnere)...")
pause()