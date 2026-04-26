from flask import Flask, request, jsonify, send_from_directory, render_template, flash, redirect, url_for


from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from dotenv import load_dotenv
import os
import random
import string

# Import Wrapper
from classifier_wrapper import ASLdpPredictor
from models import db, User, Material, UserProgress
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import re



# Initialize App
# Point explicit paths to frontend folder
template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'templates'))
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend', 'static'))
upload_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'uploads'))

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
app.config['SECRET_KEY'] = 'secret!'
app.config['UPLOAD_FOLDER'] = upload_dir

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

with app.app_context():
    db.create_all()
    
    # Create Admin if not exists
    if not User.query.filter_by(username='admin').first():
        admin = User(
            username='admin',
            password_hash=generate_password_hash('admin', method='scrypt'),
            is_admin=True
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created (admin/admin)")



# Load Predictor
predictor = ASLdpPredictor()

def extract_video_id(url):
    """
    Examples:
    - http://youtu.be/SA2iWivDJiE
    - http://www.youtube.com/watch?v=_oPAwA_Udwc&feature=feedu
    - http://www.youtube.com/embed/SA2iWivDJiE
    - http://www.youtube.com/v/SA2iWivDJiE?version=3&amp;hl=en_US
    """
    query = urlparse(url)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    # fail?
    return None

from urllib.parse import urlparse, parse_qs


# In-memory storage for MVP (Use DB for production)
users = {}


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        flash('Invalid username or password')
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
        else:
            new_user = User(
                username=username, 
                password_hash=generate_password_hash(password, method='scrypt')
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            return redirect(url_for('dashboard'))
            
    return render_template('signup.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Get user progress data
    user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    total_materials = Material.query.count()
    completed_count = sum(1 for p in user_progress if p.is_completed)
    
    # Calculate completion percentage
    completion_percentage = (completed_count / total_materials * 100) if total_materials > 0 else 0
    
    # Get recent completed materials
    recent_completed = db.session.query(Material, UserProgress)\
        .join(UserProgress, Material.id == UserProgress.material_id)\
        .filter(UserProgress.user_id == current_user.id, UserProgress.is_completed == True)\
        .order_by(UserProgress.id.desc())\
        .limit(3)\
        .all()
    
    # Calculate user level based on XP
    level = (current_user.points // 50) + 1
    xp_for_next_level = (level * 50) - current_user.points
    
    return render_template('dashboard.html',
                         total_materials=total_materials,
                         completed_count=completed_count,
                         completion_percentage=completion_percentage,
                         recent_completed=recent_completed,
                         level=level,
                         xp_for_next_level=xp_for_next_level)

@app.route('/practice')
@login_required
def practice():
    return render_template('practice.html')

@app.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
    materials = Material.query.all()
    return render_template('admin.html', materials=materials)

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')


@app.route('/upload_material', methods=['POST'])
@login_required
def upload_material():
    if not current_user.is_admin:
        return redirect(url_for('dashboard'))
        
    title = request.form.get('title')
    m_type = request.form.get('type')
    
    if m_type == 'youtube':
        youtube_url = request.form.get('youtube_url')
        if youtube_url:
            # Save the URL in the filename column (repurposing it)
            new_material = Material(title=title, type=m_type, filename=youtube_url)
            db.session.add(new_material)
            db.session.commit()
            flash('YouTube video added successfully!')
        else:
            flash('Please provide a YouTube URL.')
            
    else:
        file = request.files.get('file')
        
        if file and title and m_type: # Changed 'type' to 'm_type' to match variable name
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            
            new_material = Material(
                title=title,
                type=m_type,
                filename=filename
            )
            db.session.add(new_material)
            db.session.commit()
            
            # Create progress entries for all users
            users = User.query.all()
            for user in users:
                progress = UserProgress(user_id=user.id, material_id=new_material.id)
                db.session.add(progress)
            db.session.commit()
            
            flash('Material uploaded successfully')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('No file selected or missing title/type.') # Added more specific flash message
        
    return redirect(url_for('admin_dashboard')) # Kept original redirect for consistency

@app.route('/admin/delete_material/<int:id>', methods=['POST'])
@login_required
def delete_material(id):
    if not current_user.is_admin: # Changed from current_user.username != 'admin' to current_user.is_admin
        flash('Unauthorized access')
        return redirect(url_for('dashboard'))
        
    material = Material.query.get_or_404(id)
    
    # Delete file from filesystem if it's a file upload (not YouTube)
    if material.type != 'youtube':
        try:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], material.filename) # Changed content_url to filename
            if os.path.exists(filepath):
                os.remove(filepath)
        except Exception as e:
            print(f"Error deleting file: {e}")
        
    # Delete from database
    # Note: UserProgress entries will be deleted automatically if cascade is set up,
    # otherwise we should delete them manually. Let's do it manually to be safe.
    UserProgress.query.filter_by(material_id=id).delete()
    db.session.delete(material)
    db.session.commit()
    
    flash('Material deleted successfully')
    return redirect(url_for('admin_dashboard'))

@app.route('/learning_platform')
@login_required
def learning_platform():
    materials = Material.query.all()
    user_progress = UserProgress.query.filter_by(user_id=current_user.id).all()
    
    # Map progress
    progress_map = {p.material_id: p for p in user_progress}
    completed_count = sum(1 for p in user_progress if p.is_completed)
    total_count = len(materials)
    
    return render_template('learn.html', 
                         materials=materials, 
                         progress_map=progress_map,
                         completed_count=completed_count,
                         total_count=total_count)

@app.route('/view_material/<int:material_id>')
@login_required
def view_material(material_id):
    material = Material.query.get_or_404(material_id)
    progress = UserProgress.query.filter_by(user_id=current_user.id, material_id=material_id).first()
    
    is_completed = False
    if progress and progress.is_completed:
        is_completed = True
        
    youtube_id = None
    if material.type == 'youtube':
        youtube_id = extract_video_id(material.filename)
        
    return render_template('view_material.html', 
                         material=material, 
                         is_completed=is_completed,
                         youtube_id=youtube_id)

@app.route('/complete_material/<int:material_id>', methods=['POST'])
@login_required
def complete_material(material_id):
    progress = UserProgress.query.filter_by(user_id=current_user.id, material_id=material_id).first()
    
    if not progress:
        progress = UserProgress(user_id=current_user.id, material_id=material_id, is_completed=True)
        db.session.add(progress)
        current_user.points += 10
        db.session.commit()
        return jsonify({'success': True, 'message': 'Module Completed! +10 XP', 'new_points': current_user.points})
        
    if not progress.is_completed:
        progress.is_completed = True
        current_user.points += 10
        db.session.commit()
        return jsonify({'success': True, 'message': 'Module Completed! +10 XP', 'new_points': current_user.points})
        
    return jsonify({'success': True, 'message': 'Already completed'})


@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)




# --- SocketIO Events ---

@socketio.on('connect')
def handle_connect():
    print('Client connected:', request.sid)

@socketio.on('register')
def handle_register(data):
    """
    User registers. Generates a unique 6-digit code.
    Data: { 'username': 'Tanis' }
    Response: { 'code': '123456' }
    """
    username = data.get('username', 'Anonymous')
    # Generate 6 digit code
    code = ''.join(random.choices(string.digits, k=6))
    
    users[request.sid] = {
        'username': username,
        'code': code,
        'sid': request.sid
    }
    
    # User joins their own room initially (so others can join them)
    join_room(code) 
    
    print(f"User {username} registered with code {code}")
    emit('registration_success', {'code': code, 'username': username})

@socketio.on('join_chat')
def handle_join_chat(data):
    """
    User B wants to join User A's chat.
    Data: { 'target_code': '123456' }
    """
    target_code = data.get('target_code')
    sender_sid = request.sid
    
    # Find target session
    target_user = None
    for sid, user_data in users.items():
        if user_data['code'] == target_code:
            target_user = user_data
            break
            
    if target_user:
        # Join the room 'target_code'
        join_room(target_code)
        
        # Notify both parties
        emit('chat_connected', {'partner': target_user['username']}, to=sender_sid)
        emit('chat_connected', {'partner': users[sender_sid]['username']}, to=target_user['sid'])
        print(f"User {users[sender_sid]['username']} joined chat with {target_user['username']} (Room: {target_code})")
    else:
        emit('error', {'message': 'User not found or code invalid'})

@socketio.on('process_frame')
def handle_process_frame(data):
    """
    Receives base64 image frame. Decodes to CV2. Predicts sign.
    DEPRECATED: Use 'process_landmarks' for better performance.
    """
    image_data = data.get('image')
    if image_data:
        try:
            # Decode Base64
            import base64
            import numpy as np
            import cv2
            
            # Remove header if present
            if ',' in image_data:
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            nparr = np.frombuffer(image_bytes, np.uint8)
            img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if img is not None:
                sign = predictor.predict_image(img)
                emit('prediction_result', {'sign': sign})
                
        except Exception as e:
            print(f"Frame Processing Error: {e}")

@socketio.on('process_landmarks')
def handle_process_landmarks(data):
    """
    Receives normalized landmarks from frontend.
    Data: { 'landmarks': [[x, y], [x, y], ...] } or flat list depending on wrapper support.
    The frontend sends normalized [0, 1] coordinates.
    """
    landmarks = data.get('landmarks')
    if landmarks:
        try:
            # The wrapper's predict method expects a list of points or appropriate format.
            # Looking at classifier_wrapper.py: predict(self, landmark_list) calls _scale_to_pixel
            # landmark_list in wrapper seems to expect a list of [x, y] ?? 
            # Wrapper line 92: pixel_landmarks = self._scale_to_pixel(landmark_list)
            # Wrapper line 102: return [[int(pt[0] * width), int(pt[1] * height)] for pt in landmark_list]
            # So it expects a list of [x, y] pairs.
            
            sign = predictor.predict(landmarks)
            emit('prediction_result', {'sign': sign})
        except Exception as e:
            print(f"Landmark Processing Error: {e}")

@socketio.on('send_message')
def handle_send_message(data):
    """
    Send text message to the room (Code based room).
    Data: { 'room': '123456', 'message': 'Hello' }
    Note: The frontend needs to know which room it is in. 
    Simplification: Each user stores their current_room.
    """
    room = data.get('room')
    message = data.get('message')
    username = users[request.sid]['username']
    
    if room:
        emit('receive_message', {'sender': username, 'message': message}, room=room)

@socketio.on('check_practice_sign')
def handle_check_practice_sign(data):
    """
    Practice mode: Check if user's sign matches the target character.
    Data: { 'landmarks': [...], 'target': 'A' }
    Response: { 'correct': True/False, 'predicted': 'B', 'xp_earned': 5 }
    """
    landmarks = data.get('landmarks')
    target = data.get('target')
    
    if landmarks and target:
        try:
            # Predict the sign from landmarks
            predicted_sign = predictor.predict(landmarks)
            
            # Check if prediction matches target
            is_correct = (predicted_sign.upper() == target.upper())
            
            # Award XP if correct (only for authenticated users)
            xp_earned = 0
            if is_correct and current_user.is_authenticated:
                xp_earned = 5
                current_user.points += xp_earned
                db.session.commit()
            
            emit('practice_result', {
                'correct': is_correct,
                'predicted': predicted_sign,
                'target': target,
                'xp_earned': xp_earned,
                'total_xp': current_user.points if current_user.is_authenticated else 0
            })
            
        except Exception as e:
            print(f"Practice Sign Check Error: {e}")
            emit('practice_result', {
                'correct': False,
                'predicted': '?',
                'target': target,
                'xp_earned': 0,
                'error': str(e)
            })


if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
