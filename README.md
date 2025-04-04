# DJI Tello Drone Programming

A comprehensive Python-based programming platform for the DJI Tello drone, covering basic flight, autonomous missions, photography, and 3D modeling.

## Project Structure

```
tello-programming/
├── .gitignore           # Ignore venv, pycache, etc.
├── requirements.txt     # List all dependencies
├── README.md            # Project documentation
├── basic/
│   ├── connection.py    # Basic connection test
│   └── simple_flight.py # Simple flight commands
├── photography/
│   ├── photo_capture.py # Single photo capture
│   └── video_stream.py  # Video streaming
├── autonomous/
│   ├── square_flight.py # Fly in a square pattern
│   └── mission.py       # Complex mission planning
└── photogrammetry/
    ├── grid_flight.py   # Grid pattern for photos
    └── process_images.py # Helper for 3D processing
```

## Setup Instructions

1. Create a virtual environment:
   ```
   python -m venv venv
   ```

2. Activate the virtual environment:
   ```
   # On Windows:
   .\venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Connect to Tello's Wi-Fi network (typically named "TELLO-XXXXXX")

5. Run the basic connection test:
   ```
   python basic/connection.py
   ```

## Features

- **Basic Controls**: Connect to drone, check battery, execute simple flight patterns
- **Photography**: Capture photos, access video stream
- **Autonomous Flights**: Pre-programmed flight patterns, mission planning
- **Photogrammetry**: Structured flight paths for capturing images for 3D modeling

## Safety Guidelines

- Always maintain visual line of sight with your drone
- Check battery levels before flying
- Fly in an open area away from people and obstacles
- Respect local drone regulations
- Test new code in a safe, controlled environment

## License

MIT 