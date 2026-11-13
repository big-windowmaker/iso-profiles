"""The live session logs in through wdm, as the installed system does.

Big WindowMaker's ISO uses wdm (WINGs Display Manager) as its login screen:
profile.conf names it (manjaro-tools enables wdm.service in the image) and the
live user is bigwindowmaker, password big. wdm has no automatic login: the
screen preselects the user (user list) and the live session "Big WindowMaker
Live" (startbiglive: setup assistant, then the desktop), and its help (F1)
shows the credentials. The live overlay holds the live-only wdm configuration;
the installed system keeps the one of the wdm package.
"""

from __future__ import annotations

import configparser
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WMAKER = ROOT / "bigcommunity/wmaker"
LIVE = WMAKER / "live-overlay"


def _profile() -> dict[str, str]:
    values = {}
    for line in (WMAKER / "profile.conf").read_text(encoding="utf-8").splitlines():
        m = re.match(r'^([a-z_]+)="?([^"]*)"?$', line.strip())
        if m:
            values[m.group(1)] = m.group(2)
    return values


def _packages(path: Path) -> set[str]:
    names = set()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.split("#", 1)[0].strip()
        if line:
            names.add(line.split()[-1] if line.startswith(">") else line.split()[0])
    return names


def _resources(path: Path) -> dict[str, str]:
    res = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("!") or ":" not in line:
            continue
        key, value = line.split(":", 1)
        res[key.strip()] = value.strip()
    return res


def test_live_login_is_wdm_with_the_live_user() -> None:
    profile = _profile()
    assert profile["displaymanager"] == "wdm"
    assert profile["username"] == "bigwindowmaker"
    assert profile["password"] == "big"
    # LightDM stays installed (Calamares' displaymanager module needs one it
    # knows) but is not the live login any more.
    assert {"wdm", "lightdm"} <= _packages(WMAKER / "Packages-Desktop")
    assert not (LIVE / "etc/lightdm").exists()


def test_live_wdm_preselects_the_live_session_and_shows_the_credentials() -> None:
    res = _resources(LIVE / "etc/wdm/wdm-config")
    assert res["DisplayManager*wdmDefaultSession"] == "x11/big-wm-live"
    assert res["DisplayManager*wdmUserList"] == "true"
    help_file = res["DisplayManager*wdmHelpFile"]
    assert help_file == "/etc/wdm/live-help.txt"
    text = (LIVE / help_file.lstrip("/")).read_text(encoding="utf-8")
    assert "bigwindowmaker" in text and "big" in text
    # The rest is the wdm package's: sessions from the .desktop files,
    # Wayland sessions, the session the user chose last.
    for key in ("wdmXSessionDirs", "wdmWaylandSessionDirs", "wdmWaylandSession",
                "wdmSessionStateDir", "wdmLogin", "session"):
        assert res[f"DisplayManager*{key}"], key


def test_the_live_session_runs_the_assistant_and_is_listed() -> None:
    desktop = configparser.ConfigParser(interpolation=None)
    desktop.optionxform = str
    desktop.read_string((LIVE / "usr/share/xsessions/big-wm-live.desktop").read_text(encoding="utf-8"))
    entry = desktop["Desktop Entry"]
    assert entry["Exec"] == "/usr/bin/startbiglive"
    # wdm hides a session whose TryExec is missing (the generic livecd.desktop
    # of biglinux-livecd asks for startplasma-x11, absent in this edition).
    assert entry["TryExec"] == "/usr/bin/startbiglive"


def test_no_old_live_user_left_in_the_edition() -> None:
    for path in WMAKER.rglob("*"):
        if path.is_symlink() or not path.is_file() or path.suffix in {".mo", ".png", ".jpg", ".pf2", ".bin"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        assert not re.search(r"\b(autologin-user|username|AutomaticLogin)=\"?community\b", text), path
