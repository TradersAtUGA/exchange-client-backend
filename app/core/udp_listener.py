import asyncio
import logging
from typing import Callable, Optional

logger = logging.getLogger(__name__)


class UDPListener:
    """Asynchronous UDP listener for receiving messages."""

    def __init__(self, host: str = "0.0.0.0", port: int = 5000):
        """
        Initialize UDP listener.

        Args:
            host: Host to bind to (default: 0.0.0.0)
            port: Port to listen on (default: 5000)
        """
        self.host = host
        self.port = port
        self.transport: Optional[asyncio.DatagramTransport] = None
        self.protocol: Optional["UDPProtocol"] = None
        self.running = False
        self.message_handler: Optional[Callable] = None

    async def start(self):
        """Start the UDP listener."""
        try:
            loop = asyncio.get_event_loop()
            transport, protocol = await loop.create_datagram_endpoint(
                lambda: UDPProtocol(self._handle_message),
                local_addr=(self.host, self.port),
            )
            self.transport = transport
            self.protocol = protocol
            self.running = True
            logger.info(f"UDP listener started on {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to start UDP listener: {e}")
            raise

    async def stop(self):
        """Stop the UDP listener."""
        if self.transport:
            self.transport.close()
            self.running = False
            logger.info("UDP listener stopped")

    async def _handle_message(self, data: bytes, addr: tuple):
        """
        Handle incoming UDP message.

        Args:
            data: The received data
            addr: The sender's address (host, port)
        """
        try:
            logger.debug(f"Received UDP message from {addr}: {data[:100]}")
            # Custom message handler if set
            if self.message_handler:
                await self.message_handler(data, addr)
        except Exception as e:
            logger.error(f"Error handling UDP message: {e}")

    def set_message_handler(self, handler: Callable):
        """
        Set a custom message handler.

        Args:
            handler: Async callable that accepts (data: bytes, addr: tuple)
        """
        self.message_handler = handler


class UDPProtocol(asyncio.DatagramProtocol):
    """UDP protocol handler."""

    def __init__(self, message_handler: Callable):
        """
        Initialize protocol.

        Args:
            message_handler: Async callable to handle messages
        """
        self.message_handler = message_handler
        self.transport = None

    def connection_made(self, transport):
        """Called when connection is made."""
        self.transport = transport

    def datagram_received(self, data: bytes, addr: tuple):
        """Called when a datagram is received."""
        asyncio.create_task(self.message_handler(data, addr))

    def error_received(self, exc: Exception):
        """Called when an error is received."""
        logger.error(f"UDP error: {exc}")

    def connection_lost(self, exc: Optional[Exception]):
        """Called when connection is lost."""
        if exc:
            logger.error(f"UDP connection lost: {exc}")


# Global UDP listener instance
udp_listener: Optional[UDPListener] = None


async def init_udp_listener(host: str = "0.0.0.0", port: int = 5000):
    """Initialize and start the UDP listener."""
    global udp_listener
    udp_listener = UDPListener(host=host, port=port)
    await udp_listener.start()


async def shutdown_udp_listener():
    """Shutdown the UDP listener."""
    global udp_listener
    if udp_listener:
        await udp_listener.stop()


def get_udp_listener() -> Optional[UDPListener]:
    """Get the global UDP listener instance."""
    return udp_listener
