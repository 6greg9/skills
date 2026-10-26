"""Load port screen built with the design-system theme (app/theme.py + app/design/tokens.json).

Same contract as loadport.py. What changes under a theme: style names instead of colors and
fonts, theme.px() instead of literal paddings, and state -> style through bind_style.
The app stores the Theme on the root at startup (root.theme = apply_theme(...)); so does
tools/snap_view.py when app/design/tokens.json exists.
"""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from app.mvvm import (Bindings, Command, Observable, UiDispatcher, bind_command, bind_entry,
                      bind_grid_visible, bind_style, bind_text, computed)

# E87 transfer state -> style. In a real app this table sits next to the state enum.
TRANSFER_STATE_STYLE = {
    "READY_TO_LOAD": "StateIdle.TLabel",
    "TRANSFER_BLOCKED": "StateActive.TLabel",
    "READY_TO_UNLOAD": "StateDone.TLabel",
}


# ---- View: layout only; every color, font and spacing comes from the theme ----
class LoadPortView(ttk.Frame):
    def __init__(self, master: tk.Misc, theme):
        sp = theme.px
        super().__init__(master, style="Panel.TFrame", padding=sp("space-3"))
        self.columnconfigure(1, weight=1)
        ttk.Label(self, text="Load Port 1", style="Panel.Section.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, sp("space-2")))
        ttk.Label(self, text="Carrier ID", style="Panel.TLabel").grid(
            row=1, column=0, sticky="w", padx=(0, sp("space-3")), pady=sp("space-1"))
        self.ent_carrier = ttk.Entry(self, font=theme.font("id"))
        self.ent_carrier.grid(row=1, column=1, sticky="ew", pady=sp("space-1"))
        ttk.Label(self, text="State", style="Panel.TLabel").grid(
            row=2, column=0, sticky="w", padx=(0, sp("space-3")), pady=sp("space-1"))
        self.lbl_state = ttk.Label(self, text="-", style="StateIdle.TLabel")
        self.lbl_state.grid(row=2, column=1, sticky="w", pady=sp("space-1"))
        self.lbl_alarm = ttk.Label(self, text="", style="AlarmHigh.TLabel", anchor="w")
        self.lbl_alarm.grid(row=3, column=0, columnspan=2, sticky="ew", pady=sp("space-1"))
        self.btn_load = ttk.Button(self, text="Load")
        self.btn_load.grid(row=4, column=1, sticky="e", pady=(sp("space-3"), 0))


# ---- ViewModel contract (identical to the unthemed screen: the VM knows nothing of styles) ----
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
    b.add(bind_style(view.lbl_state, vm.state, ui,
                     lambda s: TRANSFER_STATE_STYLE.get(s, "StateIdle.TLabel")))
    b.add(bind_text(view.lbl_alarm, vm.alarm, ui, fmt=lambda a: f"P2  {a}" if a else ""))
    b.add(bind_grid_visible(view.lbl_alarm, vm.has_alarm, ui))
    b.add(bind_command(view.btn_load, vm.load, ui))
    return b


# ---- Preview contract for tools/snap_view.py ----
def preview(master, ui):
    theme = getattr(master, "theme", None)
    if theme is None:
        raise RuntimeError("needs the theme: put tokens at app/design/tokens.json (snap_view --tokens)")
    view, vm = LoadPortView(master, theme), LoadPortVM()
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
