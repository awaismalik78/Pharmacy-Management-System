import tkinter as tk
from tkinter import messagebox, ttk
import logging
from delete_data import fetch_sales_details, delete_sale
from connections import get_user_details, create_connection

# Use existing logger (configured in dashboard.py)
logger = logging.getLogger(__name__)

def show_delete_data_page(username):
    window = tk.Toplevel()
    window.title("Delete Data")
    window.geometry("1000x600")
    window.configure(bg="#d7f7f2")

    # Error label
    error_label = tk.Label(window, text="", bg="#d7f7f2", fg="red", font=("Helvetica", 12), wraplength=900)
    error_label.pack(pady=10)

    # Main frame
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

    # Treeview to display all sales details
    tree_frame = tk.Frame(main_frame)
    tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    columns = ("Sale ID", "Medicine ID", "Medicine Name", "Quantity", "Selling Price")
    tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    column_widths = {"Sale ID": 100, "Medicine ID": 100, "Medicine Name": 200, "Quantity": 100, "Selling Price": 120}
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=column_widths[col], anchor="center")

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    def refresh_sales_details():
        """Populate Treeview with all sales details."""
        try:
            for row in tree.get_children():
                tree.delete(row)
            details, error = fetch_sales_details()
            if error:
                error_label.config(text=error)
                logger.error(f"❌ Failed to fetch sales details: {error}")
                return
            for detail in details:
                tree.insert("", "end", values=detail)
            logger.info("✅ Refreshed sales details in Treeview")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in refresh_sales_details: {e}", exc_info=True)

    def handle_delete_sale():
        """Delete the sale corresponding to the selected sales detail."""
        try:
            selected = tree.selection()
            if not selected:
                error_label.config(text="Please select a sale to delete.")
                messagebox.showwarning("Warning", "Please select a sale to delete.")
                logger.warning("❌ No sale selected for deletion")
                return
            # Get sale_id from the first selected row
            sale_id = tree.item(selected[0])['values'][0]
            if not messagebox.askyesno("Confirm", f"Are you sure you want to delete Sale ID {sale_id}?"):
                logger.info("✅ Sale deletion cancelled by user")
                return
            success, error = delete_sale(sale_id)
            if success:
                messagebox.showinfo("Success", "✅ Sale deleted successfully.")
                logger.info(f"✅ Sale ID {sale_id} deleted successfully")
                error_label.config(text="")
                refresh_sales_details()
            else:
                error_label.config(text=error or "Failed to delete sale.")
                messagebox.showerror("Error", error or "Failed to delete sale.")
                logger.error(f"❌ Failed to delete sale: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_delete_sale: {e}", exc_info=True)

    # Delete button
    tk.Button(main_frame, text="Delete Selected Sale", command=handle_delete_sale, bg="#FF4444", fg="white", font=("Helvetica", 14)).pack(pady=10)

    # Initial population of Treeview
    refresh_sales_details()

    def on_close():
        window.destroy()
        logger.info("✅ Delete data page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Delete data page opened")
    window.mainloop()