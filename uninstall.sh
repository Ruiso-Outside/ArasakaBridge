#!/usr/bin/env bash
# ============================================================
#   ARASAKA BRIDGE // desinstalador
#   Uso: ./uninstall.sh          remove o app (mantem seus containers)
#        ./uninstall.sh --tudo   remove tambem containers e configuracoes
#   Wine, Flatpak e Vinegar NAO sao removidos (podem ser usados por outros apps).
# ============================================================
set -uo pipefail
APP_ID=arasaka-bridge
DATA="${XDG_DATA_HOME:-$HOME/.local/share}/$APP_ID"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
R=$'\e[38;2;227;18;31m'; B=$'\e[1m'; N=$'\e[0m'
ok() { printf '   %s■%s %s\n' "$R" "$N" "$*"; }

ALL=0
[ "${1:-}" = "--tudo" ] && ALL=1

rm -f "$HOME/.local/bin/$APP_ID" "$APPS/$APP_ID.desktop" \
      "${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps/$APP_ID.svg" \
      "${XDG_DATA_HOME:-$HOME/.local/share}/icons/Arasaka/scalable/apps/$APP_ID.svg"
rm -rf "$DATA/app" "$DATA/venv"
ok "app removido"

MIMEAPPS="${XDG_CONFIG_HOME:-$HOME/.config}/mimeapps.list"
[ -f "$MIMEAPPS" ] && sed -i "/=$APP_ID.desktop;\?$/d" "$MIMEAPPS" && ok "associacao de .exe/.msi removida"

if [ "$ALL" -eq 1 ]; then
  printf '   Apagar TODOS os containers em %s? [s/N] ' "$DATA/containers"
  read -r r
  case "$r" in
    s|S|sim|SIM)
      rm -f "$APPS/$APP_ID"-*.desktop
      rm -rf "$DATA" "${XDG_CONFIG_HOME:-$HOME/.config}/$APP_ID"
      ok "containers, atalhos e configuracoes removidos" ;;
    *) echo "   containers mantidos" ;;
  esac
else
  printf '   Seus containers continuam em %s\n' "$DATA/containers"
fi
update-desktop-database -q "$APPS" 2>/dev/null
printf '\n%s%s ■ ARASAKA BRIDGE REMOVIDO%s\n\n' "$R" "$B" "$N"
