# daq_usb5203.py
import pexpect

def leer_temperatura(canal):
    try:
        # Ejecutar el programa interactivo
        child = pexpect.spawn('~/Linux_Drivers/USB/mcc-libusb/test-usb5203', timeout=5)

        # Paso 1: Enviar 't' para seleccionar termocupla
        child.expect("Hit.*:")  # espera cualquier línea del menú
        child.sendline("t")

        # Paso 2: Esperar canal
        child.expect("Enter channel.*:")
        child.sendline(str(canal))

        # Paso 3: Esperar tipo de termocupla
        child.expect("Enter thermocouple type.*:")
        child.sendline("K")

        # Paso 4: Leer la respuesta
        child.expect("Temperature.*C")  # buscar línea que mencione grados Celsius
        output = child.before.decode('utf-8') + child.after.decode('utf-8')
        child.sendline("e")  # salir del programa

        for line in output.splitlines():
            if "Temperature" in line and "C" in line:
                parts = line.split()
                for i, part in enumerate(parts):
                    if part == "C" and i > 0:
                        return float(parts[i-1])
        return None
    except Exception as e:
        print(f"Error leyendo temperatura del DAQ: {e}")
        return None
