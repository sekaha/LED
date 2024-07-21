import os
import socket
import time
import struct
import numpy as np
from typing import Union, List, Optional


class _OPCClient:
    def __init__(self, server: Optional[str] = None) -> None:
        # Set server address; defaults to environment variable or localhost
        self.server_address = server or os.getenv("OPC_SERVER") or "127.0.0.1:7890"
        self.socket: Optional[socket.socket] = None
        self.host, port_str = self.server_address.split(":")
        self.port = int(port_str)

    def send(self, packet: bytes) -> bool:
        """Send a packet to the OPC server, reconnecting if needed. Returns True on success."""
        if self.socket is None:
            # Try to create and connect the socket
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.socket.connect((self.host, self.port))
                self.socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
            except socket.error:
                self.socket = None

        if self.socket:
            try:
                self.socket.send(packet)
                return True
            except socket.error:
                self.socket = None

        # Sleep to limit CPU usage while waiting
        time.sleep(0.1)

        return False

    def send_pixels(
        self, channel: int, *sources: Union[List[List[int]], np.ndarray]
    ) -> None:
        """Send a list of 8-bit colors to the specified channel (OPC command 0x00)."""
        rgb_values = []
        total_values = 0

        for source in sources:
            flattened: List[int] = []

            if isinstance(source, list):
                # Flatten the list of colors
                for item in source:
                    if isinstance(item, list):
                        flattened.extend(int(color) for color in item)
                    else:
                        flattened.append(int(item))
            elif isinstance(source, np.ndarray):
                # Convert NumPy array to a flat list of integers
                flattened = source.flatten().astype(int).tolist()

            # Clamp values to the range [0, 255]
            flattened = [max(min(255, v), 0) for v in flattened]
            rgb_values.extend(flattened)
            total_values += len(flattened)

        # Create the packet header and message
        header = struct.pack(">BBH", channel, 0, total_values)
        message = header + bytes(rgb_values)
        self.send(message)
