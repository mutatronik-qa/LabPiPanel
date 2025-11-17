# LabPiPanel - Sistema de Control de Laboratorio Térmico

**Instituto Tecnológico Metropolitano (ITM)**  
Medellín, Colombia  
Facultad de Ingeniería

## Descripción

LabPiPanel es un sistema integrado de control de laboratorio para investigación térmica basado en Raspberry Pi 4. El proyecto está diseñado para evaluar nanofluidos en termosifones de dos fases y caracterizar propiedades térmicas de nuevos fluidos de trabajo.

Este sistema replica experimentos de investigación térmica, permitiendo control automatizado de instrumentación, adquisición de datos en tiempo real y análisis de propiedades térmicas de materiales avanzados.

## Características Principales

### Control de Instrumentación
- **Fuente de Alimentación BK Precision XLN30052**
  - Control de voltaje (0-300V) y corriente (0-5.2A)
  - Protecciones OVP/OCP/OPP
  - Comunicación por Telnet (puerto 5024)
  - Verificación de readback automática

- **DAQ Measurement Computing USB-5203**
  - 8 canales de termopares tipo K
  - ADC de 24-bit con CJC integrado
  - Validación de rango automática
  - Detección de termopares desconectados

- **Módulo de Relés Waveshare (4 canales)**
  - Control de bomba de fluido
  - 3 canales de respaldo
  - Lógica activa en BAJO (GPIO.LOW)

### Experimentos Automatizados
- Secuencias de niveles de potencia configurables
- Adquisición de datos con frecuencia ajustable
- Cálculo automático de resistencia térmica
- Exportación de datos a CSV con timestamp
- Manejo robusto de errores y protecciones

### Interfaz Web
- Diseño con identidad corporativa ITM
- Control en tiempo real de todos los instrumentos
- Visualización de temperaturas y mediciones
- Panel de experimentos automatizados
- Responsive design (desktop, tablet, móvil)

## Requisitos del Sistema

### Hardware
- Raspberry Pi 4 (2GB RAM mínimo)
- Sistema operativo: Raspberry Pi OS (Bullseye/Bookworm)
- Conexión Ethernet configurada con IP fija
- Fuente BK Precision XLN30052 conectada por red
- DAQ Measurement Computing USB-5203 conectado por USB
- Módulo RPi Relay Board Waveshare
- 8 termopares tipo K

### Software
- Python 3.9 o superior
- Drivers MCC Linux (Warren Jasper)
- Flask 3.0.0
- RPi.GPIO 0.7.1
- python-dotenv 1.0.0

## Instalación

### 1. Clonar el Repositorio

\`\`\`bash
cd ~
git clone <URL_DEL_REPOSITORIO>
cd LabPiPanel
\`\`\`

### 2. Crear Entorno Virtual

\`\`\`bash
python3 -m venv venv
source venv/bin/activate
\`\`\`

### 3. Instalar Dependencias

\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 4. Instalar Drivers MCC Linux

\`\`\`bash
# Seguir instrucciones del fabricante Measurement Computing
# para instalar drivers USB-5203
\`\`\`

### 5. Configurar Variables de Entorno

\`\`\`bash
cp .env.example .env
nano .env
\`\`\`

Editar el archivo `.env` con la configuración de su laboratorio:

\`\`\`
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
FLASK_DEBUG=False
XLN_HOST=192.168.1.100
XLN_PORT=5024
\`\`\`

### 6. Configurar Pines GPIO

Verificar en `config.py` que los pines GPIO coincidan con su configuración:

\`\`\`python
RELAY_PINS = {
    "RELAY_1": 26,  # Bomba de fluido
    "RELAY_2": 20,
    "RELAY_3": 21,
    "RELAY_4": 16
}
\`\`\`

### 7. Crear Directorios de Logs y Resultados

Los directorios se crean automáticamente, pero puede verificar:

\`\`\`bash
mkdir -p logs results
\`\`\`

## Uso

### Iniciar el Sistema

\`\`\`bash
source venv/bin/activate
python labpipanel.py
\`\`\`

El servidor Flask se iniciará en `http://<IP_RASPBERRY>:5000`

### Acceder a la Interfaz Web

Abra un navegador y navegue a:

\`\`\`
http://<IP_RASPBERRY>:5000
\`\`\`

### Ejecutar un Experimento

1. Configure los parámetros del experimento en el panel correspondiente:
   - Niveles de potencia (W): `1.0, 2.0, 3.0`
   - Duración por nivel (segundos): `600`
   - Frecuencia de muestreo (segundos): `60`
   - Resistencia de carga (Ω): `10`

2. Active la opción "Activar bomba de fluido" si es necesario

3. Haga clic en "Iniciar Experimento"

4. Los resultados se guardarán automáticamente en `results/thermal_experiment_YYYYMMDD_HHMMSS.csv`

### API REST

El sistema expone una API REST completa. Ver `API.md` para documentación detallada.

## Estructura del Proyecto

\`\`\`
LabPiPanel/
├── labpipanel.py           # Servidor Flask principal
├── fuente_xln.py           # Control de fuente XLN30052
├── daq_usb5203.py          # Lectura de DAQ USB-5203
├── relay_controller.py     # Control de relés GPIO
├── thermal_experiment.py   # Experimentos automatizados
├── config.py               # Configuración centralizada
├── requirements.txt        # Dependencias Python
├── .env.example            # Plantilla de variables de entorno
├── README.md               # Este archivo
├── API.md                  # Documentación de API
├── HARDWARE.md             # Especificaciones de hardware
├── GUIA_ITM.md             # Contexto institucional
├── templates/
│   └── index.html          # Interfaz web con identidad ITM
├── static/
│   ├── css/
│   │   └── style.css       # Estilos corporativos ITM
│   └── img/
│       └── itm_logo.png    # Logo institucional
├── logs/                   # Archivos de log rotantes
└── results/                # Resultados de experimentos (CSV)
\`\`\`

## Seguridad

### Validación de Entradas
- Voltaje: 0-300V con confirmación para valores >50V
- Corriente: 0-5.2A
- Temperaturas: -270 a 2000°C (sanity check)

### Protecciones de Hardware
- OVP (Over Voltage Protection): 310V
- OCP (Over Current Protection): 5.5A
- OPP (Over Power Protection): 1600W

### Manejo de Errores
- Timeout en comunicaciones
- Detección de termopares desconectados
- Recuperación automática con reintentos
- Logging estructurado de todas las operaciones

## Solución de Problemas

### Error: "No se puede conectar con la fuente"
- Verificar que la fuente XLN30052 esté encendida
- Verificar conectividad de red: `ping <IP_FUENTE>`
- Verificar puerto Telnet: debe ser 5024 (NO 23)
- Revisar logs en `logs/app.log`

### Error: "No se pueden leer temperaturas"
- Verificar que el DAQ USB-5203 esté conectado: `lsusb`
- Verificar que los drivers MCC estén instalados
- Ejecutar `test-usb5203 -ch 0 -type K` manualmente
- Verificar que los termopares estén correctamente conectados

### Error: "Relés no responden"
- Verificar que los pines GPIO estén correctamente configurados en `config.py`
- Verificar que RPi.GPIO esté instalado: `pip show RPi.GPIO`
- Los relés son activos en BAJO (GPIO.LOW = ON, GPIO.HIGH = OFF)

### Experimento no inicia
- Verificar que no haya otro experimento en ejecución
- Verificar que todos los instrumentos estén conectados
- Revisar parámetros de configuración (potencia, duración, resistencia)
- Consultar logs detallados en `logs/app.log`

## Mantenimiento

### Logs
Los logs rotan automáticamente:
- Archivo: `logs/app.log`
- Tamaño máximo: 10 MB
- Backups: 5 archivos

### Resultados
Los archivos CSV se guardan en `results/`:
- Formato: `thermal_experiment_YYYYMMDD_HHMMSS.csv`
- Incluyen: timestamp, voltaje, corriente, temperaturas, resistencia térmica

### Calibración
Realizar calibración periódica de:
- Termopares tipo K (verificar con baño térmico)
- Fuente de alimentación (verificar con multímetro de referencia)
- Resistencia de carga (medir con óhmetro)

## Identidad Visual ITM

Este proyecto utiliza la paleta de colores corporativa del Instituto Tecnológico Metropolitano:

- **Azul Navy ITM**: `#17335C` (encabezados, menús principales)
- **Azul ITM**: `#2B598D` (fondos secundarios, links, bordes)
- **Verde Éxito**: `#27AE60` (estados OK, confirmaciones)
- **Rojo Alerta**: `#E74C3C` (errores, alertas)
- **Amarillo Advertencia**: `#F39C12` (advertencias)

## Licencia

Este proyecto es desarrollado con fines educativos e investigativos en el Instituto Tecnológico Metropolitano (ITM), Medellín, Colombia.

## Soporte

Para soporte técnico, consultar:
- Documentación técnica en `HARDWARE.md`
- Documentación de API en `API.md`
- Logs del sistema en `logs/app.log`

---

**Instituto Tecnológico Metropolitano (ITM)**  
Institución de Educación Superior de Alta Calidad  
Medellín, Colombia  
2024
