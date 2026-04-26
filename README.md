# Sign Language Learning Platform

An AI-powered platform for learning American Sign Language (ASL) and communicating securely, featuring real-time sign detection, a learning dashboard, and gamified progress tracking.

## Features

-   **Authentication**: Secure User/Admin Login & Registration.
-   **User Dashboard**: Central hub to access Chat and Learning modules.
-   **Admin Dashboard**: Interface for admins to upload learning materials (Video/PDF).
-   **Learning Platform**:
    -   View uploaded modules.
    -   Track progress and earn XP.
    -   Gamified experience with status badges and points.
-   **Secure Chat**:
    -   Real-time sign language detection using MediaPipe.
    -   Secure room-based communication using connection codes.
    -   Video chat with sign-to-text translation.

## Tech Stack

-   **Backend**: Flask, Flask-SocketIO, SQLAlchemy, SQLite
-   **Frontend**: HTML5, CSS3 (Glassmorphism), JavaScript
-   **AI/ML**: MediaPipe (Google), OpenCV, TensorFlow
-   **Database**: SQLite

## Setup Instructions

1.  **Clone/Download** the repository.
2.  **Create a Virtual Environment**:
    ```bash
    python -m venv venv
    .\venv\Scripts\Activate
    ```
3.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run the Application**:
    ```bash
    cd backend
    python app.py
    ```
5.  **Access the App**:
    Open your browser to `http://localhost:5000`.

## Admin Access

On the first run, a default admin account is created:
-   **Username**: `admin`
-   **Password**: `admin`

Use this account to access the Admin Dashboard and upload learning materials.

## Usage

1.  **Register** a new user account.
2.  **Chat Mode**:
    -   Click "Chat Mode" on the dashboard.
    -   Allow camera access.
    -   Share your "Connection Code" with a partner or enter theirs to connect.
3.  **Learning Mode**:
    -   Click "Learning Platform".
    -   Select a module to watch/read.
    -   Complete it to earn XP!
