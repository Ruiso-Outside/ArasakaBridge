"""
ARASAKA BRIDGE // interface (PySide6 / Qt 6).
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

from PySide6.QtCore import (QObject, QPointF, QProcess, QProcessEnvironment, QRectF, QSize, Qt, QThread, QTimer,
                            Signal)
from PySide6.QtGui import (QAction, QColor, QFont, QFontDatabase, QIcon, QPainter, QPainterPath, QPen, QPixmap,
                           QPolygonF, QTextCursor)
from PySide6.QtSvg import QSvgRenderer
from PySide6.QtWidgets import (QApplication, QButtonGroup, QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                               QFileDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout, QLabel, QLineEdit,
                               QListWidget, QListWidgetItem, QMainWindow, QMenu, QMessageBox, QPlainTextEdit,
                               QPushButton, QScrollArea, QSizePolicy, QSplitter, QStackedWidget, QToolButton,
                               QVBoxLayout, QWidget)

from . import core
from . import fx
from .core import APP_NAME, VERSION, App, Command, Config, Container

RED = QColor(227, 18, 31)
RED_HI = QColor(255, 36, 54)
BG0 = QColor(3, 3, 4)
BG1 = QColor(8, 8, 10)
BG2 = QColor(14, 14, 17)
LINE = QColor(42, 42, 49)
FG = QColor(236, 236, 240)
MUTED = QColor(140, 140, 150)

FONTS = {"ui": "Sans Serif", "mono": "Monospace", "brand": "Sans Serif"}


# ================================================================ fontes e estilo
def load_fonts():
    fid = QFontDatabase.addApplicationFont(str(core.ASSETS / "cedge1.ttf"))
    fams = set(QFontDatabase.families())
    if fid >= 0:
        FONTS["brand"] = QFontDatabase.applicationFontFamilies(fid)[0]
    for cand in ["Rajdhani", "Bahnschrift", "Inter", "Cantarell", "DejaVu Sans"]:
        if cand in fams:
            FONTS["ui"] = cand
            break
    for cand in ["Share Tech Mono", "JetBrains Mono", "Consolas", "DejaVu Sans Mono", "Monospace"]:
        if cand in fams:
            FONTS["mono"] = cand
            break


def stylesheet() -> str:
    ui, mono = FONTS["ui"], FONTS["mono"]
    size = 15 if ui == "Rajdhani" else 13
    return f"""
* {{ font-family: "{ui}"; font-size: {size}px; color: #ececf0; outline: none; }}
QMainWindow, QWidget#root, QDialog, QMessageBox {{ background: #070708; }}
QWidget#page {{ background: transparent; }}
QScrollArea, QScrollArea > QWidget > QWidget {{ background: transparent; border: none; }}

QFrame#sidebar {{ background: #030304; border-right: 1px solid #2a0a0d; }}
QPushButton#nav {{
  text-align: left; padding: 13px 20px; border: none; border-left: 3px solid transparent;
  color: #8c8c96; font-weight: 700; background: transparent;
}}
QPushButton#nav:hover {{ color: #ffffff; background: rgba(227,18,31,0.08); }}
QPushButton#nav:checked {{ color: #ffffff; border-left: 3px solid #e3121f; background: rgba(227,18,31,0.16); }}

QPushButton, QToolButton {{
  background: #141418; border: 1px solid #2a2a31; padding: 9px 16px; font-weight: 700; color: #ececf0;
}}
QPushButton:hover, QToolButton:hover {{ border-color: #e3121f; background: #1f0a0d; color: #ffffff; }}
QPushButton:pressed, QToolButton:pressed {{ background: #e3121f; }}
QPushButton:disabled {{ color: #4a4a52; border-color: #1b1b20; background: #0c0c0e; }}
QPushButton[kind="primary"] {{ background: #e3121f; border: 1px solid #ff2436; color: #ffffff; }}
QPushButton[kind="primary"]:hover {{ background: #ff2436; }}
QPushButton[kind="primary"]:disabled {{ background: #3a0a0e; border-color: #5a080e; color: #8c5a5e; }}
QPushButton[kind="danger"] {{ background: #16050a; border-color: #5a080e; color: #ff3b47; }}
QPushButton[kind="danger"]:hover {{ background: #e3121f; color: #ffffff; }}
QPushButton[kind="ghost"] {{ background: transparent; border-color: transparent; color: #8c8c96; padding: 4px 10px; }}
QPushButton[kind="ghost"]:hover {{ color: #ffffff; border-color: #e3121f; }}
QToolButton::menu-indicator {{ image: none; width: 0; }}

QLineEdit, QComboBox {{
  background: #050506; border: 1px solid #2a2a31; padding: 8px 10px; selection-background-color: #e3121f;
}}
QLineEdit:focus, QComboBox:focus, QComboBox:on {{ border-color: #e3121f; }}
QComboBox::drop-down {{ border: none; width: 26px; }}
QComboBox::down-arrow {{ image: none; border-left: 5px solid transparent; border-right: 5px solid transparent;
  border-top: 6px solid #e3121f; width: 0; height: 0; margin-right: 10px; }}
QComboBox QAbstractItemView {{ background: #0a0a0c; border: 1px solid #e3121f; selection-background-color: #e3121f; }}

QListWidget {{ background: #050506; border: 1px solid #1d1d22; }}
QListWidget::item {{ padding: 10px 8px; border-left: 3px solid transparent; }}
QListWidget::item:hover {{ background: rgba(227,18,31,0.10); }}
QListWidget::item:selected {{ background: rgba(227,18,31,0.28); border-left: 3px solid #e3121f; color: #ffffff; }}
QListWidget#grid::item {{ padding: 12px 4px; margin: 4px; border: 1px solid #1d1d22; background: #0b0b0e; }}
QListWidget#grid::item:hover {{ border-color: #e3121f; background: #160709; }}
QListWidget#grid::item:selected {{ border: 1px solid #ff2436; background: rgba(227,18,31,0.22); }}

QScrollBar:vertical {{ background: transparent; width: 8px; margin: 0; }}
QScrollBar::handle:vertical {{ background: #2e2e35; min-height: 30px; }}
QScrollBar::handle:vertical:hover {{ background: #e3121f; }}
QScrollBar:horizontal {{ background: transparent; height: 8px; }}
QScrollBar::handle:horizontal {{ background: #2e2e35; min-width: 30px; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: none; }}

QCheckBox {{ spacing: 10px; }}
QCheckBox::indicator {{ width: 16px; height: 16px; border: 1px solid #4a4a52; background: #050506; }}
QCheckBox::indicator:hover {{ border-color: #e3121f; }}
QCheckBox::indicator:checked {{ background: #e3121f; border-color: #ff2436; }}

QMenu {{ background: #0a0a0c; border: 1px solid #e3121f; padding: 4px; }}
QMenu::item {{ padding: 8px 22px; }}
QMenu::item:selected {{ background: rgba(227,18,31,0.32); }}
QMenu::separator {{ height: 1px; background: #2a2a31; margin: 4px 8px; }}
QToolTip {{ background: #000000; border: 1px solid #e3121f; color: #ececf0; padding: 6px; }}

QLabel#muted {{ color: #8c8c96; }}
QLabel#dim {{ color: #55555e; }}
QLabel#red {{ color: #e3121f; font-weight: 700; }}
QLabel#section {{ color: #e3121f; font-weight: 700; }}

QPlainTextEdit#console {{
  font-family: "{mono}"; font-size: 12px; background: #030304; border: none; color: #c9c9cf;
  selection-background-color: #e3121f;
}}
QFrame#consoleBar {{ background: #050506; border-top: 1px solid #3a0a0f; border-bottom: 1px solid #16161a; }}
QSplitter::handle {{ background: #120507; }}
QDialogButtonBox QPushButton {{ min-width: 110px; }}
"""


def spaced(w: QWidget, px: float = 2.0, size: int | None = None, bold: bool = False, family: str | None = None):
    f = w.font()
    if family:
        f.setFamily(family)
    if size:
        f.setPixelSize(size)
    if bold:
        f.setBold(True)
    f.setLetterSpacing(QFont.AbsoluteSpacing, px)
    w.setFont(f)
    return w


def label(text: str, obj: str | None = None, px: float = 1.0, size: int | None = None, bold=False, wrap=False):
    lb = QLabel(text)
    if obj:
        lb.setObjectName(obj)
    spaced(lb, px, size, bold)
    lb.setWordWrap(wrap)
    return lb


def button(text: str, kind: str | None = None, slot=None, tip: str | None = None) -> QPushButton:
    b = QPushButton(text)
    if kind:
        b.setProperty("kind", kind)
    b.setCursor(Qt.PointingHandCursor)
    spaced(b, 1.5)
    if slot:
        b.clicked.connect(lambda _checked=False, s=slot: s())
    if tip:
        b.setToolTip(tip)
    return b


def logo_pixmap(size: int, path: Path | None = None) -> QPixmap:
    r = QSvgRenderer(str(path or core.ASSETS / "arasaka.svg"))
    dpr = QApplication.instance().devicePixelRatio() if QApplication.instance() else 1
    pm = QPixmap(int(size * dpr), int(size * dpr))
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    r.render(p)
    p.end()
    pm.setDevicePixelRatio(dpr)
    return pm


# ================================================================ widgets visuais
class CutFrame(QFrame):
    """Painel com cantos cortados e borda fina (estilo HUD)."""

    def __init__(self, cut=14, border=LINE, fill=BG2, accent=True, parent=None):
        super().__init__(parent)
        self.cut, self.border, self.fill, self.accent = cut, border, fill, accent
        self.setAttribute(Qt.WA_StyledBackground, False)

    def set_border(self, c: QColor):
        self.border = c
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h, c = self.width() - 1, self.height() - 1, self.cut
        poly = QPolygonF([QPointF(c, 0.5), QPointF(w, 0.5), QPointF(w, h - c), QPointF(w - c, h),
                          QPointF(0.5, h), QPointF(0.5, c)])
        p.setBrush(self.fill)
        p.setPen(QPen(self.border, 1))
        p.drawPolygon(poly)
        if self.accent:
            p.setPen(QPen(RED, 2))
            p.drawLine(QPointF(c, 1), QPointF(c + 34, 1))
            p.drawLine(QPointF(w - c, h - 1), QPointF(w - c - 34, h - 1))


class HudHeader(QWidget):
    """Cabecalho de pagina: titulo na fonte da marca + subtitulo + linha vermelha."""

    def __init__(self, title: str, subtitle: str = "", code: str = ""):
        super().__init__()
        self.title, self.subtitle, self.code = title, subtitle, code
        self.setMinimumHeight(92)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        f = QFont(FONTS["brand"])
        f.setPixelSize(34)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 6)
        p.setFont(f)
        p.setPen(FG)
        p.drawText(QRectF(0, 6, self.width(), 44), Qt.AlignLeft | Qt.AlignVCenter, self.title)
        f2 = QFont(FONTS["ui"])
        f2.setPixelSize(14)
        f2.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
        p.setFont(f2)
        p.setPen(MUTED)
        p.drawText(QRectF(2, 52, self.width(), 22), Qt.AlignLeft | Qt.AlignVCenter, self.subtitle)
        if self.code:
            f3 = QFont(FONTS["mono"])
            f3.setPixelSize(11)
            p.setFont(f3)
            p.setPen(QColor(85, 85, 94))
            p.drawText(QRectF(0, 10, self.width(), 18), Qt.AlignRight | Qt.AlignVCenter, self.code)
        y = self.height() - 6
        p.setPen(QPen(QColor(42, 10, 13), 1))
        p.drawLine(0, y, self.width(), y)
        p.setPen(QPen(RED, 3))
        p.drawLine(0, y, 90, y)
        p.setPen(QPen(RED, 1))
        for i in range(6):
            x = self.width() - 8 - i * 9
            p.drawLine(x, y - 4, x - 4, y + 2)


class Indicator(QWidget):
    """Quadrado de status que pisca quando offline."""

    def __init__(self, ok=True):
        super().__init__()
        self.ok = ok
        self.phase = 0
        self.setFixedSize(14, 14)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._tick)
        self.timer.start(500)

    def set_ok(self, ok):
        self.ok = ok
        self.update()

    def _tick(self):
        self.phase ^= 1
        if not self.ok:
            self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        if self.ok:
            p.fillRect(2, 2, 10, 10, FG)
            p.setPen(QPen(RED, 1))
            p.drawRect(0, 0, 13, 13)
        else:
            p.fillRect(2, 2, 10, 10, RED if self.phase else QColor(90, 8, 14))


class StatusCard(CutFrame):
    def __init__(self, check: core.Check, on_fix):
        super().__init__(cut=12)
        self.setMinimumHeight(104)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(18, 14, 18, 14)
        top = QHBoxLayout()
        self.ind = Indicator(check.ok)
        top.addWidget(self.ind)
        t = label(check.title, px=2, bold=True)
        top.addWidget(t)
        top.addStretch()
        state = label("ONLINE" if check.ok else ("OPCIONAL" if check.optional else "OFFLINE"),
                      "muted" if check.ok else "red", px=2, size=12)
        top.addWidget(state)
        lay.addLayout(top)
        d = label(check.detail, "muted", px=0.5, wrap=True)
        lay.addWidget(d)
        if not check.ok and check.action:
            row = QHBoxLayout()
            row.addStretch()
            row.addWidget(button("INSTALAR" if check.key != "i386" else "ATIVAR", "primary",
                                 lambda: on_fix(check.action)))
            lay.addLayout(row)
        else:
            lay.addStretch()
        self.set_border(LINE if check.ok else QColor(90, 8, 14))


class HeroBanner(QWidget):
    """Banner grande com logo, grade e titulo (pagina Roblox Studio)."""

    def __init__(self, title: str, kicker: str):
        super().__init__()
        self.title, self.kicker = title, kicker
        self.status = ""
        self.ok = True
        self.logo = logo_pixmap(150)
        self.setMinimumHeight(210)

    def set_status(self, text: str, ok: bool):
        self.status, self.ok = text, ok
        self.update()

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w, h = self.width(), self.height()
        path = QPainterPath()
        c = 22
        path.moveTo(c, 0)
        path.lineTo(w, 0)
        path.lineTo(w, h - c)
        path.lineTo(w - c, h)
        path.lineTo(0, h)
        path.lineTo(0, c)
        path.closeSubpath()
        p.fillPath(path, QColor(10, 3, 5))
        p.save()
        p.setClipPath(path)
        p.setPen(QPen(QColor(227, 18, 31, 26), 1))
        for x in range(0, w, 32):
            p.drawLine(x, 0, x, h)
        for y in range(0, h, 32):
            p.drawLine(0, y, w, y)
        p.setOpacity(0.10)
        big = logo_pixmap(420)
        p.drawPixmap(w - 330, int(h / 2 - 210), big)
        p.setOpacity(1)
        p.restore()
        p.setPen(QPen(QColor(227, 18, 31, 160), 1))
        p.drawPath(path)
        p.drawPixmap(36, int(h / 2 - 75), self.logo)
        x0 = 220
        f = QFont(FONTS["ui"])
        f.setPixelSize(14)
        f.setBold(True)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 4)
        p.setFont(f)
        p.setPen(RED)
        p.drawText(QRectF(x0, h / 2 - 70, w - x0, 24), Qt.AlignLeft | Qt.AlignVCenter, self.kicker)
        fb = QFont(FONTS["brand"])
        fb.setPixelSize(46)
        fb.setLetterSpacing(QFont.AbsoluteSpacing, 8)
        p.setFont(fb)
        p.setPen(FG)
        p.drawText(QRectF(x0, h / 2 - 44, w - x0, 64), Qt.AlignLeft | Qt.AlignVCenter, self.title)
        fs = QFont(FONTS["mono"])
        fs.setPixelSize(13)
        p.setFont(fs)
        p.fillRect(QRectF(x0, h / 2 + 36, 10, 10), FG if self.ok else RED)
        p.setPen(FG if self.ok else RED_HI)
        p.drawText(QRectF(x0 + 20, h / 2 + 30, w - x0, 22), Qt.AlignLeft | Qt.AlignVCenter, self.status)


class SidebarBrand(QWidget):
    def __init__(self):
        super().__init__()
        self.setFixedHeight(150)
        self.logo = logo_pixmap(64)

    def paintEvent(self, _e):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        w = self.width()
        p.drawPixmap(int(w / 2 - 32), 18, self.logo)
        f = QFont(FONTS["brand"])
        f.setPixelSize(22)
        f.setLetterSpacing(QFont.AbsoluteSpacing, 5)
        p.setFont(f)
        p.setPen(FG)
        p.drawText(QRectF(0, 88, w, 28), Qt.AlignCenter, "ARASAKA")
        f2 = QFont(FONTS["ui"])
        f2.setPixelSize(12)
        f2.setBold(True)
        f2.setLetterSpacing(QFont.AbsoluteSpacing, 6)
        p.setFont(f2)
        p.setPen(RED)
        p.drawText(QRectF(0, 116, w, 18), Qt.AlignCenter, "BRIDGE")
        p.setPen(QPen(QColor(42, 10, 13), 1))
        p.drawLine(20, 146, w - 20, 146)


# ================================================================ execucao de processos
class Runner(QObject):
    """Fila de comandos. Comandos 'detached' (apps do usuario) saem da fila e
    continuam rodando mesmo se o Bridge fechar; a saida vai para um log."""

    line = Signal(str, str)          # texto, tipo: out | sys | err | ok
    busy = Signal(bool, str)

    def __init__(self, cfg: Config):
        super().__init__()
        self.cfg = cfg
        self.batches: list[tuple[list[Command], object]] = []
        self.proc: QProcess | None = None
        self.current: Command | None = None
        self.remaining: list[Command] = []
        self.on_done = None
        self.logf = None

    def _log(self, text: str):
        try:
            if self.logf is None:
                self.logf = open(core.log_file(), "a", encoding="utf-8")
            self.logf.write(text + "\n")
            self.logf.flush()
        except OSError:
            pass

    def emit(self, text: str, kind: str = "out"):
        self.line.emit(text, kind)
        self._log(text)

    def run(self, cmds: list[Command], on_done=None):
        if not cmds:
            return
        self.batches.append((list(cmds), on_done))
        if self.proc is None and not self.remaining:
            self._next_batch()

    def is_busy(self) -> bool:
        return self.proc is not None

    def _next_batch(self):
        if not self.batches:
            self.busy.emit(False, "")
            return
        cmds, self.on_done = self.batches.pop(0)
        self.remaining = cmds
        self._next()

    def _env(self, cmd: Command) -> QProcessEnvironment:
        env = QProcessEnvironment.systemEnvironment()
        for k, v in (cmd.env or {}).items():
            env.insert(k, str(v))
        return env

    def _next(self):
        if not self.remaining:
            cb, self.on_done = self.on_done, None
            if cb:
                cb(True)
            self._next_batch()
            return
        cmd = self.remaining.pop(0)
        stamp = time.strftime("%H:%M:%S")
        self.emit(f"[{stamp}] >> {cmd.label.upper()}", "sys")
        self.emit(f"$ {cmd.display()}", "dim")
        if cmd.detached:
            self._start_detached(cmd)
            QTimer.singleShot(0, self._next)
            return
        self.current = cmd
        self.proc = QProcess(self)
        self.proc.setProcessChannelMode(QProcess.MergedChannels)
        self.proc.setProcessEnvironment(self._env(cmd))
        if cmd.cwd:
            self.proc.setWorkingDirectory(cmd.cwd)
        self.proc.readyReadStandardOutput.connect(self._read)
        self.proc.finished.connect(self._finished)
        self.proc.errorOccurred.connect(self._error)
        self.busy.emit(True, cmd.label)
        self.proc.start(cmd.argv[0], cmd.argv[1:])

    def _start_detached(self, cmd: Command):
        p = QProcess()
        p.setProgram(cmd.argv[0])
        p.setArguments(cmd.argv[1:])
        p.setProcessEnvironment(self._env(cmd))
        if cmd.cwd:
            p.setWorkingDirectory(cmd.cwd)
        logp = core.LOGS / ("app-" + core.slugify(cmd.label)[:60] + ".log")
        core.LOGS.mkdir(parents=True, exist_ok=True)
        p.setStandardOutputFile(str(logp))
        p.setStandardErrorFile(str(logp), QProcess.Append)
        ok, pid = p.startDetached()
        if ok:
            self.emit(f"   iniciado (pid {pid}) · log: {logp}", "ok")
        else:
            self.emit(f"   !! falha ao iniciar {cmd.argv[0]}", "err")

    def _read(self):
        if not self.proc:
            return
        data = bytes(self.proc.readAllStandardOutput()).decode("utf-8", errors="replace")
        for ln in data.replace("\r", "\n").splitlines():
            if ln.strip():
                self.emit("   " + ln, "out")

    def _error(self, err):
        if err == QProcess.FailedToStart and self.current:
            self.emit(f"   !! nao foi possivel iniciar '{self.current.argv[0]}' (esta instalado?)", "err")
            self._finish(127)

    def _finished(self, code, _status):
        self._read()
        self._finish(code)

    def _finish(self, code):
        if self.proc is None:
            return
        self.proc.deleteLater()
        self.proc = None
        label_ = self.current.label if self.current else ""
        self.current = None
        if code == 0:
            self.emit(f"   ■ OK · {label_}", "ok")
            self._next()
        else:
            self.emit(f"   !! FALHOU (codigo {code}) · {label_}", "err")
            self.remaining = []
            cb, self.on_done = self.on_done, None
            if cb:
                cb(False)
            self._next_batch()

    def stop(self):
        if self.proc:
            self.proc.kill()


class Console(QWidget):
    def __init__(self, runner: Runner):
        super().__init__()
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)
        bar = QFrame()
        bar.setObjectName("consoleBar")
        bl = QHBoxLayout(bar)
        bl.setContentsMargins(14, 4, 8, 4)
        self.dot = Indicator(True)
        bl.addWidget(self.dot)
        self.title = label("TERMINAL // PRONTO", "muted", px=2, size=12, bold=True)
        bl.addWidget(self.title)
        bl.addStretch()
        bl.addWidget(button("PARAR", "ghost", runner.stop, "Interrompe a tarefa atual"))
        bl.addWidget(button("LIMPAR", "ghost", lambda: self.text.clear()))
        self.toggle_btn = button("RECOLHER", "ghost", self.toggle)
        bl.addWidget(self.toggle_btn)
        lay.addWidget(bar)
        self.text = QPlainTextEdit()
        self.text.setObjectName("console")
        self.text.setReadOnly(True)
        self.text.setMaximumBlockCount(4000)
        lay.addWidget(self.text)
        runner.line.connect(self.append)
        runner.busy.connect(self.on_busy)
        self.append(f"{APP_NAME} v{VERSION} // canal seguro estabelecido", "sys")
        if core.DEMO:
            self.append("MODO DEMONSTRACAO: nenhum comando real e executado", "err")

    COLORS = {"out": "#c9c9cf", "sys": "#ff3b47", "err": "#ff3b47", "ok": "#ececf0", "dim": "#55555e"}

    def append(self, text: str, kind: str = "out"):
        color = self.COLORS.get(kind, "#c9c9cf")
        esc = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        weight = "700" if kind in ("sys", "ok") else "400"
        self.text.appendHtml(f'<span style="color:{color};font-weight:{weight};white-space:pre">{esc}</span>')
        self.text.moveCursor(QTextCursor.End)

    def on_busy(self, busy: bool, what: str):
        self.dot.set_ok(not busy)
        self.title.setText(f"TERMINAL // EXECUTANDO: {what.upper()}" if busy else "TERMINAL // PRONTO")
        if busy and not self.text.isVisible():
            self.toggle()

    def toggle(self):
        vis = not self.text.isVisible()
        self.text.setVisible(vis)
        self.toggle_btn.setText("RECOLHER" if vis else "EXPANDIR")


class CheckWorker(QThread):
    done = Signal(list)

    def run(self):
        try:
            self.done.emit(core.system_checks())
        except Exception as e:  # noqa: BLE001
            self.done.emit([core.Check("erro", "ERRO", False, str(e))])


# ================================================================ dialogos
class BaseDialog(QDialog):
    def __init__(self, parent, title: str, subtitle: str = ""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(520)
        self.lay = QVBoxLayout(self)
        self.lay.setContentsMargins(26, 18, 26, 20)
        self.lay.setSpacing(12)
        self.lay.addWidget(HudHeader(title, subtitle))

    def add_buttons(self, ok_text="CONFIRMAR"):
        box = QDialogButtonBox()
        ok = button(ok_text, "primary")
        cancel = button("CANCELAR")
        box.addButton(cancel, QDialogButtonBox.RejectRole)
        box.addButton(ok, QDialogButtonBox.AcceptRole)
        box.accepted.connect(self.accept)
        box.rejected.connect(self.reject)
        self.lay.addSpacing(6)
        self.lay.addWidget(box)
        return ok


class NewContainerDialog(BaseDialog):
    def __init__(self, parent, cfg: Config, suggested=""):
        super().__init__(parent, "NOVO CONTAINER", "Um ambiente Windows isolado para seus programas")
        form = QFormLayout()
        form.setSpacing(12)
        self.name = QLineEdit(suggested or "Trabalho")
        self.name.setPlaceholderText("ex.: Ferramentas, Office, Jogos")
        form.addRow(label("NOME", "muted", 2, bold=True), self.name)
        self.arch = QComboBox()
        self.arch.addItem("64-bit (recomendado)", "win64")
        self.arch.addItem("32-bit (apps muito antigos)", "win32")
        form.addRow(label("ARQUITETURA", "muted", 2, bold=True), self.arch)
        self.lay.addLayout(form)
        self.rec = QCheckBox("Instalar componentes recomendados (DXVK, fontes, Visual C++, Windows 10)")
        self.rec.setChecked(cfg["fonts_new"])
        self.lay.addWidget(self.rec)
        self.lay.addWidget(label("Os componentes sao baixados pelo Winetricks e podem levar alguns minutos.",
                                 "dim", 0.5, wrap=True))
        self.add_buttons("CRIAR CONTAINER")

    def values(self):
        verbs = [v for v, _d, rec in core.WINETRICKS_VERBS if rec] if self.rec.isChecked() else []
        return self.name.text().strip(), self.arch.currentData(), verbs


class WinetricksDialog(BaseDialog):
    def __init__(self, parent, container: Container):
        super().__init__(parent, "COMPONENTES", f"Winetricks no container {container.name}")
        self.boxes = []
        grid = QGridLayout()
        grid.setVerticalSpacing(8)
        for i, (verb, desc, _rec) in enumerate(core.WINETRICKS_VERBS):
            cb = QCheckBox(desc)
            cb.setProperty("verb", verb)
            cb.setToolTip(verb)
            grid.addWidget(cb, i, 0)
            self.boxes.append(cb)
        self.lay.addLayout(grid)
        self.extra = QLineEdit()
        self.extra.setPlaceholderText("outros verbos do winetricks, separados por espaco (ex.: vcrun2019 dotnet6)")
        self.lay.addWidget(self.extra)
        self.add_buttons("INSTALAR")

    def verbs(self):
        v = [cb.property("verb") for cb in self.boxes if cb.isChecked()]
        return v + self.extra.text().split()


class RunFileDialog(BaseDialog):
    NEW = "__new__"

    def __init__(self, parent, path: str, containers: list[Container], preselect: str = ""):
        super().__init__(parent, "EXECUTAR ARQUIVO", Path(path).name)
        self.path = path
        form = QFormLayout()
        form.setSpacing(12)
        self.combo = QComboBox()
        for c in containers:
            self.combo.addItem(c.name, c.slug)
        self.combo.addItem("+ Novo container...", self.NEW)
        if preselect:
            i = self.combo.findData(preselect)
            if i >= 0:
                self.combo.setCurrentIndex(i)
        form.addRow(label("CONTAINER", "muted", 2, bold=True), self.combo)
        self.args = QLineEdit()
        self.args.setPlaceholderText("opcional")
        form.addRow(label("ARGUMENTOS", "muted", 2, bold=True), self.args)
        self.lay.addLayout(form)
        self.add_to_list = QCheckBox("Adicionar a lista de programas (para .exe portatil, sem instalador)")
        is_installer = any(k in Path(path).name.lower() for k in ("setup", "install", "instal")) or \
            path.lower().endswith(".msi")
        self.add_to_list.setChecked(not is_installer)
        self.lay.addWidget(self.add_to_list)
        self.add_buttons("EXECUTAR")


# ================================================================ paginas
class Page(QWidget):
    def __init__(self, win: "MainWindow", title: str, subtitle: str, code: str = ""):
        super().__init__()
        self.setObjectName("page")
        self.win = win
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        inner = QWidget()
        inner.setObjectName("page")
        self.lay = QVBoxLayout(inner)
        self.lay.setContentsMargins(36, 26, 36, 26)
        self.lay.setSpacing(16)
        self.lay.addWidget(HudHeader(title, subtitle, code))
        scroll.setWidget(inner)
        outer.addWidget(scroll)

    def refresh(self):
        pass


class DashboardPage(Page):
    def __init__(self, win):
        super().__init__(win, "SYSTEM STATUS", "Ambiente de compatibilidade para programas Windows",
                         "NODE://BRIDGE-0451")
        self.grid = QGridLayout()
        self.grid.setSpacing(14)
        self.lay.addLayout(self.grid)
        self.wait = label("VERIFICANDO SISTEMA...", "muted", 3, bold=True)
        self.grid.addWidget(self.wait, 0, 0)

        self.lay.addSpacing(6)
        self.lay.addWidget(label("ACOES RAPIDAS", "section", 3))
        row = QHBoxLayout()
        row.setSpacing(12)
        row.addWidget(button("▶  ABRIR ROBLOX STUDIO", "primary", win.open_studio))
        row.addWidget(button("EXECUTAR .EXE / .MSI", None, win.pick_and_run))
        row.addWidget(button("NOVO CONTAINER", None, win.new_container))
        row.addWidget(button("REVERIFICAR", "ghost", self.refresh))
        row.addStretch()
        self.lay.addLayout(row)

        info = CutFrame(cut=12, fill=QColor(10, 4, 6))
        il = QVBoxLayout(info)
        il.setContentsMargins(20, 16, 20, 16)
        il.addWidget(label("COMO FUNCIONA", "section", 3))
        il.addWidget(label(
            "O Bridge usa o Wine para rodar programas Windows no Linux. Cada CONTAINER e um 'mini Windows' "
            "separado (C:\\, registro, programas). Instale o programa uma vez dentro de um container e depois "
            "abra pela aba APLICATIVOS ou pelo menu do Zorin. Para o Roblox Studio o Bridge usa o Vinegar, "
            "que aplica as correcoes especificas que o Studio precisa.", "muted", 0.3, wrap=True))
        self.lay.addWidget(info)
        self.lay.addStretch()
        self.worker = None

    def refresh(self):
        if self.worker and self.worker.isRunning():
            return
        self.worker = CheckWorker()
        self.worker.done.connect(self.show_checks)
        self.worker.start()

    def show_checks(self, checks):
        while self.grid.count():
            it = self.grid.takeAt(0)
            if it.widget():
                it.widget().deleteLater()
        for i, ch in enumerate(checks):
            self.grid.addWidget(StatusCard(ch, self.win.install_dep), i // 2, i % 2)
        self.win.set_link_status(all(c.ok or c.optional for c in checks))


class RobloxPage(Page):
    def __init__(self, win):
        super().__init__(win, "ROBLOX STUDIO", "Desenvolvimento Roblox no Linux via Vinegar", "MODULE://RBX-STUDIO")
        self.hero = HeroBanner("ROBLOX STUDIO", "ARASAKA BRIDGE  //  VINEGAR RUNTIME")
        self.lay.addWidget(self.hero)

        row = QHBoxLayout()
        row.setSpacing(12)
        self.btn_open = button("▶  ABRIR ROBLOX STUDIO", "primary", win.open_studio)
        self.btn_open.setMinimumHeight(48)
        spaced(self.btn_open, 3, 16, True)
        self.btn_install = button("INSTALAR VINEGAR + ROBLOX STUDIO", "primary", lambda: win.install_dep("vinegar"))
        self.btn_install.setMinimumHeight(48)
        spaced(self.btn_install, 3, 16, True)
        row.addWidget(self.btn_open, 2)
        row.addWidget(self.btn_install, 2)
        self.lay.addLayout(row)

        tools = QGridLayout()
        tools.setSpacing(10)
        self.tool_buttons = [
            button("CONFIGURAR VINEGAR", None, lambda: win.runner.run([core.cmd_vinegar_manager()]),
                   "Abre a janela do Vinegar (renderizador, FFlags, versao do Studio)"),
            button("ATUALIZAR", None, lambda: win.runner.run([core.cmd_flatpak_update(core.VINEGAR_ID)],
                                                            lambda ok: self.refresh())),
            button("ENCERRAR STUDIO", None, lambda: win.runner.run([core.cmd_flatpak_kill(core.VINEGAR_ID)])),
            button("PASTA DE DADOS", None, lambda: win.open_path(core.vinegar_data_dirs()["data"])),
            button("PASTA DE CONFIG", None, lambda: win.open_path(core.vinegar_data_dirs()["config"])),
            button("DESINSTALAR", "danger", self.uninstall),
        ]
        for i, b in enumerate(self.tool_buttons):
            tools.addWidget(b, i // 3, i % 3)
        self.lay.addLayout(tools)

        cols = QHBoxLayout()
        cols.setSpacing(14)
        tips = CutFrame(cut=12)
        tl = QVBoxLayout(tips)
        tl.setContentsMargins(20, 16, 20, 16)
        tl.addWidget(label("DICAS DE OPERACAO", "section", 3))
        for t in [
            "■  Primeira abertura: o Vinegar baixa o Studio e prepara o Wine (alguns minutos).",
            "■  Login: o Studio abre o navegador; depois de entrar, ele volta sozinho para o Studio.",
            "■  Tela preta ou travando? Em CONFIGURAR VINEGAR troque o renderizador (D3D11 / Vulkan).",
            "■  Use os drivers Vulkan da sua GPU (veja SYSTEM STATUS).",
            "■  Plugins e arquivos locais ficam em PASTA DE DADOS.",
        ]:
            tl.addWidget(label(t, "muted", 0.3, wrap=True))
        cols.addWidget(tips, 3)

        warn = CutFrame(cut=12, border=QColor(90, 8, 14), fill=QColor(14, 4, 6))
        wl = QVBoxLayout(warn)
        wl.setContentsMargins(20, 16, 20, 16)
        wl.addWidget(label("JOGAR ROBLOX", "section", 3))
        wl.addWidget(label(
            "O Roblox Player (jogos) bloqueia o Wine com o anti-cheat. Para jogar, use o Sober, que roda a "
            "versao Android do Roblox no Linux.", "muted", 0.3, wrap=True))
        self.btn_sober = button("INSTALAR SOBER", None, lambda: win.install_dep("sober"))
        wl.addWidget(self.btn_sober)
        wl.addStretch()
        cols.addWidget(warn, 2)
        self.lay.addLayout(cols)
        self.lay.addStretch()

    def refresh(self):
        ok, ver = core.flatpak_info(core.VINEGAR_ID)
        self.btn_open.setVisible(ok)
        self.btn_install.setVisible(not ok)
        for b in self.tool_buttons:
            b.setEnabled(ok)
        self.hero.set_status(f"VINEGAR {ver} · RUNTIME ONLINE" if ok else "VINEGAR NAO INSTALADO · OFFLINE", ok)
        sober, _ = core.flatpak_info(core.SOBER_ID)
        try:
            self.btn_sober.clicked.disconnect()
        except (RuntimeError, TypeError):
            pass
        if sober:
            self.btn_sober.setText("ABRIR SOBER")
            self.btn_sober.clicked.connect(
                lambda: self.win.runner.run([Command(["flatpak", "run", core.SOBER_ID], "abrir Sober",
                                                     detached=True)]))
        else:
            self.btn_sober.setText("INSTALAR SOBER")
            self.btn_sober.clicked.connect(lambda: self.win.install_dep("sober"))

    def uninstall(self):
        if self.win.confirm("DESINSTALAR VINEGAR",
                            "Remover o Vinegar e o Roblox Studio deste computador?\n"
                            "Seus jogos/places publicados continuam na nuvem da Roblox."):
            self.win.runner.run([core.cmd_flatpak_uninstall(core.VINEGAR_ID)], lambda ok: self.refresh())


class AppsPage(Page):
    def __init__(self, win):
        super().__init__(win, "APLICATIVOS", "Containers Windows e programas instalados", "MODULE://WINE-CONTAINERS")
        body = QHBoxLayout()
        body.setSpacing(16)

        left = QVBoxLayout()
        left.addWidget(label("CONTAINERS", "section", 3))
        self.list = QListWidget()
        self.list.setFixedWidth(250)
        self.list.currentItemChanged.connect(lambda *_: self.show_container())
        left.addWidget(self.list, 1)
        left.addWidget(button("+  NOVO CONTAINER", "primary", win.new_container))
        body.addLayout(left)

        self.right = QStackedWidget()
        # vazio
        empty = CutFrame(cut=16)
        el = QVBoxLayout(empty)
        el.setContentsMargins(40, 40, 40, 40)
        el.addStretch()
        lg = QLabel()
        lg.setPixmap(logo_pixmap(90))
        lg.setAlignment(Qt.AlignCenter)
        el.addWidget(lg)
        t = label("NENHUM CONTAINER", None, 4, 20, True)
        t.setAlignment(Qt.AlignCenter)
        el.addWidget(t)
        d = label("Crie um container para instalar seus programas Windows.", "muted", 0.5)
        d.setAlignment(Qt.AlignCenter)
        el.addWidget(d)
        b = button("CRIAR PRIMEIRO CONTAINER", "primary", win.new_container)
        el.addWidget(b, 0, Qt.AlignCenter)
        el.addStretch()
        self.right.addWidget(empty)

        # detalhe
        det = QWidget()
        dl = QVBoxLayout(det)
        dl.setContentsMargins(0, 0, 0, 0)
        dl.setSpacing(12)
        self.c_title = label("", None, 3, 22, True)
        dl.addWidget(self.c_title)
        self.c_meta = label("", "muted", 0.5)
        self.c_meta.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.c_meta.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        dl.addWidget(self.c_meta)
        bar = QHBoxLayout()
        bar.setSpacing(8)
        bar.addWidget(button("INSTALAR PROGRAMA", "primary", self.install_program,
                             "Escolha o instalador .exe ou .msi"))
        bar.addWidget(button("ADICIONAR .EXE", None, self.add_exe, "Adiciona um .exe que ja esta no container"))
        bar.addWidget(button("COMPONENTES", None, self.winetricks, "Winetricks: DXVK, .NET, Visual C++..."))
        tools = QToolButton()
        tools.setText("FERRAMENTAS ▾")
        spaced(tools, 1.5)
        tools.setPopupMode(QToolButton.InstantPopup)
        tools.setCursor(Qt.PointingHandCursor)
        m = QMenu(tools)
        for key, (lbl, _a) in core.TOOLS.items():
            act = QAction(lbl, m)
            act.triggered.connect(lambda _=False, k=key: self.tool(k))
            m.addAction(act)
        m.addSeparator()
        a_drive = QAction("ABRIR DISCO C:", m)
        a_drive.triggered.connect(lambda: self.cur() and win.open_path(self.cur().drive_c))
        m.addAction(a_drive)
        tools.setMenu(m)
        bar.addWidget(tools)
        bar.addStretch()
        dl.addLayout(bar)
        bar = QHBoxLayout()
        bar.setSpacing(8)
        bar.addStretch()
        bar.addWidget(button("ENCERRAR TUDO", None, self.kill, "Fecha todos os programas deste container"))
        bar.addWidget(button("EXCLUIR", "danger", self.delete))
        dl.addLayout(bar)
        dl.addWidget(label("PROGRAMAS", "section", 3))
        self.grid = QListWidget()
        self.grid.setObjectName("grid")
        self.grid.setViewMode(QListWidget.IconMode)
        self.grid.setIconSize(QSize(56, 56))
        self.grid.setGridSize(QSize(150, 128))
        self.grid.setResizeMode(QListWidget.Adjust)
        self.grid.setMovement(QListWidget.Static)
        self.grid.setWordWrap(True)
        self.grid.setSpacing(6)
        self.grid.setUniformItemSizes(True)
        self.grid.setMinimumHeight(320)
        self.grid.itemActivated.connect(self.launch_item)
        self.grid.setContextMenuPolicy(Qt.CustomContextMenu)
        self.grid.customContextMenuRequested.connect(self.app_menu)
        dl.addWidget(self.grid, 1)
        self.empty_apps = label("Nenhum programa ainda. Clique em INSTALAR PROGRAMA e escolha o instalador "
                                "(.exe/.msi). Programas instalados aparecem aqui automaticamente.",
                                "muted", 0.3, wrap=True)
        dl.addWidget(self.empty_apps)
        dl.addWidget(label("Dica: duplo clique abre o programa · botao direito cria atalho no menu do Zorin",
                           "dim", 0.3))
        self.right.addWidget(det)
        body.addWidget(self.right, 1)
        self.lay.addLayout(body, 1)

    # ------------------------------------------------ dados
    def cur(self) -> Container | None:
        it = self.list.currentItem()
        return core.get_container(it.data(Qt.UserRole)) if it else None

    def refresh(self, select: str | None = None):
        keep = select or (self.list.currentItem().data(Qt.UserRole) if self.list.currentItem() else None)
        self.list.blockSignals(True)
        self.list.clear()
        cs = core.list_containers()
        for c in cs:
            it = QListWidgetItem(QIcon(logo_pixmap(22)), c.name.upper())
            it.setData(Qt.UserRole, c.slug)
            f = it.font()
            f.setBold(True)
            f.setLetterSpacing(QFont.AbsoluteSpacing, 1.5)
            it.setFont(f)
            self.list.addItem(it)
            if c.slug == keep:
                self.list.setCurrentItem(it)
        if self.list.currentItem() is None and self.list.count():
            self.list.setCurrentRow(0)
        self.list.blockSignals(False)
        self.show_container()

    def show_container(self):
        c = self.cur()
        if not c:
            self.right.setCurrentIndex(0)
            return
        self.right.setCurrentIndex(1)
        self.c_title.setText(c.name.upper())
        state = "PRONTO" if c.initialized else "NAO INICIALIZADO"
        self.c_meta.setText(f"{'64' if c.arch == 'win64' else '32'}-BIT  ·  {state}  ·  "
                            f"{'DXVK' if c.meta.get('dxvk') else 'WINED3D'}  ·  {c.path}")
        self.c_meta.setToolTip(str(c.path))
        self.grid.clear()
        apps = c.apps()
        for a in apps:
            if not a.icon:
                icon = QIcon()
            elif a.icon.startswith("/"):
                icon = QIcon(a.icon)
            else:
                icon = QIcon.fromTheme(a.icon)
            if icon.isNull():
                icon = QIcon(str(core.ASSETS / "arasaka-bridge.svg"))
            it = QListWidgetItem(icon, a.name)
            it.setData(Qt.UserRole, a.target)
            it.setData(Qt.UserRole + 1, a.source)
            it.setToolTip(a.target)
            it.setTextAlignment(Qt.AlignHCenter | Qt.AlignTop)
            it.setSizeHint(QSize(138, 116))
            self.grid.addItem(it)
        self.grid.setVisible(bool(apps))
        self.empty_apps.setVisible(not apps)

    def app_of(self, it) -> App | None:
        c = self.cur()
        if not c or not it:
            return None
        t = it.data(Qt.UserRole)
        for a in c.apps():
            if a.target == t:
                return a
        return None

    # ------------------------------------------------ acoes
    def launch_item(self, it):
        c, a = self.cur(), self.app_of(it)
        if c and a:
            self.win.runner.run([core.cmd_launch_app(self.win.cfg, c, a)])

    def app_menu(self, pos):
        it = self.grid.itemAt(pos)
        a = self.app_of(it)
        c = self.cur()
        if not a or not c:
            return
        m = QMenu(self)
        m.addAction("EXECUTAR", lambda: self.launch_item(it))
        m.addSeparator()
        m.addAction("CRIAR ATALHO NO MENU", lambda: self.shortcut(c, a, False))
        m.addAction("CRIAR ATALHO NO MENU + AREA DE TRABALHO", lambda: self.shortcut(c, a, True))
        m.addAction("ABRIR LOCAL DO ARQUIVO", lambda: self.win.open_path(Path(a.target).parent))
        m.addSeparator()
        m.addAction("REMOVER DA LISTA", lambda: (c.remove_app(a.target), self.show_container()))
        m.exec(self.grid.viewport().mapToGlobal(pos))

    def shortcut(self, c, a, desktop):
        p = core.create_shortcut(c, a, desktop)
        self.win.console.append(f"   ■ atalho criado: {p}", "ok")
        self.win.toast(f"Atalho de {a.name} criado no menu")

    def install_program(self):
        c = self.cur()
        if c:
            self.win.pick_and_run(c.slug)

    def add_exe(self):
        c = self.cur()
        if not c:
            return
        start = str(c.drive_c / "Program Files") if (c.drive_c / "Program Files").is_dir() else str(c.drive_c)
        path, _ = QFileDialog.getOpenFileName(self, "Escolha o .exe do programa", start,
                                              "Programas Windows (*.exe *.lnk *.bat)")
        if path:
            c.add_app(App(Path(path).stem, path))
            self.show_container()

    def winetricks(self):
        c = self.cur()
        if not c:
            return
        d = WinetricksDialog(self, c)
        if d.exec() == QDialog.Accepted and d.verbs():
            verbs = d.verbs()
            if "dxvk" in verbs:
                c.meta["dxvk"] = True
                c.save()
            self.win.runner.run([core.cmd_winetricks(self.win.cfg, c, verbs)], lambda ok: self.show_container())

    def tool(self, key):
        c = self.cur()
        if c:
            self.win.runner.run([core.cmd_tool(self.win.cfg, c, key)])

    def kill(self):
        c = self.cur()
        if c:
            self.win.runner.run([core.cmd_kill(self.win.cfg, c)])

    def delete(self):
        c = self.cur()
        if c and self.win.confirm("EXCLUIR CONTAINER",
                                  f"Excluir o container '{c.name}' e TODOS os programas instalados nele?\n"
                                  f"{c.path}\n\nIsso nao pode ser desfeito."):
            self.win.runner.run([core.cmd_kill(self.win.cfg, c)],
                                lambda ok: (core.delete_container(c), self.refresh()))


class SettingsPage(Page):
    def __init__(self, win):
        super().__init__(win, "CONFIGURACOES", "Preferencias do Bridge", f"BUILD://{VERSION}")
        cfg = win.cfg
        box = CutFrame(cut=12)
        form = QFormLayout(box)
        form.setContentsMargins(22, 20, 22, 20)
        form.setSpacing(14)
        self.wine = QLineEdit(cfg["wine"])
        self.wine.setPlaceholderText("wine")
        self.wine.editingFinished.connect(lambda: self._set("wine", self.wine.text().strip() or "wine"))
        form.addRow(label("COMANDO DO WINE", "muted", 2, bold=True), self.wine)
        self.wt = QLineEdit(cfg["winetricks"])
        self.wt.editingFinished.connect(lambda: self._set("winetricks", self.wt.text().strip() or "winetricks"))
        form.addRow(label("WINETRICKS", "muted", 2, bold=True), self.wt)
        for key, text in [("fonts_new", "Novos containers ja vem com DXVK, fontes, Visual C++ e modo Windows 10"),
                          ("esync", "Ativar esync/fsync (mais desempenho)"),
                          ("hide_wine_debug", "Esconder mensagens de debug do Wine no terminal"),
                          ("show_console", "Mostrar o terminal ao abrir o Bridge")]:
            cb = QCheckBox(text)
            cb.setChecked(bool(cfg[key]))
            cb.toggled.connect(lambda v, k=key: self._set(k, v))
            form.addRow("", cb)
        self.lay.addWidget(box)
        row = QHBoxLayout()
        row.addWidget(button("PASTA DOS CONTAINERS", None, lambda: win.open_path(core.PREFIXES)))
        row.addWidget(button("PASTA DE LOGS", None, lambda: win.open_path(core.LOGS)))
        row.addStretch()
        self.lay.addLayout(row)
        about = CutFrame(cut=12, fill=QColor(10, 4, 6))
        al = QVBoxLayout(about)
        al.setContentsMargins(22, 18, 22, 18)
        al.addWidget(label(f"{APP_NAME}  v{VERSION}", None, 3, 16, True))
        al.addWidget(label("Camada de compatibilidade Windows para Zorin OS. Usa Wine, Winetricks, DXVK e "
                           "Vinegar (Roblox Studio). Arasaka e marca da CD PROJEKT RED; uso pessoal de fa.",
                           "muted", 0.3, wrap=True))
        self.lay.addWidget(about)
        self.lay.addStretch()

    def _set(self, k, v):
        self.win.cfg[k] = v


# ================================================================ janela principal
class MainWindow(QMainWindow):
    def __init__(self, cfg: Config, open_file: str | None = None):
        super().__init__()
        self.cfg = cfg
        self.setWindowTitle(APP_NAME)
        self.setWindowIcon(QIcon(str(core.ASSETS / "arasaka-bridge.svg")))
        self.resize(1280, 860)
        self.setMinimumSize(1020, 680)
        self.runner = Runner(cfg)

        root = QWidget()
        root.setObjectName("root")
        h = QHBoxLayout(root)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        side = QFrame()
        side.setObjectName("sidebar")
        side.setFixedWidth(232)
        sl = QVBoxLayout(side)
        sl.setContentsMargins(0, 0, 0, 14)
        sl.setSpacing(2)
        sl.addWidget(SidebarBrand())
        sl.addSpacing(10)
        self.nav = QButtonGroup(self)
        self.stack = QStackedWidget()
        self.pages = {
            "dash": DashboardPage(self),
            "roblox": RobloxPage(self),
            "apps": AppsPage(self),
            "settings": SettingsPage(self),
        }
        for i, (key, text) in enumerate([("dash", "PAINEL"), ("roblox", "ROBLOX STUDIO"),
                                         ("apps", "APLICATIVOS"), ("settings", "CONFIGURACOES")]):
            b = QPushButton(f"{i + 1:02d}   {text}")
            b.setObjectName("nav")
            b.setCheckable(True)
            b.setCursor(Qt.PointingHandCursor)
            spaced(b, 2.5)
            b.clicked.connect(lambda _=False, k=key: self.go(k))
            self.nav.addButton(b, i)
            sl.addWidget(b)
            self.stack.addWidget(self.pages[key])
        sl.addStretch()
        self.link = label("■  NETWATCH LINK", "muted", 1, 11, True)
        self.link.setContentsMargins(20, 0, 0, 0)
        sl.addWidget(self.link)
        ver = label(f"BRIDGE v{VERSION}{'  ·  DEMO' if core.DEMO else ''}", "dim", 2, 11)
        ver.setContentsMargins(20, 0, 0, 0)
        sl.addWidget(ver)
        h.addWidget(side)

        right = QSplitter(Qt.Vertical)
        right.addWidget(self.stack)
        self.console = Console(self.runner)
        right.addWidget(self.console)
        right.setStretchFactor(0, 5)
        right.setStretchFactor(1, 2)
        right.setSizes([700, 150])
        self.splitter = right
        right.setHandleWidth(2)
        h.addWidget(right, 1)
        self.setCentralWidget(root)
        if not cfg["show_console"]:
            self.console.toggle()

        self.toast_lbl = QLabel(self)
        self.toast_lbl.setStyleSheet("background:#000; border:1px solid #e3121f; padding:10px 18px; color:#ececf0;")
        self.toast_lbl.hide()

        self.go("dash")
        self.pages["dash"].refresh()
        if open_file:
            QTimer.singleShot(300, lambda: self.run_file(open_file))

    # ------------------------------------------------ navegacao / util
    def go(self, key: str):
        keys = list(self.pages)
        self.nav.button(keys.index(key)).setChecked(True)
        self.stack.setCurrentWidget(self.pages[key])
        if key != "dash":
            self.pages[key].refresh()

    def set_link_status(self, ok: bool):
        self.link.setObjectName("muted" if ok else "red")
        self.link.setText("■  NETWATCH LINK · ONLINE" if ok else "■  SISTEMA INCOMPLETO")
        self.link.style().unpolish(self.link)
        self.link.style().polish(self.link)

    def toast(self, text: str):
        self.toast_lbl.setText(text)
        spaced(self.toast_lbl, 1)
        self.toast_lbl.adjustSize()
        self.toast_lbl.move(self.width() - self.toast_lbl.width() - 24, 20)
        self.toast_lbl.raise_()
        self.toast_lbl.show()
        QTimer.singleShot(3200, self.toast_lbl.hide)

    def confirm(self, title: str, text: str) -> bool:
        mb = QMessageBox(self)
        mb.setWindowTitle(title)
        mb.setText(text)
        mb.setIcon(QMessageBox.Warning)
        yes = mb.addButton("CONFIRMAR", QMessageBox.AcceptRole)
        yes.setProperty("kind", "danger")
        mb.addButton("CANCELAR", QMessageBox.RejectRole)
        mb.exec()
        return mb.clickedButton() is yes

    def open_path(self, p: Path):
        p = Path(p)
        if not p.exists():
            self.toast("Pasta ainda nao existe")
            return
        self.runner.run([core.cmd_open_folder(p)])

    # ------------------------------------------------ acoes globais
    def install_dep(self, key: str):
        cmds = core.dep_commands(key)
        if not cmds:
            return
        if key in ("wine", "vulkan", "flatpak") and not core.DEMO:
            self.toast("Digite sua senha na janela que vai abrir")

        def done(ok):
            self.pages["dash"].refresh()
            self.pages["roblox"].refresh()
            self.toast("Instalacao concluida" if ok else "A instalacao falhou: veja o terminal")
        self.runner.run(cmds, done)

    def open_studio(self):
        ok, _ = core.flatpak_info(core.VINEGAR_ID)
        if not ok:
            self.go("roblox")
            if self.confirm("ROBLOX STUDIO", "O Vinegar (que roda o Roblox Studio) ainda nao esta instalado.\n"
                                             "Instalar agora pelo Flathub?"):
                self.install_dep("vinegar")
            return
        self.runner.run([core.cmd_open_studio()])
        self.toast("Abrindo Roblox Studio...")

    def new_container(self, suggested: str = "", then=None):
        d = NewContainerDialog(self, self.cfg, suggested)
        if d.exec() != QDialog.Accepted:
            return None
        name, arch, verbs = d.values()
        c = core.new_container(name or "Container", arch, "dxvk" in verbs)
        self.go("apps")
        self.pages["apps"].refresh(c.slug)

        def done(ok):
            self.pages["apps"].refresh(c.slug)
            self.toast(f"Container {c.name} pronto" if ok else "Falha ao criar o container")
            if ok and then:
                then(c)
        self.runner.run(core.cmd_init(self.cfg, c, verbs), done)
        return c

    def pick_and_run(self, preselect: str = ""):
        path, _ = QFileDialog.getOpenFileName(self, "Escolha o programa Windows", str(Path.home() / "Downloads"),
                                              "Programas Windows (*.exe *.msi *.bat *.lnk);;Todos (*)")
        if path:
            self.run_file(path, preselect if isinstance(preselect, str) else "")

    def run_file(self, path: str, preselect: str = ""):
        cs = core.list_containers()
        d = RunFileDialog(self, path, cs, preselect or self.cfg["default_container"])
        if d.exec() != QDialog.Accepted:
            return
        slug = d.combo.currentData()
        args = d.args.text().strip()
        add = d.add_to_list.isChecked()

        def go_run(c: Container):
            self.cfg["default_container"] = c.slug
            if add:
                c.add_app(App(Path(path).stem, path, args))
            self.go("apps")
            self.pages["apps"].refresh(c.slug)
            self.runner.run([core.cmd_run_file(self.cfg, c, path, args)])

        if slug == RunFileDialog.NEW:
            self.new_container(Path(path).stem.split("_")[0].split("-")[0][:24], go_run)
        else:
            c = core.get_container(slug)
            if c and not c.initialized:
                self.runner.run(core.cmd_init(self.cfg, c, []), lambda ok: ok and go_run(c))
            elif c:
                go_run(c)


def main(argv: list[str] | None = None):
    argv = list(sys.argv if argv is None else argv)
    QApplication.setApplicationName(core.APP_ID)          # WM_CLASS = arasaka-bridge
    QApplication.setApplicationDisplayName(APP_NAME)
    QApplication.setDesktopFileName(core.APP_ID)           # app_id no Wayland
    app = QApplication(argv)
    load_fonts()
    app.setStyleSheet(stylesheet())
    app.setWindowIcon(QIcon(str(core.ASSETS / "arasaka-bridge.svg")))
    open_file = next((a for a in argv[1:] if not a.startswith("-") and core.is_windows_file(a)), None)
    win = MainWindow(Config(), open_file)
    # visual Cyberpunk (CRT, glitch, inicialização, barra de status); sem a tela de inicialização nas prévias
    fx.install(win, name="ARASAKA BRIDGE", icon=core.ASSETS / "arasaka-bridge.svg", boot=not any(a.startswith("--screenshot=") for a in argv))
    win.show()
    QTimer.singleShot(0, lambda: win.splitter.setSizes([int(win.height() * 0.8), int(win.height() * 0.2)]))
    shot = next((a.split("=", 1)[1] for a in argv if a.startswith("--screenshot=")), None)
    if shot:  # usado para gerar previas: --screenshot=arquivo.png[,pagina]
        path, _, page = shot.partition(",")

        def grab():
            win.grab().save(path)
            app.quit()
        if page:
            QTimer.singleShot(200, lambda: win.go(page))
        QTimer.singleShot(2600, grab)
    return app.exec()
