import logging
from connections import create_connection

# Configure logging (move to dashboard.py)
logger = logging.getLogger(__name__)

def fetch_all_medicines():
    """Fetch all medicines. Returns (medicines, error)."""
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to fetch medicines: {error or 'No connection'}")
        return [], error or "No database connection"
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT medicine_id, name, quantity, price
            FROM medicines
            ORDER BY medicine_id
        """)
        medicines = cur.fetchall()
        logger.info("✅ Successfully fetched medicines")
        return medicines, None
    except Exception as e:
        logger.error(f"❌ Error fetching medicines: {e}")
        return [], f"Error fetching medicines: {str(e)}"
    finally:
        conn.close()

def add_medicine(name, quantity, price):
    """Add a new medicine. Returns (success, error)."""
    if not name or quantity is None or price is None:
        logger.error("❌ Missing required fields")
        return False, "All fields are required"
    if quantity < 0 or price < 0:
        logger.error("❌ Quantity and price must be non-negative")
        return False, "Quantity and price must be non-negative"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to add medicine: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        # Check if name is unique
        cur.execute("SELECT medicine_id FROM medicines WHERE name = %s", (name,))
        if cur.fetchone():
            logger.error(f"❌ Medicine name already exists: {name}")
            return False, f"Medicine name already exists: {name}"
        cur.execute("""
            INSERT INTO medicines (name, quantity, price)
            VALUES (%s, %s, %s)
        """, (name, quantity, price))
        conn.commit()
        logger.info(f"✅ Added medicine: {name}")
        return True, None
    except Exception as e:
        logger.error(f"❌ Error adding medicine: {e}")
        return False, f"Error adding medicine: {str(e)}"
    finally:
        conn.close()

def update_medicine(medicine_id, name, quantity, price):
    """Update an existing medicine. Returns (success, error)."""
    if not name or quantity is None or price is None:
        logger.error("❌ Missing required fields")
        return False, "All fields are required"
    if quantity < 0 or price < 0:
        logger.error("❌ Quantity and price must be non-negative")
        return False, "Quantity and price must be non-negative"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to update medicine: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        # Check if name is unique (excluding current medicine)
        cur.execute("SELECT medicine_id FROM medicines WHERE name = %s AND medicine_id != %s", (name, medicine_id))
        if cur.fetchone():
            logger.error(f"❌ Medicine name already exists: {name}")
            return False, f"Medicine name already exists: {name}"
        cur.execute("""
            UPDATE medicines
            SET name = %s, quantity = %s, price = %s
            WHERE medicine_id = %s
        """, (name, quantity, price, medicine_id))
        if cur.rowcount == 0:
            logger.warning(f"❌ No medicine found with medicine_id: {medicine_id}")
            return False, f"No medicine found with medicine_id: {medicine_id}"
        conn.commit()
        logger.info(f"✅ Updated medicine ID: {medicine_id}")
        return True, None
    except Exception as e:
        logger.error(f"❌ Error updating medicine: {e}")
        return False, f"Error updating medicine: {str(e)}"
    finally:
        conn.close()

def delete_medicine(medicine_id):
    """Delete a medicine. Returns (success, error)."""
    if not medicine_id:
        logger.error("❌ No medicine_id provided")
        return False, "No medicine_id provided"
    conn, error = create_connection()
    if error or not conn:
        logger.error(f"❌ Failed to delete medicine: {error or 'No connection'}")
        return False, error or "No database connection"
    try:
        cur = conn.cursor()
        # Check for dependencies in sales_details
        cur.execute("SELECT sale_id FROM sales_details WHERE medicine_id = %s LIMIT 1", (medicine_id,))
        if cur.fetchone():
            logger.error(f"❌ Cannot delete medicine ID {medicine_id}: used in sales")
            return False, f"Cannot delete medicine: used in sales"
        # Check for dependencies in purchase_details
        cur.execute("SELECT purchase_id FROM purchase_details WHERE medicine_id = %s LIMIT 1", (medicine_id,))
        if cur.fetchone():
            logger.error(f"❌ Cannot delete medicine ID {medicine_id}: used in purchases")
            return False, f"Cannot delete medicine: used in purchases"
        cur.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
        if cur.rowcount == 0:
            logger.warning(f"❌ No medicine found with medicine_id: {medicine_id}")
            return False, f"No medicine found with medicine_id: {medicine_id}"
        conn.commit()
        logger.info(f"✅ Deleted medicine ID: {medicine_id}")
        return True, None
    except Exception as e:
        logger.error(f"❌ Error deleting medicine: {e}")
        return False, f"Error deleting medicine: {str(e)}"
    finally:
        conn.close()