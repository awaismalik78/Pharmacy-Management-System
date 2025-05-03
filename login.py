from connections import create_connection

def login(username, password):
    conn = create_connection()
    if conn:
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
                
                return username, role  # ✅ Return both
            else:
                print("❌ Invalid username or password.")
                return None, None

        except Exception as e:
            print("❌ Query error:", e)
            conn.close()
            return None, None
    else:
        print("❌ Database connection failed.")
        return None, None

# Optional test
# username, role = login("admin", "admin123")
