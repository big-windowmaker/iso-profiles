#!/usr/bin/env bash
# GRUB da ISO live da edição Big WindowMaker: a primeira entrada diz
# "Big WindowMaker" em vez de "BigCommunity".
#
# Gera, a partir do shared/ (que vale para todas as edições):
#   live-overlay/usr/share/grub/cfg/kernels.cfg   o do shared com a entrada 1 trocada
#   live-overlay/usr/share/grub/locales/bigcommunity/*.mo
#       os catálogos do shared/grub-i18n/po com a tradução da entrada nova
#       (a de "BigCommunity" com o nome trocado)
#
# Rode de novo sempre que o shared mudar; tests/test_wmaker_grub_nome.py
# reprova quando os arquivos ficam desatualizados.
set -euo pipefail

here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
root=$(cd -- "${here}/../../.." && pwd)
shared_cfg="${root}/shared/live-overlay/usr/share/grub/cfg/kernels.cfg"
po_dir="${root}/shared/grub-i18n/po"
linguas="${root}/shared/grub-i18n/LINGUAS"
overlay="${here}/../live-overlay/usr/share/grub"

old='1 - Start BigCommunity (recommended)'
new='1 - Start Big WindowMaker (recommended)'

grep -qF "\$\"${old}\"" "${shared_cfg}" || {
    echo "a entrada \"${old}\" não está mais no ${shared_cfg}" >&2
    exit 1
}

cfg="${overlay}/cfg/kernels.cfg"
rm -f "${cfg}"
sed "s/\$\"${old}\"/\$\"${new}\"/" "${shared_cfg}" >"${cfg}"

# locales/ era um link para o do shared: sem desfazer o link, o rm -rf
# abaixo apagaria os catálogos de todas as edições.
[[ -L "${overlay}/locales" ]] && rm -f "${overlay}/locales"
mo_dir="${overlay}/locales/bigcommunity"
case $(realpath -m "${mo_dir}") in
"${root}/shared/"*) echo "recusando escrever no shared: ${mo_dir}" >&2; exit 1 ;;
esac
rm -rf "${mo_dir}"
mkdir -p "${mo_dir}"
tmp=$(mktemp -d)
trap 'rm -rf "${tmp}"' EXIT
for locale in $(<"${linguas}"); do
    # msgid e msgstr da entrada 1 com o nome da edição; o resto, igual.
    python3 -I - "${po_dir}/${locale}.po" "${tmp}/${locale}.po" "${old}" "${new}" <<'EOF'
import sys
src, dst, old, new = sys.argv[1:]
lines = open(src, encoding="utf-8").read().split("\n")
out, trocar = [], False
for line in lines:
    if line == f'msgid "{old}"':
        line, trocar = f'msgid "{new}"', True
    elif trocar and line.startswith("msgstr "):
        line, trocar = line.replace("BigCommunity", "Big WindowMaker"), False
    out.append(line)
open(dst, "w", encoding="utf-8").write("\n".join(out))
EOF
    msgfmt --check "${tmp}/${locale}.po" --output-file="${mo_dir}/${locale}.mo"
done
echo "kernels.cfg e $(ls "${mo_dir}" | wc -l) catálogos gerados em ${overlay}"
