import tkinter as tk
from tkinter import messagebox
from connections import get_user_details
from manage_users_page import show_manage_users
from manage_medicines_page import show_manage_medicines
from sales_page import show_sales_page

from delete_data_page import show_delete_data_page  # Add import

def show_dashboard(username, login_callback=None):
    """
    Display the dashboard with role-based buttons.
    login_callback: Function to call on logout (e.g., show login page).
    """
    user_data = get_user_details(username)
    if not user_data:
        messagebox.showerror("Error", "Failed to fetch user details.")
        return

    user_id, username, role = user_data

    # Main Dashboard Window
    dashboard = tk.Tk()
    dashboard.title("Pharmacy Management Dashboard")
    dashboard.geometry("1920x1080")
    dashboard.configure(bg="#dafad9")

    # Welcome Message
    welcome_label = tk.Label(
        dashboard,
        text=f"Welcome {username} ({role})!",
        font=("Helvetica", 50, "bold"),
        bg="#dafad9",
        fg="#333"
    )
    welcome_label.pack(pady=20)

    # Button Frame for centering
    button_frame = tk.Frame(dashboard, bg="#dafad9")
    button_frame.pack(pady=20)

    # Button Configurations
    buttons = [
        
        {"text": "Sales", "command": lambda: show_sales_page(username), "width": 30},
       
    ]

    # Owner-specific buttons
    if role.lower() == 'owner':
        buttons.extend([
            {"text": "Manage Medicines", "command": lambda: show_manage_medicines(username), "width": 30},
            {"text": "Delete Data", "command": lambda: show_delete_data_page(username), "width": 30},  # Updated
            {"text": "Manage Users", "command": lambda: show_manage_users(username), "width": 30},
        ])

    # Create Buttons
    for btn in buttons:
        tk.Button(
            button_frame,
            text=btn["text"],
            width=btn["width"],
            font=("Helvetica", 25),
            bg="#81f77c",
            relief="flat",
            command=btn["command"]
        ).pack(pady=12)

    # Logout Button
    tk.Button(
        button_frame,
        text="Logout",
        width=20,
        command=lambda: logout(dashboard, login_callback),
        bg="red",
        fg="white",
        font=("Helvetica", 20, "bold"),
        relief="flat"
    ).pack(pady=30)

    dashboard.mainloop()

def logout(dashboard, login_callback):
    """Close dashboard and call login callback if provided."""
    dashboard.destroy()
    if login_callback:
        login_callback()

# Example usage (replace with login page call)
#show_dashboard("admin", lambda: print("Show login page"))