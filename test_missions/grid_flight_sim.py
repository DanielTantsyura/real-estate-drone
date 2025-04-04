#!/usr/bin/env python3
"""
Simulator implementation of grid flight pattern for DJI Tello drone.
This script executes a grid flight pattern with simulated photo capture at regular intervals,
optimized for 3D modeling/photogrammetry simulation.
"""
from base_controller import DroneController
import time
import os
import math
from tello_wrapper import fast_sleep

class GridFlightMission(DroneController):
    """Grid flight mission controller for simulator"""
    
    def __init__(self, grid_size=3, grid_spacing=50, height=100, overlap=0.8, config_path=None):
        """
        Initialize the grid flight mission
        
        Args:
            grid_size (int): Size of the grid (grid_size x grid_size points)
            grid_spacing (int): Spacing between grid points in cm
            height (int): Flight height in cm
            overlap (float): Target image overlap (0.0-1.0), higher is better for photogrammetry
            config_path (str, optional): Path to the config file
        """
        super().__init__(config_path)
        self.grid_size = grid_size
        self.grid_spacing = grid_spacing
        self.height = height
        self.overlap = overlap
        self.photo_count = 0
        
        # Calculate photo spacing based on overlap
        self.photo_spacing = int(grid_spacing * (1 - overlap))
        if self.photo_spacing < 10:  # Minimum distance between photos
            self.photo_spacing = 10
            
        # Number of photos to take within each grid cell
        self.photos_per_cell = max(1, int(grid_spacing / self.photo_spacing))
        
        # Force simulator mode
        self.simulator_mode = self.config['simulator']['enabled']
        if not self.simulator_mode:
            print("WARNING: This mission is designed for simulator use.")
            print("Please set simulator.enabled to true in your config file.")
    
    def execute_mission(self):
        """Execute the grid flight mission"""
        try:
            print(f"Starting grid flight mission with grid size {self.grid_size}x{self.grid_size}")
            print(f"Grid spacing: {self.grid_spacing}cm")
            print(f"Target overlap: {self.overlap*100:.0f}%")
            print(f"Photo spacing: {self.photo_spacing}cm")
            print(f"Photos per grid cell: {self.photos_per_cell}")
            
            # Take off and reach desired height
            self.takeoff()
            
            # Execute the grid pattern
            print("\nStarting grid flight pattern...")
            
            # Traditional boustrophedon (back and forth) pattern
            for row in range(self.grid_size):
                print(f"\nRow {row+1}/{self.grid_size}")
                
                # Determine direction (alternate directions for each row)
                reverse_direction = (row % 2 == 1)
                col_range = range(self.grid_size-1, -1, -1) if reverse_direction else range(self.grid_size)
                
                for col in col_range:
                    print(f"Moving to grid position ({row+1}, {col+1})")
                    
                    # Calculate actual position in cm
                    x = col * self.grid_spacing
                    y = row * self.grid_spacing
                    
                    # If first position, move directly there
                    if row == 0 and col == 0:
                        print(f"Moving to first grid position...")
                        if x > 0:
                            print(f"Moving forward {x}cm...")
                            self.drone.fly_forward(x, "cm")
                            fast_sleep(0.2)
                        if y > 0:
                            print(f"Moving right {y}cm...")
                            self.drone.fly_right(y, "cm")
                            fast_sleep(0.2)
                    # If starting a new row, just move sideways to the beginning/end of the row
                    elif col == (0 if not reverse_direction else self.grid_size-1):
                        print(f"Moving to next row...")
                        self.drone.fly_right(self.grid_spacing, "cm")
                        fast_sleep(0.2)
                    # Otherwise move forward/backward along the row
                    else:
                        step = self.grid_spacing * (-1 if reverse_direction else 1)
                        print(f"Moving {abs(step)}cm {'backward' if step < 0 else 'forward'}...")
                        if step > 0:
                            self.drone.fly_forward(step, "cm")
                        else:
                            self.drone.fly_backward(abs(step), "cm")
                        fast_sleep(0.2)
                    
                    # Take photos along each grid cell
                    if self.photos_per_cell == 1:
                        # Just take one photo at the grid intersection
                        self._capture_grid_photo(row+1, col+1, (x, y))
                    else:
                        # Take multiple photos within the grid cell for higher overlap
                        for i in range(self.photos_per_cell):
                            for j in range(self.photos_per_cell):
                                # Only move if not at the first photo position
                                if i > 0 or j > 0:
                                    # Calculate micro-movements within the cell
                                    micro_step = self.photo_spacing
                                    
                                    # Move in micro-steps
                                    if i > 0:
                                        print(f"Micro-step forward: {micro_step}cm")
                                        self.drone.fly_forward(micro_step, "cm")
                                        fast_sleep(0.1)
                                    if j > 0:
                                        print(f"Micro-step right: {micro_step}cm")
                                        self.drone.fly_right(micro_step, "cm")
                                        fast_sleep(0.1)
                                        
                                # Capture the photo
                                sub_x = x + (i * self.photo_spacing)
                                sub_y = y + (j * self.photo_spacing)
                                self._capture_grid_photo(row+1, col+1, (sub_x, sub_y))
                                
                        # Return to grid intersection for next move
                        if self.photos_per_cell > 1:
                            self.drone.fly_backward((self.photos_per_cell-1) * self.photo_spacing, "cm")
                            fast_sleep(0.1)
                            self.drone.fly_left((self.photos_per_cell-1) * self.photo_spacing, "cm")
                            fast_sleep(0.1)
            
            print("\nGrid pattern completed!")
            print(f"Total photos simulated: {self.photo_count}")
            
            # Return to starting position
            print("Returning to starting position...")
            
            # Calculate current position
            current_x = (self.grid_size-1) * self.grid_spacing if (self.grid_size % 2 == 0) else 0
            current_y = (self.grid_size-1) * self.grid_spacing
            
            # Return to home (0,0)
            if current_x > 0:
                print(f"Moving back {current_x}cm...")
                self.drone.fly_backward(current_x, "cm")
                fast_sleep(0.5)
            
            if current_y > 0:
                print(f"Moving left {current_y}cm...")
                self.drone.fly_left(current_y, "cm")
                fast_sleep(0.5)
            
            # Land
            self.land()
            
            return True
            
        except Exception as e:
            print(f"Error during grid flight mission: {e}")
            self.emergency_land()
            return False
    
    def _capture_grid_photo(self, row, col, position=None):
        """
        Capture a photo at a grid position
        
        Args:
            row (int): Row number
            col (int): Column number
            position (tuple, optional): (x, y) position in cm
        """
        try:
            # Add position info to filename if provided
            pos_info = ""
            if position:
                pos_info = f"_x{position[0]}_y{position[1]}"
                
            if self.simulator_mode:
                # Simulated photo capture
                print(f"[SIMULATOR] Photo captured at grid position ({row}, {col}){pos_info}")
                self.photo_count += 1
            else:
                # Real photo capture
                timestamp = int(time.time())
                filename = f"grid_r{row}_c{col}{pos_info}_{timestamp}.jpg"
                self.take_photo(filename, self.config['tello']['grid_photo_dir'])
                self.photo_count += 1
        except Exception as e:
            print(f"Error capturing photo at grid position ({row}, {col}): {e}")


class OrbitalFlightMission(DroneController):
    """Orbital flight mission controller for simulator"""
    
    def __init__(self, center_height=100, radius=80, points=8, config_path=None):
        """
        Initialize the orbital flight mission
        
        Args:
            center_height (int): Height to orbit at in cm
            radius (int): Radius of the orbit in cm
            points (int): Number of points to capture around the orbit
            config_path (str, optional): Path to the config file
        """
        super().__init__(config_path)
        self.center_height = center_height
        self.radius = radius
        self.points = points
        self.photo_count = 0
        
        # Force simulator mode
        self.simulator_mode = self.config['simulator']['enabled']
        if not self.simulator_mode:
            print("WARNING: This mission is designed for simulator use.")
            print("Please set simulator.enabled to true in your config file.")
    
    def execute_mission(self):
        """Execute the orbital flight mission"""
        try:
            print(f"Starting orbital flight mission with radius {self.radius}cm at height {self.center_height}cm")
            print(f"Points around orbit: {self.points}")
            
            # Take off and reach desired height
            self.takeoff()
            
            # Move forward to the orbital radius
            print(f"Moving forward to orbital position (radius: {self.radius}cm)...")
            self.drone.fly_forward(self.radius, "cm")
            fast_sleep(0.5)
            
            # Execute the orbital pattern
            print("\nStarting orbital flight pattern...")
            
            angle_step = 360 / self.points
            
            # Take first photo facing the center
            self.drone.yaw_right(180)  # Face the center
            fast_sleep(0.5)
            print("Taking first orbital photo (facing center)...")
            self._capture_orbital_photo(0)
            
            # Orbit around the subject
            for i in range(1, self.points):
                angle = i * angle_step
                print(f"\nMoving to orbital position {i+1}/{self.points} (angle: {angle:.1f}°)")
                
                # Calculate the movement (we need to move in a circle)
                # We're already at the radius, so we need to move in an arc
                
                # For simplicity, we'll use a yaw-move-yaw approach
                # First, yaw to face tangent to the circle
                self.drone.yaw_right(90)
                fast_sleep(0.3)
                
                # Calculate chord length (straight-line distance between points on circle)
                chord_length = 2 * self.radius * math.sin(math.radians(angle_step/2))
                
                # Move along the chord
                print(f"Moving {chord_length:.1f}cm along chord...")
                self.drone.fly_forward(int(chord_length), "cm")
                fast_sleep(0.5)
                
                # Yaw to face center again
                self.drone.yaw_right(90)
                fast_sleep(0.3)
                
                # Take photo facing center
                print(f"Taking orbital photo at position {i+1}...")
                self._capture_orbital_photo(i)
            
            print("\nOrbital pattern completed!")
            print(f"Total photos simulated: {self.photo_count}")
            
            # Return to home position
            print("Returning to home position...")
            
            # Yaw to face away from center
            self.drone.yaw_right(180)
            fast_sleep(0.3)
            
            # Move back to origin
            self.drone.fly_forward(self.radius, "cm")
            fast_sleep(0.5)
            
            # Land
            self.land()
            
            return True
            
        except Exception as e:
            print(f"Error during orbital flight mission: {e}")
            self.emergency_land()
            return False
    
    def _capture_orbital_photo(self, position):
        """
        Capture a photo at an orbital position
        
        Args:
            position (int): Position number around the orbit
        """
        try:
            if self.simulator_mode:
                # Simulated photo capture
                print(f"[SIMULATOR] Photo captured at orbital position {position}")
                self.photo_count += 1
            else:
                # Real photo capture
                timestamp = int(time.time())
                angle = (position * 360 / self.points)
                filename = f"orbital_pos{position}_angle{angle:.1f}_{timestamp}.jpg"
                self.take_photo(filename, self.config['tello']['orbital_photo_dir'])
                self.photo_count += 1
        except Exception as e:
            print(f"Error capturing photo at orbital position {position}: {e}")


if __name__ == "__main__":
    # Ask the user which pattern to execute
    print("Select a flight pattern:")
    print("1. Grid Pattern (for mapping/terrain)")
    print("2. Orbital Pattern (for single object)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        grid_size = int(input("Grid size (default 3): ") or "3")
        grid_spacing = int(input("Grid spacing in cm (default 50): ") or "50")
        height = int(input("Flight height in cm (default 100): ") or "100")
        mission = GridFlightMission(grid_size=grid_size, grid_spacing=grid_spacing, height=height)
        mission.execute_mission()
        mission.disconnect()
    elif choice == "2":
        radius = int(input("Orbit radius in cm (default 80): ") or "80")
        points = int(input("Number of photos around orbit (default 8): ") or "8")
        height = int(input("Flight height in cm (default 100): ") or "100")
        mission = OrbitalFlightMission(center_height=height, radius=radius, points=points)
        mission.execute_mission()
        mission.disconnect()
    else:
        print("Invalid choice. Exiting.") 