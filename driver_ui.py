import tkinter as tk
from tkinter import ttk, messagebox
from database import add_driver, get_drivers, delete_driver, update_driver_details

def load_driver_ui(main_content_frame):
    header_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)

    ttk.Label(header_frame, text="Driver Management", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)

    ttk.Button(header_frame, text="+ Add New Driver",
               command=lambda: open_add_driver_popup(main_content_frame, tree)).pack(side=tk.RIGHT)
    
    table_frame = tk.Frame(main_content_frame, bg="#ecf0f1", bd=1, relief=tk.SOLID)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    columns = ("ID", "Driver Name", "License", "Shift", "Route History")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    tree.heading("ID", text="Driver ID")
    tree.heading("Driver Name", text="Driver Name")
    tree.heading("License", text="License No.")
    tree.heading("Shift", text="Shift")
    tree.heading("Route History", text="Route History")

    tree.column("ID", width=100, anchor=tk.CENTER)
    tree.column("Driver Name", width=120, anchor=tk.CENTER)
    tree.column("License", width=200, anchor=tk.CENTER)
    tree.column("Shift", width=150, anchor=tk.CENTER)
    tree.column("Route History", width=200, anchor=tk.CENTER)

    tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

    action_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

    ttk.Button(action_frame, text="Delete Driver", command=lambda: delete_selected_driver(tree)).pack(side=tk.RIGHT, padx=(10, 0))
    ttk.Button(action_frame, text="Edit Details", command=lambda: open_add_driver_popup(main_content_frame, tree, is_edit=True)).pack(side=tk.RIGHT, padx=(10, 0))

    refresh_table(tree)

def open_add_driver_popup(parent, tree, is_edit=False):
    selected_id = None
    if is_edit:
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a driver to edit.")
            return
    
        drv_values = tree.item(selected_item[0], "values")
        selected_id = int(drv_values[0].replace("DRV-", ""))
        current_name = drv_values[1]
        current_license = drv_values[2]
        current_shift = drv_values[3]
        current_route = drv_values[4]

    popup = tk.Toplevel(parent)
    title_text = "Edit Driver Details" if is_edit else "Add New Driver"
    popup.title(title_text)
    popup.geometry("400x250")
    popup.grab_set()
    popup.resizable(False, False)

    ttk.Label(popup, text="Driver Details", font=("Arial", 14, "bold")).pack(pady=15)

    form_frame = tk.Frame(popup)
    form_frame.pack(pady=10)

    ttk.Label(form_frame, text="Driver Name:").grid(row=0, column=0, sticky="W", pady=5)
    entry_driver_name = ttk.Entry(form_frame, width=22)
    entry_driver_name.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="License Number:").grid(row=1, column=0, sticky="W", pady=5)
    entry_license = ttk.Entry(form_frame, width=22)
    entry_license.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Shift Assignment:").grid(row=2, column=0, sticky="W", pady=5)
    combo_shift = ttk.Combobox(form_frame, values=["Morning", "Afternoon", "Night"], state="readonly", width=19)
    combo_shift.set("Select Shift")
    combo_shift.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Route History:").grid(row=3, column=0, sticky="W", pady=5)
    entry_route_history = ttk.Entry(form_frame, width=22)
    entry_route_history.grid(row=3, column=1, padx=10, pady=5)

    if is_edit:
        entry_driver_name.insert(0, current_name)
        entry_license.insert(0, current_license)
        combo_shift.set(current_shift)
        entry_route_history.insert(0, current_route)

    def handle_save(event=None):
        save_driver(popup, tree, entry_driver_name, entry_license, combo_shift, entry_route_history, selected_id)
    
    popup.bind('<Return>', handle_save)
    
    ttk.Button(popup, text="Save Driver",
               command=handle_save).pack(pady=15)


def save_driver(popup, tree, entry_driver_name, entry_license, combo_shift, entry_route_history, selected_id=None):
    driver_name = entry_driver_name.get().strip()
    license_no = entry_license.get().strip()
    shift = combo_shift.get()
    route_history = entry_route_history.get().strip()

    if not driver_name or not license_no or shift == "Select Shift":
        messagebox.showerror("Input Error", "All fields are required.", parent=popup)
        return

    if len(driver_name) > 50:
        messagebox.showerror("Input Error", "Driver Name must be 50 characters or less.", parent=popup)
        return
    
    if len(license_no) > 20:
        messagebox.showerror("Input Error", "License Number must be 20 characters or less.", parent=popup)
        return
    

    if selected_id is not None:
        success = update_driver_details(selected_id, driver_name, license_no, shift, route_history)
        msg = "Driver details updated successfully."
    else:
        success = add_driver(driver_name, license_no, shift, route_history)
        msg = "Driver added successfully."

    if success:
        messagebox.showinfo("Success", msg, parent=popup)
        refresh_table(tree)
        popup.destroy()
    else:
        messagebox.showerror("Error", "Failed to save driver. Ensure the License Number is completely unique.", parent=popup)

def delete_selected_driver(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a driver to delete.")
        return

    drv_values = tree.item(selected_item[0], "values")
    driver_id = int(drv_values[0].replace("DRV-", ""))
    license_no = drv_values[2]

    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete driver with License No. '{license_no}'?")
    if confirm:
        success, error_msg = delete_driver(driver_id)
        if success:
            messagebox.showinfo("Success", f"Driver with License No. '{license_no}' deleted successfully.")
            refresh_table(tree)
        else:
            messagebox.showerror("Error", error_msg)


def refresh_table(tree):
    for row in tree.get_children():
        tree.delete(row)

    drivers = get_drivers()

    for drv in drivers:
        tree.insert("", tk.END, iid=drv[0], values=(f"DRV-{drv[0]}", drv[1], drv[2], drv[3], drv[4]))