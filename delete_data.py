import logging
from connections import create_connection

# Configure logging
logger = logging.getLogger(__name__)

def fetch_sales(conn):
    """Fetch all sales records. Returns (sales, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return [], "No database connection provided"
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT s.sale_id, s.user_id, u.username, s.total_amount, s.sale_date
            FROM sales s
            JOIN users u ON s.user_id = u.user_id
            ORDER BY s.sale_date DESC
        """)
        sales = cur.fetchall()
        logger.info("✅ Successfully fetched sales")
        return sales, None
    except Exception as e:
        logger.error(f"❌ Error fetching sales: {e}")
        return [], f"Error fetching sales: {str(e)}"

def fetch_purchases(conn):
    """Fetch all purchases records. Returns (purchases, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return [], "No database connection provided"
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT p.purchase_id, p.user_id, u.username, p.total_amount, p.purchase_date
            FROM purchases p
            JOIN users u ON p.user_id = u.user_id
            ORDER BY p.purchase_date DESC
        """)
        purchases = cur.fetchall()
        logger.info("✅ Successfully fetched purchases")
        return purchases, None
    except Exception as e:
        logger.error(f"❌ Error fetching purchases: {e}")
        return [], f"Error fetching purchases: {str(e)}"

def fetch_user_role(conn, username):
    """Fetch user role. Returns (role_id, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return None, "No database connection provided"
    try:
        cur = conn.cursor()
        cur.execute("SELECT role_id FROM users WHERE username = %s", (username,))
        result = cur.fetchone()
        if result:
            logger.info(f"✅ Fetched role_id for {username}")
            return result[0], None
        logger.warning(f"❌ No user found for username {username}")
        return None, f"No user found for username {username}"
    except Exception as e:
        logger.error(f"❌ Error fetching user role: {e}")
        return None, f"Error fetching user role: {str(e)}"

def delete_sales(conn, sale_ids):
    """Delete specified sales and update related tables. Returns (success, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return False, "No database connection provided"
    if not sale_ids:
        logger.error("❌ No sale IDs provided")
        return False, "No sale IDs provided"
    try:
        cur = conn.cursor()

        # Fetch sales details to adjust stock
        cur.execute("""
            SELECT sd.sale_id, sd.medicine_id, sd.quantity
            FROM sales_details sd
            WHERE sd.sale_id = ANY(%s)
        """, (sale_ids,))
        sale_details = cur.fetchall()

        # Update medicines quantity
        for sale_id, medicine_id, quantity in sale_details:
            cur.execute("""
                UPDATE medicines
                SET quantity = quantity + %s
                WHERE medicine_id = %s
            """, (quantity, medicine_id))
            logger.info(f"✅ Restored {quantity} units to medicine ID {medicine_id} for sale ID {sale_id}")

        # Delete stock_logs for these sales
        cur.execute("""
            DELETE FROM stock_logs
            WHERE change_type = 'sale' AND medicine_id IN (
                SELECT medicine_id FROM sales_details WHERE sale_id = ANY(%s)
            )
        """, (sale_ids,))

        # Delete sales_details
        cur.execute("DELETE FROM sales_details WHERE sale_id = ANY(%s)", (sale_ids,))

        # Delete sales
        cur.execute("DELETE FROM sales WHERE sale_id = ANY(%s)", (sale_ids,))
        if cur.rowcount == 0:
            conn.rollback()
            logger.warning("❌ No sales deleted: IDs not found")
            return False, "No sales deleted: IDs not found"

        conn.commit()
        logger.info(f"✅ Deleted sales: {sale_ids}")
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error deleting sales: {e}")
        return False, f"Error deleting sales: {str(e)}"

def delete_purchases(conn, purchase_ids):
    """Delete specified purchases and update related tables. Returns (success, error)."""
    if not conn:
        logger.error("❌ No database connection provided")
        return False, "No database connection provided"
    if not purchase_ids:
        logger.error("❌ No purchase IDs provided")
        return False, "No purchase IDs provided"
    try:
        cur = conn.cursor()

        # Fetch purchase details to adjust stock
        cur.execute("""
            SELECT pd.purchase_id, pd.medicine_id, pd.quantity
            FROM purchase_details pd
            WHERE pd.purchase_id = ANY(%s)
        """, (purchase_ids,))
        purchase_details = cur.fetchall()

        # Check stock availability before deletion
        for purchase_id, medicine_id, quantity in purchase_details:
            cur.execute("SELECT quantity FROM medicines WHERE medicine_id = %s", (medicine_id,))
            current_quantity = cur.fetchone()[0]
            if current_quantity < quantity:
                conn.rollback()
                logger.error(f"❌ Insufficient stock for medicine ID {medicine_id}: {current_quantity} available, {quantity} needed")
                return False, f"Insufficient stock for medicine ID {medicine_id}: {current_quantity} available"

        # Update medicines quantity
        for purchase_id, medicine_id, quantity in purchase_details:
            cur.execute("""
                UPDATE medicines
                SET quantity = quantity - %s
                WHERE medicine_id = %s
            """, (quantity, medicine_id))
            logger.info(f"✅ Removed {quantity} units from medicine ID {medicine_id} for purchase ID {purchase_id}")

        # Delete stock_logs for these purchases
        cur.execute("""
            DELETE FROM stock_logs
            WHERE change_type = 'purchase' AND medicine_id IN (
                SELECT medicine_id FROM purchase_details WHERE purchase_id = ANY(%s)
            )
        """, (purchase_ids,))

        # Delete purchase_details
        cur.execute("DELETE FROM purchase_details WHERE purchase_id = ANY(%s)", (purchase_ids,))

        # Delete purchases
        cur.execute("DELETE FROM purchases WHERE purchase_id = ANY(%s)", (purchase_ids,))
        if cur.rowcount == 0:
            conn.rollback()
            logger.warning("❌ No purchases deleted: IDs not found")
            return False, "No purchases deleted: IDs not found"

        conn.commit()
        logger.info(f"✅ Deleted purchases: {purchase_ids}")
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error deleting purchases: {e}")
        return False, f"Error deleting purchases: {str(e)}"