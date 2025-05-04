from connections import create_connection

def login(username, password):
    conn, error = create_connection()  # ✅ Unpack the tuple properly
    if error or not conn:
        print(f"❌ Database connection failed: {error}")
        return None, None

    try:
        cur = conn.cursor()
        query = """
            SELECT u.user_id, u.username, r.role_name
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            WHERE u.username = %s AND u.password = %s
        """
        cur.execute(query, (username, password))
        result = cur.fetchone()
        conn.close()

        if result:
            user_id, username, role = result
            return username, role
        else:
            print("❌ Invalid username or password.")
            return None, None

    except Exception as e:
        print("❌ Query error:", e)
        conn.close()
        return None, None
