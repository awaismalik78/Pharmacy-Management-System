import tkinter as tk
from tkinter import messagebox, ttk
import logging
from sales import fetch_medicines, fetch_user_id, add_sale
from connections import create_connection

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

def show_sales_page(username):
    window = tk.Toplevel()
    window.title("Sales")
    window.geometry("800x600")
    window.configure(bg="#d7f7f2")

    # Fetch connection
    conn, error = create_connection()
    if error or not conn:
        messagebox.showerror("Error", error or "Failed to connect to database.")
        window.destroy()
        logger.error(f"❌ Failed to connect to database: {error or 'No connection'}")
        return

    # Fetch user_id
    user_id, error = fetch_user_id(conn, username)
    if error or not user_id:
        messagebox.showerror("Error", error or "Failed to fetch user details.")
        conn.close()
        window.destroy()
        logger.error(f"❌ Failed to fetch user_id for {username}: {error or 'No user_id'}")
        return

    # Customer ID (optional)
    tk.Label(window, text="Customer ID (optional):", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    customer_entry = tk.Entry(window, font=("Helvetica", 13))
    customer_entry.pack(pady=5)

    # Medicine selection
    tk.Label(window, text="Select Medicine:", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    medicines, error = fetch_medicines(conn)
    if error:
        messagebox.showerror("Error", error)
        conn.close()
        window.destroy()
        logger.error(f"❌ Failed to fetch medicines: {error}")
        return
    medicine_dict = {f"{m[1]} (ID: {m[0]})": m for m in medicines}  # Format: "Name (ID: ID)"
    medicine_var = tk.StringVar()
    medicine_combobox = ttk.Combobox(window, textvariable=medicine_var, values=list(medicine_dict.keys()), font=("Helvetica", 13), state="readonly")
    medicine_combobox.pack(pady=5)

    # Quantity
    tk.Label(window, text="Quantity:", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    qty_entry = tk.Entry(window, font=("Helvetica", 13))
    qty_entry.pack(pady=5)

    # Treeview to display cart
    tree_frame = tk.Frame(window)
    tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    columns = ("Medicine ID", "Medicine Name", "Quantity", "Price", "Total Price")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    column_widths = {"Medicine ID": 100, "Medicine Name": 200, "Quantity": 100, "Price": 100, "Total Price": 120}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=column_widths[col], anchor="center")

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Cart to store items
    cart_items = []

    def add_to_cart():
        selected = medicine_var.get()
        if not selected:
            messagebox.showerror("Error", "Please select a medicine.")
            logger.warning("❌ No medicine selected for cart")
            return
        try:
            quantity = int(qty_entry.get())
            if quantity <= 0:
                messagebox.showerror("Error", "Quantity must be positive.")
                logger.warning("❌ Invalid quantity entered: non-positive")
                return
            medicine = medicine_dict[selected]
            medicine_id, name, price, stock = medicine
            if quantity > stock:
                messagebox.showwarning("Warning", f"Not enough stock for {name}. Available: {stock}")
                logger.warning(f"❌ Insufficient stock for {name}: requested {quantity}, available {stock}")
                return

            # Check for duplicate medicine (optional: comment out to allow duplicates)
            for item in cart_items:
                if item["medicine_id"] == medicine_id:
                    messagebox.showerror("Error", f"{name} is already in the cart.")
                    logger.warning(f"❌ Duplicate medicine {name} (ID: {medicine_id})")
                    return

            total_price = price * quantity
            cart_items.append({
                "medicine_id": medicine_id,
                "name": name,
                "quantity": quantity,
                "price": price,
                "total_price": total_price
            })
            tree.insert("", "end", values=(medicine_id, name, quantity, f"${price:.2f}", f"${total_price:.2f}"))
            
            logger.info(f"✅ Added {name} (ID: {medicine_id}, Quantity: {quantity}) to cart")
            medicine_var.set("")
            qty_entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid quantity.")
            logger.warning("❌ Invalid quantity entered: non-numeric")

    def remove_from_cart():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select an item to remove.")
            logger.warning("❌ No item selected for removal")
            return
        for item in selected:
            index = tree.index(item)
            removed_item = cart_items.pop(index)
            tree.delete(item)
            logger.info(f"✅ Removed {removed_item['name']} (ID: {removed_item['medicine_id']}) from cart")

    def confirm_sale():
        if not cart_items:
            messagebox.showerror("Error", "Cart is empty.")
            logger.warning("❌ Attempted to confirm empty cart")
            return
        customer_id = customer_entry.get()
        customer_id = int(customer_id) if customer_id.strip() else None
        if customer_id:
            try:
                cur = conn.cursor()
                cur.execute("SELECT customer_id FROM customers WHERE customer_id = %s", (customer_id,))
                if not cur.fetchone():
                    messagebox.showerror("Error", "Invalid customer ID.")
                    logger.warning(f"❌ Invalid customer ID: {customer_id}")
                    return
            except Exception as e:
                messagebox.showerror("Error", f"Error validating customer ID: {e}")
                logger.error(f"❌ Error validating customer ID {customer_id}: {e}")
                return
        success, error = add_sale(customer_id, user_id, cart_items)
        if success:
            messagebox.showinfo("Success", "✅ Sale processed successfully.")
            logger.info("✅ Sale confirmed successfully")
            cart_items.clear()
            tree.delete(*tree.get_children())
            customer_entry.delete(0, tk.END)
        else:
            messagebox.showerror("Error", error or "Failed to process sale.")
            logger.error(f"❌ Failed to confirm sale: {error}")

    # Buttons
    tk.Button(window, text="Add to Cart", command=add_to_cart, bg="#4CAF50", fg="white", font=("Helvetica", 14)).pack(pady=5)
    tk.Button(window, text="Remove Selected", command=remove_from_cart, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=5)
    tk.Button(window, text="Confirm Sale", command=confirm_sale, bg="#2196F3", fg="white", font=("Helvetica", 14)).pack(pady=5)

    def on_close():
        conn.close()
        window.destroy()
        logger.info("✅ Sales page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Sales page opened")
    window.mainloop()