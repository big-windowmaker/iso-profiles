"""GRUB da live da edição wmaker: a entrada 1 diz "Big WindowMaker".

O kernels.cfg e os catálogos da edição são gerados do shared/ por
bigcommunity/wmaker/grub-i18n/gerar.sh. Estes testes reprovam quando o
shared muda e a edição fica para trás (rode o gerar.sh de novo).
"""
import gettext
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
SHARED = ROOT / "shared" / "live-overlay" / "usr" / "share" / "grub"
WMAKER = ROOT / "bigcommunity" / "wmaker" / "live-overlay" / "usr" / "share" / "grub"
LINGUAS = (ROOT / "shared" / "grub-i18n" / "LINGUAS").read_text().split()
OLD = "1 - Start BigCommunity (recommended)"
NEW = "1 - Start Big WindowMaker (recommended)"


def test_kernels_cfg_igual_ao_shared_fora_a_entrada_1():
    edicao = WMAKER / "cfg" / "kernels.cfg"
    assert not edicao.is_symlink()
    esperado = (SHARED / "cfg" / "kernels.cfg").read_text(encoding="utf-8")
    assert f'$"{OLD}"' in esperado
    assert edicao.read_text(encoding="utf-8") == esperado.replace(f'$"{OLD}"', f'$"{NEW}"')


def _catalogo(base, lingua):
    with open(base / "locales" / "bigcommunity" / f"{lingua}.mo", "rb") as f:
        return gettext.GNUTranslations(f)._catalog


@pytest.mark.parametrize("lingua", LINGUAS)
def test_catalogos_em_dia_com_o_shared(lingua):
    assert not (WMAKER / "locales").is_symlink()
    shared = _catalogo(SHARED, lingua)
    edicao = _catalogo(WMAKER, lingua)
    assert NEW in edicao and OLD not in edicao
    assert "BigCommunity" not in edicao[NEW]
    if shared.get(OLD):
        assert edicao[NEW] == shared[OLD].replace("BigCommunity", "Big WindowMaker")
    resto_shared = {k: v for k, v in shared.items() if k != OLD}
    resto_edicao = {k: v for k, v in edicao.items() if k != NEW}
    assert resto_edicao == resto_shared
