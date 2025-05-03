# dashboard.py
import tkinter as tk
from tkinter import messagebox
from dashboard import get_user_details
from manage_users_page import show_manage_users

def show_dashboard(username):
    user_data = get_user_details(username)
    if not user_data:
        messagebox.showerror("Error", "Failed to fetch user details.")
        return

    user_id, username, role = user_data

    # --- Main Dashboard Window ---
    dashboard = tk.Tk()
    dashboard.title("Pharmacy Management Dashboard")
    dashboard.geometry("1920x1080")
    dashboard.configure(bg="#dafad9")

    # --- Welcome Message ---
    welcome_label = tk.Label(
        dashboard,
        text=f"Welcome {username} ({role})!",
        font=("Helvetica", 50, "bold"),
        bg="#dafad9",
        fg="#333"
    )
    welcome_label.pack(pady=20)

    # --- Buttons (Owner-specific features are shown conditionally) ---
    tk.Button(dashboard, text="Manage Medicines", width=30,font=("Helvetica", 25),bg="#81f77c",relief="flat").pack(pady=12)
    tk.Button(dashboard, text="Sales", width=30,font=("Helvetica", 25),bg="#81f77c",relief="flat").pack(pady=12)
    tk.Button(dashboard, text="Purchases", width=30,font=("Helvetica", 25),bg="#81f77c",relief="flat").pack(pady=12)

    if role.lower() == 'owner':
        tk.Button(dashboard, text="Delete Data", width=30,font=("Helvetica", 25),bg="#81f77c",relief="flat").pack(pady=12)
        tk.Button(dashboard, text="Manage Users", width=30,font=("Helvetica", 25),bg="#81f77c",relief="flat",command=show_manage_users).pack(pady=12)

    # --- Logout Button ---
    tk.Button(dashboard, text="Logout", width=20, command=dashboard.destroy, bg="red", fg="white",font=("Helvetica", 20,"bold"),relief="flat").pack(pady=30)

    dashboard.mainloop()
show_dashboard("admin")