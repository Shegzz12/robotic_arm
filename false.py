from gpiozero import Servo
from time import sleep

# Connect servo signal wire to GPIO17 (physical pin 11)
servo = Servo(17, min_pulse_width=0.5/1000, max_pulse_width=2.5/1000)

try:
    while True:
        servo.min()      # Move to one extreme
        sleep(0.5)       # Small delay before moving again
        servo.max()      # Move to the other extreme
        sleep(0.5)
except KeyboardInterrupt:
    print("Program stopped")
    servo.detach()  # Stops sending signal so servo doesn't jitter/hold torque