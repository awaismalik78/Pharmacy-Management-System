import tkinter as tk
from tkinter import messagebox, ttk
import logging
from purchases import fetch_medicines, fetch_user_id, add_purchase
from connections import create_connection

# Configure logging (ideally in main script, included here for completeness)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("pharmacy_app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def show_purchases_page(username):
    window = tk.Toplevel()
    window.title("Purchases")
    window.geometry("800x600")
    window.configure(bg="#d7f7f2")

    # Error label for persistent error display
    error_label = tk.Label(window, text="", bg="#d7f7f2", fg="red", font=("Helvetica", 12), wraplength=700)
    error_label.pack(pady=5)

    # Frame for main UI
    main_frame = tk.Frame(window, bg="#d7f7f2")
    main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Fetch connection
    conn, error = create_connection()
    if error or not conn:
        error_label.config(text=error or "Failed to connect to database. Please check database settings.")
        logger.error(f"❌ Failed to connect to database: {error or 'No connection'}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)
        return

    # Fetch user_id
    user_id, error = fetch_user_id(conn, username)
    if error or not user_id:
        error_label.config(text=error or "Failed to fetch user details. Please verify username.")
        logger.error(f"❌ Failed to fetch user_id for {username}: {error or 'No user_id'}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=lambda: (conn.close(), window.destroy()), bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)
        return

    # Fetch medicines
    medicines, error = fetch_medicines(conn)
    if error or not medicines:
        error_label.config(text=error or "No medicines available. Please add medicines to the database.")
        logger.error(f"❌ Failed to fetch medicines: {error or 'No medicines'}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=lambda: (conn.close(), window.destroy()), bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)
        return

    # Medicine selection
    medicine_dict = {f"{m[1]} (ID: {m[0]})": m for m in medicines}  # Format: "Name (ID: ID)"
    tk.Label(main_frame, text="Select Medicine:", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    medicine_var = tk.StringVar()
    medicine_combobox = ttk.Combobox(main_frame, textvariable=medicine_var, values=list(medicine_dict.keys()), font=("Helvetica", 13), state="readonly")
    medicine_combobox.pack(pady=5)

    # Quantity
    tk.Label(main_frame, text="Quantity:", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    qty_entry = tk.Entry(main_frame, font=("Helvetica", 13))
    qty_entry.pack(pady=5)

    # Cost price (per unit)
    tk.Label(main_frame, text="Cost Price (per unit):", bg="#d7f7f2", font=("Helvetica", 14)).pack(pady=5)
    cost_price_entry = tk.Entry(main_frame, font=("Helvetica", 13))
    cost_price_entry.pack(pady=5)

    # Treeview to display cart
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    columns = ("Medicine ID", "Medicine Name", "Quantity", "Cost Price", "Total Cost")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    column_widths = {"Medicine ID": 100, "Medicine Name": 200, "Quantity": 100, "Cost Price": 100, "Total Cost": 120}
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

            try:
                quantity = int(qty_entry.get())
                cost_price = float(cost_price_entry.get())
                if quantity <= 0:
                    error_label.config(text="Quantity must be positive.")
                    messagebox.showerror("Error", "Quantity must be positive.")
                    logger.warning("❌ Invalid quantity: non-positive")
                    return
                if cost_price <= 0:
                    error_label.config(text="Cost price must be positive.")
                    messagebox.showerror("Error", "Cost price must be positive.")
                    logger.warning("❌ Invalid cost price: non-positive")
                    return
            except ValueError:
                error_label.config(text="Quantity and Cost Price must be numbers.")
                messagebox.showerror("Error", "Quantity and Cost Price must be numbers.")
                logger.warning("❌ Invalid quantity or cost price: non-numeric")
                return

            medicine = medicine_dict.get(selected)
            if not medicine:
                error_label.config(text="Selected medicine not found.")
                messagebox.showerror("Error", "Selected medicine not found.")
                logger.error(f"❌ Selected medicine not found: {selected}")
                return

            medicine_id, name, _, _ = medicine
            for item in cart_items:
                if item["medicine_id"] == medicine_id:
                    error_label.config(text=f"{name} is already in the cart.")
                    messagebox.showerror("Error", f"{name} is already in the cart.")
                    logger.warning(f"❌ Duplicate medicine {name} (ID: {medicine_id})")
                    return

            total_cost = cost_price * quantity
            cart_items.append({
                "medicine_id": medicine_id,
                "name": name,
                "quantity": quantity,
                "cost_price": cost_price,
                "total_cost": total_cost
            })
            tree.insert("", "end", values=(medicine_id, name, quantity, f"${cost_price:.2f}", f"${total_cost:.2f}"))
            error_label.config(text="")
            messagebox.showinfo("Success", f"Added {name} to cart.")
            logger.info(f"✅ Added {name} (ID: {medicine_id}, Quantity: {quantity}) to cart")
            medicine_var.set("")
            qty_entry.delete(0, tk.END)
            cost_price_entry.delete(0, tk.END)
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in add_to_cart: {e}", exc_info=True)

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
                error_label.config(text="")
                logger.info(f"✅ Removed {removed_item['name']} (ID: {removed_item['medicine_id']}) from cart")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in remove_from_cart: {e}", exc_info=True)

    def confirm_purchase():
        try:
            if not cart_items:
                error_label.config(text="Cart is empty.")
                messagebox.showerror("Error", "Cart is empty.")
                logger.warning("❌ Attempted to confirm empty cart")
                return
            success, error = add_purchase(user_id, cart_items)
            if success:
                error_label.config(text="")
                messagebox.showinfo("Success", "✅ Purchase processed successfully.")
                logger.info("✅ Purchase confirmed successfully")
                cart_items.clear()
                tree.delete(*tree.get_children())
            else:
                error_label.config(text=error or "Failed to process purchase.")
                messagebox.showerror("Error", error or "Failed to process purchase.")
                logger.error(f"❌ Failed to confirm purchase: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in confirm_purchase: {e}", exc_info=True)

    # Buttons
    tk.Button(main_frame, text="Add to Cart", command=add_to_cart, bg="#4CAF50", fg="white", font=("Helvetica", 14)).pack(pady=5)
    tk.Button(main_frame, text="Remove Selected", command=remove_from_cart, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=5)
    tk.Button(main_frame, text="Confirm Purchase", command=confirm_purchase, bg="#2196F3", fg="white", font=("Helvetica", 14)).pack(pady=5)

    def on_close():
        conn.close()
        window.destroy()
        logger.info("✅ Purchases page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Purchases page opened")
    window.mainloop()