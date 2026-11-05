"""Connection screen: View + binder + preview. No model/comms imports here.

Unthemed version of the screen-module convention; connection_themed.py is the same screen
built with the design-token theme.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.mvvm import (Bindings, Command, Observable, UiDispatcher, bind_command, bind_entry,
                      bind_grid_visible, bind_text, computed)


# ---- View: layout only ----
class ConnectionView(ttk.Frame):
    def __init__(self, master: tk.Misc):
        super().__init__(master, padding=12)
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Address").grid(row=0, column=0, sticky="w", pady=4)
        self.ent_address = ttk.Entry(self)
        self.ent_address.grid(row=0, column=1, sticky="ew", pady=4)
        ttk.Label(self, text="State").grid(row=1, column=0, sticky="w", pady=4)
        self.lbl_state = ttk.Label(self, text="-")
        self.lbl_state.grid(row=1, column=1, sticky="w", pady=4)
        self.lbl_error = ttk.Label(self, text="")
        self.lbl_error.grid(row=2, column=0, columnspan=2, sticky="ew", pady=4)
        self.btn_connect = ttk.Button(self, text="Connect")
        self.btn_connect.grid(row=3, column=1, sticky="e", pady=(12, 0))


# ---- ViewModel contract (the real VM lives in app/viewmodels; this is the shape) ----
def valid_address(a: str) -> bool:
    host, _, port = a.rpartition(":")
    return bool(host) and port.isdigit()


class ConnectionVM:
    def __init__(self, connect=lambda address: None):
        self.address = Observable("")
        self.state = Observable("DISCONNECTED")
        self.busy = Observable(False)
        self.error = Observable("")
        self.has_error = computed(bool, self.error)
        can = computed(lambda a, b, s: valid_address(a) and not b and s != "CONNECTED",
                       self.address, self.busy, self.state)
        self.connect = Command(lambda: connect(self.address.value), can)


# ---- Binder ----
def bind_connection(view: ConnectionView, vm: ConnectionVM, ui: UiDispatcher) -> Bindings:
    b = Bindings(view)
    b.add(bind_entry(view.ent_address, vm.address, ui))
    b.add(bind_text(view.lbl_state, vm.state, ui))
    b.add(bind_text(view.lbl_error, vm.error, ui))
    b.add(bind_grid_visible(view.lbl_error, vm.has_error, ui))
    b.add(bind_command(view.btn_connect, vm.connect, ui))
    return b


# ---- Preview contract for tools/snap_view.py ----
def preview(master, ui):
    view, vm = ConnectionView(master), ConnectionVM()
    bind_connection(view, vm, ui)

    def ready():
        vm.address.value = "192.168.0.10:5000"

    def connecting():
        ready()
        vm.state.value, vm.busy.value = "CONNECTING", True

    def error():
        ready()
        vm.state.value = "ERROR"
        vm.error.value = "Connection refused by 192.168.0.10:5000 (retry in 5 s)"

    def long_text():
        vm.address.value = "x" * 60 + ":5000"
        vm.state.value = "WAITING_FOR_REMOTE_HANDSHAKE_LONG_STATE_NAME"
    return view, {"empty": lambda: None, "ready": ready, "connecting": connecting,
                  "error": error, "long_text": long_text}
