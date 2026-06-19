from flask import Flask, render_template, request, redirect, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.secret_key = "smarttaskmanager"

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///taskmanager.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()

def get_ai_suggestion(priority):

    if priority == "High":
        return "🔥 Complete this task first"

    elif priority == "Medium":
        return "⚡ Work on this soon"

    else:
        return "✅ Can be done later"


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    username = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(100))


class Task(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(100))

    priority = db.Column(db.String(20))

    deadline = db.Column(db.String(50))

    status = db.Column(db.String(20), default="Pending")

    suggestion = db.Column(db.String(200))


@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        existing_user = User.query.filter_by(
            username=username
        ).first()

        if existing_user:
            return "Username already exists"

        user = User(
            username=username,
            password=password
        )

        db.session.add(user)
        db.session.commit()

        return redirect('/login')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        username = request.form['username']

        password = request.form['password']

        user = User.query.filter_by(
            username=username,
            password=password
        ).first()

        if user:

            session['user'] = username

            return redirect('/')

    return render_template('login.html')


@app.route('/logout')
def logout():

    session.pop('user', None)

    return redirect('/login')


@app.route('/')
def dashboard():

    if 'user' not in session:
        return redirect('/login')

    tasks = Task.query.all()

    total = len(tasks)

    completed = len(
        [t for t in tasks if t.status == "Completed"]
    )

    pending = total - completed

    if pending > 0:

        high_tasks = [
            t for t in tasks
            if t.priority == "High"
            and t.status == "Pending"
        ]

        if high_tasks:
            ai_message = f'🔥 Complete "{high_tasks[0].title}" first.'

        else:
            ai_message = "⚡ Finish pending tasks."

    else:
        ai_message = "🎉 Excellent! All tasks completed."

    return render_template(
        'dashboard.html',
        tasks=tasks,
        total=total,
        completed=completed,
        pending=pending,
        ai_message=ai_message
    )


@app.route('/add', methods=['GET', 'POST'])
def add_task():

    if request.method == 'POST':

        title = request.form['title']

        priority = request.form['priority']

        deadline = request.form['deadline']

        task = Task(
            title=title,
            priority=priority,
            deadline=deadline,
            suggestion=get_ai_suggestion(priority)
        )

        db.session.add(task)

        db.session.commit()

        return redirect('/')

    return render_template('add_task.html')


@app.route('/complete/<int:id>')
def complete(id):

    task = Task.query.get(id)

    task.status = "Completed"

    db.session.commit()

    return redirect('/')


@app.route('/delete/<int:id>')
def delete(id):

    task = Task.query.get(id)

    db.session.delete(task)

    db.session.commit()

    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)
