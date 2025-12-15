#!/usr/bin/env python3
"""
VolumiWLED - Connect Volumio player with WLED for LED visualization
"""

import sys
import time
import math
import requests
import yaml
import logging
from typing import Dict, Optional, Tuple


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('VolumiWLED')


class VolumioClient:
    """Client for interacting with Volumio API"""
    
    def __init__(self, host: str, port: int):
        self.base_url = f"http://{host}:{port}"
        
    def get_state(self) -> Optional[Dict]:
        """Get current player state from Volumio"""
        try:
            response = requests.get(f"{self.base_url}/api/v1/getState", timeout=2)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"Error getting Volumio state: {e}")
            return None


class WLEDClient:
    """Client for controlling WLED via REST API"""
    
    def __init__(self, host: str):
        self.base_url = f"http://{host}"
        
    def set_state(self, on: bool = True, brightness: Optional[int] = None) -> bool:
        """Set WLED on/off state and brightness"""
        try:
            payload = {"on": on}
            if brightness is not None:
                payload["bri"] = brightness
            response = requests.post(
                f"{self.base_url}/json/state",
                json=payload,
                timeout=2
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error setting WLED state: {e}")
            return False
    
    def set_segment(self, segment_id: int = 0, start: int = 0, stop: int = None,
                    color: Tuple[int, int, int] = (255, 255, 255)) -> bool:
        """Set a segment with specific color"""
        try:
            payload = {
                "seg": [{
                    "id": segment_id,
                    "start": start,
                    "stop": stop,
                    "col": [list(color)]
                }]
            }
            response = requests.post(
                f"{self.base_url}/json/state",
                json=payload,
                timeout=2
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error setting WLED segment: {e}")
            return False
    
    def clear_leds(self, led_count: int) -> bool:
        """Turn off all LEDs"""
        return self.set_segment(start=0, stop=led_count, color=(0, 0, 0))
    
    def set_individual_leds(self, led_data: list) -> bool:
        """Set individual LED colors"""
        try:
            payload = {
                "seg": [{
                    "i": led_data
                }]
            }
            response = requests.post(
                f"{self.base_url}/json/state",
                json=payload,
                timeout=2
            )
            response.raise_for_status()
            return True
        except requests.RequestException as e:
            logger.error(f"Error setting individual LEDs: {e}")
            return False


class EffectManager:
    """Manages LED effects based on player state"""
    
    def __init__(self, wled_client: WLEDClient, config: Dict):
        self.wled = wled_client
        self.config = config
        self.led_count = config['led']['count']
        self.brightness = config['led']['brightness']
        self.rotation_offset = 0
        
    def apply_progress_bar(self, progress: float, duration: float) -> bool:
        """
        Apply progress bar effect showing playback progress
        
        Args:
            progress: Current position in seconds
            duration: Total track duration in seconds
        """
        if duration <= 0:
            return False
        
        # Calculate how many LEDs should be lit based on progress
        progress_ratio = min(progress / duration, 1.0)
        leds_to_light = int(self.led_count * progress_ratio)
        
        # Get progress bar color from config
        color = tuple(self.config['effects']['progress_bar']['color'])
        
        # Build LED data: light up LEDs from start to progress position
        led_data = []
        for i in range(self.led_count):
            if i < leds_to_light:
                led_data.extend([i, *color])
            else:
                led_data.extend([i, 0, 0, 0])
        
        return self.wled.set_individual_leds(led_data)
    
    def apply_vinyl_rotation(self, is_playing: bool) -> bool:
        """
        Apply rotating vinyl effect that mimics a spinning record
        
        Args:
            is_playing: Whether the player is currently playing
        """
        if not is_playing:
            # If not playing, just show a static pattern or turn off
            return self.wled.clear_leds(self.led_count)
        
        # Get vinyl effect settings
        color = tuple(self.config['effects']['vinyl_rotation']['color'])
        speed = self.config['effects']['vinyl_rotation']['speed']
        
        # Update rotation offset
        self.rotation_offset = (self.rotation_offset + 1) % self.led_count
        
        # Create rotating effect: lit LEDs move around the strip
        # Create a pattern that looks like vinyl grooves
        led_data = []
        pattern_width = max(1, self.led_count // 8)  # Width of the lit section
        
        for i in range(self.led_count):
            # Calculate position relative to rotation offset
            pos = (i - self.rotation_offset) % self.led_count
            
            # Create a pulsing pattern
            angle = (pos / self.led_count) * 2 * math.pi * 4  # 4 sections
            intensity = (math.sin(angle) + 1) / 2  # 0 to 1
            
            # Apply intensity to color
            r = int(color[0] * intensity)
            g = int(color[1] * intensity)
            b = int(color[2] * intensity)
            
            led_data.extend([i, r, g, b])
        
        # Add a slight delay based on speed setting
        time.sleep(speed / 1000.0)
        
        return self.wled.set_individual_leds(led_data)


class VolumiWLED:
    """Main application class"""
    
    def __init__(self, config_path: str = "config.yaml"):
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize clients
        self.volumio = VolumioClient(
            self.config['volumio']['host'],
            self.config['volumio']['port']
        )
        self.wled = WLEDClient(self.config['wled']['host'])
        self.effects = EffectManager(self.wled, self.config)
        
        # Track previous state
        self.previous_status = None
        
        logger.info("VolumiWLED initialized")
        
    def run(self):
        """Main application loop"""
        logger.info("Starting VolumiWLED...")
        
        # Turn on WLED
        self.wled.set_state(on=True, brightness=self.config['led']['brightness'])
        
        try:
            while True:
                # Get current Volumio state
                state = self.volumio.get_state()
                
                if state is None:
                    logger.warning("Could not get Volumio state, retrying...")
                    time.sleep(self.config['update_interval'])
                    continue
                
                status = state.get('status', 'stop')
                
                # Log status changes
                if status != self.previous_status:
                    logger.info(f"Player status changed: {self.previous_status} -> {status}")
                    self.previous_status = status
                
                # Apply effects based on player state
                if status == 'play':
                    # Get track info
                    seek = state.get('seek', 0) / 1000  # Convert ms to seconds
                    duration = state.get('duration', 0)
                    
                    # Choose which effect to apply
                    if self.config['effects']['progress_bar']['enabled'] and duration > 0:
                        self.effects.apply_progress_bar(seek, duration)
                    elif self.config['effects']['vinyl_rotation']['enabled']:
                        self.effects.apply_vinyl_rotation(True)
                        
                elif status == 'pause':
                    # Show paused state - static progress bar
                    seek = state.get('seek', 0) / 1000
                    duration = state.get('duration', 0)
                    if self.config['effects']['progress_bar']['enabled'] and duration > 0:
                        self.effects.apply_progress_bar(seek, duration)
                    else:
                        # Dim the LEDs to indicate pause
                        self.wled.set_state(on=True, brightness=self.config['led']['brightness'] // 4)
                        
                elif status == 'stop':
                    # Turn off LEDs when stopped
                    self.wled.clear_leds(self.config['led']['count'])
                
                # Wait before next update
                time.sleep(self.config['update_interval'])
                
        except KeyboardInterrupt:
            logger.info("Shutting down VolumiWLED...")
            self.wled.clear_leds(self.config['led']['count'])
            self.wled.set_state(on=False)


def main():
    """Entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='VolumiWLED - Volumio to WLED bridge')
    parser.add_argument(
        '-c', '--config',
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    args = parser.parse_args()
    
    try:
        app = VolumiWLED(args.config)
        app.run()
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {args.config}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
