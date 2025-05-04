import logging
from connections import create_connection

# Use existing logger (configured in dashboard.py)
logger = logging.getLogger(__name__)

def fetch_medicines():
    """Fetch all medicines for the Combobox. Returns (medicines, error)."""
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to fetch medicines: {error or 'No connection'}")
        return [], error or "No database connection"
    try:
        cur = conn.cursor()
        cur.execute("SELECT medicine_id, name, price, quantity FROM medicines")
        medicines = cur.fetchall()
        logger.info("✅ Successfully fetched medicines")
        return medicines, None
    except Exception as e:
        logger.error(f"❌ Error fetching medicines: {e}")
        return [], f"Error fetching medicines: {str(e)}"
    finally:
        conn.close()

def fetch_user_id(username):
    """Fetch user_id from username. Returns (user_id, error)."""
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to fetch user_id: {error or 'No connection'}")
        return None, error or "No database connection"
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
    finally:
        conn.close()

def add_sale(customer_id, user_id, cart_items):
    """Process a sale with multiple items, update stock, and log to stock_logs. Returns (success, error)."""
    if not cart_items:
        logger.error("❌ Cart is empty")
        return False, "Cart is empty"
    required_keys = {'medicine_id', 'quantity', 'price', 'total_price'}
    for item in cart_items:
        if not all(key in item for key in required_keys):
            logger.error(f"❌ Invalid cart item structure: {item}")
            return False, "Invalid cart item structure"
        if item['quantity'] <= 0:
            logger.error(f"❌ Invalid quantity in cart item: {item['quantity']}")
            return False, f"Invalid quantity for medicine ID {item['medicine_id']}"
        if item['total_price'] != item['quantity'] * item['price']:
            logger.error(f"❌ Inconsistent total_price in cart item: {item}")
            return False, f"Inconsistent total_price for medicine ID {item['medicine_id']}"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to add sale: {error or 'No connection'}")
        return False, error or "Failed to connect to database"
    try:
        cur = conn.cursor()
        total_amount = sum(item['total_price'] for item in cart_items)
        cur.execute("""
            INSERT INTO sales (customer_id, user_id, total_amount)
            VALUES (%s, %s, %s) RETURNING sale_id
        """, (customer_id, user_id, total_amount))
        sale_id = cur.fetchone()[0]
        for item in cart_items:
            medicine_id = item['medicine_id']
            quantity = item['quantity']
            price = item['price']
            cur.execute("SELECT quantity FROM medicines WHERE medicine_id = %s", (medicine_id,))
            result = cur.fetchone()
            if not result:
                conn.rollback()
                logger.error(f"❌ Medicine ID {medicine_id} not found")
                return False, f"Medicine ID {medicine_id} not found"
            stock = result[0]
            if quantity > stock:
                conn.rollback()
                logger.error(f"❌ Not enough stock for medicine ID {medicine_id}: requested {quantity}, available {stock}")
                return False, f"Not enough stock for medicine ID {medicine_id}"
            cur.execute("""
                INSERT INTO sales_details (sale_id, medicine_id, quantity, selling_price)
                VALUES (%s, %s, %s, %s)
            """, (sale_id, medicine_id, quantity, price))
            cur.execute("""
                UPDATE medicines SET quantity = quantity - %s WHERE medicine_id = %s
            """, (quantity, medicine_id))
            cur.execute("""
                INSERT INTO stock_logs (medicine_id, change_type, quantity_change)
                VALUES (%s, %s, %s)
            """, (medicine_id, 'sale', -quantity))
        conn.commit()
        logger.info(f"✅ Sale processed successfully, sale_id: {sale_id}")
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error adding sale: {e}")
        return False, f"Error adding sale: {str(e)}"
    finally:
        conn.close()