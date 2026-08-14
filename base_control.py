# -*- coding: utf-8 -*-
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# ==========================================
# USER CONFIGURATION (SET YOUR ANGLE LIMITS)
# ==========================================
MIN_ANGLE = 72.0   # Left target position in degrees (0 to 180) -> corresponds to -0.2
CENTER_ANGLE = 90.0 # Center position in degrees (0 to 180) -> corresponds to 0.0
MAX_ANGLE = 117.0  # Right target position in degrees (0 to 180) -> corresponds to +0.3

# Connect to pigpio daemon
factory = PiGPIOFactory()

PULSE_MIN = 0.2 / 1000
PULSE_MAX = 0.3 / 1000

# Initialize Base on GPIO 22
base = Servo(22, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)


# ==========================================
# ANGLE & VALUE HELPER FUNCTIONS
# ==========================================
def angle_to_value(angle):
    """Convert angle in degrees (0 to 180) to gpiozero Servo value (-1 to 1)."""
    angle = max(0, min(180, angle))
    return (angle / 90.0) - 1.0

def value_to_angle(val):
    """Convert gpiozero Servo value (-1 to 1) to angle in degrees (0 to 180)."""
    return round((val + 1.0) * 90.0, 1)

def move_to_angle_smooth(servo, start_angle, end_angle, steps=50, step_delay=0.03):
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
        current_angle = value_to_angle(current_val)
        
        # Real-time position printing on the same terminal line
        print(f"\rCurrent Position -> Angle: {current_angle:5.1f} deg | Value: {current_val:.3f}", end="", flush=True)
        sleep(step_delay)
        
    print()  # New line when movement completes


# ==========================================
# MAIN CONTROL LOOP
# ==========================================
print("==========================================")
print("   GPIO 22 SMOOTH BASE CONTROL TEST       ")
print("==========================================")

current_angle = CENTER_ANGLE
base.value = angle_to_value(current_angle)  # Set initial start position safely
sleep(1)

try:
    while True:
        print(f"\nSmoothly moving to RIGHT (Target: {MAX_ANGLE} deg)...")
        move_to_angle_smooth(base, current_angle, MAX_ANGLE, steps=50, step_delay=0.03)
        current_angle = MAX_ANGLE
        sleep(1.5)

        print(f"\nSmoothly moving back to CENTER (Target: {CENTER_ANGLE} deg)...")
        move_to_angle_smooth(base, current_angle, CENTER_ANGLE, steps=50, step_delay=0.03)
        current_angle = CENTER_ANGLE
        sleep(1.5)

        print(f"\nSmoothly testing LEFT (Target: {MIN_ANGLE} deg)...")
        move_to_angle_smooth(base, current_angle, MIN_ANGLE, steps=50, step_delay=0.03)
        current_angle = MIN_ANGLE
        sleep(1.5)

        print(f"\nSmoothly moving back to CENTER (Target: {CENTER_ANGLE} deg)...")
        move_to_angle_smooth(base, current_angle, CENTER_ANGLE, steps=50, step_delay=0.03)
        current_angle = CENTER_ANGLE
        sleep(1.5)

except KeyboardInterrupt:
    print("\n\nStopping Base test...")

finally:
    base.detach()
    print("Servo on GPIO 22 detached safely.")
