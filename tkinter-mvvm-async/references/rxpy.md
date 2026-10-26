# Option: RxPY (`reactivex`) instead of the hand-rolled Observable

Worth it when the VM needs time or combination logic: `combine_latest`, `debounce`,
`throttle_first`, `distinct_until_changed`, timeouts. For plain state and commands,
`templates/observable.py` is simpler and has no dependency.

| Need | Rx construct |
|---|---|
| VM property with current value | `BehaviorSubject(initial)` |
| Event / command stream | `Subject()` |
| Derived state from several signals | `rx.combine_latest(a, b).pipe(ops.map(...))` |
| Throttle high-rate PLC values for display | `ops.throttle_first(0.2)` or `ops.sample(0.2)` |
| Suppress redundant UI updates | `ops.distinct_until_changed()` |
| Deliver on the Tk thread | subscribe and forward through `UiDispatcher.post` (see caveat) |
| Single-thread asyncio design | `AsyncIOScheduler(loop)` from `reactivex.scheduler.eventloop` |

Caveat: `TkinterScheduler` (in `reactivex.scheduler.mainloop`) schedules with `root.after()`
called from the producing thread. That only works because official CPython builds use threaded
Tcl, which forwards the call to the main thread while `mainloop()` runs; otherwise it raises
`RuntimeError: main thread is not in main loop`. Prefer forwarding through
`UiDispatcher.post`, which works regardless:

```python
sub = vm.temperature.pipe(ops.sample(0.2), ops.distinct_until_changed()).subscribe(
    lambda v: ui.post(view.lbl_temp.configure, text=f"{v:.1f}"))
bindings.add(sub.dispose)
```

Keep Rx in the VM layer (it is tk-free); always dispose subscriptions when the view is
destroyed by adding `sub.dispose` to the view's `Bindings` bag.
