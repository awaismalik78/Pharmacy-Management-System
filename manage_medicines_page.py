import tkinter as tk
from tkinter import messagebox, ttk
import logging
from manage_medicines import fetch_all_medicines, add_medicine, update_medicine, delete_medicine
from connections import get_user_details, create_connection

# Configure logging (move to dashboard.py)
logger = logging.getLogger(__name__)

def show_manage_medicines(username):
    window = tk.Toplevel()
    window.title("Manage Medicines")
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

    # Treeview
    tree_frame = tk.Frame(main_frame, bg="#d7f7f2")
    tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    tree = ttk.Treeview(tree_frame, columns=("ID", "Name", "Quantity", "Price"), show="headings")
    tree.heading("ID", text="ID")
    tree.column("ID", width=100, anchor="center")
    tree.heading("Name", text="Name")
    tree.column("Name", width=300, anchor="center")
    tree.heading("Quantity", text="Quantity")
    tree.column("Quantity", width=150, anchor="center")
    tree.heading("Price", text="Price")
    tree.column("Price", width=150, anchor="center")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Entry Form
    form = tk.Frame(main_frame, bg="#d7f7f2")
    form.pack(pady=20)

    tk.Label(form, text="Name:", bg="#d7f7f2", font=("Helvetica", 12)).grid(row=0, column=0, padx=10, pady=5)
    entry_name = tk.Entry(form, font=("Helvetica", 12))
    entry_name.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form, text="Quantity:", bg="#d7f7f2", font=("Helvetica", 12)).grid(row=0, column=2, padx=10, pady=5)
    entry_quantity = tk.Entry(form, font=("Helvetica", 12))
    entry_quantity.grid(row=0, column=3, padx=10, pady=5)

    tk.Label(form, text="Price:", bg="#d7f7f2", font=("Helvetica", 12)).grid(row=0, column=4, padx=10, pady=5)
    entry_price = tk.Entry(form, font=("Helvetica", 12))
    entry_price.grid(row=0, column=5, padx=10, pady=5)

    # Buttons
    btn_frame = tk.Frame(main_frame, bg="#d7f7f2")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add", bg="#4CAF50", fg="white", font=("Helvetica", 12), command=lambda: handle_add()).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Update", bg="orange", fg="white", font=("Helvetica", 12), command=lambda: handle_update()).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Delete", bg="#FF4444", fg="white", font=("Helvetica", 12), command=lambda: handle_delete()).grid(row=0, column=2, padx=10)

    def refresh_medicine_list():
        try:
            for row in tree.get_children():
                tree.delete(row)
            medicines, error = fetch_all_medicines()
            if error:
                error_label.config(text=error)
                logger.error(f"❌ Failed to fetch medicines: {error}")
                return
            for med in medicines:
                tree.insert("", "end", values=med)
            logger.info("✅ Refreshed medicine list")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in refresh_medicine_list: {e}", exc_info=True)

    def handle_add():
        try:
            name = entry_name.get().strip()
            qty = entry_quantity.get().strip()
            price = entry_price.get().strip()
            if not name or not qty or not price:
                error_label.config(text="All fields are required.")
                messagebox.showerror("Error", "All fields are required.")
                logger.warning("❌ Missing required fields")
                return
            qty = int(qty)
            price = float(price)
            if qty < 0 or price < 0:
                error_label.config(text="Quantity and Price must be non-negative.")
                messagebox.showerror("Error", "Quantity and Price must be non-negative.")
                logger.warning("❌ Invalid quantity or price")
                return
            success, error = add_medicine(name, qty, price)
            if success:
                refresh_medicine_list()
                clear_fields()
                error_label.config(text="")
                messagebox.showinfo("Success", "Medicine added successfully.")
                logger.info(f"✅ Added medicine: {name}")
            else:
                error_label.config(text=error or "Failed to add medicine.")
                messagebox.showerror("Error", error or "Failed to add medicine.")
                logger.error(f"❌ Failed to add medicine: {error}")
        except ValueError:
            error_label.config(text="Quantity and Price must be numbers.")
            messagebox.showerror("Error", "Quantity and Price must be numbers.")
            logger.warning("❌ Invalid number format")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_add: {e}", exc_info=True)

    def handle_update():
        try:
            selected = tree.focus()
            if not selected:
                error_label.config(text="Select a medicine first.")
                messagebox.showwarning("Warning", "Select a medicine first!")
                logger.warning("❌ No medicine selected")
                return
            med_id = tree.item(selected)['values'][0]
            name = entry_name.get().strip()
            qty = entry_quantity.get().strip()
            price = entry_price.get().strip()
            if not name or not qty or not price:
                error_label.config(text="All fields are required.")
                messagebox.showerror("Error", "All fields are required.")
                logger.warning("❌ Missing required fields")
                return
            qty = int(qty)
            price = float(price)
            if qty < 0 or price < 0:
                error_label.config(text="Quantity and Price must be non-negative.")
                messagebox.showerror("Error", "Quantity and Price must be non-negative.")
                logger.warning("❌ Invalid quantity or price")
                return
            success, error = update_medicine(med_id, name, qty, price)
            if success:
                refresh_medicine_list()
                clear_fields()
                error_label.config(text="")
                messagebox.showinfo("Success", "Medicine updated successfully.")
                logger.info(f"✅ Updated medicine ID: {med_id}")
            else:
                error_label.config(text=error or "Failed to update medicine.")
                messagebox.showerror("Error", error or "Failed to update medicine.")
                logger.error(f"❌ Failed to update medicine: {error}")
        except ValueError:
            error_label.config(text="Quantity and Price must be numbers.")
            messagebox.showerror("Error", "Quantity and Price must be numbers.")
            logger.warning("❌ Invalid number format")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_update: {e}", exc_info=True)

    def handle_delete():
        try:
            selected = tree.focus()
            if not selected:
                error_label.config(text="Select a medicine to delete.")
                messagebox.showwarning("Warning", "Select a medicine to delete.")
                logger.warning("❌ No medicine selected")
                return
            med_id = tree.item(selected)['values'][0]
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this medicine?"):
                logger.info("✅ Deletion cancelled by user")
                return
            success, error = delete_medicine(med_id)
            if success:
                refresh_medicine_list()
                clear_fields()
                error_label.config(text="")
                messagebox.showinfo("Success", "Medicine deleted successfully.")
                logger.info(f"✅ Deleted medicine ID: {med_id}")
            else:
                error_label.config(text=error or "Failed to delete medicine.")
                messagebox.showerror("Error", error or "Failed to delete medicine.")
                logger.error(f"❌ Failed to delete medicine: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_delete: {e}", exc_info=True)

    def clear_fields():
        entry_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_price.delete(0, tk.END)

    def on_select(event):
        try:
            selected = tree.focus()
            if selected:
                values = tree.item(selected)['values']
                clear_fields()
                entry_name.insert(0, values[1])
                entry_quantity.insert(0, values[2])
                entry_price.insert(0, values[3])
                logger.info(f"✅ Selected medicine ID: {values[0]}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in on_select: {e}", exc_info=True)

    tree.bind("<<TreeviewSelect>>", on_select)
    refresh_medicine_list()

    def on_close():
        window.destroy()
        logger.info("✅ Manage medicines page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Manage medicines page opened")
    window.mainloop()