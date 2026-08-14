# -*- coding: utf-8 -*-
import readchar
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# ==========================================
# USER CONFIGURATION (SET YOUR ANGLE LIMITS)
# ==========================================
# Base (GPIO 22)
BASE_MIN_ANGLE   = 0.0     # Value: -1.0
BASE_MAX_ANGLE   = 180.0   # Value:  1.0
BASE_START_ANGLE = 90.0    # Value:  0.0

# Shoulder (GPIO 27)
SHOULDER_MIN_ANGLE   = 0.0     # Value: -1.0
SHOULDER_MAX_ANGLE   = 180.0   # Value:  1.0
SHOULDER_START_ANGLE = 45.0    # Value: -0.5

# Grip Pitch (GPIO 18)
PITCH_MIN_ANGLE   = 0.0     # Value: -1.0
PITCH_MAX_ANGLE   = 180.0   # Value:  1.0
PITCH_START_ANGLE = 90.0    # Value:  0.0

# Grip Open / Close (GPIO 23)
GRIP_MIN_ANGLE   = 9.0     # Value: -0.9 (Closed)
GRIP_MAX_ANGLE   = 72.0    # Value: -0.2 (Open)
GRIP_START_ANGLE = 18.0    # Value: -0.8 (Initial position)

# Step size in degrees per key press
ANGLE_STEP = 4.5  # Equivalent to ~0.05 gpiozero value step

# Connect to pigpio daemon
factory = PiGPIOFactory()

PULSE_MIN = 0.5 / 1000
PULSE_MAX = 2.5 / 1000

# Initialize All 4 Servos
base       = Servo(22, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
shoulder   = Servo(27, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
grip_pitch = Servo(18, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
grip       = Servo(23, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)


# ==========================================
# ANGLE & VALUE HELPER FUNCTIONS
# ==========================================
def angle_to_value(angle):
    """Convert angle in degrees (0 to 180) to gpiozero Servo value (-1 to 1)."""
    angle = max(0.0, min(180.0, angle))
    return (angle / 90.0) - 1.0

def value_to_angle(val):
    """Convert gpiozero Servo value (-1 to 1) to angle in degrees (0 to 180)."""
    return round((val + 1.0) * 90.0, 1)

def move_to_angle_smooth(servo, start_angle, end_angle, steps=5, step_delay=0.01):
    """
    Gradually moves the servo from start_angle to end_angle.
    - steps: Higher number = smoother movement.
    - step_delay: Delay between steps in seconds.
    """
    start_val = angle_to_value(start_angle)
    end_val = angle_to_value(end_angle)
    
    delta = (end_val - start_val) / steps
    current_val = start_val
    
    for _ in range(steps):
        current_val += delta
        servo.value = current_val
        sleep(step_delay)
        
    servo.value = end_val


# ==========================================
# MAIN CONTROL LOOP
# ==========================================
# Track current positions in degrees
pos_base     = BASE_START_ANGLE
pos_shoulder = SHOULDER_START_ANGLE
pos_pitch    = PITCH_START_ANGLE
pos_grip     = GRIP_START_ANGLE

# Initialize starting physical positions
base.value       = angle_to_value(pos_base)
shoulder.value   = angle_to_value(pos_shoulder)
grip_pitch.value = angle_to_value(pos_pitch)
grip.value       = angle_to_value(pos_grip)

print("=========================================")
print("   ROBOTIC ARM SMOOTH KEYBOARD CONTROL   ")
print("=========================================")
print(" Controls:")
print("   A / D : Base Left / Right     (GPIO 22)")
print("   W / S : Shoulder Up / Down    (GPIO 27)")
print("   I / K : Grip Pitch Up / Down  (GPIO 18)")
print("   O / C : Open / Close Grip     (GPIO 23)")
print("   Q     : Quit Program")
print("=========================================")

try:
    while True:
        key = readchar.readkey().lower()

        if key == 'q':
            print("\nExiting program...")
            break

        # --- Base Rotation (GPIO 22) -> A / D ---
        elif key == 'a':
            target_angle = max(BASE_MIN_ANGLE, pos_base - ANGLE_STEP)
            move_to_angle_smooth(base, pos_base, target_angle)
            pos_base = target_angle
            print(f"\rBase (GPIO 22)       -> Angle: {pos_base:5.1f} deg | Value: {angle_to_value(pos_base):.2f}", end="", flush=True)

        elif key == 'd':
            target_angle = min(BASE_MAX_ANGLE, pos_base + ANGLE_STEP)
            move_to_angle_smooth(base, pos_base, target_angle)
            pos_base = target_angle
            print(f"\rBase (GPIO 22)       -> Angle: {pos_base:5.1f} deg | Value: {angle_to_value(pos_base):.2f}", end="", flush=True)

        # --- Shoulder Movement (GPIO 27) -> W / S ---
        elif key == 'w':
            target_angle = max(SHOULDER_MIN_ANGLE, pos_shoulder - ANGLE_STEP)
            move_to_angle_smooth(shoulder, pos_shoulder, target_angle)
            pos_shoulder = target_angle
            print(f"\rShoulder (GPIO 27)   -> Angle: {pos_shoulder:5.1f} deg | Value: {angle_to_value(pos_shoulder):.2f}", end="", flush=True)

        elif key == 's':
            target_angle = min(SHOULDER_MAX_ANGLE, pos_shoulder + ANGLE_STEP)
            move_to_angle_smooth(shoulder, pos_shoulder, target_angle)
            pos_shoulder = target_angle
            print(f"\rShoulder (GPIO 27)   -> Angle: {pos_shoulder:5.1f} deg | Value: {angle_to_value(pos_shoulder):.2f}", end="", flush=True)

        # --- Grip Pitch Movement (GPIO 18) -> I / K ---
        elif key == 'i':
            target_angle = max(PITCH_MIN_ANGLE, pos_pitch - ANGLE_STEP)
            move_to_angle_smooth(grip_pitch, pos_pitch, target_angle)
            pos_pitch = target_angle
            print(f"\rGrip Pitch (GPIO 18) -> Angle: {pos_pitch:5.1f} deg | Value: {angle_to_value(pos_pitch):.2f}", end="", flush=True)

        elif key == 'k':
            target_angle = min(PITCH_MAX_ANGLE, pos_pitch + ANGLE_STEP)
            move_to_angle_smooth(grip_pitch, pos_pitch, target_angle)
            pos_pitch = target_angle
            print(f"\rGrip Pitch (GPIO 18) -> Angle: {pos_pitch:5.1f} deg | Value: {angle_to_value(pos_pitch):.2f}", end="", flush=True)

        # --- Grip Open / Close (GPIO 23) -> O / C ---
        elif key == 'o':
            target_angle = min(GRIP_MAX_ANGLE, pos_grip + ANGLE_STEP)
            move_to_angle_smooth(grip, pos_grip, target_angle)
            pos_grip = target_angle
            print(f"\rGrip Open (GPIO 23)  -> Angle: {pos_grip:5.1f} deg | Value: {angle_to_value(pos_grip):.2f}", end="", flush=True)

        elif key == 'c':
            target_angle = max(GRIP_MIN_ANGLE, pos_grip - ANGLE_STEP)
            move_to_angle_smooth(grip, pos_grip, target_angle)
            pos_grip = target_angle
            print(f"\rGrip Close (GPIO 23) -> Angle: {pos_grip:5.1f} deg | Value: {angle_to_value(pos_grip):.2f}", end="", flush=True)

except KeyboardInterrupt:
    pass

finally:
    grip.detach()
    grip_pitch.detach()
    shoulder.detach()
    base.detach()
    print("\nAll 4 servos detached safely.")
