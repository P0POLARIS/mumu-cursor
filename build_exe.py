"""编译 MUMU光标.exe（.NET Framework csc，零依赖）。
顺便编译一个控制台版本 build/MUMUCursor_console.exe，用于 --shot / --test 这类无界面自检。
"""
import os, re, subprocess, sys, pathlib, time

ROOT = pathlib.Path(__file__).resolve().parent
CSC = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe"
WPF = r"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\WPF"

# 资源：所有 png / wav 以文件名嵌入
res = []
for p in sorted((ROOT / "assets").glob("*")):
    if p.suffix.lower() in (".png", ".wav", ".cur"):
        res += [f"/resource:{p}"]

# LOCK-ROTATE: 目标被正在运行的进程占用时，Windows 允许把镜像改名（FILE_SHARE_DELETE），
# 于是先把它挪走、再往原路径写新文件；旧文件等进程退出后由系统回收。
def rotate_locked(path):
    if not os.path.exists(path):
        return None
    try:
        f = open(path, "r+b"); f.close()
        return None
    except OSError:
        pass
    aside = str(path) + ".old-" + time.strftime("%H%M%S")
    try:
        os.replace(path, aside)
        return aside
    except OSError:
        return None

def build(target, out):
    out.parent.mkdir(parents=True, exist_ok=True)
    rotate_locked(out)
    args = [
        CSC, "/nologo", f"/target:{target}", "/optimize+", "/platform:anycpu",
        f"/out:{out}",
        "/r:System.dll", "/r:System.Drawing.dll", "/r:System.Windows.Forms.dll",
        "/r:System.Core.dll",
        # WebP 等 GDI+ 读不了的图片走 WIC 解码（WPF 的 BitmapDecoder，系统自带）
        f"/r:{WPF}\\PresentationCore.dll", f"/r:{WPF}\\WindowsBase.dll", "/r:System.Xaml.dll",
        f"/win32icon:{ROOT / 'assets' / 'app.ico'}",
    ] + res + [str(ROOT / "MUMUCursor.cs")]
    p = subprocess.run(args, capture_output=True, text=True, encoding="utf-8", errors="replace")
    txt = (p.stdout or "") + (p.stderr or "")
    open(str(ROOT / "build.log"), "a", encoding="utf-8").write(f"\n=== {target} -> {out.name}\n{txt}")
    print(txt.encode("ascii", "replace").decode("ascii"))
    return p.returncode

rc = build("winexe", ROOT / "MUMU光标.exe")
if rc == 0:
    print("OK", (ROOT / "MUMU光标.exe").stat().st_size, "bytes")
    rc2 = build("exe", ROOT / "build" / "MUMUCursor_console.exe")
    print("console rc", rc2)
sys.exit(rc)
