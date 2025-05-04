import logging
from connections import create_connection

# Use existing logger (configured in dashboard.py)
logger = logging.getLogger(__name__)

def fetch_sales_details():
    """Fetch all sales details for the Treeview. Returns (details, error)."""
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to fetch sales details: {error or 'No connection'}")
        return [], error or "No database connection"
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT sd.sale_id, sd.medicine_id, m.name, sd.quantity, sd.selling_price
            FROM sales_details sd
            JOIN medicines m ON sd.medicine_id = m.medicine_id
            ORDER BY sd.sale_id, sd.medicine_id
        """)
        details = cur.fetchall()
        logger.info("✅ Successfully fetched sales details")
        return details, None
    except Exception as e:
        logger.error(f"❌ Error fetching sales details: {e}")
        return [], f"Error fetching sales details: {str(e)}"
    finally:
        conn.close()

def delete_sale(sale_id):
    """Delete a sale and its details, restoring stock. Returns (success, error)."""
    if not sale_id:
        logger.error("❌ No sale_id provided")
        return False, "No sale_id provided"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to delete sale: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        # Fetch sales_details to restore stock
        cur.execute("SELECT medicine_id, quantity FROM sales_details WHERE sale_id = %s", (sale_id,))
        sale_details = cur.fetchall()
        if not sale_details:
            logger.warning(f"❌ No sale found with sale_id: {sale_id}")
            conn.close()
            return False, f"No sale found with sale_id: {sale_id}"
        # Restore stock and log to stock_logs
        for medicine_id, quantity in sale_details:
            cur.execute("""
                UPDATE medicines SET quantity = quantity + %s WHERE medicine_id = %s
            """, (quantity, medicine_id))
            cur.execute("""
                INSERT INTO stock_logs (medicine_id, change_type, quantity_change)
                VALUES (%s, %s, %s)
            """, (medicine_id, 'sale_deletion', quantity))
        # Delete from sales_details
        cur.execute("DELETE FROM sales_details WHERE sale_id = %s", (sale_id,))
        # Delete from sales
        cur.execute("DELETE FROM sales WHERE sale_id = %s", (sale_id,))
        if cur.rowcount == 0:
            conn.rollback()
            logger.warning(f"❌ No sale found with sale_id: {sale_id}")
            return False, f"No sale found with sale_id: {sale_id}"
        conn.commit()
        logger.info(f"✅ Deleted sale ID: {sale_id}")
        return True, None
    except Exception as e:
        conn.rollback()
        logger.error(f"❌ Error deleting sale: {e}")
        return False, f"Error deleting sale: {str(e)}"
    finally:
        conn.close()