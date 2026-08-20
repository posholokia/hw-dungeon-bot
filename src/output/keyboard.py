from pynput.keyboard import Controller, Key


class KeyBoardOutput:
    def __init__(self) -> None:
        self._keyboard = Controller()

    def tap_f5(self) -> None:
        self._keyboard.tap(Key.f5)
