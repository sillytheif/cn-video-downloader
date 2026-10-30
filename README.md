# 国内视频下载器

面向非技术用户的中文 Windows 桌面下载器。界面用 CustomTkinter，下载引擎为原版 [yt-dlp](https://github.com/yt-dlp/yt-dlp)（可选 ffmpeg 合并音视频）。

腾讯视频、优酷、爱奇艺、哔哩哔哩等站点的实际可用性取决于 yt-dlp、视频权限和网站接口；**不保证**每个视频都能下。不支持 DRM / 会员 / 付费 / 登录破解或地区限制绕过。请只下载你有权保存的内容。

## Windows 用户：三步使用

若你已拿到发布包 `CNVideoDownloader-Windows-Portable.zip`：

1. 完整解压（保留整个文件夹，不要只拷启动脚本）。
2. 双击 `启动下载器.vbs`（无黑窗口），或 `启动下载器.bat`。
3. 粘贴一个或多个视频链接，选择保存目录，点「开始下载」。

无窗口时运行同目录下的 `诊断启动.bat`。默认保存到用户「下载」文件夹；最多同时下载 2 个。支持 UTF-8 / GB18030 的 `.txt` 批量链接；空白或逗号分隔，自动去重。默认不整表下载播放列表。

## 仓库里有什么

| 路径 | 说明 |
|------|------|
| `app/` | GUI 与下载队列源码 |
| `tools/` | 拉取 Windows 依赖、打包脚本 |
| `tests/` | pytest |
| `requirements.txt` | Python 依赖 |
| `pack_portable.sh` / `tools/pack_portable.py` | 生成便携 ZIP |
| `build_windows.bat` | 在 **Windows** 上用 PyInstaller 打 onedir |
| `runtime/`、`dist/` | **不入库**（本地构建产物，见 `.gitignore`） |

本仓库只含源码与构建脚本；体积较大的 Windows Python / yt-dlp.exe / ffmpeg 需按下方步骤在本机下载生成。

---

## 根据源码构建

### 环境要求

- Python **3.11+**（开发与跑测试）
- 联网（首次拉取 yt-dlp、ffmpeg、Windows CPython 等）
- Linux 开发还需系统 Tk（如 `python3-tk`）；无桌面可用 Xvfb
- 打 **Windows 便携包**可在 Linux 或 Windows 上执行打包脚本
- 打 **PyInstaller .exe** 需在 Windows 上运行 `build_windows.bat`

### 1. 克隆与安装开发依赖

```bash
git clone https://github.com/sillytheif/cn-video-downloader.git
cd cn-video-downloader

python -m venv .venv
# Windows: .venv\Scripts\activate
source .venv/bin/activate

pip install -r requirements.txt pytest
```

### 2. 跑测试（可选但推荐）

```bash
pytest -q
# Linux GUI 冒烟（需 Tk / 可用 Xvfb）:
./run_linux_smoke.sh
# 直接开界面:
python -m app.main
```

### 3. 生成 Windows 便携包（推荐分发方式）

会下载并写入 `runtime/`，再产出 `dist/CNVideoDownloader-Windows-Portable.zip`（内含 Windows 完整 CPython + Tcl/Tk、customtkinter、`yt-dlp.exe`、`ffmpeg`/`ffprobe`，目标用户无需再装 Python）。

```bash
# 拉取 Windows 侧二进制与嵌入式 Python
python tools/fetch_windows_bins.py

# Linux / macOS:
./pack_portable.sh

# 或跨平台:
python tools/pack_portable.py
```

常用参数：

- `--skip-fetch`：复用已有 `runtime/`，不再下载
- `--skip-python`：不捆绑嵌入式 Python（生成的包要求目标机器已装 Python，一般不推荐给小白用户）

产物路径：`dist/CNVideoDownloader-Windows-Portable.zip`。把 ZIP 发给用户即可。

依赖来源会记在 `runtime/binaries.json`、`runtime/python-source.json`（含 SHA-256 记录；这不等于独立代码签名验证）。下载缓存默认在 `.cache/`，删掉可强制更新版本。

### 4. 在 Windows 上打 PyInstaller 包（可选）

在 **Windows 10/11 x64** 上，已安装 Python 3.11+ 并联网：

1. 双击或在项目根目录运行 `build_windows.bat`
2. 脚本会建构建用虚拟环境、安装 PyInstaller，生成  
   `dist/windows-build/CN视频下载器/CN视频下载器.exe` 及旁路 `runtime`
3. **请分发整个 onedir 文件夹**，不要只发单个 exe  
4. 之后再跑 `pack_portable.py` 时，可把该 onedir 一并打进 ZIP

### 5. 本机构建检查清单

- [ ] `pytest -q` 通过  
- [ ] `dist/CNVideoDownloader-Windows-Portable.zip` 已生成  
- [ ] 在真机 Win10/11 解压后双击 `启动下载器.vbs` 能出窗口  
- [ ] 用一条你确认可下的公开链接试下载成功  

---

## 限制与说明

- 仅使用原版 yt-dlp 能力；VIP / DRM / 需登录片源常会失败，界面会尽量给出中文提示。
- 云主机出口访问国内站点可能被拦；用户家庭宽带结果可能不同。
- 日志里可能含视频 URL，公开日志前请自行脱敏。
- 更细的本次构建/测试记录见 `BUILD_REPORT.md`、`TEST_REPORT.md`（若仓库中保留）。

## 许可

请遵守 yt-dlp、ffmpeg、Python 及各依赖自带的许可证；分发便携包时保留 `runtime` 内附带的许可证文件。
