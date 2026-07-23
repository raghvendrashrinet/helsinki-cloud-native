import os
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Fetch database URL from environment variables
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
    'DATABASE_URL', 
    'postgresql://todo_user:todo_password@postgres-svc:5432/todo_db'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Todo Model
class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(255), nullable=False)

@app.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.content for todo in todos]), 200

@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json() or request.form
    new_content = data.get("content")
    
    if new_content:
        new_todo = Todo(content=new_content)
        db.session.add(new_todo)
        db.session.commit()
        
        todos = Todo.query.all()
        return jsonify([todo.content for todo in todos]), 201
    
    return jsonify({"error": "Content required"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
