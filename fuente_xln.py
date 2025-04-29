# fuente_xln.py
import telnetlib
import requests
import socket

class FuenteXLN:
    def __init__(self, host, http_port=80, telnet_port=23, timeout=2):
        self.host = host
        self.http_port = http_port
        self.telnet_port = telnet_port
        self.timeout = timeout
        self.method = self._detectar_metodo()
        self.telnet = None
        if self.method == "telnet":
            self.telnet = telnetlib.Telnet(self.host, self.telnet_port, self.timeout)

    def _detectar_metodo(self):
        try:
            with socket.create_connection((self.host, self.telnet_port), timeout=self.timeout):
                return "telnet"
        except:
            pass
        try:
            r = requests.get(f"http://{self.host}:{self.http_port}/", timeout=self.timeout)
            if r.status_code == 200:
                return "http"
        except:
            pass
        raise ConnectionError("No se pudo detectar un método de comunicación válido con la fuente")

    def enviar_comando(self, comando):
        if self.method == "telnet":
            try:
                self.telnet.write((comando + "\n").encode("ascii"))
                return self.telnet.read_until(b"\n", timeout=self.timeout).decode("ascii").strip()
            except Exception as e:
                return f"Error Telnet: {e}"
        elif self.method == "http":
            try:
                r = requests.post(f"http://{self.host}:{self.http_port}/comando", json={"cmd": comando})
                return r.text.strip()
            except Exception as e:
                return f"Error HTTP: {e}"

    def set_voltage(self, volts):
        return self.enviar_comando(f"VOLT {volts}")

    def set_current(self, amps):
        return self.enviar_comando(f"CURR {amps}")

    def get_voltage_current(self):
        volt = self.enviar_comando("MEAS:VOLT?")
        curr = self.enviar_comando("MEAS:CURR?")
        return volt, curr

    def cerrar(self):
        if self.method == "telnet" and self.telnet:
            self.telnet.close()
            self.telnet = None