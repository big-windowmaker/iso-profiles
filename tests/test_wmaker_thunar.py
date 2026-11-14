"""Big WindowMaker ships thunar-git (Xfce master) as its file manager.

The package comes from big-windowmaker/packages with the libxfce4ui 4.21 it
needs; it provides and conflicts with thunar, so the plugins below still
resolve and only one Thunar is installed.
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


def test_thunar_git_is_the_only_thunar() -> None:
    names = _names()
    assert "thunar-git" in names
    assert "thunar" not in names
    # plugins and thumbnails keep working on top of it
    assert {"thunar-archive-plugin", "thunar-volman", "tumbler"} <= names
