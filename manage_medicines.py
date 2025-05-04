from connections import create_connection

def fetch_all_medicines():
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                SELECT medicine_id, name, quantity, price FROM medicines ORDER BY medicine_id
            """)
            rows = cur.fetchall()
            conn.close()
            return rows
        except Exception as e:
            print("❌ Error fetching medicines:", e)
            conn.close()
            return []

def add_medicine(name, quantity, price):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                INSERT INTO medicines (name, quantity, price)
                VALUES (%s, %s, %s)
            """, (name, quantity, price))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("❌ Error adding medicine:", e)
            conn.close()
            return False

def update_medicine(medicine_id, name, quantity, price):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("""
                UPDATE medicines SET name=%s, quantity=%s, price=%s
                WHERE medicine_id = %s
            """, (name, quantity, price, medicine_id))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("❌ Error updating medicine:", e)
            conn.close()
            return False

def delete_medicine(medicine_id):
    conn = create_connection()
    if conn:
        try:
            cur = conn.cursor()
            cur.execute("DELETE FROM medicines WHERE medicine_id = %s", (medicine_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print("❌ Error deleting medicine:", e)
            conn.close()
            return False
