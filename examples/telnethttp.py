from flask import Flask, jsonify
from fuente_xln import FuenteXLN

app = Flask(__name__)

# Puedes alternar entre 'telnet' y 'http' según cómo esté configurada tu fuente
fuente = FuenteXLN(modo='http', http_url='http://192.168.1.123')  # <-- usa la IP real de la fuente

@app.route("/fuente/escalonado")
def run_waveform():
    fuente.configurar_programa_escalonado()
    fuente.ejecutar_programa()
    return jsonify({"estado": "programa ejecutado"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
