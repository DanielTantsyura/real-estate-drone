#!/usr/bin/env python3
"""
Run the simulator mission without launching Chrome.
Assumes you already have the simulator website open in your browser.
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from missions.tello_wrapper import TelloWrapper

def main():
    """Run a simulated drone mission"""
    # Create a TelloWrapper instance with simulator mode forced on
    tello = TelloWrapper(use_simulator=True)
    
    # Check if simulator mode is enabled
    if not tello.simulator_mode:
        print("ERROR: Simulator mode could not be enabled.")
        print("Make sure DroneBlocksTelloSimulator package is installed.")
        return 1
    
    # Connect to the simulator
    if not tello.connect():
        print("ERROR: Failed to connect to the simulator.")
        return 1
    
    print("Connected to simulator successfully!")
    
    # Execute a simple flight test
    try:
        print("\nRunning simple flight test...")
        print("Taking off...")
        tello.takeoff()
        
        print("Moving forward 50cm...")
        tello.move_forward(50)
        
        print("Rotating 90 degrees clockwise...")
        tello.rotate_clockwise(90)
        
        print("Moving forward 50cm...")
        tello.move_forward(50)
        
        print("Rotating 90 degrees clockwise...")
        tello.rotate_clockwise(90)
        
        print("Moving forward 50cm...")
        tello.move_forward(50)
        
        print("Rotating 90 degrees clockwise...")
        tello.rotate_clockwise(90)
        
        print("Moving forward 50cm...")
        tello.move_forward(50)
        
        print("Landing...")
        tello.land()
        
        print("\nFlight test completed successfully!")
        
    except KeyboardInterrupt:
        print("\nFlight interrupted by user.")
        tello.land()
    except Exception as e:
        print(f"\nERROR during flight: {e}")
        tello.emergency()
    finally:
        # Always disconnect
        tello.disconnect()
        
    return 0

if __name__ == "__main__":
    sys.exit(main()) 