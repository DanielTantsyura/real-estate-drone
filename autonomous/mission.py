#!/usr/bin/env python3
"""
Advanced mission planning for DJI Tello drone.
This script allows defining and executing complex flight missions.
"""
from djitellopy import Tello
import cv2
import time
import os
import math

class MissionPlanner:
    """Class for planning and executing complex drone missions"""
    
    def __init__(self, take_photos=True, save_dir="photos"):
        """
        Initialize the mission planner
        
        Args:
            take_photos (bool): Whether to take photos during the mission
            save_dir (str): Directory to save photos if take_photos is True
        """
        self.take_photos = take_photos
        self.save_dir = save_dir
        self.waypoints = []
        self.tello = None
        self.frame_read = None
        self.photo_count = 0
        self.stream_started = False
        
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
        """Connect to the Tello drone"""
        self.tello = Tello()
        print("Connecting to Tello...")
        self.tello.connect()
        
        # Check battery level
        battery = self.tello.get_battery()
        print(f"Battery level: {battery}%")
        
        # Start video stream if taking photos
        if self.take_photos:
            print("Starting video stream...")
            self.tello.streamon()
            self.stream_started = True
            self.frame_read = self.tello.get_frame_read()
            time.sleep(2)  # Camera warm-up
            
        return battery
    
    def disconnect_drone(self):
        """Disconnect from the Tello drone"""
        if self.tello:
            # Stop video stream if it was started
            if self.take_photos and self.stream_started:
                print("Stopping video stream...")
                cv2.destroyAllWindows()
                try:
                    self.tello.streamoff()
                except Exception as e:
                    print(f"Error stopping video stream: {e}")
                
            print("Disconnecting...")
            try:
                self.tello.end()
            except Exception as e:
                print(f"Error disconnecting: {e}")
            print("Disconnected.")
    
    def take_photo(self, label="waypoint"):
        """
        Take a photo with the drone camera
        
        Args:
            label (str): Label for the saved photo
        """
        if not self.take_photos or not self.frame_read or not self.stream_started:
            return
        
        try:
            img = self.frame_read.frame
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
            if not self.tello:
                battery = self.connect_drone()
            else:
                battery = self.tello.get_battery()
                
            # Check battery level
            if battery < min_battery:
                print(f"Battery too low for mission: {battery}%. Need at least {min_battery}%.")
                return False
            
            # Take off
            print("Taking off...")
            self.tello.takeoff()
            time.sleep(3)  # Stabilize after takeoff
            
            # Initialize current position and heading
            current_x, current_y, current_z = 0, 0, 0
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
                        self.tello.move_up(dz)
                    else:
                        self.tello.move_down(-dz)
                    time.sleep(2)
                
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
                            self.tello.rotate_clockwise(int(rotation))
                        else:
                            self.tello.rotate_counter_clockwise(int(-rotation))
                        time.sleep(2)
                        current_heading = target_heading
                    
                    # Calculate distance to move
                    distance = math.sqrt(dx**2 + dy**2)
                    print(f"Moving forward: {distance:.0f}cm...")
                    self.tello.move_forward(int(distance))
                    time.sleep(2)
                
                # Update current position
                current_x, current_y, current_z = waypoint['x'], waypoint['y'], waypoint['z']
                
                # Adjust to specific heading if requested
                if waypoint['heading'] is not None and waypoint['heading'] != current_heading:
                    # Calculate the rotation needed
                    rotation = (waypoint['heading'] - current_heading) % 360
                    if rotation > 180:
                        rotation -= 360
                    
                    # Execute rotation
                    print(f"Adjusting final heading to {waypoint['heading']}°...")
                    if rotation > 0:
                        self.tello.rotate_clockwise(int(rotation))
                    else:
                        self.tello.rotate_counter_clockwise(int(-rotation))
                    time.sleep(2)
                    current_heading = waypoint['heading']
                
                # Take photo if requested
                if waypoint['take_photo']:
                    print("Taking photo...")
                    self.take_photo(f"waypoint_{i+1}")
                
                # Execute custom action if provided
                if waypoint['action']:
                    print("Executing custom action...")
                    try:
                        waypoint['action'](self.tello, self)
                    except Exception as e:
                        print(f"Error executing custom action: {e}")
                
                print(f"Waypoint {i+1} reached.")
            
            # Mission completed, return to home
            print("\nMission completed! Returning to launch point...")
            
            # Calculate return home movements
            if current_z > 20:  # If we're high enough, go home at current height
                # First face home
                return_heading = (180 + math.degrees(math.atan2(current_y, current_x))) % 360
                # Calculate the rotation needed
                rotation = (return_heading - current_heading) % 360
                if rotation > 180:
                    rotation -= 360
                
                # Execute rotation to face home
                if rotation != 0:
                    print(f"Rotating to face home: {rotation}°...")
                    if rotation > 0:
                        self.tello.rotate_clockwise(int(rotation))
                    else:
                        self.tello.rotate_counter_clockwise(int(-rotation))
                    time.sleep(2)
                
                # Calculate distance home
                distance_home = math.sqrt(current_x**2 + current_y**2)
                if distance_home > 20:  # If we're far enough to need to move
                    print(f"Moving home: {distance_home:.0f}cm...")
                    self.tello.move_forward(int(distance_home))
                    time.sleep(2)
            
            # Land
            print("Landing...")
            self.tello.land()
            print("Landed successfully")
            
            return True
            
        except Exception as e:
            print(f"Error during mission: {e}")
            # Try to land safely if an error occurs mid-flight
            try:
                self.tello.land()
                print("Emergency landing executed")
            except Exception as e:
                print(f"Could not execute emergency landing: {e}")
            return False
            
        finally:
            # Take final battery reading
            try:
                if self.tello:
                    final_battery = self.tello.get_battery()
                    print(f"Mission completed. Final battery level: {final_battery}%")
                    print(f"Battery used: {battery - final_battery}%")
            except Exception as e:
                print(f"Could not get final battery reading: {e}")

def create_spiral_mission(radius=100, height=150, turns=2, points_per_turn=8):
    """
    Create a spiral mission pattern
    
    Args:
        radius (int): Radius of the spiral in cm
        height (int): Maximum height of the spiral in cm
        turns (int): Number of spiral turns
        points_per_turn (int): Number of waypoints per turn
        
    Returns:
        MissionPlanner: Configured mission planner
    """
    planner = MissionPlanner(take_photos=True)
    
    # Calculate points on the spiral
    total_points = points_per_turn * turns
    height_step = height / total_points
    
    for i in range(total_points + 1):
        # Calculate angle and radius for this point
        angle = (i * 2 * math.pi) / points_per_turn
        current_radius = radius * (i / total_points)
        
        # Calculate cartesian coordinates
        x = current_radius * math.cos(angle)
        y = current_radius * math.sin(angle)
        z = i * height_step
        
        # Calculate heading (tangent to the spiral)
        heading = (math.degrees(angle) + 90) % 360
        
        # Add waypoint
        planner.add_waypoint(
            x=int(x), 
            y=int(y), 
            z=int(z), 
            heading=int(heading),
            take_photo=True
        )
    
    return planner

def main():
    """Run a demonstration mission"""
    # Uncomment one of these example missions
    
    # Example 1: Square mission at fixed height
    mission = MissionPlanner(take_photos=True)
    side_length = 80
    height = 100
    
    # Add waypoints to form a square
    mission.add_waypoint(0, 0, height, heading=0, take_photo=True)
    mission.add_waypoint(side_length, 0, height, heading=90, take_photo=True)
    mission.add_waypoint(side_length, side_length, height, heading=180, take_photo=True)
    mission.add_waypoint(0, side_length, height, heading=270, take_photo=True)
    mission.add_waypoint(0, 0, height, heading=0, take_photo=True)
    
    # Execute the mission
    mission.execute_mission(min_battery=30)
    mission.disconnect_drone()
    
    # Example 2: Spiral mission
    # spiral_mission = create_spiral_mission(radius=100, height=150, turns=2)
    # spiral_mission.execute_mission(min_battery=50)
    # spiral_mission.disconnect_drone()

if __name__ == "__main__":
    main() 