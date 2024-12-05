import time
from machine import Pin, PWM
from hcsr04 import HCSR04  # Asegúrate de que esta biblioteca esté instalada en tu entorno
import _thread  # Módulo de threading para ESP32 MicroPython

# Configuración del motor paso a paso (4 pines)
step_pins = [Pin(19, Pin.OUT), Pin(16, Pin.OUT), Pin(5, Pin.OUT), Pin(17, Pin.OUT)]

# Secuencia para controlar el motor paso a paso
seq = [
    [1, 0, 0, 1],
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
]

# Configuración del buzzer
buzzer = PWM(Pin(14))
buzzer.freq(1000)

# Configuración del sensor ultrasónico
sensor = HCSR04(trigger_pin=13, echo_pin=12)


# Notas para la melodía ajustada (en Hz), sin repeticiones consecutivas
# Notas para la melodía ajustada (en Hz), basadas en la transcripción que proporcionaste
notes = [
    261, 349, 349, 392, 349, 330, 293, 293,  # "DO FA FA SOL FA MI RE RE"
    293, 392, 392, 440, 392, 349, 330, 261, 261,  # "RE SOL SOL LA SOL FA MI DO DO"
    440, 440, 466, 440, 392, 349, 293,  # "LA LA SI B LA SOL FA RE"
    261, 261, 293, 392, 330, 349,  # "DO DO RE SOL MI FA"
    261, 349, 349, 349, 330,  # "DO FA FA FA MI"
    330, 349, 330, 293, 261,  # "MI FA MI RE DO"
    392, 440, 392, 349, 261,  # "SOL LA SOL FA DO"
    261, 261, 293, 392, 330, 349,  # "DO DO RE SOL MI FA"
    261, 349, 349, 392, 349, 330, 293, 293,  # "DO FA FA SOL FA MI RE RE"
    293, 392, 392, 440, 392, 349, 330, 261, 261,  # "RE SOL SOL LA SOL FA MI DO DO"
]

# Duraciones correspondientes para cada nota (en segundos)
durations = [
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # "DO FA FA SOL FA MI RE RE"
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # "RE SOL SOL LA SOL FA MI DO DO"
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5, 0.75,  # "LA LA SI B LA SOL FA RE"
    0.5, 0.5, 0.5, 0.5, 0.5, 0.5,  # "DO DO RE SOL MI FA"
    0.5, 0.5, 0.5, 0.5, 0.5,  # "DO FA FA FA MI"
    0.5, 0.5, 0.5, 0.5, 0.5,  # "MI FA MI RE DO"
    0.5, 0.5, 0.5, 0.5, 0.5,  # "SOL LA SOL FA DO"
    0.5, 0.5, 0.5, 0.5, 0.5,  # "DO DO RE SOL MI FA"
    0.5, 0.5, 0.5, 0.5, 0.5,  # "DO FA FA SOL FA MI RE RE"
   # "DO DO RE SOL MI FA"
]






def play_song():
    """Reproduce una canción navideña usando el buzzer."""
    # Asegúrate de que las listas tengan la misma longitud
    length = min(len(notes), len(durations))
    
    for i in range(length):  # Itera hasta la longitud más corta
        note = notes[i]
        duration = durations[i]
        if note == 0:  # Pausa
            buzzer.duty(0)
        else:
            buzzer.duty(512)  # Ciclo de trabajo del 50% para onda cuadrada
            buzzer.freq(note)
        time.sleep(duration)
    
    buzzer.duty(0)  # Apaga el buzzer después de la canción

def step_motor(steps, direction, delay=0.005):
    """Controla el motor paso a paso para un número específico de pasos."""
    for _ in range(steps):
        for step in (seq if direction == 1 else reversed(seq)):
            for pin, val in zip(step_pins, step):
                pin.value(val)
            time.sleep(delay)

def motor_task():
    """Tarea para ejecutar las acciones del motor."""
    # Girar motor 90 grados en sentido horario (~128 pasos)
    step_motor(128, 1)
    # Girar motor 180 grados en sentido antihorario
    step_motor(256, -1)
    # Girar motor de vuelta 90 grados en sentido horario
    step_motor(128, 1)

def action_task():
    """Ejecuta el motor y la música en paralelo."""
    # Inicia las tareas del motor y la música en hilos separados
    _thread.start_new_thread(motor_task, ())
    play_song()

def main():
    print("Esperando detección de objeto...")
    try:
        while True:
            # Leer distancia del sensor ultrasónico
            distance = sensor.distance_cm()
            print(f"Distancia: {distance:.2f} cm")
            
            if distance < 80:  # Objeto detectado dentro de 1 metro
                print("Objeto detectado. Realizando acciones...")
                action_task()  # Disparar ejecución paralela de motor y música
            else:
                # Apagar motor y buzzer si no se detecta objeto
                for pin in step_pins:
                    pin.value(0)
                buzzer.duty(0)
            
            # Esperar un momento antes de la siguiente lectura
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Programa detenido manualmente.")
        for pin in step_pins:
            pin.value(0)
        buzzer.duty(0)

if __name__ == "__main__":
    main()
