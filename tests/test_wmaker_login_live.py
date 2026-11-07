"""The live session's login screen looks like Big WindowMaker, not GNOME.

The live session logs in by itself (LightDM autologin into "livecd"); the
greeter shows when the user leaves the session. manjaro-tools rewrites
/etc/lightdm/slick-greeter.conf in the desktop image with the BigCommunity
background (/usr/share/backgrounds/community/lightdm-default.jpg, which this
edition does not ship: the greeter came up black, with the default dark GTK
look) and keeps ours as slick-greeter.conf.bak. The live overlay sits above
that image at boot, so the greeter configuration lives there, next to the
autologin.
"""

from __future__ import annotations

import configparser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WMAKER = ROOT / "bigcommunity/wmaker"
LIGHTDM = WMAKER / "live-overlay/etc/lightdm"


def _ini(path: Path) -> configparser.ConfigParser:
    parser = configparser.ConfigParser(interpolation=None)
    parser.read_string(path.read_text(encoding="utf-8"))
    return parser


def _packages(path: Path) -> set[str]:
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line.split()[-1] if line.startswith(">") else line.split()[0])
    return names


def test_live_autologin_is_kept() -> None:
    seat = _ini(LIGHTDM / "lightdm.conf")["Seat:*"]
    assert seat["autologin-user"] == "community"
    assert seat["autologin-session"] == "livecd"
    assert seat["autologin-user-timeout"] == "0"


def test_live_greeter_is_slick_with_the_big_wm_session() -> None:
    seat = _ini(LIGHTDM / "lightdm.conf")["Seat:*"]
    assert seat["greeter-session"] == "lightdm-slick-greeter"
    # The X11 session of the edition (big-wm.desktop), preselected.
    assert seat["user-session"] == "big-wm"


def test_live_greeter_has_the_big_wm_look() -> None:
    greeter = _ini(LIGHTDM / "slick-greeter.conf")["Greeter"]
    assert greeter["background"] == "/usr/share/backgrounds/big-wm/default.jpg"
    assert "community" not in greeter["background"]
    assert greeter["theme-name"] == "OneStepBack"
    assert greeter["draw-user-backgrounds"] == "false"
    # A PNG of a fixed size: slick-greeter draws the logo at its own size
    # (the scalable SVG covered a third of the screen).
    assert greeter["logo"].endswith("/apps/big-wm.png")
    assert "/64x64/" in greeter["logo"]


def test_greeter_assets_come_from_the_edition_packages() -> None:
    packages = _packages(WMAKER / "Packages-Desktop")
    # big-wm-themes: wallpaper and logo; onestepback-gtk-theme: GTK theme.
    assert {"big-wm-themes", "onestepback-gtk-theme", "lightdm", "lightdm-slick-greeter"} <= packages
