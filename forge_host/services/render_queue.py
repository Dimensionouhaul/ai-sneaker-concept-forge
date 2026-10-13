"""Async render queue with a bounded worker pool.

Jobs are enqueued by the UI; the pool runs them with the configured
concurrency cap. Cancellation is cooperative via ``asyncio.Event``.
"""

from __future__ import annotations

import asyncio
import logging
from collections.abc import Awaitable, Callable

from forge_contracts.errors import RenderQueueError

log = logging.getLogger("forge.queue")

JobFn = Callable[[], Awaitable[None]]


class RenderQueue:
    def __init__(self, max_concurrent: int = 2) -> None:
        if max_concurrent < 1:
            raise Render