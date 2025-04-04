#!/usr/bin/env python3
"""
Advanced waypoint mission planning for DJI Tello drone with simulator support.
This script allows defining and executing complex flight missions for both
real Tello drones and the DroneBlocks simulator.
"""
import sys
import os

# Add parent directory to path so we can import modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tello_wrapper import TelloWrapper, fast_sleep
from missions.video_stream_sim import SimulatedVideoStream
import cv2
import time
import math
import numpy as np

class WaypointMissionPlanner:
    """Class for planning and executing waypoint-based drone missions with simulator support"""
    
    def __init__(self, take_photos=True, save_dir="photos/missions", use_simulator=True):
        """
        Initialize the waypoint mission planner
        
        Args:
            take_photos (bool): Whether to take photos during the mission
            save_dir (str): Directory to save photos if take_photos is True
            use_simulator (bool): Whether to use the simulator
        """
        self.take_photos = take_photos
        self.save_dir = save_dir
        self.waypoints = []
        self.tello_wrapper = None
        self.frame_read = None
        self.photo_count = 0
        self.stream_started = False
        self.use_simulator = use_simulator
        
        # For simulator visualization
        self.sim_video = None
        self.current_pos = [0, 0, 0]  # x, y, z in cm
        self.current_heading = 0  # degrees
        self.flying = False
        
        # Create directory if taking photos and directory doesn't exist
        if take_photos and not os.path.exists(save_dir):
            os.makedirs(save_dir)
            print(f"Created directory: {save_dir}")
    
    def add_waypoint(self, x, y, z, heading=None, take_photo=False, action=None):
        """
        Add a waypoint to the mission
        
        Args:
            x (int): X coordinate relative to starting position (forward/backward in cm)
            y (int): Y coordinate relative to starting position (left/right in cm)
            z (int): Z coordinate relative to starting position (up/down in cm)
            heading (int, optional): Desired heading in degrees at waypoint
            take_photo (bool): Whether to take a photo at this waypoint
            action (callable, optional): Custom action to perform at this waypoint
        """
        self.waypoints.append({
            'x': x,
            'y': y,
            'z': z,
            'heading': heading,
            'take_photo': take_photo,
            'action': action
        })
        print(f"Added waypoint: ({x}, {y}, {z}), heading: {heading}")
        return self
    
    def clear_waypoints(self):
        """Clear all waypoints"""
        self.waypoints = []
        print("All waypoints cleared")
        return self
    
    def connect_drone(self):
        """Connect to the Tello drone or simulator"""
        # Initialize drone
        self.tello_wrapper = TelloWrapper()
        
        # Force simulator mode if requested
        if self.use_simulator:
            self.tello_wrapper.config['simulator']['enabled'] = True
            
        print("Connecting to Tello...")
        self.tello_wrapper.connect()
        
        # Set up simulated video if in simulator mode
        if self.tello_wrapper.simulator_mode:
            print("Running in simulator mode")
            self.sim_video = SimulatedVideoStream()
        else:
            print("Running in real drone mode")
            # Start video stream for real drone if taking photos
            if self.take_photos:
                print("Starting video stream...")
                self.tello_wrapper.drone.streamon()
                self.stream_started = True
                self.frame_read = self.tello_wrapper.drone.get_frame_read()
                time.sleep(2)  # Camera warm-up
        
        return True
    
    def disconnect_drone(self):
        """Disconnect from the Tello drone or simulator"""
        if self.tello_wrapper:
            if not self.tello_wrapper.simulator_mode:
                # Stop video stream if it was started with real drone
                if self.take_photos and self.stream_started:
                    print("Stopping video stream...")
                    cv2.destroyAllWindows()
                    try:
                        self.tello_wrapper.drone.streamoff()
                    except Exception as e:
                        print(f"Error stopping video stream: {e}")
            
            print("Disconnecting...")
            try:
                self.tello_wrapper.disconnect()
            except Exception as e:
                print(f"Error disconnecting: {e}")
            print("Disconnected.")
    
    def take_photo(self, label="waypoint"):
        """
        Take a photo with the drone camera or simulator
        
        Args:
            label (str): Label for the saved photo
        """
        if not self.take_photos:
            return
        
        try:
            # Get the image either from real drone or simulation
            if self.tello_wrapper.simulator_mode and self.sim_video:
                # Update the simulated view
                self.sim_video.update(
                    altitude=self.current_pos[2],
                    direction=self.current_heading,
                    position=[self.current_pos[0], self.current_pos[1]],
                    flying=self.flying
                )
                img = self.sim_video.frame
            elif self.frame_read:
                img = self.frame_read.frame
            else:
                print("No camera feed available")
                return
            
            # Save the photo
            timestamp = int(time.time())
            filename = f"{self.save_dir}/{label}_{self.photo_count}_{timestamp}.jpg"
            cv2.imwrite(filename, img)
            print(f"Photo captured: {filename}")
            
            # Show preview
            small_img = cv2.resize(img, (640, 480))
            cv2.imshow(f"Photo: {label}", small_img)
            cv2.waitKey(500)  # Show briefly
            cv2.destroyAllWindows()
            
            self.photo_count += 1
        except Exception as e:
            print(f"Error taking photo: {e}")
    
    def execute_mission(self, min_battery=30):
        """
        Execute the planned mission
        
        Args:
            min_battery (int): Minimum battery percentage required to start the mission
            
        Returns:
            bool: True if mission completed successfully, False otherwise
        """
        if not self.waypoints:
            print("No waypoints defined. Mission aborted.")
            return False
            
        try:
            # Connect to drone if not already connected
            if not self.tello_wrapper:
                self.connect_drone()
            
            # Check if we need battery check (skip for simulator)
            if not self.tello_wrapper.simulator_mode:
                battery = self.tello_wrapper.drone.get_battery()
                if battery < min_battery:
                    print(f"Battery too low for mission: {battery}%. Need at least {min_battery}%.")
                    return False
            
            # Take off
            print("Taking off...")
            self.tello_wrapper.takeoff()
            self.flying = True
            self.current_pos[2] = 100  # Initial altitude after takeoff (cm)
            fast_sleep(2)  # Stabilize after takeoff
            
            # Initialize current position and heading
            current_x, current_y, current_z = 0, 0, self.current_pos[2]
            current_heading = 0
            
            # Execute each waypoint
            for i, waypoint in enumerate(self.waypoints):
                print(f"\nNavigating to waypoint {i+1}/{len(self.waypoints)}...")
                
                # Calculate relative movement needed
                dx = waypoint['x'] - current_x
                dy = waypoint['y'] - current_y
                dz = waypoint['z'] - current_z
                
                # Adjust height first (safer)
                if dz != 0:
                    print(f"Adjusting height: {dz}cm...")
                    if dz > 0:
                        if self.tello_wrapper.simulator_mode:
                            self.tello_wrapper.drone.fly_up(dz, "cm")
                        else:
                            self.tello_wrapper.drone.move_up(dz)
                    else:
                        if self.tello_wrapper.simulator_mode:
                            self.tello_wrapper.drone.fly_down(-dz, "cm")
                        else:
                            self.tello_wrapper.drone.move_down(-dz)
                    self.current_pos[2] += dz
                    current_z += dz
                    fast_sleep(1.5)
                
                # Rotate to appropriate heading for movement if needed
                if dx != 0 or dy != 0:
                    # Calculate the target heading for movement
                    if dx == 0:
                        target_heading = 90 if dy > 0 else 270
                    else:
                        target_heading = math.degrees(math.atan2(dy, dx))
                        if target_heading < 0:
                            target_heading += 360
                    
                    # Calculate the rotation needed
                    rotation = (target_heading - current_heading) % 360
                    if rotation > 180:
                        rotation -= 360
                    
                    # Execute rotation
                    if rotation != 0:
                        print(f"Rotating: {rotation}° to heading {target_heading}°...")
                        if rotation > 0:
                            if self.tello_wrapper.simulator_mode:
                                self.tello_wrapper.drone.yaw_right(int(rotation))
                            else:
                                self.tello_wrapper.drone.rotate_clockwise(int(rotation))
                        else:
                            if self.tello_wrapper.simulator_mode:
                                self.tello_wrapper.drone.yaw_left(int(-rotation))
                            else:
                                self.tello_wrapper.drone.rotate_counter_clockwise(int(-rotation))
                        current_heading = target_heading
                        self.current_heading = current_heading
                        fast_sleep(1.5)
                    
                    # Calculate distance to move
                    distance = int(math.sqrt(dx**2 + dy**2))
                    print(f"Moving forward: {distance}cm...")
                    
                    # Move the drone
                    if self.tello_wrapper.simulator_mode:
                        self.tello_wrapper.drone.fly_forward(distance, "cm")
                    else:
                        self.tello_wrapper.drone.move_forward(distance)
                    
                    # Update position - important to update both trackers
                    self.current_pos[0] = waypoint['x']
                    self.current_pos[1] = waypoint['y']
                    current_x = waypoint['x']
                    current_y = waypoint['y']
                    fast_sleep(1.5)
                    
                    # For debugging spiral flight
                    print(f"Current position: [{current_x}, {current_y}, {current_z}]")
                
                # Update current position - Z was already updated above
                current_z = waypoint['z']
                
                # Adjust to specific heading if requested
                if waypoint['heading'] is not None and waypoint['heading'] != current_heading:
                    # Calculate the rotation needed
                    rotation = (waypoint['heading'] - current_heading) % 360
                    if rotation > 180:
                        rotation -= 360
                    
                    # Execute rotation
                    print(f"Adjusting final heading to {waypoint['heading']}°...")
                    if rotation > 0:
                        if self.tello_wrapper.simulator_mode:
                            self.tello_wrapper.drone.yaw_right(int(rotation))
                        else:
                            self.tello_wrapper.drone.rotate_clockwise(int(rotation))
                    else:
                        if self.tello_wrapper.simulator_mode:
                            self.tello_wrapper.drone.yaw_left(int(-rotation))
                        else:
                            self.tello_wrapper.drone.rotate_counter_clockwise(int(-rotation))
                    current_heading = waypoint['heading']
                    self.current_heading = current_heading
                    fast_sleep(1.5)
                
                # Take photo if requested
                if waypoint['take_photo']:
                    print("Taking photo...")
                    self.take_photo(f"waypoint_{i+1}")
                
                # Execute custom action if provided
                if waypoint['action']:
                    print("Executing custom action...")
                    try:
                        waypoint['action'](self.tello_wrapper.drone, self)
                    except Exception as e:
                        print(f"Error executing custom action: {e}")
                
                print(f"Waypoint {i+1} reached.")
            
            # Mission completed, return to home
            print("\nMission completed! Returning to launch point...")
            
            # Calculate return path
            return_distance = math.sqrt(current_x**2 + current_y**2)
            if return_distance > 20:  # Only if we're far enough to matter
                # First rotate towards home
                home_heading = (math.degrees(math.atan2(-current_y, -current_x)) + 360) % 360
                rotation = (home_heading - current_heading) % 360
                if rotation > 180:
                    rotation -= 360
                
                if rotation != 0:
                    print(f"Rotating towards home: {rotation}°...")
                    if rotation > 0:
                        if self.tello_wrapper.simulator_mode:
                            self.tello_wrapper.drone.yaw_right(int(rotation))
                        else:
                            self.tello_wrapper.drone.rotate_clockwise(int(rotation))
                    else:
                        if self.tello_wrapper.simulator_mode:
                            self.tello_wrapper.drone.yaw_left(int(-rotation))
                        else:
                            self.tello_wrapper.drone.rotate_counter_clockwise(int(-rotation))
                    current_heading = home_heading
                    self.current_heading = current_heading
                    fast_sleep(1.5)
                
                # Then move home
                print(f"Returning to home, distance: {return_distance:.0f}cm...")
                if self.tello_wrapper.simulator_mode:
                    self.tello_wrapper.drone.fly_forward(int(return_distance), "cm")
                else:
                    self.tello_wrapper.drone.move_forward(int(return_distance))
                # Reset position trackers on return to home
                self.current_pos[0] = 0
                self.current_pos[1] = 0
                current_x = 0
                current_y = 0
                fast_sleep(2)
            
            # Land
            print("Landing...")
            self.tello_wrapper.land()
            self.flying = False
            self.current_pos[2] = 0
            
            return True
            
        except Exception as e:
            print(f"Error during mission: {e}")
            # Try to land safely
            try:
                self.tello_wrapper.land()
                self.flying = False
                self.current_pos[2] = 0
            except Exception as e:
                print(f"Error during emergency landing: {e}")
            return False
        
        finally:
            # Ensure we clean up
            if self.take_photos:
                cv2.destroyAllWindows()

    def create_spiral_mission(self, radius=150, height=100, circles=2, points_per_circle=8, take_photos=True):
        """
        Create a spiral flight mission that circles and rises around a central point.
        
        Args:
            radius (int): Maximum radius of the spiral in cm
            height (int): Maximum height to reach in cm
            circles (int): Number of complete circles to make
            points_per_circle (int): Number of waypoints per circle
            take_photos (bool): Whether to take photos at each waypoint
            
        Returns:
            self: The mission planner object
        """
        self.clear_waypoints()
        
        # First waypoint at starting position, with higher altitude
        self.add_waypoint(0, 0, 100, heading=0, take_photo=take_photos)  # Start at 100cm
        
        # Calculate the height increment per waypoint
        height_inc = height / (circles * points_per_circle)
        
        # Calculate the radius increment per circle
        radius_inc = radius / circles
        
        current_height = 100  # Start at initial takeoff height
        
        # Create waypoints for each circle
        for circle in range(circles):
            # Calculate the radius for this circle
            current_radius = radius_inc * (circle + 1)
            
            # Calculate waypoints around the circle
            for i in range(points_per_circle):
                # Calculate the angle for this waypoint
                angle = (i / points_per_circle) * 2 * math.pi
                
                # Calculate the coordinates
                x = int(current_radius * math.cos(angle))
                y = int(current_radius * math.sin(angle))
                current_height += height_inc
                z = int(current_height)
                
                # Calculate the heading (facing the center)
                heading = int((math.degrees(angle) + 180) % 360)
                
                # Add the waypoint
                self.add_waypoint(x, y, z, heading=heading, take_photo=take_photos)
        
        return self

def test_waypoint_mission():
    """Run a test waypoint mission"""
    # Create mission planner
    mission = WaypointMissionPlanner(take_photos=True, use_simulator=True)
    
    # Add waypoints for a simple square pattern
    mission.add_waypoint(0, 0, 120, heading=0, take_photo=True)  # Rise to 120cm
    mission.add_waypoint(100, 0, 120, heading=0, take_photo=True)  # Forward 100cm
    mission.add_waypoint(100, 100, 120, heading=90, take_photo=True)  # Right 100cm
    mission.add_waypoint(0, 100, 120, heading=180, take_photo=True)  # Back 100cm
    mission.add_waypoint(0, 0, 120, heading=270, take_photo=True)  # Left 100cm
    
    # Execute the mission
    try:
        mission.execute_mission()
    finally:
        mission.disconnect_drone()

def test_spiral_mission():
    """Run a test spiral mission"""
    # Create mission planner
    mission = WaypointMissionPlanner(take_photos=True, use_simulator=True)
    
    # Create a spiral mission (smaller radius for better visualization)
    mission.create_spiral_mission(radius=80, height=80, circles=2, points_per_circle=8)
    
    # Execute the mission
    try:
        mission.execute_mission()
    finally:
        mission.disconnect_drone()

if __name__ == "__main__":
    print("Select a demo mission:")
    print("1. Square Pattern")
    print("2. Spiral Pattern")
    
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        test_waypoint_mission()
    elif choice == "2":
        test_spiral_mission()
    else:
        print("Invalid choice. Exiting.") 