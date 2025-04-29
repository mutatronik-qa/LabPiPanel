from flask import Flask, request, jsonify, render_template
import subprocess
import time

app = Flask(__name__)

# Estado inicial de los relés
relay_status = {
    'Relay1': 1,
    'Relay2': 1,
    'Relay3': 1,
    'Relay4': 1,
}

@app.route('/')
def index():
    return render_template('index.html')  # Asegúrate de tener index.html en /templates

@app.route('/Relay', methods=['POST'])
def control_relays():
    global relay_status
    data = request.form.to_dict()
    for k in relay_status.keys():
        if k in data:
            relay_status[k] = int(data[k])
            print(f"Relay {k} set to {'ON' if relay_status[k] else 'OFF'}")
            # Aquí va tu lógica para activar/desactivar los relés
    return '', 204

@app.route('/set_voltage', methods=['POST'])
def set_voltage():
    voltage = request.json.get('voltage')
    print(f"Set voltage to {voltage} V")
    # Aquí va el comando para controlar la fuente XLN30052
    return jsonify({'status': 'ok'})

@app.route('/set_current', methods=['POST'])
def set_current():
    current = request.json.get('current')
    print(f"Set current to {current} A")
    # Aquí va el comando para controlar la fuente XLN30052
    return jsonify({'status': 'ok'})

@app.route('/get_voltage_current')
def get_voltage_current():
    # Simulación temporal
    return jsonify({"voltage": 5.1, "current": 0.8})

@app.route('/read_daq')
def read_daq():
    
    channel = request.args.get('channel', 0, type=int)
    print(f"Reading from DAQ channel {channel}")
    # Aquí deberías poner el código que lee desde el DAQ USB-5203
    return jsonify({'temperature': 22.5 + channel})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
