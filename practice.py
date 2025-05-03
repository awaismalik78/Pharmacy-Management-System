import tkinter as tk
from tkinter import messagebox
from login import login

def handle_login():
    username = entry_username.get()
    password = entry_password.get()
    
    if not username or not password:
        messagebox.showerror("Input Error", "Both fields are required!")
        return
    
    role = login(username, password)
    
    if role:
        messagebox.showinfo("Login Successful", f"Welcome, {username} ({role})!")
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# --- GUI Setup ---
root = tk.Tk()
root.title("Pharmacy Management Login")
root.geometry("1920x1080")
root.config(bg="#33c45a")

# --- Login Frame ---
frame = tk.Frame(root, bg="#41f070", bd=2, relief="flat")
frame.place(relx=0.5, rely=0.5, anchor="center", width=350, height=300)

# --- Title ---
title = tk.Label(frame, text="User Login", font=("Helvetica", 20, "bold"), bg="#FFFFFF", fg="#333")
title.pack(pady=15)

# --- Username Label ---
username_label = tk.Label(frame, text="Username", font=("Helvetica", 12), bg="#FFFFFF", fg="#333")
username_label.place(x=40, y=50)

# --- Username Shadow and Entry ---
username_shadow = tk.Frame(frame, bg="#A9A9A9")
username_shadow.place(x=42, y=75, width=230, height=30)

entry_username = tk.Entry(frame, font=("Helvetica", 12), bg="#F5F5F5", fg="#000", relief="flat")
entry_username.place(x=40, y=73, width=230, height=30)

# --- Password Label ---
password_label = tk.Label(frame, text="Password", font=("Helvetica", 12), bg="#FFFFFF", fg="#333")
password_label.place(x=40, y=110)

# --- Password Shadow and Entry ---
password_shadow = tk.Frame(frame, bg="#A9A9A9")
password_shadow.place(x=42, y=135, width=230, height=30)

entry_password = tk.Entry(frame, font=("Helvetica", 12), show="*", bg="#F5F5F5", fg="#000", relief="flat")
entry_password.place(x=40, y=133, width=230, height=30)

# --- Login Button ---
login_btn = tk.Button(frame, text="Login", font=("Helvetica", 12, "bold"), bg="#4CAF50", fg="#fff", relief="flat", command=handle_login)
login_btn.place(x=115, y=190, width=100, height=35)

# --- Footer ---
footer = tk.Label(root, text="Pharmacy Management System", font=("Helvetica", 10), bg="#E8F0FE", fg="#333")
footer.pack(side="bottom", pady=10)

root.mainloop()
