# emiglio-controller
Robot controller code on Raspberry pi 1 B

## Setup
usa `piImager` per flashare il Raspberry pi 1 B, scegli il modello, poi versione lite OS senza gui. **SCEGLI "pi" come nome utente**, il raspberry pi 1 B non ha scheda wifi quindi devi pluggare ethernet e fare una prima configurazione con cavo HDMI per sbloccare ssh. Inoltre, ci mette molto ad avviarsi e quindi per capire cosa sta succedendo all'inizio serve HDMI

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

```
python blink.py
```
schema TODO

```
python debug-controller.py
```
schema TODO

```
python control.py
```
schema TODO

## Servizi automatici


```
sudo nano /etc/systemd/system/control.service
```

```
[Unit]
Description=Foo

[Service]
ExecStart=/usr/bin/python /home/pi/control.py

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