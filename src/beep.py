"""Play a short OS sound signal on demand."""

from __future__ import annotations

import logging
import shutil
import subprocess
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

_SOUNDS = (
    Path("/usr/share/sounds/freedesktop/stereo/bell.oga"),
    Path("/usr/share/sounds/freedesktop/stereo/message.oga"),
    Path("/usr/share/sounds/freedesktop/stereo/complete.oga"),
)


def beep() -> None:
    """Emit a short system beep/sound without blocking the caller.

    On Windows uses ``winsound.MessageBeep``. On Linux prefers ``paplay``,
    then ``ffplay``, then the terminal bell. Failures are logged and ignored
    so call sites stay safe.
    """
    try:
        if sys.platform == "win32":
            import winsound

            winsound.MessageBeep(winsound.MB_OK)
            return

        sound = next((path for path in _SOUNDS if path.is_file()), None)
        if sound is not None and shutil.which("paplay"):
            subprocess.Popen(
                ["paplay", str(sound)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        if sound is not None and shutil.which("ffplay"):
            subprocess.Popen(
                ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", str(sound)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return
        print("\a", end="", flush=True)
    except Exception:
        logger.warning("Failed to play beep", exc_info=True)
