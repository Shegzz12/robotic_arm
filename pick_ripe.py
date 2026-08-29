# -*- coding: utf-8 -*-
from gpiozero import Servo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

# ==========================================
# CONFIGURATION & CONSTANTS
# ==========================================
PULSE_MIN = 0.5 / 1000
PULSE_MAX = 2.5 / 1000

# Servo 1: GPIO 24 (Physical Pin 18)
MIN_ANGLE_24 = 80.0
MAX_ANGLE_24 = 140.0

# Servo 2: GPIO 25 (Physical Pin 22)
MIN_ANGLE_25 = 70.0
MAX_ANGLE_25 = 25.0

# Gripper Servo: GPIO 23 (Physical Pin 16)
CLOSED_GRIP_ANGLE = 90.0   # Closed grip position
OPEN_GRIP_ANGLE = 130.0    # Open grip position

# Base Servo: GPIO 18 (Physical Pin 12)
HOME_BASE_ANGLE = 57.5     # Pickup & Default Home Position
TARGET_BASE_ANGLE = 100.0  # Execution 2 Drop Location (MID)


# ==========================================
# HELPER FUNCTIONS
# ==========================================
def angle_to_value(angle):
    """Convert angle in degrees (0 to 180) to gpiozero Servo value (-1 to 1)."""
    angle = max(0.0, min(180.0, angle))
    return (angle / 90.0) - 1.0

def value_to_angle(val):
    """Convert gpiozero Servo value (-1 to 1) to angle in degrees (0 to 180)."""
    return round((val + 1.0) * 90.0, 1)

def move_to_angle_smooth(servo, start_angle, end_angle, name, steps=80, step_delay=0.04):
    """
    Smoothly moves the servo from start_angle to end_angle.
    If start_angle equals end_angle, no movement is performed.
    """
    if abs(start_angle - end_angle) < 0.1:
        servo.value = angle_to_value(end_angle)
        return

    start_val = angle_to_value(start_angle)
    end_val = angle_to_value(end_angle)
    
    delta = (end_val - start_val) / steps
    current_val = start_val
    
    for _ in range(steps):
        current_val += delta
        clamped_val = max(-1.0, min(1.0, current_val))
        servo.value = clamped_val
        
        current_angle = value_to_angle(clamped_val)
        print(f"\r[{name}] Angle: {current_angle:5.1f} deg | Value: {clamped_val:.3f}", end="", flush=True)
        sleep(step_delay)
        
    servo.value = max(-1.0, min(1.0, end_val))
    print()


# ==========================================
# MAIN EXECUTION: DROP AT 100°
# ==========================================
print("==========================================")
print("  EXECUTION 2: PICK AT 57.5° -> DROP AT 100° -> HOME")
print("==========================================")

factory = PiGPIOFactory()

# Initialize Servo objects without sudden position assignments
servo_24 = Servo(24, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
servo_25 = Servo(25, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
grip     = Servo(23, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
base     = Servo(18, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)

try:
    # --------------------------------------
    # 1. INITIALIZATION & HOME CHECK
    # --------------------------------------
    print("Checking home positions...")

    # Engage hardware output smoothly to initial positions
    servo_24.value = angle_to_value(MIN_ANGLE_24)
    servo_25.value = angle_to_value(MIN_ANGLE_25)
    grip.value     = angle_to_value(CLOSED_GRIP_ANGLE)
    base.value     = angle_to_value(HOME_BASE_ANGLE)
    
    sleep(0.8)

    # --------------------------------------
    # 2. PICK & LIFT UP SEQUENCE
    # --------------------------------------
    print("\n--- PHASE 1: PICK AT HOME (57.5°) ---")
    
    # Open grip before reaching down
    print(f"Opening Grip ({CLOSED_GRIP_ANGLE} -> {OPEN_GRIP_ANGLE} deg)...")
    move_to_angle_smooth(grip, CLOSED_GRIP_ANGLE, OPEN_GRIP_ANGLE, name="Gripper", steps=40, step_delay=0.03)
    sleep(0.3)

    # Extend Arm Down
    print(f"Moving GPIO 24 Down ({MIN_ANGLE_24} -> {MAX_ANGLE_24} deg)...")
    move_to_angle_smooth(servo_24, MIN_ANGLE_24, MAX_ANGLE_24, name="GPIO 24", steps=80, step_delay=0.04)
    sleep(0.3)

    print(f"Moving GPIO 25 Down ({MIN_ANGLE_25} -> {MAX_ANGLE_25} deg)...")
    move_to_angle_smooth(servo_25, MIN_ANGLE_25, MAX_ANGLE_25, name="GPIO 25", steps=80, step_delay=0.04)
    sleep(0.3)

    # Grip object
    print(f"Closing Grip ({OPEN_GRIP_ANGLE} -> {CLOSED_GRIP_ANGLE} deg)...")
    move_to_angle_smooth(grip, OPEN_GRIP_ANGLE, CLOSED_GRIP_ANGLE, name="Gripper", steps=40, step_delay=0.03)
    sleep(0.8)

    # Retract arm before base rotation
    print("\nLifting arm up before base rotation...")
    print(f"Retracting GPIO 25 ({MAX_ANGLE_25} -> {MIN_ANGLE_25} deg)...")
    move_to_angle_smooth(servo_25, MAX_ANGLE_25, MIN_ANGLE_25, name="GPIO 25", steps=80, step_delay=0.04)
    sleep(0.3)

    print(f"Retracting GPIO 24 ({MAX_ANGLE_24} -> {MIN_ANGLE_24} deg)...")
    move_to_angle_smooth(servo_24, MAX_ANGLE_24, MIN_ANGLE_24, name="GPIO 24", steps=80, step_delay=0.04)
    sleep(0.3)

    # --------------------------------------
    # 3. BASE ROTATION TO 100.0°
    # --------------------------------------
    print("\n--- PHASE 2: BASE ROTATION TO DROP LOCATION 2 (100.0°) ---")
    print(f"Rotating Base ({HOME_BASE_ANGLE} -> {TARGET_BASE_ANGLE} deg)...")
    move_to_angle_smooth(base, HOME_BASE_ANGLE, TARGET_BASE_ANGLE, name="Base (GPIO 18)", steps=80, step_delay=0.04)
    sleep(0.8)

    # --------------------------------------
    # 4. LOWER ARM & DROP
    # --------------------------------------
    print("\n--- PHASE 3: LOWER ARM & DROP AT 100.0° ---")
    
    # Extend Arm Down
    print(f"Moving GPIO 24 Down ({MIN_ANGLE_24} -> {MAX_ANGLE_24} deg)...")
    move_to_angle_smooth(servo_24, MIN_ANGLE_24, MAX_ANGLE_24, name="GPIO 24", steps=80, step_delay=0.04)
    sleep(0.3)

    print(f"Moving GPIO 25 Down ({MIN_ANGLE_25} -> {MAX_ANGLE_25} deg)...")
    move_to_angle_smooth(servo_25, MIN_ANGLE_25, MAX_ANGLE_25, name="GPIO 25", steps=80, step_delay=0.04)
    sleep(0.3)

    # Drop (Ungrip)
    print(f"Opening Grip ({CLOSED_GRIP_ANGLE} -> {OPEN_GRIP_ANGLE} deg)...")
    move_to_angle_smooth(grip, CLOSED_GRIP_ANGLE, OPEN_GRIP_ANGLE, name="Gripper", steps=40, step_delay=0.03)
    sleep(0.8)

    # --------------------------------------
    # 5. RETURN HOME
    # --------------------------------------
    print("\n--- PHASE 4: RETURN HOME (57.5°) ---")

    # Retract Arm back up
    print(f"Retracting GPIO 25 ({MAX_ANGLE_25} -> {MIN_ANGLE_25} deg)...")
    move_to_angle_smooth(servo_25, MAX_ANGLE_25, MIN_ANGLE_25, name="GPIO 25", steps=80, step_delay=0.04)
    sleep(0.3)

    print(f"Retracting GPIO 24 ({MAX_ANGLE_24} -> {MIN_ANGLE_24} deg)...")
    move_to_angle_smooth(servo_24, MAX_ANGLE_24, MIN_ANGLE_24, name="GPIO 24", steps=80, step_delay=0.04)
    sleep(0.3)

    # Return base back to home position (57.5°)
    print(f"Returning Base to Home ({TARGET_BASE_ANGLE} -> {HOME_BASE_ANGLE} deg)...")
    move_to_angle_smooth(base, TARGET_BASE_ANGLE, HOME_BASE_ANGLE, name="Base (GPIO 18)", steps=80, step_delay=0.04)
    sleep(0.8)

    print("\nExecution 2 complete successfully!")

except KeyboardInterrupt:
    print("\n\nInterrupted by user...")

finally:
    # Safely detach all servos
    servo_24.detach()
    servo_25.detach()
    grip.detach()
    base.detach()
    print("All servos detached safely.")
