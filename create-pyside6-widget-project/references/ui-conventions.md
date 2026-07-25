# PySide6 UI and View conventions

## Naming contract

For a form named `main_window`:

- Designer source: `views/main_window.ui`
- UI XML class and root object name: `MainWindow`
- Generated module and class: `views/main_window_ui.py`, `Ui_MainWindow`
- Hand-written module and class: `views/view_main_window.py`, `View_MainWindow`

Derive PascalCase directly from the snake_case file stem. Do not preserve historical spelling mistakes.

## Root widget and inheritance

Use the root widget type declared by the `.ui` file:

| Designer root | View declaration |
| --- | --- |
| `QMainWindow` | `class View_Name(QMainWindow, Ui_Name):` |
| `QWidget` | `class View_Name(QWidget, Ui_Name):` |
| `QDialog` | `class View_Name(QDialog, Ui_Name):` |

Put the concrete Qt class first and the generated UI mixin second. In `__init__`, call `super().__init__(parent)` before `self.setupUi(self)`.

## Ownership boundaries

- Edit layout, widgets, visible text, tab order, and static properties only in `.ui`.
- Never edit `*_ui.py`; regenerate it with `uv run python scripts/compile_ui.py`.
- Keep View code limited to signal/slot connections, model attachment, and presentation updates.
- Keep state changes in ViewModels, domain data in Models, and I/O/configuration in Services.
- Do not construct visible widgets or layouts in View code.

## Sidebar and stacked-page shell

- Keep `main_window.ui` limited to the sidebar, navigation list, page title, and empty `QStackedWidget` host.
- Give each page its own `.ui`, generated `Ui_` class, and hand-written `View_` class, such as `dashboard_page.ui` / `Ui_DashboardPage` / `View_DashboardPage`.
- Construct page Views in the application composition root and pass them to `View_MainWindow`; adding an already-constructed page to the stack is composition, not UI construction.
- Keep navigation labels in the Designer-owned sidebar list. Require the number and order of injected pages to match those items.
- Switch pages through `QListWidget.currentRowChanged` and keep the page-title label synchronized with the selected navigation item.

## Adding a form

1. Add `<form_name>.ui` with a supported root widget and matching PascalCase XML class/object name.
2. Add `view_<form_name>.py` with the exact `View_` inheritance contract.
3. Run `scripts/compile_ui.py` to validate and generate `<form_name>_ui.py`.
4. Commit both the `.ui` source and generated Python module.
5. Add an offscreen `pytest-qt` test for important wiring or behavior.
