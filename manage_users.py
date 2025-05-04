import logging
from connections import create_connection

# Configure logging (move to dashboard.py)
logger = logging.getLogger(__name__)

def fetch_all_users():
    """Fetch all users with roles. Returns (users, error)."""
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to fetch users: {error or 'No connection'}")
        return [], error or "No database connection"
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT u.user_id, u.username, r.role_name, u.created_at
            FROM users u
            JOIN roles r ON u.role_id = r.role_id
            ORDER BY u.user_id
        """)
        users = cur.fetchall()
        logger.info("✅ Successfully fetched users")
        return users, None
    except Exception as e:
        logger.error(f"❌ Error fetching users: {e}")
        return [], f"Error fetching users: {str(e)}"
    finally:
        conn.close()

def add_user(username, password, role_id):
    """Add a new user. Returns (success, error)."""
    if not username or not password or not role_id:
        logger.error("❌ Missing required fields")
        return False, "All fields are required"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to add user: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        # Check if role_id exists
        cur.execute("SELECT role_id FROM roles WHERE role_id = %s", (role_id,))
        if not cur.fetchone():
            logger.error(f"❌ Invalid role_id: {role_id}")
            return False, f"Invalid role_id: {role_id}"
        # Check if username is unique
        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        if cur.fetchone():
            logger.error(f"❌ Username already exists: {username}")
            return False, f"Username already exists: {username}"
        cur.execute("""
            INSERT INTO users (username, password, role_id)
            VALUES (%s, %s, %s)
        """, (username, password, role_id))
        conn.commit()
        logger.info(f"✅ Added user: {username}")
        return True, None
    except Exception as e:
        logger.error(f"❌ Error adding user: {e}")
        return False, f"Error adding user: {str(e)}"
    finally:
        conn.close()

def update_user(user_id, username, password, role_id):
    """Update an existing user. Returns (success, error)."""
    if not username or not role_id:
        logger.error("❌ Missing required fields")
        return False, "Username and role are required"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to update user: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        # Check if role_id exists
        cur.execute("SELECT role_id FROM roles WHERE role_id = %s", (role_id,))
        if not cur.fetchone():
            logger.error(f"❌ Invalid role_id: {role_id}")
            return False, f"Invalid role_id: {role_id}"
        # Check if username is unique (excluding current user)
        cur.execute("SELECT user_id FROM users WHERE username = %s AND user_id != %s", (username, user_id))
        if cur.fetchone():
            logger.error(f"❌ Username already exists: {username}")
            return False, f"Username already exists: {username}"
        # Update user
        if password:
            cur.execute("""
                UPDATE users
                SET username = %s, password = %s, role_id = %s
                WHERE user_id = %s
            """, (username, password, role_id, user_id))
        else:
            cur.execute("""
                UPDATE users
                SET username = %s, role_id = %s
                WHERE user_id = %s
            """, (username, role_id, user_id))
        if cur.rowcount == 0:
            logger.warning(f"❌ No user found with user_id: {user_id}")
            return False, f"No user found with user_id: {user_id}"
        conn.commit()
        logger.info(f"✅ Updated user: {username}")
        return True, None
    except Exception as e:
        logger.error(f"❌ Error updating user: {e}")
        return False, f"Error updating user: {str(e)}"
    finally:
        conn.close()

def delete_user(user_id):
    """Delete a user. Returns (success, error)."""
    if not user_id:
        logger.error("❌ No user_id provided")
        return False, "No user_id provided"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to delete user: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM users WHERE user_id = %s", (user_id,))
        if cur.rowcount == 0:
            logger.warning(f"❌ No user found with user_id: {user_id}")
            return False, f"No user found with user_id: {user_id}"
        conn.commit()
        logger.info(f"✅ Deleted user_id: {user_id}")
        return True, None
    except Exception as e:
        logger.error(f"❌ Error deleting user: {e}")
        return False, f"Error deleting user: {str(e)}"
    finally:
        conn.close()