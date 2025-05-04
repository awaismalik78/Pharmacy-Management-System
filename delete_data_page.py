import tkinter as tk
from tkinter import messagebox, ttk
import logging
from delete_data import fetch_sales, fetch_purchases, delete_sales, delete_purchases
from connections import create_connection, get_user_details

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

def show_delete_data_page(username):
    window = tk.Toplevel()
    window.title("Delete Data")
    window.geometry("1000x600")
    window.configure(bg="#d7f7f2")

    # Error label for persistent error display
    error_label = tk.Label(window, text="", bg="#d7f7f2", fg="red", font=("Helvetica", 12), wraplength=900)
    error_label.pack(pady=5)

    # Frame for main UI
    main_frame = tk.Frame(window, bg="#d7f7f2")
    main_frame.pack(pady=10, fill=tk.BOTH, expand=True)

    # Verify owner role
    user_data = get_user_details(username)
    if not user_data:
        error_label.config(text="Failed to fetch user details.")
        logger.error(f"❌ Failed to fetch user details for {username}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)
        return
    user_id, username, role = user_data
    if role.lower() != 'owner':
        error_label.config(text="Unauthorized access. Owner privileges required.")
        logger.error(f"❌ Unauthorized access for {username}: role is {role}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)
        return

    # Fetch connection
    conn, error = create_connection()
    if error or not conn:
        error_label.config(text=error or "Failed to connect to database. Please check database settings.")
        logger.error(f"❌ Failed to connect to database: {error or 'No connection'}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)
        return

    # Tabs for Sales and Purchases
    notebook = ttk.Notebook(main_frame)
    notebook.pack(pady=10, fill=tk.BOTH, expand=True)

    # Sales Tab
    sales_frame = tk.Frame(notebook, bg="#d7f7f2")
    notebook.add(sales_frame, text="Sales")

    # Purchases Tab
    purchases_frame = tk.Frame(notebook, bg="#d7f7f2")
    notebook.add(purchases_frame, text="Purchases")

    # Sales Treeview
    sales_tree_frame = tk.Frame(sales_frame)
    sales_tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    sales_columns = ("Select", "Sale ID", "User", "Total Amount", "Sale Date")
    sales_tree = ttk.Treeview(sales_tree_frame, columns=sales_columns, show="headings")
    sales_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    sales_column_widths = {"Select": 50, "Sale ID": 100, "User": 150, "Total Amount": 120, "Sale Date": 200}
    for col in sales_columns:
        sales_tree.heading(col, text=col)
        sales_tree.column(col, width=sales_column_widths[col], anchor="center")
    sales_scrollbar = ttk.Scrollbar(sales_tree_frame, orient="vertical", command=sales_tree.yview)
    sales_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    sales_tree.configure(yscrollcommand=sales_scrollbar.set)

    # Purchases Treeview
    purchases_tree_frame = tk.Frame(purchases_frame)
    purchases_tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    purchases_columns = ("Select", "Purchase ID", "User", "Total Amount", "Purchase Date")
    purchases_tree = ttk.Treeview(purchases_tree_frame, columns=purchases_columns, show="headings")
    purchases_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    purchases_column_widths = {"Select": 50, "Purchase ID": 100, "User": 150, "Total Amount": 120, "Purchase Date": 200}
    for col in purchases_columns:
        purchases_tree.heading(col, text=col)
        purchases_tree.column(col, width=purchases_column_widths[col], anchor="center")
    purchases_scrollbar = ttk.Scrollbar(purchases_tree_frame, orient="vertical", command=purchases_tree.yview)
    purchases_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    purchases_tree.configure(yscrollcommand=purchases_scrollbar.set)

    # Store selected items
    selected_sales = []
    selected_purchases = []

    def toggle_sale_selection(item):
        try:
            sale_id = sales_tree.item(item)['values'][1]
            if sale_id in selected_sales:
                selected_sales.remove(sale_id)
                sales_tree.set(item, "Select", "")
            else:
                selected_sales.append(sale_id)
                sales_tree.set(item, "Select", "✔")
            logger.info(f"✅ Toggled sale ID {sale_id} selection: {sale_id in selected_sales}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in toggle_sale_selection: {e}", exc_info=True)

    def toggle_purchase_selection(item):
        try:
            purchase_id = purchases_tree.item(item)['values'][1]
            if purchase_id in selected_purchases:
                selected_purchases.remove(purchase_id)
                purchases_tree.set(item, "Select", "")
            else:
                selected_purchases.append(purchase_id)
                purchases_tree.set(item, "Select", "✔")
            logger.info(f"✅ Toggled purchase ID {purchase_id} selection: {purchase_id in selected_purchases}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in toggle_purchase_selection: {e}", exc_info=True)

    def on_sales_click(event):
        item = sales_tree.identify_row(event.y)
        if item and sales_tree.identify_column(event.x) == "#1":  # Select column
            toggle_sale_selection(item)

    def on_purchases_click(event):
        item = purchases_tree.identify_row(event.y)
        if item and purchases_tree.identify_column(event.x) == "#1":  # Select column
            toggle_purchase_selection(item)

    sales_tree.bind("<Button-1>", on_sales_click)
    purchases_tree.bind("<Button-1>", on_purchases_click)

    def refresh_data():
        try:
            # Clear Treeviews
            for item in sales_tree.get_children():
                sales_tree.delete(item)
            for item in purchases_tree.get_children():
                purchases_tree.delete(item)
            selected_sales.clear()
            selected_purchases.clear()

            # Fetch Sales
            sales, error = fetch_sales(conn)
            if error:
                error_label.config(text=error)
                logger.error(f"❌ Failed to fetch sales: {error}")
                return
            for sale in sales:
                sales_tree.insert("", "end", values=("", sale[0], sale[2], f"${sale[3]:.2f}", sale[4]))

            # Fetch Purchases
            purchases, error = fetch_purchases(conn)
            if error:
                error_label.config(text=error)
                logger.error(f"❌ Failed to fetch purchases: {error}")
                return
            for purchase in purchases:
                purchases_tree.insert("", "end", values=("", purchase[0], purchase[2], f"${purchase[3]:.2f}", purchase[4]))

            logger.info("✅ Refreshed sales and purchases data")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in refresh_data: {e}", exc_info=True)

    def delete_selected():
        try:
            if not selected_sales and not selected_purchases:
                error_label.config(text="No records selected for deletion.")
                messagebox.showerror("Error", "No records selected for deletion.")
                logger.warning("❌ No records selected for deletion")
                return

            # Confirm deletion
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete the selected records? This cannot be undone."):
                logger.info("✅ Deletion cancelled by user")
                return

            # Delete sales
            if selected_sales:
                success, error = delete_sales(conn, selected_sales)
                if not success:
                    error_label.config(text=error or "Failed to delete sales.")
                    messagebox.showerror("Error", error or "Failed to delete sales.")
                    logger.error(f"❌ Failed to delete sales: {error}")
                    return

            # Delete purchases
            if selected_purchases:
                success, error = delete_purchases(conn, selected_purchases)
                if not success:
                    error_label.config(text=error or "Failed to delete purchases.")
                    messagebox.showerror("Error", error or "Failed to delete purchases.")
                    logger.error(f"❌ Failed to delete purchases: {error}")
                    return

            error_label.config(text="")
            messagebox.showinfo("Success", "✅ Selected records deleted successfully.")
            logger.info(f"✅ Deleted {len(selected_sales)} sales and {len(selected_purchases)} purchases")
            refresh_data()
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in delete_selected: {e}", exc_info=True)

    # Delete Button
    tk.Button(
        main_frame,
        text="Delete Selected",
        command=delete_selected,
        bg="#FF4444",
        fg="white",
        font=("Helvetica", 14)
    ).pack(pady=10)

    refresh_data()

    def on_close():
        conn.close()
        window.destroy()
        logger.info("✅ Delete data page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Delete data page opened")
    window.mainloop()