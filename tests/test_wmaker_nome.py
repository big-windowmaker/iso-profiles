"""Edição wmaker: o sistema se apresenta como Big WindowMaker, baseado no BigLinux.

O nome vem do pacote big-wm-name (os-release, lsb-release, /etc/issue), no
lugar do bigcommunity-name; o instalador usa o perfil bigwindowmaker do
biglinux-livecd (identidade própria), escolhido pelo marcador da imagem.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WMAKER = ROOT / "bigcommunity" / "wmaker"


def _packages(path: Path) -> set:
    return {line.split()[0] for line in path.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("#")}


def test_big_wm_name_replaces_bigcommunity_name():
    assert "big-wm-name" in _packages(WMAKER / "Packages-Desktop")
    # Packages-Root é o do shared/ (link): a edição tira o bigcommunity-name
    # pelo Root-remove, sem mexer nas outras edições.
    assert (WMAKER / "Packages-Root").is_symlink()
    assert "bigcommunity-name" in _packages(WMAKER / "Root-remove")


def test_installer_profile_marker():
    marker = WMAKER / "live-overlay" / "etc" / "biglinux-livecd" / "profile"
    assert not marker.is_symlink()
    assert marker.read_text(encoding="utf-8") == "bigwindowmaker\n"
    # resolve-profile recusa marcador gravável por outros.
    assert marker.stat().st_mode & 0o022 == 0


def test_live_console_and_hostname():
    issue = WMAKER / "live-overlay" / "etc" / "issue"
    assert not issue.is_symlink()
    text = issue.read_text(encoding="utf-8")
    assert "Big WindowMaker, based on BigLinux Live ISO" in text
    assert "BigCommunity" not in text
    profile = (WMAKER / "profile.conf").read_text(encoding="utf-8")
    assert re.search(r'^hostname="big-windowmaker"$', profile, re.MULTILINE)
