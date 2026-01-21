from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import re
from html import escape

load_dotenv()

# Funkce pro validaci a sanitaci dat
def validate_username(username):
    """Validuj uživatelské jméno - max 80 znaků, jen alfanumerické znaky a podtržítka"""
    if not username or len(username) < 3 or len(username) > 80:
        return False, "Uživatelské jméno musí mít 3-80 znaků"
    
    if not re.match(r'^[a-zA-Z0-9_-]+$', username):
        return False, "Uživatelské jméno může obsahovat jen písmena, čísla, podtržítko a pomlčku"
    
    return True, ""

def validate_email(email):
    """Validuj email"""
    if not email or len(email) > 120:
        return False, "Email je neplatný"
    
    # Jednoduchý email regex
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False, "Email je neplatný"
    
    return True, ""

def validate_password(password):
    """Validuj heslo - min 6 znaků, max 200"""
    if not password or len(password) < 6 or len(password) > 200:
        return False, "Heslo musí mít 6-200 znaků"
    
    return True, ""

def validate_habit_name(name):
    """Validuj název návyku - max 100 znaků, bez nebezpečných znaků"""
    if not name or len(name) < 1 or len(name) > 100:
        return False, "Název návyku musí mít 1-100 znaků"
    
    # Odstraň HTML znaky a přebytečné mezery
    name = escape(name).strip()
    
    return True, ""

def safe_string(value, max_length=100):
    """Ochrana před XSS - escapuj HTML znaky"""
    if not value:
        return ""
    value = str(value)[:max_length].strip()
    return escape(value)

app = Flask(__name__)

# Konfigurace databáze - SQL Server nebo SQLite
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')  # 'sqlite' nebo 'mssql'

if DB_TYPE == 'sqlite':
    # SQLite pro vývoj
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///habits.db'
else:
    # SQL Server pro produkci
    DB_USER = os.getenv('DB_USER', 'sa')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'DefaultPassword123')
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = os.getenv('DB_PORT', '1433')
    DB_NAME = os.getenv('DB_NAME', 'habit_tracker')
    
    # Connection string pro SQL Server
    connection_string = f'mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}?driver=ODBC+Driver+17+for+SQL+Server'
    app.config['SQLALCHEMY_DATABASE_URI'] = connection_string

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'your-secret-key-change-this-in-production')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Pro přístup se musíš přihlásit.'

# Modely databáze
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created = db.Column(db.DateTime, default=datetime.utcnow)
    habits = db.relationship('Habit', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class Habit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    target_per_week = db.Column(db.Integer, default=7)  # Cílový počet splnění za týden
    created = db.Column(db.Date, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    records = db.relationship('Record', backref='habit', lazy=True, cascade='all, delete-orphan')

class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    habit_id = db.Column(db.Integer, db.ForeignKey('habit.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    
    __table_args__ = (db.UniqueConstraint('habit_id', 'date', name='_habit_date_uc'),)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routy
@app.route('/')
@login_required
def index():
    """Hlavní stránka"""
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    today = datetime.now().date()
    today_str = today.strftime('%Y-%m-%d')
    
    # Příprava dat pro zobrazení
    habits_with_status = []
    for habit in habits:
        # Zkontrolovat, zda je návyk splněn dnes
        completed_today = Record.query.filter_by(habit_id=habit.id, date=today).first() is not None
        
        # Počet splnění za poslední týden
        week_start = today - timedelta(days=6)
        week_count = Record.query.filter(
            Record.habit_id == habit.id,
            Record.date >= week_start,
            Record.date <= today
        ).count()
        
        habits_with_status.append({
            'id': habit.id,
            'name': habit.name,
            'target_per_week': habit.target_per_week,
            'completed_today': completed_today,
            'week_count': week_count
        })
    
    return render_template('index.html', habits=habits_with_status, today=today_str)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Registrace nového uživatele"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password2 = request.form.get('password2', '').strip()
        
        # Validace uživatelského jména
        valid, msg = validate_username(username)
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('register'))
        
        # Validace emailu
        valid, msg = validate_email(email)
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('register'))
        
        # Validace hesla
        valid, msg = validate_password(password)
        if not valid:
            flash(msg, 'error')
            return redirect(url_for('register'))
        
        if password != password2:
            flash('Hesla se neshodují!', 'error')
            return redirect(url_for('register'))
        
        # Kontrola, zda uživatel už neexistuje
        if User.query.filter_by(username=username).first():
            flash('Uživatelské jméno už je použité!', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email už je použitý!', 'error')
            return redirect(url_for('register'))
        
        # Vytvoření nového uživatele
        user = User(username=safe_string(username, 80), email=safe_string(email, 120))
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registrace úspěšná! Můžeš se přihlásit.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Přihlášení uživatele"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash(f'Vítej zpět, {user.username}!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Nesprávné uživatelské jméno nebo heslo!', 'error')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Odhlášení uživatele"""
    logout_user()
    flash('Byl jsi odhlášen.', 'info')
    return redirect(url_for('login'))

@app.route('/add_habit', methods=['POST'])
@login_required
def add_habit():
    """Přidání nového návyku"""
    habit_name = request.form.get('habit_name', '').strip()
    target_per_week = request.form.get('target_per_week', '7').strip()
    
    # Validace názvu návyku
    valid, msg = validate_habit_name(habit_name)
    if not valid:
        flash(msg, 'error')
        return redirect(url_for('index'))
    
    try:
        target = int(target_per_week)
        if target < 1:
            target = 1
        elif target > 7:
            target = 7
    except ValueError:
        target = 7
    
    # Sanitace názvu
    habit_name = safe_string(habit_name, 100)
        
    new_habit = Habit(
        name=habit_name,
        target_per_week=target,
        created=datetime.now().date(),
        user_id=current_user.id
    )
    db.session.add(new_habit)
    db.session.commit()
    
    flash(f'Návyk "{habit_name}" přidán!', 'success')
    return redirect(url_for('index'))

@app.route('/delete_habit/<int:habit_id>', methods=['POST'])
@login_required
def delete_habit(habit_id):
    """Smazání návyku"""
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    db.session.delete(habit)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/toggle_habit/<int:habit_id>', methods=['POST'])
@login_required
def toggle_habit(habit_id):
    """Označení/odznačení návyku pro dnešní den"""
    # Ověření, že návyk patří aktuálnímu uživateli
    habit = Habit.query.filter_by(id=habit_id, user_id=current_user.id).first_or_404()
    
    today = datetime.now().date()
    
    # Zkontrolovat, zda už záznam existuje
    record = Record.query.filter_by(habit_id=habit_id, date=today).first()
    
    if record:
        # Záznam existuje, smažeme ho
        db.session.delete(record)
        completed = False
    else:
        # Vytvořit nový záznam
        new_record = Record(habit_id=habit_id, date=today)
        db.session.add(new_record)
        completed = True
    
    db.session.commit()
    return jsonify({'completed': completed})

@app.route('/statistics')
@login_required
def statistics():
    """Stránka se statistikami"""
    habits = Habit.query.filter_by(user_id=current_user.id).all()
    
    # Příprava statistik pro každý návyk
    stats = []
    for habit in habits:
        # Všechny záznamy pro tento návyk
        all_records = Record.query.filter_by(habit_id=habit.id).order_by(Record.date).all()
        record_dates = [r.date for r in all_records]
        
        # Celkový počet splnění
        total_count = len(record_dates)
        
        # Aktuální série (streak)
        current_streak = 0
        check_date = datetime.now().date()
        while check_date in record_dates:
            current_streak += 1
            check_date -= timedelta(days=1)
        
        # Nejdelší série
        max_streak = 0
        if record_dates:
            temp_streak = 1
            max_streak = 1
            
            for i in range(1, len(record_dates)):
                if (record_dates[i] - record_dates[i-1]).days == 1:
                    temp_streak += 1
                    max_streak = max(max_streak, temp_streak)
                else:
                    temp_streak = 1
        
        # Poslední 30 dní
        last_30_days = []
        for i in range(29, -1, -1):
            date = datetime.now().date() - timedelta(days=i)
            last_30_days.append({
                'date': date.strftime('%Y-%m-%d'),
                'completed': date in record_dates
            })
        
        stats.append({
            'habit': {
                'id': habit.id,
                'name': habit.name,
                'target_per_week': habit.target_per_week,
                'created': habit.created.strftime('%Y-%m-%d')
            },
            'total_count': total_count,
            'current_streak': current_streak,
            'max_streak': max_streak,
            'last_30_days': last_30_days
        })
    
    return render_template('statistics.html', stats=stats)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)
