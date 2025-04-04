#!/usr/bin/env python3
"""
Test script for the video_stream_sim.py functionality.
This script demonstrates automated control of the simulated drone and capturing photos.
"""
import sys
import os
import time

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tello_wrapper import TelloWrapper
from missions.video_stream_sim import SimulatedVideoStream
import cv2

def test_video_simulator():
    """Test the video simulator functionality with automated movements"""
    # Create directory for photos
    save_dir = "photos/test"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")
    
    # Initialize the drone with simulator mode
    tello_wrapper = TelloWrapper()
    tello_wrapper.config['simulator']['enabled'] = True
    
    # Set up simulated video
    sim_video = SimulatedVideoStream()
    photo_counter = 0
    
    # Drone state tracking
    drone_altitude = 0
    drone_direction = 0
    drone_position = [0, 0]
    drone_flying = False
    
    try:
        # Connect to the drone
        print("Connecting to Tello simulator...")
        tello_wrapper.connect()
        
        # Take off
        print("Taking off...")
        tello_wrapper.takeoff()
        drone_flying = True
        drone_altitude = 100
        
        # Update the simulated video and take a photo at takeoff position
        sim_video.update(drone_altitude, drone_direction, drone_position, drone_flying)
        frame = sim_video.frame
        timestamp = int(time.time())
        filename = f"{save_dir}/takeoff_photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        photo_counter += 1
        print(f"Photo captured at takeoff: {filename}")
        
        # Move forward
        print("Moving forward...")
        tello_wrapper.drone.fly_forward(50, "cm")
        # Update simulated position
        drone_position[0] += 50
        
        # Update the video and take another photo
        sim_video.update(drone_altitude, drone_direction, drone_position, drone_flying)
        frame = sim_video.frame
        timestamp = int(time.time())
        filename = f"{save_dir}/forward_photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        photo_counter += 1
        print(f"Photo captured after moving forward: {filename}")
        
        # Rotate 90 degrees
        print("Rotating right...")
        tello_wrapper.drone.yaw_right(90)
        drone_direction = 90
        
        # Update the video and take another photo
        sim_video.update(drone_altitude, drone_direction, drone_position, drone_flying)
        frame = sim_video.frame
        timestamp = int(time.time())
        filename = f"{save_dir}/rotated_photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        photo_counter += 1
        print(f"Photo captured after rotation: {filename}")
        
        # Move up higher
        print("Moving up...")
        tello_wrapper.drone.fly_up(50, "cm")
        drone_altitude += 50
        
        # Update the video and take final photo
        sim_video.update(drone_altitude, drone_direction, drone_position, drone_flying)
        frame = sim_video.frame
        timestamp = int(time.time())
        filename = f"{save_dir}/high_photo_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        photo_counter += 1
        print(f"Photo captured at higher altitude: {filename}")
        
        # Land
        print("Landing...")
        tello_wrapper.land()
        drone_flying = False
        drone_altitude = 0
        
    except Exception as e:
        print(f"Error during test: {e}")
        # Try emergency landing
        try:
            tello_wrapper.land()
        except:
            pass
        
    finally:
        # Disconnect
        print("Disconnecting...")
        try:
            tello_wrapper.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
        print("Disconnected")
        print(f"Total photos taken: {photo_counter}")
        
        # Display each photo
        print("\nSaved photos:")
        for i, filename in enumerate(os.listdir(save_dir)):
            if filename.endswith(".jpg"):
                print(f"  {i+1}. {filename}")

if __name__ == "__main__":
    test_video_simulator() 