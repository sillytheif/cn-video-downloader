"""Entry point for both python -m app.main and python app/main.py."""
if __package__ in (None, ''):
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def main():
    from app.gui import DownloaderApp
    DownloaderApp().mainloop()


if __name__ == '__main__':
    main()
