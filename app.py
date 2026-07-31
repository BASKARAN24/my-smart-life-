from flask import Flask, render_template, request, redirect, session
from models.calorie_model import predict_calories
from models.diet_model import recommend_diet
from models.lifestyle_model import lifestyle_advice
import sqlite3
import datetime

app = Flask(__name__)
app.secret_key = "smart_life_secret" # Essential for session security

# --- AUTHENTICATION ---
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        username, email, password = request.form["username"], request.form["email"], request.form["password"]
        conn = sqlite3.connect("database/users.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username,email,password) VALUES (?,?,?)", (username,email,password))
        conn.commit()
        conn.close()
        return redirect("/login")
    return render_template("register.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        email, password = request.form["email"], request.form["password"]
        conn = sqlite3.connect("database/users.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email,password))
        user = cursor.fetchone()
        conn.close()
        if user:
            session['user'] = user[1]       # Display name
            session['user_email'] = user[2] # Unique ID for DB operations
            return redirect("/dashboard")
        return "Invalid Login"
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear() 
    return redirect("/")

# --- DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    if 'user' not in session:
        return redirect("/login")
    return render_template("dashboard.html", username=session['user'])

# --- HEALTH & AI TOOLS ---
@app.route("/health", methods=["GET","POST"])
def health():
    calories, workout_tips = None, []
    if request.method == "POST":
        # ADD THIS REAL NOTIFICATION
        now = datetime.datetime.now().strftime("%I:%M %p")
        cursor = sqlite3.connect("database/users.db").cursor()
        cursor.execute("""
            INSERT INTO notifications (user_email, icon, title, body, time) 
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_email'], "🎯", "New Health Goal", f"Target set: {calories} kcal. Stay hydrated!", now))
        # ... (rest of route)
        age, weight, height, activity = int(request.form["age"]), int(request.form["weight"]), int(request.form["height"]), int(request.form["activity"])
        calories = predict_calories(age, weight, height, activity)
        if activity == 1: workout_tips = ["🚶 45 min Brisk Walk", "🧘 Morning Yoga", "💧 Drink 2.5L Water"]
        elif activity == 2: workout_tips = ["🏃 30 min Jogging", "🏋️ HIIT Session", "🥗 High Fiber Diet"]
        else: workout_tips = ["🚴 60 min Cycling", "💪 Weight Lifting", "🍌 Protein Recovery"]
    return render_template("health.html", calories=calories, workout_tips=workout_tips)

@app.route("/diet", methods=["GET","POST"])
def diet():
    meal_plan = recommend_diet(request.form["goal"]) if request.method == "POST" else None
    return render_template("diet.html", meal_plan=meal_plan)

@app.route("/lifestyle", methods=["GET", "POST"])
def lifestyle():
    # 1. Security check
    if 'user_email' not in session:
        return redirect("/login")

    advice = None
    if request.method == "POST":
        # Extract data from the form
        sleep = float(request.form.get("sleep", 0))
        stress = int(request.form.get("stress", 0))
        water = float(request.form.get("water", 0))

        # 2. Generate the AI Advice
        advice = lifestyle_advice(sleep, stress, water)

        # 3. Logic for "Smart" Notifications
        # We customize the alert based on their lowest stat
        now = datetime.datetime.now().strftime("%I:%M %p")
        notif_title = "Lifestyle Analysis"
        
        if stress > 7:
            icon, msg = "🧘", "High stress detected. AI suggests a 5-min meditation."
        elif sleep < 6:
            icon, msg = "😴", "Sleep debt recorded. Try to avoid screens 1h before bed."
        elif water < 2:
            icon, msg = "💧", "Hydration goal missed. Drink a glass of water now!"
        else:
            icon, msg = "✨", "Great balance! Your lifestyle scores are optimal."

        # 4. Save Notification to Database
        conn = sqlite3.connect("database/users.db")
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO notifications (user_email, icon, title, body, time) 
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_email'], icon, notif_title, msg, now))
        conn.commit()
        conn.close()

    return render_template("lifestyle.html", advice=advice)
# --- DATABASE LOGGING (TASKS, MOOD, ANALYTICS) ---
@app.route("/tasks", methods=["GET","POST"])
def tasks():
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    
    if request.method == "POST":
        task_content = request.form["task"]
        
        # 1. Save the Task (Your existing code)
        cursor.execute("INSERT INTO tasks (task) VALUES (?)", (task_content,))
        
        # 2. CREATE THE NOTIFICATION (The new part)
        now = datetime.datetime.now().strftime("%I:%M %p")
        user_email = session.get('user_email') # Make sure this matches your login session name!
        
        cursor.execute("""
            INSERT INTO notifications (user_email, icon, title, body, time) 
            VALUES (?, ?, ?, ?, ?)
        """, (user_email, "📝", "Task Created", task_content, now))
        
        conn.commit()
    
    # ... rest of your code ...
    cursor.execute("SELECT * FROM tasks")
    task_list = cursor.fetchall()
    conn.close()
    return render_template("tasks.html", tasks=task_list)

@app.route("/delete_task/<int:task_id>/") 
def delete_task(task_id):
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return redirect("/tasks")

@app.route("/mood", methods=["GET", "POST"])
def mood():
    # 1. Security Check: Redirect to login if not authenticated
    if 'user_email' not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()

    if request.method == "POST":
        # Get the selected mood from the form
        selected_mood = request.form.get("mood")
        # Format the current time for the mood entry
        date_str = datetime.datetime.now().strftime("%d %b, %I:%M %p")
        
        # 2. SAVE THE MOOD to the mood table
        cursor.execute("INSERT INTO mood (mood, date) VALUES (?,?)", (selected_mood, date_str))
        
        # 3. SEND REAL NOTIFICATION to the notifications table
        # We use a matching emoji based on the mood selected
        mood_icons = {"Happy": "🌟", "Neutral": "😐", "Sad": "📉", "Stressed": "🧘", "Energetic": "⚡"}
        icon = mood_icons.get(selected_mood, "😊")
        
        cursor.execute("""
            INSERT INTO notifications (user_email, icon, title, body, time) 
            VALUES (?, ?, ?, ?, ?)
        """, (session['user_email'], icon, "Mood Logged", f"You recorded feeling {selected_mood}.", date_str))
        
        conn.commit()

    # 4. FETCH DATA: Get the last 5 moods to show on the page
    cursor.execute("SELECT * FROM mood ORDER BY id DESC LIMIT 5")
    moods = cursor.fetchall()
    conn.close()
    
    return render_template("mood.html", moods=moods)

@app.route("/analytics")
def analytics():
    data = {"calories": 1800, "protein": 75, "carbs": 220, "fat": 60}
    return render_template("analytics.html", data=data)

# --- SYSTEM PAGES ---
@app.route("/reports")
def reports():
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM tasks")
    total_tasks = cursor.fetchone()[0]
    cursor.execute("SELECT mood, COUNT(mood) as occurrence FROM mood GROUP BY mood ORDER BY occurrence DESC LIMIT 1")
    mood_data = cursor.fetchone()
    dominant_mood = mood_data[0] if mood_data else "No Data"
    cursor.execute("SELECT COUNT(*) FROM mood")
    mood_count = cursor.fetchone()[0]
    conn.close()

    stats = {
        "tasks_done": total_tasks,
        "avg_mood": dominant_mood,
        "consistency": f"{min(mood_count * 10, 100)}%",
        "calories_avg": 2100
    }
    return render_template("reports.html", stats=stats)

@app.route("/notifications")
def notifications():
    if 'user_email' not in session:
        return redirect("/login")

    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    
    # Pull ONLY the notifications belonging to the logged-in user
    cursor.execute("""
        SELECT icon, title, body, time 
        FROM notifications 
        WHERE user_email = ? 
        ORDER BY id DESC
    """, (session['user_email'],))
    
    db_data = cursor.fetchall()
    conn.close()

    # Convert the database rows into a format the HTML understands
    alerts = []
    for row in db_data:
        alerts.append({
            "icon": row[0],
            "title": row[1],
            "body": row[2],
            "time": row[3]
        })

    return render_template("notifications.html", alerts=alerts)

@app.route("/settings", methods=["GET", "POST"])
def settings():
    if 'user_email' not in session:
        return redirect("/login")
    conn = sqlite3.connect("database/users.db")
    cursor = conn.cursor()
    if request.method == "POST":
        new_name = request.form.get("username")
        cursor.execute("UPDATE users SET username = ? WHERE email = ?", (new_name, session['user_email']))
        conn.commit()
        session['user'] = new_name 
        return redirect("/dashboard")
    cursor.execute("SELECT username, email FROM users WHERE email = ?", (session['user_email'],))
    user_data = cursor.fetchone()
    conn.close()
    return render_template("settings.html", user=user_data)

if __name__ == "__main__":
    app.run(debug=True)
