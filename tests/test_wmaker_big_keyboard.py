"""Big WindowMaker ships the Big WM Virtual Keyboard (big-keyboard).

Its virtual gamepad needs /dev/uinput for the active-seat user, which the
uaccess rule of game-devices-udev gives; both must be in the edition.
"""

from __future__ import annotations

from pathlib import Path

PACKAGES = Path(__file__).resolve().parent.parent / "bigcommunity/wmaker/Packages-Desktop"


def _names() -> set[str]:
    names = set()
    for line in PACKAGES.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line.split()[-1] if line.startswith(">") else line.split()[0])
    return names


def test_big_keyboard_and_its_uinput_rule_are_installed() -> None:
    names = _names()
    assert "big-keyboard" in names
    assert "game-devices-udev" in names
