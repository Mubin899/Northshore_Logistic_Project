from database import get_connection, hash_password

def seed_users():
    conn = get_connection()
    if conn:
        cursor = conn.cursor()

        users_to_seed = [
            ("admin", "admin", "Admin"),
            ("manager", "admin", "Manager"),
            ("warehouse1", "admin", "Warehouse Staff"),
            ("dispatcher1", "admin", "Dispatcher")
        ]

        for username, password, role in users_to_seed:
            hashed_password = hash_password(password)
            try:
                cursor.execute("INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
                               (username, hashed_password, role))
                print(f"User created: {username} with role {role}")
            except Exception as e:
                print(f"User {username} already exists: {e}")

        conn.commit()
        conn.close()

if __name__ == "__main__":
    seed_users()