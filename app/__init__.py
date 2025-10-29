from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from app.config import config
from app.logging_config import setup_logging

db = SQLAlchemy()
migrate = Migrate()


def create_app(config_name='default'):
    """Application factory pattern"""
    app = Flask(__name__)
    app.config.from_object(config[config_name])

    # Setup CORS
    CORS(app)

    # Initialize logging
    logger = setup_logging(app)
    logger.info(f"Starting Flask App with config: {config_name}")

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)

    # Register Blueprints
    from app.routes import main
    app.register_blueprint(main)

    # Error Handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Resource not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Internal server error"}), 500

    @app.route('/api/health')
    def health_check():
        """Simple health check endpoint"""
        return jsonify({"status": "ok"}), 200

    return app
