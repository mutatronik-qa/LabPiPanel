import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)  # 🔹 Oculta warnings de telnetlib

from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import telnetlib  # 🔹 Aunque está obsoleto, aún funciona
import RPi.GPIO as GPIO
import usb.core
import usb.util

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# --- CONFIGURACIÓN DE RELÉS ---
GPIO.setwarnings(False)  # 🔹 Solución para el warning de pines ya en uso
GPIO.setmode(GPIO.BCM)
RELAY_PINS = [17, 27, 22, 23]
for pin in RELAY_PINS:
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)

# --- CONFIGURACIÓN DE FUENTE XLN30052 (Telnet) ---
HOST = "192.168.1.150"  # 🔹 Cambia a la IP de tu fuente
PORT = 5025  # 🔹 Puerto Telnet

def send_command(command):
    """Envía un comando a la fuente de poder mediante Telnet."""
    try:
        with telnetlib.Telnet(HOST, PORT) as tn:
            tn.write(command.encode('ascii') + b"\n")
            response = tn.read_until(b"\n", timeout=2)
            return response.decode("ascii").strip()
    except Exception as e:
        return f"Error: {e}"

# --- CONFIGURACIÓN DEL DAQ USB-5203 ---
def read_temperature():
    """Intenta leer la temperatura desde el DAQ USB-5203."""
    dev = usb.core.find(idVendor=0x09DB)  # Vendor ID de Measurement Computing
    if dev is None:
        return {"error": "DAQ no encontrado"}
    else:
        return {"temperature": "Simulación de temperatura (DAQ en Linux no soportado)"}

# --- RUTAS FLASK ---
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/set_voltage", methods=["POST"])
def set_voltage():
    """Establece el voltaje en la fuente de poder."""
    voltage = request.json.get("voltage")
    response = send_command(f"VOLT {voltage}")
    return jsonify({"message": response})

@app.route("/get_voltage", methods=["GET"])
def get_voltage():
    """Obtiene el voltaje actual de la fuente."""
    response = send_command("MEAS:VOLT?")
    return jsonify({"voltage": response})

@app.route("/get_temperature", methods=["GET"])
def get_temperature():
    """Obtiene la temperatura del DAQ."""
    response = read_temperature()
    return jsonify(response)

# --- CONTROL DE RELÉS CON WEBSOCKETS ---
@socketio.on("toggle_relay")
def toggle_relay(data):
    """Activa o desactiva un relé según los datos recibidos por WebSockets."""
    relay_id = int(data["relay"])
    state = bool(data["state"])

    if 0 <= relay_id < len(RELAY_PINS):
        GPIO.output(RELAY_PINS[relay_id], GPIO.HIGH if state else GPIO.LOW)
        status = {"relay": relay_id, "state": state}
        socketio.emit("relay_status", status)
    else:
        socketio.emit("relay_status", {"error": "Número de relé inválido"})

@socketio.on("request_relay_status")
def send_relay_status():
    """Envía el estado de todos los relés a la interfaz."""
    status = {f"Relay {i}": GPIO.input(pin) for i, pin in enumerate(RELAY_PINS)}
    socketio.emit("relay_status", status)

# --- EJECUCIÓN DEL SERVIDOR ---
if __name__ == "__main__":
    try:
        socketio.run(app, host="0.0.0.0", port=5000, debug=True)
    except KeyboardInterrupt:
        GPIO.cleanup()
