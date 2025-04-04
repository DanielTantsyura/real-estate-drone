#!/usr/bin/env python3
"""
Base controller for DJI Tello drone that works with both simulator and real drone
"""

import os
import json
import time
import cv2
import sys
from pathlib import Path

# Import the TelloWrapper
from tello_wrapper import TelloWrapper

class DroneController:
    """Base class for drone mission controllers"""
    
    def __init__(self, config_path=None):
        """
        Initialize the drone controller
        
        Args:
            config_path (str, optional): Path to the config file
        """
        # Initialize drone
        self.tello = TelloWrapper(config_path)
        self.drone = self.tello.drone  # For direct access if needed
        self.config = self.tello.config
        self.simulator_mode = self.tello.simulator_mode
        
        # Set higher speed for simulator
        if self.simulator_mode and hasattr(self.drone, 'set_speed'):
            try:
                self.drone.set_speed(100)  # Set to maximum speed
            except:
                pass  # Ignore if set_speed is not available
        
        # Photo storage paths
        self._ensure_photo_directories()
    
    def _ensure_photo_directories(self):
        """Ensure all photo directories exist"""
        os.makedirs(self.config['tello']['photo_dir'], exist_ok=True)
        os.makedirs(self.config['tello']['grid_photo_dir'], exist_ok=True)
        os.makedirs(self.config['tello']['orbital_photo_dir'], exist_ok=True)
    
    def connect(self):
        """
        Connect to the drone
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        return self.tello.connect()
    
    def disconnect(self):
        """Disconnect from the drone"""
        self.tello.disconnect()
    
    def takeoff(self):
        """
        Take off with the drone
        
        Returns:
            bool: True if takeoff successful, False otherwise
        """
        return self.tello.takeoff()
    
    def land(self):
        """
        Land the drone
        
        Returns:
            bool: True if landing successful, False otherwise
        """
        return self.tello.land()
    
    def emergency_land(self):
        """Emergency land the drone"""
        try:
            print("Emergency landing initiated")
            if self.simulator_mode:
                # Simulator doesn't have emergency method, use land instead
                self.land()
            elif self.config['tello']['emergency_stop']:
                # Cut motors immediately
                self.tello.emergency()
            else:
                # Try to land normally
                self.land()
        except Exception as e:
            print(f"Error during emergency landing: {e}")
    
    def start_video(self):
        """
        Start video stream
        
        Returns:
            bool: True if stream started successfully, False otherwise
        """
        return self.tello.streamon()
    
    def stop_video(self):
        """Stop video stream"""
        self.tello.streamoff()
    
    def take_photo(self, filename=None, directory=None):
        """
        Take a photo with the drone
        
        Args:
            filename (str, optional): Filename to save the photo
            directory (str, optional): Directory to save the photo
            
        Returns:
            str: Path to saved photo or None if failed
        """
        return self.tello.take_photo(filename, directory)
    
    def display_photo(self, photo_path):
        """
        Display a photo using OpenCV
        
        Args:
            photo_path (str): Path to the photo
            
        Returns:
            bool: True if display successful, False otherwise
        """
        try:
            if self.simulator_mode:
                print(f"[SIMULATOR] Would display photo: {photo_path}")
                return True
                
            # Check if photo exists
            if not os.path.exists(photo_path):
                print(f"Error: Photo not found at {photo_path}")
                return False
                
            # Load and display the image
            img = cv2.imread(photo_path)
            if img is None:
                print(f"Error: Failed to load image from {photo_path}")
                return False
                
            # Resize if the image is too large
            max_width = 800
            if img.shape[1] > max_width:
                scale = max_width / img.shape[1]
                img = cv2.resize(img, (int(img.shape[1] * scale), int(img.shape[0] * scale)))
                
            # Display the image
            cv2.imshow('Tello Photo', img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            return True
            
        except Exception as e:
            print(f"Error displaying photo: {e}")
            return False
    
    def execute_mission(self):
        """
        Execute the mission (to be implemented by subclasses)
        
        Returns:
            bool: True if mission successful, False otherwise
        """
        print("Base controller has no mission implementation")
        print("This method should be overridden by subclasses")
        return False


# Simple test if run directly
if __name__ == "__main__":
    controller = DroneController()
    
    try:
        if controller.connect():
            print("Connection successful")
            
            if input("Take off? (y/n): ").lower() == 'y':
                controller.takeoff()
                time.sleep(3)
                
                # Take a photo
                if input("Take a photo? (y/n): ").lower() == 'y':
                    photo_path = controller.take_photo()
                    if photo_path and input("Display photo? (y/n): ").lower() == 'y':
                        controller.display_photo(photo_path)
                
                controller.land()
            
        # Always disconnect
        controller.disconnect()
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        controller.emergency_land()
        controller.disconnect()
    except Exception as e:
        print(f"Error during test: {e}")
        controller.emergency_land()
        controller.disconnect() 