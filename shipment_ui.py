import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
from database import add_shipment, get_shipments, delete_shipment, update_shipment_status, update_shipment_details, get_drivers, get_vehicles

def load_shipment_ui(main_content_frame):
    header_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)

    ttk.Label(header_frame, text="Shipment Management", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)

    ttk.Button(header_frame, text="+ Add New Shipment",
              command=lambda: open_add_shipment_popup(main_content_frame, tree)).pack(side=tk.RIGHT)
    
    table_frame = tk.Frame(main_content_frame, bg="#ecf0f1", bd=1, relief=tk.SOLID)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 10))

    columns = ("ID", "Order No", "Sender", "Receiver", "Date", "Status", "Driver", "Vehicle", "Cost (£)", "Surcharges", "Payment Status", "Item Desc", "Incident Report")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    for col in columns:
        tree.heading(col, text=col)
        
    tree.column("ID", width=50, anchor=tk.CENTER)
    tree.column("Order No", width=100, anchor=tk.CENTER)
    tree.column("Sender", width=150, anchor=tk.CENTER)
    tree.column("Receiver", width=150, anchor=tk.CENTER)
    tree.column("Date", width=100, anchor=tk.CENTER)
    tree.column("Status", width=80, anchor=tk.CENTER)
    tree.column("Driver", width=70, anchor=tk.CENTER)
    tree.column("Vehicle", width=70, anchor=tk.CENTER)
    tree.column("Cost (£)", width=80, anchor=tk.CENTER)
    tree.column("Surcharges", width=80, anchor=tk.CENTER)
    tree.column("Payment Status", width=100, anchor=tk.CENTER)
    tree.column("Item Desc", width=100, anchor=tk.CENTER)
    tree.column("Incident Report", width=100, anchor=tk.CENTER)

    tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)


    action_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

    ttk.Label(action_frame, text="Update Status:", font=("Arial", 10, "bold"), background="#ecf0f1").pack(side=tk.LEFT, padx=(0, 10))

    status_options = ["Pending", "In Transit", "Delivered", "Returned to Warehouse", "Delayed", "Cancelled"]
    combo_status = ttk.Combobox(action_frame, values=status_options, state="readonly", width=20)
    combo_status.set("Select Status")
    combo_status.pack(side=tk.LEFT, padx=(0, 10))

    ttk.Button(action_frame, text="Update Status",
                command=lambda: change_status(tree, combo_status)).pack(side=tk.LEFT)
    

    ttk.Button(action_frame, text="Delete Shipment",
                command=lambda: delete_selected_shipment(tree)).pack(side=tk.RIGHT, padx=(10, 0))
    ttk.Button(action_frame, text="Edit Details",
                command=lambda: open_add_shipment_popup(main_content_frame, tree, is_edit=True)).pack(side=tk.RIGHT, padx=(10, 0))
    
    refresh_table(tree)

def open_add_shipment_popup(parent, tree, is_edit=False):
    selected_id = None
    if is_edit:
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select a shipment to edit.")
            return
        s_vals = tree.item(selected_item[0], "values")
        selected_id = int(s_vals[0])

    popup = tk.Toplevel(parent)
    title_text = "Edit Shipment" if is_edit else "Add New Shipment"
    popup.title(title_text)
    popup.geometry("450x480")
    popup.grab_set()
    popup.resizable(False, False)

    ttk.Label(popup, text="Shipment Details", font=("Arial", 14, "bold")).pack(pady=10)

    form_frame = tk.Frame(popup)
    form_frame.pack(pady=5, padx=20, fill=tk.X)

    ttk.Label(form_frame, text="Order No:").grid(row=0, column=0, sticky="W", pady=5)
    entry_order = ttk.Entry(form_frame, width=30)
    entry_order.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Sender Details:").grid(row=1, column=0, sticky="W", pady=5)
    entry_sender = ttk.Entry(form_frame, width=30)
    entry_sender.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Receiver Details:").grid(row=2, column=0, sticky="W", pady=5)
    entry_receiver = ttk.Entry(form_frame, width=30)
    entry_receiver.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Item Description:").grid(row=3, column=0, sticky="W", pady=5)
    entry_item_desc = ttk.Entry(form_frame, width=30)
    entry_item_desc.grid(row=3, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Date (YYYY-MM-DD):").grid(row=4, column=0, sticky="W", pady=5)
    entry_date = ttk.Entry(form_frame, width=30)
    entry_date.grid(row=4, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Assign Driver:").grid(row=5, column=0, sticky="W", pady=5)
    drivers = get_drivers()
    driver_dict = {d[1]: d[0] for d in drivers} 
    combo_driver = ttk.Combobox(form_frame, values=list(driver_dict.keys()), state="readonly", width=27)
    combo_driver.set("Select a Driver" if not is_edit else "Keep Current Driver (Select to Change)")
    combo_driver.grid(row=5, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Assign Vehicle:").grid(row=6, column=0, sticky="W", pady=5)
    vehicles = get_vehicles()
    vehicle_dict = {f"Vehicle {v[0]} (Cap: {v[1]})": v[0] for v in vehicles}
    combo_vehicle = ttk.Combobox(form_frame, values=list(vehicle_dict.keys()), state="readonly", width=27)
    combo_vehicle.set("Select a Vehicle" if not is_edit else "Keep Current Vehicle (Select to Change)")
    combo_vehicle.grid(row=6, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Cost (£) (Optional):").grid(row=7, column=0, sticky="W", pady=5)
    entry_cost = ttk.Entry(form_frame, width=30)
    entry_cost.grid(row=7, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Surcharges (£) (Optional):").grid(row=8, column=0, sticky="W", pady=5)
    entry_surcharges = ttk.Entry(form_frame, width=30)
    entry_surcharges.grid(row=8, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Payment Status:").grid(row=9, column=0, sticky="W", pady=5)
    combo_payment = ttk.Combobox(form_frame, values=["Pending", "Paid", "Overdue"], state="readonly", width=27)
    combo_payment.set("Select Payment Status")
    combo_payment.grid(row=9, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Incident Report:").grid(row=12, column=0, sticky="W", pady=5)
    entry_incident = ttk.Entry(form_frame, width=30)
    entry_incident.grid(row=12, column=1, padx=10, pady=5)

    if is_edit:
        entry_order.insert(0, s_vals[1])
        entry_sender.insert(0, s_vals[2])
        entry_receiver.insert(0, s_vals[3])
        entry_item_desc.insert(0, s_vals[11])
        entry_date.insert(0, s_vals[4])
        entry_cost.insert(0, s_vals[8])
        entry_surcharges.insert(0, s_vals[9])
        combo_payment.set(s_vals[10])
        entry_incident.insert(0, s_vals[12])
    def handle_save(event=None):
        save_shipment(popup, entry_order, entry_sender, entry_receiver, entry_date, 
                        combo_driver, combo_vehicle, entry_cost, entry_surcharges, combo_payment, entry_item_desc, entry_incident,
                        driver_dict, vehicle_dict, tree, selected_id)
        
    popup.bind('<Return>', handle_save)
    
    ttk.Button(popup, text="Save Shipment",
                command=handle_save).pack(pady=20)   

def save_shipment(popup, order, sender, receiver, date, c_drv, c_veh, cost, surcharges, payment_status, item_desc, incident_report, driver_dict, vehicle_dict, tree, selected_id=None):
    o_val = order.get().strip()
    s_val = sender.get().strip()
    r_val = receiver.get().strip()
    d_val = date.get().strip()
    cost_val = cost.get().strip()
    surcharges_val = surcharges.get().strip()
    payment_val = payment_status.get().strip()
    desc_val = item_desc.get().strip()
    incident_val = incident_report.get().strip()

    if not o_val or not s_val or not r_val or not d_val:
        messagebox.showerror("Input Error", "Please fill in all core fields.", parent=popup)
        return
    
    if len(o_val) > 50:
        messagebox.showerror("Input Error", "Order Number must be 50 characters or less.", parent=popup)
        return
    if len(s_val) > 200 or len(r_val) > 200:
        messagebox.showerror("Input Error", "Sender and Receiver details must be 200 characters or less.", parent=popup)
        return
    

    try:
        datetime.strptime(d_val, "%Y-%m-%d")
    except ValueError:
        messagebox.showerror("Input Error", "Date must be in YYYY-MM-DD format.", parent=popup)
        return
    
    
    drv_id = driver_dict.get(c_drv.get()) 
    veh_id = vehicle_dict.get(c_veh.get())
    
    try:
        cost_float = float(cost_val) if cost_val else None
    except ValueError:
        messagebox.showerror("Input Error", "Cost must be a number.", parent=popup)
        return

    desc_val = desc_val if desc_val else None
    incident_val = incident_val if incident_val else None
    try:
        surcharges_float = float(surcharges_val) if surcharges_val else None
    except ValueError:
        messagebox.showerror("Input Error", "Surcharges must be a number.", parent=popup)
        return

    if selected_id is not None:
        success = update_shipment_details(selected_id, o_val, s_val, r_val, d_val, drv_id, veh_id, cost_float, surcharges_float, payment_val, desc_val, incident_val)
        msg = f"Shipment '{o_val}' updated."
    else:
        success = add_shipment(o_val, s_val, r_val, d_val, drv_id, veh_id, cost_float, surcharges_float, payment_val, desc_val, incident_val)
        msg = f"Shipment '{o_val}' added."

    if success:
        messagebox.showinfo("Success", msg, parent=popup)
        refresh_table(tree)
        popup.destroy()
    else:
        messagebox.showerror("Error", "Failed to save shipment. Ensure Order Number is unique.", parent=popup)

def change_status(tree, combo_status):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a shipment to update.")
        return
    
    shipment_id = int(tree.item(selected_item[0], "values")[0])
    new_status = combo_status.get()

    if new_status == "Select Status":
        messagebox.showwarning("Input Error", "Please select a valid status from the dropdown.")
        return

    if update_shipment_status(shipment_id, new_status):
        messagebox.showinfo("Success", f"Shipment status updated to '{new_status}'.")
        refresh_table(tree)
    else:
        messagebox.showerror("Error", "Failed to update shipment status.")
    
def delete_selected_shipment(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select a shipment to delete.")
        return
    
    shipment_id = int(tree.item(selected_item[0], "values")[0])
    order_num = tree.item(selected_item[0], "values")[1]

    if messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete shipment '{order_num}'?"):
        if delete_shipment(shipment_id):
            messagebox.showinfo("Deleted", f"Shipment '{order_num}' deleted successfully.")
            refresh_table(tree)
        else:
            messagebox.showerror("Error", "Failed to delete shipment.")


def refresh_table(tree):
    for item in tree.get_children():
        tree.delete(item)

    items = get_shipments()

    for item in items:
        display_values = (item[0], item[1], item[2], item[3], item[4], item[5], item[6], item[7], item[8], item[9], item[10], item[11], item[12])
        tree.insert("", tk.END, iid=item[0], values=display_values) 