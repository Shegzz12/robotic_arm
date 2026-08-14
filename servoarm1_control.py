w# -*- coding: utf-8 -*-
import sys
import tty
import termios
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# 1. Connect to pigpio daemon
factory = PiGPIOFactory()

PULSE_MIN = 0.5 / 1000
PULSE_MAX = 2.5 / 1000

# 2. Define Servos based on your wiring setup
# GPIO 17: Grip / Claw
# GPIO 18: Grip Pitch (Claw Up/Down)
# GPIO 27: Main Body / Shoulder Up/Down
# GPIO 22: Base Rotation (90 degrees Left / Right)
grip       = Servo(17, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
grip_pitch = Servo(18, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
shoulder   = Servo(27, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
base       = Servo(22, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)

# Set initial rest values (-1.0 to 1.0)
pos_base = 0.0
pos_shoulder = -0.5
pos_pitch = 0.0
pos_grip = -0.8

# Apply starting positions
base.value = pos_base
shoulder.value = pos_shoulder
grip_pitch.value = pos_pitch
grip.value = pos_grip

# Helper function to read single keypresses
def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch

STEP = 0.05  # Movement sensitivity per keypress

print("=========================================")
print("      ROBOTIC ARM KEYBOARD CONTROL      ")
print("=========================================")
print(" Controls:")
print("   A / D : Rotate Base Left / Right")
print("   W / S : Move Shoulder Up / Down")
print("   I / K : Pitch Grip Up / Down")
print("   O / C : Open / Close Grip")
print("   Q     : Quit Program")
print("=========================================")

try:
    while True:
        key = getch().lower()

        if key == 'q':
            print("\nExiting program...")
            break

        # Base Rotation (A / D)
        elif key == 'a':
            pos_base = max(-1.0, pos_base - STEP)
            base.value = pos_base
            print(f"Base: {pos_base:.2f}")

        elif key == 'd':
            pos_base = min(1.0, pos_base + STEP)
            base.value = pos_base
            print(f"Base: {pos_base:.2f}")

        # Shoulder Movement (W / S)
        elif key == 'w':
            pos_shoulder = max(-1.0, pos_shoulder - STEP)
            shoulder.value = pos_shoulder
            print(f"Shoulder: {pos_shoulder:.2f}")

        elif key == 's':
            pos_shoulder = min(1.0, pos_shoulder + STEP)
            shoulder.value = pos_shoulder
            print(f"Shoulder: {pos_shoulder:.2f}")

        # Grip Pitch Movement (I / K)
        elif key == 'i':
            pos_pitch = max(-1.0, pos_pitch - STEP)
            grip_pitch.value = pos_pitch
            print(f"Grip Pitch: {pos_pitch:.2f}")

        elif key == 'k':
            pos_pitch = min(1.0, pos_pitch + STEP)
            grip_pitch.value = pos_pitch
            print(f"Grip Pitch: {pos_pitch:.2f}")

        # Grip Open / Close (O / C)
        elif key == 'o':
            pos_grip = max(-1.0, pos_grip - STEP)
            grip.value = pos_grip
            print(f"Grip Open: {pos_grip:.2f}")

        elif key == 'c':
            pos_grip = min(1.0, pos_grip + STEP)
            grip.value = pos_grip
            print(f"Grip Close: {pos_grip:.2f}")

except KeyboardInterrupt:
    pass

finally:
    # Safely detach all servos on exit
    grip.detach()
    grip_pitch.detach()
    shoulder.detach()
    base.detach()
    print("Arm detached safely.")
