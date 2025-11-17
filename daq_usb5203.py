"""
Módulo de adquisición de datos para DAQ Measurement Computing USB-5203
Lectura de 8 canales de termopares tipo K usando drivers MCC Linux
Instituto Tecnológico Metropolitano (ITM) - Medellín, Colombia
"""

import logging
import subprocess
import re
from typing import List, Optional, Dict

logger = logging.getLogger(__name__)


class DAQUSB5203:
    """Controlador para DAQ USB-5203 con termopares tipo K"""
    
    def __init__(self, num_channels: int = 8, tc_type: str = "K", timeout: int = 10):
        """
        Inicializa el DAQ USB-5203
        
        Args:
            num_channels: Número de canales (0-7)
            tc_type: Tipo de termopar (J, K, R, S, T, N, E, B)
            timeout: Timeout para lectura en segundos
        """
        self.num_channels = num_channels
        self.tc_type = tc_type.upper()
        self.timeout = timeout
        self.temp_min = -270.0
        self.temp_max = 2000.0
        self.valid_tc_types = ["J", "K", "R", "S", "T", "N", "E", "B"]
        
        if self.tc_type not in self.valid_tc_types:
            logger.error(f"Tipo de termopar inválido: {tc_type}")
            raise ValueError(f"Tipo de termopar debe ser uno de: {self.valid_tc_types}")
        
        logger.info(f"DAQ USB-5203 inicializado: {num_channels} canales, tipo {tc_type}")
    
    def _validate_channel(self, channel: int) -> bool:
        """Valida que el canal esté en rango válido"""
        if not (0 <= channel < self.num_channels):
            logger.error(f"Canal {channel} fuera de rango [0-{self.num_channels-1}]")
            return False
        return True
    
    def _validate_temperature(self, temperature: float) -> bool:
        """Valida que la temperatura esté en rango físico razonable"""
        if not (self.temp_min <= temperature <= self.temp_max):
            logger.warning(f"Temperatura {temperature}°C fuera de rango esperado [{self.temp_min}-{self.temp_max}°C]")
            return False
        return True
    
    def _execute_mcc_command(self, command: str) -> Optional[str]:
        """
        Ejecuta comando de drivers MCC Linux
        
        Args:
            command: Comando a ejecutar
            
        Returns:
            Salida del comando o None si error
        """
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.returncode == 0:
                return result.stdout.strip()
            else:
                logger.error(f"Error en comando MCC: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            logger.error(f"Timeout ejecutando comando: {command}")
            return None
        except Exception as e:
            logger.error(f"Excepción ejecutando comando MCC: {e}")
            return None
    
    def read_channel(self, channel: int) -> Optional[float]:
        """
        Lee temperatura de un canal específico
        
        Args:
            channel: Número de canal (0-7)
            
        Returns:
            Temperatura en °C o None si error
        """
        if not self._validate_channel(channel):
            return None
        
        try:
            command = f"test-usb5203 -ch {channel} -type {self.tc_type}"
            output = self._execute_mcc_command(command)
            
            if output is None:
                logger.error(f"No se obtuvo respuesta del canal {channel}")
                return None
            
            temp_match = re.search(r'[-+]?\d*\.?\d+', output)
            if temp_match:
                temperature = float(temp_match.group())
                
                if self._validate_temperature(temperature):
                    logger.debug(f"Canal {channel}: {temperature:.2f}°C")
                    return temperature
                else:
                    logger.error(f"Canal {channel}: temperatura inválida {temperature}°C (posible open thermocouple)")
                    return None
            else:
                logger.error(f"No se pudo parsear temperatura del canal {channel}: {output}")
                return None
        
        except Exception as e:
            logger.error(f"Error leyendo canal {channel}: {e}")
            return None
    
    def read_all_channels(self) -> Dict[int, Optional[float]]:
        """
        Lee todos los canales configurados
        
        Returns:
            Diccionario con canal -> temperatura (°C)
        """
        readings = {}
        
        for channel in range(self.num_channels):
            readings[channel] = self.read_channel(channel)
        
        valid_count = sum(1 for v in readings.values() if v is not None)
        logger.info(f"Lectura completa: {valid_count}/{self.num_channels} canales válidos")
        
        return readings
    
    def read_channels_list(self, channels: List[int]) -> Dict[int, Optional[float]]:
        """
        Lee una lista específica de canales
        
        Args:
            channels: Lista de números de canal
            
        Returns:
            Diccionario con canal -> temperatura (°C)
        """
        readings = {}
        
        for channel in channels:
            readings[channel] = self.read_channel(channel)
        
        return readings
    
    def check_open_thermocouples(self) -> List[int]:
        """
        Detecta termopares desconectados (open thermocouple)
        
        Returns:
            Lista de canales con termopares desconectados
        """
        open_channels = []
        readings = self.read_all_channels()
        
        for channel, temp in readings.items():
            if temp is None:
                open_channels.append(channel)
        
        if open_channels:
            logger.warning(f"Termopares desconectados en canales: {open_channels}")
        
        return open_channels
    
    def get_average_temperature(self, channels: List[int]) -> Optional[float]:
        """
        Calcula temperatura promedio de un grupo de canales
        
        Args:
            channels: Lista de canales a promediar
            
        Returns:
            Temperatura promedio en °C o None si no hay lecturas válidas
        """
        readings = self.read_channels_list(channels)
        valid_temps = [temp for temp in readings.values() if temp is not None]
        
        if not valid_temps:
            logger.error(f"No hay lecturas válidas para promediar en canales {channels}")
            return None
        
        average = sum(valid_temps) / len(valid_temps)
        logger.debug(f"Promedio de canales {channels}: {average:.2f}°C ({len(valid_temps)} válidos)")
        
        return average
