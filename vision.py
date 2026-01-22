import cv2
import mediapipe as mp
import time
import numpy as np

# --- CONFIGURATION ---
# Sensitivity: Lower = Easier to count, Higher = Harder hits only
PUNCH_THRESHOLD = 0.6 
RESET_THRESHOLD = 0.4

class AIEye:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(min_detection_confidence=0.7, min_tracking_confidence=0.7)
        self.mp_draw = mp.solutions.drawing_utils
        
        # State Tracking
        self.left_stage = "retracted"
        self.right_stage = "retracted"
        self.punch_count = 0
        self.last_count_time = 0

    def calculate_angle(self, a, b, c):
        """Calculates angle of elbow to determine extension"""
        a = np.array(a) # Shoulder
        b = np.array(b) # Elbow
        c = np.array(c) # Wrist
        
        radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
        angle = np.abs(radians*180.0/np.pi)
        
        if angle > 180.0:
            angle = 360-angle
            
        return angle

    def process_frame(self, frame):
        # 1. Convert to RGB for MediaPipe
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(img_rgb)
        
        # 2. Draw Skeleton
        if results.pose_landmarks:
            self.mp_draw.draw_landmarks(frame, results.pose_landmarks, self.mp_pose.POSE_CONNECTIONS)
            
            landmarks = results.pose_landmarks.landmark
            
            # --- EXTRACT COORDINATES ---
            # Left Arm
            l_shoulder = [landmarks[11].x, landmarks[11].y]
            l_elbow = [landmarks[13].x, landmarks[13].y]
            l_wrist = [landmarks[15].x, landmarks[15].y]
            
            # Right Arm
            r_shoulder = [landmarks[12].x, landmarks[12].y]
            r_elbow = [landmarks[14].x, landmarks[14].y]
            r_wrist = [landmarks[16].x, landmarks[16].y]
            
            # --- LOGIC: ELBOW EXTENSION ---
            # We use angle to detect a punch extension (close to 160-180 degrees)
            left_angle = self.calculate_angle(l_shoulder, l_elbow, l_wrist)
            right_angle = self.calculate_angle(r_shoulder, r_elbow, r_wrist)
            
            # LEFT HAND LOGIC
            if left_angle > 160 and self.left_stage == "retracted":
                self.left_stage = "extended"
                self.punch_count += 1
                self.last_count_time = time.time()
            if left_angle < 70:
                self.left_stage = "retracted"

            # RIGHT HAND LOGIC
            if right_angle > 160 and self.right_stage == "retracted":
                self.right_stage = "extended"
                self.punch_count += 1
                self.last_count_time = time.time()
            if right_angle < 70:
                self.right_stage = "retracted"

            # --- VISUAL FEEDBACK ---
            # Display Count
            cv2.rectangle(frame, (0,0), (250, 80), (245, 117, 16), -1)
            cv2.putText(frame, 'PUNCHES', (15,12), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,0), 1, cv2.LINE_AA)
            cv2.putText(frame, str(self.punch_count), (10,70), cv2.FONT_HERSHEY_SIMPLEX, 2, (255,255,255), 2, cv2.LINE_AA)

            # Form Check (Hands Drop Warning)
            # If wrist is below shoulder (y value increases as you go down screen)
            if l_wrist[1] > l_shoulder[1] + 0.1 or r_wrist[1] > r_shoulder[1] + 0.1:
                cv2.putText(frame, "HANDS UP!", (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 4)

        return frame

# --- RUNNER ---
def start_camera():
    cap = cv2.VideoCapture(0) # 0 is usually the default webcam
    eye = AIEye()
    
    print("🥊 Ghost Eye Active. Press 'q' to quit.")
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret: break
        
        # Mirror image for easier shadowboxing
        frame = cv2.flip(frame, 1)
        
        # Process
        frame = eye.process_frame(frame)
        
        # Show Result
        cv2.imshow('CornerMan AI Vision Test', frame)
        
        if cv2.waitKey(10) & 0xFF == ord('q'):
            break
            
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    start_camera()