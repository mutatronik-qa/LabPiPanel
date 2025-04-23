import usb.core
import usb.util

# Encuentra el dispositivo USB-5203
dev = usb.core.find(idVendor=0x09DB)  # 0x09DB es el Vendor ID de Measurement Computing

if dev is None:
    print("Dispositivo DAQ no encontrado")
else:
    print(f"Dispositivo encontrado: {dev}")

