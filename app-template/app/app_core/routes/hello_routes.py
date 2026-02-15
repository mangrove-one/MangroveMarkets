from flask import Blueprint, request

from app_core.services.hello_service import guess_age_for_name, get_guess_for_name
from app_core.utils.auth.middleware import auth_required

hello_bp = Blueprint("hello", __name__)


@hello_bp.post("/guess")
@auth_required
def create_guess():
    payload = request.get_json(silent=True) or {}
    name = (payload.get("name") or "").strip()
    if not name:
        return {"error": "name_required"}, 400

    guess = guess_age_for_name(name)
    return {"name": name, "age_guess": guess}, 201


@hello_bp.get("/guess/<name>")
@auth_required
def get_guess(name: str):
    guess = get_guess_for_name(name)
    if guess is None:
        return {"error": "not_found"}, 404
    return {"name": name, "age_guess": guess}, 200
