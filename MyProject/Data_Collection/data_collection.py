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

# Define the MQTT server details
MQTT_BROKER = "128.205.218.189"
MQTT_PORT = 1883  # Default MQTT port
MQTT_TOPIC = "test/topic"

# Callback function for when a message is received
def on_message(client, userdata, message):
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")
    

# Callback function for when the client connects to the broker
def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    # Subscribe to the topic
    client.subscribe(MQTT_TOPIC)

# Create an MQTT client instance
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# Function to collect device details using psutil library
def collect_device_details():
    devices = psutil.net_if_addrs()
    print("Collected device details:")
    print(devices)
    return devices

# Function to store collected data in the PostgreSQL database
# def store_data(device_data):
#     for device, data in device_data.items():
#         for entry in data:
#             # Extract MAC address from the address attribute
#             # Note: psutil.AF_LINK is used to determine if the current snicaddr object represents a link-layer address (like a MAC address).
#             mac_address = entry.address if entry.family == psutil.AF_LINK else None

#             # Insert data into the device_details table in the database
#             cur.execute(
#                 "INSERT INTO device_details (device_name, address_family, ip_address, netmask, broadcast, mac_address) VALUES (%s, %s, %s, %s, %s, %s)",
#                 (device, entry.family, entry.address, entry.netmask, entry.broadcast, mac_address)
#             )
#     conn.commit()

# Main function to execute the data collection and storage process
def main():
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    client.loop_start()
    
    while True:

        # # Step 1: Collect raw device details using the collect_device_details function
        device_info = collect_device_details()
        
        time.sleep(5)  # Pause for 5 seconds
        # # Step 2: Store the preprocessed data in the PostgreSQL database using the store_data function
        # store_data(device_info)
    # Clean up
    client.loop_stop()
    client.disconnect()

# Entry point of the script
if __name__ == "__main__":
    main()
