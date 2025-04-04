# DJI Tello Drone Control with Simulator Support

A comprehensive Python codebase for controlling DJI Tello drones, with support for both real hardware and the DroneBlocks Tello Simulator.

## Features

- Basic flight controls (takeoff, landing, movement, rotation)
- Photo and video capture
- Autonomous flight patterns
- Photogrammetry capabilities (grid and orbital flight patterns)
- Simulator support for testing without a physical drone
- Abstraction layer that works with both real drone and simulator

## Project Structure

```
.
├── basic/                  # Basic drone operations
│   ├── connection.py       # Simple connection test
│   └── simple_flight.py    # Basic flight control
├── config/                 # Configuration files
│   └── config.json         # Main config (simulator & drone settings)
├── missions/               # Mission controllers
│   ├── base_controller.py  # Base mission controller
│   ├── tello_wrapper.py    # Tello wrapper (for simulator and real drone)
│   ├── simulator/          # Simulator-specific missions
│   │   ├── grid_flight_sim.py  # Grid flight pattern for simulator
│   │   └── square_flight_sim.py # Square flight pattern for simulator
│   └── real_drone/         # Real drone-specific missions
├── photography/            # Photography capabilities
│   ├── photo_capture.py    # Photo capture functions
│   └── video_stream.py     # Video streaming functions
├── photogrammetry/         # 3D photogrammetry capabilities
│   ├── grid_flight.py      # Grid flight pattern
│   └── process_images.py   # Process captured images
├── scripts/                # Utility scripts
│   └── launch_simulator.py # Launch Chrome for simulator
├── tests/                  # Test cases
│   └── integration/        # Integration tests
├── autonomous/             # Autonomous flight
│   ├── mission.py          # Mission controller
│   └── square_flight.py    # Square flight pattern
├── requirements.txt        # Python dependencies
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
git clone https://github.com/yourusername/tello-drone-control.git
cd tello-drone-control
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure settings:
```bash
# Edit config/config.json if needed
```

## Using the Simulator

The codebase supports both real Tello drones and the DroneBlocks Tello Simulator, allowing you to test your code without physical hardware.

### Simulator Setup

1. Launch the simulator in Chrome:
```bash
python scripts/launch_simulator.py
```

2. This will open Chrome with the appropriate settings for the simulator.

3. In the simulator web interface:
   - Click on "Simulator" at the top
   - Select "Tello" from the dropdown menu
   - The simulator is ready when you see the virtual drone

### Running Simulator Missions

To run a mission with the simulator:

```bash
# Enable simulator mode in config/config.json:
# Set "simulator": { "enabled": true }

# Run a grid flight mission
python missions/simulator/grid_flight_sim.py

# Run a square flight mission
python missions/simulator/square_flight_sim.py
```

## Working with Real Drones

To use with a real Tello drone:

1. Connect to the Tello's Wi-Fi network with your computer

2. Disable simulator mode in the config:
```bash
# Edit config/config.json
# Set "simulator": { "enabled": false }
```

3. Run your desired mission:
```bash
# Basic connection test
python basic/connection.py

# Simple flight
python basic/simple_flight.py

# Photo capture
python photography/photo_capture.py

# Photogrammetry grid flight
python photogrammetry/grid_flight.py
```

## Development

### Adding New Flight Patterns

1. Create a new file in either `missions/simulator/` or `missions/real_drone/`
2. Inherit from `DroneController` and implement your flight pattern
3. Override the `execute_mission()` method with your custom flight logic

Example:
```python
from missions.base_controller import DroneController

class MyCustomMission(DroneController):
    def __init__(self, param1=10, param2=20, config_path=None):
        super().__init__(config_path)
        self.param1 = param1
        self.param2 = param2
        
    def execute_mission(self):
        try:
            # Your flight logic here
            self.takeoff()
            # ... more code ...
            self.land()
            return True
        except Exception as e:
            print(f"Mission error: {e}")
            self.emergency_land()
            return False
```

## License

MIT

## Contributions

Contributions are welcome! Please feel free to submit a Pull Request. 