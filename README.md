# DJI Tello Drone Control with Simulator Support

A comprehensive Python codebase for controlling DJI Tello drones, with support for both real hardware and the DroneBlocks Tello Simulator.

## Features

- Basic flight controls (takeoff, landing, movement, rotation)
- Photo and video capture
- Autonomous flight patterns including:
  - Square flight pattern
  - Grid flight pattern (for mapping/photogrammetry)
  - Spiral/orbital flight patterns
  - Customizable waypoint missions
- Photogrammetry capabilities
- Simulator support for testing without a physical drone
- Abstraction layer that works with both real drone and simulator

## Project Structure

```
.
├── config/                 # Configuration files
│   └── config.json         # Main config (simulator & drone settings)
├── missions/               # Mission controllers
│   ├── base_controller.py  # Base mission controller
│   ├── square_flight_sim.py # Square flight pattern for simulator
│   ├── grid_flight_sim.py  # Grid flight pattern for simulator
│   ├── waypoint_sim.py     # Waypoint-based missions
│   ├── photo_capture_sim.py # Photo capture for simulator
│   ├── video_stream_sim.py  # Video streaming for simulator
│   └── video_test.py       # Video testing utility
├── photos/                 # Stored photos
│   └── missions/           # Photos taken during missions
├── tello_wrapper.py        # Tello wrapper (for simulator and real drone)
├── run_simulator.py        # Main script for testing flight patterns
└── README.md               # This file
```

## Setup Instructions

### Prerequisites

- Python 3.6 or higher
- DJI Tello drone (for real hardware testing)
- Google Chrome browser (for simulator)

### Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/real-estate-drone.git
cd real-estate-drone
```

2. Create a virtual environment:
```bash
python -m venv sim_env
source sim_env/bin/activate  # On Windows: sim_env\Scripts\activate
```

3. Install dependencies:
```bash
pip install djitellopy DroneBlocksTelloSimulator
```

## Using the Simulator

The codebase supports both real Tello drones and the DroneBlocks Tello Simulator, allowing you to test your code without physical hardware.

### Simulator Setup

1. Open the DroneBlocks Tello Simulator in Chrome:
   - Go to https://coding-sim.droneblocks.io/
   - Enter your simulator key (found in `config/config.json`)
   - Ensure the simulator is ready (you should see the virtual drone)

### Running Simulator Missions

The `run_simulator.py` script provides a unified way to test different flight patterns:

```bash
# Run a square flight pattern
python run_simulator.py --pattern square

# Run a grid flight mission with parameters
python run_simulator.py --pattern grid --grid-size 3 --grid-spacing 50 --overlap 0.7

# Run an orbital flight mission
python run_simulator.py --pattern orbital --radius 100 --points 8
```

### Available Flight Patterns

#### Square Flight
```
python run_simulator.py --pattern square
```

Parameters:
- `--side-length`: Length of each side of the square in cm (default: 80)
- `--height`: Flight height in cm (default: 100)

#### Grid Flight (for mapping/photogrammetry)
```
python run_simulator.py --pattern grid --grid-size 3 --grid-spacing 50 --overlap 0.7
```

Parameters:
- `--grid-size`: Size of the grid (N x N points)
- `--grid-spacing`: Spacing between grid points in cm
- `--overlap`: Photo overlap (0.0-1.0)
- `--height`: Flight height in cm

#### Orbital Flight (for capturing an object from different angles)
```
python run_simulator.py --pattern orbital --radius 100 --points 8
```

Parameters:
- `--radius`: Radius of the orbital pattern in cm
- `--points`: Number of photos to take around the orbit
- `--height`: Flight height in cm

### Advanced Waypoint Missions

For more complex flight paths, you can use the waypoint mission planner:

```bash
python missions/waypoint_sim.py
```

This will prompt you to choose between:
1. Square Pattern - A simple square flight pattern
2. Spiral Pattern - A rising spiral pattern that creates a helical flight path

The waypoint mission system allows for:
- Precise control over drone position (x, y, z coordinates)
- Control over drone heading at each waypoint
- Automatic photo capture at waypoints
- Custom actions at waypoints

## Working with Real Drones

To use with a real Tello drone:

1. Connect to the Tello's Wi-Fi network with your computer

2. Disable simulator mode in your mission scripts

3. Run your desired mission as you would for the simulator

## Development

### Adding New Flight Patterns

1. Create a new file in the `missions/` directory
2. Inherit from `TelloWrapper` and implement your flight pattern
3. Add command-line options to `run_simulator.py` if you want to make it available through the unified interface

Example for a custom waypoint mission:
```python
from tello_wrapper import TelloWrapper

class MyCustomMission:
    def __init__(self, custom_param=10):
        self.drone = TelloWrapper()
        self.custom_param = custom_param
        
    def execute_mission(self):
        try:
            # Your flight logic here
            self.drone.connect()
            self.drone.takeoff()
            # ... more code ...
            self.drone.land()
            return True
        except Exception as e:
            print(f"Mission error: {e}")
            self.drone.land()
            return False

if __name__ == "__main__":
    mission = MyCustomMission()
    mission.execute_mission()
```

## Transitioning to Real Hardware

The same code can be used with real hardware by changing the `enabled` setting in the simulator section of the config file:

```json
"simulator": {
    "enabled": false
}
```

## License

MIT

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request. 