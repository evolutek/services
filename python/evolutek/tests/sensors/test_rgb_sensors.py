#!/usr/bin/env python3
"""
Test script for RGB sensors (TCS34725) behind TCA9548A multiplexer.
Scans all channels and displays detected sensors.
"""

import board
import busio
import adafruit_tca9548a
import adafruit_tcs34725
from time import sleep


class RGBSensorScanner:
    def __init__(self):
        self.i2c = None
        self.tca = None
        self.found_sensors = []

    def initialize(self):
        """Initialize I2C bus and TCA9548A multiplexer."""
        try:
            self.i2c = busio.I2C(board.SCL, board.SDA)
            print("[I2C] Bus initialized")
        except Exception as e:
            print(f"[I2C] Failed to initialize: {e}")
            return False

        # Deselect all channels first
        while not self.i2c.try_lock():
            sleep(0.001)
        try:
            self.i2c.writeto(0x70, bytes([0x00]))
            print("[TCA9548A] All channels deselected")
        finally:
            self.i2c.unlock()

        # Initialize TCA9548A
        try:
            self.tca = adafruit_tca9548a.TCA9548A(self.i2c)
            print("[TCA9548A] Multiplexer initialized (0x70)")
        except Exception as e:
            print(f"[TCA9548A] Failed to initialize: {e}")
            return False

        return True

    def scan_channels(self):
        """Scan all 8 channels of TCA9548A for all I2C devices."""
        print("\nScanning TCA9548A channels for I2C devices (all addresses)\n")

        # Known device types by address
        known_devices = {
            0x29: "TCS34725 (RGB color sensor)",
            0x39: "TCS3400 or TSL2561 (color/light sensor)",
            0x49: "TSL2561 variant",
            0x44: "SHT31 (temp/humidity)",
            0x68: "DS3231 (RTC)",
            0x70: "TCA9548A (multiplexer)",
        }

        for channel in range(8):
            print(f"Channel {channel}:")
            found_on_channel = []

            # Try TCS34725 at 0x29 first (main sensor)
            try:
                sensor = adafruit_tcs34725.TCS34725(self.tca[channel])
                try:
                    color_rgb = sensor.color_rgb_bytes
                    self.found_sensors.append({
                        'channel': channel,
                        'rgb': color_rgb,
                        'sensor': sensor,
                        'type': 'TCS34725 (0x29)'
                    })
                    found_on_channel.append(f"0x29: TCS34725 - RGB: {color_rgb}")
                except Exception:
                    pass
            except Exception:
                pass

            # Scan all other I2C addresses
            from adafruit_bus_device.i2c_device import I2CDevice
            for addr in range(0x00, 0xFF):
                if addr == 0x29:  # Already tried
                    continue
                
                try:
                    i2c_dev = I2CDevice(self.tca[channel], addr)
                    buf = bytearray(1)
                    i2c_dev.readinto(buf)
                    
                    device_name = known_devices.get(addr, f"Unknown device")
                    found_on_channel.append(f"0x{addr:02x}: {device_name}")
                except Exception:
                    pass

            if found_on_channel:
                for device in found_on_channel:
                    print(f"  [OK] {device}")
            else:
                print(f"  [EMPTY]")

        return len(self.found_sensors) > 0

    def continuous_read(self):
        """Read from sensors continuously."""
        if not self.found_sensors:
            print("No sensors to read")
            return

        print("Starting continuous read (Ctrl+C to stop)\n")
        
        try:
            while True:
                for sensor_info in self.found_sensors:
                    channel = sensor_info['channel']
                    sensor = sensor_info['sensor']
                    
                    try:
                        rgb = sensor.color_rgb_bytes
                        print(f"Channel {channel}: RGB = {rgb}")
                    except Exception as e:
                        print(f"Channel {channel}: Read failed - {e}")
                
                sleep(0.5)
        except KeyboardInterrupt:
            print("\nRead stopped")


    def run(self):
        """Run the complete scan."""
        if not self.initialize():
            print("\n[FATAL] Failed to initialize hardware")
            return False

        if not self.scan_channels():
            print("\n[WARNING] No sensors found during scan")

        self.continuous_read()

        return len(self.found_sensors) > 0


if __name__ == '__main__':
    scanner = RGBSensorScanner()
    success = scanner.run()
    exit(0 if success else 1)
