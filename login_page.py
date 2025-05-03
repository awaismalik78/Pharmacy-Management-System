import tkinter as tk
from tkinter import messagebox
from login import login
from dashboard_page import show_dashboard

def handle_login():
    username = entry_username.get()
    password = entry_password.get()
    
    if not username or not password:
        messagebox.showerror("Input Error", "Both fields are required!")
        return
    
    role = login(username, password)
    
    if role:
        
        root.destroy()  # ✅ Close login window
        show_dashboard(username)  # ✅ Open dashboard
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

# --- GUI Setup ---
root = tk.Tk()
root.title("Pharmacy Management Login")
root.geometry("1920x1080")
root.config(bg="#dafad9")

# --- Login Frame ---
frame = tk.Frame(root, bg="#81f77c", bd=2, relief="flat")
frame.place(relx=0.5, rely=0.5, anchor="center", width=450, height=300)

# --- Title ---
title = tk.Label(frame, text="WELLCOME", font=("Helvetica", 20, "bold"), bg="#81f77c", fg="#333")
title.pack(pady=15)

# --- Username Label ---
username_label = tk.Label(frame, text="Username", font=("Helvetica", 12), bg="#81f77c", fg="#333")
username_label.place(x=100, y=70)

# --- Username Shadow and Entry ---
username_shadow = tk.Frame(frame, bg="#A9A9A9")
username_shadow.place(x=102, y=95, width=230, height=30)

entry_username = tk.Entry(frame, font=("Helvetica", 12), bg="#ecfceb", fg="#000", relief="flat")
entry_username.place(x=100, y=93, width=230, height=30)

# --- Password Label ---
password_label = tk.Label(frame, text="Password", font=("Helvetica", 12), bg="#81f77c", fg="#333")
password_label.place(x=100, y=130)

# --- Password Shadow and Entry ---
password_shadow = tk.Frame(frame, bg="#A9A9A9")
password_shadow.place(x=102, y=155, width=230, height=30)

entry_password = tk.Entry(frame, font=("Helvetica", 12), show="*", bg="#ecfceb", fg="#000", relief="flat")
entry_password.place(x=100, y=153, width=230, height=30)

# --- Login Button ---
login_btn = tk.Button(frame, text="Login", font=("Helvetica", 15, "bold"), bg="#ff0008", fg="#fff", relief="flat", command=handle_login)
login_btn.place(x=163, y=210, width=120, height=45)

# --- Footer ---
footer = tk.Label(root, text="Pharmacy Management System", font=("Helvetica", 10), bg="#E8F0FE", fg="#333")
footer.pack(side="bottom", pady=10)

root.mainloop()
