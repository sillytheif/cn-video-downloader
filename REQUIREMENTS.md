# 需求与验收

- Windows 10/11 x64；开发使用 Python 3.11+，CustomTkinter、yt-dlp。
- 中文多链接输入、TXT 导入、保存目录、两路并发、进度、逐项状态、滚动日志。
- 取消终止进程树；后台只写事件队列，主线程每 100 ms 轮询更新界面。
- 使用原版 yt-dlp，不绕过 DRM、VIP、登录或地区限制；不保证特定网站或全部视频可下载。
- 完整源码可在 Linux 导入、测试及通过 Xvfb 启动界面。
- 便携 ZIP 包含源码、Windows yt-dlp/ffmpeg、启动脚本及说明。
- 首选完整 Windows CPython（含 Tk），不使用缺少 Tk 的官方嵌入式 ZIP。
- Windows 可通过 build_windows.bat 生成 PyInstaller onedir 可执行程序。
- 构建完成不等于真实 Windows 验证，交付说明必须区分。
