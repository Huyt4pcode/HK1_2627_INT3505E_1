from flask import Blueprint, jsonify

from .users_data import get_user


bp = Blueprint("v1", __name__)


@bp.get("/users/<int:uid>")
def get_user_v1(uid: int):
    user = get_user(uid)
    if user is None:
        return jsonify(error="not_found"), 404

    return jsonify(
        id=user["id"],
        full_name=f'{user["first_name"]} {user["last_name"]}',
        email=user["email"],
    )
