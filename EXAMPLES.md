# VolumiWLED Examples

## API Response Examples

### Volumio API Response (getState)

When a track is playing:

```json
{
  "status": "play",
  "position": 0,
  "title": "Song Title",
  "artist": "Artist Name",
  "album": "Album Name",
  "albumart": "/albumart?...",
  "uri": "...",
  "trackType": "mp3",
  "seek": 45000,
  "duration": 180,
  "samplerate": "44.1 KHz",
  "bitdepth": "16 bit",
  "channels": 2,
  "random": false,
  "repeat": false,
  "repeatSingle": false,
  "consume": false,
  "volume": 50,
  "mute": false,
  "stream": false,
  "updatedb": false,
  "volatile": false,
  "service": "mpd"
}
```

Key fields used by VolumiWLED:
- `status`: "play", "pause", or "stop"
- `seek`: Current position in milliseconds
- `duration`: Track duration in seconds

### WLED JSON API Examples

#### Turn on LEDs with brightness

Request:
```json
{
  "on": true,
  "bri": 128
}
```

#### Set individual LED colors

Request:
```json
{
  "seg": [{
    "i": [
      0, 255, 0, 0,     // LED 0: Red
      1, 0, 255, 0,     // LED 1: Green
      2, 0, 0, 255      // LED 2: Blue
    ]
  }]
}
```

#### Set a segment with color

Request:
```json
{
  "seg": [{
    "id": 0,
    "start": 0,
    "stop": 30,
    "col": [[0, 255, 0]]  // Green
  }]
}
```

## Effect Behavior Examples

### Progress Bar Effect

For a 3-minute track (180 seconds) at 90 seconds (50% progress) with 60 LEDs:

- LEDs 0-29: Lit with configured progress color
- LEDs 30-59: Off (black)

As the track progresses, more LEDs light up from left to right.

### Vinyl Rotation Effect

Creates a rotating pattern with 4 "grooves" that spin around the LED strip:

- Uses sine wave to create intensity variation
- Rotation speed controlled by `speed` config parameter
- Pattern continuously rotates while music is playing
- Stops when music is paused or stopped

## Configuration Examples

### High-Speed Vinyl Rotation

```yaml
effects:
  vinyl_rotation:
    enabled: true
    color: [255, 0, 255]
    speed: 25  # Faster rotation
```

### Slow, Smooth Vinyl Rotation

```yaml
effects:
  vinyl_rotation:
    enabled: true
    color: [255, 0, 255]
    speed: 100  # Slower rotation
```

### Blue Progress Bar

```yaml
effects:
  progress_bar:
    enabled: true
    color: [0, 0, 255]  # Blue
```

### Multiple LED Strips

If you have multiple WLED devices, create multiple configuration files:

**config_strip1.yaml**:
```yaml
wled:
  host: "192.168.1.100"
led:
  count: 60
```

**config_strip2.yaml**:
```yaml
wled:
  host: "192.168.1.101"
led:
  count: 144
```

Run multiple instances:
```bash
python3 volumiwled.py -c config_strip1.yaml &
python3 volumiwled.py -c config_strip2.yaml &
```

## Testing Without WLED Hardware

You can test the Volumio integration without WLED hardware by watching the logs:

```bash
# Run with verbose logging
python3 volumiwled.py
```

The application will log errors when it can't connect to WLED, but will continue monitoring Volumio. This lets you verify the Volumio integration is working before connecting LED hardware.

## Common LED Configurations

### WS2812B Strip (60 LEDs/meter, 1 meter)
```yaml
led:
  count: 60
  brightness: 128
```

### WS2812B Strip (144 LEDs/meter, 1 meter)
```yaml
led:
  count: 144
  brightness: 100  # Lower brightness for more LEDs
```

### Ring Configuration (24 LED Ring)
```yaml
led:
  count: 24
  brightness: 150
effects:
  vinyl_rotation:
    speed: 40  # Adjust for smaller ring
```

### Long Strip (300 LEDs)
```yaml
led:
  count: 300
  brightness: 80  # Lower brightness for many LEDs
update_interval: 0.3  # Slightly slower updates for many LEDs
```
