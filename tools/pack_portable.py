#!/usr/bin/env python3
"""Assemble source portable Windows package, including complete Python/Tk if available."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tarfile
import urllib.request
import zipfile
from fetch_windows_bins import ROOT, download, fetch

NAME = 'CNVideoDownloader-Windows-Portable'


def bundle_python(runtime: Path):
    """Use full standalone CPython, because the official embed ZIP omits Tcl/Tk."""
    cache = ROOT / '.cache'
    metadata = download('https://api.github.com/repos/astral-sh/python-build-standalone/releases/latest', cache / 'python-release.json')
    assets = json.loads(metadata.read_text(encoding='utf-8'))['assets']
    choices = [a for a in assets if 'cpython-3.12.' in a['name']
               and 'x86_64-pc-windows-msvc' in a['name']
               and a['name'].endswith('install_only.tar.gz')]
    if not choices:
        raise RuntimeError('No compatible full Windows CPython asset found')
    asset = choices[0]
    archive = download(asset['browser_download_url'], cache / asset['name'])
    destination = runtime / 'python'
    if not (destination / 'pythonw.exe').exists():
        with tarfile.open(archive) as source:
            source.extractall(runtime, filter='data')
    if not (destination / 'DLLs' / '_tkinter.pyd').exists():
        raise RuntimeError('Full Python distribution is missing tkinter')
    wheels = runtime / 'wheels'
    wheels.mkdir(exist_ok=True)
    subprocess.run([sys.executable, '-m', 'pip', 'download', '--only-binary=:all:',
                    '--platform', 'win_amd64', '--python-version', '312', '--implementation', 'cp',
                    '--abi', 'cp312', '--dest', str(wheels), '-r', str(ROOT / 'requirements.txt')], check=True)
    site = destination / 'Lib' / 'site-packages'
    site.mkdir(parents=True, exist_ok=True)
    for wheel in wheels.glob('*.whl'):
        with zipfile.ZipFile(wheel) as source:
            source.extractall(site)
    (runtime / 'python-source.json').write_text(json.dumps({'source': asset['browser_download_url'],
        'distribution': 'Astral python-build-standalone; full CPython with Tcl/Tk'}, indent=2), encoding='utf-8')


def write_windows(path: Path, content: str, encoding='utf-8-sig'):
    path.write_bytes(content.replace('\r\n', '\n').replace('\n', '\r\n').encode(encoding))


def pack(skip_fetch=False, skip_python=False):
    if not skip_fetch:
        fetch(ROOT / 'runtime')
    if not skip_python:
        bundle_python(ROOT / 'runtime')
    target = ROOT / 'dist' / NAME
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for folder in ('app', 'tools', 'assets', 'tests'):
        shutil.copytree(ROOT / folder, target / folder, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copytree(ROOT / 'runtime', target / 'runtime', ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    for name in ('README.md', 'REQUIREMENTS.md', 'BUILD_REPORT.md', 'requirements.txt', 'pytest.ini', 'build_windows.bat', 'pack_portable.sh', 'run_linux_smoke.sh'):
        shutil.copy2(ROOT / name, target / name)
    built = ROOT / 'dist' / 'windows-build'
    if built.exists():
        shutil.copytree(built, target / 'windows-build')
    write_windows(target / '启动下载器.bat', '''@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist "%~dp0runtime\\python\\pythonw.exe" (
  start "" "%~dp0runtime\\python\\pythonw.exe" "%~dp0app\\main.py"
  exit /b
)
echo 本包缺少完整 Python，请安装 Python 3.11 或更新版本（勾选 Tcl/Tk 和 Add to PATH）。
py -3 -m pip install -r requirements.txt
if errorlevel 1 goto failed
py -3 -m app.main
if errorlevel 1 goto failed
exit /b
:failed
echo 启动失败，请查看 README.md 或运行 诊断启动.bat。
pause
''', 'utf-8')
    write_windows(target / '诊断启动.bat', '''@echo off
chcp 65001 >nul
cd /d "%~dp0"
if exist runtime\\python\\python.exe (
 runtime\\python\\python.exe -m app.main
) else (
 py -3 -m app.main
)
pause
''', 'utf-8')
    write_windows(target / '启动下载器.vbs', '''Option Explicit
Dim shell, fso, base, python, entry
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")
base = fso.GetParentFolderName(WScript.ScriptFullName)
shell.CurrentDirectory = base
python = fso.BuildPath(base, "runtime\\python\\pythonw.exe")
entry = fso.BuildPath(base, "app\\main.py")
If fso.FileExists(python) Then
 shell.Run Chr(34) & python & Chr(34) & " " & Chr(34) & entry & Chr(34), 0, False
Else
 shell.Run Chr(34) & fso.BuildPath(base, "启动下载器.bat") & Chr(34), 1, False
End If
''', 'utf-16')
    has_python = (target / 'runtime/python/pythonw.exe').exists()
    instructions = '''国内视频下载器 — Windows 10/11 64 位

1. 将 ZIP 完整解压到一个文件夹，请勿直接在压缩包中运行。
2. 双击“启动下载器.vbs”（无控制台）；也可双击“启动下载器.bat”。
3. 粘贴视频链接，选择保存位置，点击“开始下载”。最多同时下载 2 个视频。

''' + ('已附带完整 Windows Python（含 Tcl/Tk）及界面依赖，无需安装 Python。\n' if has_python else '此包不含 Python：请安装 Python 3.11+（含 Tcl/Tk，勾选 PATH），首次运行 BAT 会安装依赖，需要联网。\n') + '''
仅使用原版 yt-dlp，不提供 DRM、会员、付费、登录或地区限制破解。
腾讯、优酷、爱奇艺、哔哩哔哩等是否可下载取决于 yt-dlp 支持及视频权限，不能保证所有视频可用。
仅下载您有权保存的内容。播放列表默认只处理当前视频。
取消会终止当前任务，已下载的部分文件可能保留，再次下载可续传。
若双击没有窗口，请运行“诊断启动.bat”查看错误。
“清空列表状态”只清除界面记录，不删除已下载文件。
此包在 Linux 组装，未经过真实 Windows 运行验证；Windows 构建方法见 README.md。
'''
    write_windows(target / 'README使用说明.txt', instructions)
    archive = shutil.make_archive(str(ROOT / 'dist' / NAME), 'zip', target.parent, target.name)
    print(f'Portable directory: {target}\nZIP: {archive}')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--skip-fetch', action='store_true')
    parser.add_argument('--skip-python', action='store_true', help='Explicitly ship source-only with install instructions')
    options = parser.parse_args()
    pack(options.skip_fetch, options.skip_python)
