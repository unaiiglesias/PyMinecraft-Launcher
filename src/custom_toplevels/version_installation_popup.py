from concurrent.futures.thread import ThreadPoolExecutor
import customtkinter as ctk
from queue import Queue
from portablemc.standard import Environment, Version
from src.custom_toplevels.popup_download import ProgressBarWindow
from src.launch_managers.custom_installation_watcher import InstallationWatcher


class VersionInstallationPopup(ctk.CTkToplevel):
    """
        Popup to track progress of version installation.
        Will define the GUI and utilities that all version installers use, each mode launcher will have to
        implement their event handlers.
    """
    WIDTH = 400
    HEIGHT = 300
    def __init__(self, master, version_name : str, task_list : tuple, version: Version):
        super().__init__()
        self.title(master.translations["installation_popup_title"].format(version_name)) # Set window title / name

        """
            Window will contain:
            [frame with tasks]
            -- loading bar --
        """
        # Frame where each task is a CheckBox
        self.tasklist_frame = ctk.CTkFrame(self)
        self.tasklist_frame.grid(row=0, pady=0, sticky="nswe")
        self.tasks = [] # for each task, 1 checkbox
        for i, task in enumerate(task_list):
            aux = ctk.CTkCheckBox(self.tasklist_frame)
            aux.configure(text=f"{i+1} - {task}")
            aux.configure(state="DISABLED")
            aux.grid(row=i, padx=10, pady=10, sticky="nw")
            self.tasks.append(aux)
        # Configure the height of the tasklist's frame manually
        self.tasklist_frame.configure(height=self.tasks[0].cget("height") * len(self.tasks) + 10)

        # We'll place a loading bar at the bottom so that we give the illusion that everything is working fine
        self.loading_bar = ctk.CTkProgressBar(self, mode="indeterminate", width=400)
        self.loading_bar.grid(row=1)
        self.loading_bar.start()

        self.grab_set()
        self.window : None | ProgressBarWindow = None # Chlidren will use it

        # Launch the other thread where portablemc will install
        self.queue = Queue() # Queue that we'll use to communicate with InstallationWatcher
        self.env : None | Environment = None # Result
        watcher = InstallationWatcher(self.queue)
        self.executor = ThreadPoolExecutor()
        args = {"watcher": watcher}
        self.future = self.executor.submit(version.install, **args)
        self.after(0, self.handle_event)


    def handle_event(self):
        """
        Must be overwritten by children
        """
        raise Exception()
