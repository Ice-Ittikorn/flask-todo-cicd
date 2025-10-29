from flask import Blueprint, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from app.models import db, Todo

api = Blueprint('api', __name__)


@api.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # ✅ ลองเชื่อมต่อฐานข้อมูล ถ้าไม่มีปัญหาคืน 200
        db.session.execute("SELECT 1")
        db.session.commit()

        return jsonify({
            "status": "healthy",
            "database": "connected"
        }), 200

    except Exception as e:
        # ✅ คืน 503 ถ้า database ใช้งานไม่ได้
        db.session.rollback()
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }), 503


@api.route('/todos', methods=['GET'])
def get_todos():
    todos = Todo.query.all()
    todos_data = [todo.to_dict() for todo in todos]
    return jsonify({
        "success": True,
        "count": len(todos_data),
        "data": todos_data
    }), 200


@api.route('/todos/<int:todo_id>', methods=['GET'])
def get_todo_by_id(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({
            "success": False,
            "error": "Todo not found"
        }), 404
    return jsonify({
        "success": True,
        "data": todo.to_dict()
    }), 200


@api.route('/todos', methods=['POST'])
def create_todo():
    data = request.get_json()
    if not data or 'title' not in data:
        return jsonify({
            "success": False,
            "error": "Title is required"
        }), 400

    try:
        todo = Todo(
            title=data['title'],
            description=data.get('description', ''),  # ✅ ใช้ '' แทน None
            completed=data.get('completed', False)
        )
        db.session.add(todo)
        db.session.commit()
        return jsonify({
            "success": True,
            "message": "Todo created successfully",
            "data": todo.to_dict()
        }), 201

    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({
            "success": False,
            "error": "Database error",
            "message": str(e)
        }), 500


@api.route('/todos/<int:todo_id>', methods=['PUT'])
def update_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({
            "success": False,
            "error": "Todo not found"
        }), 404

    data = request.get_json()
    todo.title = data.get('title', todo.title)
    todo.description = data.get('description', todo.description)
    todo.completed = data.get('completed', todo.completed)

    db.session.commit()
    return jsonify({
        "success": True,
        "data": todo.to_dict()
    }), 200


@api.route('/todos/<int:todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    todo = Todo.query.get(todo_id)
    if not todo:
        return jsonify({
            "success": False,
            "error": "Todo not found"
        }), 404

    db.session.delete(todo)
    db.session.commit()
    return jsonify({
        "success": True,
        "message": "Todo deleted"
    }), 200
