from flask import Flask, render_template, request, jsonify, session
import os

from CalmBot.app.models.response_model import ResponseModel

from flask import send_file
from PIL import Image
import io
from datetime import datetime
from CalmBot.app.models.database import CalendarEntry, MoodEntry, User, db, UserActivity, GratitudeEntry
from sqlalchemy import extract
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for, session
from functools import wraps
from flask import Flask, render_template, request, jsonify, session
import os
import requests
from CalmBot.app.models.response_model import ResponseModel
from datetime import datetime
from CalmBot.app.models.database import CalendarEntry, MoodEntry, User, db, UserActivity, GratitudeEntry
from sqlalchemy import extract
from werkzeug.security import generate_password_hash, check_password_hash
from flask import redirect, url_for
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Initialize the response model
response_model = ResponseModel()

# Create directories if they do not exist
if not os.path.exists('logs'):
    os.makedirs('logs')

basedir = os.path.abspath(os.path.dirname(__file__))
database_dir = os.path.join(basedir, 'database')
if not os.path.exists(database_dir):
    os.makedirs(database_dir)

# Set the path for the database
database_path = os.path.join(database_dir, 'calmbot.db')
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{database_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize database
db.init_app(app)

# Create tables if they don't exist
with app.app_context():
    db.create_all()
    print("Database created successfully at:", database_path)

# User registration route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Hash password and save user to database
        hash_password = generate_password_hash(password)
        user = User(username=username, password=hash_password, email=email)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

# User login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Check credentials and create a session
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('index'))
        return 'Invalid credentials'
    return render_template('login.html')

# User logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Decorator for protected routes
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Home route (index)
@app.route('/')
@app.route('/index')
@login_required
def index():
    return render_template('index.html')

# API route for chat with BlenderBot
@app.route('/api/chat', methods=['POST'])
def chat():
    try:
        # Get user input and session ID from request
        data = request.json
        message = data['message']
        session_id = data['session_id']

        # Call the ResponseModel to interact with BlenderBot using Hugging Face API
        response = response_model.get_response(message, session_id)

        return jsonify({'response': response})
    except Exception as e:
        print("Error:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities/<activity_type>', methods=['POST'])
def handle_activity(activity_type):
    try:
        data = request.json
        session_id = data['session_id']

        new_activity = UserActivity(
            session_id=session_id,
            activity_type=activity_type
        )
        db.session.add(new_activity)
        db.session.commit()

        return jsonify({'status': 'success', 'message': f'{activity_type} activity recorded'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/activities/mood', methods=['POST'])
def track_mood():
    try:
        data = request.json
        print("Received mood data:", data)
        new_mood = MoodEntry(
            session_id=data['session_id'],
            mood=data['mood'],
            date=datetime.now().date(),
            notes=data.get('notes', '')
        )
        db.session.add(new_mood)
        db.session.commit()
        print("Mood saved successfully")
        return jsonify({'status': 'success'})
    except Exception as e:
        print("Error saving mood:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/moods/<int:month>/<int:year>')
def get_moods(month, year):
    try:
        month_moods = MoodEntry.query.filter(
            extract('month', MoodEntry.date) == month,
            extract('year', MoodEntry.date) == year
        ).all()

        return jsonify({
            'moods': [{
                'date': entry.date.strftime('%Y-%m-%d'),
                'mood': entry.mood,
                'notes': entry.notes
            } for entry in month_moods]
        })
    except Exception as e:
        print("Error fetching moods:", str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/api/calendar/<int:month>/<int:year>')
def get_calendar_data(month, year):
    entries = CalendarEntry.query.filter(
        extract('month', CalendarEntry.date) == month,
        extract('year', CalendarEntry.date) == year,
        CalendarEntry.user_id == session['user_id']
    ).all()

    return jsonify({
        'entries': [entry.to_dict() for entry in entries]
    })

@app.route('/api/calendar/day/<date>')
def get_day_details(date):
    try:
        date_obj = datetime.strptime(date, '%Y-%m-%d').date()
        entry = CalendarEntry.query.filter_by(
            date=date_obj,
            user_id=session['user_id']
        ).first()

        if entry:
            return jsonify({
                'mood': entry.mood,
                'gratitude': entry.gratitude,
                'activities': entry.activities.split(',') if entry.activities else []
            })
        return jsonify({'message': 'No entries for this date'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# Route for user activities, calendar, moods, etc.
@app.route('/user-activities', methods=['GET', 'POST'])
@login_required
def user_activities():
    if request.method == 'POST':
        activity = request.form['activity']
        user_id = session['user_id']
        new_activity = UserActivity(user_id=user_id, activity=activity, date=datetime.now())
        db.session.add(new_activity)
        db.session.commit()
        return redirect(url_for('user_activities'))

    activities = UserActivity.query.filter_by(user_id=session['user_id']).all()
    return render_template('user_activities.html', activities=activities)

# Route to view and log mood entries
@app.route('/mood-entry', methods=['GET', 'POST'])
@login_required
def mood_entry():
    if request.method == 'POST':
        mood = request.form['mood']
        user_id = session['user_id']
        new_mood = MoodEntry(user_id=user_id, mood=mood, date=datetime.now())
        db.session.add(new_mood)
        db.session.commit()
        return redirect(url_for('mood_entry'))

    moods = MoodEntry.query.filter_by(user_id=session['user_id']).all()
    return render_template('mood_entry.html', moods=moods)

# Route for calendar entries
@app.route('/calendar-entry', methods=['GET', 'POST'])
@login_required
def calendar_entry():
    if request.method == 'POST':
        event_name = request.form['event_name']
        event_date = request.form['event_date']
        user_id = session['user_id']
        new_event = CalendarEntry(user_id=user_id, event_name=event_name, event_date=event_date)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('calendar_entry'))

    events = CalendarEntry.query.filter_by(user_id=session['user_id']).all()
    return render_template('calendar_entry.html', events=events)


@app.route('/api/stats')
def get_stats():
    try:
        breathing_count = UserActivity.query.filter_by(activity_type='breathing').count()
        journal_count = UserActivity.query.filter_by(activity_type='gratitude').count()
        mood_count = UserActivity.query.filter_by(activity_type='mood').count()

        return jsonify({
            'breathing_exercises': breathing_count,
            'journal_entries': journal_count,
            'mood_checks': mood_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/log-specialist-selection', methods=['POST'])
def log_specialist_selection():
    data = request.json
    print(f"Specialist selected: {data}")
    return jsonify({'status': 'success'})

@app.route('/api/placeholder/<int:width>/<int:height>')
def placeholder_image(width, height):
    img = Image.new('RGB', (width, height), color='lightgray')
    img_io = io.BytesIO()
    img.save(img_io, 'PNG')
    img_io.seek(0)
    return send_file(img_io, mimetype='image/png')

    return response
@app.route('/api/calendar/entry', methods=['POST'])
def update_calendar_entry():
    try:
        data = request.json
        date_obj = datetime.strptime(data['date'][:10], '%Y-%m-%d').date()

        entry = CalendarEntry.query.filter_by(
            date=date_obj,
            user_id=session['user_id']
        ).first()

        if not entry:
            entry = CalendarEntry(
                user_id=session['user_id'],
                date=date_obj
            )
            db.session.add(entry)

        if 'mood' in data:
            entry.mood = data['mood']
        if 'gratitude' in data:
            entry.gratitude = data['gratitude']
        if 'activities' in data:
            current_activities = entry.activities.split(',') if entry.activities else []
            current_activities.append(data['activities'])
            entry.activities = ','.join(set(current_activities))

        db.session.commit()
        return jsonify({'status': 'success'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route for gratitude journaling
@app.route('/gratitude-entry', methods=['GET', 'POST'])
@login_required
def gratitude_entry():
    if request.method == 'POST':
        gratitude = request.form['gratitude']
        user_id = session['user_id']
        new_gratitude = GratitudeEntry(user_id=user_id, gratitude=gratitude, date=datetime.now())
        db.session.add(new_gratitude)
        db.session.commit()
        return redirect(url_for('gratitude_entry'))

    gratitudes = GratitudeEntry.query.filter_by(user_id=session['user_id']).all()
    return render_template('gratitude_entry.html', gratitudes=gratitudes)

# Run the app
#if __name__ == '__main__':
#   app.run(debug=True)
app = Flask(__name__)

