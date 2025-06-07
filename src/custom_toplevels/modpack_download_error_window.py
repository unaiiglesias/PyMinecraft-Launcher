from os import startfile, remove
import customtkinter as ctk
from app_utils.launch_data_manager import LaunchData


class ModpackDownloadError(ctk.CTkToplevel):
    """
    We download mods directly from a link stored in the modlist. sometimes (rather often) some mods' link's break
    and the download fails. In those cases, we want to inform the user properly and let them decide what to do.
    NOTE: This popup is called right after updating / installing the modpack, right before we launch forge.

    We'll give the user 3 choices:
        - Abort the launch: Just close this popup and the launcher should stop the launch
        - Launch anyway: Ignore the missing mods and launch anyway
        - Retry: Retry the installation process in case it was a temporary error, OR...
        We will also let the user install the missing mods manually. If they then retry launch, the modpack won't even
        attempt to download them and it should work

    The GUI will have a text box explaining what happened, including a list with the missing mods and 3 buttons:
    Retry installation, open mods folder (to manually install mods) and continue anyway.
    (Closing the window will be the "abort" button)

    Usage:
    Create an object and save it in a variable, that will block the main thread. Once execution in main thread is
    recovered (the toplevel exited), use get_choice method to get what the user wanted to do.
    True: Proceed with launch
    False: Abort launch
    None: Retry installation
    """

    def __init__(self, app, launch_data : LaunchData, modlist : list, *args, **kwargs):
        """
        This method will build the window and "ask" for a choice (wait for button press)

        Once a button is pressed, choice is saved in self.choice and the window is destroyed. Then, the method that
        called this window will consult the choice of the user with get_choice.

        Params:
            app: master app
            launch_data: Modpack launch data
            modlist: List with the names of the mods that failed to download
        """
        super().__init__(*args, **kwargs)
        self.choice = None # True: Continue, False: Retry, None: Abort
        self.modpack_path = launch_data.path + "\\CalvonettaModpacks\\" + launch_data.modpack + "\\mods"

        self.grab_set()  # Focus and hijack
        self.title(app.translations["modpack_error_title"])
        self.rowconfigure(5)
        self.columnconfigure(1)

        self.explanation_frame = ctk.CTkFrame(self)
        self.explanation_frame.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        self.textbox = ctk.CTkTextbox(self.explanation_frame, width=500, height=150)
        self.textbox.configure(wrap="word") # If EOL, dont cut the word in half
        self.textbox.insert("0.0", app.translations["modpack_error_explanation"].format(f"https://github.com/CalvonettaModpacks/{launch_data.modpack}"))
        modlist_to_text = "\n"
        for mod in modlist:
            modlist_to_text += f" - {mod}\n"
        self.textbox.insert("end", modlist_to_text)
        self.textbox.configure(state="disabled")
        self.textbox.grid()

        self.retry = ctk.CTkButton(self, text=app.translations["modpack_error_retry"], width=60, height=30, command=self.retry)
        self.retry.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="nswe")

        self.open_directory = ctk.CTkButton(self, text=app.translations["modpack_error_open"], width=60, height=30, command=self.open_directory)
        self.open_directory.grid(row=3, column=0, padx=5, pady=(0, 10), sticky="nswe")

        self.continue_ex = ctk.CTkButton(self, text=app.translations["modpack_error_continue"], width=60, height=30, command=self.continue_ex)
        self.continue_ex.grid(row=4, column=0, padx=5, pady=(0, 10), sticky="nswe")

    def retry(self):
        self.choice = False
        self.destroy()

    def continue_ex(self):
        self.choice = True
        self.destroy()

    def open_directory(self):
        startfile(self.modpack_path) # Open path in explorer

    def get_choice(self):
        return self.choice


def main():
    app = ctk.CTk()
    app.translations = {"modpack_error_title" : "Some mods failed to download",
    "modpack_error_explanation" : "Some of the mods required by this modpack failed to download.\nThis might be caused by a broken link, please open an issue on github: {}\nYou can also manually install the missing mods and retry:",
    "modpack_error_retry" : "Retry installation",
    "modpack_error_open" : "Open mods folder",
    "modpack_error_continue" : "Continue launch anyway"}
    debug_launch_data = LaunchData()
    debug_launch_data.modpack = "test"
    res = ModpackDownloadError(app, debug_launch_data, ["this", "that", "the other"])
    app.btn = ctk.CTkButton(app, command=app.destroy)
    app.btn.grid()
    app.mainloop()
    print(res.get_choice())
    remove("launch_data.json")

if __name__ == "__main__":
    main()