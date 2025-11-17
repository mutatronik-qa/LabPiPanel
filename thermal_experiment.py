"""
Módulo de experimentos térmicos automatizados
Secuencia de niveles de potencia con adquisición de datos
Instituto Tecnológico Metropolitano (ITM) - Medellín, Colombia
"""

import logging
import time
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict
import math

from fuente_xln import FuenteXLN
from daq_usb5203 import DAQUSB5203
from relay_controller import RelayController

logger = logging.getLogger(__name__)


class ThermalExperiment:
    """Controlador de experimentos térmicos automatizados"""
    
    def __init__(
        self,
        fuente: FuenteXLN,
        daq: DAQUSB5203,
        relay: RelayController,
        results_dir: Path
    ):
        """
        Inicializa experimento térmico
        
        Args:
            fuente: Instancia de FuenteXLN
            daq: Instancia de DAQUSB5203
            relay: Instancia de RelayController
            results_dir: Directorio para guardar resultados
        """
        self.fuente = fuente
        self.daq = daq
        self.relay = relay
        self.results_dir = results_dir
        self.is_running = False
        self.current_experiment = None
        
        logger.info("ThermalExperiment inicializado")
    
    def calculate_power_settings(self, power_w: float, resistance_ohm: float) -> tuple:
        """
        Calcula voltaje y corriente para potencia deseada
        
        Args:
            power_w: Potencia deseada en vatios
            resistance_ohm: Resistencia de carga en ohmios
            
        Returns:
            Tupla (voltaje, corriente) o (None, None) si inválido
        """
        try:
            voltage = math.sqrt(power_w * resistance_ohm)
            current = voltage / resistance_ohm
            
            if voltage > 300 or current > 5.2:
                logger.error(f"Configuración excede límites: {voltage:.2f}V, {current:.3f}A")
                return (None, None)
            
            logger.debug(f"Potencia {power_w}W: {voltage:.2f}V @ {current:.3f}A (R={resistance_ohm}Ω)")
            return (voltage, current)
        except Exception as e:
            logger.error(f"Error calculando configuración de potencia: {e}")
            return (None, None)
    
    def calculate_thermal_resistance(
        self,
        temp_evap_avg: float,
        temp_cond_avg: float,
        power_w: float
    ) -> Optional[float]:
        """
        Calcula resistencia térmica del sistema
        
        Args:
            temp_evap_avg: Temperatura promedio del evaporador (°C)
            temp_cond_avg: Temperatura promedio del condensador (°C)
            power_w: Potencia aplicada (W)
            
        Returns:
            Resistencia térmica en °C/W o None si inválido
        """
        if power_w <= 0:
            logger.error("Potencia debe ser mayor que cero")
            return None
        
        delta_t = temp_evap_avg - temp_cond_avg
        r_thermal = delta_t / power_w
        
        logger.debug(f"R_thermal = ({temp_evap_avg:.2f} - {temp_cond_avg:.2f}) / {power_w} = {r_thermal:.4f} °C/W")
        
        return r_thermal
    
    def run_experiment(
        self,
        power_levels: List[float],
        duration_per_level: int,
        sample_rate: int,
        resistance_ohm: float = 10.0,
        evaporator_channels: List[int] = [0, 1, 2, 3],
        condenser_channels: List[int] = [4, 5, 6, 7],
        enable_pump: bool = True
    ) -> Dict:
        """
        Ejecuta experimento térmico completo
        
        Args:
            power_levels: Lista de niveles de potencia (W)
            duration_per_level: Duración de cada nivel (segundos)
            sample_rate: Intervalo entre muestras (segundos)
            resistance_ohm: Resistencia de la carga (Ω)
            evaporator_channels: Canales del evaporador
            condenser_channels: Canales del condensador
            enable_pump: Activar bomba de fluido
            
        Returns:
            Diccionario con resultados del experimento
        """
        if self.is_running:
            logger.error("Ya hay un experimento en ejecución")
            return {"status": "error", "message": "Experimento ya en ejecución"}
        
        self.is_running = True
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        experiment_name = f"thermal_experiment_{timestamp}"
        csv_path = self.results_dir / f"{experiment_name}.csv"
        
        logger.info(f"Iniciando experimento: {experiment_name}")
        logger.info(f"Niveles de potencia: {power_levels}W")
        logger.info(f"Duración por nivel: {duration_per_level}s")
        logger.info(f"Frecuencia de muestreo: {sample_rate}s")
        
        results = {
            "status": "in_progress",
            "name": experiment_name,
            "csv_file": str(csv_path),
            "power_levels": power_levels,
            "samples_collected": 0,
            "errors": []
        }
        
        try:
            if enable_pump:
                self.relay.activate_relay("RELAY_1")
                logger.info("Bomba de fluido activada")
                time.sleep(5)
            
            with open(csv_path, 'w', newline='') as csvfile:
                fieldnames = [
                    "timestamp", "elapsed_time", "power_level", "voltage", "current",
                    "temp_evap_ch0", "temp_evap_ch1", "temp_evap_ch2", "temp_evap_ch3",
                    "temp_cond_ch4", "temp_cond_ch5", "temp_cond_ch6", "temp_cond_ch7",
                    "temp_evap_avg", "temp_cond_avg", "r_thermal"
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                
                experiment_start = time.time()
                
                for level_idx, power_w in enumerate(power_levels):
                    logger.info(f"=== Nivel {level_idx + 1}/{len(power_levels)}: {power_w}W ===")
                    
                    voltage, current = self.calculate_power_settings(power_w, resistance_ohm)
                    
                    if voltage is None:
                        error_msg = f"No se pudo calcular configuración para {power_w}W"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                        continue
                    
                    if not self.fuente.set_voltage(voltage):
                        error_msg = f"Error configurando voltaje: {voltage}V"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                        continue
                    
                    if not self.fuente.set_current(current * 1.1):
                        error_msg = f"Error configurando corriente: {current}A"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                        continue
                    
                    if not self.fuente.output_on():
                        error_msg = "Error activando salida de fuente"
                        logger.error(error_msg)
                        results["errors"].append(error_msg)
                        continue
                    
                    level_start = time.time()
                    sample_count = 0
                    
                    while (time.time() - level_start) < duration_per_level:
                        sample_start = time.time()
                        
                        voltage_meas = self.fuente.measure_voltage()
                        current_meas = self.fuente.measure_current()
                        
                        temps = self.daq.read_all_channels()
                        
                        temp_evap_list = [temps.get(ch) for ch in evaporator_channels if temps.get(ch) is not None]
                        temp_cond_list = [temps.get(ch) for ch in condenser_channels if temps.get(ch) is not None]
                        
                        temp_evap_avg = sum(temp_evap_list) / len(temp_evap_list) if temp_evap_list else None
                        temp_cond_avg = sum(temp_cond_list) / len(temp_cond_list) if temp_cond_list else None
                        
                        r_thermal = None
                        if temp_evap_avg and temp_cond_avg and power_w > 0:
                            r_thermal = self.calculate_thermal_resistance(temp_evap_avg, temp_cond_avg, power_w)
                        
                        elapsed = time.time() - experiment_start
                        
                        row = {
                            "timestamp": datetime.now().isoformat(),
                            "elapsed_time": f"{elapsed:.2f}",
                            "power_level": power_w,
                            "voltage": f"{voltage_meas:.2f}" if voltage_meas else "N/A",
                            "current": f"{current_meas:.3f}" if current_meas else "N/A",
                            "temp_evap_ch0": f"{temps.get(0):.2f}" if temps.get(0) else "N/A",
                            "temp_evap_ch1": f"{temps.get(1):.2f}" if temps.get(1) else "N/A",
                            "temp_evap_ch2": f"{temps.get(2):.2f}" if temps.get(2) else "N/A",
                            "temp_evap_ch3": f"{temps.get(3):.2f}" if temps.get(3) else "N/A",
                            "temp_cond_ch4": f"{temps.get(4):.2f}" if temps.get(4) else "N/A",
                            "temp_cond_ch5": f"{temps.get(5):.2f}" if temps.get(5) else "N/A",
                            "temp_cond_ch6": f"{temps.get(6):.2f}" if temps.get(6) else "N/A",
                            "temp_cond_ch7": f"{temps.get(7):.2f}" if temps.get(7) else "N/A",
                            "temp_evap_avg": f"{temp_evap_avg:.2f}" if temp_evap_avg else "N/A",
                            "temp_cond_avg": f"{temp_cond_avg:.2f}" if temp_cond_avg else "N/A",
                            "r_thermal": f"{r_thermal:.4f}" if r_thermal else "N/A"
                        }
                        
                        writer.writerow(row)
                        csvfile.flush()
                        
                        sample_count += 1
                        results["samples_collected"] += 1
                        
                        protections = self.fuente.check_protections()
                        if protections["status"] != "ok":
                            error_msg = f"Protección activada: {protections['status']}"
                            logger.warning(error_msg)
                            results["errors"].append(error_msg)
                            break
                        
                        elapsed_sample = time.time() - sample_start
                        sleep_time = max(0, sample_rate - elapsed_sample)
                        
                        if sleep_time > 0:
                            time.sleep(sleep_time)
                    
                    logger.info(f"Nivel {power_w}W completado: {sample_count} muestras")
                    
                    self.fuente.output_off()
                    time.sleep(2)
            
            if enable_pump:
                self.relay.deactivate_relay("RELAY_1")
                logger.info("Bomba de fluido desactivada")
            
            results["status"] = "completed"
            total_time = time.time() - experiment_start
            results["total_time"] = f"{total_time:.2f}s"
            
            logger.info(f"Experimento completado: {results['samples_collected']} muestras en {total_time:.2f}s")
            logger.info(f"Resultados guardados en: {csv_path}")
            
        except KeyboardInterrupt:
            logger.warning("Experimento interrumpido por usuario")
            results["status"] = "interrupted"
            self.fuente.output_off()
            if enable_pump:
                self.relay.deactivate_relay("RELAY_1")
        
        except Exception as e:
            logger.error(f"Error durante experimento: {e}", exc_info=True)
            results["status"] = "error"
            results["errors"].append(str(e))
            self.fuente.output_off()
            if enable_pump:
                self.relay.deactivate_relay("RELAY_1")
        
        finally:
            self.is_running = False
            self.current_experiment = results
        
        return results
    
    def get_experiment_status(self) -> Dict:
        """
        Obtiene el estado del experimento actual
        
        Returns:
            Diccionario con estado del experimento
        """
        if self.is_running:
            return {
                "running": True,
                "experiment": self.current_experiment
            }
        else:
            return {
                "running": False,
                "last_experiment": self.current_experiment
            }
