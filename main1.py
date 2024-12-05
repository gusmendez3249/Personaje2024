import time
import network
from machine import Pin, SPI, PWM
from max7219 import MAX7219
import ubinascii
import ustruct
from umqtt.simple import MQTTClient

# Configuración de la conexión SPI para las matrices MAX7219
spi = SPI(1, baudrate=1000000, polarity=0, phase=0, sck=Pin(18), mosi=Pin(23))  # Bus SPI (común para ambas matrices)
cs1 = Pin(5, Pin.OUT)  # Chip Select para el primer MAX7219 (Matriz 1)
cs2 = Pin(4, Pin.OUT)  # Chip Select para el segundo MAX7219 (Matriz 2)

matrix1 = MAX7219(spi, cs1, 1)  # Primer MAX7219
matrix2 = MAX7219(spi, cs2, 1)  # Segundo MAX7219

# Configuración del Servomotor
servo = PWM(Pin(19), freq=50)  # 50 Hz es la frecuencia típica de los servos

# Función para mover el servo de manera suave y restringida
def set_angle_slow(angle):
    # Limitar el ángulo a un máximo de 40 grados
    angle = max(0, min(40, angle))  # Asegura que el ángulo esté en el rango de 0 a 40 grados
    
    current_angle = 0  # Empezamos desde 0 grados
    step = 2  # Definir el tamaño del paso (puedes ajustar este valor)
    direction = 1 if angle > current_angle else -1  # Determinar si debemos aumentar o disminuir el ángulo

    # Mover en pequeños pasos hacia el ángulo deseado
    while current_angle != angle:
        current_angle += direction * step
        if direction == 1 and current_angle > angle:
            current_angle = angle
        elif direction == -1 and current_angle < angle:
            current_angle = angle
        pulse_width = int((current_angle / 180) * 75 + 40)  # Convertir el ángulo en pulso para el servo
        servo.duty(pulse_width)
        time.sleep(0.05)  # Retardo pequeño para hacer el movimiento más lento
    servo.duty(int((angle / 180) * 75 + 40))  # Ajustar el pulso final

# Configuración del MQTT
MQTT_BROKER = "broker.emqx.io"
MQTT_PORT = 1883
MQTT_TOPIC_SUBSCRIBE = "gds0642/gcm/control"
MQTT_CLIENT_ID = ubinascii.b2a_base64(ustruct.pack(">Q", time.ticks_ms())).decode('utf-8')
client = MQTTClient(MQTT_CLIENT_ID, MQTT_BROKER, port=MQTT_PORT)

# Estado actual del mensaje MQTT
mqtt_message = None

# Función para conectar a WiFi
def conectar_wifi():
    print("Conectando a WiFi...", end="")
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_if.connect('UTNG_GUEST', 'R3d1nv1t4d0s#UT')
    while not sta_if.isconnected():
        print(".", end="")
        time.sleep(0.3)
    print("WiFi Conectada!")

# Función para manejar los mensajes de MQTT
def on_message(topic, msg):
    global mqtt_message
    print(f"Mensaje recibido en {topic}: {msg}")
    mqtt_message = msg  # Guardar el mensaje recibido para procesarlo en el ciclo principal

# Suscribirse al topic de Node-RED
def suscribirse_mqtt():
    client.set_callback(on_message)
    client.subscribe(MQTT_TOPIC_SUBSCRIBE)
    print(f"Suscrito al topic {MQTT_TOPIC_SUBSCRIBE}")

# Función para mover la mano (servo) 80 grados hacia adelante y luego regresar
def mover_mano():
    print("Moviendo la mano...")
    set_angle_slow(0)   # Mover la mano a la posición inicial (0 grados)
    time.sleep(1)
    set_angle_slow(40)  # Mover la mano a los 40 grados hacia adelante
    time.sleep(1)
    set_angle_slow(0)   # Regresar la mano a la posición inicial (0 grados)
    time.sleep(1)
    set_angle_slow(40)  # Mover la mano a los 40 grados hacia adelante nuevamente
    time.sleep(1)
    set_angle_slow(0)   # Volver a la posición inicial (0 grados)
    time.sleep(1)

# Función para guiñar el ojo
def guinar_ojo():
    print("Guiñando el ojo...")
    matrix1.fill(0)  # Cerrar el ojo izquierdo
    matrix1.show()
    time.sleep(0.5)
    matrix1.fill(1)  # Abrir el ojo izquierdo
    matrix1.show()
    time.sleep(0.5)

# Función para dibujar un círculo (iris) en las matrices
def dibujar_circulo(matrix, cx, cy, r):
    for x in range(cx-r, cx+r+1):
        for y in range(cy-r, cy+r+1):
            if (x - cx)**2 + (y - cy)**2 <= r**2:  # Ecuación del círculo
                if 0 <= x < 8 and 0 <= y < 8:
                    matrix.pixel(x, y, 1)
    matrix.show()

# Función para dibujar un ojo completo
def dibujar_ojo(matrix, cx, cy, iris_r, pupila_r, pupila_x, pupila_y):
    matrix.fill(0)  # Limpiar la matriz
    dibujar_circulo(matrix, cx, cy, iris_r)  # Dibujar el iris
    matrix.pixel(pupila_x, pupila_y, 1)  # Dibujar la pupila
    matrix.show()

# Función para simular el parpadeo
def parpadear_ojo(matrix):
    matrix.fill(0)  # Ojo cerrado
    matrix.show()
    time.sleep(0.3)
    matrix.fill(1)  # Ojo completamente abierto
    matrix.show()
    time.sleep(0.3)

# Función para la animación predeterminada con efectos chidos
def animacion_predeterminada():
    print("Ejecutando animación predeterminada...")

    # Movimiento lento de las pupilas de izquierda a derecha
    for pos in range(0, 8, 2):
        dibujar_ojo(matrix1, 3, 3, 3, 1, 3 + pos, 3)
        dibujar_ojo(matrix2, 3, 3, 3, 1, 3 - pos, 3)
        time.sleep(0.2)  # Movimiento más lento

    # Parpadeo suave de los ojos
    for _ in range(3):  # Repetir parpadeo 3 veces
        parpadear_ojo(matrix1)
        parpadear_ojo(matrix2)
        time.sleep(0.5)

    # Movimiento de las pupilas mirando en diferentes direcciones
    for i in range(4):
        # Mirar hacia la izquierda
        dibujar_ojo(matrix1, 3, 3, 3, 1, 1, 3)
        dibujar_ojo(matrix2, 3, 3, 3, 1, 1, 3)
        time.sleep(0.5)

        # Mirar hacia la derecha
        dibujar_ojo(matrix1, 3, 3, 3, 1, 5, 3)
        dibujar_ojo(matrix2, 3, 3, 3, 1, 5, 3)
        time.sleep(0.5)

        # Mirar hacia arriba
        dibujar_ojo(matrix1, 3, 3, 3, 1, 3, 1)
        dibujar_ojo(matrix2, 3, 3, 3, 1, 3, 1)
        time.sleep(0.5)

        # Mirar hacia abajo
        dibujar_ojo(matrix1, 3, 3, 3, 1, 3, 5)
        dibujar_ojo(matrix2, 3, 3, 3, 1, 3, 5)
        time.sleep(0.5)

    # Efecto sorpresa: Dilatación progresiva de las pupilas
    for r in range(1, 4):
        dibujar_ojo(matrix1, 3, 3, 3, r, 3, 3)
        dibujar_ojo(matrix2, 3, 3, 3, r, 3, 3)
        time.sleep(0.7)

    # Volver a las pupilas normales
    dibujar_ojo(matrix1, 3, 3, 3, 1, 3, 3)
    dibujar_ojo(matrix2, 3, 3, 3, 1, 3, 3)
    time.sleep(0.5)

# Conectar a MQTT
def conectar_mqtt():
    client.connect()
    print("Conectado al broker MQTT")

# Ciclo principal
try:
    conectar_wifi()  # Conectar a Wi-Fi
    conectar_mqtt()  # Conectar al broker MQTT
    suscribirse_mqtt()  # Suscribirse al topic de Node-RED

    while True:
        # Escuchar mensajes MQTT
        client.check_msg()

        # Procesar el mensaje recibido
        if mqtt_message == b'1':  # Mover mano
            mover_mano()
            mqtt_message = None  # Resetear el mensaje
        elif mqtt_message == b'2':  # Guiñar ojo
            guinar_ojo()
            mqtt_message = None  # Resetear el mensaje
        else:
            # Ejecutar la animación predeterminada si no hay mensaje
            animacion_predeterminada()

except KeyboardInterrupt:
    print("Programa detenido por el usuario.")
    matrix1.fill(0)
    matrix2.fill(0)
    matrix1.show()
    matrix2.show()
    servo.deinit()  # Detener el servo
    client.disconnect()  # Desconectar del broker MQTT

