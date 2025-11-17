"""
LabPiPanel - Sistema de Control de Laboratorio Térmico
Instituto Tecnológico Metropolitano (ITM) - Medellín, Colombia
Servidor Flask con API REST para control de instrumentación
"""

from flask import Flask, render_template, jsonify, request
import logging
from logging.handlers import RotatingFileHandler
import os
from datetime import datetime
from pathlib import Path
import threading

import config
from fuente_xln import FuenteXLN
from daq_usb5203 import DAQUSB5203
from relay_controller import RelayController
from thermal_experiment import ThermalExperiment

app = Flask(__name__)

logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    datefmt=config.LOG_DATE_FORMAT
)

file_handler = RotatingFileHandler(
    config.LOG_FILE,
    maxBytes=config.LOG_MAX_BYTES,
    backupCount=config.LOG_BACKUP_COUNT
)
file_handler.setFormatter(logging.Formatter(config.LOG_FORMAT))
app.logger.addHandler(file_handler)

logger = logging.getLogger(__name__)

fuente = FuenteXLN(config.XLN_HOST, config.XLN_PORT, config.XLN_TIMEOUT)
daq = DAQUSB5203(config.DAQ_CHANNELS, config.DAQ_THERMOCOUPLE_TYPE, config.DAQ_TIMEOUT)
relay = RelayController(config.RELAY_PINS)
experiment_controller = ThermalExperiment(fuente, daq, relay, config.RESULTS_DIR)

logger.info("=" * 80)
logger.info("LabPiPanel - Sistema de Control de Laboratorio Térmico")
logger.info("Instituto Tecnológico Metropolitano (ITM) - Medellín, Colombia")
logger.info("=" * 80)


@app.route('/')
def index():
    """Página principal del sistema"""
    return render_template('index.html')


@app.route('/api/status', methods=['GET'])
def api_status():
    """Estado general del sistema"""
    try:
        fuente_connected = fuente.connection is not None or fuente.connect()
        
        relay_states = relay.get_all_states()
        
        experiment_status = experiment_controller.get_experiment_status()
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "system": {
                "fuente": "connected" if fuente_connected else "disconnected",
                "daq": "ready",
                "relays": relay_states,
                "experiment": experiment_status
            }
        }), 200
    except Exception as e:
        logger.error(f"Error en /api/status: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/fuente/voltage', methods=['GET', 'POST'])
def api_fuente_voltage():
    """Obtener o configurar voltaje de la fuente"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            voltage = float(data.get('voltage', 0))
            
            if voltage < 0 or voltage > config.XLN_VOLTAGE_MAX:
                return jsonify({
                    "status": "error",
                    "message": f"Voltaje debe estar entre 0 y {config.XLN_VOLTAGE_MAX}V"
                }), 400
            
            if voltage > 50:
                confirm = data.get('confirm', False)
                if not confirm:
                    return jsonify({
                        "status": "warning",
                        "message": f"Voltaje alto ({voltage}V). Confirmar operación.",
                        "require_confirm": True
                    }), 200
            
            success = fuente.set_voltage(voltage)
            
            if success:
                return jsonify({
                    "status": "ok",
                    "voltage_set": voltage
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo configurar voltaje"
                }), 500
        
        else:
            voltage = fuente.get_voltage()
            
            if voltage is not None:
                return jsonify({
                    "status": "ok",
                    "voltage": voltage
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo leer voltaje"
                }), 500
    
    except Exception as e:
        logger.error(f"Error en /api/fuente/voltage: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/fuente/current', methods=['GET', 'POST'])
def api_fuente_current():
    """Obtener o configurar corriente límite de la fuente"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            current = float(data.get('current', 0))
            
            if current < 0 or current > config.XLN_CURRENT_MAX:
                return jsonify({
                    "status": "error",
                    "message": f"Corriente debe estar entre 0 y {config.XLN_CURRENT_MAX}A"
                }), 400
            
            success = fuente.set_current(current)
            
            if success:
                return jsonify({
                    "status": "ok",
                    "current_set": current
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo configurar corriente"
                }), 500
        
        else:
            current = fuente.get_current()
            
            if current is not None:
                return jsonify({
                    "status": "ok",
                    "current": current
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo leer corriente"
                }), 500
    
    except Exception as e:
        logger.error(f"Error en /api/fuente/current: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/fuente/output', methods=['GET', 'POST'])
def api_fuente_output():
    """Obtener o cambiar estado de salida de la fuente"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            state = data.get('state', 'off').lower()
            
            if state == 'on':
                success = fuente.output_on()
            elif state == 'off':
                success = fuente.output_off()
            else:
                return jsonify({
                    "status": "error",
                    "message": "Estado debe ser 'on' o 'off'"
                }), 400
            
            if success:
                return jsonify({
                    "status": "ok",
                    "output_state": state
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": f"No se pudo cambiar estado a {state}"
                }), 500
        
        else:
            state = fuente.get_output_state()
            
            if state is not None:
                return jsonify({
                    "status": "ok",
                    "output_state": "on" if state else "off"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": "No se pudo leer estado de salida"
                }), 500
    
    except Exception as e:
        logger.error(f"Error en /api/fuente/output: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/fuente/measure', methods=['GET'])
def api_fuente_measure():
    """Medir voltaje y corriente actual de la fuente"""
    try:
        voltage = fuente.measure_voltage()
        current = fuente.measure_current()
        
        if voltage is not None and current is not None:
            power = voltage * current
            
            return jsonify({
                "status": "ok",
                "voltage": round(voltage, 2),
                "current": round(current, 3),
                "power": round(power, 2)
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "No se pudieron obtener mediciones"
            }), 500
    
    except Exception as e:
        logger.error(f"Error en /api/fuente/measure: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/fuente/protections', methods=['GET'])
def api_fuente_protections():
    """Verificar estado de protecciones de la fuente"""
    try:
        protections = fuente.check_protections()
        
        return jsonify({
            "status": "ok",
            "protections": protections
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /api/fuente/protections: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/daq/read', methods=['GET'])
def api_daq_read():
    """Leer todos los canales del DAQ"""
    try:
        channels = request.args.getlist('channels', type=int)
        
        if channels:
            temps = daq.read_channels_list(channels)
        else:
            temps = daq.read_all_channels()
        
        evap_channels = config.EVAPORATOR_CHANNELS
        cond_channels = config.CONDENSER_CHANNELS
        
        temp_evap_avg = daq.get_average_temperature(evap_channels)
        temp_cond_avg = daq.get_average_temperature(cond_channels)
        
        return jsonify({
            "status": "ok",
            "timestamp": datetime.now().isoformat(),
            "temperatures": {f"ch{ch}": round(temp, 2) if temp else None for ch, temp in temps.items()},
            "averages": {
                "evaporator": round(temp_evap_avg, 2) if temp_evap_avg else None,
                "condenser": round(temp_cond_avg, 2) if temp_cond_avg else None
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /api/daq/read: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/relay/<relay_name>', methods=['GET', 'POST'])
def api_relay(relay_name):
    """Obtener o cambiar estado de un relé"""
    try:
        relay_name = relay_name.upper()
        
        if relay_name not in config.RELAY_PINS:
            return jsonify({
                "status": "error",
                "message": f"Relé {relay_name} no existe"
            }), 404
        
        if request.method == 'POST':
            data = request.get_json()
            action = data.get('action', 'toggle').lower()
            
            if action == 'on':
                success = relay.activate_relay(relay_name)
            elif action == 'off':
                success = relay.deactivate_relay(relay_name)
            elif action == 'toggle':
                success = relay.toggle_relay(relay_name)
            else:
                return jsonify({
                    "status": "error",
                    "message": "Acción debe ser 'on', 'off' o 'toggle'"
                }), 400
            
            if success:
                state = relay.get_relay_state(relay_name)
                return jsonify({
                    "status": "ok",
                    "relay": relay_name,
                    "state": "active" if state else "inactive"
                }), 200
            else:
                return jsonify({
                    "status": "error",
                    "message": f"No se pudo cambiar estado del relé {relay_name}"
                }), 500
        
        else:
            state = relay.get_relay_state(relay_name)
            
            return jsonify({
                "status": "ok",
                "relay": relay_name,
                "state": "active" if state else "inactive"
            }), 200
    
    except Exception as e:
        logger.error(f"Error en /api/relay/{relay_name}: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/relay/all', methods=['GET'])
def api_relay_all():
    """Obtener estado de todos los relés"""
    try:
        states = relay.get_all_states()
        
        return jsonify({
            "status": "ok",
            "relays": {name: ("active" if state else "inactive") for name, state in states.items()}
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /api/relay/all: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/experiment/run', methods=['POST'])
def api_experiment_run():
    """Ejecutar experimento térmico automatizado"""
    try:
        if experiment_controller.is_running:
            return jsonify({
                "status": "error",
                "message": "Ya hay un experimento en ejecución"
            }), 400
        
        data = request.get_json()
        
        power_levels = data.get('power_levels', config.EXPERIMENT_POWER_LEVELS)
        duration = data.get('duration', config.EXPERIMENT_DURATION_PER_LEVEL)
        sample_rate = data.get('sample_rate', config.EXPERIMENT_SAMPLE_RATE)
        resistance = data.get('resistance', 10.0)
        enable_pump = data.get('enable_pump', True)
        
        def run_experiment_thread():
            experiment_controller.run_experiment(
                power_levels=power_levels,
                duration_per_level=duration,
                sample_rate=sample_rate,
                resistance_ohm=resistance,
                evaporator_channels=config.EVAPORATOR_CHANNELS,
                condenser_channels=config.CONDENSER_CHANNELS,
                enable_pump=enable_pump
            )
        
        thread = threading.Thread(target=run_experiment_thread)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "ok",
            "message": "Experimento iniciado",
            "parameters": {
                "power_levels": power_levels,
                "duration_per_level": duration,
                "sample_rate": sample_rate,
                "resistance": resistance,
                "enable_pump": enable_pump
            }
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /api/experiment/run: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/api/experiment/status', methods=['GET'])
def api_experiment_status():
    """Obtener estado del experimento actual"""
    try:
        status = experiment_controller.get_experiment_status()
        
        return jsonify({
            "status": "ok",
            "experiment": status
        }), 200
    
    except Exception as e:
        logger.error(f"Error en /api/experiment/status: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.errorhandler(404)
def not_found(error):
    """Manejador de error 404"""
    return jsonify({"status": "error", "message": "Endpoint no encontrado"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Manejador de error 500"""
    logger.error(f"Error interno del servidor: {error}")
    return jsonify({"status": "error", "message": "Error interno del servidor"}), 500


if __name__ == '__main__':
    try:
        logger.info(f"Iniciando servidor Flask en {config.FLASK_HOST}:{config.FLASK_PORT}")
        logger.info(f"Acceda al sistema en: http://{config.FLASK_HOST}:{config.FLASK_PORT}")
        
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG
        )
    
    except KeyboardInterrupt:
        logger.info("Servidor detenido por usuario")
    
    finally:
        relay.cleanup()
        fuente.disconnect()
        logger.info("Sistema LabPiPanel finalizado")
