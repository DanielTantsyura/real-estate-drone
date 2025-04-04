#!/usr/bin/env python3
"""
Grid flight pattern for photogrammetry with DJI Tello drone.
This script executes a grid flight pattern with photo capture at regular intervals,
optimized for 3D modeling/photogrammetry applications.
"""
from djitellopy import Tello
import cv2
import time
import os
import math

def grid_flight(grid_size=3, grid_spacing=50, height=100, overlap=0.8, save_dir="photos/grid"):
    """
    Execute a grid flight pattern optimized for photogrammetry
    
    Args:
        grid_size (int): Size of the grid (grid_size x grid_size points)
        grid_spacing (int): Spacing between grid points in cm
        height (int): Flight height in cm
        overlap (float): Target image overlap (0.0-1.0), higher is better for photogrammetry
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
        
        # Check battery level before flying
        battery = tello.get_battery()
        print(f"Battery level: {battery}%")
        
        if battery <= 30:  # Higher threshold for photogrammetry mission
            print("Battery too low for safe photogrammetry mission")
            return
            
        # Start video stream
        print("Starting video stream...")
        tello.streamon()
        stream_started = True
        frame_read = tello.get_frame_read()
        time.sleep(2)  # Camera warm-up
        
        # Initialize photo counter
        photo_count = 0
        
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
        
        # Calculate photo spacing based on overlap
        photo_spacing = int(grid_spacing * (1 - overlap))
        if photo_spacing < 10:  # Minimum distance between photos
            photo_spacing = 10
            
        # Number of photos to take within each grid cell
        photos_per_cell = max(1, int(grid_spacing / photo_spacing))
        
        print(f"Grid size: {grid_size}x{grid_size}")
        print(f"Grid spacing: {grid_spacing}cm")
        print(f"Target overlap: {overlap*100:.0f}%")
        print(f"Photo spacing: {photo_spacing}cm")
        print(f"Photos per grid cell: {photos_per_cell}")
        
        # Function to capture photo
        def capture_photo(row, col, position=None):
            nonlocal photo_count
            try:
                img = frame_read.frame
                timestamp = int(time.time())
                
                # Add position info to filename if provided
                pos_info = ""
                if position:
                    pos_info = f"_x{position[0]}_y{position[1]}"
                    
                filename = f"{save_dir}/grid_r{row}_c{col}{pos_info}_{timestamp}.jpg"
                cv2.imwrite(filename, img)
                photo_count += 1
                print(f"Photo {photo_count} captured at position ({row}, {col}){pos_info}")
                
                # Show a small preview
                small_img = cv2.resize(img, (640, 480))
                cv2.imshow("Grid Photo", small_img)
                cv2.waitKey(100)  # Show briefly
            except Exception as e:
                print(f"Error capturing photo: {e}")
        
        # Execute the grid pattern
        print("\nStarting grid flight pattern...")
        
        # Traditional boustrophedon (back and forth) pattern
        for row in range(grid_size):
            print(f"\nRow {row+1}/{grid_size}")
            
            # Determine direction (alternate directions for each row)
            reverse_direction = (row % 2 == 1)
            col_range = range(grid_size-1, -1, -1) if reverse_direction else range(grid_size)
            
            for col in col_range:
                print(f"Moving to grid position ({row+1}, {col+1})")
                
                # Calculate actual position in cm
                x = col * grid_spacing
                y = row * grid_spacing
                
                # If first position, move directly there
                if row == 0 and col == 0:
                    print(f"Moving to first grid position...")
                    tello.move_forward(x)
                    time.sleep(1)
                    tello.move_right(y)
                    time.sleep(1)
                # If starting a new row, just move sideways to the beginning/end of the row
                elif col == (0 if not reverse_direction else grid_size-1):
                    print(f"Moving to next row...")
                    tello.move_right(grid_spacing)
                    time.sleep(1)
                # Otherwise move forward/backward along the row
                else:
                    step = grid_spacing * (-1 if reverse_direction else 1)
                    print(f"Moving {abs(step)}cm {'backward' if step < 0 else 'forward'}...")
                    if step > 0:
                        tello.move_forward(step)
                    else:
                        tello.move_back(abs(step))
                    time.sleep(1)
                
                # Take photos along each grid cell
                if photos_per_cell == 1:
                    # Just take one photo at the grid intersection
                    capture_photo(row+1, col+1, (x, y))
                else:
                    # Take multiple photos within the grid cell for higher overlap
                    for i in range(photos_per_cell):
                        for j in range(photos_per_cell):
                            # Only move if not at the first photo position
                            if i > 0 or j > 0:
                                # Calculate micro-movements within the cell
                                micro_step = photo_spacing
                                
                                # Move in micro-steps
                                if i > 0:
                                    print(f"Micro-step forward: {micro_step}cm")
                                    tello.move_forward(micro_step)
                                    time.sleep(0.5)
                                if j > 0:
                                    print(f"Micro-step right: {micro_step}cm")
                                    tello.move_right(micro_step)
                                    time.sleep(0.5)
                                    
                            # Capture the photo
                            sub_x = x + (i * photo_spacing)
                            sub_y = y + (j * photo_spacing)
                            capture_photo(row+1, col+1, (sub_x, sub_y))
                            
                    # Return to grid intersection for next move
                    if photos_per_cell > 1:
                        tello.move_back((photos_per_cell-1) * photo_spacing)
                        time.sleep(0.5)
                        tello.move_left((photos_per_cell-1) * photo_spacing)
                        time.sleep(0.5)
        
        print("\nGrid pattern completed!")
        print(f"Total photos captured: {photo_count}")
        
        # Return to starting position
        print("Returning to starting position...")
        
        # Calculate current position
        current_x = (grid_size-1) * grid_spacing if (grid_size % 2 == 0) else 0
        current_y = (grid_size-1) * grid_spacing
        
        # Return to home (0,0)
        if current_x > 0:
            print(f"Moving back {current_x}cm...")
            tello.move_back(current_x)
            time.sleep(2)
        
        if current_y > 0:
            print(f"Moving left {current_y}cm...")
            tello.move_left(current_y)
            time.sleep(2)
        
        # Land
        print("Landing...")
        tello.land()
        print("Landed successfully")
        
    except Exception as e:
        print(f"Error during grid flight: {e}")
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

def orbital_flight(center_height=100, radius=80, points=8, save_dir="photos/orbital"):
    """
    Execute an orbital flight pattern around a subject for photogrammetry
    
    Args:
        center_height (int): Height to orbit at in cm
        radius (int): Radius of the orbit in cm
        points (int): Number of points to capture around the orbit
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
        
        # Check battery level before flying
        battery = tello.get_battery()
        print(f"Battery level: {battery}%")
        
        if battery <= 30:
            print("Battery too low for safe orbital flight")
            return
            
        # Start video stream
        print("Starting video stream...")
        tello.streamon()
        stream_started = True
        frame_read = tello.get_frame_read()
        time.sleep(2)  # Camera warm-up
        
        # Take off and reach desired height
        print("Taking off...")
        tello.takeoff()
        time.sleep(3)  # Stabilize after takeoff
        
        # Adjust to desired height
        current_height = tello.get_height()
        if current_height < center_height:
            print(f"Adjusting height to {center_height}cm...")
            tello.move_up(center_height - current_height)
            time.sleep(2)
        
        # Move forward to the orbital radius
        print(f"Moving forward to orbital position (radius: {radius}cm)...")
        tello.move_forward(radius)
        time.sleep(2)
        
        # Execute the orbital pattern
        print("\nStarting orbital flight pattern...")
        
        angle_step = 360 / points
        photo_count = 0
        
        # Function to capture photo
        def capture_orbital_photo(angle):
            nonlocal photo_count
            try:
                img = frame_read.frame
                timestamp = int(time.time())
                filename = f"{save_dir}/orbital_{angle:.0f}_{timestamp}.jpg"
                cv2.imwrite(filename, img)
                photo_count += 1
                print(f"Photo {photo_count} captured at angle {angle:.0f}°")
                
                # Show a small preview
                small_img = cv2.resize(img, (640, 480))
                cv2.imshow("Orbital Photo", small_img)
                cv2.waitKey(100)  # Show briefly
            except Exception as e:
                print(f"Error capturing orbital photo: {e}")
        
        # Take first photo facing the center
        tello.rotate_clockwise(180)  # Face the center
        time.sleep(2)
        print("Taking first orbital photo (facing center)...")
        capture_orbital_photo(0)
        
        # Orbit around the subject
        for i in range(1, points):
            angle = i * angle_step
            
            # Calculate rotation to maintain facing the center
            print(f"Rotating to orbital position {i+1}/{points} ({angle:.0f}°)...")
            
            # Move along the orbit (small clockwise steps)
            tello.rotate_counter_clockwise(90)  # Face tangent to the circle
            time.sleep(1)
            
            # Calculate arc distance to move
            arc_distance = 2 * math.pi * radius * (angle_step / 360)
            print(f"Moving along orbital arc: {arc_distance:.0f}cm...")
            tello.move_forward(int(arc_distance))
            time.sleep(2)
            
            # Rotate to face the center again
            tello.rotate_clockwise(90)  # Face center
            time.sleep(1)
            
            # Take photo
            print(f"Taking orbital photo at {angle:.0f}°...")
            capture_orbital_photo(angle)
        
        print("\nOrbital pattern completed!")
        print(f"Total photos captured: {photo_count}")
        
        # Return to starting position
        print("Returning to starting position...")
        
        # Move backward to return to center
        print(f"Moving back to center...")
        tello.rotate_counter_clockwise(180)  # Face away from center
        time.sleep(1)
        tello.move_forward(radius)  # Move back to center
        time.sleep(2)
        
        # Land
        print("Landing...")
        tello.land()
        print("Landed successfully")
        
    except Exception as e:
        print(f"Error during orbital flight: {e}")
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

if __name__ == "__main__":
    # Choose which flight pattern to execute
    print("Select a flight pattern:")
    print("1. Grid Pattern (for mapping/terrain)")
    print("2. Orbital Pattern (for single object)")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        grid_size = int(input("Grid size (default 3): ") or "3")
        grid_spacing = int(input("Grid spacing in cm (default 50): ") or "50")
        height = int(input("Flight height in cm (default 100): ") or "100")
        grid_flight(grid_size=grid_size, grid_spacing=grid_spacing, height=height)
    elif choice == "2":
        radius = int(input("Orbit radius in cm (default 80): ") or "80")
        points = int(input("Number of photos around orbit (default 8): ") or "8")
        height = int(input("Flight height in cm (default 100): ") or "100")
        orbital_flight(center_height=height, radius=radius, points=points)
    else:
        print("Invalid choice. Exiting.")