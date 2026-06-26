import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from functools import wraps

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-prod")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Use absolute path so it works on any server
DB_PATH = os.path.join(os.path.dirname(__file__), "project.db")
if not os.path.exists(DB_PATH):
    open(DB_PATH, "w").close()

db = SQL(f"sqlite:///{DB_PATH}")

# Create tables if they don't exist
db.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
)""")
db.execute("""CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    description TEXT,
    category TEXT,
    priority TEXT NOT NULL DEFAULT 'medium',
    due_date TEXT,
    completed INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    completed_at DATETIME,
    FOREIGN KEY(user_id) REFERENCES users(id)
)""")


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def apology(message, code=400):
    return render_template("apology.html", message=message), code


@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    user_id = session["user_id"]
    category = request.args.get("category", "all")
    priority = request.args.get("priority", "all")

    query = "SELECT * FROM tasks WHERE user_id = ? AND completed = 0"
    params = [user_id]

    if category != "all":
        query += " AND category = ?"
        params.append(category)
    if priority != "all":
        query += " AND priority = ?"
        params.append(priority)

    query += " ORDER BY CASE priority WHEN 'high' THEN 1 WHEN 'medium' THEN 2 WHEN 'low' THEN 3 END, created_at DESC"

    tasks = db.execute(query, *params)
    categories = db.execute("SELECT DISTINCT category FROM tasks WHERE user_id = ? AND category IS NOT NULL", user_id)
    total = db.execute("SELECT COUNT(*) AS n FROM tasks WHERE user_id = ? AND completed = 0", user_id)[0]["n"]
    done = db.execute("SELECT COUNT(*) AS n FROM tasks WHERE user_id = ? AND completed = 1", user_id)[0]["n"]

    return render_template("index.html", tasks=tasks, categories=categories,
                           selected_category=category, selected_priority=priority,
                           total=total, done=done)


@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "medium")
        due_date = request.form.get("due_date", "").strip()

        if not title:
            return apology("Task title is required", 400)
        if priority not in ("low", "medium", "high"):
            return apology("Invalid priority", 400)

        db.execute(
            "INSERT INTO tasks (user_id, title, description, category, priority, due_date) VALUES (?, ?, ?, ?, ?, ?)",
            session["user_id"], title,
            description or None,
            category or None,
            priority,
            due_date or None
        )
        flash("Task added!")
        return redirect("/")
    return render_template("add.html")


@app.route("/edit/<int:task_id>", methods=["GET", "POST"])
@login_required
def edit(task_id):
    task = db.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", task_id, session["user_id"])
    if not task:
        return apology("Task not found", 404)
    task = task[0]

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        category = request.form.get("category", "").strip()
        priority = request.form.get("priority", "medium")
        due_date = request.form.get("due_date", "").strip()

        if not title:
            return apology("Task title is required", 400)

        db.execute(
            "UPDATE tasks SET title=?, description=?, category=?, priority=?, due_date=? WHERE id=? AND user_id=?",
            title, description or None, category or None, priority, due_date or None,
            task_id, session["user_id"]
        )
        flash("Task updated!")
        return redirect("/")
    return render_template("edit.html", task=task)


@app.route("/complete/<int:task_id>", methods=["POST"])
@login_required
def complete(task_id):
    db.execute(
        "UPDATE tasks SET completed=1, completed_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?",
        task_id, session["user_id"]
    )
    flash("Task completed!")
    return redirect("/")


@app.route("/delete/<int:task_id>", methods=["POST"])
@login_required
def delete(task_id):
    db.execute("DELETE FROM tasks WHERE id=? AND user_id=?", task_id, session["user_id"])
    flash("Task deleted.")
    return redirect(request.referrer or "/")


@app.route("/history")
@login_required
def history():
    tasks = db.execute(
        "SELECT * FROM tasks WHERE user_id=? AND completed=1 ORDER BY completed_at DESC",
        session["user_id"]
    )
    return render_template("history.html", tasks=tasks)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        if not username:
            return apology("Username required", 400)
        if not password:
            return apology("Password required", 400)
        if password != confirmation:
            return apology("Passwords do not match", 400)

        try:
            db.execute("INSERT INTO users (username, hash) VALUES (?, ?)",
                       username, generate_password_hash(password))
        except ValueError:
            return apology("Username already exists", 400)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        session["user_id"] = rows[0]["id"]
        flash("Registered successfully!")
        return redirect("/")
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username:
            return apology("Username required", 403)
        if not password:
            return apology("Password required", 403)

        rows = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], password):
            return apology("Invalid username and/or password", 403)

        session["user_id"] = rows[0]["id"]
        return redirect("/")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        current = request.form.get("current_password", "")
        new = request.form.get("new_password", "")
        confirm = request.form.get("confirm_password", "")

        row = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])
        if not check_password_hash(row[0]["hash"], current):
            return apology("Current password incorrect", 400)
        if not new:
            return apology("New password required", 400)
        if new != confirm:
            return apology("Passwords do not match", 400)

        db.execute("UPDATE users SET hash=? WHERE id=?",
                   generate_password_hash(new), session["user_id"])
        flash("Password changed successfully!")
        return redirect("/")
    return render_template("change_password.html")
