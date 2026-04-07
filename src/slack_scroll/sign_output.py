"""Sign output abstractions for different modes."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SignOutput(ABC):
    """Abstract base class for sign output implementations."""

    @abstractmethod
    def begin_message(self, reset: bool = False) -> None:
        """Begin a new message on the sign."""

    @abstractmethod
    def end_message(self) -> None:
        """End the current message."""

    @abstractmethod
    def begin_file(self, file_id: int) -> None:
        """Begin a new file on the sign."""

    @abstractmethod
    def end_file(self) -> None:
        """End the current file."""

    @abstractmethod
    def add_run_mode(self, mode: str) -> None:
        """Add a run mode (effect) to the current frame."""

    @abstractmethod
    def add_special(self, special: str) -> None:
        """Add a special command (color, font, etc.)."""

    @abstractmethod
    def add_text(self, text: str) -> None:
        """Add text to the current frame."""

    @abstractmethod
    def end_frame(self) -> None:
        """End the current frame."""


class SerialSignOutput(SignOutput):
    """Real serial output to LED sign."""

    def __init__(self, port: str) -> None:
        from slack_scroll.ledsign2 import LEDSign

        self.sign = LEDSign(port)

    def begin_message(self, reset: bool = False) -> None:
        self.sign.begin_message(reset=reset)

    def end_message(self) -> None:
        self.sign.end_message()

    def begin_file(self, file_id: int) -> None:
        self.sign.begin_file(file_id)

    def end_file(self) -> None:
        self.sign.end_file()

    def add_run_mode(self, mode: str) -> None:
        import slack_scroll.ledsign2 as ledsign2

        effect = getattr(ledsign2, f"EFFECT_{mode}", ledsign2.EFFECT_SCROLL_LEFT)
        self.sign.add_run_mode(effect)

    def add_special(self, special: str) -> None:
        import slack_scroll.ledsign2 as ledsign2

        value = getattr(ledsign2, special, b"")
        self.sign.add_special(value)

    def add_text(self, text: str) -> None:
        self.sign.add_text(text)

    def end_frame(self) -> None:
        self.sign.end_frame()


class ConsoleSignOutput(SignOutput):
    """Console output for development - shows what would be sent to sign."""

    def __init__(self, port: str = "CONSOLE") -> None:
        self.port = port
        self.frame_count = 0
        self.line_count = 0

    def begin_message(self, reset: bool = False) -> None:
        print(f"\n[CONSOLE] Beginning message (reset={reset})")
        self.frame_count = 0
        self.line_count = 0

    def end_message(self) -> None:
        print(f"[CONSOLE] Ending message ({self.frame_count} frames, {self.line_count} lines)")

    def begin_file(self, file_id: int) -> None:
        print(f"[CONSOLE] Beginning file {file_id}")

    def end_file(self) -> None:
        print("[CONSOLE] Ending file")

    def add_run_mode(self, mode: str) -> None:
        print(f"  [EFFECT] {mode}")

    def add_special(self, special: str) -> None:
        print(f"  [SPECIAL] {special}")

    def add_text(self, text: str) -> None:
        safe_text = text.encode("ascii", errors="replace").decode("ascii")
        print(f'  [TEXT] "{safe_text}"')
        self.line_count += 1

    def end_frame(self) -> None:
        self.frame_count += 1
        print(f"  [END FRAME #{self.frame_count}]")


class TestSignOutput(SignOutput):
    """Test output that records all operations for verification."""

    def __init__(self) -> None:
        self.operations: list[tuple[str, dict[str, Any]]] = []
        self.frame_count = 0

    def begin_message(self, reset: bool = False) -> None:
        self.operations.append(("begin_message", {"reset": reset}))

    def end_message(self) -> None:
        self.operations.append(("end_message", {}))

    def begin_file(self, file_id: int) -> None:
        self.operations.append(("begin_file", {"file_id": file_id}))

    def end_file(self) -> None:
        self.operations.append(("end_file", {}))

    def add_run_mode(self, mode: str) -> None:
        self.operations.append(("add_run_mode", {"mode": mode}))

    def add_special(self, special: str) -> None:
        self.operations.append(("add_special", {"special": special}))

    def add_text(self, text: str) -> None:
        self.operations.append(("add_text", {"text": text}))

    def end_frame(self) -> None:
        self.frame_count += 1
        self.operations.append(("end_frame", {"frame": self.frame_count}))

    def get_operations(self) -> list[tuple[str, dict[str, Any]]]:
        return self.operations.copy()

    def clear(self) -> None:
        self.operations = []
        self.frame_count = 0
