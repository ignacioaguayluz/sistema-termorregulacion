# Sistema de termorregulación para ajolotes

import time
import board
import busio # manejo de comunicaciones entre chips / Unión LCD-IdeaBoard / Protocolo de comunicación
import pwmio # Controlar velocidad de ventiladores a través del Mosfet
import digitalio # Manejar los pines digitales, para el relay 

# Sensor DS18B20
import adafruit_ds18x20 # Para leer temperaturas del sensor
from adafruit_onewire.bus import OneWireBus # Libreria para para comunicarse con el sensor

# Configuración del proyecto
from config import (
    PIN_SENSOR, PIN_RELAY, PIN_PWM,
    PIN_SDA, PIN_SCL,
    TEMP_IDEAL_MAX, TEMP_IDEAL_MIN, TEMP_CRITICA,
    INTERVALO_LECTURA
)

# Sensor de temperatura
ow_bus = OneWireBus(PIN_SENSOR) # Crea el bus 1-Wire, es como abrir una comunicación con el pin IO5
sensor = adafruit_ds18x20.DS18X20(ow_bus, ow_bus.scan()[0]) # Buscar quién esta conectado y recibir el primero de la lista

# Pantalla LCD (que controlamos con comandos directos sin librería de Adafruit)
# Primero crearemos el objeto de control directo sobre el pin SDA, activando su resistencia interna pull/up de 3.3V
# esto fuerza a la IdeaBoard a tener su propio voltaje de referencia antes de que el CircuitPython intente validar el bus I2C
sda_pin = digitalio.DigitalInOut(PIN_SDA) 
sda_pin.direction = digitalio.Direction.INPUT
sda_pin.pull = digitalio.Pull.UP

scl_pin = digitalio.DigitalInOut(PIN_SCL)
scl_pin.direction = digitalio.Direction.INPUT
scl_pin.pull = digitalio.Pull.UP

sda_pin.deinit() # con esto liberamos el pin de su control manual pero el pull-up queda grabado el tiempo suficiente para que CircuitPython lo detecte y pueda crear el bus
scl_pin.deinit()

i2c = busio.I2C(PIN_SCL, PIN_SDA)
LCD_ADDR = 0x27 # dirección de la I2C

def lcd_send(nibble, rs=False):
    """Mandamos un nibble que no es más que 4 bits, porque el Protocolo de la LCD
    en modo '4-bit' solo manda esa cantidad de información.
    rs  es el 'Register Select' que es un booleano que slecciona a cuál de los dos registros internos de
    la LCD le estamos hablando.
    """
    control = 0x08 # hexadecimal de 8 que en binario sería 00001000, esto es más que nada para estar asignado valores a control y que si rs=True que el backlight y RS queden activos juntos
    if rs:
        control |= 0x01
    byte_actual = (nibble << 4) | control # desplazamos los 4 bits a la izquierda, moviendo los bits de datos hacia la mitad del byte para dejar espacio a los bits de control (backlight, rs, Enable)
    if i2c.try_lock():
        try:
            # aquí mandamos el byte con enable en high esperamos medio milisegundo y luego lo mandamos de nuevo en low, esto permite que la lcd lea los datos que le mandamos 
            i2c.writeto(LCD_ADDR, bytes([byte_actual | 0x04]))
            time.sleep(0.0005)
            i2c.writeto(LCD_ADDR, bytes([byte_actual & 0xFB]))
            time.sleep(0.0005)
        finally:
            i2c.unlock()

def lcd_clear(): # Limpiamos la pantalla
    lcd_send(0x00); lcd_send(0x01)
    time.sleep(0.002)

def lcd_segunda_linea():
    """Función para mover el lcd a la segunda línea.
    """
    lcd_send(0x0C, rs=False) 
    lcd_send(0x00, rs=False)

def lcd_print(texto):
    """Recorremos el string letra por letra, con valor convertidmos la letra a su ASCII
    luego desplazamos a la derecha esos bits para poder leerlos como un número normal.
    """
    for caracter in texto:
        valor = ord(caracter)
        lcd_send((valor >> 4) & 0x0F, rs=True) # limpieza de seguridad
        lcd_send(valor & 0x0F, rs=True) # sacamos el nibble de abajo. y true porque le estamos mandado daos no un comando de control

def lcd_init():
    """Arranque obligatorio del controlador para que entienda en que modo vamos a hablarle.
    Hacemos 3 arranques para asegurar que el chip esta sincronizado. después cambaimos a modo 4-bit,
    para asegurar que quede en ese modo y decirle que la pantalla tiene 2 líneas.
    """
    time.sleep(0.05)
    lcd_send(0x03)
    time.sleep(0.005)
    lcd_send(0x03)
    time.sleep(0.001)
    lcd_send(0x03)
    time.sleep(0.001)
    lcd_send(0x02)
    lcd_send(0x02); lcd_send(0x08)
    lcd_send(0x00); lcd_send(0x0C)
    lcd_clear()

lcd_init()

# Relay
relay = digitalio.DigitalInOut(PIN_RELAY) # Creamos el objeto para controlar el pin del relay, señalo que ese es el pin del relay 
relay.direction = digitalio.Direction.OUTPUT # Mandamos señales de la IdeaBoard al relay
relay.value = False  # apagado por defecto por seguridad, no queremos que lo ventiladores empiecen encendidos

# MOSFET PWM 
mosfet = pwmio.PWMOut(PIN_PWM, frequency=20000) # Señal a 20kHz porque los ventiladores reciben señales a esa frecuencia, así nos mantenemos lejos del rango auditivo.
mosfet.duty_cycle = 0  # 0 = apagado, 65535 = máxima velocidad, porque CircuitPython no usa porcentajes, trabaja a 16 bits por ende 2¹⁶ = 65536

# Loop principal
while True:
    try:
        temperatura = sensor.temperature # llama a la libreria que lee la temperatura del sensor

        # Mostrar en LCD
        lcd_clear()
        lcd_print(f"Temp: {temperatura:.1f}C")
        lcd_segunda_linea()

        # Lógica de control
        if temperatura >= TEMP_CRITICA: # condición que en caso de llegar a la temperatura peligorsa activa los ventiladores al máximo
            lcd_print("ALERTA CRITICA!")
            relay.value = True
            mosfet.duty_cycle = 65535  # máxima velocidad

        elif temperatura >= TEMP_IDEAL_MAX: # regulamos la velocidad de los ventiladores en caso de acercarse a la temperatura máxima, y se asgina la velocidad proporcional al exceso 
            lcd_print("Ventilando...")
            relay.value = True
            # Velocidad proporcional a qué tan lejos está del umbral
            exceso = temperatura - TEMP_IDEAL_MAX
            velocidad = min(int(65535 * (exceso / 4)), 65535) # dividimos entre 4 porque es el número máximo de grados antes de ir al 100%
            mosfet.duty_cycle = velocidad
        
        # Zona de histéresis (16°C-18°C): si los ventiladores están encendidos siguen encendidos,
        # si están apagados siguen apagados. Evitamos que se prendan y apaguen constantemente.
        elif temperatura <= TEMP_IDEAL_MIN:
            lcd_print("Temp ideal :)")
            relay.value = False
            mosfet.duty_cycle = 0

        else:
            lcd_print("Monitoreando...")
        time.sleep(INTERVALO_LECTURA) # Esperamos 5 segundos antes de la siguiente lectura

    except KeyboardInterrupt: # Se ejecuta solo cuando presionamos Ctlr-C para detener el programa, para detener los ventiladores y que no queden prendidos cuando apagamos el programa.
        relay.value = False
        mosfet.duty_cycle = 0
        lcd_clear()
        lcd_print("Sistema detenido")
        lcd_segunda_linea()
        lcd_print("con exito")
        break

    except Exception as e: # Capturamos cualquier error que pueda pasar, sensor desconectado, lcd no responde, cualquier cosa.
        lcd_clear()
        lcd_print("Error:") # Mostramos el error
        lcd_segunda_linea()
        lcd_print(str(e)[:16])
        time.sleep(2)
