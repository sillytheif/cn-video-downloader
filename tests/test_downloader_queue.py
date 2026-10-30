import queue
import sys
import time
from app import downloader


def statuses(worker, count):
    result = {}
    deadline = time.monotonic() + 8
    while len(result) < count and time.monotonic() < deadline:
        try:
            event = worker.events.get(timeout=.1)
        except queue.Empty:
            continue
        if event[0] == 'status' and event[2] in ('完成', '失败', '已取消'):
            result[event[1]] = event[2]
    return result


def test_subprocess_success_and_failure(monkeypatch, tmp_path):
    def args(url, folder):
        return [sys.executable, '-c', 'print("CNPROGRESS:50.0%", flush=True); exit(' + ('0' if url == 'ok' else '1') + ')']
    monkeypatch.setattr(downloader, 'build_args', args)
    worker = downloader.DownloadQueue()
    worker.start(['ok', 'bad'], tmp_path)
    assert statuses(worker, 2) == {0: '完成', 1: '失败'}


def test_cancel_running_and_waiting(monkeypatch, tmp_path):
    monkeypatch.setattr(downloader, 'build_args', lambda *a: [sys.executable, '-c', 'import time; time.sleep(20)'])
    worker = downloader.DownloadQueue()
    worker.start(['a', 'b', 'c', 'd'], tmp_path)
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        with worker.lock:
            count = len(worker.processes)
        if count == 2:
            break
        time.sleep(.01)
    assert count == 2
    worker.cancel()
    assert statuses(worker, 4) == dict.fromkeys(range(4), '已取消')
    worker.executor.shutdown(wait=True)
    assert not worker.processes
