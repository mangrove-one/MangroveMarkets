"""MangroveMarkets application entrypoint."""
from flask import Flask, render_template

from src.shared.config import config
from src.shared.health import health_payload


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    @app.get("/")
    def index():
        """Serve the landing page."""
        return render_template("index.html")

    @app.get("/health")
    def health():
        """Health check endpoint."""
        return health_payload(), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=config.MCP_PORT)
