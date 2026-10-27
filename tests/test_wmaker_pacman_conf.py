"""O pacman.conf da edição wmaker é o shared/pacman.conf mais o IgnorePkg do
windowmaker (o pamac 11.99 trocava o windowmaker do Big WindowMaker pelo do
extra e removia a sessão). Qualquer outra diferença é um esquecimento: as
mudanças do shared têm de chegar aqui também."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared" / "pacman.conf"
WMAKER = ROOT / "bigcommunity" / "wmaker" / "root-overlay" / "etc" / "pacman.conf"


def _sem_ignorepkg(texto):
    linhas = texto.splitlines()
    saida, pular = [], False
    for linha in linhas:
        if linha.startswith("# Big WindowMaker: o windowmaker instalado"):
            pular = True
        if pular:
            if linha.startswith("IgnorePkg"):
                saida.append("#IgnorePkg   =")
                pular = False
            continue
        saida.append(linha)
    return saida


def test_wmaker_ignora_windowmaker():
    assert not WMAKER.is_symlink()
    linhas = [l.split("#", 1)[0].strip() for l in WMAKER.read_text().splitlines()]
    assert "IgnorePkg   = windowmaker".split() == next(
        l.split() for l in linhas if l.startswith("IgnorePkg"))


def test_wmaker_igual_ao_shared_fora_o_ignorepkg():
    assert _sem_ignorepkg(WMAKER.read_text()) == SHARED.read_text().splitlines()
