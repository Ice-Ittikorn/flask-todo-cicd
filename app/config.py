from dotenv import load_dotenv
import os

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv()


def fix_postgres_url(url):
    """Convert postgres:// to postgresql:// for SQLAlchemy"""
    if url and url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Config:
    SQLALCHEMY_DATABASE_URI = fix_postgres_url(
        os.getenv("DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'data.db')}")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = fix_postgres_url(
        os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@db:5432/todo_dev')
    )


class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    """Production configuration"""
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
