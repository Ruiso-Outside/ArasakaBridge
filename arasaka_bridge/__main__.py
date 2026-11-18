"""
ARASAKA BRIDGE // ponto de entrada.

  arasaka-bridge                      abre a interface
  arasaka-bridge arquivo.exe          abre a interface ja pedindo onde executar
  arasaka-bridge --launch SLUG ALVO   abre um programa direto (usado pelos atalhos do menu)
  arasaka-bridge --studio             abre o Roblox Studio direto
"""
import os
import sys

from . import core


def launch(slug: str, target: str) -> int:
    cfg = core.Config()
    c = core.get_container(slug)
    if not c:
        print(f"container '{slug}' nao encontrado", file=sys.stderr)
        return 1
    app = next((a for a in c.apps() if a.target == target), core.App(os.path.basename(target), target))
    cmd = core.cmd_launch_app(cfg, c, app)
    env = dict(os.environ)
    env.update({k: str(v) for k, v in (cmd.env or {}).items()})
    if cmd.cwd:
        os.chdir(cmd.cwd)
    os.execvpe(cmd.argv[0], cmd.argv, env)
    return 0


def main() -> int:
    args = sys.argv[1:]
    if len(args) >= 3 and args[0] == "--launch":
        return launch(args[1], args[2])
    if args[:1] == ["--studio"]:
        cmd = core.cmd_open_studio()
        os.execvp(cmd.argv[0], cmd.argv)
    if args[:1] in (["--version"], ["-v"]):
        print(f"{core.APP_NAME} {core.VERSION}")
        return 0
    from .app import main as gui
    return gui(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
