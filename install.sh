#!/usr/bin/env bash
# ============================================================
#   ARASAKA BRIDGE // instalador para Zorin OS (17 / 18)
#   Programas Windows no Linux (Wine) + Roblox Studio (Vinegar)
#
#   Uso:  ./install.sh [opcoes]        (NAO rode com sudo)
#     --sem-wine       nao instala Wine / Winetricks
#     --sem-vinegar    nao instala o Vinegar (Roblox Studio)
#     --nao-associar   nao abre .exe/.msi com o Bridge por padrao
#     -y               nao pede confirmacao
# ============================================================
set -uo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
APP_ID=arasaka-bridge
DATA="${XDG_DATA_HOME:-$HOME/.local/share}/$APP_ID"
BIN="$HOME/.local/bin"
APPS="${XDG_DATA_HOME:-$HOME/.local/share}/applications"
ICONS="${XDG_DATA_HOME:-$HOME/.local/share}/icons/hicolor/scalable/apps"

DO_WINE=1 DO_VINEGAR=1 DO_MIME=1 YES=0
for a in "$@"; do
  case "$a" in
    --sem-wine) DO_WINE=0 ;;
    --sem-vinegar) DO_VINEGAR=0 ;;
    --nao-associar) DO_MIME=0 ;;
    -y|--yes) YES=1 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) echo "Opcao desconhecida: $a"; exit 1 ;;
  esac
done

R=$'\e[38;2;227;18;31m'; RH=$'\e[38;2;255;59;71m'; W=$'\e[38;2;236;236;240m'
G=$'\e[38;2;120;120;130m'; B=$'\e[1m'; N=$'\e[0m'
STEP=0
step() { STEP=$((STEP + 1)); printf '\n%s%s[%02d]%s %s%s%s\n' "$R" "$B" "$STEP" "$N" "$W$B" "$*" "$N"; }
ok()   { printf '     %s■%s %s\n' "$R" "$N" "$*"; }
info() { printf '     %s›%s %s\n' "$R" "$N" "$*"; }
warn() { printf '     %s!! %s%s\n' "$RH" "$*" "$N"; }
die()  { printf '\n%s!! %s%s\n' "$RH" "$*" "$N"; exit 1; }

printf '\n%s%s   A R A S A K A   B R I D G E%s\n' "$R" "$B" "$N"
printf '   %sProgramas Windows e Roblox Studio no Zorin OS%s\n' "$G" "$N"

[ "$EUID" -eq 0 ] && die "Rode como seu usuario normal (sem sudo): ./install.sh"
[ -f "$DIR/arasaka_bridge/app.py" ] || die "Arquivos do app nao encontrados em $DIR"
command -v python3 >/dev/null || die "python3 nao encontrado"
python3 -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)' || die "Precisa de Python 3.9 ou mais novo"

if [ "$YES" -eq 0 ]; then
  printf '\n   Vai instalar: o app (Python + Qt)'
  [ "$DO_WINE" -eq 1 ] && printf ', Wine + Winetricks'
  [ "$DO_VINEGAR" -eq 1 ] && printf ', Flatpak + Vinegar (Roblox Studio)'
  printf '.\n   %sContinuar? [s/N] %s' "$W" "$N"
  read -r r
  case "$r" in s|S|y|Y|sim|SIM) ;; *) echo "Cancelado."; exit 0 ;; esac
fi

# ---------------------------------------------------------------- pacotes do sistema
step "Pacotes do sistema"
sudo -v || die "sudo necessario"
PKGS=(python3-venv python3-pip libxcb-cursor0 libxkbcommon-x11-0 libxcb-icccm4 libxcb-keysyms1
      libxcb-image0 libxcb-render-util0 libxcb-xinerama0 libxcb-shape0 libegl1 xdg-utils desktop-file-utils)
[ "$DO_VINEGAR" -eq 1 ] && PKGS+=(flatpak)
if [ "$DO_WINE" -eq 1 ]; then
  if ! dpkg --print-foreign-architectures | grep -qx i386; then
    info "ativando arquitetura i386 (programas 32-bit)"
    sudo dpkg --add-architecture i386
  fi
  PKGS+=(wine64 wine32:i386 winetricks)
fi
MISSING=()
for p in "${PKGS[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || MISSING+=("$p"); done
if [ ${#MISSING[@]} -gt 0 ]; then
  info "instalando: ${MISSING[*]}"
  sudo apt-get update -qq || warn "apt update falhou"
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq --install-recommends "${MISSING[@]}" \
    || warn "alguns pacotes falharam; o app mostra o que falta na aba PAINEL"
else
  ok "tudo ja instalado"
fi
command -v wine >/dev/null && ok "$(wine --version 2>/dev/null)"

# ---------------------------------------------------------------- app
step "Ambiente Python (PySide6 / Qt 6)"
mkdir -p "$DATA"
if [ ! -x "$DATA/venv/bin/python" ]; then
  python3 -m venv "$DATA/venv" || die "falha ao criar o venv (falta python3-venv?)"
fi
"$DATA/venv/bin/python" -m pip install -q --upgrade pip >/dev/null 2>&1
info "baixando PySide6 (~120 MB na primeira vez)..."
"$DATA/venv/bin/python" -m pip install -q --upgrade "PySide6-Essentials>=6.5" || die "falha ao instalar PySide6"
ok "PySide6 $("$DATA/venv/bin/python" -c 'import PySide6; print(PySide6.__version__)')"

step "Arquivos do app"
rm -rf "$DATA/app"
mkdir -p "$DATA/app"
cp -r "$DIR/arasaka_bridge" "$DATA/app/"
find "$DATA/app" -name '__pycache__' -prune -exec rm -rf {} +
mkdir -p "$BIN" "$APPS" "$ICONS"
cat > "$BIN/$APP_ID" <<EOF
#!/bin/sh
# ARASAKA BRIDGE launcher
export PYTHONPATH="$DATA/app\${PYTHONPATH:+:\$PYTHONPATH}"
exec "$DATA/venv/bin/python" -m arasaka_bridge "\$@"
EOF
chmod +x "$BIN/$APP_ID"
cp "$DIR/arasaka_bridge/assets/arasaka-bridge.svg" "$ICONS/$APP_ID.svg"
ok "comando: $BIN/$APP_ID"

cat > "$APPS/$APP_ID.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=Arasaka Bridge
GenericName=Programas Windows
Comment=Rode programas Windows e o Roblox Studio no Linux
Exec="$BIN/$APP_ID" %f
Icon=$APP_ID
Terminal=false
Categories=Utility;System;Emulator;
Keywords=wine;windows;exe;roblox;studio;vinegar;arasaka;
MimeType=application/x-ms-dos-executable;application/x-msdownload;application/vnd.microsoft.portable-executable;application/x-msi;application/x-ms-shortcut;application/x-bat;
StartupWMClass=arasaka-bridge
Actions=studio;

[Desktop Action studio]
Name=Abrir Roblox Studio
Exec="$BIN/$APP_ID" --studio
EOF
update-desktop-database -q "$APPS" 2>/dev/null
ok "atalho no menu: Arasaka Bridge (botao direito: Abrir Roblox Studio)"

if [ "$DO_MIME" -eq 1 ] && command -v xdg-mime >/dev/null; then
  for m in application/x-ms-dos-executable application/x-msdownload application/vnd.microsoft.portable-executable \
           application/x-msi; do
    xdg-mime default "$APP_ID.desktop" "$m" 2>/dev/null
  done
  ok "duplo clique em .exe/.msi abre no Bridge"
fi

# ---------------------------------------------------------------- Roblox Studio
if [ "$DO_VINEGAR" -eq 1 ]; then
  step "Roblox Studio (Vinegar via Flathub)"
  if command -v flatpak >/dev/null; then
    flatpak remote-add --user --if-not-exists flathub https://dl.flathub.org/repo/flathub.flatpakrepo \
      && ok "Flathub configurado"
    if flatpak info org.vinegarhq.Vinegar >/dev/null 2>&1; then
      ok "Vinegar ja instalado"
    else
      info "instalando Vinegar (pode levar alguns minutos)..."
      flatpak install --user -y --noninteractive flathub org.vinegarhq.Vinegar && ok "Vinegar instalado" \
        || warn "falhou: instale depois pela aba ROBLOX STUDIO do app"
    fi
  else
    warn "flatpak indisponivel; instale o Vinegar depois pela aba ROBLOX STUDIO"
  fi
fi

printf '\n%s%s ■ INSTALACAO CONCLUIDA%s\n' "$R" "$B" "$N"
printf '   %sAbra "Arasaka Bridge" no menu do Zorin (ou rode: arasaka-bridge).%s\n' "$W" "$N"
printf '   %sNa primeira abertura do Roblox Studio o Vinegar baixa o Studio (alguns minutos).%s\n' "$G" "$N"
printf '   %sSe o Flatpak acabou de ser instalado, encerre a sessao e entre de novo.%s\n\n' "$G" "$N"
