# webapp/__init__.py
from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_mapping(
        SECRET_KEY="change-me",  # replace in production
    )

    # Register blueprints
    from .routes import bp as main_bp
    app.register_blueprint(main_bp)

    return app
