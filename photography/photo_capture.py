#!/usr/bin/env python3
"""
Photo capture for DJI Tello drone.
This script demonstrates how to capture photos from the Tello's camera.
"""
from djitellopy import Tello
import cv2
import time
import os

def capture_photo(save_dir="photos"):
    """
    Capture photos from the Tello drone's camera
    
    Args:
        save_dir (str): Directory to save photos
    """
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")
    
    # Initialize the drone
    tello = Tello()
    stream_started = False
    
    try:
        # Connect to the drone
        print("Connecting to Tello...")
        tello.connect()
        
        # Check battery
        battery = tello.get_battery()
        print(f"Battery level: {battery}%")
        
        # Start video stream
        print("Starting video stream...")
        tello.streamon()
        stream_started = True
        
        # Get the frame read object
        frame_read = tello.get_frame_read()
        
        # Allow some time for the camera to warm up
        print("Warming up camera...")
        time.sleep(2)
        
        # Capture a photo
        print("Capturing photo...")
        img = frame_read.frame
        timestamp = int(time.time())
        filename = f"{save_dir}/tello_photo_{timestamp}.jpg"
        cv2.imwrite(filename, img)
        print(f"Photo captured and saved as {filename}")
        
        # Display the image (optional)
        print("Displaying captured image (press any key to continue)...")
        cv2.imshow("Tello Photo", img)
        cv2.waitKey(0)  # Wait until a key is pressed
        cv2.destroyAllWindows()
    
    except Exception as e:
        print(f"Error during photo capture: {e}")
    
    finally:
        # Always stop the video stream and disconnect
        print("Stopping video stream...")
        if stream_started:
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
    capture_photo() 