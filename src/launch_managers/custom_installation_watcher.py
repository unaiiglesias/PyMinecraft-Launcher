
"""
    Tkinter can only execute windows (CTk) or popups (CTkToplevel) on the main thread. Therefore, if we want to execute
    any task and have a GUI "wait" for the task to finish we must display the GUI on the main thread and execute
    the task on a separate thread. Otherwise, we run the risk of blocking the GUI while the task executes.

    We could work around this when downloading a customtkinter version because customtkinter spams quite a lot of
    DownloadEvents, so we could use those to update the GUI fast enough for it not to get stuck for too long.
    Unfortunately, this isn't the case for all the installation steps. For example: installing a forge version
    takes a couple seconds and only logs a couple times, which blocks the GUI.

    We used to run version.install() in the foreground, which meant that if we wanted to have a GUI waiting for
    the installation to finish it would have to run on a secondary thread. I haven't been able to implement this fix
    so far...

    Instead of tinkering some kind of weird solution that would enable us to run a CTkToplevel on the background I've
    decided to turn the problem around and make a more elegant solution: Whenever we launch the game, PyMinecraft
    will display a window with each step that portablemc has to go through when launching the game. The version
    installation (portablemc.Version.install) will be run on the background and via this "installation watcher" it will
    communicate with the GUI in the foreground which will log how the installation is going without blocking the GUI.
"""
from queue import Queue
from portablemc.standard import Watcher

class InstallationWatcher(Watcher):
    """
    Handle each event by sending it to the main thread
    """
    def __init__(self, queue : Queue):
        self.queue = queue

    def handle(self, event) -> None:
        self.queue.put(event)