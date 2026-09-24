from pathlib import Path

from flask import Flask

ROOT = Path(__file__).resolve().parent.parent


def create_app():
    app = Flask(
        __name__,
        template_folder=str(ROOT / "templates"),
        static_folder=str(ROOT / "static"),
    )

    from webapp.routes import register_routes

    register_routes(app)
    return app


app = create_app()