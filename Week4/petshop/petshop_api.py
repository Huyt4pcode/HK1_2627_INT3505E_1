from __future__ import annotations

from flask import Flask, jsonify, request

app = Flask(__name__)

pets = [
    {"id": 1, "name": "LuLu", "tag": "dog"},
    {"id": 2, "name": "Milo", "tag": "cat"},
]
next_id = 3


def error_response(code: int, message: str):
    return jsonify({"code": code, "message": message}), code


def require_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return False
    token = auth_header.split(" ", 1)[1].strip()
    return bool(token)


@app.before_request
def check_auth():
    if request.path.startswith("/v1") and request.method in {"GET", "POST", "DELETE"}:
        if not require_bearer_token():
            return error_response(401, "Token không hợp lệ hoặc bị thiếu")


@app.route("/v1/pets", methods=["GET"])
def listPets():
    limit = request.args.get("limit", default=10, type=int)
    if limit <= 0:
        limit = 10
    return jsonify(pets[:limit]), 200


@app.route("/v1/pets", methods=["POST"])
def createPets():
    global next_id

    payload = request.get_json(silent=True) or {}
    if not isinstance(payload, dict):
        return error_response(422, "Dữ liệu đầu vào không hợp lệ")

    name = payload.get("name")
    if not isinstance(name, str) or not name.strip():
        return error_response(422, "Trường 'name' là bắt buộc")

    pet = {"id": next_id, "name": name.strip()}
    if "tag" in payload:
        tag = payload.get("tag")
        if not isinstance(tag, str):
            return error_response(422, "Trường 'tag' phải là chuỗi")
        pet["tag"] = tag

    next_id += 1
    pets.append(pet)
    return jsonify(pet), 201


@app.route("/v1/pets/<int:petId>", methods=["GET"])
def showPetById(petId: int):
    for pet in pets:
        if pet["id"] == petId:
            return jsonify(pet), 200
    return error_response(404, "Không tìm thấy thông tin")


@app.route("/v1/pets/<int:petId>", methods=["DELETE"])
def deletePet(petId: int):
    for index, pet in enumerate(pets):
        if pet["id"] == petId:
            pets.pop(index)
            return "", 204
    return error_response(404, "Không tìm thấy thông tin")


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
