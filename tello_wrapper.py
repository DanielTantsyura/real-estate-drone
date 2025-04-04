#!/usr/bin/env python3
"""
Tello wrapper module that provides a unified interface for both
the real Tello drone and the DroneBlocks simulator.
"""

import os
import json
import time
import sys
from pathlib import Path

# Try to import the simulator package
SIMULATOR_AVAILABLE = False
try:
    from DroneBlocksTelloSimulator import SimulatedDrone
    SIMULATOR_AVAILABLE = True
except ImportError:
    print("DroneBlocksTelloSimulator not installed. Simulator mode will not be available.")

# Always import the real Tello
from djitellopy import Tello as RealTello

# Utility function for optimized sleep
def fast_sleep(seconds):
    """
    Sleep function that respects the DRONE_FAST_MODE environment variable.
    When in fast mode, sleep times are reduced.
    
    Args:
        seconds (float): Time to sleep in seconds
    """
    if os.environ.get("DRONE_FAST_MODE") == "1":
        # In fast mode, reduce sleep times by 75%
        time.sleep(max(0.05, seconds * 0.25))
    else:
        time.sleep(seconds)

class TelloWrapper:
    """
    Wrapper class for DJI Tello drone that provides a unified interface
    for both the real drone and the DroneBlocks simulator.
    """
    
    def __init__(self, config_path=None, use_simulator=None):
        """
        Initialize the Tello wrapper with configuration
        
        Args:
            config_path (str, optional): Path to the config file
            use_simulator (bool, optional): Override config setting for simulator
        """
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Override simulator setting if specified
        if use_simulator is not None:
            self.config['simulator']['enabled'] = use_simulator
            
        # Determine if we should use the simulator
        self.simulator_mode = self.config['simulator']['enabled']
        
        # Check if simulator is available when requested
        if self.simulator_mode and not SIMULATOR_AVAILABLE:
            print("WARNING: Simulator requested but DroneBlocksTelloSimulator package not found.")
            print("Falling back to real drone mode.")
            self.simulator_mode = False
            
        # Initialize the appropriate drone interface
        self.drone = None
        if self.simulator_mode:
            print("Initializing DroneBlocks Tello Simulator...")
            # Get the simulator key from config (could be under 'key' or 'simulator_key')
            sim_key = self.config['simulator'].get('key', self.config['simulator'].get('simulator_key', ''))
            if sim_key:
                print(f"Using simulator key: {sim_key}")
            else:
                print("WARNING: No simulator key provided in config.")
            self.drone = SimulatedDrone(sim_key)
        else:
            print("Initializing real DJI Tello drone...")
            self.drone = RealTello()
            
        # Set default speed
        self.default_speed = self.config['tello']['default_speed']
            
        # Track connection state
        self.connected = False
    
    def _load_config(self, config_path=None):
        """
        Load configuration from file
        
        Args:
            config_path (str, optional): Path to the config file
            
        Returns:
            dict: Configuration dictionary
        """
        # Default configuration
        default_config = {
            "simulator": {
                "enabled": False,
                "simulator_key": "",
                "chrome": {
                    "allow_insecure": True,
                    "simulator_url": "https://sim.droneblocks.io/"
                }
            },
            "tello": {
                "default_speed": 100,
                "emergency_stop": True,
                "photo_dir": "photos",
                "grid_photo_dir": "photos/grid",
                "orbital_photo_dir": "photos/orbital"
            }
        }
        
        # If no config path provided, check some default locations
        if config_path is None:
            possible_paths = [
                "simulator_config.json",
                "config/config.json",
                os.path.join(os.path.dirname(__file__), "simulator_config.json"),
                os.path.join(os.path.dirname(__file__), "config/config.json"),
                os.path.join(os.path.expanduser("~"), ".tello/config.json")
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        # Load config if it exists
        config = default_config
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    loaded_config = json.load(f)
                    # Merge with defaults (simple version)
                    for section in loaded_config:
                        if section in config:
                            if isinstance(config[section], dict) and isinstance(loaded_config[section], dict):
                                config[section].update(loaded_config[section])
                            else:
                                config[section] = loaded_config[section]
                        else:
                            config[section] = loaded_config[section]
            except Exception as e:
                print(f"Error loading config from {config_path}: {e}")
                print("Using default configuration")
        else:
            print("No config file found, using default configuration")
            
        return config
    
    def connect(self):
        """
        Connect to the Tello drone or simulator
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.simulator_mode:
                print("Connecting to DroneBlocks Tello Simulator...")
                # Simulator doesn't need a connect call
                self.connected = True
            else:
                print("Connecting to Tello drone...")
                self.drone.connect()
                # Set default speed for real drone
                self.drone.set_speed(self.default_speed)
                self.connected = True
                
            # Check battery level for real drone
            if not self.simulator_mode:
                battery = self.drone.get_battery()
                print(f"Connected to Tello drone. Battery: {battery}%")
                if battery < 15:
                    print("WARNING: Battery level is low!")
            else:
                print("Connected to DroneBlocks Tello Simulator")
                
            return True
        except Exception as e:
            print(f"Error connecting to Tello: {e}")
            self.connected = False
            return False
    
    def disconnect(self):
        """
        Disconnect from the Tello drone or simulator
        """
        try:
            if self.connected:
                if not self.simulator_mode:
                    # Real drone cleanup
                    print("Disconnecting from Tello drone...")
                    self.drone.end()
                else:
                    # Simulator cleanup
                    print("Disconnecting from Tello simulator...")
                    # No specific disconnect needed for simulator
                self.connected = False
        except Exception as e:
            print(f"Error disconnecting from Tello: {e}")
    
    def takeoff(self):
        """
        Take off with the Tello drone
        
        Returns:
            bool: True if takeoff successful, False otherwise
        """
        try:
            if not self.connected:
                self.connect()
                
            print("Taking off...")
            self.drone.takeoff()
            fast_sleep(1)  # Reduced stabilization time
            return True
        except Exception as e:
            print(f"Error during takeoff: {e}")
            return False
    
    def land(self):
        """
        Land the Tello drone
        
        Returns:
            bool: True if landing successful, False otherwise
        """
        try:
            print("Landing...")
            self.drone.land()
            time.sleep(2)  # Give time to complete
            return True
        except Exception as e:
            print(f"Error during landing: {e}")
            return False
    
    def emergency(self):
        """
        Emergency stop (cut motors)
        """
        try:
            print("EMERGENCY STOP - Cutting motors!")
            self.drone.emergency()
        except Exception as e:
            print(f"Error during emergency stop: {e}")
    
    def streamon(self):
        """
        Start video stream
        
        Returns:
            bool: True if stream started successfully, False otherwise
        """
        try:
            if not self.simulator_mode:
                print("Starting video stream...")
                self.drone.streamon()
            else:
                print("[SIMULATOR] Video stream would start here")
            return True
        except Exception as e:
            print(f"Error starting video stream: {e}")
            return False
    
    def streamoff(self):
        """
        Stop video stream
        """
        try:
            if not self.simulator_mode:
                print("Stopping video stream...")
                self.drone.streamoff()
            else:
                print("[SIMULATOR] Video stream would stop here")
        except Exception as e:
            print(f"Error stopping video stream: {e}")
    
    def get_frame_read(self):
        """
        Get the current frame from the video stream
        
        Returns:
            BackgroundFrameRead: Frame read object for real drone, None for simulator
        """
        if not self.simulator_mode:
            return self.drone.get_frame_read()
        return None
    
    def move_forward(self, distance_cm):
        """
        Move forward by distance_cm
        
        Args:
            distance_cm (int): Distance in centimeters
        """
        try:
            if self.simulator_mode:
                self.drone.fly_forward(distance_cm, "cm")
            else:
                self.drone.move_forward(distance_cm)
        except Exception as e:
            print(f"Error moving forward: {e}")
    
    def move_back(self, distance_cm):
        """
        Move backward by distance_cm
        
        Args:
            distance_cm (int): Distance in centimeters
        """
        try:
            if self.simulator_mode:
                self.drone.fly_backward(distance_cm, "cm")
            else:
                self.drone.move_back(distance_cm)
        except Exception as e:
            print(f"Error moving backward: {e}")
    
    def move_left(self, distance_cm):
        """
        Move left by distance_cm
        
        Args:
            distance_cm (int): Distance in centimeters
        """
        try:
            if self.simulator_mode:
                self.drone.fly_left(distance_cm, "cm")
            else:
                self.drone.move_left(distance_cm)
        except Exception as e:
            print(f"Error moving left: {e}")
    
    def move_right(self, distance_cm):
        """
        Move right by distance_cm
        
        Args:
            distance_cm (int): Distance in centimeters
        """
        try:
            if self.simulator_mode:
                self.drone.fly_right(distance_cm, "cm")
            else:
                self.drone.move_right(distance_cm)
        except Exception as e:
            print(f"Error moving right: {e}")
    
    def move_up(self, distance_cm):
        """
        Move up by distance_cm
        
        Args:
            distance_cm (int): Distance in centimeters
        """
        try:
            if self.simulator_mode:
                self.drone.fly_up(distance_cm, "cm")
            else:
                self.drone.move_up(distance_cm)
        except Exception as e:
            print(f"Error moving up: {e}")
    
    def move_down(self, distance_cm):
        """
        Move down by distance_cm
        
        Args:
            distance_cm (int): Distance in centimeters
        """
        try:
            if self.simulator_mode:
                self.drone.fly_down(distance_cm, "cm")
            else:
                self.drone.move_down(distance_cm)
        except Exception as e:
            print(f"Error moving down: {e}")
    
    def rotate_clockwise(self, degrees):
        """
        Rotate clockwise by degrees
        
        Args:
            degrees (int): Degrees to rotate
        """
        try:
            if self.simulator_mode:
                self.drone.yaw_right(degrees)
            else:
                self.drone.rotate_clockwise(degrees)
        except Exception as e:
            print(f"Error rotating clockwise: {e}")
    
    def rotate_counter_clockwise(self, degrees):
        """
        Rotate counter-clockwise by degrees
        
        Args:
            degrees (int): Degrees to rotate
        """
        try:
            if self.simulator_mode:
                self.drone.yaw_left(degrees)
            else:
                self.drone.rotate_counter_clockwise(degrees)
        except Exception as e:
            print(f"Error rotating counter-clockwise: {e}")
    
    def take_photo(self, filename=None, directory=None):
        """
        Take a photo with the Tello drone
        
        Args:
            filename (str, optional): Filename to save the photo
            directory (str, optional): Directory to save the photo
            
        Returns:
            str: Path to saved photo or None if failed
        """
        if self.simulator_mode:
            print(f"[SIMULATOR] Taking photo: {filename or 'photo.jpg'}")
            return None
            
        try:
            if not self.connected:
                self.connect()
                
            # Ensure stream is on
            self.streamon()
            time.sleep(0.5)  # Give time to initialize
            
            # Get frame
            frame_read = self.get_frame_read()
            if frame_read is None:
                print("Error: No frame read available")
                return None
                
            # Get the image
            img = frame_read.frame
            if img is None:
                print("Error: No image captured")
                return None
                
            # Prepare filename and path
            if directory is None:
                directory = self.config['tello']['photo_dir']
                
            # Ensure directory exists
            os.makedirs(directory, exist_ok=True)
            
            if filename is None:
                filename = f"tello_photo_{int(time.time())}.jpg"
                
            # Save the photo
            import cv2
            photo_path = os.path.join(directory, filename)
            success = cv2.imwrite(photo_path, img)
            
            if success:
                print(f"Photo saved: {photo_path}")
                return photo_path
            else:
                print("Error: Failed to save photo")
                return None
                
        except Exception as e:
            print(f"Error taking photo: {e}")
            return None


# Simple test if run directly
if __name__ == "__main__":
    tello = TelloWrapper()
    
    # Check if simulator mode
    if tello.simulator_mode:
        print("Running in simulator mode")
    else:
        print("Running in real drone mode")
    
    try:
        # Connect
        if tello.connect():
            print("Connection successful")
            
            # Takeoff
            if input("Takeoff? (y/n): ").lower() == 'y':
                tello.takeoff()
                
                # Move forward
                if input("Move forward? (y/n): ").lower() == 'y':
                    tello.move_forward(30)
                    time.sleep(2)
                
                # Rotate
                if input("Rotate? (y/n): ").lower() == 'y':
                    tello.rotate_clockwise(90)
                    time.sleep(2)
                
                # Take photo
                if input("Take photo? (y/n): ").lower() == 'y':
                    tello.take_photo()
                
                # Land
                tello.land()
            
        # Disconnect in any case
        tello.disconnect()
        
    except KeyboardInterrupt:
        print("\nOperation interrupted by user")
        # Emergency land if in the air
        tello.land()
        tello.disconnect()
    except Exception as e:
        print(f"Error during test: {e}")
        # Emergency land if in the air
        tello.emergency()
        tello.disconnect() 