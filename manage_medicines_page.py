import tkinter as tk
from tkinter import messagebox, ttk
from manage_medicines import fetch_all_medicines, add_medicine, update_medicine, delete_medicine

def show_manage_medicines():
    window = tk.Toplevel()
    window.title("Manage Medicines")
    window.geometry("1000x600")
    window.configure(bg="#e0fff4")

    def refresh_medicine_list():
        for row in tree.get_children():
            tree.delete(row)
        for med in fetch_all_medicines():
            tree.insert("", "end", values=med)

    def handle_add():
        name = entry_name.get()
        qty = entry_quantity.get()
        price = entry_price.get()
        if not name or not qty or not price:
            messagebox.showerror("Error", "All fields are required.")
            return
        try:
            if add_medicine(name, int(qty), float(price)):
                refresh_medicine_list()
                clear_fields()
            else:
                messagebox.showerror("Error", "Failed to add medicine.")
        except:
            messagebox.showerror("Error", "Quantity and Price must be numbers.")

    def handle_update():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a medicine first!")
            return
        med_id = tree.item(selected)['values'][0]
        name = entry_name.get()
        qty = entry_quantity.get()
        price = entry_price.get()
        if update_medicine(med_id, name, int(qty), float(price)):
            refresh_medicine_list()
            clear_fields()
        else:
            messagebox.showerror("Error", "Failed to update medicine.")

    def handle_delete():
        selected = tree.focus()
        if not selected:
            messagebox.showwarning("Warning", "Select a medicine to delete.")
            return
        med_id = tree.item(selected)['values'][0]
        if delete_medicine(med_id):
            refresh_medicine_list()
            clear_fields()
        else:
            messagebox.showerror("Error", "Failed to delete medicine.")

    def clear_fields():
        entry_name.delete(0, tk.END)
        entry_quantity.delete(0, tk.END)
        entry_price.delete(0, tk.END)

    def on_select(event):
        selected = tree.focus()
        if selected:
            values = tree.item(selected)['values']
            entry_name.delete(0, tk.END)
            entry_name.insert(0, values[1])
            entry_quantity.delete(0, tk.END)
            entry_quantity.insert(0, values[2])
            entry_price.delete(0, tk.END)
            entry_price.insert(0, values[3])

    # --- Treeview ---
    tree = ttk.Treeview(window, columns=("ID", "Name", "Quantity", "Price"), show="headings")
    for col in ("ID", "Name", "Quantity", "Price"):
        tree.heading(col, text=col)
    tree.pack(fill="x", padx=20, pady=10)
    tree.bind("<<TreeviewSelect>>", on_select)

    # --- Entry Form ---
    form = tk.Frame(window, bg="#d0ffe1")
    form.pack(pady=20)

    tk.Label(form, text="Name:", bg="#d0ffe1").grid(row=0, column=0, padx=10, pady=5)
    entry_name = tk.Entry(form)
    entry_name.grid(row=0, column=1, padx=10, pady=5)

    tk.Label(form, text="Quantity:", bg="#d0ffe1").grid(row=0, column=2, padx=10, pady=5)
    entry_quantity = tk.Entry(form)
    entry_quantity.grid(row=0, column=3, padx=10, pady=5)

    tk.Label(form, text="Price:", bg="#d0ffe1").grid(row=0, column=4, padx=10, pady=5)
    entry_price = tk.Entry(form)
    entry_price.grid(row=0, column=5, padx=10, pady=5)

    # --- Buttons ---
    btn_frame = tk.Frame(window, bg="#e0fff4")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="Add", bg="green", fg="white", command=handle_add).grid(row=0, column=0, padx=10)
    tk.Button(btn_frame, text="Update", bg="orange", fg="white", command=handle_update).grid(row=0, column=1, padx=10)
    tk.Button(btn_frame, text="Delete", bg="red", fg="white", command=handle_delete).grid(row=0, column=2, padx=10)

    refresh_medicine_list()
