import tkinter as tk
from tkinter import ttk, messagebox
from database import add_vehicle, get_vehicles, delete_vehicle, update_vehicle, update_vehicle_status

def load_fleet_ui(main_content_frame):
    header_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)

    ttk.Label(header_frame, text="Fleet Management", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)

    ttk.Button(header_frame, text="+ Add New Vehicle",
               command=lambda: open_add_vehicle_popup(main_content_frame, tree)).pack(side=tk.RIGHT)
    
    table_frame = tk.Frame(main_content_frame, bg="#ecf0f1", bd=1, relief=tk.SOLID)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    columns = ("ID", "Capacity", "Maintenance Schedule", "Status")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    tree.heading("ID", text="Vehicle ID")
    tree.heading("Capacity", text="Capacity")
    tree.heading("Maintenance Schedule", text="Maintenance Schedule")
    tree.heading("Status", text="Availability")

    tree.column("ID", width=80, anchor=tk.CENTER)
    tree.column("Capacity", width=200, anchor=tk.CENTER)
    tree.column("Maintenance Schedule", width=200, anchor=tk.CENTER)
    tree.column("Status", width=120, anchor=tk.CENTER)


    tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)


    action_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

    ttk.Label(action_frame, text="Update Status:", font=("Arial", 10, "bold"), background="#ecf0f1").pack(side=tk.LEFT, padx=(0, 5))
    combo_status = ttk.Combobox(action_frame, values=["Available", "Unavailable"], state="readonly", width=15)
    combo_status.set("Select Status")
    combo_status.pack(side=tk.LEFT, padx=(0, 10))
    ttk.Button(action_frame, text="Update Status", command=lambda: change_status(tree, combo_status)).pack(side=tk.LEFT)

    ttk.Button(action_frame, text="Delete Vehicle", command=lambda: delete_selected_vehicle(tree)).pack(side=tk.RIGHT, padx=(10, 0))
    ttk.Button(action_frame, text="Edit Details", command=lambda: open_add_vehicle_popup(main_content_frame, tree, is_edit=True)).pack(side=tk.RIGHT)

    refresh_table(tree)


def open_add_vehicle_popup(parent, tree, is_edit=False):
    selected_id = None
    if is_edit:
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a vehicle to edit.")
            return
        
        selected_id = int(tree.item(selected_item[0], "values")[0].replace("VEH-", ""))
        current_cap = tree.item(selected_item[0], "values")[1]
        current_maint = tree.item(selected_item[0], "values")[2]
        current_status = tree.item(selected_item[0], "values")[3]

    popup = tk.Toplevel(parent)
    title_text = "Edit Vehicle Details" if is_edit else "Add New Vehicle"
    popup.title(title_text)
    popup.geometry("400x300")
    popup.grab_set()
    popup.resizable(False, False)

    ttk.Label(popup, text=title_text, font=("Arial", 14, "bold")).pack(pady=15)

    form_frame = tk.Frame(popup)
    form_frame.pack(pady=10)

    ttk.Label(form_frame, text="Capacity (e.g. 2000kg):").grid(row=0, column=0, sticky="W", pady=5)
    entry_cap = ttk.Entry(form_frame, width=25)
    entry_cap.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Maintenance (e.g. Monthly):").grid(row=1, column=0, sticky="W", pady=5)
    entry_maint = ttk.Entry(form_frame, width=25)
    entry_maint.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Is Available?:").grid(row=2, column=0, sticky="W", pady=5)
    combo_avail = ttk.Combobox(form_frame, values=["Yes", "No"], state="readonly", width=22)
    combo_avail.grid(row=2, column=1, padx=10, pady=5)

    if is_edit:
        entry_cap.insert(0, current_cap)
        entry_maint.insert(0, current_maint)
        combo_avail.set("Yes" if current_status == "Available" else "No")
    else:
        combo_avail.set("Yes")

    ttk.Button(popup, text="Save Vehicle",
               command=lambda: save_vehicle(popup, tree, entry_cap, entry_maint, combo_avail, selected_id)).pack(pady=20)


def save_vehicle(popup, tree, entry_cap, entry_maint, combo_avail, selected_id=None):
    capacity = entry_cap.get().strip()
    maintenance = entry_maint.get().strip()
    availability = combo_avail.get()

    if not capacity or not maintenance or not availability:
        messagebox.showerror("Input Error", "All fields are required.", parent=popup)
        return
    

    is_available = 1 if availability == "Yes" else 0

    if selected_id is not None:
        success = update_vehicle(selected_id, capacity, maintenance, is_available)
        msg = "Vehicle updated successfully."
    else:
        success = add_vehicle(capacity, maintenance, is_available)
        msg = "Vehicle added successfully."

    if success:
        messagebox.showinfo("Success", msg, parent=popup)
        refresh_table(tree)
        popup.destroy()
    else:
        messagebox.showerror("Database Error", "Failed to save vehicle.", parent=popup)


def change_status(tree, combo_status):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a vehicle to update.")
        return
    
    vehicle_id = int(tree.item(selected_item[0], "values")[0].replace("VEH-", ""))
    new_status = combo_status.get()

    if new_status not in ["Available", "Unavailable"]:
        messagebox.showwarning("Input Error", "Please select a valid status.")
        return

    is_available = 1 if new_status == "Available" else 0

    if update_vehicle_status(vehicle_id, is_available):
        messagebox.showinfo("Success", f"Vehicle status updated to '{new_status}'.")
        refresh_table(tree)
    else:
        messagebox.showerror("Database Error", "Failed to update vehicle status.")


def delete_selected_vehicle(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a vehicle to delete.")
        return

    vehicle_id = int(tree.item(selected_item[0], "values")[0].replace("VEH-", ""))
    
    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete Vehicle ID {vehicle_id}?")
    if confirm:
        success, error_msg = delete_vehicle(vehicle_id)
        if success:
            messagebox.showinfo("Deleted", "Vehicle has been deleted.")
            refresh_table(tree)
        else:
            messagebox.showerror("Error", error_msg)


def refresh_table(tree):
    for row in tree.get_children():
        tree.delete(row)

    vehicles = get_vehicles()

    for v in vehicles:
        status = "Available" if str(v[3]) == "1" else "Unavailable"
        tree.insert("", tk.END, iid=v[0], values=(f"VEH-{v[0]}", v[1], v[2], status))