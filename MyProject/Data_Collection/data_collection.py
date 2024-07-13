# data_collection.py

# Import necessary libraries
import psutil  # Library for accessing system details
import psycopg2  # Library for connecting to PostgreSQL database
import pandas as pd  # Library for data manipulation and analysis
import time  # Library for handling time-related operations
import paho.mqtt.client as mqtt # Library for mqtt connection
import hashlib
import json


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
# JSONB objects are very similar to python dictionaries except key-value pairs can be made dynamically.
# This is the basic format of such objects:
# "ssid": "CoffeeShopWiFi",                     router name ex: eudoram
# "bssid": "00:1A:2B:3C:4D:5E",                 physical address assigned to a router
# "rssi": [-70, -72, -68],                      signal strength from a router
# "network_id": 123,                            unique identifier to distinguish between saved networks
# "link_speed": [54, 56, 52],                   the rate at which data can be transfered on the WiFi
# "frequency": [2412, 2417, 2422]               radio frequency at which the wireless network operates
# Can add more later

cur.execute("""
        CREATE TABLE IF NOT EXISTS wifi_data (
            id SERIAL PRIMARY KEY,
            timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
            device_id VARCHAR(255) NOT NULL,
            raw_data JSONB, 
            preprocessed_data JSONB,  
            inference_result JSONB
        );
    """)
conn.commit()


def generate_id(message_content):
    return hashlib.sha256(message_content.encode()).hexdigest()

# Define the MQTT server details
MQTT_BROKER = "128.205.218.189"
MQTT_PORT = 1883  # Default MQTT port
MQTT_TOPIC = "test/topic" #change to whatever topic you need

# Callback function for when a message is received
def on_message(client, userdata, message):
    #print statement used for testing purposes
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")
    msg = message.payload.decode().split(",")
    msg = [item.strip() for item in msg]
    unique_id = generate_id(message.payload.decode())
    # first index of msg should be what the request is
    if msg[0] == "store" : #store
        msg.pop(0)
        msg.insert(0, unique_id)
        client.publish("preprocess",message.payload.decode()) 
        client.publish("receive/topic", "Successfully submitted") # sends a confirmation
        store_data(msg) # stores raw data

        #need to fix the store_data now
        # Assuming the list is always in the correct order
        # data_dict = {
        #     "rssi": data_list[1],
        #     "ssid": data_list[2],
        #     "bssid": data_list[3],
        #     "network_id": data_list[4],
        #     "link_speed": data_list[5],
        #     "frequency": data_list[6]
        # }
        # the message to store MUST be in this format
        # ex of how to get data to store in the table
    

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
def view_all_data():
    # Prepare the SELECT statement
    select_query = "SELECT * FROM wifi_data;"

    # Execute the SELECT statement
    cur.execute(select_query)

    # Fetch all rows from the table
    rows = cur.fetchall()

    # Print each row
    for row in rows:
        print(row)

# Function to store collected data in the PostgreSQL database
def store_data(device_data):

    data_dict = {
    "ssid": device_data[2],
    "bssid": device_data[3],
    "network_id": device_data[4],
    "rssi": [device_data[1]],  # Start as a list
    "link_speed": [device_data[5]],  # Start as a list
    "frequency": [device_data[6]]  # Start as a list
    }

    json_data = json.dumps(data_dict)

    # Check if an entry for this BSSID already exists
    cur.execute("SELECT raw_data FROM wifi_data WHERE raw_data->>'bssid' = %s", (device_data[3],))
    result = cur.fetchone()

    if result:
    # If entry exists, update it by appending new values to the lists
        cur.execute("""
            UPDATE wifi_data 
            SET raw_data = jsonb_set(jsonb_set(jsonb_set(raw_data, '{rssi}', (raw_data->'rssi') || %s::jsonb), '{link_speed}', (raw_data->'link_speed') || %s::jsonb), '{frequency}', (raw_data->'frequency') || %s::jsonb)
            WHERE raw_data->>'bssid' = %s;
        """, (json.dumps([device_data[1]]), json.dumps([device_data[5]]), json.dumps([device_data[6]]), device_data[3]))
    else:
        # If no entry exists, insert a new one
        cur.execute("""
            INSERT INTO wifi_data (device_id, raw_data) VALUES (%s, %s)
        """, (device_data[0], json_data))

    

    conn.commit()
    print("Stored data from device")

    # This is for testing
    view_all_data()


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
    # waits for mqtt broker to start up
    time.sleep(1)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    #this publish tests that we can send messages on the topic test/topic to another broker
    client.loop_start()
    
    while True:
        time.sleep(1)  # Pause for 1 second to continue with the MQTT connection

# Entry point of the script
if __name__ == "__main__":
    main()