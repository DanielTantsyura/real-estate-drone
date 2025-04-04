#!/usr/bin/env python3
"""
Autonomous square flight pattern for DJI Tello drone.
This script executes a square flight pattern with optional photo capture at each corner.
"""
from djitellopy import Tello
import cv2
import time
import os

def square_flight(side_length=50, height=80, take_photos=True, save_dir="photos"):
    """
    Execute an autonomous square flight pattern
    
    Args:
        side_length (int): Length of each side of the square in cm
        height (int): Flight height in cm
        take_photos (bool): Whether to take photos at each corner
        save_dir (str): Directory to save photos if take_photos is True
    """
    # Create directory if taking photos and directory doesn't exist
    if take_photos and not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")
    
    # Initialize the drone
    tello = Tello()
    stream_started = False
    
    try:
        # Connect to the drone
        print("Connecting to Tello...")
        tello.connect()
        
        # Check battery level before flying
        battery = tello.get_battery()
        print(f"Battery level: {battery}%")
        
        if battery <= 20:
            print("Battery too low for safe flight")
            return
            
        # Start video stream if taking photos
        if take_photos:
            print("Starting video stream...")
            tello.streamon()
            stream_started = True
            frame_read = tello.get_frame_read()
            time.sleep(2)  # Camera warm-up
            
        # Take off and reach desired height
        print("Taking off...")
        tello.takeoff()
        time.sleep(3)  # Stabilize after takeoff
        
        # Adjust to desired height if needed
        current_height = tello.get_height()
        if current_height < height:
            print(f"Adjusting height to {height}cm...")
            tello.move_up(height - current_height)
            time.sleep(2)
        
        # Execute the square pattern
        print("Executing square flight pattern...")
        
        # Function to capture photo if enabled
        def capture_corner_photo(corner_num):
            if take_photos:
                img = frame_read.frame
                timestamp = int(time.time())
                filename = f"{save_dir}/corner_{corner_num}_{timestamp}.jpg"
                cv2.imwrite(filename, img)
                print(f"Photo captured at corner {corner_num}")
                
                # Display a preview
                small_img = cv2.resize(img, (640, 480))
                cv2.imshow(f"Corner {corner_num}", small_img)
                cv2.waitKey(500)  # Show briefly
                cv2.destroyAllWindows()
        
        # Corner 1: Starting position
        print("Corner 1: Starting position")
        capture_corner_photo(1)
        
        # Move to corner 2
        print("Moving to corner 2...")
        tello.move_forward(side_length)
        time.sleep(2)
        print("Corner 2: Reached")
        capture_corner_photo(2)
        
        # Rotate 90 degrees
        tello.rotate_clockwise(90)
        time.sleep(2)
        
        # Move to corner 3
        print("Moving to corner 3...")
        tello.move_forward(side_length)
        time.sleep(2)
        print("Corner 3: Reached")
        capture_corner_photo(3)
        
        # Rotate 90 degrees
        tello.rotate_clockwise(90)
        time.sleep(2)
        
        # Move to corner 4
        print("Moving to corner 4...")
        tello.move_forward(side_length)
        time.sleep(2)
        print("Corner 4: Reached")
        capture_corner_photo(4)
        
        # Rotate 90 degrees
        tello.rotate_clockwise(90)
        time.sleep(2)
        
        # Return to starting position (complete the square)
        print("Returning to starting position...")
        tello.move_forward(side_length)
        time.sleep(2)
        
        # Final rotation to original orientation
        tello.rotate_clockwise(90)
        time.sleep(2)
        
        print("Square pattern completed!")
        
        # Land
        print("Landing...")
        tello.land()
        print("Landed successfully")
        
    except Exception as e:
        print(f"Error during square flight: {e}")
        # Try to land safely if an error occurs mid-flight
        try:
            tello.land()
            print("Emergency landing executed")
        except Exception as e:
            print(f"Could not execute emergency landing: {e}")
    
    finally:
        # Always stop the video stream and disconnect
        if take_photos and stream_started:
            print("Stopping video stream...")
            cv2.destroyAllWindows()
            try:
                tello.streamoff()
            except Exception as e:
                print(f"Error stopping video stream: {e}")
            
        print("Disconnecting...")
        try:
            tello.end()
        except Exception as e:
            print(f"Error disconnecting: {e}")
        print("Disconnected.")

if __name__ == "__main__":
    # Execute a square with 80cm sides at 100cm height
    square_flight(side_length=80, height=100, take_photos=True) 