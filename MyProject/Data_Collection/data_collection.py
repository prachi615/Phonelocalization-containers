# data_collection.py

# Import necessary libraries
import psutil  # Library for accessing system details
import psycopg2  # Library for connecting to PostgreSQL database
import pandas as pd  # Library for data manipulation and analysis
import time  # Library for handling time-related operations

# Establish connection to PostgreSQL
# Replace the connection details (dbname, user, password, host) with your own values
conn = psycopg2.connect(
    dbname='Wifi_Details',
    user='postgres',
    password='123456',
    host='localhost'  # Change this if your PostgreSQL is hosted elsewhere
)
cur = conn.cursor()

# Function to collect device details using psutil library
def collect_device_details():
    devices = psutil.net_if_addrs()
    print("Collected device details:")
    print(devices)
    return devices

# Function to store collected data in the PostgreSQL database
def store_data(device_data):
    for device, data in device_data.items():
        for entry in data:
            # Extract MAC address from the address attribute
            # Note: psutil.AF_LINK is used to determine if the current snicaddr object represents a link-layer address (like a MAC address).
            mac_address = entry.address if entry.family == psutil.AF_LINK else None

            # Insert data into the device_details table in the database
            cur.execute(
                "INSERT INTO device_details (device_name, address_family, ip_address, netmask, broadcast, mac_address) VALUES (%s, %s, %s, %s, %s, %s)",
                (device, entry.family, entry.address, entry.netmask, entry.broadcast, mac_address)
            )
    conn.commit()

# Main function to execute the data collection and storage process
def main():
    while True:
        # Step 1: Collect raw device details using the collect_device_details function
        device_info = collect_device_details()
        time.sleep(5)  # Pause for 5 seconds
        # Step 2: Store the preprocessed data in the PostgreSQL database using the store_data function
        store_data(device_info)

# Entry point of the script
if __name__ == "__main__":
    main()
