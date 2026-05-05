import sqlite3

def build_tables():

    conn = sqlite3.connect('northshore.db')
    cursor = conn.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
        user_id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Warehouses (
        warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
        location_name TEXT NOT NULL
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Inventory (
        item_id INTEGER PRIMARY KEY AUTOINCREMENT,
        warehouse_id INTEGER REFERENCES Warehouses (warehouse_id),
        item_name TEXT NOT NULL,
        stock_quantity INTEGER,
        reorder_level INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vehicles (
        vehicle_id INTEGER PRIMARY KEY AUTOINCREMENT,
        capacity TEXT,
        maintenance_schedule TEXT,
        is_available INTEGER
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Drivers (
        driver_id INTEGER PRIMARY KEY AUTOINCREMENT,
        driver_name TEXT NOT NULL,
        license_number TEXT UNIQUE,
        shift_assignment TEXT,
        route_history TEXT
    )''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Shipments (
        shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_number TEXT UNIQUE,
        sender_details TEXT,
        receiver_details TEXT,
        status TEXT DEFAULT 'Pending',
        delivery_date TEXT,
        driver_id INTEGER REFERENCES Drivers (driver_id),
        vehicle_id INTEGER REFERENCES Vehicles (vehicle_id),
        transportation_cost REAL,
        surcharges REAL DEFAULT 0.00,
        item_description TEXT,
        incident_report TEXT
    )''')

    try:
        cursor.execute("ALTER TABLE Drivers ADD COLUMN route_history TEXT")
        print("Migration: Added route_history to Drivers.")
    except sqlite3.OperationalError:
        pass # Column already exists

    # 2. Fix Shipments Table (Resolves "no such column: s.surcharges")[cite: 16, 23]
    try:
        cursor.execute("ALTER TABLE Shipments ADD COLUMN surcharges REAL DEFAULT 0.00")
        print("Migration: Added surcharges to Shipments.")
    except sqlite3.OperationalError:
        pass

    try:
        cursor.execute("ALTER TABLE Shipments ADD COLUMN payment_status TEXT DEFAULT 'Unpaid'")
        print("Migration: Added payment_status to Shipments.")
    except sqlite3.OperationalError:
        pass
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipment_status ON Shipments (status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipment_driver ON Shipments (driver_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_shipment_vehicle ON Shipments (vehicle_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON Inventory (warehouse_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_vehicle_availability ON Vehicles (is_available)")
    
    conn.commit()
    conn.close()
    print("Success: Database structure built perfectly!")

if __name__ == "__main__":
    build_tables()