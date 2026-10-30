# 测试报告（Asia/Shanghai）

测试时间：2026-10-30 12:35 CST  
环境：Debian Linux x86_64 + Wine 10.0 + Xvfb  
产物：`dist/CNVideoDownloader-Windows-Portable.zip`

## 结果一览

| # | 项目 | 结果 | 说明 |
|---|------|------|------|
| 1 | pytest（`tests/`） | PASS | 13 passed（已收窄 testpaths，不再误收集 runtime 内 certifi） |
| 2 | Linux GUI 冒烟（Xvfb） | PASS | 窗口标题「国内视频下载器」1000x820；截图 `test-output/gui-smoke.png` |
| 3 | 应用 DownloadQueue 实下（YouTube） | PASS | 状态「完成」；`test-output/queue-download/` 474596 字节 |
| 4 | yt-dlp CLI 实下（YouTube） | PASS | `test-output/Me at the zoo [jNQXAC9IVRw].mkv` 474596 字节 |
| 5 | 取消队列 | PASS | 2 个任务均「已取消」，进程集合清空 |
| 6 | 国内站探测（腾讯/B站/爱奇艺/优酷） | 部分 | 优酷可解析元数据，HLS 拉流 HTTP 500；腾讯/爱奇艺不可用；B站 412。判定为云 IP/地区限制，非本工具逻辑错误 |
| 7 | 便携包解压与文件清单 | PASS | 启动器、pythonw、yt-dlp/ffmpeg/ffprobe、_tkinter、customtkinter 均在；4013 个文件 |
| 8 | PE 头 / 架构 | PASS | 全部 MZ；yt-dlp/ffmpeg/pythonw = AMD64 |
| 9 | Wine：yt-dlp.exe --version | PASS | 2026.10.26 |
| 10 | Wine：ffmpeg.exe -version | PASS | 9.0.2 essentials |
| 11 | Wine：python import customtkinter/yt_dlp/tkinter | PASS | IMPORT_OK 5.2.2 / 2026.10.26 |
| 12 | Wine：便携 yt-dlp+ffmpeg 实下并合并 | PASS | `test-output/wine-download/` 474561 字节 |
| 13 | Wine：GUI 启动 | PASS | xwininfo 见「国内视频下载器」(python.exe)；`wine-gui-meta.txt` / `wine-gui-desktop.png` |

## 国内站详情

见 `test-output/cn-sites-probe.log`、`youku-download-result.txt`。  
本机（云出口）无法稳定拉取腾讯/优酷/爱奇艺/B站公开流；Windows 用户在国内网络下结果可能更好，但仍受会员/DRM/站点策略限制。

## 修复

- `pytest.ini`：增加 `testpaths = tests`，避免收集 `runtime/python` 内第三方测试。
- **未发现需改业务逻辑的致命缺陷**；未改下载器/GUI 源码。ZIP 因报告与 pytest.ini 同步而重建。

## 仍需真实 Windows 验收的缺口

1. 双击 `启动下载器.vbs` / `.bat` 在 Win10/11 资源管理器中的体验（无控制台窗口、中文路径解压）。
2. 国内宽带下对腾讯/优酷/爱奇艺真实链接的成功率。
3. Wine 提示缺少 wine32（本测仅 wine64），与真机 Windows 不完全等价。
4. 未跑 `build_windows.bat` 生成的单文件 PyInstaller exe（便携包走的是捆绑 pythonw 方案）。

## 产物路径

- ZIP：`/workspace/cn-video-downloader/dist/CNVideoDownloader-Windows-Portable.zip`
- 测试产物目录：`/workspace/cn-video-downloader/test-output/`

## ZIP SHA256

`c463dbc06f43c1281d5caf8641fdd9b663bc2cabd8276906827281d8398b2d47`（151383322 bytes）
同目录：`dist/CNVideoDownloader-Windows-Portable.zip.sha256`

