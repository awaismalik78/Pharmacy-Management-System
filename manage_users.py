from connections import create_connection

def fetch_all_users():
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT u.user_id, u.username, r.role_name, u.created_at
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                ORDER BY u.user_id
            """)
            users = cur.fetchall()
            conn.close()
            return users
        except Exception as e:
            print("❌ Error fetching users:", e)
            conn.close()
            return []

def add_user(username, password, role_id):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO users (username, password, role_id)
                VALUES (%s, %s, %s)
            """, (username, password, role_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("❌ Error adding user:", e)
            conn.close()
            return False

def delete_user(user_id):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("❌ Error deleting user:", e)
            conn.close()
            return False
