# Encrypted Cloud Communication for Sign Language Learning Using Deep Learning and Edge AI

An AI-powered real-time sign language learning and communication platform that combines Deep Learning, Computer Vision, Edge AI, and Secure Cloud Communication to provide an interactive and inclusive learning experience.

The system enables users to learn and practice sign language through real-time gesture recognition, progress tracking, secure communication, and gamified learning modules.

---

# Project Overview

This project focuses on improving accessibility and communication for deaf and speech-impaired individuals through an intelligent sign language learning platform.

The system captures live video input from the user's webcam, extracts hand landmarks using computer vision techniques, and performs gesture classification using deep learning models. The platform provides instant feedback, secure user authentication, learning progress tracking, and real-time communication features.

---

# Key Features

## Authentication & Security
- Secure User Registration and Login
- Password Hashing and Authentication
- Session Management
- Secure Cloud Communication
- Access Control for Users and Admins

## Real-Time Gesture Recognition
- Live webcam-based gesture detection
- Hand landmark extraction using MediaPipe
- Deep Learning-based sign classification
- Real-time prediction with low latency
- Landmark-based optimized inference pipeline

## Learning Platform
- Structured sign language learning modules
- Learning materials management
- Progress tracking system
- XP and gamified learning experience
- Completion percentage monitoring

## Admin Dashboard
- Upload learning materials
- Add YouTube learning resources
- Manage educational content
- Track platform materials

## Real-Time Communication
- SocketIO-based communication
- Room-based secure chat
- Unique connection codes
- Real-time message transmission

## Edge AI Processing
- Lightweight preprocessing pipeline
- Noise reduction and normalization
- Low latency inference
- Efficient frame processing

---

# System Architecture

The system follows a client-server architecture integrated with Edge AI and secure cloud communication.

## Workflow

1. Live video is captured from the user's webcam.
2. Frames are preprocessed using resizing, normalization, and noise reduction.
3. Hand landmarks are extracted using MediaPipe/OpenCV.
4. Deep Learning models classify gestures in real-time.
5. Predicted gestures are displayed instantly to users.
6. Feedback and learning support are provided dynamically.
7. User progress and learning history are securely stored.

---

# System Architecture Diagram

![System Architecture](./screenshots/system_architecture.png)

---

# Technology Stack

## Backend
- Python
- Flask
- Flask-SocketIO
- SQLAlchemy
- Flask-Login

## Frontend
- HTML5
- CSS3
- JavaScript

## AI / Machine Learning
- TensorFlow
- OpenCV
- MediaPipe

## Database
- SQLite

## Development Tools
- VS Code
- GitHub

---

# Folder Structure

```bash
project/
│
├── backend/
│   ├── app.py
│   ├── models.py
│   ├── classifier_wrapper.py
│   ├── uploads/
│
├── frontend/
│   ├── templates/
│   ├── static/
│
├── utils/
│
├── requirements.txt
├── README.md
```

---

# Installation & Setup

## 1. Clone the Repository

```bash
git clone https://github.com/1Yash8/SIGN-LANGUAGE-LEARNING-USING-DEEP-LEARNING-AND-EDGE-AI.git
```

---

## 2. Navigate to the Project Directory

```bash
cd SIGN-LANGUAGE-LEARNING-USING-DEEP-LEARNING-AND-EDGE-AI
```

---

## 3. Create Virtual Environment

```bash
python -m venv venv
```

### Activate Virtual Environment

#### Windows
```bash
venv\Scripts\activate
```

#### Linux / Mac
```bash
source venv/bin/activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 5. Run the Application

```bash
python app.py
```

---

## 6. Open in Browser

```text
http://127.0.0.1:5000
```

---

# Default Admin Access

On the first run, the system automatically creates a default admin account.

## Admin Credentials

```text
Username: *****
Password: *****
```

Use this account to:
- Access Admin Dashboard
- Upload Learning Materials
- Manage Educational Content

---

# Usage Guide

## User Workflow

### Step 1: Register/Login
- Create a new account or login securely.

### Step 2: Access Dashboard
- View learning progress and XP.

### Step 3: Learning Platform
- Open learning modules.
- Watch videos or study uploaded materials.
- Complete modules to gain XP.

### Step 4: Practice Mode
- Enable webcam access.
- Perform sign gestures.
- Receive real-time predictions and feedback.

### Step 5: Chat Mode
- Generate unique connection code.
- Join secure communication rooms.
- Exchange messages in real time.

---

# Real-Time Gesture Recognition Pipeline

## Input Acquisition
- Webcam captures live frames.

## Preprocessing
- Resize
- Normalize
- Noise Reduction
- Background Optimization

## Feature Extraction
- Hand landmark detection using MediaPipe.

## Model Inference
- Deep Learning model predicts sign labels.

## Output Generation
- Predicted sign displayed instantly.

## Feedback Support
- Learning assistance and performance tracking.

---

# Security Features

- Password Hashing
- Secure Authentication
- Session Management
- Controlled Access
- Secure Data Handling
- Encrypted Communication Architecture

---

# Performance Highlights

- Real-Time Gesture Recognition
- Low Latency Prediction
- Optimized Landmark Processing
- Modular Scalable Architecture
- Interactive User Experience

---

# Screenshots

## Login Page
(Add Screenshot Here)

---

## User Dashboard
(Add Screenshot Here)

---

## Learning Platform
(Add Screenshot Here)

---

## Real-Time Gesture Recognition
(Add Screenshot Here)

---

## Admin Dashboard
(Add Screenshot Here)

---

# Future Enhancements

- Multi-language Sign Support
- Continuous Sign Recognition
- Voice-to-Sign Conversion
- Facial Expression Recognition
- Cloud Deployment
- Mobile Application Integration

---

# Research & Academic Context

This project was developed as part of the Bachelor of Technology degree requirements in Computer Science and Engineering.

Project Title:
**Encrypted Cloud Communication for Sign Language Learning Using Deep Learning and Edge AI**

Institution:
**SRM Institute of Science and Technology**

---

# Contributors

- Yeswanth Kumar
- Ravindra Kumar

---

# License

This project is developed for academic and educational purposes.

Repository Link:

```text
https://github.com/1Yash8/SIGN-LANGUAGE-LEARNING-USING-DEEP-LEARNING-AND-EDGE-AI
```

---
