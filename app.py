import os
from flask import Flask, request, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Configure the database connection from an environment variable
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    raise RuntimeError("DATABASE_URL environment variable not set.")

# Heroku/Azure PostgreSQL uses 'postgres://' but SQLAlchemy needs 'postgresql://'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- Database Model ---
class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    completed = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        """Serializes the object to a dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "completed": self.completed
        }

# --- Database Initialization ---
def init_db():
    """Initializes the database and creates tables."""
    with app.app_context():
        db.create_all()

# Run the DB initialization
init_db()

# --- API Endpoints ---

@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    """Fetches all tasks from the database."""
    tasks = Task.query.all()
    return jsonify([task.to_dict() for task in tasks])

@app.route('/api/tasks', methods=['POST'])
def create_task():
    """Creates a new task."""
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({"error": "Title is required"}), 400
    
    new_task = Task(title=data['title'], completed=False)
    db.session.add(new_task)
    db.session.commit()
    
    return jsonify(new_task.to_dict()), 201

@app.route('/api/tasks/<int:id>', methods=['PUT'])
def update_task(id):
    """Toggles the completed status of a task."""
    task = db.session.get(Task, id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    task.completed = not task.completed
    db.session.commit()
    
    return jsonify(task.to_dict())

@app.route('/api/tasks/<int:id>', methods=['DELETE'])
def delete_task(id):
    """Deletes a task."""
    task = db.session.get(Task, id)
    if not task:
        return jsonify({"error": "Task not found"}), 404
        
    db.session.delete(task)
    db.session.commit()
    
    return jsonify({"success": True, "message": "Task deleted"})

# --- Frontend Serving ---

@app.route('/')
def index():
    """Serves the main index.html file."""
    # Assumes index.html is in a 'templates' folder
    return render_template('index.html')

if __name__ == '__main__':
    # This is for local development, not for production
    app.run(debug=True)
