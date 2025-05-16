from portablemc.standard import Watcher, DownloadStartEvent, DownloadProgressEvent, DownloadCompleteEvent
from src.custom_windows.popup_download import ProgressBarWindow

class DownloadWatcher(Watcher):
    def __init__(self, app, title):
        self.app = app
        self.title = title
        self.window = None

    def handle(self, event) -> None:
        if isinstance(event, DownloadStartEvent):
            self.window = ProgressBarWindow(self.title)
            self.window.set_total(event.entries_count)
        if isinstance(event, DownloadProgressEvent):
            self.window.update_progress(event.count, event.speed)
        if isinstance(event, DownloadCompleteEvent):
            self.window.finish()