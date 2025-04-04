#!/usr/bin/env python3
"""
Photo capture for DJI Tello drone with simulator support.
This script demonstrates how to capture photos from the Tello's camera
and works with both the real drone and the DroneBlocks simulator.
"""
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tello_wrapper import TelloWrapper
import cv2
import time
import random
import numpy as np

def capture_photo(save_dir="photos", use_simulator=True):
    """
    Capture photos from the Tello drone's camera or simulator
    
    Args:
        save_dir (str): Directory to save photos
        use_simulator (bool): Whether to use the simulator
    """
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")
    
    # Initialize the drone with simulator mode if requested
    tello_wrapper = TelloWrapper()
    if use_simulator:
        # Force simulator mode
        tello_wrapper.config['simulator']['enabled'] = True
    
    stream_started = False
    
    try:
        # Connect to the drone
        print("Connecting to Tello...")
        tello_wrapper.connect()
        simulator_mode = tello_wrapper.simulator_mode
        
        if simulator_mode:
            print("Running in simulator mode")
        else:
            print("Running in real drone mode")
        
        # Take off first (needed for simulator to see the ground)
        print("Taking off...")
        tello_wrapper.takeoff()
        time.sleep(2)
        
        # In simulator mode, we'll generate a simulated photo
        if simulator_mode:
            print("Simulating photo capture...")
            # Generate a simulated photo (a color gradient)
            width, height = 640, 480
            img = create_simulated_photo(width, height)
            timestamp = int(time.time())
            filename = f"{save_dir}/simulated_photo_{timestamp}.jpg"
            cv2.imwrite(filename, img)
            print(f"Simulated photo saved as {filename}")
            
            # Display the image
            print("Displaying simulated image (press any key to continue)...")
            cv2.imshow("Simulated Photo", img)
            cv2.waitKey(0)  # Wait until a key is pressed
            cv2.destroyAllWindows()
        else:
            # With a real drone, use the video stream
            print("Starting video stream...")
            tello_wrapper.drone.streamon()
            stream_started = True
            
            # Get the frame read object
            frame_read = tello_wrapper.drone.get_frame_read()
            
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
            
            # Display the image
            print("Displaying captured image (press any key to continue)...")
            cv2.imshow("Tello Photo", img)
            cv2.waitKey(0)  # Wait until a key is pressed
            cv2.destroyAllWindows()
        
        # Land the drone
        print("Landing...")
        tello_wrapper.land()
        time.sleep(1)
    
    except Exception as e:
        print(f"Error during photo capture: {e}")
        # Try emergency landing
        try:
            tello_wrapper.land()
        except:
            pass
    
    finally:
        # Always stop the video stream and disconnect
        if not simulator_mode and stream_started:
            print("Stopping video stream...")
            try:
                tello_wrapper.drone.streamoff()
            except Exception as e:
                print(f"Error stopping video stream: {e}")
        
        print("Disconnecting...")
        try:
            tello_wrapper.disconnect()
        except Exception as e:
            print(f"Error disconnecting: {e}")
        print("Disconnected.")

def create_simulated_photo(width, height):
    """
    Create a simulated photo (color gradient with random elements)
    
    Args:
        width (int): Image width
        height (int): Image height
        
    Returns:
        numpy.ndarray: Simulated photo image
    """
    # Create a base image (blue sky gradient)
    img = cv2.imread("photos/aerial_photo.jpg") if os.path.exists("photos/aerial_photo.jpg") else None
    
    # If no image available, create a gradient
    if img is None or img.shape[0] < height or img.shape[1] < width:
        img = create_gradient(width, height)
    else:
        # Resize the image if needed
        img = cv2.resize(img, (width, height))
    
    # Add text overlay
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    cv2.putText(img, "SIMULATED PHOTO", (20, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
    cv2.putText(img, timestamp, (20, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
    
    return img

def create_gradient(width, height):
    """Create a blue sky gradient image"""
    # Create an empty image
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Fill with a blue gradient (darker at the top, lighter at the bottom)
    for y in range(height):
        # Calculate intensity based on y position (0 at top, 1 at bottom)
        intensity = y / height
        
        # Create gradient from dark blue to light blue
        blue = int(100 + intensity * 155)
        green = int(100 + intensity * 100)
        red = int(50 + intensity * 100)
        
        # Set row color
        img[y, :] = [blue, green, red]
    
    # Add some clouds (random white patches)
    for _ in range(5):
        x = random.randint(0, width-100)
        y = random.randint(0, height//3)
        size = random.randint(30, 80)
        color = (220, 220, 220)  # Off-white for clouds
        cv2.circle(img, (x, y), size, color, -1)
    
    # Add a simulated ground/landscape at the bottom
    ground_height = height // 5
    ground_start = height - ground_height
    ground_color = (30, 100, 30)  # Green-brown for ground
    img[ground_start:height, :] = ground_color
    
    return img

if __name__ == "__main__":
    capture_photo(use_simulator=True) 