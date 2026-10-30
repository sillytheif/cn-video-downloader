"""Locate portable resources and user folders."""
import os
import shutil
import sys
from pathlib import Path


def app_root() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent


def runtime_dir() -> Path:
    return app_root() / 'runtime'


def downloader_command() -> list[str]:
    binary = runtime_dir() / ('yt-dlp.exe' if os.name == 'nt' else 'yt-dlp')
    if binary.is_file():
        return [str(binary)]
    system = shutil.which('yt-dlp')
    if system:
        return [system]
    if getattr(sys, 'frozen', False):
        raise FileNotFoundError('缺少 runtime/yt-dlp.exe，请重新解压完整便携包。')
    return [sys.executable, '-m', 'yt_dlp']


def downloads_dir() -> Path:
    if os.name == 'nt':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r'Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders') as key:
                return Path(os.path.expandvars(winreg.QueryValueEx(key, '{374DE290-123F-4565-9164-39C4925E467B}')[0]))
        except OSError:
            pass
    return Path.home() / 'Downloads'
