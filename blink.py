import pigpio
import time

# Configurazione del pin
# GPIO 8 (BCM) = Pin fisico 24
LED_PIN = 7
#25 e 8 ok 4 7 ok
#7 no 11 no 22 no
# Connessione al demone pigpiod
pi = pigpio.pi()

if not pi.connected:
    print("Assicurati di aver avviato 'sudo pigpiod'!")
    exit()

# Imposta il pin come OUTPUT
pi.set_mode(LED_PIN, pigpio.OUTPUT)

print(f"Blink avviato sul GPIO {LED_PIN} (Pin 24). Premi Ctrl+C per fermare.")

try:
    while True:
        pi.write(LED_PIN, 1) # Accendi
        print("LED ON ", end='\r')
        time.sleep(0.5)

        pi.write(LED_PIN, 0) # Spegni
        print("LED OFF", end='\r')
        time.sleep(0.5)

except KeyboardInterrupt:
    print("\nBlink interrotto. Pulisco i pin...")
    pi.write(LED_PIN, 0) # Spegne il LED prima di uscire
    pi.stop()