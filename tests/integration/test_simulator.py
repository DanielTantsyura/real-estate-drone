#!/usr/bin/env python3
"""
Integration test for the DroneBlocks Tello Simulator setup
"""

import os
import sys
import time
import unittest
from pathlib import Path

# Add parent directory to sys.path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from missions.tello_wrapper import TelloWrapper
from missions.base_controller import DroneController
from missions.simulator.square_flight_sim import SquareFlightMission

class SimulatorIntegrationTest(unittest.TestCase):
    """Test case for the simulator integration"""
    
    def setUp(self):
        """Set up the test case"""
        # Force simulator mode for testing
        self.tello = TelloWrapper(use_simulator=True)
        
        # Check if simulator is available
        if not self.tello.simulator_mode:
            self.skipTest("Simulator not available - skipping tests")
    
    def tearDown(self):
        """Clean up after test"""
        if hasattr(self, 'tello') and self.tello:
            self.tello.disconnect()
    
    def test_simulator_connection(self):
        """Test basic connection to simulator"""
        self.assertTrue(self.tello.connect())
        print("Simulator connection successful")
    
    def test_basic_commands(self):
        """Test basic commands in simulator"""
        self.tello.connect()
        
        # Takeoff
        self.assertTrue(self.tello.takeoff())
        print("Takeoff successful")
        time.sleep(2)
        
        # Move forward
        print("Moving forward")
        self.tello.move_forward(30)
        time.sleep(2)
        
        # Rotate
        print("Rotating clockwise")
        self.tello.rotate_clockwise(90)
        time.sleep(2)
        
        # Land
        self.assertTrue(self.tello.land())
        print("Landing successful")
    
    def test_base_controller(self):
        """Test the base controller with the simulator"""
        controller = DroneController()
        
        # Verify simulator mode
        self.assertTrue(controller.simulator_mode)
        
        # Connect and basic operations
        self.assertTrue(controller.connect())
        self.assertTrue(controller.takeoff())
        time.sleep(2)
        controller.land()
        controller.disconnect()
        print("Base controller test successful")
    
    def test_square_flight_mission(self):
        """Test the square flight mission with the simulator"""
        mission = SquareFlightMission(side_length=50, height=50)
        
        # Verify simulator mode
        self.assertTrue(mission.simulator_mode)
        
        # Execute mission
        result = mission.execute_mission()
        self.assertTrue(result)
        print("Square flight mission test successful")


def main():
    """Main function"""
    print("\n====== DroneBlocks Tello Simulator Integration Test ======")
    print("This test verifies that the simulator setup is working correctly.")
    print("Make sure the simulator is running in Chrome before proceeding.\n")
    
    if input("Is the simulator running? (y/n): ").lower() != 'y':
        print("Please run the simulator first with: python scripts/launch_simulator.py")
        return 1
    
    # Run tests
    unittest.main(argv=['first-arg-is-ignored'], exit=False)
    return 0

if __name__ == "__main__":
    sys.exit(main()) 