import tkinter as tk
from tkinter import messagebox, ttk
from manage_users import fetch_all_users, add_user, delete_user

def show_manage_users():
    window = tk.Toplevel()
    window.title("Manage Users")
    window.geometry("1920x1080")
    window.configure(bg="#dafad9")

    def refresh_user_list():
        for row in tree.get_children():
            tree.delete(row)
        for user in fetch_all_users():
            tree.insert("", "end", values=user)

    def handle_add_user():
        username = entry_username.get()
        password = entry_password.get()
        role_id = entry_role.get()
        if not username or not password or not role_id:
            messagebox.showerror("Error", "All fields required!")
            return
        if add_user(username, password, int(role_id)):
            
            refresh_user_list()
        else:
            messagebox.showerror("Error", "Failed to add user.")

    def handle_delete_user():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a user first!")
            return
        user_id = tree.item(selected)['values'][0]
        if delete_user(user_id):
            refresh_user_list()
        else:
            messagebox.showerror("Error", "Failed to delete user.")

    # --- User List ---
    tree = ttk.Treeview(window, columns=("ID", "Username", "Role", "Created At"), show="headings")
    tree.heading("ID", text="ID")
    tree.heading("Username", text="Username")
    tree.heading("Role", text="Role")
    tree.heading("Created At", text="Created At")
    tree.pack(pady=10, fill="x", padx=20)

    delete_btn = tk.Button(window, text="Delete Selected User", command=handle_delete_user, bg="red", fg="white",font=("Helvetica", 15))
    delete_btn.pack(pady=10)

    # --- Form Frame ---
    form = tk.Frame(window, bg="#DFFFD6")
    form.pack(pady=20)

    tk.Label(form, text="Username:", bg="#DFFFD6",font=("Helvetica", 20)).grid(row=0, column=0, padx=10, pady=5)
    entry_username = tk.Entry(form,font=("Helvetica", 15))
    entry_username.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form, text="Password:", bg="#DFFFD6",font=("Helvetica", 20)).grid(row=0, column=2, padx=10, pady=5)
    entry_password = tk.Entry(form,font=("Helvetica", 15), show="*")
    entry_password.grid(row=0, column=3, padx=10, pady=5)

    tk.Label(form, text="Role ID (1=Owner, 2=Worker):", bg="#DFFFD6",font=("Helvetica", 20)).grid(row=0, column=4, padx=10, pady=5)
    entry_role = tk.Entry(form,font=("Helvetica", 15))
    entry_role.grid(row =0, column=5, padx=10, pady=5)

    form2 = tk.Frame(window, bg="#DFFFD6")
    form2.pack()
    add_btn = tk.Button(form2, text="Add User", command=handle_add_user, bg="#4CAF50", fg="white",font=("Helvetica", 15))
    add_btn.grid()

    

    refresh_user_list()
