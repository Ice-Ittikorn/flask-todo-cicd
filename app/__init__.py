import os
from flask import Flask, jsonify
from flask_cors import CORS
from app.models import db
from app.routes import api
from app.config import config


def create_app(config_name=None):
    """Flask Application Factory"""
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')

    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # ✅ Enable CORS for local + GitHub Pages + Railway
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                "http://localhost:3000",
                "http://127.0.0.1:3000",
                "https://*.github.io",
                "https://your-username.github.io",
                "https://*.railway.app"
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type"],
        }
    })

    # ✅ Initialize Database
    db.init_app(app)

    # ✅ Register API Blueprint
    app.register_blueprint(api, url_prefix="/api")

    # ✅ Root endpoint (for quick info)
    @app.route('/')
    def index():
        return jsonify({
            'message': 'Flask Todo API',
            'version': '1.0.0',
            'status': 'running',
            'endpoints': {
                'health': '/api/health',
                'todos': '/api/todos'
            }
        })

    # ✅ Health check endpoint (used by CI/CD & Railway)
    @app.route('/api/health', methods=['GET'])
    def health_check():
        try:
            db.session.execute("SELECT 1")
            db_status = True
        except Exception as e:
            print(f"[HealthCheck] DB connection error: {e}")
            db_status = False

        return jsonify({
            'status': 'ok' if db_status else 'degraded',
            'database': db_status
        }), 200 if db_status else 503

    # ✅ Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return jsonify({'error': 'Internal server error'}), 500

    @app.errorhandler(Exception)
    def handle_exception(error):
        db.session.rollback()
        return jsonify({'error': str(error)}), 500

    # ✅ Auto-create database tables
    with app.app_context():
        db.create_all()

    return app


# ✅ Entry point for Railway or local dev
if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_ENV") == "development")
