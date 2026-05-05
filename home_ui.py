import tkinter as tk
from tkinter import ttk
from database import get_delivery_progress, get_warehouse_stock_totals, get_vehicle_utilization

def load_home_ui(main_content_frame):
    header_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)
    ttk.Label(header_frame, text="Operational Dashboard", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)

    dashboard_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    dashboard_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

    dashboard_frame.columnconfigure(0, weight=1)
    dashboard_frame.columnconfigure(1, weight=1)
    dashboard_frame.columnconfigure(2, weight=1)

    delivery_frame = tk.LabelFrame(dashboard_frame, text="Delivery Progress", font=("Arial", 12, "bold"), bg="#ffffff", padx=15, pady=15)
    delivery_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")


    deliveries = get_delivery_progress()
    if deliveries:
        for status, count in deliveries:
            ttk.Label(delivery_frame, text=f"{status}: {count}", font=("Arial", 11), background="#ffffff").pack(anchor=tk.W, pady=4)
    else:
        ttk.Label(delivery_frame, text="No delivery data available.", background="#ffffff").pack(anchor=tk.W)

    warehouse_frame = tk.LabelFrame(dashboard_frame, text="Warehouse Stock Totals", font=("Arial", 12, "bold"), bg="#ffffff", padx=15, pady=15)
    warehouse_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

    warehouses_totals = get_warehouse_stock_totals()
    if warehouses_totals:
        for w_name, total_stock in warehouses_totals:
            ttk.Label(warehouse_frame, text=f"{w_name}: {total_stock} items", font=("Arial", 11), background="#ffffff").pack(anchor=tk.W, pady=4)
    else:
        ttk.Label(warehouse_frame, text="No warehouse data available.", background="#ffffff").pack(anchor=tk.W)

    vehicle_frame = tk.LabelFrame(dashboard_frame, text="Vehicle Status", font=("Arial", 12, "bold"), bg="#ffffff", padx=15, pady=15)
    vehicle_frame.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    vehicles = get_vehicle_utilization()
    if vehicles:
        for status, count in vehicles:
            display_status = "Available" if str(status) == "1" else ("In Use / Unavailable" if str(status) == "0" else status)
            ttk.Label(vehicle_frame, text=f"{display_status}: {count}", font=("Arial", 11), background="#ffffff").pack(anchor=tk.W, pady=4)
    else:
        ttk.Label(vehicle_frame, text="No vehicle data available.", background="#ffffff").pack(anchor=tk.W)
