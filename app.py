from flask import Flask, render_template, request, redirect, url_for, session
import psycopg2
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = "your_secret_key"
bcrypt = Bcrypt(app)

# Database connection function
def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        user="jialihuang",
        password="yourpassword",
        dbname="my_local_db"
    )

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("todo"))  # Redirect to To-Do page if logged in
    return redirect(url_for("login"))  # Redirect to Login page if not logged in

@app.route("/todo", methods=["GET", "POST"])
def todo():
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()

    if request.method == "POST":
        task = request.form["task"].strip()
        if task:
            cur.execute("SELECT COUNT(*) FROM tasks WHERE user_id = %s AND task = %s", (session["user_id"], task))
            if cur.fetchone()[0] == 0:
                cur.execute("INSERT INTO tasks (user_id, task) VALUES (%s, %s)", (session["user_id"], task))
                conn.commit()

        return redirect(url_for("todo"))

    # Fetch tasks for the logged-in user
    cur.execute("SELECT id, task FROM tasks WHERE user_id = %s ORDER BY id ASC", (session["user_id"],))
    tasks = cur.fetchall()

    # Fetch quotes
    cur.execute("SELECT id, quote, emoji FROM quotes ORDER BY id ASC")
    quotes = cur.fetchall()

    # Count quotes
    cur.execute("SELECT COUNT(*) FROM quotes")
    quote_count = cur.fetchone()[0]

    cur.close()
    conn.close()

    return render_template("todo.html", tasks=tasks, quotes=quotes, quote_count=quote_count)

@app.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM tasks WHERE id = %s AND user_id = %s", (task_id, session["user_id"]))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("todo"))

@app.route("/add_quote", methods=["POST"])
def add_quote():
    quote = request.form["quote"].strip()
    emoji = request.form["emoji"].strip() or "💬"

    if quote:
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("INSERT INTO quotes (quote, emoji) VALUES (%s, %s)", (quote, emoji))
        conn.commit()
        cur.close()
        conn.close()

    return redirect(url_for("todo"))

@app.route("/delete_quote/<int:quote_id>", methods=["POST"])
def delete_quote(quote_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM quotes WHERE id = %s", (quote_id,))
    conn.commit()
    cur.close()
    conn.close()

    return redirect(url_for("todo"))

# 🟢 LOGIN ROUTE
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db_connection()
        cur = conn.cursor()

        # Check if user exists
        cur.execute("SELECT id, password FROM users WHERE username = %s", (username,))
        user = cur.fetchone()

        if user and bcrypt.check_password_hash(user[1], password):
            session["user_id"] = user[0]
            return redirect(url_for("todo"))  # Redirect to To-Do page

        cur.close()
        conn.close()
        return render_template("login.html", error="Invalid username or password")

    return render_template("login.html")

# 🟢 LOGOUT ROUTE
@app.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = bcrypt.generate_password_hash(request.form["password"]).decode("utf-8")

        conn = get_db_connection()
        cur = conn.cursor()

        try:
            cur.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (username, password))
            conn.commit()
            return redirect(url_for("login"))  # Redirect to login after registering
        except psycopg2.errors.UniqueViolation:
            return render_template("register.html", error="Username already taken")

        cur.close()
        conn.close()

    return render_template("register.html")

if __name__ == "__main__":
    app.run(debug=True)
