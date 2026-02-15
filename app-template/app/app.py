from flask import Flask

from app_core.config import app_config
from app_core.routes.hello_routes import hello_bp
from app_core.health import health_payload


def create_app() -> Flask:
    app = Flask(__name__)

    # Force config load on startup
    _ = app_config.ENVIRONMENT

    app.register_blueprint(hello_bp, url_prefix="/api")

    @app.get("/health")
    def health():
        return health_payload(), 200

    return app


if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=8080)
