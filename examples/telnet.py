import telnetlib

HOST = "192.168.1.150"  # Dirección IP de la fuente
PORT = 5025  # Puerto Telnet

def send_command(command):
    try:
        tn = telnetlib.Telnet(HOST, PORT)
        tn.write(command.encode('ascii') + b"\n")
        response = tn.read_until(b"\n", timeout=2).decode('ascii').strip()
        tn.close()
        return response
    except Exception as e:
        return f"Error: {e}"

# Ejemplo: Configurar voltaje a 10V
print(send_command("VOLT 10"))

# Ejemplo: Leer el voltaje actual
print(send_command("MEAS:VOLT?"))
