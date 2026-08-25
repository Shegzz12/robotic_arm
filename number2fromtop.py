# -*- coding: utf-8 -*-
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# ==========================================
# USER CONFIGURATION (SET YOUR ANGLE LIMITS)
# ==========================================
MIN_ANGLE = 0.0   # Closed grip position in degrees (0 to 180)
MAX_ANGLE = 100.0  # Open grip position in degrees (0 to 180)

# Connect to pigpio daemon
factory = PiGPIOFactory()

PULSE_MIN = 0.5 / 1000
PULSE_MAX = 2.5 / 1000

# Initialize GPIO 25 (Physical Pin 22)
grip = Servo(25, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)


# ==========================================
# ANGLE & VALUE HELPER FUNCTIONS
# ==========================================
def angle_to_value(angle):
    """Convert angle in degrees (0 to 180) to gpiozero Servo value (-1 to 1)."""
    # Clamp angle between 0 and 180
    angle = max(0.0, min(180.0, angle))
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
        
        # FIX: Clamp current_val strictly between -1.0 and 1.0 to prevent floating-point overshoot
        clamped_val = max(-1.0, min(1.0, current_val))
        servo.value = clamped_val
        
        current_angle = value_to_angle(clamped_val)
        
        print(f"\rCurrent Position -> Angle: {current_angle:5.1f} deg | Value: {clamped_val:.3f}", end="", flush=True)
        sleep(step_delay)
        
    # Ensure final position lands cleanly on end_val
    servo.value = max(-1.0, min(1.0, end_val))
    print()  # New line when movement completes


# ==========================================
# MAIN CONTROL LOOP
# ==========================================
print("==========================================")
print("     GPIO 25 GRIPPER VERIFICATION TEST    ")
print("==========================================")

current_angle = MAX_ANGLE
grip.value = angle_to_value(current_angle)  # Set initial starting position

try:
    while True:
        print(f"\nClosing Grip (Target: {MIN_ANGLE} deg)...")
        move_to_angle_smooth(grip, current_angle, MIN_ANGLE, steps=50, step_delay=0.03)
        current_angle = MIN_ANGLE
        sleep(2)

        print(f"\nOpening Grip (Target: {MAX_ANGLE} deg)...")
        move_to_angle_smooth(grip, current_angle, MAX_ANGLE, steps=50, step_delay=0.03)
        current_angle = MAX_ANGLE
        sleep(2)

except KeyboardInterrupt:
    print("\n\nStopping test...")

finally:
    grip.detach()
    print("Servo on GPIO 25 detached safely.")
