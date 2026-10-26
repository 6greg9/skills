"""Load port screen: View + binder + preview. No model/comms imports here.

Unthemed version of the screen-module convention; loadport_themed.py is the same screen built
with the design-system theme.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.mvvm import (Bindings, Command, Observable, UiDispatcher, bind_command, bind_entry,
                      bind_grid_visible, bind_text, computed)


# ---- View: layout only ----
class LoadPortView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, padding=12)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Carrier ID").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_carrier = ttk.Entry(self)
        self.ent_carrier.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(self, text="State").grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_state = ttk.Label(self, text="-")
        self.lbl_state.grid(row=1, column=1, sticky="w", pady=4)
        self.lbl_alarm = ttk.Label(self, text="")
        self.lbl_alarm.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
        self.btn_load = ttk.Button(self, text="Load")
        self.btn_load.grid(row=3, column=1, sticky="e", pady=(12, 0))


# ---- ViewModel contract (the real VM lives in app/viewmodels; this is the shape) ----
class LoadPortVM:
    def __init__(self, load=lambda cid: None):
        self.carrier_id = Observable("")
        self.state = Observable("READY_TO_LOAD")
        self.e84_ready = Observable(False)
        self.alarm = Observable("")
        self.has_alarm = computed(bool, self.alarm)
        can = computed(lambda c, r, a: len(c) >= 6 and r and not a,
                       self.carrier_id, self.e84_ready, self.alarm)
        self.load = Command(lambda: load(self.carrier_id.value), can)


# ---- Binder ----
def bind_loadport(view: LoadPortView, vm: LoadPortVM, ui: UiDispatcher) -> Bindings:
    b = Bindings(view)
    b.add(bind_entry(view.ent_carrier, vm.carrier_id, ui))
    b.add(bind_text(view.lbl_state, vm.state, ui))
    b.add(bind_text(view.lbl_alarm, vm.alarm, ui))
    b.add(bind_grid_visible(view.lbl_alarm, vm.has_alarm, ui))
    b.add(bind_command(view.btn_load, vm.load, ui))
    return b


# ---- Preview contract for tools/snap_view.py ----
def preview(master, ui):
    view, vm = LoadPortView(master), LoadPortVM()
    bind_loadport(view, vm, ui)

    def ready():
        vm.carrier_id.value, vm.e84_ready.value = "FOUP-000123", True

    def loading():
        ready()
        vm.state.value = "TRANSFER_BLOCKED"

    def alarm():
        ready()
        vm.alarm.value = "E84 TP3 timeout: carrier not removed from load port"

    def long_text():
        vm.carrier_id.value = "X" * 60
        vm.state.value = "WAITING_FOR_HOST_ID_VERIFICATION_LONG_STATE_NAME"
    return view, {"empty": lambda: None, "ready": ready, "loading": loading, "alarm": alarm,
                  "long_text": long_text}
