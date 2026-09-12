from __future__ import annotations

from threading import Event

from pynput.keyboard import Key, KeyCode, Listener

# Физическая клавиша Q (US/PC): Windows VK_Q. Не зависит от раскладки.
_VK_Q = 0x51
_X11_Q = 24
_CTRL_KEYS = {Key.ctrl, Key.ctrl_l, Key.ctrl_r}


class CtrlQListener:
    """Глобальный слушатель Ctrl+Q. Срабатывает по физической Q в любой раскладке."""

    def listen(self, event: Event) -> None:
        ctrl_down = False

        def on_press(key: Key | KeyCode | None) -> bool | None:
            nonlocal ctrl_down
            if key is None:
                return None
            if key in _CTRL_KEYS:
                ctrl_down = True
                return None
            if ctrl_down and _is_q(key):
                event.set()
                return False
            return None

        def on_release(key: Key | KeyCode | None) -> None:
            nonlocal ctrl_down
            if key in _CTRL_KEYS:
                ctrl_down = False

        listener = Listener(on_press=on_press, on_release=on_release)
        listener.daemon = True  # type: ignore[attr-defined]
        listener.start()


def _is_q(key: Key | KeyCode) -> bool:
    if not isinstance(key, KeyCode):
        return False
    if key.vk in {_VK_Q, _X11_Q}:
        return True
    # При зажатом Ctrl символ часто приходит как ASCII DC1, а не как "q".
    return key.char in {"q", "Q", "\x11"}
