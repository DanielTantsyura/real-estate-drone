#!/usr/bin/env python3
"""
Simulator implementation of square flight pattern for DJI Tello drone.
This script executes a square flight pattern with simulated photo capture at each corner.
"""
from base_controller import DroneController
import time
import os
from tello_wrapper import fast_sleep

class SquareFlightMission(DroneController):
    """Square flight mission controller for simulator"""
    
    def __init__(self, side_length=80, height=100, config_path=None):
        """
        Initialize the square flight mission
        
        Args:
            side_length (int): Length of each side of the square in cm
            height (int): Flight height in cm
            config_path (str, optional): Path to the config file
        """
        super().__init__(config_path)
        self.side_length = side_length
        self.height = height
        self.corners_visited = 0
        
        # Force simulator mode
        self.simulator_mode = self.config['simulator']['enabled']
        if not self.simulator_mode:
            print("WARNING: This mission is designed for simulator use.")
            print("Please set simulator.enabled to true in your config file.")
    
    def execute_mission(self):
        """Execute the square flight mission"""
        try:
            print(f"Starting square flight mission with side length {self.side_length}cm at height {self.height}cm")
            
            # Take off and reach desired height
            self.takeoff()
            
            # Execute the square pattern
            print("Executing square flight pattern...")
            
            # Corner 1: Starting position
            print("Corner 1: Starting position")
            self._take_corner_photo(1)
            
            # Move to corner 2
            print("Moving to corner 2...")
            self.drone.fly_forward(self.side_length, "cm")
            fast_sleep(0.5)
            print("Corner 2: Reached")
            self._take_corner_photo(2)
            
            # Rotate 90 degrees
            self.drone.yaw_right(90)
            fast_sleep(0.5)
            
            # Move to corner 3
            print("Moving to corner 3...")
            self.drone.fly_forward(self.side_length, "cm")
            fast_sleep(0.5)
            print("Corner 3: Reached")
            self._take_corner_photo(3)
            
            # Rotate 90 degrees
            self.drone.yaw_right(90)
            fast_sleep(0.5)
            
            # Move to corner 4
            print("Moving to corner 4...")
            self.drone.fly_forward(self.side_length, "cm")
            fast_sleep(0.5)
            print("Corner 4: Reached")
            self._take_corner_photo(4)
            
            # Rotate 90 degrees
            self.drone.yaw_right(90)
            fast_sleep(0.5)
            
            # Return to starting position (complete the square)
            print("Returning to starting position...")
            self.drone.fly_forward(self.side_length, "cm")
            fast_sleep(0.5)
            
            # Final rotation to original orientation
            self.drone.yaw_right(90)
            fast_sleep(0.5)
            
            print("Square pattern completed!")
            print(f"Total corners visited: {self.corners_visited}/4")
            
            # Land
            self.land()
            
            return True
            
        except Exception as e:
            print(f"Error during square flight mission: {e}")
            self.emergency_land()
            return False
    
    def _take_corner_photo(self, corner_num):
        """Take a photo at a corner in the square pattern"""
        try:
            if self.simulator_mode:
                # Simulated photo capture
                print(f"[SIMULATOR] Photo captured at corner {corner_num}")
                self.corners_visited += 1
            else:
                # Real photo capture
                timestamp = int(time.time())
                filename = f"corner_{corner_num}_{timestamp}.jpg"
                self.take_photo(filename)
                self.corners_visited += 1
        except Exception as e:
            print(f"Error capturing photo at corner {corner_num}: {e}")


if __name__ == "__main__":
    # Run the mission
    mission = SquareFlightMission(side_length=80, height=100)
    mission.execute_mission()
    mission.disconnect() 