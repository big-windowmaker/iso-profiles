"""Programs without the session environment keep the Window Maker look.

pkexec and sudo start root programs (GParted, Timeshift) with a clean
environment: no GTK_THEME and no QT_STYLE_OVERRIDE from the Big WindowMaker
session. GTK reads /etc/gtk-3.0 and /etc/gtk-4.0 when the user (here root)
has no settings.ini of its own, and Kvantum reads /etc/xdg/Kvantum when the
user has no kvantum.kvconfig. Only the wmaker edition ships them.
"""

from __future__ import annotations

import configparser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WMAKER = ROOT / "bigcommunity/wmaker"
OVERLAY = WMAKER / "desktop-overlay"


def _packages(path: Path) -> set[str]:
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line.split()[-1] if line.startswith(">") else line.split()[0])
    return names


def _ini(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser()
    parser.read_string(path.read_text(encoding="utf-8"))
    return parser


def test_gtk_system_settings_use_onestepback() -> None:
    for version in ("gtk-3.0", "gtk-4.0"):
        settings = _ini(OVERLAY / "etc" / version / "settings.ini")
        assert settings["Settings"]["gtk-theme-name"] == "OneStepBack"
        # Only the theme: icons, fonts and dark preference stay as they were.
        assert list(settings["Settings"]) == ["gtk-theme-name"]


def test_kvantum_system_default_is_qtstep() -> None:
    settings = _ini(OVERLAY / "etc/xdg/Kvantum/kvantum.kvconfig")
    assert settings["General"]["theme"] == "QTStepOpenStep"


def test_theme_packages_are_in_the_edition() -> None:
    packages = _packages(WMAKER / "Packages-Desktop")
    assert {"onestepback-gtk-theme", "qtstep-kvantum", "kvantum-qt5"} <= packages


def test_nothing_is_written_into_root_home() -> None:
    # /root is 0750; an overlay directory would bring the checkout's mode.
    for overlay in ("root-overlay", "desktop-overlay", "live-overlay"):
        assert not (WMAKER / overlay / "root").exists()
