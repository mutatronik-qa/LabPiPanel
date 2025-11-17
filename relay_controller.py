"""
Módulo de control para relés Waveshare RPi Relay Board
Control de 4 relés mediante GPIO (activos en BAJO)
Instituto Tecnológico Metropolitano (ITM) - Medellín, Colombia
"""

import logging
from typing import Dict

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False
    logging.warning("RPi.GPIO no disponible - Modo simulación activado")

logger = logging.getLogger(__name__)


class RelayController:
    """Controlador para módulo de 4 relés Waveshare (activos en BAJO)"""
    
    def __init__(self, relay_pins: Dict[str, int]):
        """
        Inicializa controlador de relés
        
        Args:
            relay_pins: Diccionario con nombres y pines GPIO (BCM)
        """
        self.relay_pins = relay_pins
        self.relay_states = {}
        
        if GPIO_AVAILABLE:
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            for name, pin in self.relay_pins.items():
                GPIO.setup(pin, GPIO.OUT, initial=GPIO.HIGH)
                self.relay_states[name] = False
                logger.info(f"Relé {name} (GPIO {pin}) inicializado: DESACTIVADO")
        else:
            for name in self.relay_pins.keys():
                self.relay_states[name] = False
                logger.info(f"Relé {name} inicializado en modo simulación")
    
    def activate_relay(self, relay_name: str) -> bool:
        """
        Activa un relé específico (GPIO LOW)
        
        Args:
            relay_name: Nombre del relé (ej: "RELAY_1")
            
        Returns:
            True si activación exitosa
        """
        if relay_name not in self.relay_pins:
            logger.error(f"Relé {relay_name} no existe")
            return False
        
        pin = self.relay_pins[relay_name]
        
        try:
            if GPIO_AVAILABLE:
                GPIO.output(pin, GPIO.LOW)
            
            self.relay_states[relay_name] = True
            logger.info(f"Relé {relay_name} (GPIO {pin}) ACTIVADO")
            return True
        except Exception as e:
            logger.error(f"Error activando relé {relay_name}: {e}")
            return False
    
    def deactivate_relay(self, relay_name: str) -> bool:
        """
        Desactiva un relé específico (GPIO HIGH)
        
        Args:
            relay_name: Nombre del relé
            
        Returns:
            True si desactivación exitosa
        """
        if relay_name not in self.relay_pins:
            logger.error(f"Relé {relay_name} no existe")
            return False
        
        pin = self.relay_pins[relay_name]
        
        try:
            if GPIO_AVAILABLE:
                GPIO.output(pin, GPIO.HIGH)
            
            self.relay_states[relay_name] = False
            logger.info(f"Relé {relay_name} (GPIO {pin}) DESACTIVADO")
            return True
        except Exception as e:
            logger.error(f"Error desactivando relé {relay_name}: {e}")
            return False
    
    def toggle_relay(self, relay_name: str) -> bool:
        """
        Cambia el estado de un relé (on->off, off->on)
        
        Args:
            relay_name: Nombre del relé
            
        Returns:
            True si cambio exitoso
        """
        if relay_name not in self.relay_pins:
            logger.error(f"Relé {relay_name} no existe")
            return False
        
        current_state = self.relay_states.get(relay_name, False)
        
        if current_state:
            return self.deactivate_relay(relay_name)
        else:
            return self.activate_relay(relay_name)
    
    def get_relay_state(self, relay_name: str) -> bool:
        """
        Consulta el estado de un relé
        
        Args:
            relay_name: Nombre del relé
            
        Returns:
            True si activo, False si inactivo
        """
        return self.relay_states.get(relay_name, False)
    
    def get_all_states(self) -> Dict[str, bool]:
        """
        Obtiene estado de todos los relés
        
        Returns:
            Diccionario con nombre -> estado
        """
        return self.relay_states.copy()
    
    def deactivate_all(self) -> bool:
        """
        Desactiva todos los relés (modo seguro)
        
        Returns:
            True si todas las desactivaciones fueron exitosas
        """
        success = True
        
        for relay_name in self.relay_pins.keys():
            if not self.deactivate_relay(relay_name):
                success = False
        
        if success:
            logger.info("Todos los relés desactivados")
        else:
            logger.warning("Algunos relés no se desactivaron correctamente")
        
        return success
    
    def cleanup(self):
        """Limpia recursos GPIO al finalizar"""
        if GPIO_AVAILABLE:
            self.deactivate_all()
            GPIO.cleanup()
            logger.info("GPIO limpiado")
