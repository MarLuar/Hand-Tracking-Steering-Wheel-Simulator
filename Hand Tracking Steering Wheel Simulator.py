import cv2
import mediapipe as mp
import math
import pyautogui
import time

# Initialize MediaPipe with optimized settings
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0
)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

# Camera setup
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
cap.set(cv2.CAP_PROP_FPS, 30)

# Track which keys are held
keys_pressed = {'a': False, 'd': False, 'w': False, 's': False}

# Steering parameters
DEAD_ZONE_ANGLE = 20
MAX_ANGLE = 60
current_steering = 0
STEERING_SMOOTHING = 0
RECOVERY_FACTOR = 0  # How aggressively to recover (0-1)
RECOVERY_DURATION = 0  # How long to apply recovery (seconds)

# Recovery tracking
last_steering_direction = 0  # -1 for left, 1 for right, 0 for neutral
recovery_start_time = 0
in_recovery = False

def key_down(key):
    if not keys_pressed[key]:
        pyautogui.keyDown(key)
        keys_pressed[key] = True

def key_up(key):
    if keys_pressed[key]:
        pyautogui.keyUp(key)
        keys_pressed[key] = False

def release_all():
    for key in keys_pressed:
        key_up(key)

def is_thumb_up(hand, handedness):
    tip = hand.landmark[4]
    mcp = hand.landmark[2]
    if handedness == 'Left':
        return tip.x > mcp.x + 0.03
    else:
        return tip.x < mcp.x - 0.03

# For FPS calculation
prev_time = 0
fps = 0

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Calculate FPS
    curr_time = time.time()
    fps = 1 / (curr_time - prev_time)
    prev_time = curr_time

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb_frame)
    h, w = frame.shape[:2]

    steering_action = "WAITING FOR BOTH HANDS"
    throttle_action = "IDLE"
    angle_deg = 0

    left_hand = None
    right_hand = None

    if result.multi_hand_landmarks:
        for lm, handedness in zip(result.multi_hand_landmarks, result.multi_handedness):
            label = handedness.classification[0].label
            if label == 'Left':
                left_hand = lm
            elif label == 'Right':
                right_hand = lm

    if left_hand and right_hand:
        lw = left_hand.landmark[0]
        rw = right_hand.landmark[0]
        lx, ly = int(lw.x * w), int(lw.y * h)
        rx, ry = int(rw.x * w), int(rw.y * h)

        # Draw landmarks
        mp_drawing.draw_landmarks(
            frame, left_hand, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        mp_drawing.draw_landmarks(
            frame, right_hand, mp_hands.HAND_CONNECTIONS,
            mp_drawing_styles.get_default_hand_landmarks_style(),
            mp_drawing_styles.get_default_hand_connections_style())
        cv2.line(frame, (lx, ly), (rx, ry), (255, 0, 0), 2)

        # Calculate angle
        dx = rx - lx
        dy = ry - ly
        angle_rad = math.atan2(dy, dx)
        angle_deg = math.degrees(angle_rad)

        # Determine current steering direction
        current_direction = 0
        if angle_deg > DEAD_ZONE_ANGLE:
            current_direction = 1  # Right
        elif angle_deg < -DEAD_ZONE_ANGLE:
            current_direction = -1  # Left

        # Check if we need to start recovery
        if (last_steering_direction == 1 and current_direction == -1) or \
           (last_steering_direction == -1 and current_direction == 1):
            # Direction changed - start recovery
            in_recovery = True
            recovery_start_time = curr_time
            recovery_direction = -last_steering_direction

        # Update last direction
        if current_direction != 0:
            last_steering_direction = current_direction

        # Handle recovery
        if in_recovery:
            if curr_time - recovery_start_time < RECOVERY_DURATION:
                # Apply recovery steering
                recovery_strength = RECOVERY_FACTOR * (1 - (curr_time - recovery_start_time) / RECOVERY_DURATION)
                if recovery_direction > 0:
                    steering_action = f"RECOVERY RIGHT ({int(recovery_strength*100)}%)"
                    key_down('d')
                    key_up('a')
                    current_steering = recovery_strength
                else:
                    steering_action = f"RECOVERY LEFT ({int(recovery_strength*100)}%)"
                    key_down('a')
                    key_up('d')
                    current_steering = -recovery_strength
                continue  # Skip normal steering during recovery
            else:
                in_recovery = False

        # Normal steering
        if abs(angle_deg) > DEAD_ZONE_ANGLE:
            normalized_angle = min(abs(angle_deg), MAX_ANGLE) / MAX_ANGLE
            direction = 1 if angle_deg > 0 else -1
            target_steering = direction * normalized_angle
            current_steering = (1 - STEERING_SMOOTHING) * target_steering + STEERING_SMOOTHING * current_steering
            
            if current_steering > 0:
                steering_action = f"RIGHT ({int(current_steering*100)}%)"
                key_down('d')
                key_up('a')
            else:
                steering_action = f"LEFT ({int(-current_steering*100)}%)"
                key_down('a')
                key_up('d')
        else:
            steering_action = "STRAIGHT"
            current_steering = 0
            key_up('a')
            key_up('d')

        # Throttle & brake
        left_thumb_open = is_thumb_up(left_hand, 'Left')
        right_thumb_open = is_thumb_up(right_hand, 'Right')

        if left_thumb_open:
            throttle_action = "ACCELERATE"
            key_down('w')
            key_up('s')
        elif right_thumb_open:
            throttle_action = "BRAKE"
            key_down('s')
            key_up('w')
        else:
            throttle_action = "IDLE"
            key_up('w')
            key_up('s')

    else:
        release_all()
        if result.multi_hand_landmarks:
            for lm in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, lm, mp_hands.HAND_CONNECTIONS)

    # Display info
    cv2.putText(frame, f"FPS: {int(fps)}", (w-150, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    cv2.putText(frame, f"Angle: {int(angle_deg)}°", (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,255), 2)
    cv2.putText(frame, f"Steer: {steering_action}", (30, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255,255,0), 2)
    cv2.putText(frame, f"Throttle: {throttle_action}", (30, 130),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255,0), 2)
    if in_recovery:
        cv2.putText(frame, "RECOVERY MODE", (w//2 - 100, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255), 2)

    cv2.imshow("Steering Wheel", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

release_all()
cap.release()
cv2.destroyAllWindows()
hands.close()