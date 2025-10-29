from flask import Blueprint, request, jsonify
from app.models import Todo, db

# ✅ ต้องมีบรรทัดนี้
main = Blueprint('main', __name__)


@main.route('/api/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    return jsonify([todo.to_dict() for todo in todos])


@main.route('/api/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({'error': 'Title is required'}), 400

    todo = Todo(
        title=data['title'],
        description=data.get('description'),
        completed=False,
    )
    db.session.add(todo)
    db.session.commit()
    return jsonify(todo.to_dict()), 201


@main.route('/api/todos/<int:todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404
    return jsonify(todo.to_dict())


@main.route('/api/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    data = request.get_json()
    todo.title = data.get('title', todo.title)
    todo.description = data.get('description', todo.description)
    todo.completed = data.get('completed', todo.completed)

    db.session.commit()
    return jsonify(todo.to_dict())


@main.route('/api/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({'error': 'Todo not found'}), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({'message': 'Todo deleted'})
