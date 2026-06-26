# TaskFlow - Personal Task Manager

#### Video Demo: <URL HERE>

#### Description:

TaskFlow is a web-based personal task management application built with Python, Flask, SQL, and Bootstrap. It allows users to create accounts, manage their daily tasks, organize them by category and priority, mark them as complete, and review their productivity history. The goal of the project is to provide a clean, intuitive, and functional tool for staying organized.

## Features

- **User authentication**: Secure registration and login with hashed passwords using Werkzeug's `generate_password_hash` and `check_password_hash`. Each user's data is completely private and isolated from other users.
- **Task creation**: Users can add tasks with a title, an optional description, a category (free-form text such as "Work" or "Personal"), a priority level (low, medium, or high), and an optional due date.
- **Task editing**: Any existing pending task can be edited at any time to update its details.
- **Task completion**: Tasks can be marked as complete with a single click. Completed tasks are moved out of the main view and into the history page, along with the timestamp of completion.
- **Task deletion**: Tasks can be deleted permanently from both the pending list and the history view.
- **Filtering**: The main task list can be filtered by category and priority level, making it easy to focus on what matters most at any given moment.
- **Priority sorting**: Tasks are automatically sorted by priority (high → medium → low) and then by creation date, so the most urgent items always appear first.
- **Statistics**: The home page displays a count of pending and completed tasks at a glance.
- **History**: A dedicated page shows all completed tasks in reverse chronological order.
- **Password change**: Users can change their password from the account dropdown menu.

## File Structure

### `app.py`
The main application file. Contains all Flask routes and the application logic:
- `/` — Home page with the task list, filters, and stats.
- `/add` — Form to create a new task.
- `/edit/<id>` — Form to edit an existing task.
- `/complete/<id>` — POST endpoint to mark a task as done.
- `/delete/<id>` — POST endpoint to delete a task.
- `/history` — View of all completed tasks.
- `/register`, `/login`, `/logout` — Authentication routes.
- `/change_password` — Lets users update their password.

### `schema.sql`
SQL schema for the database, defining the `users` and `tasks` tables with appropriate types, defaults, foreign keys, and indexes.

### `project.db`
SQLite database file containing all application data. Generated automatically on first run.

### `templates/`
All Jinja2 HTML templates:
- `layout.html` — Base template with navbar and flash message support.
- `index.html` — Main task list with filter controls and task cards.
- `add.html` — New task form.
- `edit.html` — Edit task form (pre-filled with current values).
- `history.html` — Completed tasks table.
- `login.html` / `register.html` — Authentication forms.
- `apology.html` — Generic error page.
- `change_password.html` — Password change form.

### `static/styles.css`
Custom CSS for minor styling adjustments on top of Bootstrap 5.

### `requirements.txt`
Python package dependencies: `cs50`, `Flask`, `Flask-Session`, `Werkzeug`.

## Design Decisions

**Why Flask + CS50 SQL?** The course's tooling was already familiar and well-suited for a project of this scope. Using `cs50.SQL` keeps the database interaction straightforward and readable without the overhead of a full ORM.

**Why free-form categories instead of a fixed list?** Letting users type their own category names (e.g., "UAB", "Gym", "Side Project") is more flexible than forcing them to pick from a predefined set. A dropdown could be added in the future based on the user's own past categories.

**Why store completed tasks in the same table?** Using a single `tasks` table with a `completed` boolean and a `completed_at` timestamp avoids duplication and makes queries simpler. The trade-off is that the main query always needs a `WHERE completed = 0` filter, which is handled consistently throughout.

**Why sort by priority first?** The primary use case is "what should I work on right now?" — so surfacing high-priority tasks at the top is more actionable than sorting purely by creation date.

## How to Run

```bash
cd project
pip install -r requirements.txt
flask run
```

Then open the URL shown in the terminal. Register an account and start adding tasks.
