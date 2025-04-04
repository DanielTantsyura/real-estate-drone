#!/usr/bin/env python3
"""
Basic connection test for DJI Tello drone.
This script connects to the drone and displays the battery level.
"""
from djitellopy import Tello
import time

def main():
    # Initialize the drone
    tello = Tello()
    
    try:
        # Connect to the drone
        print("Connecting to Tello...")
        tello.connect()
        
        # Print battery level as a connection test
        battery = tello.get_battery()
        print(f"Connection successful!")
        print(f"Battery level: {battery}%")
        
        # Print additional information
        temp = tello.get_temperature()
        height = tello.get_height()
        tof = tello.get_distance_tof()
        
        print(f"Temperature: {temp}°C")
        print(f"Height: {height}cm")
        print(f"TOF distance: {tof}cm")
        
    except Exception as e:
        print(f"Error connecting to Tello: {e}")
    
    finally:
        # Disconnect
        print("Disconnecting...")
        tello.end()
        print("Disconnected.")

if __name__ == "__main__":
    main() 