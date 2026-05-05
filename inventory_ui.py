import tkinter as tk
from tkinter import ttk, messagebox
from database import add_inventory_item, get_inventory_items, delete_inventory_item, update_inventory_item, update_inventory_item_details, get_warehouses

def load_inventory_ui(main_content_frame):
    header_frame= tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)

    ttk.Label(header_frame, text="Inventory Management", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)

    ttk.Button(header_frame, text="+ Add New Item",
                command=lambda: open_add_item_popup(main_content_frame, tree)).pack(side=tk.RIGHT)
    
    table_frame = tk.Frame(main_content_frame, bg="#ecf0f1", bd=1, relief=tk.SOLID)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    columns = ("ID", "Item Name", "Stock Quantity", "Reorder Level", "Warehouse")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

    tree.heading("ID", text="ID")
    tree.heading("Item Name", text="Item Name")
    tree.heading("Stock Quantity", text="Stock Quantity")
    tree.heading("Reorder Level", text="Reorder Level")
    tree.heading("Warehouse", text="Warehouse")

    tree.column("ID", width=50, anchor=tk.CENTER)
    tree.column("Item Name", width=200, anchor=tk.CENTER)
    tree.column("Stock Quantity", width=120, anchor=tk.CENTER)
    tree.column("Reorder Level", width=120, anchor=tk.CENTER)
    tree.column("Warehouse", width=150, anchor=tk.CENTER)

    tree.tag_configure("low_stock", background="#f8d7da")


    tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)


    action_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    action_frame.pack(fill=tk.X, padx=20, pady=(0, 20))

    ttk.Button(action_frame, text="Update Stock", 
                command=lambda: open_update_stock_popup(main_content_frame, tree)).pack(side=tk.LEFT)


    ttk.Button(action_frame, text="Delete Item", 
                command=lambda: delete_item(tree)).pack(side=tk.RIGHT, padx=(10, 0))
    ttk.Button(action_frame, text="Edit Details",
                command=lambda: open_add_item_popup(main_content_frame, tree, is_edit=True)).pack(side=tk.RIGHT, padx=(10, 0))
    
    refresh_table(tree)

def open_add_item_popup(parent, tree, is_edit=False):
    selected_id = None
    if is_edit:
        selected_item = tree.selection()
        if not selected_item:
            messagebox.showerror("Selection Error", "Please select an item to edit.")
            return

        item_values = tree.item(selected_item[0], "values")
        selected_id = int(item_values[0])
        current_name = item_values[1]
        current_stock = item_values[2]
        current_reorder = item_values[3]
        current_warehouse = item_values[4]

    popup = tk.Toplevel(parent)
    title_text = "Edit Inventory Item" if is_edit else "Add New Inventory Item"
    popup.title(title_text)
    popup.geometry("400x350")
    popup.grab_set()
    popup.resizable(False, False)

    ttk.Label(popup, text="Item Details", font=("Arial", 14, "bold")).pack(pady=15)

    form_frame = tk.Frame(popup)
    form_frame.pack(pady=10)

    ttk.Label(form_frame, text="Item Name:").grid(row=0, column=0, sticky="W", pady=5)
    entry_name = ttk.Entry(form_frame, width=27)
    entry_name.grid(row=0, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Current Stock:").grid(row=1, column=0, sticky="W", pady=5)
    entry_stock = ttk.Entry(form_frame, width=27)
    entry_stock.grid(row=1, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Reorder Level:").grid(row=2, column=0, sticky="W", pady=5)
    entry_reorder = ttk.Entry(form_frame, width=27)
    entry_reorder.grid(row=2, column=1, padx=10, pady=5)

    ttk.Label(form_frame, text="Warehouse:").grid(row=3, column=0, sticky="W", pady=5)
    warehouse = get_warehouses()
    warehouse_dict = {w[1]: w[0] for w in warehouse}
    warehouse_names = list(warehouse_dict.keys())

    combo_warehouse = ttk.Combobox(form_frame, values=warehouse_names, state="readonly", width=25)
    if warehouse_names:
        combo_warehouse.set(warehouse_names[0])
    combo_warehouse.grid(row=3, column=1, padx=10, pady=5)

    if is_edit:
        entry_name.insert(0, current_name)
        entry_stock.insert(0, current_stock)
        entry_reorder.insert(0, current_reorder)
        combo_warehouse.set(current_warehouse)

    def handle_save(event=None):
        save_item(popup, entry_name, entry_stock, entry_reorder, warehouse_dict, combo_warehouse, tree, selected_id)

    ttk.Button(popup, text="Save Item",
                command=handle_save).pack(pady=20)
    
def save_item(popup, entry_name, entry_stock, entry_reorder, warehouse_dict, combo_warehouse, tree, selected_id=None):
    item_name = entry_name.get().strip()
    stock_quantity = entry_stock.get().strip()
    reorder_level = entry_reorder.get().strip()
    warehouse_name = combo_warehouse.get()

    if not item_name or not stock_quantity or not reorder_level or not warehouse_name:
        messagebox.showerror("Input Error", "All fields are required.")
        return

    if len(item_name) > 100:
        messagebox.showerror("Input Error", "Item Name must be 100 characters or less.")
        return
    

    
    try:
        stock_int = int(stock_quantity)
        reorder_int = int(reorder_level)

    except ValueError:
        messagebox.showerror("Input Error", "Stock Quantity and Reorder Level must be integers.")
        return
    
    warehouse_id = warehouse_dict.get(warehouse_name)
    
    if selected_id is not None:
        success = update_inventory_item_details(selected_id, warehouse_id, item_name, stock_int, reorder_int)
        msg = f"Item '{item_name}' updated successfully."
    else:
        success = add_inventory_item(warehouse_id, item_name, stock_int, reorder_int)
        msg = f"Item '{item_name}' added successfully."
    
    if success:
        messagebox.showinfo("Success", msg, parent=popup)
        refresh_table(tree)
        popup.destroy()
    else:
        messagebox.showerror("Error", "Failed to save item. Please try again.", parent=popup)

def open_update_stock_popup(parent, tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select an item to update.")
        return
    
    item_id = int(tree.item(selected_item[0], "values")[0])
    item_name = tree.item(selected_item[0], "values")[1]
    current_stock = tree.item(selected_item[0], "values")[2]

    popup = tk.Toplevel(parent)
    popup.title("Update Stock")
    popup.geometry("300x200")
    popup.grab_set()
    popup.resizable(False, False)

    ttk.Label(popup, text=f"Update: {item_name}", font=("Arial", 12, "bold")).pack(pady=15)

    ttk.Label(popup, text="New Stock Quantity:").pack(pady=5)
    entry_stock = ttk.Entry(popup, width=20)
    entry_stock.insert(0, current_stock)
    entry_stock.pack(pady=5)

    ttk.Button(popup, text="Update Stock",
               command=lambda: save_updated_stock(popup, item_id, entry_stock, tree)).pack(pady=15)
    

def save_updated_stock(popup, item_id, entry_stock, tree):
    new_stock = entry_stock.get().strip()

    if not new_stock:
        messagebox.showerror("Input Error", "Please enter a stock quantity.", parent=popup)
        return

    try:
        stock_int = int(new_stock)
        if stock_int < 0:
            raise ValueError
    except ValueError:
        messagebox.showerror("Input Error", "Stock must be a valid non-negative integer.", parent=popup)
        return

    if update_inventory_item(item_id, stock_int):
        messagebox.showinfo("Success", "Stock updated successfully.", parent=popup)
        refresh_table(tree)
        popup.destroy()
    else:
        messagebox.showerror("Error", "Failed to update stock.", parent=popup)



def delete_item(tree):
    selected_item = tree.selection()
    if not selected_item:
        messagebox.showerror("Selection Error", "Please select an item to delete.")
        return

    item_id = int(selected_item[0])
    item_values = tree.item(selected_item[0], "values")
    item_name = item_values[1]

    confirm = messagebox.askyesno("Confirm Deletion", f"Are you sure you want to delete '{item_name}'?")
    if confirm:
        if delete_inventory_item(item_id):
            messagebox.showinfo("Deleted", f"Item '{item_name}' has been deleted.")
            refresh_table(tree)
        else:
            messagebox.showerror("Error", "Failed to delete item. Please try again.")

def refresh_table(tree):
    for row in tree.get_children():
        tree.delete(row)

    items = get_inventory_items()
    for item in items:
        item_id = item[0]
        warehouse_loc = item[1]
        name = item[2]
        stock = item[3]
        reorder = item[4]

        if stock <= reorder:
            tree.insert("", "end", iid=item_id, values=(item_id, name, stock, reorder, warehouse_loc), tags=("low_stock",))
        else:
            tree.insert("", "end", iid=item_id, values=(item_id, name, stock, reorder, warehouse_loc))