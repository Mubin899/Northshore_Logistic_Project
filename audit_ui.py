import tkinter as tk
from tkinter import ttk
import os

def load_audit_ui(main_content_frame):
    header_frame = tk.Frame(main_content_frame, bg="#ecf0f1")
    header_frame.pack(fill=tk.X, padx=20, pady=20)

    ttk.Label(header_frame, text="System Audit Logs", font=("Arial", 18, "bold"), background="#ecf0f1").pack(side=tk.LEFT)
    
    ttk.Button(header_frame, text="Refresh Logs", command=lambda: refresh_logs(tree)).pack(side=tk.RIGHT)

    table_frame = tk.Frame(main_content_frame, bg="#ecf0f1", bd=1, relief=tk.SOLID)
    table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 20))

    columns = ("Timestamp", "Level", "Message")
    tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=20)
    
    tree.heading("Timestamp", text="Timestamp")
    tree.heading("Level", text="Severity")
    tree.heading("Message", text="Audit Message")
    
    tree.column("Timestamp", width=180, anchor=tk.W)
    tree.column("Level", width=100, anchor=tk.CENTER)
    tree.column("Message", width=550, anchor=tk.W)

    tree.tag_configure("ERROR", foreground="#c0392b")
    tree.tag_configure("WARNING", foreground="#d35400")
    tree.tag_configure("INFO", foreground="#2c3e50")

    tree_scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=tree.yview)
    tree.configure(yscrollcommand=tree_scrollbar.set)
    tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10, padx=(0, 10))
    tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(10, 0), pady=10)

    refresh_logs(tree)

def refresh_logs(tree):
    for row in tree.get_children():
        tree.delete(row)

    if not os.path.exists('system_audit.log'):
        tree.insert("", tk.END, values=("N/A", "INFO", "No audit log file found."), tags=("INFO",))
        return

    try:
        with open('system_audit.log', 'r') as f:
            lines = f.readlines()
        for line in reversed(lines):
            parts = line.strip().split(' - ', 2)
            
            if len(parts) == 3:
                timestamp, level, msg = parts
                tree.insert("", tk.END, values=(timestamp, level, msg), tags=(level,))
            else:
                tree.insert("", tk.END, values=("", "UNKNOWN", line.strip()), tags=("INFO",))
                
    except Exception as e:
        tree.insert("", tk.END, values=("", "ERROR", f"Failed to read logs: {e}"), tags=("ERROR",))