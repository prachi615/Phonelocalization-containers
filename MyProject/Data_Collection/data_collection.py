# data_collection.py

# Import necessary libraries
import psutil  # Library for accessing system details
import psycopg2  # Library for connecting to PostgreSQL database
import pandas as pd  # Library for data manipulation and analysis
import time  # Library for handling time-related operations

import paho.mqtt.client as mqtt # Library for mqtt connection


# Establish connection to PostgreSQL
# Replace the connection details (dbname, user, password, host) with your own values
conn = psycopg2.connect(
    dbname='Wifi_Details',
    user='postgres',
    password='123456',
    host='postgres'  # Change this if your PostgreSQL is hosted elsewhere
)
cur = conn.cursor()

# Create a table for all data if one has not already been created
cur.execute("""
        CREATE TABLE IF NOT EXISTS device_data (
            phone_id VARCHAR(255) PRIMARY KEY,
            device_name VARCHAR(255),
            address_family INTEGER,
            ip_address VARCHAR(255),
            netmask VARCHAR(255),
            broadcast VARCHAR(255),
            mac_address VARCHAR(255)
        );
    """)
conn.commit

# Define the MQTT server details
MQTT_BROKER = "128.205.218.189"
MQTT_PORT = 1883  # Default MQTT port
MQTT_TOPIC = "test/topic" #change to whatever topic you need

# Callback function for when a message is received
def on_message(client, userdata, message):
    #print statement used for testing purposes
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")
    store_data(message)
    

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    # Subscribe to the topic
    client.subscribe(MQTT_TOPIC)

# Create an MQTT client instance
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Function to collect device details using psutil library
# def collect_device_details():
#     devices = psutil.net_if_addrs()
#     print("Collected device details:")
#     print(devices)
#     return devices
# This above function does not need to be used since all the information from devices is being received from the apps

# This is for testing
# def view_all_data():
#     # Prepare the SELECT statement
#     select_query = "SELECT * FROM device_data;"

#     # Execute the SELECT statement
#     cur.execute(select_query)

#     # Fetch all rows from the table
#     rows = cur.fetchall()

#     # Print each row
#     for row in rows:
#         print(row)

# Function to store collected data in the PostgreSQL database
def store_data(device_data):
    entry = device_data.payload.decode()
    #splits the entry to make a list

    # For example: ['1', 'DeviceA', '2', '192.168.1.100', '255.255.255.0', '192.168.1.255', 'AA:BB:CC:DD:EE:FF']
    
    entry = entry.split(",")
    entry = [item.strip() for item in entry]
    insert_query = """
        INSERT INTO device_data (phone_id, device_name, address_family, ip_address, netmask, broadcast, mac_address) 
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (phone_id) DO NOTHING;
    """
    
    # Execute the INSERT statement
    cur.execute(insert_query, entry)

    conn.commit()

    # This is for testing
    # view_all_data()


    # for device, data in device_data.items():
    #     for entry in data:
    #         # Extract MAC address from the address attribute
    #         # Note: psutil.AF_LINK is used to determine if the current snicaddr object represents a link-layer address (like a MAC address).
    #         mac_address = entry.address if entry.family == psutil.AF_LINK else None

    #         # Insert data into the device_details table in the database
    #         cur.execute(
    #             "INSERT INTO device_details (device_name, address_family, ip_address, netmask, broadcast, mac_address) VALUES (%s, %s, %s, %s, %s, %s)",
    #             (device, entry.family, entry.address, entry.netmask, entry.broadcast, mac_address)
    #         )
    # conn.commit()

# Main function to execute the data collection and storage process
def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    while True:
        time.sleep(1)  # Pause for 1 second to continue with the MQTT connection

# Entry point of the script
if __name__ == "__main__":
    main()
