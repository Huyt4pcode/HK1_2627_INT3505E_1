USERS = {
    1: {
        "id": 1,
        "first_name": "Đào",
        "last_name": "Huy",
        "email": "12345ljjkg@example.com",
    },
    42: {
        "id": 42,
        "first_name": "Vũ",
        "last_name": "Đức An",
        "email": "an@example.com",
    },
}


def get_user(uid: int) -> dict | None:
    return USERS.get(uid)
