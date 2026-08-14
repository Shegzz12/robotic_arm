# -*- coding: utf-8 -*-
from gpiozero import AngularServo
from gpiozero.pins.pigpio import PiGPIOFactory
from time import sleep

factory = PiGPIOFactory()
PULSE_MIN = 0.5 / 1000
PULSE_MAX = 2.5 / 1000

base = AngularServo(22, pin_factory=factory, min_angle=0, max_angle=180, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
shoulder = AngularServo(27, pin_factory=factory, min_angle=0, max_angle=180, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
pitch = AngularServo(18, pin_factory=factory, min_angle=0, max_angle=180, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)
grip = AngularServo(23, pin_factory=factory, min_pulse_width=PULSE_MIN, max_pulse_width=PULSE_MAX)

current_angles = {'base': 90, 'shoulder': 90, 'pitch': 0, 'grip': 0}

def move_angle(servo_obj, key, target_angle, steps=30, delay=0.02):
    start_angle = current_angles[key]
    if abs(start_angle - target_angle) < 0.5: return
    step_size = (target_angle - start_angle) / steps
    curr = start_angle
    for _ in range(steps):
        curr += step_size
        servo_obj.angle = curr
        sleep(delay)
    servo_obj.angle = target_angle
    current_angles[key] = target_angle

print('=== STARTING CALIBRATED SEQUENCE (2s PAUSE PER STEP) ===')
try:
    print('1. Initializing Home Position: Pitch 0, Shoulder 90, Base 90...')
    move_angle(pitch, 'pitch', 0, steps=15)
    sleep(2.0)
    move_angle(shoulder, 'shoulder', 90, steps=20)
    sleep(2.0)
    move_angle(base, 'base', 90, steps=20)
    sleep(2.0)
    move_angle(grip, 'grip', 0, steps=10)
    print('--> Home posture set. Pausing 2s...')
    sleep(2.0)

    print('2. Opening Grip (60 degrees)...')
    move_angle(grip, 'grip', 60)
    sleep(2.0)

    print('3. Lowering Shoulder down (45 degrees)...')
    move_angle(shoulder, 'shoulder', 45)
    sleep(2.0)

    print('4. Closing Grip to grab object (0 degrees)...')
    move_angle(grip, 'grip', 0)
    sleep(2.0)

    print('5. Lifting Shoulder back up (90 degrees)...')
    move_angle(shoulder, 'shoulder', 90)
    sleep(2.0)

    print('6. Rotating Base to the LEFT (150 degrees)...')
    move_angle(base, 'base', 150)
    sleep(2.0)

    print('7. Lowering Shoulder to drop height (45 degrees)...')
    move_angle(shoulder, 'shoulder', 45)
    sleep(2.0)

    print('8. Opening Grip to release object (60 degrees)...')
    move_angle(grip, 'grip', 60)
    sleep(2.0)

    print('9. Lifting Shoulder back up (90 degrees)...')
    move_angle(shoulder, 'shoulder', 90)
    sleep(2.0)

    print('10. Closing Grip (0 degrees)...')
    move_angle(grip, 'grip', 0)
    sleep(2.0)

    print('11. Rotating Base back to CENTER (90 degrees)...')
    move_angle(base, 'base', 90)
    sleep(2.0)

    print('Sequence Completed Successfully!')

except KeyboardInterrupt:
    pass
finally:
    grip.detach()
    pitch.detach()
    shoulder.detach()
    base.detach()
