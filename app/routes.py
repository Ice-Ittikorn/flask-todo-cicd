from flask import Blueprint, jsonify, request
from app.models import db, Todo

# ✅ ใช้ชื่อ api ให้ตรงกับ import ใน __init__.py
api = Blueprint('api', __name__)


@api.route('/')
def root():
    return jsonify({"message": "Welcome to Flask TODO API"}), 200

@api.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    try:
        db.session.execute("SELECT 1")
        return jsonify({"status": "ok"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# ✅ CRUD Routes for Todos
@api.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos]), 200


@api.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict()), 200


@api.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    try:
        todo = Todo(
            title=data['title'],
            description=data.get('description'),
            completed=data.get('completed', False)
        )
        db.session.add(todo)
        db.session.commit()
        return jsonify(todo.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': 'Database error', 'message': str(e)}), 500


@api.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    data = request.get_json()
    todo.title = data.get('title', todo.title)
    todo.description = data.get('description', todo.description)
    todo.completed = data.get('completed', todo.completed)

    db.session.commit()
    return jsonify(todo.to_dict()), 200


@api.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'}), 200
