"""Model B: an asyncio loop on its own thread for PLC / SECS / E84 I/O. No tkinter in here.

Copy to app/comms_runtime.py.

    runtime = CommsRuntime(); runtime.start()
    fut = runtime.submit(plc.read_status())                 # from the Tk thread
    fut.add_done_callback(lambda f: ui.post(show, f))       # callback runs on the comms thread

Shutdown order on WM_DELETE_WINDOW: runtime.stop() -> ui.close() -> root.destroy().
"""
from __future__ import annotations

import asyncio
import concurrent.futures
import threading
from typing import Any, Coroutine


class CommsRuntime:
    """Owns an asyncio loop on a dedicated thread."""

    def __init__(self) -> None:
        self.loop = asyncio.new_event_loop()
        self._thread = threading.Thread(target=self._run, name="comms", daemon=True)

    def start(self) -> None:
        self._thread.start()

    def _run(self) -> None:
        asyncio.set_event_loop(self.loop)
        try:
            self.loop.run_forever()
        finally:
            self.loop.run_until_complete(self.loop.shutdown_asyncgens())
            self.loop.close()

    def submit(self, coro: Coroutine[Any, Any, Any]) -> concurrent.futures.Future:
        """Call from any non-comms thread (normally the Tk thread)."""
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self, timeout: float = 3.0) -> None:
        async def _shutdown() -> None:
            tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
            for t in tasks:
                t.cancel()
            await asyncio.gather(*tasks, return_exceptions=True)

        if self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(_shutdown(), self.loop).result(timeout)
            except Exception:
                pass    # a task ignoring cancellation must not block closing the window
            self.loop.call_soon_threadsafe(self.loop.stop)
        self._thread.join(timeout)
