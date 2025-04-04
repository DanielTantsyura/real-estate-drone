#!/usr/bin/env python3
"""
Run the simulator mission without launching Chrome.
Assumes you already have the simulator website open in your browser.
"""

import sys
import os
import time
import argparse
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from tello_wrapper import TelloWrapper
from missions.simple.grid_flight_sim import GridFlightMission, OrbitalFlightMission
from missions.simple.square_flight_sim import SquareFlightMission

def run_square_flight(side_length=80, height=100):
    """Run a square flight pattern"""
    print(f"\nRunning square flight with side length {side_length}cm at height {height}cm...")
    
    mission = SquareFlightMission(
        side_length=side_length,
        height=height
    )
    
    try:
        result = mission.execute_mission()
        mission.disconnect()
        return result
    except KeyboardInterrupt:
        print("\nMission interrupted by user")
        mission.emergency_land()
        mission.disconnect()
        return False
    except Exception as e:
        print(f"Error during mission: {e}")
        mission.emergency_land()
        mission.disconnect()
        return False

def run_grid_flight(grid_size=2, grid_spacing=50, height=100, overlap=0.5):
    """Run a grid flight pattern"""
    print(f"\nRunning grid flight with size {grid_size}x{grid_size}, spacing {grid_spacing}cm, overlap {overlap*100}%...")
    
    mission = GridFlightMission(
        grid_size=grid_size,
        grid_spacing=grid_spacing,
        height=height,
        overlap=overlap
    )
    
    try:
        result = mission.execute_mission()
        mission.disconnect()
        return result
    except KeyboardInterrupt:
        print("\nMission interrupted by user")
        mission.emergency_land()
        mission.disconnect()
        return False
    except Exception as e:
        print(f"Error during mission: {e}")
        mission.emergency_land()
        mission.disconnect()
        return False

def run_orbital_flight(radius=80, points=6, height=100):
    """Run an orbital flight pattern"""
    print(f"\nRunning orbital flight with radius {radius}cm, {points} points, height {height}cm...")
    
    mission = OrbitalFlightMission(
        center_height=height,
        radius=radius,
        points=points
    )
    
    try:
        result = mission.execute_mission()
        mission.disconnect()
        return result
    except KeyboardInterrupt:
        print("\nMission interrupted by user")
        mission.emergency_land()
        mission.disconnect()
        return False
    except Exception as e:
        print(f"Error during mission: {e}")
        mission.emergency_land()
        mission.disconnect()
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Test flight patterns with the Tello simulator")
    parser.add_argument("--pattern", choices=["square", "grid", "orbital"], default="square",
                      help="Flight pattern to test (default: square)")
    
    # Grid pattern options
    parser.add_argument("--grid-size", type=int, default=2,
                      help="Size of the grid (N x N points) (default: 2)")
    parser.add_argument("--grid-spacing", type=int, default=50,
                      help="Spacing between grid points in cm (default: 50)")
    parser.add_argument("--overlap", type=float, default=0.5,
                      help="Photo overlap for grid pattern (0.0-1.0) (default: 0.5)")
    
    # Orbital pattern options
    parser.add_argument("--radius", type=int, default=80,
                      help="Radius of the orbital pattern in cm (default: 80)")
    parser.add_argument("--points", type=int, default=6,
                      help="Number of points around the orbit (default: 6)")
    
    # Square pattern options
    parser.add_argument("--side-length", type=int, default=80,
                      help="Side length for square pattern in cm (default: 80)")
    
    # Common options
    parser.add_argument("--height", type=int, default=100,
                      help="Flight height in cm (default: 100)")
    parser.add_argument("--fast-mode", action="store_true",
                      help="Run simulation faster with optimized timing")
    
    args = parser.parse_args()
    
    # Apply fast mode by setting the environment variable
    if args.fast_mode:
        print("Running in fast mode - reduced delays for faster simulation")
        os.environ["DRONE_FAST_MODE"] = "1"
    
    if args.pattern == "square":
        # Run square flight mission
        result = run_square_flight(
            side_length=args.side_length,
            height=args.height
        )
        return 0 if result else 1
        
    elif args.pattern == "grid":
        # Run grid flight mission
        result = run_grid_flight(
            grid_size=args.grid_size,
            grid_spacing=args.grid_spacing,
            height=args.height,
            overlap=args.overlap
        )
        return 0 if result else 1
        
    elif args.pattern == "orbital":
        # Run orbital flight mission
        result = run_orbital_flight(
            radius=args.radius,
            points=args.points,
            height=args.height
        )
        return 0 if result else 1
    
    # Should never reach here due to argument choices
    return 1

if __name__ == "__main__":
    sys.exit(main()) 