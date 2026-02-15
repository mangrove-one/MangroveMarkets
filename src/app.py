"""MangroveMarkets application entrypoint."""
from flask import Flask

from src.shared.config import config
from src.shared.health import health_payload


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    @app.get("/health")
    def health():
        return health_payload(), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=config.MCP_PORT)
