# Configuración del sistema de termorregulación
import board

# Pines
PIN_SENSOR = board.IO5      # DS18B20 data

PIN_RELAY  = board.IO19     # Módulo relé

PIN_PWM    = board.IO18     # MOSFET PWM (velocidad ventiladores)

PIN_SDA    = board.IO21     # LCD I2C data
PIN_SCL    = board.IO22     # LCD I2C clock

# Umbrales térmicos (°C)
TEMP_IDEAL_MAX  = 18.0      # Por encima de esto → activar ventiladores
TEMP_IDEAL_MIN  = 16.0      # Por debajo de esto → apagar ventiladores

TEMP_CRITICA    = 22.0      # Por encima de esto → alerta crítica

# Tiempos
INTERVALO_LECTURA = 5       # Segundos entre cada lectura del sensor
