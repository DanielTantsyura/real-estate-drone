#!/usr/bin/env python3
"""
Simple test of the DroneBlocksTelloSimulator
"""

import sys
import os
import time

try:
    # Try to import the simulator
    from DroneBlocksTelloSimulator import SimulatedDrone
    print("Successfully imported DroneBlocksTelloSimulator!")
    
    # Get simulator key from config
    import json
    config_path = "config/config.json"
    sim_key = ""
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
                sim_key = config.get('simulator', {}).get('key', '')
                print(f"Found simulator key: {sim_key}")
        except Exception as e:
            print(f"Error reading config: {e}")
    
    # Initialize the simulator
    print("\nInitializing simulator...")
    tello = SimulatedDrone(sim_key)
    print("Simulator initialized!")
    
    # Run a simple flight
    print("\nRunning simple flight test...")
    
    print("Taking off...")
    tello.takeoff()
    time.sleep(3)
    
    print("Flying forward...")
    tello.fly_forward(50, "cm")
    time.sleep(2)
    
    print("Rotating right...")
    tello.yaw_right(90)
    time.sleep(2)
    
    print("Landing...")
    tello.land()
    
    print("\nTest completed successfully!")
    
except ImportError as e:
    print(f"Error importing DroneBlocksTelloSimulator: {e}")
    print("\nTry running: pip install DroneBlocksTelloSimulator")
    sys.exit(1)
except Exception as e:
    print(f"Error during test: {e}")
    sys.exit(1) 