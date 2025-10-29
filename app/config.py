import os
from dotenv import load_dotenv

load_dotenv()

def fix_postgres_url(url):
    """Convert postgres:// to postgresql:// for SQLAlchemy (Railway compatibility)"""
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url

class Config:
    """Base configuration class"""
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    """Development configuration (runs on your Mac)"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = fix_postgres_url(os.getenv(
        'DATABASE_URL',
        # ✅ default to localhost (for local PostgreSQL)
        'postgresql://postgres:postgres@localhost:5432/todo_dev'
    ))

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

class ProductionConfig(Config):
    """Production configuration (for Railway / Docker)"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = fix_postgres_url(os.getenv('DATABASE_URL'))

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        assert os.getenv('DATABASE_URL'), 'DATABASE_URL must be set in production'

config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
