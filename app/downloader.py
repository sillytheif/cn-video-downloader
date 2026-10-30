"""Subprocess download queue. Workers emit events; never touch Tk."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import os
import queue
import re
import signal
import subprocess
import threading
from .paths import downloader_command, runtime_dir
from .messages import friendly_error


def build_args(url: str, folder: Path) -> list[str]:
    args = downloader_command() + [
        '--ignore-config', '--no-playlist', '--no-mtime', '--newline', '--progress',
        '--no-color', '--encoding', 'utf-8', '--socket-timeout', '20', '--retries', '3',
        '-f', 'bv*+ba/b', '--merge-output-format', 'mkv',
        '--progress-template', 'download:CNPROGRESS:%(progress._percent_str)s',
        '-o', str(Path(folder) / '%(title).80B [%(id)s].%(ext)s'),
    ]
    ffmpeg = runtime_dir() / ('ffmpeg.exe' if os.name == 'nt' else 'ffmpeg')
    if ffmpeg.is_file():
        args += ['--ffmpeg-location', str(ffmpeg.parent)]
    return args + ['--', url]


class DownloadQueue:
    def __init__(self):
        self.events: queue.Queue = queue.Queue()
        self.cancelled = threading.Event()
        self.lock = threading.Lock()
        self.processes: set[subprocess.Popen] = set()
        self.executor = None

    def start(self, urls: list[str], folder: Path):
        self.cancelled.clear()
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='download')
        for index, url in enumerate(urls):
            self.executor.submit(self._download, index, url, folder)
        self.executor.shutdown(wait=False)

    def _emit(self, index, status, message='', progress=0):
        self.events.put(('status', index, status, message, progress))

    def _download(self, index: int, url: str, folder: Path):
        process = None
        lines = []
        try:
            with self.lock:
                if self.cancelled.is_set():
                    self._emit(index, '已取消', '已取消')
                    return
                folder.mkdir(parents=True, exist_ok=True)
                kwargs = {'creationflags': subprocess.CREATE_NO_WINDOW} if os.name == 'nt' else {'start_new_session': True}
                process = subprocess.Popen(build_args(url, folder), stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT, text=True, encoding='utf-8', errors='replace', **kwargs)
                self.processes.add(process)
            self._emit(index, '下载中', '正在解析视频…')
            for line in process.stdout:
                line = line.rstrip()
                match = re.search(r'CNPROGRESS:\s*([\d.]+)%', line)
                if match:
                    self._emit(index, '下载中', match.group(1) + '%', min(float(match.group(1)), 100))
                elif line:
                    lines.append(line)
                    lines = lines[-40:]
                    self.events.put(('log', index, line))
            code = process.wait()
            if self.cancelled.is_set():
                self._emit(index, '已取消', '已取消，部分文件可在重试时续传')
            elif code == 0:
                self._emit(index, '完成', '已保存', 100)
            else:
                self._emit(index, '失败', friendly_error('\n'.join(lines)))
        except Exception as exc:
            self.events.put(('log', index, str(exc)))
            self._emit(index, '已取消' if self.cancelled.is_set() else '失败', str(exc) if isinstance(exc, FileNotFoundError) else friendly_error(str(exc)))
        finally:
            if process:
                if process.stdout:
                    process.stdout.close()
                with self.lock:
                    self.processes.discard(process)

    def cancel(self):
        self.cancelled.set()
        with self.lock:
            for process in list(self.processes):
                if process.poll() is not None:
                    continue
                try:
                    if os.name == 'nt':
                        result = subprocess.run(['taskkill', '/PID', str(process.pid), '/T', '/F'],
                            creationflags=subprocess.CREATE_NO_WINDOW, capture_output=True, timeout=10)
                        if result.returncode and process.poll() is None:
                            process.kill()
                    else:
                        os.killpg(process.pid, signal.SIGKILL)
                except (OSError, subprocess.TimeoutExpired):
                    try:
                        process.kill()
                    except OSError:
                        pass
