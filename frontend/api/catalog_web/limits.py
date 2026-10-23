"""Limits on how many submissions the service accepts, per visitor address and in total."""

import os
import time
from collections import deque

WINDOW_SECONDS = 3600


class SubmissionLimit:
    """Counts submissions in the last hour. Kept in memory, so a restart clears the counts."""

    def __init__(self, per_address: int | None = None, total: int | None = None) -> None:
        self.per_address = per_address if per_address is not None else int(os.environ.get("SUBMISSIONS_PER_ADDRESS_PER_HOUR", "5"))
        self.total = total if total is not None else int(os.environ.get("SUBMISSIONS_PER_HOUR", "50"))
        self._by_address: dict[str, deque[float]] = {}
        self._all: deque[float] = deque()

    def _prune(self, times: deque[float], now: float) -> None:
        while times and now - times[0] >= WINDOW_SECONDS:
            times.popleft()

    def allow(self, address: str, now: float | None = None) -> bool:
        """Record a submission from the address and return True, or return False when over a limit."""
        now = time.monotonic() if now is None else now
        self._prune(self._all, now)
        if len(self._by_address) > 10_000:
            for key in [key for key, times in self._by_address.items() if not times or now - times[-1] >= WINDOW_SECONDS]:
                del self._by_address[key]
        times = self._by_address.setdefault(address, deque())
        self._prune(times, now)
        if len(times) >= self.per_address or len(self._all) >= self.total:
            return False
        times.append(now)
        self._all.append(now)
        return True
