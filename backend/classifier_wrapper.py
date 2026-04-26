import os
import sys

# Add the parent directory to sys.path to allow imports from core
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.model.keypoint_classifier.keypoint_classifier import KeyPointClassifier
# from core.model.keypoint_classifier.keypoint_classifier_label import read_labels # Removed: It is a CSV file.


# Adjust the model path to be absolute or relative to this wrapper
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'model', 'keypoint_classifier', 'keypoint_classifier.tflite')
LABEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'core', 'model', 'keypoint_classifier', 'keypoint_classifier_label.csv')

class ASLdpPredictor:
    def __init__(self):
        self.classifier = KeyPointClassifier(model_path=MODEL_PATH)
        self.labels = self._load_labels()
        
        # Initialize MediaPipe Hands (Python)
        import mediapipe as mp
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            static_image_mode=True, # Use static mode for independent frame processing or False for stream (keep state)
            max_num_hands=1,
            min_detection_confidence=0.7,
            min_tracking_confidence=0.5,
        )

    def _load_labels(self):
        import csv
        with open(LABEL_PATH, encoding='utf-8-sig') as f:
            keypoint_classifier_labels = csv.reader(f)
            return [row[0] for row in keypoint_classifier_labels]

    def predict_image(self, image):
        """
        Process a CV2 image (BGR), extract landmarks, and predict sign.
        """
        import cv2
        import copy
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Process
        results = self.hands.process(image_rgb)
        
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Calc Bounding Rect (optional, skip for now)
                
                # Calc Landmark List (Convert normalized to pixel)
                # Note: calc_landmark_list in app.py does exactly what _scale_to_pixel did but returns list not array of arrays.
                # Let's reuse the logic we just wrote but adapted.
                
                width = image.shape[1]
                height = image.shape[0]
                
                landmark_list = []
                for _, landmark in enumerate(hand_landmarks.landmark):
                    landmark_x = min(int(landmark.x * width), width - 1)
                    landmark_y = min(int(landmark.y * height), height - 1)
                    landmark_list.append([landmark_x, landmark_y])
                
                # Pre-process
                processed_landmarks = self.pre_process_landmark(landmark_list)
                
                # Classify
                sign_id = self.classifier(processed_landmarks)
                return self.labels[sign_id]
        
        return ""

    def predict(self, landmark_list):
        """
        Args:
            landmark_list: List of 42 floats (21 points * x, y).
                           The original app expects PRE-PROCESSED (normalized/relative) landmarks.
                           
        We need to ensure the frontend sends PRE-PROCESSED landmarks OR we process them here.
        The original app did preprocessing in Python (pre_process_landmark).
        
        Strategy: Frontend sends RAW landmarks. Backend (this wrapper) processes them to match training data.
        """
        # Validate input
        if not landmark_list:
            return ""

        # Scaling: Model was trained on pixel coordinates (960x540 default in app.py)
        # Input landmark_list is normalized [0,1]. We must scale it.
        pixel_landmarks = self._scale_to_pixel(landmark_list)
        
        processed_landmarks = self.pre_process_landmark(pixel_landmarks)
        sign_id = self.classifier(processed_landmarks)
        return self.labels[sign_id]

    def _scale_to_pixel(self, landmark_list, width=960, height=540):
        """
        Scales normalized [0-1] landmarks to pixel coordinates.
        """
        return [[int(pt[0] * width), int(pt[1] * height)] for pt in landmark_list]


    def pre_process_landmark(self, landmark_list):
        """
        Converts raw landmarks to relative and normalized coordinates.
        Input: List of [x, y] coordinates (21 points).
        """
        import copy
        import itertools

        temp_landmark_list = copy.deepcopy(landmark_list)

        # Convert to relative coordinates
        base_x, base_y = 0, 0
        for index, landmark_point in enumerate(temp_landmark_list):
            if index == 0:
                base_x, base_y = landmark_point[0], landmark_point[1]

            temp_landmark_list[index][0] = temp_landmark_list[index][0] - base_x
            temp_landmark_list[index][1] = temp_landmark_list[index][1] - base_y

        # Convert to a one-dimensional list
        temp_landmark_list = list(itertools.chain.from_iterable(temp_landmark_list))

        # Normalization
        max_value = max(list(map(abs, temp_landmark_list)))

        def normalize_(n):
            return n / max_value if max_value != 0 else 0

        temp_landmark_list = list(map(normalize_, temp_landmark_list))

        return temp_landmark_list
