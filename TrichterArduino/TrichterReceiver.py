"""
HC-05 Bluetooth Module Receiver
Connects to an HC-05 Bluetooth module using PyBluez and receives data from it.
"""

import bluetooth
import time
import sys


class BluetoothReceiver:
    """Class to manage HC-05 Bluetooth module communication using PyBluez."""
    
    def __init__(self, device_name='HC-05', device_address=None, timeout=1):
        """
        Initialize Bluetooth receiver.
        
        Args:
            device_name (str): Name of the HC-05 device (default: 'HC-05')
            device_address (str): MAC address of HC-05 (e.g., '00:1A:7D:DA:71:13')
            timeout (int): Read timeout in seconds
        """
        self.device_name = device_name
        self.device_address = device_address
        self.timeout = timeout
        self.socket = None
        self.buffer = bytearray()
        
    def discover_devices(self):
        """
        Scan for nearby Bluetooth devices.
        
        Returns:
            list: List of tuples (address, name)
        """
        print("Scanning for Bluetooth devices...")
        try:
            nearby_devices = bluetooth.discover_devices(
                duration=8,
                lookup_names=True,
                flush_cache=True,
                caching=False
            )
            return nearby_devices
        except Exception as e:
            print(f"✗ Error during device discovery: {e}")
            return []
    
    def find_hc05(self):
        """
        Search for HC-05 device by name or use provided address.
        
        Returns:
            str: MAC address of HC-05 or None if not found
        """
        if self.device_address:
            print(f"Using provided HC-05 address: {self.device_address}")
            return self.device_address
        
        devices = self.discover_devices()
        if not devices:
            print("✗ No Bluetooth devices found")
            return None
        
        print(f"\nFound {len(devices)} device(s):")
        for address, name in devices:
            print(f"  {address} - {name}")
            if name and self.device_name.lower() in name.lower():
                print(f"✓ Found HC-05: {address} ({name})")
                return address
        
        print(f"✗ HC-05 device '{self.device_name}' not found")
        return None
    
    def connect(self):
        """Establish Bluetooth socket connection to HC-05 module."""
        if not self.device_address:
            self.device_address = self.find_hc05()
            if not self.device_address:
                return False
        
        try:
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.socket.settimeout(self.timeout)
            self.socket.connect((self.device_address, 1))  # RFCOMM port 1
            print(f"✓ Connected to HC-05 at {self.device_address}")
            return True
        except Exception as e:
            print(f"✗ Failed to connect to {self.device_address}: {e}")
            return False
    
    def disconnect(self):
        """Close Bluetooth socket connection."""
        if self.socket:
            try:
                self.socket.close()
                print("✓ Disconnected from HC-05")
            except Exception as e:
                print(f"✗ Error closing connection: {e}")
            self.socket = None
    
    def receive_bytes(self, buffer_size=1024):
        """
        Read raw bytes from the HC-05 module.
        
        Args:
            buffer_size (int): Number of bytes to read
        
        Returns:
            bytes: Raw data or None if error or no data
        """
        if not self.socket:
            return None
        
        try:
            data = self.socket.recv(buffer_size)
            return data if data else None
        except bluetooth.BluetoothError as e:
            if "timed out" not in str(e).lower():
                print(f"✗ Error reading data: {e}")
            return None
        except Exception as e:
            print(f"✗ Error reading data: {e}")
            return None
    
    def receive_line(self):
        """
        Read one line of data from the HC-05 module (delimited by newline).
        
        Returns:
            str: Decoded data line or None if no complete line available
        """
        while True:
            # Check if we have a complete line in buffer
            try:
                newline_index = self.buffer.find(b'\n')
                if newline_index >= 0:
                    line = self.buffer[:newline_index]
                    self.buffer = self.buffer[newline_index + 1:]
                    return line.decode('utf-8', errors='ignore').strip()
            except Exception as e:
                print(f"✗ Error decoding line: {e}")
                self.buffer.clear()
                return None
            
            # Read more data
            data = self.receive_bytes()
            if data:
                self.buffer.extend(data)
            else:
                return None
    
    def listen(self, decode=True):
        """
        Continuously listen for incoming data from HC-05.
        
        Args:
            decode (bool): If True, decode as UTF-8 text. If False, show raw bytes.
        """
        print("Listening for data... (Press Ctrl+C to stop)")
        try:
            while True:
                if decode:
                    data = self.receive_line()
                    if data:
                        print(f"Received: {data}")
                else:
                    data = self.receive_bytes()
                    if data:
                        print(f"Received (raw): {data.hex()}")
                
                time.sleep(0.05)  # Small delay to reduce CPU usage
        
        except KeyboardInterrupt:
            print("\n✓ Stopped listening")


def main():
    """Main function - example usage."""
    # Configure these values based on your HC-05 device
    HC05_NAME = 'HC-05'  # Device name (appears in Bluetooth settings)
    HC05_ADDRESS = None  # Optional: MAC address (e.g., '00:1A:7D:DA:71:13')
    
    # Create receiver instance
    receiver = BluetoothReceiver(
        device_name=HC05_NAME,
        device_address=HC05_ADDRESS
    )
    
    # Connect to HC-05
    if not receiver.connect():
        print("Failed to connect. Exiting.")
        sys.exit(1)
    
    try:
        # Listen for data (decode as text)
        receiver.listen(decode=True)
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Clean up
        receiver.disconnect()


if __name__ == '__main__':
    main()
