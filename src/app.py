"""MangroveMarkets application entrypoint."""
import random

from flask import Flask, jsonify, render_template, request

from src.shared.config import app_config
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

    @app.post("/hello")
    def hello():
        """Hello world endpoint. POST a name, get a random number back."""
        data = request.get_json(silent=True) or {}
        name = data.get("name", "stranger")
        number = random.randint(1, 100)
        return jsonify({
            "name": name,
            "number": number,
            "message": f"Hello, {name}! Your random number is {number}.",
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=int(app_config.MCP_PORT))
