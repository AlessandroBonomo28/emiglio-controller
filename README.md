# emiglio-controller
Robot controller code on Raspberry pi 1 B
- https://alessandrobonomo28.github.io/posts/Trasformare-Emiglio-in-un-AI-assistant/
- https://alessandrobonomo28.github.io/posts/Trasformare-Emiglio-in-un-AI-assistant-2/
## Setup
usa `piImager` per flashare il Raspberry pi 1 B, scegli il modello, poi versione lite OS senza gui. **SCEGLI "pi" come nome utente**, il raspberry pi 1 B non ha scheda wifi quindi devi pluggare ethernet e fare una prima configurazione con cavo HDMI per sbloccare ssh. Inoltre, ci mette molto ad avviarsi e quindi per capire cosa sta succedendo all'inizio serve HDMI.

**Nota importante**: mai spegnere il raspberry staccando la spina altrimenti si corrompe la SD card. Prima premere il pulsante di spegnimento configurato, attendere spegnimento (si capisce dai led del raspberry vicino l'usb e poi staccare la spina.

```
sudo raspi-config
```
- abilita autologin
- abilita ssh se non lo hai già attivato

ora installiamo dipendenze python
```
sudo apt install pigpio python3-pigpio
```

avviamo servizio gpio
```
sudo pigpiod
```

abilitiamo il servizio per l'avvio automatico
```
sudo systemctl enable pigpiod
```

- cloniamo questo repo e testiamo gli script con python
```
git clone https://github.com/AlessandroBonomo28/emiglio-controller
```
Ecco un primo programma di test che riceve il segnale dal radiocomando e attiva 4 led di debug in base alla direzione di movimento
```
python control.py
```

<img width="1200" height="726" alt="R-Pi-1-GPIO-Pinout-768x726-2453249405 - Copia" src="https://github.com/user-attachments/assets/dc38b802-5264-4092-a896-d7cea30ca8b9" />

### Tank movement
per muovere Emiglio uso lo script `tank.py`. Il driver `tb6612fng` pilota il carico di un battery pack sui 4 motori in base a 4 input gpio digitali e 2 gpio PWM che controllano la velocità del motore A e B. Più info qui:
- https://lastminuteengineers.com/tb6612fng-dc-motor-control-arduino-tutorial/

<img width="1200" height="726" alt="R-Pi-1-GPIO-Pinout-768x726-2453249405 - Copia - Copia" src="https://github.com/user-attachments/assets/00d1ae42-3b6a-415b-9eca-51cafb995c0e" />

## Servizi automatici


```
sudo nano /etc/systemd/system/control.service
```

```
[Unit]
Description=Foo

[Service]
ExecStart=/usr/bin/python /home/pi/tank.py

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl enable control.service
```

```
sudo nano /etc/systemd/system/button.service
```

```
[Unit]
Description=Foo

[Service]
ExecStart=/usr/bin/python /home/pi/btn.py

[Install]
WantedBy=multi-user.target
```

```
sudo systemctl enable button.service
```
