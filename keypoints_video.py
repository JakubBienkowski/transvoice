import cv2
import mediapipe as mp
import numpy as np

# Initialize MediaPipe Holistic
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils

# Video file path
video_path = 'K63AF12-26_753.mp4'  # Replace with your video file path

# Initialize video capture
cap = cv2.VideoCapture(video_path)

# Get video properties
frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = int(cap.get(cv2.CAP_PROP_FPS))

# Initialize video writer
fourcc = cv2.VideoWriter_fourcc(*'mp4v')
out = cv2.VideoWriter('output_video_with_zoom.mp4', fourcc, fps, (frame_width, frame_height))

def get_hand_bbox(hand_landmarks, image_shape):
    if hand_landmarks:
        x_coordinates = [landmark.x for landmark in hand_landmarks.landmark]
        y_coordinates = [landmark.y for landmark in hand_landmarks.landmark]
        x_min, x_max = min(x_coordinates), max(x_coordinates)
        y_min, y_max = min(y_coordinates), max(y_coordinates)
        
        # Add padding
        padding = 0.3
        width = x_max - x_min
        height = y_max - y_min
        x_min = max(0, x_min - width * padding)
        x_max = min(1, x_max + width * padding)
        y_min = max(0, y_min - height * padding)
        y_max = min(1, y_max + height * padding)
        
        bbox = np.array([x_min, y_min, x_max, y_max]) * np.array([image_shape[1], image_shape[0], image_shape[1], image_shape[0]])
        return bbox.astype(int)
    return None

def zoom_hand(image, bbox, zoom_factor=2):
    x_min, y_min, x_max, y_max = bbox
    hand_img = image[y_min:y_max, x_min:x_max]
    zoomed_hand = cv2.resize(hand_img, None, fx=zoom_factor, fy=zoom_factor)
    return zoomed_hand

# Initialize holistic model
with mp_holistic.Holistic(min_detection_confidence=0.5, min_tracking_confidence=0.5) as holistic:
    paused = False
    while cap.isOpened():
        if not paused:
            ret, frame = cap.read()
            if not ret:
                print("End of video file")
                break
            
            # Recolor feed
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Make detections
            results = holistic.process(image)
            
            # Recolor image back to BGR for rendering
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # Draw face landmarks
            mp_drawing.draw_landmarks(image, results.face_landmarks, mp_holistic.FACEMESH_CONTOURS)
            
            # Draw pose landmarks
            mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_holistic.POSE_CONNECTIONS)
            
            # Process left hand
            left_hand_bbox = get_hand_bbox(results.left_hand_landmarks, image.shape)
            if left_hand_bbox is not None:
                mp_drawing.draw_landmarks(image, results.left_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                zoomed_left_hand = zoom_hand(image, left_hand_bbox)
                image[0:zoomed_left_hand.shape[0], 0:zoomed_left_hand.shape[1]] = zoomed_left_hand
            
            # Process right hand
            right_hand_bbox = get_hand_bbox(results.right_hand_landmarks, image.shape)
            if right_hand_bbox is not None:
                mp_drawing.draw_landmarks(image, results.right_hand_landmarks, mp_holistic.HAND_CONNECTIONS)
                zoomed_right_hand = zoom_hand(image, right_hand_bbox)
                image[0:zoomed_right_hand.shape[0], -zoomed_right_hand.shape[1]:] = zoomed_right_hand
            
            # Write the frame to the output video
            out.write(image)
        
        # Show image
        cv2.imshow('Holistic Model Detections with Hand Zoom', image)
        
        key = cv2.waitKey(1)
        if key & 0xFF == ord('q'):
            break
        elif key & 0xFF == ord(' '):
            paused = not paused

cap.release()
out.release()
cv2.destroyAllWindows()
