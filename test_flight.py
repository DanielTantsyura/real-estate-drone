#!/usr/bin/env python3
"""
Test script to run a simulated drone flight
"""

import sys
import os
from pathlib import Path

# Add the project root directory to Python path
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

from missions.simulator.square_flight_sim import SquareFlightMission

def main():
    """Run a simulated square flight mission"""
    print("Starting simulated square flight mission...")
    mission = SquareFlightMission(side_length=80, height=100)
    
    # Check if simulator mode is enabled
    if not mission.simulator_mode:
        print("ERROR: Simulator mode is not enabled in config/config.json")
        print("Please set simulator.enabled to true")
        return 1
    
    # Execute the mission
    try:
        result = mission.execute_mission()
        if result:
            print("Mission completed successfully!")
        else:
            print("Mission failed.")
        
        # Always disconnect
        mission.disconnect()
        
        return 0 if result else 1
    except KeyboardInterrupt:
        print("\nMission interrupted by user")
        mission.emergency_land()
        mission.disconnect()
        return 2
    except Exception as e:
        print(f"Error during mission: {e}")
        mission.emergency_land()
        mission.disconnect()
        return 3

if __name__ == "__main__":
    sys.exit(main()) 