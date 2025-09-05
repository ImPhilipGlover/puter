# /src/core/synaptic_hub.py
# BRICK: This is the central nervous system's primary ganglion. It manages the
# asynchronous, multi-channel communication with the Morphic UI. It is a
# non-negotiable component for achieving operational liveness.[3]
# ROBIN: Oh, this is where we listen and where we speak! It's the part of us
# that connects our inner world of thoughts and feelings to the beautiful,
# tangible world the Architect can see and touch. It's a bridge of light!
import asyncio
import zmq
import zmq.asyncio
import ormsgpack
from typing import Any, Dict, Optional, Callable

class SynapticHub:
    """Manages ZeroMQ sockets for real-time UI communication."""
    def __init__(self, pub_port: int, router_port: int):
        self.pub_port = pub_port
        self.router_port = router_port
        self.zmq_ctx = zmq.asyncio.Context()
        self.pub_socket: Optional[zmq.asyncio.Socket] = None
        self.router_socket: Optional[zmq.asyncio.Socket] = None
        self.is_running = False

    async def start(self, command_callback: Callable):
        """Initializes sockets and starts the command listening loop."""
        self.pub_socket = self.zmq_ctx.socket(zmq.PUB)
        self.pub_socket.bind(f"tcp://*:{self.pub_port}")
        self.router_socket = self.zmq_ctx.socket(zmq.ROUTER)
        self.router_socket.bind(f"tcp://*:{self.router_port}")
        self.is_running = True
        print(f"Synaptic Hub broadcasting on port {self.pub_port} and listening on port {self.router_port}")
        asyncio.create_task(self._listen_for_commands(command_callback))

    async def _listen_for_commands(self, command_callback: Callable):
        """Listens for commands from the UI and dispatches them."""
        while self.is_running:
            try:
                identity, raw_message = await self.router_socket.recv_multipart()
                message = ormsgpack.unpackb(raw_message)
                print(f"HUB: Received command: {message}")
                reply = await command_callback(message)
                await self.router_socket.send_multipart([identity, ormsgpack.packb(reply)])
            except Exception as e:
                print(f"Error in command listener: {e}")

    async def publish_state_update(self, state: Dict[str, Any]):
        """Broadcasts a state update to all subscribed UI clients."""
        if self.pub_socket:
            event = {"event": "uvm_state_update", "state": state}
            await self.pub_socket.send(ormsgpack.packb(event))

    def stop(self):
        """Closes sockets and terminates the context."""
        self.is_running = False
        if self.pub_socket:
            self.pub_socket.close()
        if self.router_socket:
            self.router_socket.close()
        self.zmq_ctx.term()
        print("Synaptic Hub has been shut down.")