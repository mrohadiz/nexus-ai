from collections import deque
from datetime import datetime
from typing import Deque, Dict, List


class RoutingMetrics:
    def __init__(self, max_items: int = 500):
        self._events: Deque[Dict] = deque(maxlen=max_items)

    def log(self, event: Dict) -> None:
        payload = dict(event)
        payload["timestamp"] = datetime.utcnow().isoformat()
        self._events.append(payload)

    def snapshot(self, limit: int = 50) -> List[Dict]:
        if limit <= 0:
            return []
        items = list(self._events)
        return items[-limit:]


routing_metrics = RoutingMetrics()
