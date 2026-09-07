from app.db import execute, fetch_all, fetch_one


def create_document(user_id, name, category, object_key, content_type, file_size):
    return execute(
        """
        INSERT INTO documents
            (user_id, name, category, object_key, content_type, file_size)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (user_id, name, category, object_key, content_type, file_size),
    )


def list_for_user(user_id, search="", category=""):
    query = """
        SELECT id, name, category, content_type, file_size, created_at
        FROM documents
        WHERE user_id = %s
    """
    params = [user_id]
    if search:
        query += " AND name LIKE %s"
        params.append(f"%{search}%")
    if category:
        query += " AND category = %s"
        params.append(category)
    query += " ORDER BY created_at DESC"
    return fetch_all(query, tuple(params))


def recent_for_user(user_id, limit=5):
    return fetch_all(
        """
        SELECT id, name, category, created_at
        FROM documents
        WHERE user_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (user_id, limit),
    )


def categories_for_user(user_id):
    return fetch_all(
        """
        SELECT category, COUNT(*) AS total
        FROM documents
        WHERE user_id = %s
        GROUP BY category
        ORDER BY total DESC, category ASC
        """,
        (user_id,),
    )


def find_for_user(document_id, user_id):
    return fetch_one(
        "SELECT * FROM documents WHERE id = %s AND user_id = %s",
        (document_id, user_id),
    )


def delete_for_user(document_id, user_id):
    return execute(
        "DELETE FROM documents WHERE id = %s AND user_id = %s",
        (document_id, user_id),
    )
