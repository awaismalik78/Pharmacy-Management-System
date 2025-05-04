import logging
from connections import create_connection

# Configure logging
logger = logging.getLogger(__name__)

def fetch_medicines(conn):
    """Fetch all medicines for the Combobox. Returns (medicines, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return [], "No database connection provided"
    try:
        cur = conn.cursor()
        cur.execute("SELECT medicine_id, name, price, quantity FROM medicines")
        medicines = cur.fetchall()
        logger.info("✅ Successfully fetched medicines")
        return medicines, None
    except Exception as e:
        logger.error(f"❌ Error fetching medicines: {e}")
        return [], f"Error fetching medicines: {str(e)}"

def fetch_user_id(conn, username):
    """Fetch user_id from username. Returns (user_id, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return None, "No database connection provided"
    try:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            logger.info(f"✅ Fetched user_id for {username}")
            return result[0], None
        logger.warning(f"❌ No user found for username {username}")
        return None, f"No user found for username {username}"
    except Exception as e:
        logger.error(f"❌ Error fetching user_id: {e}")
        return None, f"Error fetching user_id: {str(e)}"

def add_purchase(user_id, cart_items):
    """
    Process a purchase with multiple items, update stock, and log to stock_logs.
    Returns (success, error): success is True/False, error is a string or None.
    """
    if not cart_items:
        logger.error("❌ Cart is empty")
        return False, "Cart is empty"

    # Validate cart_items
    required_keys = {'medicine_id', 'quantity', 'cost_price', 'total_cost'}
    for item in cart_items:
        if not all(key in item for key in required_keys):
            logger.error(f"❌ Invalid cart item structure: {item}")
            return False, "Invalid cart item structure"
        if item['quantity'] <= 0:
            logger.error(f"❌ Invalid quantity in cart item: {item['quantity']}")
            return False, f"Invalid quantity for medicine ID {item['medicine_id']}"
        if item['total_cost'] != item['quantity'] * item['cost_price']:
            logger.error(f"❌ Inconsistent total_cost in cart item: {item}")
            return False, f"Inconsistent total_cost for medicine ID {item['medicine_id']}"

    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to add purchase: {error or 'No connection'}")
        return False, error or "Failed to connect to database"
    
    try:
        cur = conn.cursor()
        total_amount = sum(item['total_cost'] for item in cart_items)

        # Insert into purchases
        cur.execute("""
            INSERT INTO purchases (user_id, total_amount)
            VALUES (%s, %s) RETURNING purchase_id
        """, (user_id, total_amount))
        purchase_id = cur.fetchone()[0]

        # Process each cart item
        for item in cart_items:
            medicine_id = item['medicine_id']
            quantity = item['quantity']
            cost_price = item['cost_price']

            # Check medicine exists
            cur.execute("SELECT quantity FROM medicines WHERE medicine_id = %s", (medicine_id,))
            result = cur.fetchone()
            if not result:
                conn.rollback()
                conn.close()
                logger.error(f"❌ Medicine ID {medicine_id} not found")
                return False, f"Medicine ID {medicine_id} not found"

            # Insert into purchase_details
            cur.execute("""
                INSERT INTO purchase_details (purchase_id, medicine_id, quantity, cost_price)
                VALUES (%s, %s, %s, %s)
            """, (purchase_id, medicine_id, quantity, cost_price))

            # Update medicine quantity
            cur.execute("""
                UPDATE medicines SET quantity = quantity + %s WHERE medicine_id = %s
            """, (quantity, medicine_id))

            # Log to stock_logs
            cur.execute("""
                INSERT INTO stock_logs (medicine_id, change_type, quantity_change)
                VALUES (%s, %s, %s)
            """, (medicine_id, 'purchase', quantity))

        conn.commit()
        conn.close()
        logger.info(f"✅ Purchase processed successfully, purchase_id: {purchase_id}")
        return True, None
    except Exception as e:
        conn.rollback()
        conn.close()
        logger.error(f"❌ Error adding purchase: {e}")
        return False, f"Error adding purchase: {str(e)}"