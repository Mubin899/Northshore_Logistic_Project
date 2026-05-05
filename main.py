import tkinter as tk
from tkinter import ttk, messagebox
from database import verify_login
from setup_database import build_tables

from home_ui import load_home_ui
from inventory_ui import load_inventory_ui
from shipment_ui import load_shipment_ui
from fleet_ui import load_fleet_ui
from driver_ui import load_driver_ui
from reports_ui import load_reports_ui
from audit_ui import load_audit_ui


class NorthshoreApp(tk.Tk):
    def __init__(self):
        super().__init__()
        build_tables()
        self.title("Northshore Logistics Ltd")
        self.geometry("1200x700")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        self.style.configure("Sidebar.TButton", font=("Arial", 12), padding=10)

        self.container = tk.Frame(self)
        self.container.pack(fill=tk.BOTH, expand=True)

        self.show_login_screen()

    def clear_container(self, parent_frame):
        for widget in parent_frame.winfo_children():
            widget.destroy()
    
    def show_login_screen(self):
        self.clear_container(self.container)

        login_frame = tk.Frame(self.container)
        login_frame.pack(expand=True)

        tk.Label(login_frame, text="Northshore Logistics Ltd", font=("Arial", 24, "bold")).pack(pady=20)

        ttk.Label(login_frame, text="Username:", font=("Arial", 14)).pack(pady=5)
        entry_username = ttk.Entry(login_frame, font=("Arial", 14), width=30)
        entry_username.pack(pady=5)

        entry_username.focus()

        ttk.Label(login_frame, text="Password:", font=("Arial", 14)).pack(pady=5)
        entry_password = ttk.Entry(login_frame, font=("Arial", 14), show="*", width=30)
        entry_password.pack(pady=5)

        def handle_login(event=None):
            username = entry_username.get()
            password = entry_password.get()
            role, token = verify_login(username, password)

            if role:
                self.username = username
                self.role = role
                self.session_token = token
                self.build_dashboard()

            else:
                messagebox.showerror("Login Failed", "Invalid username or password.")

        ttk.Button(login_frame, text="Login", command=handle_login).pack(pady=20)
        self.bind('<Return>', handle_login)

    def build_dashboard(self):
        self.clear_container(self.container)

        sidebar = tk.Frame(self.container, bg="#2c3e50", width=250)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)

        self.main_content = tk.Frame(self.container, bg="#ecf0f1")
        self.main_content.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        ttk.Label(sidebar, text=f"Welcome, {self.username}", background="#2c3e50", foreground="white", font=("Arial", 14, "bold")).pack(pady=(20, 5))
        ttk.Label(sidebar, text=f"Role: {self.role}", background="#2c3e50", foreground="#bdc3c7", font=("Arial", 12)).pack(pady=(0, 20))

        ttk.Button(sidebar, text="Home", style="Sidebar.TButton", command=self.load_home).pack(fill=tk.X, padx=10, pady=5)


        if self.role in ["Admin", "Manager", "Warehouse Staff"]:
            ttk.Button(sidebar, text="Inventory", style="Sidebar.TButton", command=self.load_inventory).pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(sidebar, text="Shipments", style='Sidebar.TButton', command=self.load_shipment).pack(fill=tk.X, padx=10, pady=5)

        if self.role in ["Admin", "Manager", "Dispatcher"]:
            ttk.Button(sidebar, text="Fleet", style='Sidebar.TButton', command=self.load_fleet).pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(sidebar, text="Drivers", style='Sidebar.TButton', command=self.load_driver).pack(fill=tk.X, padx=10, pady=5)
            
        if self.role in ["Admin", "Manager"]:
            ttk.Button(sidebar, text="Reports", style='Sidebar.TButton', command=self.load_reports).pack(fill=tk.X, padx=10, pady=5)
            ttk.Button(sidebar, text="System Audit", style='Sidebar.TButton', command=self.load_audit).pack(fill=tk.X, padx=10, pady=5)

        ttk.Button(sidebar, text="Logout", style='Sidebar.TButton', command=self.show_login_screen).pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

        self.load_home()

    def load_home(self):
        self.clear_container(self.main_content)
        load_home_ui(self.main_content)

    def load_inventory(self):
        self.clear_container(self.main_content)
        load_inventory_ui(self.main_content)

    def load_shipment(self):
        self.clear_container(self.main_content)
        load_shipment_ui(self.main_content)
        
    def load_fleet(self):
        self.clear_container(self.main_content)
        load_fleet_ui(self.main_content)

    def load_driver(self):
        self.clear_container(self.main_content)
        load_driver_ui(self.main_content)

    def load_reports(self):
        self.clear_container(self.main_content)
        load_reports_ui(self.main_content)

    def load_audit(self):
        self.clear_container(self.main_content)
        load_audit_ui(self.main_content)

if __name__ == "__main__":
    app = NorthshoreApp()
    app.mainloop()