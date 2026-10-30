# Build CN Video Downloader — Windows desktop GUI

## Goal
Create a foolproof Windows desktop video downloader for non-technical users.
Chinese UI. Sites: Tencent Video, Youku, iQiyi, Bilibili, and anything yt-dlp supports.

## Stack
- Python 3.11+
- customtkinter for modern GUI
- yt-dlp via subprocess calling bundled `yt-dlp.exe` on Windows (or `yt-dlp` module as fallback)
- Packaging: create a **portable Windows folder** that includes:
  1. Full app source under `app/`
  2. Scripts to produce a double-click launcher
  3. A `tools/fetch_windows_bins.py` that downloads official Windows yt-dlp.exe + ffmpeg essentials zip into `runtime/`
  4. A `pack_portable.sh` / `pack_portable.py` that builds `dist/CNVideoDownloader-Windows-Portable/` ready to zip
  5. Prefer also producing a real GUI .exe via PyInstaller when run ON Windows (`build_windows.bat`). On Linux, produce the portable layout + try wine if available.

## App features (v1)
1. Chinese UI window title: 「国内视频下载器」
2. Large multiline text box: paste one or many URLs (newline / comma / whitespace separated)
3. Button: 从文件导入 (.txt)
4. Save folder picker (default: user's Downloads)
5. Buttons: 开始下载 / 取消 / 清空列表状态
6. Progress: overall progress bar + listbox/tree of each URL with status (等待/下载中/完成/失败) and short message
7. Concurrent downloads: max 2 at a time (thread pool)
8. Log panel at bottom (scrollable)
9. On failure: friendly Chinese messages for common cases (DRM, VIP/login required, geo-block, network, unsupported)
10. Do NOT claim DRM/VIP circumvention. Use stock yt-dlp only. No cookies in v1 unless trivial.

## yt-dlp invocation
- Prefer bundled binary next to app: `runtime/yt-dlp.exe` (Windows) or system yt-dlp
- ffmpeg from `runtime/ffmpeg.exe` via `--ffmpeg-location`
- Sensible args: `-o "%(title).80B [%(id)s].%(ext)s"` under chosen folder, `--no-mtime`, `--newline`, merge best video+audio when needed
- Parse progress from yt-dlp stdout (`--progress` / `--newline`)

## Project layout to create
```
/workspace/cn-video-downloader/
  README.md                 # Chinese user + developer docs
  REQUIREMENTS.md
  requirements.txt
  app/
    __init__.py
    main.py                 # entry: python -m app.main or python app/main.py
    gui.py                  # CustomTkinter UI
    downloader.py           # yt-dlp wrapper, queue, cancel
    url_parser.py           # split/normalize URLs
    messages.py             # Chinese error mapping
    paths.py                # runtime binary discovery, Downloads default
  tests/
    test_url_parser.py
    test_messages.py
    test_downloader_args.py
  tools/
    fetch_windows_bins.py   # download yt-dlp.exe + ffmpeg for Windows into runtime/
    pack_portable.py        # assemble dist/CNVideoDownloader-Windows-Portable/
  build_windows.bat         # for user/CI on Windows: pip + pyinstaller onefile or onedir
  run_linux_smoke.sh        # launch GUI briefly / headless import check on Linux
  assets/                   # optional icon
```

## Deliverables you must produce
1. Working source that imports cleanly on Linux
2. Unit tests passing (`pytest`)
3. `dist/CNVideoDownloader-Windows-Portable/` folder containing:
   - `启动下载器.vbs` (pythonw, no console) and `启动下载器.bat`
   - `README使用说明.txt` (Chinese, 3-step usage + limitations)
   - `app/` code
   - `runtime/` with placeholder or actual windows bins if fetch succeeds from Linux (yt-dlp.exe and ffmpeg windows builds CAN be downloaded from Linux)
   - Embedded Windows Python (python-embed-amd64) with pip-installed customtkinter + deps, OR clear instructions — **prefer embedding** so end user double-clicks and it works with zero install
4. Zip: `dist/CNVideoDownloader-Windows-Portable.zip`

## Embedded Python portable approach (required for foolproof)
On Linux in pack_portable.py:
1. Download https://www.python.org/ftp/python/3.12.7/python-3.12.7-embed-amd64.zip
2. Extract to runtime/python/
3. Enable site-packages via python312._pth (uncomment import site)
4. Download get-pip.py and install pip into embeddable python using... wait: embeddable python is Windows PE, cannot run on Linux.
   
**Problem**: Cannot pip-install into Windows embeddable Python from Linux.

**Solution A (preferred)**: Bundle wheels of customtkinter, darkdetect, packaging, yt-dlp (pure python) into `runtime/wheels/` and a `bootstrap.bat` that on first run uses embeddable python + get-pip + install from local wheels — still needs one run. Better: include pre-extracted `Lib/site-packages` by downloading platform-independent wheels and unpacking them into `runtime/python/Lib/site-packages` ourselves on Linux (unzip .whl files). customtkinter depends on tkinter — **embeddable Python does NOT include tkinter/tcl!**

**Critical**: Python embeddable lacks tkinter. CustomTkinter needs tkinter.

**Revised packaging strategy**:
1. Use **PyInstaller onedir build instructions** for Windows (`build_windows.bat`) that produces `CN视频下载器.exe`
2. On Linux, download Windows `yt-dlp.exe` + `ffmpeg` into `runtime/`
3. Ship a **complete source portable** + a **standalone launcher approach**:
   - Best path that works from Linux WITHOUT wine: create an Auto-Hotkey-free solution using **Tauri/Go/Rust** — too heavy.
   - OR install **wine** + Windows Python in wine + PyInstaller → real .exe
   - OR ship portable with **WinPython / full Python Windows zip that includes tk** 

**Practical decision for this task**:
1. Implement the full CustomTkinter app + tests.
2. Install wine64 + download Windows Python installer or embed — actually use **official python windows nuget or the full python stand-alone**...

Simplest foolproof path that WE can finish on Linux today:
1. `sudo apt-get install -y wine64 wine` (or winehq) if possible
2. Download python-3.12.x-amd64.exe Windows installer, silent install into wine prefix
3. pip install pyinstaller customtkinter yt-dlp under wine python
4. PyInstaller --onefile or onedir → `CN视频下载器.exe`
5. Bundle ffmpeg + ensure yt-dlp is included (PyInstaller collects yt-dlp; still bundle ffmpeg.exe next to exe)
6. Zip the onedir folder

If wine install fails or is too slow:
- Fall back to portable folder: app source + runtime/yt-dlp.exe + ffmpeg + `下载器.bat` that calls yt-dlp for each URL (CLI wrapper GUI via PowerShell WinForms or python if present) — weaker.
- ALSO provide `build_windows.bat` for one-click build on any Windows PC with Python.

**DO THIS ORDER**:
1. Write all app code + tests first, make tests pass on Linux
2. Fetch windows yt-dlp.exe + ffmpeg into runtime/
3. Try wine+pyinstaller path for real .exe
4. Always produce zip of whatever works + Chinese README
5. Smoke test: import modules, run pytest, dry-run downloader args, optionally live-download a short YouTube URL with yt-dlp on Linux to prove pipeline

## Code quality
- UTF-8 everywhere
- Type hints where reasonable
- No DRM hacks
- Cancel = kill subprocess for current items
- Thread-safe UI updates via `after()`

Start implementing now. Create all files. Run tests. Then packaging.
