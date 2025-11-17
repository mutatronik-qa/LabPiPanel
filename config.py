"""
Configuración centralizada del sistema LabPiPanel
Instituto Tecnológico Metropolitano (ITM) - Medellín, Colombia
Proyecto: Sistema de Control para Laboratorio de Investigación Térmica
"""

import os
from pathlib import Path

# Directorios del proyecto
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
RESULTS_DIR = BASE_DIR / "results"
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"

# Crear directorios si no existen
LOGS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Configuración de Flask
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# Configuración de fuente XLN30052
XLN_HOST = os.getenv("XLN_HOST", "192.168.1.100")
XLN_PORT = int(os.getenv("XLN_PORT", 5024))
XLN_TIMEOUT = 10
XLN_VOLTAGE_MAX = 300.0
XLN_CURRENT_MAX = 5.2
XLN_OVP = 310.0
XLN_OCP = 5.5
XLN_OPP = 1600.0

# Configuración DAQ USB-5203
DAQ_TIMEOUT = 10
DAQ_CHANNELS = 8
DAQ_TEMP_MIN = -270.0
DAQ_TEMP_MAX = 2000.0
DAQ_THERMOCOUPLE_TYPE = "K"

# Configuración de relés (GPIO BCM - Activos en BAJO)
RELAY_PINS = {
    "RELAY_1": 26,  # Bomba de fluido
    "RELAY_2": 20,  # Respaldo 1
    "RELAY_3": 21,  # Respaldo 2
    "RELAY_4": 16   # Respaldo 3
}

# Configuración de experimentos
EXPERIMENT_POWER_LEVELS = [1.0, 2.0, 3.0]  # Watios
EXPERIMENT_DURATION_PER_LEVEL = 600  # 10 minutos en segundos
EXPERIMENT_SAMPLE_RATE = 60  # 1 lectura por minuto

# Canales de termopares
EVAPORATOR_CHANNELS = [0, 1, 2, 3]
CONDENSER_CHANNELS = [4, 5, 6, 7]

# Configuración de logging
LOG_FILE = LOGS_DIR / "app.log"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Identidad visual ITM
ITM_COLORS = {
    "navy": "#17335C",
    "blue": "#2B598D",
    "white": "#FFFFFF",
    "gray": "#333333",
    "success": "#27AE60",
    "alert": "#E74C3C",
    "warning": "#F39C12",
    "light_bg": "#F5F7FA",
    "border": "#DCE4EC"
}
