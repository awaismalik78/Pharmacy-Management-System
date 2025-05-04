import tkinter as tk
from tkinter import messagebox, ttk
import logging
from manage_users import fetch_all_users, add_user, update_user, delete_user
from connections import get_user_details, create_connection

# Configure logging (move to dashboard.py)
logger = logging.getLogger(__name__)

def show_manage_users(username):
    window = tk.Toplevel()
    window.title("Manage Users")
    window.geometry("1920x1080")
    window.configure(bg="#d7f7f2")

    # Error label
    error_label = tk.Label(window, text="", bg="#d7f7f2", fg="red", font=("Helvetica", 15), wraplength=1800)
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
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 15)).pack(pady=10)
        return
    user_id, username, role = user_data
    if role.lower() != 'owner':
        error_label.config(text="Unauthorized access. Owner privileges required.")
        logger.error(f"❌ Unauthorized access for {username}: role is {role}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 15)).pack(pady=10)
        return

    # Fetch roles for dropdown
    conn, error = create_connection()
    if error or not conn:
        error_label.config(text=error or "Failed to connect to database.")
        logger.error(f"❌ Failed to connect to database: {error or 'No connection'}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=window.destroy, bg="#FF4444", fg="white", font=("Helvetica", 15)).pack(pady=10)
        return
    try:
        cur = conn.cursor()
        cur.execute("SELECT role_id, role_name FROM roles ORDER BY role_id")
        roles = cur.fetchall()
        role_dict = {role_name: role_id for role_id, role_name in roles}
    except Exception as e:
        error_label.config(text=f"Error fetching roles: {str(e)}")
        logger.error(f"❌ Error fetching roles: {e}")
        main_frame.pack_forget()
        tk.Button(window, text="Close", command=lambda: (conn.close(), window.destroy()), bg="#FF4444", fg="white", font=("Helvetica", 15)).pack(pady=10)
        return
    finally:
        conn.close()

    # Treeview
    tree_frame = tk.Frame(main_frame, bg="#d7f7f2")
    tree_frame.pack(pady=10, fill=tk.BOTH, expand=True)
    tree = ttk.Treeview(tree_frame, columns=("ID", "Username", "Role", "Created At"), show="headings")
    tree.heading("ID", text="ID")
    tree.column("ID", width=100, anchor="center")
    tree.heading("Username", text="Username")
    tree.column("Username", width=200, anchor="center")
    tree.heading("Role", text="Role")
    tree.column("Role", width=150, anchor="center")
    tree.heading("Created At", text="Created At")
    tree.column("Created At", width=200, anchor="center")
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    # Scrollbar
    scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    tree.configure(yscrollcommand=scrollbar.set)

    # Form Frame
    form = tk.Frame(main_frame, bg="#d7f7f2")
    form.pack(pady=20)

    tk.Label(form, text="Username:", bg="#d7f7f2", font=("Helvetica", 20)).grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(form, font=("Helvetica", 15))
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form, text="Password:", bg="#d7f7f2", font=("Helvetica", 20)).grid(row=0, column=2, padx=10, pady=5)
    entry_password = tk.Entry(form, font=("Helvetica", 15), show="*")
    entry_password.grid(row=0, column=3, padx=10, pady=5)

    tk.Label(form, text="Role:", bg="#d7f7f2", font=("Helvetica", 20)).grid(row=0, column=4, padx=10, pady=5)
    role_var = tk.StringVar()
    role_dropdown = ttk.Combobox(form, textvariable=role_var, values=list(role_dict.keys()), state="readonly", font=("Helvetica", 15))
    role_dropdown.grid(row=0, column=5, padx=10, pady=5)

    # Buttons
    btn_frame = tk.Frame(main_frame, bg="#d7f7f2")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add User", bg="#4CAF50", fg="white", font=("Helvetica", 15), command=lambda: handle_add_user()).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Update User", bg="orange", fg="white", font=("Helvetica", 15), command=lambda: handle_update_user()).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Delete User", bg="#FF4444", fg="white", font=("Helvetica", 15), command=lambda: handle_delete_user()).grid(row=0, column=2, padx=10)

    def refresh_user_list():
        try:
            for row in tree.get_children():
                tree.delete(row)
            users, error = fetch_all_users()
            if error:
                error_label.config(text=error)
                logger.error(f"❌ Failed to fetch users: {error}")
                return
            for user in users:
                tree.insert("", "end", values=user)
            logger.info("✅ Refreshed user list")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in refresh_user_list: {e}", exc_info=True)

    def handle_add_user():
        try:
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            role_name = role_var.get()
            if not username or not password or not role_name:
                error_label.config(text="All fields are required.")
                messagebox.showerror("Error", "All fields are required.")
                logger.warning("❌ Missing required fields")
                return
            role_id = role_dict.get(role_name)
            success, error = add_user(username, password, role_id)
            if success:
                refresh_user_list()
                clear_fields()
                error_label.config(text="")
                messagebox.showinfo("Success", "User added successfully.")
                logger.info(f"✅ Added user: {username}")
            else:
                error_label.config(text=error or "Failed to add user.")
                messagebox.showerror("Error", error or "Failed to add user.")
                logger.error(f"❌ Failed to add user: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_add_user: {e}", exc_info=True)

    def handle_update_user():
        try:
            selected = tree.focus()
            if not selected:
                error_label.config(text="Select a user first.")
                messagebox.showwarning("Warning", "Select a user first!")
                logger.warning("❌ No user selected")
                return
            selected_user_id = tree.item(selected)['values'][0]
            username = entry_username.get().strip()
            password = entry_password.get().strip()
            role_name = role_var.get()
            if not username or not role_name:
                error_label.config(text="Username and Role are required.")
                messagebox.showerror("Error", "Username and Role are required.")
                logger.warning("❌ Missing required fields")
                return
            role_id = role_dict.get(role_name)
            success, error = update_user(selected_user_id, username, password, role_id)
            if success:
                refresh_user_list()
                clear_fields()
                error_label.config(text="")
                messagebox.showinfo("Success", "User updated successfully.")
                logger.info(f"✅ Updated user ID: {selected_user_id}")
            else:
                error_label.config(text=error or "Failed to update user.")
                messagebox.showerror("Error", error or "Failed to update user.")
                logger.error(f"❌ Failed to update user: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_update_user: {e}", exc_info=True)

    def handle_delete_user():
        try:
            selected = tree.focus()
            if not selected:
                error_label.config(text="Select a user to delete.")
                messagebox.showwarning("Warning", "Select a user to delete.")
                logger.warning("❌ No user selected")
                return
            selected_user_id = tree.item(selected)['values'][0]
            if selected_user_id == user_id:  # Prevent deleting current user
                error_label.config(text="Cannot delete the current user.")
                messagebox.showerror("Error", "Cannot delete the current user.")
                logger.warning("❌ Attempted to delete current user")
                return
            if not messagebox.askyesno("Confirm", "Are you sure you want to delete this user?"):
                logger.info("✅ Deletion cancelled by user")
                return
            success, error = delete_user(selected_user_id)
            if success:
                refresh_user_list()
                clear_fields()
                error_label.config(text="")
                messagebox.showinfo("Success", "User deleted successfully.")
                logger.info(f"✅ Deleted user ID: {selected_user_id}")
            else:
                error_label.config(text=error or "Failed to delete user.")
                messagebox.showerror("Error", error or "Failed to delete user.")
                logger.error(f"❌ Failed to delete user: {error}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            messagebox.showerror("Error", f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in handle_delete_user: {e}", exc_info=True)

    def clear_fields():
        entry_username.delete(0, tk.END)
        entry_password.delete(0, tk.END)
        role_var.set("")

    def on_select(event):
        try:
            selected = tree.focus()
            if selected:
                values = tree.item(selected)['values']
                clear_fields()
                entry_username.insert(0, values[1])
                role_var.set(values[2])
                logger.info(f"✅ Selected user ID: {values[0]}")
        except Exception as e:
            error_label.config(text=f"Unexpected error: {str(e)}")
            logger.error(f"❌ Unexpected error in on_select: {e}", exc_info=True)

    tree.bind("<<TreeviewSelect>>", on_select)
    refresh_user_list()

    def on_close():
        window.destroy()
        logger.info("✅ Manage users page closed")
    window.protocol("WM_DELETE_WINDOW", on_close)

    logger.info("✅ Manage users page opened")
    window.mainloop()