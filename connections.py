import psycopg2
from config import config
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pharmacy_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def create_connection():
    """
    Establishes a connection to the PostgreSQL database using settings from config.
    Returns a tuple (conn, error): conn is the connection object or None, error is a string or None.
    Callers are responsible for closing the connection using conn.close().
    """
    conn = None
    error = None
    try:
        params = config()
        if not params:
            raise ValueError("Configuration is empty or invalid")
        conn = psycopg2.connect(**params)
        logger.info("✅ Connected to the database successfully")
    except (psycopg2.Error, ValueError, Exception) as e:
        error = f"Database connection failed: {str(e)}"
        logger.error(f"❌ {error}")
    return conn, error

def get_user_details(username):
    """
    Fetch user details (user_id, username, role_name) for a given username.
    Returns a tuple (user_id, username, role_name) or None if not found or on error.
    """
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to fetch user details: {error or 'No connection'}")
        return None
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT user_id, username, role_name FROM users JOIN roles ON users.role_id = roles.role_id WHERE username = %s",
            (username,)
        )
        result = cur.fetchone()
        conn.close()
        if result:
            logger.info(f"✅ Fetched user details for {username}")
            return result
        logger.warning(f"❌ No user found for username {username}")
        return None
    except Exception as e:
        logger.error(f"❌ Error fetching user details: {e}")
        conn.close()
        return None