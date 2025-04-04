#!/usr/bin/env python3
"""
Interactive video stream for DJI Tello drone.
This script displays the live video feed and allows taking photos with key presses.
"""
from djitellopy import Tello
import cv2
import time
import os

def interactive_stream(save_dir="photos"):
    """
    Display live video feed and provide interactive controls
    
    Controls:
        - 'q': Quit the application
        - 'p': Take a picture
        - 't': Take off
        - 'l': Land
        - 'w': Move forward
        - 's': Move backward
        - 'a': Move left
        - 'd': Move right
        - 'Up': Move up
        - 'Down': Move down
        - 'Left': Rotate counter-clockwise
        - 'Right': Rotate clockwise
    
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
    photo_counter = 0
    
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
        
        # Control speed (cm/s)
        speed = 30
        tello.set_speed(speed)
        
        print("\nControls:")
        print("  'q': Quit the application")
        print("  'p': Take a picture")
        print("  't': Take off")
        print("  'l': Land")
        print("  'w/a/s/d': Move forward/left/backward/right")
        print("  'Arrow Up/Down': Move up/down")
        print("  'Arrow Left/Right': Rotate counter-clockwise/clockwise\n")
        
        while True:
            # Get the current frame
            frame = frame_read.frame
            
            # Add battery and status information to the frame
            battery = tello.get_battery()
            height = tello.get_height()
            
            cv2.putText(frame, f"Battery: {battery}%", (10, 20), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(frame, f"Height: {height}cm", (10, 40), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            
            # Display the frame
            cv2.imshow("Tello Camera", frame)
            
            # Check for key presses (wait 1ms)
            key = cv2.waitKey(1) & 0xFF
            
            # Handle key presses
            if key == ord('q'):
                # Quit
                print("Quitting application...")
                break
                
            elif key == ord('p'):
                # Take a picture
                timestamp = int(time.time())
                filename = f"{save_dir}/tello_photo_{timestamp}.jpg"
                cv2.imwrite(filename, frame)
                photo_counter += 1
                print(f"Photo captured and saved as {filename}")
                
            elif key == ord('t'):
                # Take off
                print("Taking off...")
                tello.takeoff()
                
            elif key == ord('l'):
                # Land
                print("Landing...")
                tello.land()
                
            elif key == ord('w'):
                # Move forward
                print("Moving forward...")
                tello.move_forward(speed)
                
            elif key == ord('s'):
                # Move backward
                print("Moving backward...")
                tello.move_back(speed)
                
            elif key == ord('a'):
                # Move left
                print("Moving left...")
                tello.move_left(speed)
                
            elif key == ord('d'):
                # Move right
                print("Moving right...")
                tello.move_right(speed)
                
            elif key == 82:  # Up arrow
                # Move up
                print("Moving up...")
                tello.move_up(speed)
                
            elif key == 84:  # Down arrow
                # Move down
                print("Moving down...")
                tello.move_down(speed)
                
            elif key == 81:  # Left arrow
                # Rotate counter-clockwise
                print("Rotating counter-clockwise...")
                tello.rotate_counter_clockwise(30)
                
            elif key == 83:  # Right arrow
                # Rotate clockwise
                print("Rotating clockwise...")
                tello.rotate_clockwise(30)
    
    except Exception as e:
        print(f"Error during interactive stream: {e}")
        # Try to land safely if an error occurs mid-flight
        try:
            tello.land()
            print("Emergency landing executed")
        except Exception as e:
            print(f"Could not execute emergency landing: {e}")
    
    finally:
        # Always stop the video stream and disconnect
        print("Stopping video stream...")
        cv2.destroyAllWindows()
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
        print(f"Total photos taken: {photo_counter}")

if __name__ == "__main__":
    interactive_stream() 