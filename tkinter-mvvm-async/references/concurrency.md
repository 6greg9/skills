# Concurrency details

## Model A — asyncio owns the thread, Tk is pumped

Only for small tools where a UI freeze of a few seconds is harmless.

```python
import asyncio
import tkinter as tk

class App:
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.running = True
        self.root.protocol("WM_DELETE_WINDOW", self.close)

    def close(self) -> None:
        self.running = False

    async def tk_pump(self) -> None:
        while self.running:
            self.root.update()
            await asyncio.sleep(1 / 60)
        self.root.destroy()

    async def main(self) -> None:
        await asyncio.gather(self.tk_pump(), self.worker())

    async def worker(self) -> None:
        while self.running:
            # await async I/O here; touching widgets is safe (same thread)
            await asyncio.sleep(0.1)

if __name__ == "__main__":
    asyncio.run(App().main())
```

Known freezes in Model A (every coroutine stops):
- **Windows window drag/resize**: the OS enters a modal move/size loop; `update()` does not
  return until the mouse is released.
- `messagebox.*`, `filedialog.*`, `wait_window`, `wait_variable`: they spin their own nested loop.
- Any CPU-heavy callback.

## Model B — comms loop on its own thread

Use `templates/comms_runtime.py`. Wiring in the app:

```python
root = tk.Tk()
ui = UiDispatcher(root)
runtime = CommsRuntime()
runtime.start()
vm = LoadPortVM(plc=PlcClient(...), runtime=runtime)    # VM gets the runtime, never the UI

def on_close() -> None:
    runtime.stop()
    ui.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_close)
root.mainloop()
```

In the VM, a command submits a coroutine and posts its result back through observables, which
the binders marshal to the Tk thread:

```python
async def _load(self) -> None:
    self.busy.value = True                  # set on the comms thread; binders post to Tk
    try:
        await self.plc.write_bit("M100", True)
        self.state.value = await self.plc.read_state()
    finally:
        self.busy.value = False

self.load = Command(lambda: self.runtime.submit(self._load()), can_load)
```

`CommsRuntime.stop()` cancels all tasks, waits up to `timeout` seconds, stops and closes the
loop. A task that swallows `CancelledError` cannot block closing the window.

## Model C — plain worker threads

For a single legacy blocking driver: a `threading.Thread(daemon=True)` loop that reads and sets
VM observables; binders post to the UI. Signal shutdown with a `threading.Event`, join with a
timeout. Move to Model B as soon as there are several protocols or any protocol timers.

## Blocking libraries and CPU work

- pyserial, synchronous pymodbus, vendor PLC DLLs via ctypes, synchronous DB drivers:
  `await asyncio.to_thread(fn, ...)` (or `loop.run_in_executor`). In Model A the await resumes
  on the Tk thread (widgets are safe afterwards); in Model B it resumes on the comms thread
  (still go through the dispatcher).
- CPU-heavy work (image processing, large log parsing): `ProcessPoolExecutor`, not threads.

## Threaded Tcl caveat

Official CPython builds use threaded Tcl, which forwards some calls made from other threads
(e.g. `root.after(...)`) to the main thread while `mainloop()` runs, and raises
`RuntimeError: main thread is not in main loop` otherwise. Code that happens to work this way
is fragile; route everything through `UiDispatcher.post` instead.
