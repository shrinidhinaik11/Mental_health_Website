from flask import Flask, render_template, request, redirect, session
from datetime import datetime
import re
import mysql.connector


app = Flask(__name__)

def get_mysql_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Meera",
        database="mindwell_db"
    )

app.secret_key = "mindwell123"
ADMIN_EMAIL = "liyanandininaik@gmail.com"

from flask_mail import Mail, Message
import os

app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "liyanandininaik@gmail.com"
app.config["MAIL_PASSWORD"] = os.environ.get("MINDWELL_EMAIL_PASSWORD")
print("Gmail username configured:", bool(app.config["MAIL_USERNAME"]))
print("App password available:", bool(app.config["MAIL_PASSWORD"]))
app.config["MAIL_DEFAULT_SENDER"] = "liyanandininaik@gmail.com"

mail = Mail(app)

def send_welcome_email(username, user_email):
    try:
        msg = Message(
            subject="Welcome to MindWell!",
            recipients=[user_email]
        )

        msg.body = f"""
Hello {username},

Welcome to MindWell! 🌿

Your account has been created successfully.

We're happy to have you join our community. Take a moment for yourself,
explore our wellness services, and begin your journey toward better
mental well-being.

Thank you for joining MindWell!

Warm regards,
The MindWell Team
"""

        mail.send(msg)
        print("Welcome email sent successfully to:", user_email)
        return True

    except Exception as e:
        print("Email sending failed:", e)
        return False


def create_notebook_table():
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notebook_entries (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        title VARCHAR(150),
        feelings TEXT NOT NULL,
        created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    )
""")

    conn.commit()
    conn.close()



@app.route("/feelings-notebook", methods=["GET", "POST"])
def feelings_notebook():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_mysql_connection()
    cursor = conn.cursor()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        feelings = request.form.get("feelings", "").strip()

        if feelings:
            cursor.execute("""
                INSERT INTO notebook_entries
                (user_id, title, feelings, created_at)
                VALUES (%s, %s, %s, %s)
            """, (
                session["user_id"],
                title,
                feelings,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ))

            conn.commit()

        conn.close()
        return redirect("/feelings-notebook")

    cursor.execute("""
        SELECT id, title, feelings, created_at
        FROM notebook_entries
        WHERE user_id = %s
        ORDER BY id DESC
    """, (session["user_id"],))

    entries = cursor.fetchall()
    conn.close()

    return render_template(
        "feelings_notebook.html",
        entries=entries
    )



def analyze_journal(text):

    positive_words = [
        "happy", "good", "great", "joy", "love",
        "excited", "peaceful", "calm", "wonderful"
    ]

    negative_words = [
        "sad", "bad", "stress", "stressed", "angry",
        "tired", "lonely", "worried", "anxious", "upset"
    ]

    text = text.lower()

    positive_count = 0
    negative_count = 0

    for word in positive_words:
        if word in text:
            positive_count += 1

    for word in negative_words:
        if word in text:
            negative_count += 1

    if positive_count > negative_count:
        sentiment = "Positive 😊"

    elif negative_count > positive_count:
        sentiment = "Negative 😔"

    else:
        sentiment = "Neutral 😐"

    return sentiment

@app.route("/")
def home():

    user_id = session.get("user_id")

    daily_tip = "Take a moment to relax and take care of yourself. 🌿"

    if user_id:

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT mood
            FROM journal
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        conn.close()

        if result:

            mood = result[0]

            if mood == "Happy":
                daily_tip = "😊 Keep doing things that make you feel good!"

            elif mood == "Sad":
                daily_tip = "😔 Take some time to relax and talk to someone you trust."

            elif mood == "Stressed":
                daily_tip = "😣 Take a short break and try some deep breathing."

            elif mood == "Neutral":
                daily_tip = "😐 Try something new today to lift your mood."

    return render_template(
        "home.html",
        username=session.get("username"),
        logged_in="user_id" in session
    )
@app.route("/daily-tips")
def daily_tips():
    daily_tip = "Take a few minutes today to relax and care for yourself."
    advice = "Be kind to yourself. Small steps toward wellbeing matter."
    self_care = "Take a short break, drink some water, and breathe slowly."

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    daily_tip = "Take a moment to relax and take care of yourself. 🌿"

    if user_id:

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT mood
            FROM journal
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
            """,
            (user_id,)
        )

        result = cursor.fetchone()

        conn.close()

        if result:

            mood = result[0]

            daily_tip = "Take a moment to relax and take care of yourself. 🌿"
            advice = ""
            self_care = []

            if mood == "Happy":

              daily_tip = "😊 Keep enjoying the positive moments in your day!"

              advice = "🌻 Your happiness is something worth celebrating. Enjoy the little things and share your positive energy with the people around you. 💚✨"

              self_care = [
               "🎵 Listen to your favorite song.",
                "💃 Dance or do something fun.",
                "🫶 Spend some time with someone you love.",
                "📸 Capture a happy memory.",
                "🌈 Do something that makes you smile."
    ]

            elif mood == "Sad":

              daily_tip = "😔 It's okay to have difficult days. Be gentle with yourself. 🫶"

              advice = "🌧️ You don't have to force yourself to feel happy all the time. Give yourself space to feel what you're feeling, and remember that difficult moments can pass. 🌱💚"

              self_care = [
        "🫶 Talk to someone you trust.",
        "🎵 Listen to something comforting.",
        "📖 Read a book you enjoy.",
        "🌿 Spend some quiet time with yourself.",
        "☕ Have a warm drink and relax."
    ]

            elif mood == "Stressed":

             daily_tip = "😣 You don't have to handle everything at once. Take it one step at a time. 🌿"

             advice = "🧘‍♀️ Give yourself permission to pause. Focus on what you can do right now instead of everything at once. A small break can help you feel more balanced. 💚✨"

             self_care = [
             "🌬️ Take 5 slow, deep breaths.",
              "💧 Drink a glass of water.",
              "📵 Take a short break from your screen.",
              "🚶 Go for a short peaceful walk.",
               "🎵 Listen to some calming music."
    ]

            elif mood == "Neutral":

               daily_tip = "😐 Today is a fresh opportunity to try something new. ✨🌱"

               advice = "🌈 A neutral day doesn't have to stay the same. Give yourself a little spark by doing something different, creative, or enjoyable. 💚✨"

               self_care = [
        "🎨 Try a creative activity.",
        "🎵 Listen to a new song.",
        "🚶 Take a refreshing walk.",
        "📖 Read a few pages of a book.",
        "🌻 Do one small thing you've been putting off."
    ]

    return render_template(
        "daily_tips.html",
        daily_tip=daily_tip,
        advice=advice,
    self_care=self_care
    )
@app.route("/affirmations")
def affirmations():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT mood
        FROM journal
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 1
        """,
        (user_id,)
    )

    result = cursor.fetchone()

    conn.close()

    mood = result[0] if result else "Neutral"

    return render_template(
        "affirmations.html",
        mood=mood
    )
@app.route("/about")
def about():
    return render_template(
        "about.html",
        username=session.get("username")
    )
@app.route("/services")
def services():
    return render_template(
        "services.html",
        username=session.get("username")
    )
@app.route("/contact", methods=["GET", "POST"])
def contact():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    if request.method == "POST":

        name = request.form["name"]
        email = request.form["email"]
        subject = request.form["subject"]
        message = request.form["message"]

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute("""
    CREATE TABLE IF NOT EXISTS contact_messages (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        name VARCHAR(100) NOT NULL,
        email VARCHAR(150) NOT NULL,
        subject VARCHAR(200),
        message TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")

        cursor.execute("""
        INSERT INTO contact_messages
        (user_id, name, email, subject, message)
        VALUES (%s, %s, %s, %s, %s)
        """, (user_id, name, email, subject, message))

        conn.commit()
        conn.close()

        return render_template(
            "contact.html",
            username=session.get("username"),
            success="Your message has been sent successfully!"
        )

    return render_template(
        "contact.html",
        username=session.get("username")
    )
@app.route("/contact-messages")
def contact_messages():

    if "user_id" not in session:
        return redirect("/login")

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT email FROM users WHERE id = %s",
        (session["user_id"],)
    )

    user = cursor.fetchone()
    conn.close()

    # Check if the logged-in user is the admin
    if not user or user[0] != ADMIN_EMAIL:
        return "Access Denied ❌", 403

    # Admin can view all contact messages
    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT name, email, subject, message, created_at
        FROM contact_messages
        ORDER BY id DESC
    """)

    messages = cursor.fetchall()

    conn.close()

    return render_template(
        "contact_messages.html",
        messages=messages
    )
@app.route("/happy-wish")
def happy_wish():

    if "user_id" not in session:
        return redirect("/login")

    return render_template("happy_wish.html")
@app.route("/journal", methods=["GET", "POST"])
def journal():
    if "user_id" not in session:
      return redirect("/login")
    
    user_id = session["user_id"]

    if request.method == "POST":

        title = request.form["title"]
        journal = request.form["journal"]
        mood = request.form["mood"]
        date = datetime.now().strftime("%Y-%m-%d")

        try:

            conn = get_mysql_connection()
            cursor = conn.cursor()

            cursor.execute("""
    CREATE TABLE IF NOT EXISTS journal (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT,
        title VARCHAR(255),
        journal TEXT,
        mood VARCHAR(50),
        date DATE
    )
""")

            cursor.execute(
    "INSERT INTO journal(user_id, title, journal, mood, date) VALUES (%s, %s, %s, %s, %s)",
    (user_id, title, journal, mood, date)
)

            conn.commit()
            conn.close()

            return "Journal Saved Successfully! 🎉"

        except Exception as e:
            return f"Error: {e}"

    return render_template("journal.html")
@app.route("/register", methods=["GET", "POST"])

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"].strip()
        email = request.form["email"].strip()
        password = request.form["password"]

        error = None

        if len(password) < 8:
            error = "Password must contain at least 8 characters."
        elif not re.search(r"[A-Z]", password):
            error = "Password must contain at least one uppercase letter."
        elif not re.search(r"[a-z]", password):
            error = "Password must contain at least one lowercase letter."
        elif not re.search(r"[0-9]", password):
            error = "Password must contain at least one number."
        elif not re.search(r"[@#$%^&*!]", password):
            error = "Password must contain at least one special character."

        if error:
            return render_template("register.html", error=error)

        conn = None
        cursor = None

        try:
            conn = get_mysql_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT id FROM users WHERE email = %s",
                (email,)
            )

            if cursor.fetchone():
                return render_template(
                    "register.html",
                    error="This email is already registered. Please log in."
                )

            cursor.execute(
                "INSERT INTO users (name, email, password) "
                "VALUES (%s, %s, %s)",
                (username, email, password)
            )

            conn.commit()

        except mysql.connector.Error as e:
            if conn and conn.is_connected():
                conn.rollback()

            print("Registration database error:", repr(e))

            return render_template(
                "register.html",
                error="Registration could not be completed. Please try again."
            )

        finally:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()

        send_welcome_email(username, email)

        return render_template(
            "register_success.html",
            username=username,
            email=email
        )

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        email = request.form["email"]
        password = request.form["password"]

        conn = get_mysql_connection()
        cursor = conn.cursor()

        cursor.execute(
    "SELECT * FROM users WHERE email = %s AND password = %s",
    (email, password)
)

        user = cursor.fetchone()

        conn.close()

        if user:

           session["user_id"] = user[0]
           session["username"] = user[1]

           return redirect("/")

        else:

           return "Invalid Email or Password ❌"

    return render_template("login.html")

@app.route("/view-journals")
def view_journals():
    if "user_id" not in session:
     return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute(
    "SELECT * FROM journal WHERE user_id = %s",
    (user_id,))
    journals = cursor.fetchall()

    conn.close()

    return render_template("view_journals.html", journals=journals)
@app.route("/mood-analysis")
def mood_analysis():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
    SELECT mood, COUNT(*)
    FROM journal
    WHERE user_id = %s
    GROUP BY mood
    """, (user_id,))

    mood_counts = cursor.fetchall()
    
    cursor.execute(
    "SELECT mood FROM journal WHERE user_id = %s",
    (user_id,)
     )

    all_moods = cursor.fetchall()

    print("ALL MY MOODS:", all_moods)

    conn.close()

    if mood_counts:
      max_count = max(count for mood, count in mood_counts)
    else:
      max_count = 1

    mood_data = []

    for mood, count in mood_counts:
      percentage = (count / max_count) * 100
      mood_data.append((mood, count, percentage))

    return render_template(
    "mood_analysis.html",
    mood_data=mood_data
    )
@app.route("/mood-analysis/<mood>")
def selected_mood_analysis(mood):

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()

    # Count selected mood
    cursor.execute(
        """
        SELECT COUNT(*)
        FROM journal
        WHERE user_id = %s AND mood = %s
        """,
        (user_id, mood)
    )

    mood_count = cursor.fetchone()[0]

    # Find most frequently recorded mood
    cursor.execute(
        """
        SELECT mood, COUNT(*) as count
        FROM journal
        WHERE user_id = %s
        GROUP BY mood
        ORDER BY count DESC
        LIMIT 1
        """,
        (user_id,)
    )

    most_common = cursor.fetchone()

    conn.close()

    return render_template(
    "selected_mood.html",
    mood=mood,
    mood_count=mood_count,
    most_common=most_common

)
@app.route("/delete/<int:id>")
def delete_journal(id):
    if "user_id" not in session:
      return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM journal WHERE id = %s", (id,))

    conn.commit()
    conn.close()

    return redirect("/view-journals")
@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_journal(id):
    if "user_id" not in session:
      return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()

    if request.method == "POST":

        title = request.form["title"]
        journal = request.form["journal"]
        mood = request.form["mood"]

        cursor.execute("""
    UPDATE journal
    SET title = %s, journal = %s, mood = %s
    WHERE id = %s AND user_id = %s
    """, (title, journal, mood, id, user_id))

        conn.commit()
        conn.close()

        return redirect("/view-journals")

    cursor.execute(
    "SELECT * FROM journal WHERE id = %s AND user_id = %s",
    (id, user_id)
     )
    journal = cursor.fetchone()

    conn.close()

    return render_template("edit_journal.html", journal=journal)
@app.route("/mood-tracker")
def mood_tracker():

    if "user_id" not in session:
        return redirect("/login")

    user_id = session["user_id"]

    conn = get_mysql_connection()
    cursor = conn.cursor()
    cursor.execute(
    """
    SELECT mood, COUNT(*)
    FROM journal
    WHERE user_id = %s
    GROUP BY mood
    """,
    (user_id,)
)

    mood_data = cursor.fetchall()
    max_count = max([count for mood, count in mood_data], default=1)
    cursor.execute(
    """
    SELECT date, mood
    FROM journal
    WHERE user_id = %s AND date IS NOT NULL
    ORDER BY date
    """,
    (user_id,)
)

    mood_trend = cursor.fetchall()
    if mood_data:

        most_frequent_mood = max(
        mood_data,
        key=lambda x: x[1]
    )

        mood_insight = (
        f"{most_frequent_mood[0]} is your most frequently recorded mood. "
        f"You recorded it {most_frequent_mood[1]} times."
    )

    else:

       mood_insight = "Keep journaling to discover your mood patterns. 🌱"

    cursor.execute(
        """
        SELECT journal
        FROM journal
        WHERE user_id = %s
        """,
        (user_id,)
    )

    journals = cursor.fetchall()

    conn.close()

    positive_count = 0
    negative_count = 0
    neutral_count = 0

    for (journal,) in journals:

        sentiment = analyze_journal(journal)

        if sentiment == "Positive 😊":
            positive_count += 1

        elif sentiment == "Negative 😔":
            negative_count += 1

        else:
            neutral_count += 1

    if not journals:
        overall_sentiment = None

    elif positive_count > negative_count and positive_count > neutral_count:
        overall_sentiment = "Positive 😊"

    elif negative_count > positive_count and negative_count > neutral_count:
        overall_sentiment = "Negative 😔"

    else:
        overall_sentiment = "Neutral 😐"

    return render_template(
        "mood_tracker.html",
        overall_sentiment=overall_sentiment,
        positive_count=positive_count,
        negative_count=negative_count,
        neutral_count=neutral_count,
        mood_data=mood_data,
        max_count=max_count,
        mood_insight=mood_insight,
        mood_trend=mood_trend
    )
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/edit-notebook/<int:entry_id>", methods=["GET", "POST"])
def edit_notebook(entry_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_mysql_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT id, title, feelings
        FROM notebook_entries
        WHERE id = %s AND user_id = %s
    """, (entry_id, session["user_id"]))

    entry = cursor.fetchone()

    if entry is None:
        conn.close()
        return "Entry not found or access denied.", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        feelings = request.form.get("feelings", "").strip()

        if feelings:
            cursor.execute("""
               UPDATE notebook_entries
SET title = %s, feelings = %s
WHERE id = %s AND user_id = %s
            """, (
                title,
                feelings,
                entry_id,
                session["user_id"]
            ))

            conn.commit()
            conn.close()
            return redirect("/feelings-notebook")

    conn.close()

    return render_template(
        "edit_notebook.html",
        entry=entry
    )


@app.route("/delete-notebook/<int:entry_id>", methods=["POST"])
def delete_notebook(entry_id):

    if "user_id" not in session:
        return redirect("/login")

    conn = get_mysql_connection()
    conn.autocommit = False
    cursor = conn.cursor()
    

    cursor.execute("""
        DELETE FROM notebook_entries
WHERE id = %s AND user_id = %s
    """, (entry_id, session["user_id"]))

    conn.commit()
    conn.close()

    return redirect("/feelings-notebook")


    

if __name__ == "__main__":
    create_notebook_table()
    app.run(debug=True)
