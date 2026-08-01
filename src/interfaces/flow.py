from typing import Protocol
from threading import Event

from models.dto import State


class IStep(Protocol):
    def execute(self, state: State, stop_event: Event) -> None:
        ...
