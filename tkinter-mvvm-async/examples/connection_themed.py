"""Connection screen built with the design-token theme (app/theme.py + app/design/tokens.json).

Same contract as connection.py. What changes under a theme: style names instead of colors and
fonts, theme.px() instead of literal paddings, and state -> style through bind_style.
The app stores the Theme on the root at startup (root.theme = apply_theme(...)); so does
tools/snap_view.py when app/design/tokens.json exists.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.mvvm import (Bindings, Command, Observable, UiDispatcher, bind_command, bind_entry,
                      bind_grid_visible, bind_style, bind_text, computed)

# Connection state -> style. In a real app this table sits next to the state enum.
CONNECTION_STATE_STYLE = {
    "DISCONNECTED": "StateIdle.TLabel",
    "CONNECTING": "StateActive.TLabel",
    "CONNECTED": "StateDone.TLabel",
    "ERROR": "StateAlarm.TLabel",
}


# ---- View: layout only; every color, font and spacing comes from the theme ----
class ConnectionView(ttk.Frame):
    def __init__(self, master: tk.Misc, theme):
        sp = theme.px
        super().__init__(master, style="Panel.TFrame", padding=sp("space-3"))
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Connection", style="Panel.Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, sp("space-2")))
        ttk.Label(self, text="Address", style="Panel.TLabel").grid(
            row=1, column=0, sticky="w", padx=(0, sp("space-3")), pady=sp("space-1"))
        self.ent_address = ttk.Entry(self, font=theme.font("id"))
        self.ent_address.grid(row=1, column=1, sticky="ew", pady=sp("space-1"))
        ttk.Label(self, text="State", style="Panel.TLabel").grid(
            row=2, column=0, sticky="w", padx=(0, sp("space-3")), pady=sp("space-1"))
        self.lbl_state = ttk.Label(self, text="-", style="StateIdle.TLabel")
        self.lbl_state.grid(row=2, column=1, sticky="w", pady=sp("space-1"))
        self.lbl_error = ttk.Label(self, text="", style="AlarmHigh.TLabel", anchor="w")
        self.lbl_error.grid(row=3, column=0, columnspan=2, sticky="ew", pady=sp("space-1"))
        self.btn_connect = ttk.Button(self, text="Connect")
        self.btn_connect.grid(row=4, column=1, sticky="e", pady=(sp("space-3"), 0))


# ---- ViewModel contract (identical to the unthemed screen: the VM knows nothing of styles) ----
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
    b.add(bind_style(view.lbl_state, vm.state, ui,
                     lambda s: CONNECTION_STATE_STYLE.get(s, "StateIdle.TLabel")))
    # A colored fill always carries a text label too, never color alone.
    b.add(bind_text(view.lbl_error, vm.error, ui, fmt=lambda e: f"ERROR  {e}" if e else ""))
    b.add(bind_grid_visible(view.lbl_error, vm.has_error, ui))
    b.add(bind_command(view.btn_connect, vm.connect, ui))
    return b


# ---- Preview contract for tools/snap_view.py ----
def preview(master, ui):
    theme = getattr(master, "theme", None)
    if theme is None:
        raise RuntimeError("needs the theme: put tokens at app/design/tokens.json (snap_view --tokens)")
    view, vm = ConnectionView(master, theme), ConnectionVM()
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
