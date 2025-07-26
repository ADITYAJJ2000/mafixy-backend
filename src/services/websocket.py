from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
from datetime import datetime
from ..config.settings import get_settings

settings = get_settings()

class WebSocketService:
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.last_active: Dict[str, datetime] = {}

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """Connect a WebSocket client."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)
        self.last_active[user_id] = datetime.utcnow()

    def disconnect(self, websocket: WebSocket, user_id: str) -> None:
        """Disconnect a WebSocket client."""
        if user_id in self.active_connections:
            self.active_connections[user_id].discard(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]
            if user_id in self.last_active:
                del self.last_active[user_id]

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """Send a message to a single client."""
        await websocket.send_json(message)

    async def broadcast(self, message: dict, user_id: str) -> None:
        """Broadcast a message to all clients of a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    self.disconnect(connection, user_id)

    def get_active_users(self) -> List[str]:
        """Get list of active users."""
        return list(self.active_connections.keys())

    def cleanup_inactive_connections(self) -> None:
        """Cleanup inactive connections."""
        current_time = datetime.utcnow()
        inactive_users = []
        
        for user_id, last_active in self.last_active.items():
            if (current_time - last_active).total_seconds() > settings.WEBSOCKET_TIMEOUT:
                inactive_users.append(user_id)
        
        for user_id in inactive_users:
            if user_id in self.active_connections:
                del self.active_connections[user_id]
            del self.last_active[user_id]

websocket_service = WebSocketService()
