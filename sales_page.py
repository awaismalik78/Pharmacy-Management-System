import tkinter as tk
from tkinter import messagebox, ttk
import logging
from sales import fetch_medicines, fetch_user_id, add_sale
from connections import create_connection

# Use existing logger (configured in dashboard.py)
logger = logging.getLogger(__name__)

def show_sales_page(username):
    window = tk.Toplevel()
    window.title("Sales")
    window.geometry("800x600")
    window.configure(bg="#d7f7f2")

    # Error label
    error_label = tk.Label(window, text="", bg="#d7f7f2", fg="red", font=("Helvetica", 12), wraplength=700)
    error_label.pack(pady=5)

    # Customer ID (optional)
    tk.Label(window, text="Customer ID (optional):", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    customer_entry = tk.Entry(window, font=("Helvetica", 13))
    customer_entry.pack(pady=5)

    # Medicine selection
    tk.Label(window, text="Select Medicine:", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    medicines, error = fetch_medicines()
    if error:
        error_label.config(text=error)
        messagebox.showerror("Error", error)
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
        try:
            selected = medicine_var.get()
            if not selected:
                error_label.config(text="Please select a medicine.")
                messagebox.showerror("Error", "Please select a medicine.")
                logger.warning("❌ No medicine selected for cart")
                return
            quantity = int(qty_entry.get())
            if quantity <= 0:
                error_label.config(text="Quantity must be positive.")
                messagebox.showerror("Error", "Quantity must be positive.")
                logger.warning("❌ Invalid quantity entered: non-positive")
                return
            medicine = medicine_dict[selected]
            medicine_id, name, price, stock = medicine
            if quantity > stock:
                error_label.config(text=f"Not enough stock for {name}. Available: {stock}")
                messagebox.showwarning("Warning", f"Not enough stock for {name}. Available: {stock}")
                logger.warning(f"❌ Insufficient stock for {name}: requested {quantity}, available {stock}")
                return
            for item in cart_items:
                if item["medicine_id"] == medicine_id:
                    error_label.config(text=f"{name} is already in the cart.")
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
            error_label.config(text="")
        except ValueError:
            error_label.config(text="Please enter a valid quantity.")
            messagebox.showerror("Error", "Please enter a valid quantity.")
            logger.warning("❌ Invalid quantity entered: non-numeric")

    def remove_from_cart():
        try:
            selected = tree.selection()
            if not selected:
                error_label.config(text="Please select an item to remove.")
                messagebox.showerror("Error", "Please select an item to remove.")
                logger.warning("❌ No item selected for removal")
                return
            for item in selected:
                index = tree.index(item)
                removed_item = cart_items.pop(index)
                tree.delete(item)
                logger.info(f"✅ Removed {removed_item['name']} (ID: {removed_item['medicine_id']}) from cart")
                error_label.config(text="")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in remove_from_cart: {e}", exc_info=True)

    def confirm_sale():
        try:
            if not cart_items:
                error_label.config(text="Cart is empty.")
                messagebox.showerror("Error", "Cart is empty.")
                logger.warning("❌ Attempted to confirm empty cart")
                return
            customer_id = customer_entry.get().strip()
            customer_id = int(customer_id) if customer_id else None
            if customer_id:
                conn, error = create_connection()
                if error or not conn:
                    error_label.config(text=error or "Failed to connect to database.")
                    messagebox.showerror("Error", error or "Failed to connect to database.")
                    logger.error(f"❌ Failed to validate customer ID: {error or 'No connection'}")
                    return
                try:
                    cur = conn.cursor()
                    cur.execute("SELECT customer_id FROM customers WHERE customer_id = %s", (customer_id,))
                    if not cur.fetchone():
                        error_label.config(text="Invalid customer ID.")
                        messagebox.showerror("Error", "Invalid customer ID.")
                        logger.warning(f"❌ Invalid customer ID: {customer_id}")
                        return
                except Exception as e:
                    error_label.config(text=f"Error validating customer ID: {str(e)}")
                    messagebox.showerror("Error", f"Error validating customer ID: {str(e)}")
                    logger.error(f"❌ Error validating customer ID {customer_id}: {e}")
                    return
                finally:
                    conn.close()
            user_id, error = fetch_user_id(username)
            if error or not user_id:
                error_label.config(text=error or "Failed to fetch user details.")
                messagebox.showerror("Error", error or "Failed to fetch user details.")
                logger.error(f"❌ Failed to fetch user_id for {username}: {error or 'No user_id'}")
                return
            success, error = add_sale(customer_id, user_id, cart_items)
            if success:
                messagebox.showinfo("Success", "✅ Sale processed successfully.")
                logger.info("✅ Sale confirmed successfully")
                cart_items.clear()
                tree.delete(*tree.get_children())
                customer_entry.delete(0, tk.END)
                error_label.config(text="")
            else:
                error_label.config(text=error or "Failed to process sale.")
                messagebox.showerror("Error", error or "Failed to process sale.")
                logger.error(f"❌ Failed to confirm sale: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in confirm_sale: {e}", exc_info=True)

    # Buttons
    tk.Button(window, text="Add to Cart", command=add_to_cart, bg="#4CAF50", fg="white", font=("Helvetica", 14)).pack(pady=5)
    tk.Button(window, text="Remove Selected", command=remove_from_cart, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=5)
    tk.Button(window, text="Confirm Sale", command=confirm_sale, bg="#2196F3", fg="white", font=("Helvetica", 14)).pack(pady=5)

    def on_close():
        window.destroy()
        logger.info("✅ Sales page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Sales page opened")
    window.mainloop()