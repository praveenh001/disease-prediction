import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import re
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__)
app.secret_key = 'a8b3c7d2e9f43a14bf1e92587db67c3a5cc9f71baf9d4465f7e9842e1c6cda3b'


# --- Database Initialization ---
def init_db():
    with sqlite3.connect('users.db') as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT,
            age INTEGER,
            gender TEXT
        )''')
        try:
            conn.execute('INSERT OR IGNORE INTO users (username, password, email, age, gender) VALUES (?, ?, ?, ?, ?)',
                         ('testuser', generate_password_hash('password123'), 'test@example.com', 30, 'Other'))
            conn.commit()
        except sqlite3.IntegrityError:
            pass

init_db()

# --- Symptom-Disease Dataset & ML Model ---
data = {
    'Disease': [
        'Common Cold', 'Influenza', 'Strep Throat', 'Gastroenteritis', 'Migraine',
        'Pneumonia', 'Bronchitis', 'Allergic Rhinitis', 'Sinusitis', 'COVID-19',
        'Tonsillitis', 'Laryngitis', 'Asthma', 'Food Poisoning', 'Tension Headache'
    ],
    'Symptoms': [
        ['fever', 'cough', 'sore throat', 'runny nose', 'fatigue', 'sneezing'],
        ['high fever', 'cough', 'sore throat', 'muscle aches', 'fatigue', 'headache', 'chills'],
        ['sore throat', 'fever', 'difficulty swallowing', 'swollen lymph nodes', 'red tonsils'],
        ['nausea', 'vomiting', 'diarrhea', 'abdominal pain', 'fever'],
        ['headache', 'nausea', 'sensitivity to light', 'sensitivity to sound', 'dizziness'],
        ['high fever', 'cough', 'shortness of breath', 'chest pain', 'fatigue'],
        ['cough', 'wheezing', 'chest tightness', 'fatigue', 'mucus production'],
        ['runny nose', 'sneezing', 'itchy eyes', 'nasal congestion', 'itchy throat'],
        ['facial pain', 'nasal congestion', 'headache', 'fever', 'thick nasal discharge'],
        ['fever', 'cough', 'shortness of breath', 'loss of taste', 'fatigue', 'loss of smell'],
        ['sore throat', 'fever', 'difficulty swallowing', 'white patches on tonsils'],
        ['hoarseness', 'sore throat', 'dry cough', 'difficulty speaking'],
        ['wheezing', 'shortness of breath', 'chest tightness', 'cough'],
        ['nausea', 'vomiting', 'diarrhea', 'abdominal pain', 'fever'],
        ['headache', 'neck stiffness', 'sensitivity to light', 'fatigue']
    ],
    'Severity_Weights': [
        1.0, 1.5, 1.8, 1.2, 1.4, 2.0, 1.3, 1.0, 1.5, 2.0, 1.8, 1.2, 1.7, 1.3, 1.1
    ]
}

df = pd.DataFrame(data)
mlb = MultiLabelBinarizer()
symptom_matrix = mlb.fit_transform(df['Symptoms'])

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(symptom_matrix, df['Disease'])

# --- Utility Functions ---
def predict_diseases(user_symptoms, user_severities):
    user_vector = mlb.transform([user_symptoms])[0]
    weighted_vector = user_vector * np.array([user_severities.get(sym, 1.0) for sym in mlb.classes_])
    probs = rf.predict_proba([weighted_vector])[0]
    predictions = [(rf.classes_[idx], round(prob * 100, 2)) for idx, prob in enumerate(probs) if prob > 0.1]
    return sorted(predictions, key=lambda x: x[1], reverse=True)[:3]

def login_required(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            flash('Login required!')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return wrapper

# --- Routes ---

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()

        with sqlite3.connect('users.db') as conn:
            user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
            if user and check_password_hash(user[2], password):
                session['username'] = username
                return redirect(url_for('home'))
            elif not user:
                flash('User not found. Please register.')
            else:
                flash('Incorrect password.')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password'].strip()
        email = request.form['email'].strip()
        age = request.form['age']
        gender = request.form['gender']

        if not username or not password or not email or not age:
            flash('All fields are required.')
            return redirect(url_for('register'))

        if len(password) < 6:
            flash('Password must be at least 6 characters long.')
            return redirect(url_for('register'))

        if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
            flash('Invalid email format.')
            return redirect(url_for('register'))

        try:
            with sqlite3.connect('users.db') as conn:
                conn.execute('INSERT INTO users (username, password, email, age, gender) VALUES (?, ?, ?, ?, ?)',
                             (username, generate_password_hash(password), email, int(age), gender))
                conn.commit()
                flash('Registration successful. Please login.')
                return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username already exists.')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out.')
    return redirect(url_for('login'))

@app.route('/home')
@login_required
def home():
    return render_template('home.html', username=session['username'])

@app.route('/symptoms', methods=['GET', 'POST'])
@login_required
def symptoms():
    if request.method == 'POST':
        user_symptoms = request.form.getlist('symptoms')
        user_severities = {key.replace('severity_', ''): float(request.form[key]) for key in request.form if key.startswith('severity_')}

        if not user_symptoms:
            flash('Please select at least one symptom.')
            return redirect(url_for('symptoms'))

        invalid_symptoms = [s for s in user_symptoms if s not in mlb.classes_]
        if invalid_symptoms:
            flash(f'Invalid symptoms: {", ".join(invalid_symptoms)}')
            return redirect(url_for('symptoms'))

        session['predictions'] = predict_diseases(user_symptoms, user_severities)
        return redirect(url_for('results'))

    return render_template('symptoms.html', symptoms=mlb.classes_)

@app.route('/results')
@login_required
def results():
    return render_template('results.html', predictions=session.get('predictions', []))

@app.route('/profile')
@login_required
def profile():
    with sqlite3.connect('users.db') as conn:
        user = conn.execute('SELECT username, email, age, gender FROM users WHERE username = ?', (session['username'],)).fetchone()
    return render_template('profile.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)
