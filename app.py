from flask import Flask, render_template, request, jsonify, send_file, session, redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json
import uuid
from datetime import datetime, date
from functools import wraps
from flask_pymongo import PyMongo
from bson import ObjectId

app = Flask(__name__)

# Get environment variables with error checking
MONGO_URI = os.environ.get("MONGO_URI")
SECRET_KEY = os.environ.get("SECRET_KEY")

if not MONGO_URI:
    raise ValueError("MONGO_URI environment variable is not set")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY environment variable is not set")

app.config["MONGO_URI"] = MONGO_URI
app.secret_key = SECRET_KEY
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'doc', 'docx', 'txt', 'png', 'jpg', 'jpeg'}
app.config['SESSION_COOKIE_SECURE'] = True  # Required for Vercel HTTPS
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Prevent CSRF

mongo = PyMongo(app)
db = mongo.db
# Official rate card (display only - admin sets actual price)
RATE_CARD = {
    'Blue Book': {'base': 15, 'fee': 2, 'unit': 'page'},
    'Observation': {'base': 17, 'fee': 2, 'unit': 'page'},
    'Record-Ruled': {'base': 20, 'fee': 2, 'unit': 'page'},
    'Record-Unruled': {'base': 15, 'fee': 2, 'unit': 'page'},
    'PPT': {'base': 60, 'fee': 7, 'unit': '10 slides'},
    'Word Doc': {'base': 50, 'fee': 6, 'unit': 'doc'},
    'Report': {'base': 100, 'fee': 12, 'unit': 'doc'}
}

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# MongoDB Database Helper Functions
def fetch_all_tasks():
    """Get all tasks from database"""
    tasks = list(db.tasks.find().sort('created_at', -1))
    # Convert ObjectId to string for JSON serialization
    for task in tasks:
        if '_id' in task:
            task['_id'] = str(task['_id'])
    return tasks

def get_task_by_id(task_id):
    """Get single task by ID"""
    task = db.tasks.find_one({'task_id': task_id})
    if task and '_id' in task:
        task['_id'] = str(task['_id'])
    return task

def save_task(task_data):
    """Insert or update task"""
    task_id = task_data.get('task_id')
    existing_task = db.tasks.find_one({'task_id': task_id})
    
    if existing_task:
        # Update existing task
        db.tasks.update_one(
            {'task_id': task_id},
            {'$set': task_data}
        )
    else:
        # Insert new task
        db.tasks.insert_one(task_data)
    
    return task_id

def save_user_file(task_id, filename):
    """Save user uploaded file reference - MongoDB stores files array in task document"""
    db.tasks.update_one(
        {'task_id': task_id},
        {'$push': {'user_uploaded_files': filename}}
    )
    return True

def get_user_by_username(username):
    """Get user by username from users collection"""
    user = db.users.find_one({'username': username})
    if user and '_id' in user:
        user['_id'] = str(user['_id'])
        user['id'] = user.get('id', str(user['_id']))
    return user

def get_writer_by_username(username):
    """Get writer by username from writers collection"""
    writer = db.writers.find_one({'username': username})
    if writer and '_id' in writer:
        writer['_id'] = str(writer['_id'])
        writer['id'] = writer.get('id', str(writer['_id']))
    return writer

def get_admin_by_username(username):
    """Get admin by username"""
    admin = db.admin.find_one({'username': username})
    if admin and '_id' in admin:
        admin['_id'] = str(admin['_id'])
    return admin

def create_user(user_data):
    """Create new user"""
    user_doc = {
        'id': str(uuid.uuid4()),
        'username': user_data['username'],
        'email': user_data['email'],
        'password': user_data['password'],
        'phone': user_data.get('phone', ''),
        'created_at': datetime.now().isoformat()
    }
    result = db.users.insert_one(user_doc)
    return result.inserted_id

def create_writer(writer_data):
    """Create new writer"""
    writer_doc = {
        'id': str(uuid.uuid4()),
        'username': writer_data['username'],
        'email': writer_data['email'],
        'password': writer_data['password'],
        'phone': writer_data.get('phone', ''),
        'created_at': datetime.now().isoformat(),
        'completed_tasks': 0,
        'earnings': 0.0
    }
    result = db.writers.insert_one(writer_doc)
    return result.inserted_id

# Authentication decorators
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def writer_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_role' not in session or session['user_role'] != 'writer':
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    return render_template('index.html')

# Authentication Routes
@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/api/signup', methods=['POST'])
def signup():
    try:
        data = request.json
        user_type = data.get('user_type')  # 'user' or 'writer'
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        
        if not all([user_type, username, email, password, phone]):
            return jsonify({'error': 'All fields including phone number are required'}), 400
        
        # Check if user already exists
        existing_user = get_user_by_username(username)
        existing_writer = get_writer_by_username(username)
        
        if existing_user or existing_writer:
            return jsonify({'error': 'Username already exists'}), 400
        
        # Check email
        user_email_check = db.users.find_one({'email': email})
        writer_email_check = db.writers.find_one({'email': email})
        
        if user_email_check or writer_email_check:
            return jsonify({'error': 'Email already exists'}), 400
        
        # Create new user
        user_data = {
            'username': username,
            'email': email,
            'password': generate_password_hash(password),
            'phone': phone
        }
        
        if user_type == 'writer':
            create_writer(user_data)
        else:
            create_user(user_data)
        
        return jsonify({
            'success': True,
            'message': f'{user_type.capitalize()} account created successfully'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username')
        password = data.get('password')
        user_type = data.get('user_type')  # 'user', 'writer', or 'admin'
        
        if not all([username, password, user_type]):
            return jsonify({'error': 'All fields required'}), 400
        
        # Admin login
        if user_type == 'admin':
            admin = get_admin_by_username(username)
            if admin and check_password_hash(admin['password'], password):
                session['user_id'] = 'admin'
                session['username'] = username
                session['user_role'] = 'admin'
                return jsonify({
                    'success': True,
                    'role': 'admin',
                    'redirect': '/admin'
                })
            return jsonify({'error': 'Invalid admin credentials'}), 401
        
        # User/Writer login
        user = None
        if user_type == 'user':
            user = get_user_by_username(username)
        elif user_type == 'writer':
            user = get_writer_by_username(username)
        
        if user and check_password_hash(user['password'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['user_role'] = user_type
            session['user_email'] = user['email']
            
            redirect_url = '/user-dashboard' if user_type == 'user' else '/writer-dashboard'
            
            return jsonify({
                'success': True,
                'role': user_type,
                'redirect': redirect_url
            })
        
        return jsonify({'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

# User Dashboard
@app.route('/user-dashboard')
@login_required
def user_dashboard():
    if session.get('user_role') != 'user':
        return redirect(url_for('index'))
    return render_template('user_dashboard.html')

# Writer Dashboard
@app.route('/writer-dashboard')
@writer_required
def writer_dashboard():
    return render_template('writer_dashboard.html')

@app.route('/pricing')
def pricing():
    return render_template('pricing.html')

@app.route('/create-order')
@login_required
def create_order_page():
    if session.get('user_role') != 'user':
        return redirect(url_for('index'))
    return render_template('create_order.html')

@app.route('/admin')
@admin_required
def admin_dashboard():
    return render_template('admin.html')

@app.route('/user-task')
def user_task_page():
    return render_template('user_task.html')

# API Endpoints
@app.route('/api/create_task', methods=['POST'])
@login_required
def create_task():
    try:
        if session.get('user_role') != 'user':
            return jsonify({'error': 'Only users can create tasks'}), 403
        
        # Get form data
        work_type = request.form.get('work_type')
        user_contact = session.get('user_email')
        deadline_date = request.form.get('deadline')
        deadline_time = request.form.get('deadline_time')
        notes = request.form.get('notes', '')
        material_option = request.form.get('material_option', 'provide')  # 'provide' or 'buy'
        
        if not all([work_type, deadline_date, deadline_time]):
            return jsonify({'error': 'Work type, deadline date and time required'}), 400
        
        # Combine date and time
        deadline = f"{deadline_date} {deadline_time}"
        
        # Check if same-day order
        from datetime import date
        is_same_day = deadline_date == date.today().isoformat()
        same_day_surcharge = 0.25 if is_same_day else 0  # 25% extra
        
        # Calculate material cost
        material_cost = 0
        if material_option == 'buy':
            if work_type == 'Blue Book':
                material_cost = 20
            elif work_type in ['Record-Ruled', 'Record-Unruled']:
                material_cost = 90
        
        # Handle file upload (REQUIRED) - Store in MongoDB as base64
        import base64
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    # Read file and convert to base64
                    file_data = base64.b64encode(file.read()).decode('utf-8')
                    uploaded_files.append({
                        'filename': filename,
                        'data': file_data,
                        'content_type': file.content_type
                    })
        
        # Ensure at least one file is uploaded
        if not uploaded_files:
            return jsonify({'error': 'Please upload at least one file with the content to be written'}), 400
        
        # Generate task ID
        task_id = f"WX{uuid.uuid4().hex[:6].upper()}"
        
        # Create task (admin will set price later)
        task = {
            'task_id': task_id,
            'work_type': work_type,
            'pages': None,  # Admin will determine
            'base_price': None,  # Admin will set
            'platform_fee': None,  # Admin will set
            'material_cost': material_cost,  # Blue Book ₹20 or Record ₹90
            'material_option': material_option,  # 'provide' or 'buy'
            'same_day_surcharge': same_day_surcharge,  # 25% if same day
            'is_same_day': is_same_day,
            'final_price': None,  # Admin will set
            'worker_payout': None,  # Admin will set
            'user_id': session.get('user_id'),
            'user_contact': user_contact,
            'user_uploaded_files': uploaded_files,
            'admin_uploaded_result': None,
            'status': 'Pending',
            'deadline': deadline,
            'writer_id': None,
            'writer_username': None,
            'notes': notes,
            'created_at': datetime.now().isoformat(),
            'payment_received': False,
            'writer_paid': False
        }
        
        # Save task to database
        save_task(task)
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task created! Admin will review and set the price.'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/tasks', methods=['GET'])
@admin_required
def get_all_tasks():
    try:
        tasks = fetch_all_tasks()
        
        # Enrich tasks with full user and writer details
        for task in tasks:
            # Add user details
            if task.get('user_id'):
                user = db.users.find_one({'id': task['user_id']})
                if user:
                    task['user_details'] = {
                        'username': user['username'],
                        'email': user['email'],
                        'phone': user.get('phone', 'N/A')
                    }
            
            # Add writer details
            if task.get('writer_id'):
                writer = db.writers.find_one({'id': task['writer_id']})
                if writer:
                    task['writer_details'] = {
                        'username': writer['username'],
                        'email': writer['email'],
                        'phone': writer.get('phone', 'N/A'),
                        'completed_tasks': writer.get('completed_tasks', 0),
                        'earnings': writer.get('earnings', 0)
                    }
        
        return jsonify({'tasks': tasks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Writer API - Get available tasks
@app.route('/api/writer/available_tasks', methods=['GET'])
@writer_required
def get_available_tasks():
    try:
        tasks = list(db.tasks.find({
            '$or': [
                {'writer_id': None},
                {'writer_id': {'$exists': False}}
            ],
            'status': 'Pending'
        }).sort('created_at', -1))
        
        # Convert ObjectId to string
        for task in tasks:
            if '_id' in task:
                task['_id'] = str(task['_id'])
            # user_uploaded_files already in task document
        
        return jsonify({'tasks': tasks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Writer API - Claim a task
@app.route('/api/writer/claim_task', methods=['POST'])
@writer_required
def claim_task():
    try:
        data = request.json
        task_id = data.get('task_id')
        
        task = get_task_by_id(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if already claimed by someone else
        if task['writer_id'] is not None:
            if task['writer_id'] == session.get('user_id'):
                return jsonify({'error': 'You have already claimed this task'}), 400
            else:
                return jsonify({'error': 'This task has been claimed by another writer'}), 400
        
        # Update task
        db.tasks.update_one(
            {'task_id': task_id},
            {'$set': {
                'writer_id': session.get('user_id'),
                'writer_username': session.get('username'),
                'status': 'In Progress',
                'claimed_at': datetime.now().isoformat()
            }}
        )
        return jsonify({'success': True, 'message': 'Task claimed successfully!'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Writer API - Get my tasks
@app.route('/api/writer/my_tasks', methods=['GET'])
@writer_required
def get_my_tasks():
    try:
        writer_id = session.get('user_id')
        tasks = list(db.tasks.find({'writer_id': writer_id}).sort('created_at', -1))
        
        # Convert ObjectId to string
        for task in tasks:
            if '_id' in task:
                task['_id'] = str(task['_id'])
            # user_uploaded_files already in task document
        
        return jsonify({'tasks': tasks})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Writer API - Mark task as complete
@app.route('/api/writer/mark_complete', methods=['POST'])
@writer_required
def mark_task_complete():
    try:
        data = request.json
        task_id = data.get('task_id')
        
        task = get_task_by_id(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Check if task belongs to this writer
        if task['writer_id'] != session.get('user_id'):
            return jsonify({'error': 'You are not assigned to this task'}), 403
        
        # Check if already completed
        if task['status'] in ['Completed', 'Delivered']:
            return jsonify({'error': 'Task is already marked as complete'}), 400
        
        # Delete file data to save space, keep only filenames
        if 'user_uploaded_files' in task and task['user_uploaded_files']:
            files_without_data = []
            for file_info in task['user_uploaded_files']:
                files_without_data.append({
                    'filename': file_info.get('filename') if isinstance(file_info, dict) else file_info,
                    'content_type': file_info.get('content_type') if isinstance(file_info, dict) else None
                })
        
        # Mark as completed and remove file data
        update_data = {
            'status': 'Completed',
            'completed_at': datetime.now().isoformat()
        }
        
        if 'user_uploaded_files' in task and task['user_uploaded_files']:
            update_data['user_uploaded_files'] = files_without_data
        
        db.tasks.update_one(
            {'task_id': task_id},
            {'$set': update_data}
        )
        return jsonify({'success': True, 'message': 'Task marked as complete! Admin will review and upload the final work.'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# User API - Get my orders
@app.route('/api/user/my_orders', methods=['GET'])
@login_required
def get_my_orders():
    try:
        if session.get('user_role') != 'user':
            return jsonify({'error': 'Unauthorized'}), 403
        
        user_id = session.get('user_id')
        my_orders = list(db.tasks.find({'user_id': user_id}).sort('created_at', -1))
        
        # Convert ObjectId to string
        for order in my_orders:
            if '_id' in order:
                order['_id'] = str(order['_id'])
            # user_uploaded_files already in task document
            if 'user_uploaded_files' not in order:
                order['user_uploaded_files'] = []
        
        # Make writer information anonymous for users
        for order in my_orders:
            if order.get('writer_id'):
                order['writer_username'] = 'Anonymous Writer'
                order['writer_id'] = 'ANONYMOUS'
        
        return jsonify({'orders': my_orders})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/update_task', methods=['POST'])
@admin_required
def update_task():
    try:
        data = request.form
        task_id = data.get('task_id')
        
        task = get_task_by_id(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Prepare update fields for MongoDB
        update_data = {}
        
        # Admin can update all fields including pricing
        if 'status' in data:
            update_data['status'] = data['status']
        if 'writer_id' in data and data['writer_id']:
            update_data['writer_id'] = data['writer_id']
        if 'pages' in data and data['pages']:
            update_data['pages'] = int(data['pages'])
        if 'base_price' in data and data['base_price']:
            update_data['base_price'] = float(data['base_price'])
        if 'platform_fee' in data and data['platform_fee']:
            update_data['platform_fee'] = float(data['platform_fee'])
        if 'final_price' in data and data['final_price']:
            update_data['final_price'] = float(data['final_price'])
        if 'worker_payout' in data and data['worker_payout']:
            update_data['worker_payout'] = float(data['worker_payout'])
        if 'payment_received' in data:
            update_data['payment_received'] = data['payment_received'] == 'true'
        if 'writer_paid' in data:
            update_data['writer_paid'] = data['writer_paid'] == 'true'
        
        # Handle file upload (admin uploads completed work)
        if 'completed_file' in request.files:
            file = request.files['completed_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = f"{task_id}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER_COMPLETED'], unique_filename))
                update_data['admin_uploaded_result'] = unique_filename
                update_data['status'] = 'Completed'
        
        # Execute update
        if update_data:
            db.tasks.update_one(
                {'task_id': task_id},
                {'$set': update_data}
            )
        
        # Fetch updated task
        task = get_task_by_id(task_id)
        return jsonify({'success': True, 'task': task})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/user/task/<task_id>', methods=['GET'])
def get_task(task_id):
    try:
        task = get_task_by_id(task_id)
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Return limited info for user privacy
        return jsonify({
            'task_id': task['task_id'],
            'work_type': task['work_type'],
            'pages': task['pages'],
            'final_price': task['final_price'],
            'status': task['status'],
            'deadline': task['deadline'],
            'has_result': task['admin_uploaded_result'] is not None,
            'result_file': task['admin_uploaded_result']
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download/<task_id>', methods=['GET'])
def download_file(task_id):
    try:
        task = get_task_by_id(task_id)
        
        if not task or not task['admin_uploaded_result']:
            return jsonify({'error': 'File not found'}), 404
        
        file_path = os.path.join(app.config['UPLOAD_FOLDER_COMPLETED'], task['admin_uploaded_result'])
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on server'}), 404
        
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download_user_file/<task_id>/<int:file_index>', methods=['GET'])
def download_user_file(task_id, file_index):
    try:
        import base64
        from io import BytesIO
        
        task = get_task_by_id(task_id)
        
        if not task or 'user_uploaded_files' not in task:
            return jsonify({'error': 'Task or files not found'}), 404
        
        files = task['user_uploaded_files']
        
        if file_index >= len(files):
            return jsonify({'error': 'File not found'}), 404
        
        file_info = files[file_index]
        
        # Check if file data exists (not deleted after completion)
        if 'data' not in file_info:
            return jsonify({'error': 'File data has been removed after task completion'}), 410
        
        # Decode base64 data
        file_data = base64.b64decode(file_info['data'])
        
        # Create BytesIO object
        file_obj = BytesIO(file_data)
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=file_info['filename'],
            mimetype=file_info.get('content_type', 'application/octet-stream')
        )
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/rate_card', methods=['GET'])
def get_rate_card():
    return jsonify(RATE_CARD)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify API is running"""
    try:
        # Test MongoDB connection
        db.command('ping')
        return jsonify({
            'status': 'healthy',
            'mongodb': 'connected',
            'environment': 'production' if os.environ.get('VERCEL') else 'local'
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

# Vercel serverless function handler
app_handler = app

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
