#!/usr/bin/env python3
"""
Simulator implementation of grid flight pattern for DJI Tello drone.
This script executes a grid flight pattern with simulated photo capture at regular intervals,
optimized for 3D modeling/photogrammetry simulation.
"""
from missions.base_controller import DroneController
import time
import os
import math

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
                            self.drone.fly_forward(x, "cm") if self.simulator_mode else self.drone.move_forward(x)
                            time.sleep(1)
                        if y > 0:
                            print(f"Moving right {y}cm...")
                            self.drone.fly_right(y, "cm") if self.simulator_mode else self.drone.move_right(y)
                            time.sleep(1)
                    # If starting a new row, just move sideways to the beginning/end of the row
                    elif col == (0 if not reverse_direction else self.grid_size-1):
                        print(f"Moving to next row...")
                        self.drone.fly_right(self.grid_spacing, "cm") if self.simulator_mode else self.drone.move_right(self.grid_spacing)
                        time.sleep(1)
                    # Otherwise move forward/backward along the row
                    else:
                        step = self.grid_spacing * (-1 if reverse_direction else 1)
                        print(f"Moving {abs(step)}cm {'backward' if step < 0 else 'forward'}...")
                        if step > 0:
                            self.drone.fly_forward(step, "cm") if self.simulator_mode else self.drone.move_forward(step)
                        else:
                            self.drone.fly_backward(abs(step), "cm") if self.simulator_mode else self.drone.move_back(abs(step))
                        time.sleep(1)
                    
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
                                        self.drone.fly_forward(micro_step, "cm") if self.simulator_mode else self.drone.move_forward(micro_step)
                                        time.sleep(0.5)
                                    if j > 0:
                                        print(f"Micro-step right: {micro_step}cm")
                                        self.drone.fly_right(micro_step, "cm") if self.simulator_mode else self.drone.move_right(micro_step)
                                        time.sleep(0.5)
                                        
                                # Capture the photo
                                sub_x = x + (i * self.photo_spacing)
                                sub_y = y + (j * self.photo_spacing)
                                self._capture_grid_photo(row+1, col+1, (sub_x, sub_y))
                                
                        # Return to grid intersection for next move
                        if self.photos_per_cell > 1:
                            self.drone.fly_backward((self.photos_per_cell-1) * self.photo_spacing, "cm") if self.simulator_mode else self.drone.move_back((self.photos_per_cell-1) * self.photo_spacing)
                            time.sleep(0.5)
                            self.drone.fly_left((self.photos_per_cell-1) * self.photo_spacing, "cm") if self.simulator_mode else self.drone.move_left((self.photos_per_cell-1) * self.photo_spacing)
                            time.sleep(0.5)
            
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
                self.drone.fly_backward(current_x, "cm") if self.simulator_mode else self.drone.move_back(current_x)
                time.sleep(2)
            
            if current_y > 0:
                print(f"Moving left {current_y}cm...")
                self.drone.fly_left(current_y, "cm") if self.simulator_mode else self.drone.move_left(current_y)
                time.sleep(2)
            
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
            self.drone.fly_forward(self.radius, "cm") if self.simulator_mode else self.drone.move_forward(self.radius)
            time.sleep(2)
            
            # Execute the orbital pattern
            print("\nStarting orbital flight pattern...")
            
            angle_step = 360 / self.points
            
            # Take first photo facing the center
            self.drone.yaw_right(180) if self.simulator_mode else self.drone.rotate_clockwise(180)  # Face the center
            time.sleep(2)
            print("Taking first orbital photo (facing center)...")
            self._capture_orbital_photo(0)
            
            # Orbit around the subject
            for i in range(1, self.points):
                angle = i * angle_step
                
                # Calculate rotation to maintain facing the center
                print(f"Rotating to orbital position {i+1}/{self.points} ({angle:.0f}°)...")
                
                # Move along the orbit (small clockwise steps)
                self.drone.yaw_left(90) if self.simulator_mode else self.drone.rotate_counter_clockwise(90)  # Face tangent to the circle
                time.sleep(1)
                
                # Calculate arc distance to move
                arc_distance = 2 * math.pi * self.radius * (angle_step / 360)
                print(f"Moving along orbital arc: {arc_distance:.0f}cm...")
                self.drone.fly_forward(int(arc_distance), "cm") if self.simulator_mode else self.drone.move_forward(int(arc_distance))
                time.sleep(2)
                
                # Rotate to face the center again
                self.drone.yaw_right(90) if self.simulator_mode else self.drone.rotate_clockwise(90)  # Face center
                time.sleep(1)
                
                # Take photo
                print(f"Taking orbital photo at {angle:.0f}°...")
                self._capture_orbital_photo(angle)
            
            print("\nOrbital pattern completed!")
            print(f"Total photos simulated: {self.photo_count}")
            
            # Return to starting position
            print("Returning to starting position...")
            
            # Move backward to return to center
            print(f"Moving back to center...")
            self.drone.yaw_left(180) if self.simulator_mode else self.drone.rotate_counter_clockwise(180)  # Face away from center
            time.sleep(1)
            self.drone.fly_forward(self.radius, "cm") if self.simulator_mode else self.drone.move_forward(self.radius)  # Move back to center
            time.sleep(2)
            
            # Land
            self.land()
            
            return True
            
        except Exception as e:
            print(f"Error during orbital flight mission: {e}")
            self.emergency_land()
            return False
    
    def _capture_orbital_photo(self, angle):
        """
        Capture a photo at an orbital position
        
        Args:
            angle (float): Angle in degrees
        """
        try:
            if self.simulator_mode:
                # Simulated photo capture
                print(f"[SIMULATOR] Photo captured at angle {angle:.0f}°")
                self.photo_count += 1
            else:
                # Real photo capture
                timestamp = int(time.time())
                filename = f"orbital_{angle:.0f}_{timestamp}.jpg"
                self.take_photo(filename, self.config['tello']['orbital_photo_dir'])
                self.photo_count += 1
        except Exception as e:
            print(f"Error capturing orbital photo at {angle:.0f}°: {e}")


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