# dashboard_logic.py
import psycopg2
from connections import create_connection


def get_user_details(username):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            query = """
                SELECT u.user_id, u.username, r.role_name
                FROM users u
                JOIN roles r ON u.role_id = r.role_id
                WHERE u.username = %s
            """
            cur.execute(query, (username,))
            result = cur.fetchone()
            conn.close()
            return result  # returns (user_id, username, role_name)
        except Exception as e:
            print("❌ Error fetching user details:", e)
            return None
    return None
