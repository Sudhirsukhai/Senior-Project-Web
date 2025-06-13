from flask import Flask, render_template, request, redirect, url_for, flash, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import date

app = Flask(__name__)
app.secret_key = 'supersecretkey'
DB = 'users.db'

# Initialize SQLite DB
def init_db():
    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            calorie_goal INTEGER
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                meal_type TEXT,
                food TEXT NOT NULL,
                calories INTEGER NOT NULL,
                date_logged DATE NOT NULL,
                FOREIGN KEY(user_id) REFERENCES users(id)
            )
        ''')
        conn.commit()

# Home route redirects to login
@app.route('/')
def home():
    return redirect(url_for('login'))

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash("Passwords do not match", "danger")
            return redirect(url_for('register'))

        hashed_pw = generate_password_hash(password)

        try:
            with sqlite3.connect(DB) as conn:
                c = conn.cursor()
                c.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
                conn.commit()
            flash("Registration successful. Please log in.", "success")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash("Username already exists.", "danger")
            return redirect(url_for('register'))

    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("SELECT id, password FROM users WHERE username = ?", (username,))
            user = c.fetchone()

        if user and check_password_hash(user[1], password):
            session['user_id'] = user[0]
            session['username'] = username
            flash("Login successful.", "success")
            return redirect('/dashboard')
        else:
            flash("Invalid credentials.", "danger")
            return redirect(url_for('login'))

    return render_template('index.html')

# Dashboard (protected)
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("SELECT COUNT(*), SUM(calories) FROM meals WHERE user_id = ?", (user_id,))
        meal_count, total_calories = c.fetchone()

    average = round(total_calories / meal_count, 2) if meal_count > 0 else 0

    # Optional motivational messages
    if meal_count == 0:
        message = "Let’s start logging your first meal today!"
    elif meal_count < 5:
        message = "Great start! Keep building that streak!"
    elif meal_count < 15:
        message = "Awesome! You're building healthy habits!"
    else:
        message = "You're a meal-logging master! 🔥"

    return render_template(
        'MainPage.html',
        username=session['username'],
        meal_count=meal_count,
        total_calories=total_calories or 0,
        average_calories=average,
        message=message
    )
    








@app.route('/log/<meal_type>', methods=['GET', 'POST'])
def log_meal(meal_type):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        food = request.form['food']
        calories = int(request.form['calories'])
        today = date.today()

        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO meals (user_id, meal_type, food, calories, date_logged)
                VALUES (?, ?, ?, ?, ?)
            ''', (session['user_id'], meal_type, food, calories, today))
            conn.commit()

        flash(f"{meal_type} logged successfully!", "success")
        return redirect(url_for('dashboard'))

    return render_template('CalCell.html', meal_type=meal_type)







# Logout
@app.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('login'))






def calculate_bmr(gender: str, age: int, height_cm: float, weight_kg: float) -> float:
    if gender.lower() == 'male':
        return 66.5 + (13.75 * weight_kg) + (5.003 * height_cm) - (6.75 * age)
    elif gender.lower() == 'female':
        return 655.1 + (9.563 * weight_kg) + (1.850 * height_cm) - (4.676 * age)
    else:
        raise ValueError("Gender must be 'male' or 'female'")

def calculate_tdee(bmr: float, activity_level: str) -> float:
    multipliers = {
        'sedentary': 1.2,
        'light': 1.375,
        'moderate': 1.55,
        'active': 1.725,
        'super': 1.9
    }
    return bmr * multipliers.get(activity_level, 1.2)

@app.route('/bmr', methods=['GET', 'POST'])
def bmr_page():
    bmr = tdee = None
    if request.method == 'POST':
        gender = request.form['gender']
        age = int(request.form['age'])
        height = float(request.form['height'])
        weight = float(request.form['weight'])
        activity_level = request.form['activity']

        bmr = round(calculate_bmr(gender, age, height, weight), 2)
        tdee = round(calculate_tdee(bmr, activity_level), 2)
        with sqlite3.connect(DB) as conn:
            c = conn.cursor()
            c.execute("UPDATE users SET calorie_goal = ? WHERE id = ?", (tdee, session['user_id']))
            conn.commit()

            flash(f"Calorie goal set to {tdee} kcal/day.", "success")
    return render_template('CalTrack.html', bmr=bmr, tdee=tdee)



@app.route('/history')
def meal_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    with sqlite3.connect(DB) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT date_logged, meal_type, food, calories
            FROM meals
            WHERE user_id = ?
            ORDER BY date_logged DESC
        """, (session['user_id'],))
        meals = c.fetchall()

    return render_template('Meal_History.html', meals=meals)
 
if __name__ == '__main__':
    init_db()
    app.run(debug=True)