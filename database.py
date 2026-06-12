import sqlite3
import os

DB_PATH = 'fleet_ledger.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the futuristic ledger table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS fleet_compliance (
        plate_number TEXT PRIMARY KEY,
        fleet_company TEXT,
        emission_class TEXT,
        status TEXT
    )
    ''')
    
    # Insert some dummy "authorized" plates
    # We will seed it with a known plate we expect to test with, e.g., "MH12DE1433" or "KL01AB1234"
    # Let's add a few generic ones and we'll dynamically add the detected one during testing
    dummy_data = [
        ("ABC1234", "RoboTaxi Inc.", "Zero Emission", "AUTHORIZED"),
        ("XYZ9876", "AutoLogistics Gov", "Hybrid", "AUTHORIZED"),
        ("BANNED1", "OldTech Cars", "Diesel", "RESTRICTED")
    ]
    
    for row in dummy_data:
        cursor.execute('''
        INSERT OR IGNORE INTO fleet_compliance (plate_number, fleet_company, emission_class, status)
        VALUES (?, ?, ?, ?)
        ''', row)
        
    conn.commit()
    conn.close()

def check_compliance(plate_number):
    """
    Checks the ledger for the given plate number.
    If not found, defaults to UNKNOWN / RESTRICTED.
    """
    # Clean the plate number
    plate_number = "".join(e for e in plate_number if e.isalnum()).upper()
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT fleet_company, emission_class, status FROM fleet_compliance WHERE plate_number = ?', (plate_number,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            "registered": True,
            "plate_number": plate_number,
            "company": result[0],
            "emission_class": result[1],
            "status": result[2]
        }
    else:
        return {
            "registered": False,
            "plate_number": plate_number,
            "company": "Unknown",
            "emission_class": "Unknown",
            "status": "RESTRICTED"
        }

def register_plate(plate_number, company="TestFleet", emission="Zero Emission", status="AUTHORIZED"):
    """Utility to register a new plate for testing purposes."""
    plate_number = "".join(e for e in plate_number if e.isalnum()).upper()
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    INSERT OR REPLACE INTO fleet_compliance (plate_number, fleet_company, emission_class, status)
    VALUES (?, ?, ?, ?)
    ''', (plate_number, company, emission, status))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
    print("Futuristic Ledger Database Initialized.")
