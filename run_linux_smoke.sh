#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
PY=.venv/bin/python
"$PY" -c 'import app.main, app.gui, app.downloader, app.paths; print("Imports OK")'
if command -v xvfb-run >/dev/null; then
  xvfb-run -a "$PY" -c 'from app.gui import DownloaderApp; app=DownloaderApp(); app.after(800,app.destroy); app.mainloop(); print("GUI smoke OK")'
else
  echo 'No xvfb-run: import smoke only.'
fi
