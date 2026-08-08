# """DEPRECATED"""

# from __future__ import annotations

# from collections.abc import Callable
# from contextlib import AbstractContextManager
# from typing import Any, Self

# from pynput import keyboard


# def _normalize_hotkey(hotkey: str) -> str:
#     """Normalize user input like ``F8`` / ``ctrl+shift+q`` to pynput form."""
#     text = hotkey.strip().lower().replace(" ", "")
#     if not text:
#         raise ValueError("hotkey must not be empty")

#     parts = [p for p in text.replace("-", "+").split("+") if p]
#     mapped: list[str] = []
#     for part in parts:
#         if part.startswith("<") and part.endswith(">"):
#             mapped.append(part)
#             continue
#         if len(part) == 1:
#             mapped.append(part)
#             continue
#         mapped.append(f"<{part}>")
#     return "+".join(mapped)


# class GlobalStopHotkey(AbstractContextManager["GlobalStopHotkey"]):
#     """Listen for a global hotkey and invoke a callback (works without focus)."""

#     def __init__(self, hotkey: str, on_stop: Callable[[], None]) -> None:
#         self.hotkey = hotkey
#         self._normalized = _normalize_hotkey(hotkey)
#         self._on_stop = on_stop
#         self._listener: Any = None

#     def __enter__(self) -> Self:
#         def _handle() -> None:
#             self._on_stop()

#         self._listener = keyboard.GlobalHotKeys({self._normalized: _handle})
#         self._listener.start()
#         return self

#     def __exit__(self, *exc: object) -> None:
#         if self._listener is not None:
#             self._listener.stop()
#             self._listener = None
