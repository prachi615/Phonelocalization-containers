# preprocessing.py
import pandas as pd
import psycopg2  # Library for connecting to PostgreSQL database
import time
import paho.mqtt.client as mqtt # Library for mqtt connection

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

# def view_all_data():
#     # Prepare the SELECT statement
#     select_query = "SELECT * FROM wifi_data;"

#     # Execute the SELECT statement
#     cur.execute(select_query)

#     # Fetch all rows from the table
#     rows = cur.fetchall()

#     # Print each row
#     for row in rows:
#         print(row)

def on_message(client, userdata, message):
    #print statement used for testing purposes
    print(f"Received message: {message.payload.decode()} on topic {message.topic}")


    
def on_connect(client, userdata, flags, rc, properties):
    print("Connected with result code " + str(rc))
    # Subscribe to the topic
    client.subscribe("preprocess")


# Create an MQTT client instance
client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)



def preprocess_data(raw_data):
    # Convert raw data to a DataFrame for preprocessing
    # columns = ['device_name', 'address_family', 'ip_address', 'netmask', 'broadcast', 'mac_address']
    # df = pd.DataFrame(raw_data, columns=columns)

    # # Perform preprocessing steps (example: drop irrelevant columns)
    # df_preprocessed = df.drop(['address_family'], axis=1)

    # Change code later to process data
    print("preprocessed data")

    # return df_preprocessed

def store_preprocessed_data(preprocessed_data):
    # Implement database storage logic here
    x = 0
    # print("Storing preprocessed data:")
    # print(preprocessed_data)

def main():
    time.sleep(1)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)
    #this publish tests that we can send messages on the topic test/topic to another broker
    client.loop_start()
    
    while True:
        time.sleep(1)  # Pause for 1 second to continue with the MQTT connection
    # while True:
        # Replace this with the actual method to collect raw data
        #raw_data = {}  # Replace with your logic to collect raw data

        # Perform data preprocessing
        #preprocessed_data = preprocess_data(raw_data)

        # Store the preprocessed data
        # store_preprocessed_data("y")
        # query = "SELECT * FROM device_data WHERE device_name = %s AND data_type = %s;"
        # param = ('DeviceB', 'raw')
        # cur.execute(query, param)
        # info = cur.fetchall()
        # print(info)
        

if __name__ == "__main__":
    main()
