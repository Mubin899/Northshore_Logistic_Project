import sqlite3
import hashlib
import logging
import secrets

logging.basicConfig(filename='system_audit.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')
def get_connection():
    try:
        conn = sqlite3.connect('northshore.db')
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except sqlite3.Error as e:
        logging.error(f"Error connecting to database: {e}")
        return None
    
def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    hashed = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${hashed}"

def verify_login(username, password):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT role, password_hash FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            role, stored_hash_string = result

            if "$" in stored_hash_string:
                salt, stored_hash = stored_hash_string.split("$")
                calculated_hash = hashlib.sha256((salt + password).encode()).hexdigest()
                if secrets.compare_digest(calculated_hash, stored_hash):
                    session_token = secrets.token_hex(32)
                    logging.info(f"User logged in securely: {username}. Session Token: {session_token[:8]}...")
                    return role, session_token
            else:
                old_hash = hashlib.sha256(password.encode()).hexdigest()
                if secrets.compare_digest(old_hash, stored_hash_string):
                    session_token = secrets.token_hex(32)
                    logging.info(f"User logged in (Legacy Hash): {username}. Session Token: {session_token[:8]}...")
                    return role, session_token
        logging.warning(f"Failed login attempt: {username}")

    return None, None

def get_warehouses():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT warehouse_id, location_name FROM warehouses")
            warehouses = cursor.fetchall()
            
            if not warehouses:
                cursor.execute("INSERT INTO warehouses (location_name) VALUES ('Main London Depot')")
                conn.commit()
                cursor.execute("SELECT warehouse_id, location_name FROM warehouses")
                warehouses = cursor.fetchall()
                logging.info("No warehouses found. Added default warehouse.")
            return warehouses
        
        except Exception as e:
            logging.error(f"Error getting warehouses: {e}")
            return []
        finally:
            conn.close()
    return []

def get_warehouse_summary():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT w.location_name, i.item_name, i.stock_quantity, i.reorder_level FROM inventory i LEFT JOIN warehouses w ON i.warehouse_id = w.warehouse_id WHERE i.stock_quantity <= i.reorder_level")
            return cursor.fetchall()
        
        except Exception as e:
            logging.error(f"Error getting warehouse summary: {e}")
            return []
        
        finally:
            conn.close()
    return []

def get_warehouse_stock_totals():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT w.location_name, COALESCE(SUM(i.stock_quantity), 0)
                FROM warehouses w
                LEFT JOIN inventory i ON w.warehouse_id = i.warehouse_id
                GROUP BY w.warehouse_id
           """)
            return cursor.fetchall()    
        
        except Exception as e:
            logging.error(f"Error getting warehouse stock totals: {e}")
            return []
        finally:
            conn.close()
    return []

def add_inventory_item(warehouse_id, item_name, stock_quantity, reorder_level):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO inventory (warehouse_id, item_name, stock_quantity, reorder_level) VALUES (?, ?, ?, ?)", 
                            (warehouse_id, item_name, int(stock_quantity), int(reorder_level)))
            conn.commit()
            logging.info(f"Inventory item added: {item_name} at Warehouse ID {warehouse_id}")
            return True
        except Exception as e:
            logging.error(f"Error adding inventory item: {e}")
            return False
        finally:
            conn.close()
    return False

def get_inventory_items():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT i.item_id, w.location_name, i.item_name, i.stock_quantity, i.reorder_level FROM inventory i LEFT JOIN warehouses w ON i.warehouse_id = w.warehouse_id")
            items = cursor.fetchall()
            return items
        
        except Exception as e:
            logging.error(f"Error getting inventory items: {e}")
            return []
        finally:
            conn.close()

    return []

def delete_inventory_item(item_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM inventory WHERE item_id = ?", (item_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Inventory item deleted: Item ID {item_id}")
                return True
            else:
                return False
            
        except Exception as e:
            logging.error(f"Error deleting inventory item: {e}")
            return False
        finally:
            conn.close()
    return False

def update_inventory_item(item_id, new_stock):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET stock_quantity = ? WHERE item_id = ?", (int(new_stock), item_id))
            conn.commit()   

            if cursor.rowcount > 0:
                logging.info(f"Inventory stock updated: Item ID {item_id} new stock {new_stock}")
                return True
            else:
                return False
        
        except Exception as e:
            logging.error(f"Error updating inventory stock: {e}")
            return False
        finally:
            conn.close()
    return False

def update_inventory_item_details(item_id, warehouse_id, item_name, stock_quantity, reorder_level):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE inventory SET warehouse_id = ?, item_name = ?, stock_quantity = ?, reorder_level = ? WHERE item_id = ?", 
                           (warehouse_id, item_name, int(stock_quantity), int(reorder_level), item_id))
            conn.commit() 
            logging.info(f"Inventory item details updated: Item ID {item_id}")  
            return True
        except Exception as e:
            logging.error(f"Error updating inventory item details: {e}")
            return False
        finally:
            conn.close()
    return False



def add_shipment(order_number, sender_details, receiver_details, delivery_date, driver_id=None, vehicle_id=None, transportation_cost=None, item_description=None, incident_report=None):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO shipments (order_number, sender_details, receiver_details, delivery_date, driver_id, vehicle_id, transportation_cost, item_description, incident_report) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", 
                            (order_number, sender_details, receiver_details, delivery_date, driver_id, vehicle_id, transportation_cost, item_description, incident_report))
            conn.commit()
            logging.info(f"Shipment added: Order Number {order_number}")
            return True
        
        except Exception as e:
            logging.error(f"Error adding shipment: {e}")
            return False
        
        finally:
            conn.close()
    return False

def get_shipments():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT 
                    s.shipment_id, 
                    s.order_number, 
                    s.sender_details, 
                    s.receiver_details, 
                    s.delivery_date, 
                    s.status, 
                    COALESCE(d.driver_name, 'Unassigned'), 
                    COALESCE('Veh ' || v.vehicle_id || ' (' || v.capacity || ')', 'Unassigned'), 
                    s.transportation_cost, 
                    s.item_description, 
                    s.incident_report
                FROM shipments s 
                LEFT JOIN drivers d ON s.driver_id = d.driver_id 
                LEFT JOIN vehicles v ON s.vehicle_id = v.vehicle_id
            """)
            shipments = cursor.fetchall()
            return shipments
        except Exception as e:
            logging.error(f"Error getting shipments: {e}")
            return []
        finally:
            conn.close()
    return []

def update_shipment_details(shipment_id, order_number, sender_details, receiver_details, delivery_date, driver_id, vehicle_id, transportation_cost, item_description, incident_report):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE shipments SET order_number = ?, sender_details = ?, receiver_details = ?, delivery_date = ?, driver_id = ?, vehicle_id = ?, transportation_cost = ?, item_description = ?, incident_report = ? WHERE shipment_id = ?", 
                           (order_number, sender_details, receiver_details, delivery_date, driver_id, vehicle_id, transportation_cost, item_description, incident_report, shipment_id))
            conn.commit()   
            return True
        except Exception as e:
            logging.error(f"Error updating shipment details: {e}")
            return False
        finally:
            conn.close()
    return False

def delete_shipment(shipment_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shipments WHERE shipment_id = ?", (shipment_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Shipment deleted: ID {shipment_id}")
                return True
            else:
                return False
            
        except Exception as e:
            logging.error(f"Error deleting shipment: {e}")
            return False
        finally:
            conn.close()
    return False

def update_shipment_status(shipment_id, new_status):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE shipments SET status = ? WHERE shipment_id = ?", (new_status, shipment_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Shipment status updated: ID {shipment_id} to Status '{new_status}'")
                return True
            else:
                return False
            
        except Exception as e:
            logging.error(f"Error updating shipment status: {e}")
            return False
        finally:
            conn.close()
    return False



def add_vehicle(capacity, maintenance_schedule, is_available):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO vehicles (capacity, maintenance_schedule, is_available) VALUES (?, ?, ?)", 
                            (capacity, maintenance_schedule, int(is_available)))
            conn.commit()
            logging.info(f"Vehicle added: Capacity {capacity}")
            return True
        except Exception as e:
            logging.error(f"Error adding vehicle: {e}")
            return False
        finally:
            conn.close()
    return False

def get_vehicles():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT vehicle_id, capacity, maintenance_schedule, is_available FROM vehicles")
            vehicles = cursor.fetchall()
            return vehicles
        except Exception as e:
            logging.error(f"Error getting vehicles: {e}")
            return []
        finally:
            conn.close()
    return []

def delete_vehicle(vehicle_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM vehicles WHERE vehicle_id = ?", (vehicle_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Vehicle deleted: ID {vehicle_id}")
                return True, ""
            else:
                return False, "Vehicle not found."
            
        except sqlite3.IntegrityError:
            logging.warning(f"Failed to delete vehicle ID {vehicle_id}: In use by shipment.")
            return False, "Cannot delete vehicle assigned to shipments."
            
        except Exception as e:
            logging.error(f"Error deleting vehicle: {e}")
            return False, f"An unexpected database error occurred: {str(e)}"
        finally:
            conn.close()
    return False, "Database connection error."

def update_vehicle(vehicle_id, capacity, maintenance, is_available):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE vehicles SET capacity = ?, maintenance_schedule = ?, is_available = ? WHERE vehicle_id = ?", 
                           (capacity, maintenance, int(is_available), vehicle_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Vehicle updated: ID {vehicle_id}")
                return True
            else:
                return False
        except Exception as e:
            logging.error(f"Error updating vehicle: {e}")
            return False
        finally:
            conn.close()
    return False

def update_vehicle_status(vehicle_id, is_available):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE vehicles SET is_available = ? WHERE vehicle_id = ?", (int(is_available), vehicle_id))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Vehicle status updated: ID {vehicle_id}")
                return True
            return False
        except Exception as e:
            logging.error(f"Error updating vehicle status: {e}")
            return False
        finally:
            conn.close()
    return False

def get_vehicle_utilization():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT is_available, COUNT(*) FROM vehicles GROUP BY is_available")
            return cursor.fetchall()
        except Exception as e:
            logging.error(f"Error getting vehicle utilization: {e}")
            return []
        finally:
            conn.close()
    return []



def add_driver(driver_name, license_number, shift_assignment, route_history):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("INSERT INTO drivers (driver_name, license_number, shift_assignment, route_history) VALUES (?, ?, ?, ?)", 
                            (driver_name, license_number, shift_assignment, route_history))
    
            conn.commit()
            logging.info(f"Driver added: {driver_name}, License: {license_number}")
            return True
            
        except Exception as e:
            logging.error(f"Error adding driver: {e}")
            return False
        finally:
            conn.close()
    return False

def get_drivers():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT driver_id, driver_name, license_number, shift_assignment, route_history FROM drivers")
            drivers = cursor.fetchall()
            return drivers
        except Exception as e:
            logging.error(f"Error getting drivers: {e}")
            return []
        finally:
            conn.close()
    return []

def delete_driver(driver_id):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM drivers WHERE driver_id = ?", (driver_id,))
            conn.commit()
            
            if cursor.rowcount > 0:
                logging.info(f"Driver deleted: ID {driver_id}")
                return True, ""
            else:
                return False, "Driver not found."

        except sqlite3.IntegrityError:
            logging.warning(f"Failed to delete driver ID {driver_id}: In use by shipment.")
            return False, "Cannot delete: driver assigned to shipments."
            
        except Exception as e:
            logging.error(f"Error deleting driver: {e}")
            return False, f"An unexpected database error occurred: {str(e)}"
        finally:
            conn.close()
    return False, "Database connection error."

def update_driver_details(driver_id, driver_name, license_number, shift_assignment, route_history):
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE drivers SET driver_name = ?, license_number = ?, shift_assignment = ?, route_history = ? WHERE driver_id = ?", 
                           (driver_name, license_number, shift_assignment, route_history, driver_id))
            conn.commit()
            logging.info(f"Driver details updated: ID {driver_id}")
            return True
        except Exception as e:
            logging.error(f"Error updating driver: {e}")
            return False
        finally:
            conn.close()
    return False

def get_delivery_progress():
    conn = get_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT status, COUNT(*) FROM shipments GROUP BY status")
            return cursor.fetchall()
        
        except Exception as e:
            logging.error(f"Error getting delivery progress: {e}")
            return []
        finally:
            conn.close()
    return []