"""
ARASAKA BRIDGE // nucleo.

Tudo que nao e interface: configuracao, containers Wine (prefixos),
descoberta de programas, montagem de comandos, checagem do sistema e
integracao com Vinegar (Roblox Studio) via Flatpak.

Os comandos sao devolvidos como objetos `Command`; quem executa e a
interface (QProcess) ou o modo --launch (os.execvpe).
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

APP_ID = "arasaka-bridge"
APP_NAME = "ARASAKA BRIDGE"
VERSION = "1.0.0"

# Modo demonstracao: roda a interface sem Wine (ex.: no Windows, para testes).
DEMO = os.environ.get("ARASAKA_BRIDGE_DEMO") == "1" or sys.platform == "win32"

_home_override = os.environ.get("ARASAKA_BRIDGE_HOME")
HOME = Path(_home_override) if _home_override else Path.home()
if _home_override:
    DATA = HOME / ".local/share" / APP_ID
    CONFIG_DIR = HOME / ".config" / APP_ID
else:
    DATA = Path(os.environ.get("XDG_DATA_HOME", HOME / ".local/share")) / APP_ID
    CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", HOME / ".config")) / APP_ID
PREFIXES = DATA / "containers"
LOGS = DATA / "logs"
APPS_DIR = HOME / ".local/share/applications"

VINEGAR_ID = "org.vinegarhq.Vinegar"
SOBER_ID = "org.vinegarhq.Sober"
FLATHUB_URL = "https://dl.flathub.org/repo/flathub.flatpakrepo"

ASSETS = Path(__file__).resolve().parent / "assets"


# ================================================================ comandos
@dataclass
class Command:
    argv: list
    label: str
    env: dict | None = None      # variaveis extras (somadas ao ambiente atual)
    cwd: str | None = None
    detached: bool = False       # programas do usuario: nao bloqueiam a fila

    def display(self) -> str:
        pre = " ".join(f"{k}={v}" for k, v in (self.env or {}).items() if k.startswith("WINE"))
        return (pre + " " if pre else "") + " ".join(_q(a) for a in self.argv)


def _q(s: str) -> str:
    s = str(s)
    return f'"{s}"' if (" " in s or not s) else s


def demo_command(label: str, lines: list[str], seconds: float = 1.5) -> Command:
    """Processo falso para o modo demonstracao (imprime linhas aos poucos)."""
    code = (
        "import time,sys\n"
        f"lines={lines!r}\n"
        "for l in lines:\n"
        f"    print(l, flush=True); time.sleep({seconds}/max(1,len(lines)))\n"
    )
    return Command([sys.executable, "-c", code], label)


# ================================================================ config
DEFAULTS = {
    "wine": "wine",
    "winetricks": "winetricks",
    "default_container": "",
    "dxvk_new": True,
    "fonts_new": True,
    "esync": True,
    "hide_wine_debug": True,
    "show_console": True,
}


class Config:
    def __init__(self):
        self.path = CONFIG_DIR / "config.json"
        self.data = dict(DEFAULTS)
        try:
            self.data.update(json.loads(self.path.read_text(encoding="utf-8")))
        except Exception:
            pass

    def __getitem__(self, k):
        return self.data.get(k, DEFAULTS.get(k))

    def __setitem__(self, k, v):
        self.data[k] = v
        self.save()

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.data, indent=2, ensure_ascii=False), encoding="utf-8")


# ================================================================ containers
def slugify(name: str) -> str:
    s = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip().lower()).strip("-")
    return s or f"container-{int(time.time())}"


@dataclass
class App:
    name: str
    target: str                  # caminho unix do .exe ou .lnk
    args: str = ""
    icon: str = ""               # nome de icone do tema ou caminho
    source: str = "manual"       # manual | menu

    def key(self) -> str:
        return self.target


SKIP_LNK = re.compile(
    r"uninstall|unins\d|desinstal|remov|readme|leia-?me|help|ajuda|website|site|manual|license|licen|changelog",
    re.I)


class Container:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.meta_path = self.path / "bridge.json"
        self.meta = {"name": self.path.name, "arch": "win64", "dxvk": False, "apps": [], "env": {},
                     "created": time.strftime("%Y-%m-%d %H:%M")}
        try:
            self.meta.update(json.loads(self.meta_path.read_text(encoding="utf-8")))
        except Exception:
            pass

    # -------------------------------------------------- propriedades
    @property
    def slug(self) -> str:
        return self.path.name

    @property
    def name(self) -> str:
        return self.meta.get("name") or self.slug

    @property
    def arch(self) -> str:
        return self.meta.get("arch", "win64")

    @property
    def drive_c(self) -> Path:
        return self.path / "drive_c"

    @property
    def initialized(self) -> bool:
        return (self.path / "system.reg").exists()

    def save(self):
        self.path.mkdir(parents=True, exist_ok=True)
        self.meta_path.write_text(json.dumps(self.meta, indent=2, ensure_ascii=False), encoding="utf-8")

    def size_text(self) -> str:
        total = 0
        try:
            for root, _dirs, files in os.walk(self.path):
                for f in files:
                    try:
                        total += os.lstat(os.path.join(root, f)).st_size
                    except OSError:
                        pass
        except OSError:
            pass
        for unit in ["B", "KB", "MB", "GB"]:
            if total < 1024:
                return f"{total:.0f} {unit}"
            total /= 1024
        return f"{total:.1f} TB"

    # -------------------------------------------------- ambiente
    def env(self, cfg: Config) -> dict:
        e = {"WINEPREFIX": str(self.path), "WINEARCH": self.arch}
        if cfg["hide_wine_debug"]:
            e["WINEDEBUG"] = "-all"
        if cfg["esync"]:
            e["WINEESYNC"] = "1"
            e["WINEFSYNC"] = "1"
        if self.meta.get("dxvk"):
            e["DXVK_LOG_LEVEL"] = "warn"
        e.update(self.meta.get("env") or {})
        return e

    # -------------------------------------------------- programas
    def manual_apps(self) -> list[App]:
        out = []
        for a in self.meta.get("apps", []):
            try:
                out.append(App(a["name"], a["target"], a.get("args", ""), a.get("icon", ""), "manual"))
            except KeyError:
                pass
        return out

    def add_app(self, app: App):
        apps = [a for a in self.meta.get("apps", []) if a.get("target") != app.target]
        apps.append({"name": app.name, "target": app.target, "args": app.args, "icon": app.icon})
        self.meta["apps"] = apps
        self.save()

    def remove_app(self, target: str):
        self.meta["apps"] = [a for a in self.meta.get("apps", []) if a.get("target") != target]
        hidden = set(self.meta.get("hidden", []))
        hidden.add(target)
        self.meta["hidden"] = sorted(hidden)
        self.save()

    def menu_apps(self) -> list[App]:
        """Atalhos .lnk criados pelos instaladores (Menu Iniciar / Area de trabalho)."""
        c = self.drive_c
        roots = [c / "ProgramData/Microsoft/Windows/Start Menu/Programs"]
        users = c / "users"
        desktops = []
        if users.is_dir():
            for u in users.iterdir():
                roots.append(u / "AppData/Roaming/Microsoft/Windows/Start Menu/Programs")
                roots.append(u / "Start Menu/Programs")
                desktops.append(u / "Desktop")
        icons = wine_menu_icons(self)
        seen, out = set(), []
        hidden = set(self.meta.get("hidden", []))

        def add(p: Path):
            name = p.stem
            if SKIP_LNK.search(name) or name.lower() in seen or str(p) in hidden:
                return
            seen.add(name.lower())
            out.append(App(name, str(p), "", icons.get(name.lower(), ""), "menu"))

        for r in roots:
            if r.is_dir():
                for p in sorted(r.rglob("*.lnk")):
                    add(p)
        for d in desktops:
            # a Desktop do Wine costuma ser um link para a Area de Trabalho real: nao varre recursivo
            if d.is_dir():
                for p in sorted(d.glob("*.lnk")):
                    add(p)
        return out

    def apps(self) -> list[App]:
        manual = self.manual_apps()
        keys = {a.name.lower() for a in manual}
        return manual + [a for a in self.menu_apps() if a.name.lower() not in keys]


def wine_menu_icons(container: Container) -> dict:
    """Le os .desktop que o Wine gera para pegar o icone de cada programa."""
    out = {}
    base = APPS_DIR / "wine"
    if not base.is_dir():
        return out
    needle = str(container.path)
    for f in base.rglob("*.desktop"):
        try:
            txt = f.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if needle not in txt:
            continue
        name = re.search(r"^Name=(.*)$", txt, re.M)
        icon = re.search(r"^Icon=(.*)$", txt, re.M)
        if name and icon:
            out[name.group(1).strip().lower()] = icon.group(1).strip()
    return out


def list_containers() -> list[Container]:
    PREFIXES.mkdir(parents=True, exist_ok=True)
    out = [Container(p) for p in sorted(PREFIXES.iterdir()) if p.is_dir()]
    return sorted(out, key=lambda c: c.name.lower())


def get_container(slug: str) -> Container | None:
    p = PREFIXES / slug
    return Container(p) if p.is_dir() else None


def new_container(name: str, arch: str = "win64", dxvk: bool = True) -> Container:
    slug = slugify(name)
    base, i = slug, 2
    while (PREFIXES / slug).exists():
        slug = f"{base}-{i}"
        i += 1
    c = Container(PREFIXES / slug)
    c.meta.update({"name": name.strip() or slug, "arch": arch, "dxvk": dxvk})
    c.save()
    return c


def delete_container(c: Container):
    remove_shortcuts(c)
    shutil.rmtree(c.path, ignore_errors=True)


# ================================================================ comandos Wine
WINETRICKS_VERBS = [
    ("corefonts", "Fontes da Microsoft (Arial, Times...)", True),
    ("vcrun2022", "Visual C++ 2015-2022 (a maioria dos apps)", True),
    ("dxvk", "DXVK: DirectX 9/10/11 sobre Vulkan (mais desempenho)", True),
    ("d3dcompiler_47", "Compilador de shaders DirectX", False),
    ("vkd3d", "VKD3D: DirectX 12 sobre Vulkan", False),
    ("dotnet48", ".NET Framework 4.8 (demora, ~15 min)", False),
    ("dotnetdesktop8", ".NET 8 Desktop Runtime", False),
    ("gdiplus", "GDI+ (apps com graficos antigos)", False),
    ("vcrun2010", "Visual C++ 2010", False),
    ("xact", "XACT (audio de jogos antigos)", False),
    ("mfc140", "MFC 14 (apps com interface MFC)", False),
    ("win10", "Reportar Windows 10 para os apps", True),
]


def wine_bin(cfg: Config) -> str:
    return cfg["wine"] or "wine"


def cmd_init(cfg: Config, c: Container, extra_verbs: list[str]) -> list[Command]:
    if DEMO:
        cmds = [demo_command(f"criar {c.name}", [
            f"wine: created the configuration directory '{c.path}'",
            "wineboot: initializing prefix...", "wineboot: done"], 2)]
        (c.path / "drive_c/ProgramData/Microsoft/Windows/Start Menu/Programs").mkdir(parents=True, exist_ok=True)
        (c.path / "system.reg").write_text("demo")
    else:
        env = c.env(cfg)
        env["WINEDLLOVERRIDES"] = "mscoree=d;mshtml=d"  # sem janelas do Mono/Gecko
        cmds = [Command([wine_bin(cfg), "wineboot", "-u"], f"criar container {c.name}", env)]
    if extra_verbs:
        cmds.append(cmd_winetricks(cfg, c, extra_verbs))
    return cmds


def cmd_run_file(cfg: Config, c: Container, path: str, args: str = "") -> Command:
    p = Path(path)
    if DEMO:
        return demo_command(f"executar {p.name}", [f"[{c.name}] iniciando {p.name}...", "instalador em execucao",
                                                    "processo finalizado"], 2)
    ext = p.suffix.lower()
    w = wine_bin(cfg)
    if ext == ".msi":
        argv = [w, "msiexec", "/i", str(p)]
    elif ext in (".bat", ".cmd"):
        argv = [w, "cmd", "/c", str(p)]
    elif ext == ".lnk":
        argv = [w, "start", "/wait", "/unix", str(p)]
    else:
        argv = [w, str(p)]
    if args:
        argv += split_args(args)
    return Command(argv, f"{c.name} :: {p.name}", c.env(cfg), str(p.parent) if p.parent.is_dir() else None,
                   detached=True)


def cmd_launch_app(cfg: Config, c: Container, app: App) -> Command:
    return cmd_run_file(cfg, c, app.target, app.args)


def split_args(s: str) -> list[str]:
    import shlex
    try:
        return shlex.split(s)
    except ValueError:
        return s.split()


def cmd_winetricks(cfg: Config, c: Container, verbs: list[str]) -> Command:
    if DEMO:
        return demo_command(f"winetricks {' '.join(verbs)}", [f"Executing w_do_call {v}" for v in verbs] + ["ok"], 3)
    env = c.env(cfg)
    env["WINE"] = shutil.which(wine_bin(cfg)) or wine_bin(cfg)
    return Command([cfg["winetricks"] or "winetricks", "-q", "--unattended", *verbs],
                   f"winetricks {' '.join(verbs)} ({c.name})", env)


TOOLS = {
    "winecfg": ("CONFIGURAR WINE", ["winecfg"]),
    "regedit": ("REGISTRO", ["regedit"]),
    "taskmgr": ("GERENCIADOR DE TAREFAS", ["taskmgr"]),
    "control": ("PAINEL DE CONTROLE", ["control"]),
    "explorer": ("EXPLORER DO WINDOWS", ["explorer"]),
    "cmd": ("PROMPT (CMD)", ["wineconsole", "cmd"]),
}


def cmd_tool(cfg: Config, c: Container, tool: str) -> Command:
    label, args = TOOLS[tool]
    if DEMO:
        return demo_command(f"{tool} ({c.name})", [f"{tool}: aberto"], 1)
    return Command([wine_bin(cfg), *args], f"{label.lower()} ({c.name})", c.env(cfg), detached=True)


def cmd_kill(cfg: Config, c: Container) -> Command:
    if DEMO:
        return demo_command("wineserver -k", ["todos os processos encerrados"], 0.5)
    ws = shutil.which("wineserver") or "wineserver"
    return Command([ws, "-k"], f"encerrar tudo ({c.name})", c.env(cfg))


def cmd_open_folder(path: Path) -> Command:
    if DEMO:
        return demo_command("abrir pasta", [f"xdg-open {path}"], 0.3)
    return Command(["xdg-open", str(path)], "abrir pasta", detached=True)


# ================================================================ atalhos
def _shortcut_name(c: Container, app: App) -> str:
    return f"{APP_ID}-{c.slug}-{slugify(app.name)}.desktop"


def _exec_arg(s: str) -> str:
    """Escapa um argumento para a linha Exec= de um .desktop (spec freedesktop)."""
    s = str(s).replace("%", "%%")
    for ch in ("\\", '"', "`", "$"):
        s = s.replace(ch, "\\" + ch)
    s = s.replace("\\", "\\\\")
    return f'"{s}"'


def create_shortcut(c: Container, app: App, desktop_too: bool = False) -> Path:
    APPS_DIR.mkdir(parents=True, exist_ok=True)
    icon = app.icon or APP_ID
    exe = shutil.which(APP_ID) or str(HOME / ".local/bin" / APP_ID)
    content = (
        "[Desktop Entry]\n"
        "Type=Application\n"
        f"Name={app.name}\n"
        f"Comment=Windows via {APP_NAME} ({c.name})\n"
        f"Exec={_exec_arg(exe)} --launch {c.slug} {_exec_arg(app.target)}\n"
        f"Icon={icon}\n"
        "Categories=Wine;\n"
        "StartupNotify=true\n"
        f"X-Arasaka-Container={c.slug}\n"
    )
    p = APPS_DIR / _shortcut_name(c, app)
    p.write_text(content, encoding="utf-8")
    p.chmod(0o755)
    if desktop_too:
        desk = _desktop_dir()
        if desk:
            d = desk / p.name
            d.write_text(content, encoding="utf-8")
            d.chmod(0o755)
            if not DEMO and shutil.which("gio"):
                subprocess.run(["gio", "set", str(d), "metadata::trusted", "true"],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return p


def _desktop_dir() -> Path | None:
    try:
        out = subprocess.run(["xdg-user-dir", "DESKTOP"], capture_output=True, text=True, timeout=3).stdout.strip()
        if out and Path(out).is_dir():
            return Path(out)
    except Exception:
        pass
    d = HOME / "Desktop"
    return d if d.is_dir() else None


def remove_shortcuts(c: Container):
    for d in [APPS_DIR, _desktop_dir()]:
        if d and d.is_dir():
            for f in d.glob(f"{APP_ID}-{c.slug}-*.desktop"):
                f.unlink(missing_ok=True)


# ================================================================ sistema
@dataclass
class Check:
    key: str
    title: str
    ok: bool
    detail: str
    action: str | None = None      # chave de DEP_ACTIONS para corrigir
    optional: bool = False


def _run(argv, timeout=6) -> tuple[int, str]:
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout + p.stderr).strip()
    except Exception as e:  # noqa: BLE001
        return 127, str(e)


def flatpak_info(app_id: str) -> tuple[bool, str]:
    if DEMO:
        return (app_id == VINEGAR_ID), "1.8.1"
    if not shutil.which("flatpak"):
        return False, ""
    for scope in ("--user", "--system"):
        rc, out = _run(["flatpak", "info", scope, app_id])
        if rc == 0:
            m = re.search(r"Version:\s*(\S+)", out)
            return True, (m.group(1) if m else "instalado")
    return False, ""


def has_flathub() -> bool:
    if DEMO:
        return True
    rc, out = _run(["flatpak", "remotes", "--columns=name"])
    return rc == 0 and "flathub" in out.split()


def gpu_name() -> str:
    if DEMO:
        return "AMD Radeon RX 6700 XT (demo)"
    rc, out = _run(["lspci"])
    if rc == 0:
        for line in out.splitlines():
            if re.search(r"VGA|3D controller|Display controller", line):
                return re.sub(r"^.*?: ", "", line).strip()
    return "desconhecida"


def vulkan_drivers() -> list[str]:
    if DEMO:
        return ["radeon"]
    names = set()
    for d in ["/usr/share/vulkan/icd.d", "/etc/vulkan/icd.d"]:
        p = Path(d)
        if p.is_dir():
            for f in p.glob("*.json"):
                names.add(re.sub(r"_icd.*$", "", f.stem))
    return sorted(names)


def system_checks() -> list[Check]:
    checks = []
    if DEMO:
        return [
            Check("wine", "WINE", True, "wine-9.0 (demo)"),
            Check("winetricks", "WINETRICKS", True, "20240105"),
            Check("i386", "SUPORTE 32-BIT", True, "i386 ativo"),
            Check("flatpak", "FLATPAK + FLATHUB", True, "flathub configurado"),
            Check("vinegar", "VINEGAR (ROBLOX STUDIO)", True, "versao 1.8.1"),
            Check("vulkan", "VULKAN / GPU", True, "AMD Radeon RX 6700 XT · radeon"),
        ]
    w = shutil.which("wine")
    ver = _run(["wine", "--version"])[1] if w else ""
    checks.append(Check("wine", "WINE", bool(w), ver or "nao instalado", None if w else "wine"))
    wt = shutil.which("winetricks")
    wtv = _run(["winetricks", "--version"])[1].split()[0] if wt else ""
    checks.append(Check("winetricks", "WINETRICKS", bool(wt), wtv or "nao instalado", None if wt else "wine"))
    rc, arches = _run(["dpkg", "--print-foreign-architectures"])
    i386 = "i386" in arches.split()
    checks.append(Check("i386", "SUPORTE 32-BIT", i386, "i386 ativo" if i386 else "desativado (apps 32-bit)",
                        None if i386 else "wine", optional=True))
    fp = bool(shutil.which("flatpak"))
    fh = fp and has_flathub()
    checks.append(Check("flatpak", "FLATPAK + FLATHUB", fh,
                        "flathub configurado" if fh else ("sem o repositorio Flathub" if fp else "nao instalado"),
                        None if fh else "flatpak"))
    vin, vv = flatpak_info(VINEGAR_ID)
    checks.append(Check("vinegar", "VINEGAR (ROBLOX STUDIO)", vin, f"versao {vv}" if vin else "nao instalado",
                        None if vin else "vinegar"))
    drv = vulkan_drivers()
    gpu = gpu_name()
    checks.append(Check("vulkan", "VULKAN / GPU", bool(drv), f"{gpu} · {', '.join(drv) or 'sem driver Vulkan'}",
                        None if drv else "vulkan"))
    return checks


# acoes que instalam dependencias (pkexec abre a janela de senha grafica)
def dep_commands(key: str) -> list[Command]:
    if DEMO:
        return [demo_command(f"instalar {key}", [f"Lendo listas de pacotes... ({key})", "Configurando...",
                                                  "Concluido."], 3)]
    if key == "wine":
        script = ("set -e; dpkg --add-architecture i386; apt-get update; "
                  "DEBIAN_FRONTEND=noninteractive apt-get install -y --install-recommends wine64 wine32:i386 winetricks")
        return [Command(["pkexec", "sh", "-c", script], "instalar Wine + Winetricks")]
    if key == "flatpak":
        cmds = []
        if not shutil.which("flatpak"):
            cmds.append(Command(["pkexec", "sh", "-c", "DEBIAN_FRONTEND=noninteractive apt-get install -y flatpak"],
                                "instalar Flatpak"))
        cmds.append(Command(["flatpak", "remote-add", "--user", "--if-not-exists", "flathub", FLATHUB_URL],
                            "adicionar Flathub"))
        return cmds
    if key == "vinegar":
        return dep_commands("flatpak") + [flatpak_install(VINEGAR_ID, "instalar Vinegar")]
    if key == "sober":
        return dep_commands("flatpak") + [flatpak_install(SOBER_ID, "instalar Sober")]
    if key == "vulkan":
        script = ("set -e; dpkg --add-architecture i386; apt-get update; DEBIAN_FRONTEND=noninteractive "
                  "apt-get install -y mesa-vulkan-drivers mesa-vulkan-drivers:i386 vulkan-tools")
        return [Command(["pkexec", "sh", "-c", script], "instalar drivers Vulkan (Mesa)")]
    return []


def flatpak_install(app_id: str, label: str) -> Command:
    return Command(["flatpak", "install", "--user", "-y", "--noninteractive", "flathub", app_id], label)


# ================================================================ Roblox Studio / Vinegar
def vinegar_data_dirs() -> dict:
    base = HOME / ".var/app" / VINEGAR_ID
    return {
        "config": base / "config/vinegar",
        "data": base / "data/vinegar",
        "cache": base / "cache/vinegar",
    }


def flatpak_desktop_entries(app_id: str) -> list[tuple[str, Path]]:
    """Atalhos exportados por um app Flatpak (ex.: 'Roblox Studio' do Vinegar)."""
    dirs = [HOME / ".local/share/flatpak/exports/share/applications",
            Path("/var/lib/flatpak/exports/share/applications")]
    out = []
    for d in dirs:
        if not d.is_dir():
            continue
        for f in sorted(d.glob(f"{app_id}*.desktop")):
            try:
                txt = f.read_text(encoding="utf-8", errors="ignore")
            except OSError:
                continue
            m = re.search(r"^Name=(.*)$", txt, re.M)
            if re.search(r"^NoDisplay=true", txt, re.M) and "studio" not in f.name.lower():
                continue
            out.append(((m.group(1).strip() if m else f.stem), f))
    return out


def cmd_open_studio() -> Command:
    if DEMO:
        return demo_command("Roblox Studio", ["vinegar: checking deployment...", "vinegar: launching studio",
                                              "Roblox Studio aberto"], 3)
    entries = flatpak_desktop_entries(VINEGAR_ID)
    studio = [p for n, p in entries if "studio" in (n + p.name).lower()]
    if studio and shutil.which("gio"):
        return Command(["gio", "launch", str(studio[0])], "abrir Roblox Studio", detached=True)
    return Command(["flatpak", "run", VINEGAR_ID, "run"], "abrir Roblox Studio (Vinegar)", detached=True)


def cmd_vinegar_manager() -> Command:
    if DEMO:
        return demo_command("Vinegar", ["vinegar: janela de configuracao aberta"], 1)
    return Command(["flatpak", "run", VINEGAR_ID], "abrir Vinegar", detached=True)


def cmd_flatpak_update(app_id: str) -> Command:
    if DEMO:
        return demo_command("atualizar", ["Procurando atualizacoes...", "Nada para atualizar."], 2)
    return Command(["flatpak", "update", "--user", "-y", "--noninteractive", app_id], f"atualizar {app_id}")


def cmd_flatpak_kill(app_id: str) -> Command:
    if DEMO:
        return demo_command("encerrar", ["encerrado"], 0.5)
    return Command(["flatpak", "kill", app_id], f"encerrar {app_id}")


def cmd_flatpak_uninstall(app_id: str) -> Command:
    if DEMO:
        return demo_command("desinstalar", ["Desinstalando...", "ok"], 1)
    return Command(["flatpak", "uninstall", "--user", "-y", "--noninteractive", app_id], f"desinstalar {app_id}")


# ================================================================ utilidades
def is_windows_file(path: str) -> bool:
    return Path(path).suffix.lower() in (".exe", ".msi", ".bat", ".cmd", ".lnk")


def log_file() -> Path:
    LOGS.mkdir(parents=True, exist_ok=True)
    return LOGS / time.strftime("bridge-%Y%m%d.log")
