# VolumiWLED

Python script that connects a Volumio music player with WLED LED controller to create dynamic LED visualizations based on player state.

## Features

- **Progress Bar Effect**: Displays playback progress as a visual LED bar
- **Rotating Vinyl Effect**: Mimics a spinning vinyl record when music is playing
- **State-based Control**: Different LED behaviors for play, pause, and stop states
- **Configurable**: Easy YAML-based configuration
- **Lightweight**: Designed to run on Raspberry Pi 3B

## Requirements

- Python 3.7 or higher
- Volumio music player (local or network accessible)
- WLED-compatible LED controller
- LED strip connected to WLED controller

## Installation

### 1. Clone the repository

```bash
cd /home/volumio
git clone https://github.com/petjek/VolumiWLED.git
cd VolumiWLED
```

### 2. Install Python dependencies

```bash
pip3 install -r requirements.txt
```

### 3. Configure the application

Edit `config.yaml` to match your setup:

```yaml
# Volumio settings
volumio:
  host: "localhost"  # Change if Volumio is on another device
  port: 3000

# WLED settings
wled:
  host: "192.168.1.100"  # Change to your WLED device IP

# LED settings
led:
  count: 60              # Number of LEDs in your strip
  brightness: 128        # Brightness (0-255)

# Effect settings
effects:
  progress_bar:
    enabled: true
    color: [0, 255, 0]   # RGB color for progress bar
    
  vinyl_rotation:
    enabled: true
    color: [255, 0, 255] # RGB color for vinyl effect
    speed: 50            # Rotation speed (lower = faster)

# Update interval in seconds
update_interval: 0.5
```

### 4. Test the application

```bash
python3 volumiwled.py
```

Press Ctrl+C to stop.

## Usage

### Run manually

```bash
python3 volumiwled.py
```

With custom config file:

```bash
python3 volumiwled.py -c /path/to/custom_config.yaml
```

### Run as a service (systemd)

To have VolumiWLED start automatically on boot:

1. Copy the service file:
```bash
sudo cp volumiwled.service /etc/systemd/system/
```

2. Edit the service file if needed (adjust paths and user):
```bash
sudo nano /etc/systemd/system/volumiwled.service
```

3. Enable and start the service:
```bash
sudo systemctl enable volumiwled.service
sudo systemctl start volumiwled.service
```

4. Check status:
```bash
sudo systemctl status volumiwled.service
```

5. View logs:
```bash
sudo journalctl -u volumiwled.service -f
```

## How it Works

VolumiWLED monitors the Volumio player state via its REST API and translates playback information into LED effects:

### Player States

- **Playing**: Shows either progress bar or rotating vinyl effect
  - Progress bar fills from left to right based on track position
  - Vinyl effect creates a rotating pattern that mimics a spinning record
  
- **Paused**: Shows static progress bar at current position, or dims LEDs

- **Stopped**: Turns off all LEDs

### Effect Selection

The application prioritizes the progress bar effect when enabled and track duration is available. Otherwise, it uses the vinyl rotation effect when playing.

## Configuration Options

### Volumio Settings
- `host`: Volumio hostname or IP address
- `port`: Volumio API port (default: 3000)

### WLED Settings
- `host`: WLED device IP address

### LED Settings
- `count`: Total number of LEDs in your strip
- `brightness`: Default brightness level (0-255)

### Effect Settings

#### Progress Bar
- `enabled`: Enable/disable progress bar effect
- `color`: RGB color array [R, G, B] (0-255 each)

#### Vinyl Rotation
- `enabled`: Enable/disable vinyl rotation effect
- `color`: RGB color array [R, G, B] (0-255 each)
- `speed`: Rotation speed in milliseconds (lower = faster)

### Update Interval
- `update_interval`: How often to check player state (seconds)

## Troubleshooting

### Cannot connect to Volumio
- Verify Volumio is running: `curl http://localhost:3000/api/v1/getState`
- Check the host and port in config.yaml
- Ensure network connectivity if Volumio is on another device

### Cannot connect to WLED
- Verify WLED is accessible: `curl http://WLED_IP/json/state`
- Check the WLED host IP in config.yaml
- Ensure WLED device is powered on and connected to network

### LEDs not updating
- Check LED count in config.yaml matches your physical LED strip
- Verify WLED is not running another effect or preset
- Check application logs for errors

### Service not starting
- Check service status: `sudo systemctl status volumiwled.service`
- View detailed logs: `sudo journalctl -u volumiwled.service -n 50`
- Verify paths in volumiwled.service file are correct
- Ensure config.yaml exists and is readable

## Examples

See [EXAMPLES.md](EXAMPLES.md) for:
- API response examples from Volumio and WLED
- Effect behavior demonstrations
- Additional configuration examples
- Testing without hardware
- Common LED strip configurations

## API References

- [Volumio API Documentation](https://volumio.github.io/docs/API/REST_API.html)
- [WLED JSON API Documentation](https://kno.wled.ge/interfaces/json-api/)

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Created for controlling WLED LED strips based on Volumio playback state on Raspberry Pi devices.
