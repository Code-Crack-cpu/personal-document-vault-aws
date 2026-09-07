from app.db import execute, fetch_one


def create_user(name, email, password_hash):
    return execute(
        "INSERT INTO users (name, email, password_hash) VALUES (%s, %s, %s)",
        (name, email, password_hash),
    )


def find_by_email(email):
    return fetch_one("SELECT * FROM users WHERE email = %s", (email,))


def find_by_id(user_id):
    return fetch_one(
        "SELECT id, name, email, created_at FROM users WHERE id = %s",
        (user_id,),
    )
