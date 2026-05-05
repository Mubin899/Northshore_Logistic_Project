import tkinter as tk
from tkinter import ttk
from database import get_delivery_progress, get_warehouse_summary, get_vehicle_utilization

def load_reports_ui(main_content_frame):
    header_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)
    ttk.Label(header_frame, text="Reports & Analytics", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)

    content_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

    delivery_frame = tk.Frame(content_frame, bd=1, relief=tk.SOLID, bg="white")
    delivery_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    tk.Label(delivery_frame, text="Delivery Progress", font=("Helvetica", 14, "bold"), fg="#2c3e50", bg="white").pack(pady=15)
    
    delivery_data = get_delivery_progress()
    if not delivery_data:
        tk.Label(delivery_frame, text="No delivery data available", bg="white").pack()
    else:
        for status, count in delivery_data:
            tk.Label(delivery_frame, text=f"{status}: {count} shipment(s)", font=("Helvetica", 12), bg="white").pack(anchor="w", padx=20, pady=5)

    
    warehouse_frame = tk.Frame(content_frame, bd=1, relief=tk.SOLID, bg="white")
    warehouse_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    tk.Label(warehouse_frame, text="Low Stock Alerts", font=("Helvetica", 14, "bold"), fg="#c0392b", bg="white").pack(pady=15)
    
    warehouse_columns = ("Location", "Item", "Stock", "Reorder")
    warehouse_tree = ttk.Treeview(warehouse_frame, columns=warehouse_columns, show="headings", height=15)

    for col in warehouse_columns:
        warehouse_tree.heading(col, text=col)
        warehouse_tree.column(col, width=100, anchor=tk.CENTER)

    warehouse_data = get_warehouse_summary()
    for row in warehouse_data:
        warehouse_tree.insert("", tk.END, values=row)

    warehouse_scrollbar = ttk.Scrollbar(warehouse_frame, orient=tk.VERTICAL, command=warehouse_tree.yview)
    warehouse_tree.configure(yscrollcommand=warehouse_scrollbar.set)
    warehouse_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=5, padx=(0, 10))
    warehouse_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=5)


    vehicle_frame = tk.Frame(content_frame, bd=1, relief=tk.SOLID, bg="white")
    vehicle_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
    tk.Label(vehicle_frame, text="Vehicle Utilization", font=("Helvetica", 14, "bold"), fg="#27ae60", bg="white").pack(pady=15) 

    vehicle_data = get_vehicle_utilization()
    if not vehicle_data:
        tk.Label(vehicle_frame, text="No vehicle data available", bg="white").pack()
    else:
        for is_available, count in vehicle_data:
            status_text = "Available" if is_available == 1 else "Not Available"
            tk.Label(vehicle_frame, text=f"{status_text}: {count} vehicle(s)", font=("Helvetica", 12), bg="white").pack(anchor="w", padx=20, pady=5)


    