#!/usr/bin/env python3
"""
Simple flight commands for DJI Tello drone.
This script demonstrates takeoff, basic movement, and landing.
"""
from djitellopy import Tello
import time

def simple_flight():
    """Execute a simple flight pattern"""
    # Initialize the drone
    tello = Tello()
    
    try:
        # Connect to the drone
        print("Connecting to Tello...")
        tello.connect()
        
        # Check battery level before flying
        battery = tello.get_battery()
        print(f"Battery level: {battery}%")
        
        if battery > 20:  # Only fly if battery is sufficient
            # Take off
            print("Taking off...")
            tello.takeoff()
            time.sleep(3)  # Give the drone time to stabilize
            
            # Move forward 50cm
            print("Moving forward...")
            tello.move_forward(50)
            time.sleep(2)
            
            # Rotate 90 degrees clockwise
            print("Rotating...")
            tello.rotate_clockwise(90)
            time.sleep(2)
            
            # Move up 30cm
            print("Moving up...")
            tello.move_up(30)
            time.sleep(2)
            
            # Fly in a small square
            print("Flying in a square pattern...")
            for i in range(4):
                tello.move_forward(30)
                time.sleep(2)
                tello.rotate_clockwise(90)
                time.sleep(2)
                
            # Land
            print("Landing...")
            tello.land()
            print("Flight completed successfully!")
        else:
            print("Battery too low for safe flight")
    
    except Exception as e:
        print(f"Error during flight: {e}")
        # Try to land safely if an error occurs mid-flight
        try:
            tello.land()
            print("Emergency landing executed")
        except:
            print("Could not execute emergency landing")
    
    finally:
        # Disconnect
        print("Disconnecting...")
        tello.end()
        print("Disconnected.")

if __name__ == "__main__":
    simple_flight() 