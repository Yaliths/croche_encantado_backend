# CRUD

from models import User


def create_user(user: User, conn):
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (name, email, password) VALUES (%s, %s, %s)",
        (user.name, user.email, user.password),
    )
    conn.commit()


def get_all_users(conn) -> list[User]:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users")
    rows = cur.fetchall()
    users = []
    for row in rows:
        user = User(row[0], row[1], row[2])
        users.append(user)
    return users


def edit_user(updates: dict, user: User, conn):
    cur = conn.cursor()
    fields = []
    values = []

    for key, value in updates.items():
        fields.append(f"{key} = %s")
        values.append(value)

    cur.execute(
        f"UPDATE users SET {','.join(fields)} WHERE userid = %s",
        (*values, user.userid),
    )

    conn.commit()

def delete_user(user: User, conn):
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM users WHERE userid = %s",
        (user.userid,),
    )
    conn.commit()

def get_user_by_email(conn, email: str) -> User:
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    row = cur.fetchone()
    if row:
        return User(row[0], row[1], row[2])
    return None