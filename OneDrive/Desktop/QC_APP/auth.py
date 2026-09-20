import email

from database import get_connection


def login(email, password):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT role
        FROM accounts
        WHERE email = ?
        AND password = ?
        """,
        (email, password)
    )

    user = cursor.fetchone()

    conn.close()

    return user
