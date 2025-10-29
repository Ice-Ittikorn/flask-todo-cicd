import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.models import db
from app.routes import api
from app.config import config


def create_app(config_name=None):
    """Application factory pattern"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # ✅ Enable CORS for GitHub Pages and local dev
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://localhost:5000",
                "https://*.github.io",
                "https://your-username.github.io"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"],
            "supports_credentials": False
        }
    })

    # ✅ Initialize database
    db.init_app(app)

    # ✅ Register API Blueprint
    app.register_blueprint(api, url_prefix='/api')

    # ✅ Root endpoint
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Flask Todo API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'todos': '/api/todos'
            }
        })

    # ✅ Health check endpoint (used by CI/CD + Railway)
    @app.route('/api/health', methods=['GET'])
    def health_check():
        try:
            # ลองเชื่อมต่อฐานข้อมูลเพื่อดูว่าทำงานได้ไหม
            db.session.execute("SELECT 1")
            return jsonify({
                'status': 'ok',
                'database': True
            }), 200
        except Exception as e:
            return jsonify({
                'status': 'error',
                'database': False,
                'error': str(e)
            }), 503

    # ✅ Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 'Resource not found'
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500

    # ✅ Auto create tables if not exist
    with app.app_context():
        db.create_all()

    return app


# ✅ Entry point for Railway
if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))  # Railway จะส่ง PORT มาใน env
    app.run(host="0.0.0.0", port=port)
