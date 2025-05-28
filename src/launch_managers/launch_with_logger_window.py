from queue import Queue
from threading import Thread
from typing import Any
from portablemc.standard import StreamRunner, XmlStreamEvent, Environment
from src.app_utils.launch_data_manager import LaunchData
import customtkinter as ctk
from portablemc.cli.util import format_time


class LaunchWithLoggerPopup(ctk.CTkToplevel):
    """
    When we launch Minecraft, we'll open a window that displays the game logs. That way, we'll know if the game crashes.
    (Plus, it is a more elegant approach than just a popup saying "hey, I think everything is ok". Beef SuccessWindow)

    Portablemc already does this with CliRunner. Instead, we'll copy the same log format but forward them to a
    toplevel using a Queue (same approach as in custom_installation_watcher).

    This class launches the env in a separate thread and opens the pop-up in the main thread (as required by tkinter).
    """
    def __init__(self, app, launch_data : LaunchData, env : Environment):
        super().__init__()
        title = ""
        if launch_data.version_type == "Vanilla":
            title = f"Vanilla {launch_data.version}"
        elif launch_data.version_type == "Forge":
            title = f"Forge {launch_data.version}:{launch_data.subversion}"
        elif launch_data.version == "Modpack":
            title = f"{launch_data.modpack} {launch_data.version}:{launch_data.subversion}"
        self.title(title)

        self.log_box = ctk.CTkTextbox(self, width=600, height=800, wrap="word", state="disabled")
        self.log_box.grid(row=0, padx=20, pady=10)

        # Button to wipe log window
        self.clear_button = ctk.CTkButton(self, text=app.translations["runner_clear"], width=500, command=self.clear)
        self.clear_button.grid(row=1)

        # We'll remind the user that they can close the popup if it bothers them without causing the game to close
        self.reminder = ctk.CTkLabel(self, text=app.translations["runner_you_can_close"])
        self.reminder.grid(row=2, pady=10)

        # Launch the game and connect the communication queue
        self.queue = Queue()
        self.game = Thread(target= lambda : env.run(LogRunner(self.queue)))
        self.game.start()
        self.update()
        # the handle method will read and display events
        self.after(0, self.handle)

    def clear(self):
        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")  # delete all text
        self.log_box.configure(state="disabled")

    def handle(self) -> None:
        """
        Reads the communication queue and logs events with the same format as in portablemc's CliRunner
        """
        while not self.queue.empty():
            event : XmlStreamEvent = self.queue.get()
            time = format_time(event.time)
            log = f"[{time}] [{event.thread}] [{event.level}] {event.message}\n"
            self.log_box.configure(state="normal")
            self.log_box.insert("end", log)
            self.log_box.configure(state="disabled")

        if  not self.game.is_alive():
            # If the game closes, notify it but don't destroy the window. That way, we'll know if the game crashed.
            self.log_box.configure(state="normal")
            self.log_box.insert("end", "\n--- GAME CLOSED ---")
            self.log_box.configure(state="disabled")
            return

        self.update()
        self.after(1000, self.handle)


class LogRunner(StreamRunner):
    """
    Simple portablemc.Environment runner that forwards all XmlStreamEvents to a queue. Meant to be run on a
    separate thread.
    """
    def __init__(self, queue : Queue):
        self.queue = queue

    def process_stream_event(self, event: Any) -> None:
        if isinstance(event, XmlStreamEvent):
            self.queue.put(event)
        # We'll ignore the rest of the cases
        #else:
        #    print(f"raw log: {event}")
