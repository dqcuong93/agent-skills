# PyQt / PySide stack pack

Written for: PyQt 5

Desktop UI code is reviewed under `backend` with this pack; `frontend.md` is written for web pages and does not apply to Qt widgets.

## Threads

- [ ] **Widgets on the main thread only**: No `QWidget` method (`setText`, `setValue`, `setEnabled`, `QMessageBox.*`, model edits behind a view) is called from a worker thread or a `threading.Thread`. The worker emits a signal; a slot in the main thread updates the widget. Qt: GUI classes "can only be used from the main thread".
- [ ] **Slots on a `QThread` subclass run in the old thread**: A `QThread` object lives in the thread that created it, so its own slots and `__init__` run there, not in `run()`'s thread. Work meant for the thread is inside `run()`, or on a worker object moved with `moveToThread()`; the moved object has no parent ("the object cannot be moved if it has a parent").
- [ ] **Connect before start**: Every signal of a worker is connected before `start()`; a signal emitted before its `connect` is lost.
- [ ] **No shared mutable state**: Lists, dicts, or objects are not mutated from two threads. Pass copies or immutable values in signal arguments; stop/pause flags are simple attributes read by the worker, or a `threading.Event`.
- [ ] **Cross-thread delete**: A `QObject` owned by another thread is released with `deleteLater()`, never `del` or a direct call from the wrong thread.

## Lifecycle

- [ ] **Finish signal always fires**: A worker's "finished"/"failed" signal is emitted in a `finally` (or every exit path), including stop, pause-then-stop, and exceptions, so the UI never stays in a running state.
- [ ] **Stop wins over pause**: A pause loop checks the stop flag; stopping while paused exits.
- [ ] **One worker at a time**: Starting checks that the previous worker is `None` or not `isRunning()`; a finished worker's reference is dropped or `deleteLater()`d.
- [ ] **Shutdown**: `closeEvent` (or app quit) asks running threads to stop and `wait()`s for them with a bound; no "QThread: Destroyed while thread is still running".
- [ ] **Exceptions in slots kill the app**: Since PyQt 5.5 an unhandled exception in Python code called by Qt (a slot, an event handler, a `paintEvent`) calls `qFatal()` and aborts unless the app installs `sys.excepthook`. A slot that can fail (file I/O, parsing, a missing resource) catches the specific exception and shows a message.

## Signals and connections

- [ ] **Signal signature stable**: Every `emit` passes the arguments the `pyqtSignal(...)` declares, in that order and count. Changing a signal's arguments updates every `connect`ed slot and the tests that assert on it.
- [ ] **Lambda captures**: A `lambda` in `connect` inside a loop binds the loop variable with a default (`lambda _=False, i=i: ...`) or uses `functools.partial`. A lambda that references `self` keeps `self` alive; disconnect or parent the sender.
- [ ] **`clicked` passes `checked`**: A slot connected to `clicked`/`toggled` either accepts the `bool` or is decorated `@pyqtSlot()` so the extra argument does not land in a real parameter.
- [ ] **No duplicate connects**: A `connect` in code that runs more than once (each start, each dialog open) is matched by a `disconnect`, or moved to setup, so a slot does not fire twice.

## State and styling

- [ ] **One place owns control state**: Enabling and disabling buttons for each state (idle, running, paused, done, blocked) goes through one method or state table; other code does not call `setEnabled` on those buttons directly, and a blocking condition (licence, missing config) is re-applied after every state change.
- [ ] **Stylesheet, not per-widget colours**: Colours and fonts live in the app stylesheet with object names or properties; no hex colours in widget code. A rule on a bare `QWidget` selector paints every child, including labels.
- [ ] **Long lists**: A table or list fed one row per item over tens of thousands of items uses a model/view with a cap or batching; `QTableWidget` with an unbounded row count and `scrollToBottom()` per row stalls the UI.

## Packaging (PyInstaller)

- [ ] **Bundled file paths**: Bundled assets are located through one helper that uses `sys._MEIPASS` when frozen and the source directory otherwise; no path relative to the current working directory. User-writable files (config, logs, state) live next to the executable or in a user data directory, not in the bundle.
- [ ] **No console in windowed builds**: With `--noconsole`/`console=False` on Windows, `sys.stdout`, `sys.stderr`, and `sys.stdin` are `None`. No `input()`, no `sys.stdout.write`/`flush` without a check, and `print` is not the only error channel.
- [ ] **Data files and DLLs declared**: Every new asset, font, plugin, or DLL loaded at runtime (`ctypes`, PKCS#11, Qt plugins) is listed in the spec's `datas`/`binaries`; modules imported by string (`importlib`, `__import__`) are in `hiddenimports`.
- [ ] **No `multiprocessing` without `freeze_support()`**: A frozen app that uses `multiprocessing` calls `multiprocessing.freeze_support()` first in the entry point; otherwise it respawns itself. Prefer threads for I/O-bound work.

## Tests

- [ ] **pytest-qt**: Widget tests use `qtbot` (`addWidget`, `waitSignal`, `waitUntil`) instead of `time.sleep` or a manual event loop; a test that needs a signal asserts it with `waitSignal(..., timeout=...)`.
- [ ] **No real dialogs**: `QMessageBox`/`QFileDialog` static calls are monkeypatched in tests so the suite never blocks on a modal.
