 # robot-arm-joystick-with-smoothing.py
import time, board, analogio, digitalio, pwmio
from adafruit_motor import servo

EASING_STEP = 1 # Make smaller (1) for slower, smoother motion
ANGLE_THRESHOLD = 3 # Raise to ignore more minor joystick wiggles
LOOP_DELAY = 0.02 # Lower for quicker updates, higher for more chill motion

# Setup Buttons
claw_open = digitalio.DigitalInOut(board.GP16)
claw_open.switch_to_input(pull=digitalio.Pull.UP)

claw_closed = digitalio.DigitalInOut(board.GP17)
claw_closed.switch_to_input(pull=digitalio.Pull.UP)

base_right = digitalio.DigitalInOut(board.GP18)
base_right.switch_to_input(pull=digitalio.Pull.UP)

base_left = digitalio.DigitalInOut(board.GP19)
base_left.switch_to_input(pull=digitalio.Pull.UP)

# Setup servos
pwm = pwmio.PWMOut(board.GP14, frequency=50) # orange
x_servo = servo.Servo(pwm, min_pulse=500, max_pulse=2500)

pwm2 = pwmio.PWMOut(board.GP15, frequency=50) # blue
y_servo = servo.Servo(pwm2, min_pulse=500, max_pulse=2500) 

pwm3 = pwmio.PWMOut(board.GP13, frequency=50) # yellow
claw_servo = servo.Servo(pwm3, min_pulse=250, max_pulse=2300)

pwm4 = pwmio.PWMOut(board.GP12, frequency=50) # white
base_servo = servo.Servo(pwm4, min_pulse=500, max_pulse=2500)

x_servo.angle = 90
y_servo.angle = 90
base_servo.angle = 0
claw_servo.angle = 90

# Setup analog inputs
x_axis = analogio.AnalogIn(board.A0)  # GP26
y_axis = analogio.AnalogIn(board.A1)  # GP27

# Setup digital input for joystick button
button = digitalio.DigitalInOut(board.GP22)
button.switch_to_input(pull=digitalio.Pull.UP)

# --- Smoothing parameters ---
NUM_SAMPLES = 5
x_samples = [0] * NUM_SAMPLES
y_samples = [0] * NUM_SAMPLES

# Servo state tracking
current_x_angle = 90
current_y_angle = 90
target_x_angle = 90
target_y_angle = 90

def read_smoothed(samples, new_val): 
    samples.pop(0)
    samples.append(new_val)
    return sum(samples) / len(samples)

def map_to_angle(raw):
    angle = (raw / 65535) * 180
    return max(0, min(180, angle))

def ease_toward(current, target, step):
    if abs(target - current) < step:
        return target
    return current + step if target > current else current - step

print("Joystick Smoothed Servo Control with Easing Running!")

while True:
    # Read joystick axes
    x_raw = x_axis.value
    y_raw = y_axis.value

    smoothed_x = read_smoothed(x_samples, x_raw)
    smoothed_y = read_smoothed(y_samples, y_raw)

    new_target_x = map_to_angle(smoothed_x)
    new_target_y = map_to_angle(smoothed_y)

    # Update target angles only if the change is meaningful
    if abs(new_target_x - target_x_angle) > ANGLE_THRESHOLD:
        if target_x_angle < new_target_x:
            print("UP")
        else:
            print("DOWN")
        target_x_angle = new_target_x
    if abs(new_target_y - target_y_angle) > ANGLE_THRESHOLD:
        if target_y_angle < new_target_y:
            print("RIGHT")
        else:
            print("LEFT")
        target_y_angle = new_target_y

    # Ease current angles toward targets
    current_x_angle = ease_toward(current_x_angle, target_x_angle, EASING_STEP)
    current_y_angle = ease_toward(current_y_angle, target_y_angle, EASING_STEP)

    # Set servo angles
    x_servo.angle = current_x_angle
    y_servo.angle = current_y_angle

    ANGLE_STEP = 3 
    if not base_right.value:
        print("base right")
        base_servo.angle = int(max(0, base_servo.angle - ANGLE_STEP))
        print(f"RIGHT: base_servo.angle: {base_servo.angle}")
    if not base_left.value:
        print("base left")
        base_servo.angle = int(min(180, base_servo.angle + ANGLE_STEP))
        print(f"base_servo.angle: {base_servo.angle}")
    if not claw_open.value:
        print("claw open")
        claw_servo.angle = int(min(100, claw_servo.angle + ANGLE_STEP))
        print(f"CLAW LEFT: claw_servo.angle: {claw_servo.angle}")
    if not claw_closed.value:
        print("claw closed")
        claw_servo.angle = int(max(0, claw_servo.angle - ANGLE_STEP))
        print(f"CLAW RIGHT: claw_servo.angle: {claw_servo.angle}")

    time.sleep(LOOP_DELAY)  # Fast update loop for smooth easing
