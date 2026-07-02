# test_sensor.py — Prueba del sensor DS18B20
 
import time
import board
from adafruit_onewire.bus import OneWireBus
import adafruit_ds18x20
 
# Inicializar sensor
ow_bus = OneWireBus(board.IO5)
dispositivos = ow_bus.scan()
print(f"Sensor detectado: {len(dispositivos)} dispositivo(s)")
 
sensor = adafruit_ds18x20.DS18X20(ow_bus, dispositivos[0])
 
# Leer 5 veces cada 3 segundos
print("Leyendo temperatura cada 3 segundos...\n")
for i in range(5):
    try:
        temp = sensor.temperature
        print(f"Lectura {i+1}: {temp:.1f}°C")
    except Exception as e:
        print(f"Lectura {i+1}: Error — {e}")
    time.sleep(3)
 
print("\nPrueba completada.")
