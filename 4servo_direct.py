# -*- coding: utf-8 -*-
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# 1. Connect to pigpio daemon for smooth hardware PWM
factory = PiGPIOFactory()

# Pulse width settings for standard 180-degree servos (0.5ms to 2.5ms)
PULSE_MIN = 0.5 / 1000
PULSE_MAX = 2.5 / 1000

# 2. Define the 4 Servos
# Pair A (Moves in Direction 1)
servo1 = Servo(17, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
servo2 = Servo(18, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)

# Pair B (Moves in Direction 2 - Opposite)
servo3 = Servo(27, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
servo4 = Servo(22, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)

print("Starting 4-Servo Synchronized Counter-Rotation Demo...")

try:
    while True:
        print("\n--- Position 1 ---")
        print("Servos 1 & 2 -> MAX (+1.0)")
        print("Servos 3 & 4 -> MIN (-1.0)")
        
        # Smooth transition to Position 1
        steps = 50
        for i in range(steps + 1):
            val = -1.0 + (2.0 * i / steps)  # Goes from -1.0 to +1.0
            
            # Pair A moves forward
            servo1.value = val
            servo2.value = val
            
            # Pair B moves backward
            servo3.value = -val
            servo4.value = -val
            
            sleep(0.03)  # Adjust delay for speed
        
        sleep(1.5)  # Pause at full extension

        print("\n--- Position 2 ---")
        print("Servos 1 & 2 -> MIN (-1.0)")
        print("Servos 3 & 4 -> MAX (+1.0)")
        
        # Smooth transition to Position 2
        for i in range(steps + 1):
            val = 1.0 - (2.0 * i / steps)  # Goes from +1.0 down to -1.0
            
            # Pair A moves backward
            servo1.value = val
            servo2.value = val
            
            # Pair B moves forward
            servo3.value = -val
            servo4.value = -val
            
            sleep(0.03)
        
        sleep(1.5)  # Pause at full extension

except KeyboardInterrupt:
    print("\nStopping and detaching all servos...")
    servo1.detach()
    servo2.detach()
    servo3.detach()
    servo4.detach()
    print("Done!")
