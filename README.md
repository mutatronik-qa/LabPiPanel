# LabPiPanel
 Control de laboradorio con funete XLN30052 y el DAQ 5203

# LabPiPanel

**LabPiPanel** es una plataforma de control y monitoreo en tiempo real para experimentos de laboratorio, basada en **Raspberry Pi** y desarrollada con **Flask**.  
Permite controlar una fuente de voltaje BK Precision XLN30052, leer datos de un DAQ USB-5203 y operar un módulo de relés RPi_Relay_Board — todo desde una interfaz web interactiva.

## 🚀 Características

- 🔌 Control de fuente de voltaje XLN30052 vía Telnet/HTTP.
- 🌡 Lectura de temperatura desde DAQ USB-5203 (o simulación en Linux).
- ⚡ Control de relés RPi en tiempo real.
- 🖥 Interfaz web amigable con actualización en vivo vía WebSockets.
- 🍓 Diseñado para correr en Raspberry Pi 3 (o superior).

---

## 📦 Requisitos

- Raspberry Pi con Raspbian
- Python 3.9+
- Acceso de red a la fuente XLN30052
- DAQ USB-5203 (requiere Windows para acceso real, o simulación en Linux)
- Módulo RPi_Relay_Board
- Dependencias Python:

```bash
pip install flask flask-socketio eventlet RPi.GPIO pyusb
```

```bash
git clone 
cd LabPiPanel
```

Test demo
Execute the following commands in the terminal, download the demo and extract it to the specified directory.
```
wget https://files.waveshare.com/upload/0/0c/RPi_Relay_Board.zip
unzip -o RPi_Relay_Board.zip -d ./RPi_Relay_Board
sudo chmod 777 -R RPi_Relay_Board
cd RPi_Relay_Board
```


sudo nano /etc/systemd/system/labpipanel.service


sudo systemctl daemon-reexec
sudo systemctl daemon-reload
sudo systemctl enable labpipanel.service


sudo systemctl start labpipanel.service


sudo systemctl status labpipanel.service
