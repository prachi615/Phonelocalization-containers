# data_collection.py
import psutil
import time

def collect_device_details():
    devices = psutil.net_if_addrs()
    print("Collected device details:")
    print(devices)
    return devices

def main():
    while True:
        device_info = collect_device_details()
        time.sleep(5)

if __name__ == "__main__":
    main()
