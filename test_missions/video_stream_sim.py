#!/usr/bin/env python3
"""
Interactive video stream for DJI Tello drone with simulator support.
This script displays a simulated video feed and allows controlling the drone with key presses.
"""
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tello_wrapper import TelloWrapper, fast_sleep
import cv2
import time
import numpy as np
import math
import random

class SimulatedVideoStream:
    """Class to generate a simulated video feed for the Tello drone simulator"""
    
    def __init__(self, width=640, height=480):
        """Initialize the simulated video stream"""
        self.width = width
        self.height = height
        self.altitude = 0
        self.direction = 0  # 0-360 degrees, 0 is forward
        self.position = [0, 0]  # [x, y] in cm
        self.flying = False
        self.last_update = time.time()
        self.frame = self._create_frame()
        
    def update(self, altitude, direction, position, flying):
        """Update the simulated video parameters"""
        self.altitude = altitude
        self.direction = direction
        self.position = position
        self.flying = flying
        self.last_update = time.time()
        self.frame = self._create_frame()
        
    def _create_frame(self):
        """Create a simulated camera frame based on current position"""
        # Create a base image (sky gradient)
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        
        # Fill with a blue sky gradient
        for y in range(self.height):
            # Calculate intensity based on y position
            intensity = y / self.height
            
            # Create gradient from dark blue to light blue
            blue = int(100 + intensity * 155)
            green = int(100 + intensity * 100)
            red = int(30 + intensity * 120)
            
            # Set row color
            frame[y, :] = [blue, green, red]
        
        # If we're flying, create more realistic scene
        if self.flying:
            # Add horizon line
            horizon_y = self.height // 2 - int(self.altitude * 0.1)
            horizon_y = max(50, min(self.height - 50, horizon_y))  # Keep within frame
            
            # Add ground below horizon (green/brown)
            for y in range(horizon_y, self.height):
                # Calculate ground intensity (darker as we look further)
                ground_intensity = (y - horizon_y) / (self.height - horizon_y)
                ground_color = [
                    int(30 + ground_intensity * 40),  # Blue
                    int(100 - ground_intensity * 30),  # Green
                    int(70 - ground_intensity * 20)   # Red
                ]
                frame[y, :] = ground_color
                
            # Add grid pattern to simulate ground
            grid_size = max(20, min(60, int(200 - self.altitude * 0.2)))
            for x in range(0, self.width, grid_size):
                for y in range(horizon_y, self.height, grid_size):
                    # Adjust grid based on direction
                    adjusted_x = x + int(math.sin(math.radians(self.direction)) * 20)
                    adjusted_y = y + int(math.cos(math.radians(self.direction)) * 20)
                    if 0 <= adjusted_x < self.width and horizon_y <= adjusted_y < self.height:
                        # Draw grid point
                        grid_pt_size = max(1, min(5, int(6 - self.altitude / 50)))
                        cv2.circle(frame, (adjusted_x, adjusted_y), grid_pt_size, (70, 70, 70), -1)
            
            # Add clouds if we're high enough
            if self.altitude > 100:
                for _ in range(3):
                    cloud_x = random.randint(0, self.width-50)
                    cloud_y = random.randint(20, horizon_y - 20)
                    cloud_size = random.randint(20, 40)
                    cv2.circle(frame, (cloud_x, cloud_y), cloud_size, (200, 200, 220), -1)
        
        # Add HUD overlay
        self._add_hud(frame)
        
        return frame
    
    def _add_hud(self, frame):
        """Add Heads-Up Display information to the frame"""
        # Add altitude
        cv2.putText(frame, f"ALT: {self.altitude}cm", (10, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add direction/heading
        cv2.putText(frame, f"DIR: {int(self.direction)}°", (10, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add position
        cv2.putText(frame, f"POS: [{self.position[0]}, {self.position[1]}]", (10, 60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add simulated time
        cv2.putText(frame, f"SIM TIME: {time.strftime('%H:%M:%S')}", (self.width - 180, 20), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        # Add battery (simulated)
        battery = 100 - int((time.time() - self.last_update) / 60)  # Decrease 1% per minute
        battery = max(0, min(100, battery))
        battery_color = (0, 255, 0) if battery > 20 else (0, 0, 255)
        cv2.putText(frame, f"BAT: {battery}%", (self.width - 180, 40), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, battery_color, 1)
        
        # Add central crosshair
        center_x, center_y = self.width // 2, self.height // 2
        cv2.line(frame, (center_x - 20, center_y), (center_x + 20, center_y), (0, 255, 0), 1)
        cv2.line(frame, (center_x, center_y - 20), (center_x, center_y + 20), (0, 255, 0), 1)
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), 1)
        
        # Add "SIMULATOR" indicator
        cv2.putText(frame, "SIMULATOR", (center_x - 50, self.height - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
        
        return frame

def interactive_stream_sim(save_dir="photos", use_simulator=True):
    """
    Display simulated video feed and provide interactive controls
    
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
        use_simulator (bool): Whether to use the simulator
    """
    # Create directory if it doesn't exist
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created directory: {save_dir}")
    
    # Initialize the drone with simulator mode
    tello_wrapper = TelloWrapper()
    if use_simulator:
        # Force simulator mode
        tello_wrapper.config['simulator']['enabled'] = True
    
    # Set up simulated video if in simulator mode
    sim_video = None
    photo_counter = 0
    
    # Drone state tracking
    drone_altitude = 0
    drone_direction = 0
    drone_position = [0, 0]
    drone_flying = False
    drone_speed = 30  # cm/s
    
    try:
        # Connect to the drone
        print("Connecting to Tello...")
        tello_wrapper.connect()
        simulator_mode = tello_wrapper.simulator_mode
        
        if simulator_mode:
            print("Running in simulator mode")
            # Create simulated video stream
            sim_video = SimulatedVideoStream()
        else:
            print("Running in real drone mode")
            # Start video stream for real drone
            print("Starting video stream...")
            tello_wrapper.drone.streamon()
            frame_read = tello_wrapper.drone.get_frame_read()
            # Allow some time for the camera to warm up
            print("Warming up camera...")
            time.sleep(2)
        
        # Set drone speed
        if hasattr(tello_wrapper.drone, 'set_speed'):
            tello_wrapper.drone.set_speed(drone_speed)
        
        print("\nControls:")
        print("  'q': Quit the application")
        print("  'p': Take a picture")
        print("  't': Take off")
        print("  'l': Land")
        print("  'w/a/s/d': Move forward/left/backward/right")
        print("  'Arrow Up/Down': Move up/down")
        print("  'Arrow Left/Right': Rotate counter-clockwise/clockwise\n")
        
        # Main loop
        while True:
            # Get the current frame
            if simulator_mode and sim_video:
                # Update simulated video
                sim_video.update(drone_altitude, drone_direction, drone_position, drone_flying)
                frame = sim_video.frame
            else:
                # Get real frame from drone
                frame = frame_read.frame
            
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
                if not drone_flying:
                    print("Taking off...")
                    tello_wrapper.takeoff()
                    drone_flying = True
                    drone_altitude = 100  # Initial altitude after takeoff in cm
                
            elif key == ord('l'):
                # Land
                if drone_flying:
                    print("Landing...")
                    tello_wrapper.land()
                    drone_flying = False
                    drone_altitude = 0
                
            elif key == ord('w'):
                # Move forward
                if drone_flying:
                    print("Moving forward...")
                    if simulator_mode:
                        tello_wrapper.drone.fly_forward(drone_speed, "cm")
                        # Update simulated position
                        dx = drone_speed * math.cos(math.radians(drone_direction))
                        dy = drone_speed * math.sin(math.radians(drone_direction))
                        drone_position[0] += dx
                        drone_position[1] += dy
                    else:
                        tello_wrapper.drone.move_forward(drone_speed)
                
            elif key == ord('s'):
                # Move backward
                if drone_flying:
                    print("Moving backward...")
                    if simulator_mode:
                        tello_wrapper.drone.fly_backward(drone_speed, "cm")
                        # Update simulated position
                        dx = drone_speed * math.cos(math.radians(drone_direction))
                        dy = drone_speed * math.sin(math.radians(drone_direction))
                        drone_position[0] -= dx
                        drone_position[1] -= dy
                    else:
                        tello_wrapper.drone.move_back(drone_speed)
                
            elif key == ord('a'):
                # Move left
                if drone_flying:
                    print("Moving left...")
                    if simulator_mode:
                        tello_wrapper.drone.fly_left(drone_speed, "cm")
                        # Update simulated position
                        dx = drone_speed * math.cos(math.radians(drone_direction + 90))
                        dy = drone_speed * math.sin(math.radians(drone_direction + 90))
                        drone_position[0] += dx
                        drone_position[1] += dy
                    else:
                        tello_wrapper.drone.move_left(drone_speed)
                
            elif key == ord('d'):
                # Move right
                if drone_flying:
                    print("Moving right...")
                    if simulator_mode:
                        tello_wrapper.drone.fly_right(drone_speed, "cm")
                        # Update simulated position
                        dx = drone_speed * math.cos(math.radians(drone_direction - 90))
                        dy = drone_speed * math.sin(math.radians(drone_direction - 90))
                        drone_position[0] += dx
                        drone_position[1] += dy
                    else:
                        tello_wrapper.drone.move_right(drone_speed)
                
            elif key == 82:  # Up arrow
                # Move up
                if drone_flying:
                    print("Moving up...")
                    if simulator_mode:
                        tello_wrapper.drone.fly_up(drone_speed, "cm")
                        # Update simulated altitude
                        drone_altitude += drone_speed
                    else:
                        tello_wrapper.drone.move_up(drone_speed)
                
            elif key == 84:  # Down arrow
                # Move down
                if drone_flying:
                    print("Moving down...")
                    if simulator_mode:
                        tello_wrapper.drone.fly_down(drone_speed, "cm")
                        # Update simulated altitude
                        drone_altitude = max(0, drone_altitude - drone_speed)
                    else:
                        tello_wrapper.drone.move_down(drone_speed)
                
            elif key == 81:  # Left arrow
                # Rotate counter-clockwise
                if drone_flying:
                    print("Rotating counter-clockwise...")
                    if simulator_mode:
                        tello_wrapper.drone.yaw_left(30)
                        # Update simulated direction
                        drone_direction = (drone_direction - 30) % 360
                    else:
                        tello_wrapper.drone.rotate_counter_clockwise(30)
                
            elif key == 83:  # Right arrow
                # Rotate clockwise
                if drone_flying:
                    print("Rotating clockwise...")
                    if simulator_mode:
                        tello_wrapper.drone.yaw_right(30)
                        # Update simulated direction
                        drone_direction = (drone_direction + 30) % 360
                    else:
                        tello_wrapper.drone.rotate_clockwise(30)
    
    except Exception as e:
        print(f"Error during interactive stream: {e}")
        # Try to land safely if an error occurs mid-flight
        try:
            tello_wrapper.land()
            print("Emergency landing executed")
        except Exception as e:
            print(f"Could not execute emergency landing: {e}")
    
    finally:
        # Always stop the video stream and disconnect
        print("Stopping video stream...")
        cv2.destroyAllWindows()
        
        # If not in simulator mode and using real drone
        if not simulator_mode and hasattr(tello_wrapper.drone, 'streamoff'):
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
        print(f"Total photos taken: {photo_counter}")

if __name__ == "__main__":
    interactive_stream_sim(use_simulator=True) 