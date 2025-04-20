from portablemc.standard import (Context, Version, Watcher, DownloadStartEvent,
                                 DownloadProgressEvent, DownloadCompleteEvent)
from portablemc.forge import ForgeVersion
from pathlib import Path
import customtkinter as ctk
from threading import Thread
import os
from config_manager import load_json
from wget import download
from subprocess import call


class SuccessWindow(ctk.CTkToplevel):
    def __init__(self, app, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grab_set()  # Focus and hijack
        self.title(app.translations["status_success"])
        self.rowconfigure(3)
        self.columnconfigure(1)

        self.header = ctk.CTkLabel(self, text=app.translations["status_success"])
        self.header.grid(row=0, column=0, pady=(10, 0))

        self.disclaimer_frame = ctk.CTkFrame(self)
        self.disclaimer_frame.grid(row=1, column=0, sticky="nswe", padx=10, pady=20)
        self.textbox = ctk.CTkTextbox(self.disclaimer_frame, width=500, height=100)
        self.textbox.insert("0.0", app.translations["launched_notice"])
        self.textbox.configure(state="disabled")
        self.textbox.grid()

        self.OK = ctk.CTkButton(self, text="OK", width=60, height=30, command=self.close)
        self.OK.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="nswe")

    def close(self):
        self.grab_release()
        self.destroy()


class ProgressBarWindow(ctk.CTkToplevel):
    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.grab_set()  # Focus and hijack
        self.title(title)
        self.rowconfigure(2)
        self.columnconfigure(2)

        self.total_count = 0  # This will save the total items to download
        self.current_count = 0  # This will save the amount of items downloaded
        self.download_counter = ctk.CTkLabel(self, text="0/0")
        self.download_counter.grid(row=0, column=0, padx=(20, 0), pady=20)

        self.download_speed = ctk.CTkLabel(self, text="0.0Mb/s")
        self.download_speed.grid(row=0, column=1, padx=(0, 20), pady=20)

        self.progress_bar = ctk.CTkProgressBar(self, orientation="horizontal", mode="determinate", width=400)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=1, columnspan=2)

        self.grab_set()

    def set_total(self, total):
        self.total_count = total
        self.progress_bar.update()

    def update_progress(self, new_count, current_speed):
        """
        Used to update the progress_bar using portablemc DownloadProgressEvent

        Updates currently downloaded item count and speed

        ex: Installing a vanilla version
        """

        # Updated each progress event (not every time a download is completed, rather a tick)
        self.download_counter.configure(text=f"{new_count}/{self.total_count}")  # update current count
        self.download_counter.update()
        self.download_speed.configure(text=f"{format(current_speed / 1000000, '.2f')}Mb/s")  # Update speed
        self.download_speed.update()

        if new_count != self.current_count:
            # Update only when an item dwonload has beeen completed
            self.current_count += 1
            self.progress_bar.set(self.current_count / self.total_count)
            self.progress_bar.update()

        self.update()  # So that windows doesn't complain that the window stopped working

    def update_from_wget(self, new_count, total, _width):
        """
        Similar to self.update_progress but adapted to wget.download's callback

        For single file downloads only:
        It uses self.current and self.total for the item's size and "dynamically" calculates the speed
        (speed is Mb/tick, not Mb/s, though)

        _width is passed by wget, but I won't use it

        ex: Downloading git installer
        """
        self.download_counter.configure(text=f"{format(new_count/1000000, '.2f')}/{format(total/1000000, '.2f')} Mb")
        # update both current and total
        self.progress_bar.set(new_count / total)
        self.download_speed.configure(text=f"{format(new_count/1000000 - self.current_count/1000000, '.2f')}Mb/tick")
        self.current_count = new_count
        self.download_speed.update()
        self.download_counter.update()
        self.progress_bar.update()
        self.update()  # So that windows doesn't complain that the window stopped working

    def update_speed_from_wget(self, new_count, total, _width):
        """
        Simpler version of self.update_from_wget that only updates the speed, but doesn't touch current or total

        Use when downloading several  (more than 1) items with wget

        In this case, since I don't have speed, I will use the speed counter as downloaded size counter

        _width is passed by wget but I won'r use it

        ex: when downloading mods for a modpack
        """
        self.download_speed.configure(text=f"{format(new_count/1000000, '.2f')} / {format(total/1000000, '.2f')} Mb")
        self.update()

    def finish(self):
        self.grab_release()
        self.destroy()


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


# TODO: launch_vanilla & launch_forge are very similar, they can surely be compacted in a single function
def launch_vanilla(launch_parameters, app):
    main_dir = Path(launch_parameters["path"])
    work_dir = Path(main_dir)
    version_id = launch_parameters["version"]
    ram_amount = launch_parameters["ram"]
    username = launch_parameters["username"]

    ctx = Context(main_dir, work_dir)
    version = Version(version_id, context=ctx)

    print("Downloading and installing Minecraft version")
    app.update_status("working", app.translations["status_working_downloading_version"])
    version.set_auth_offline(username, None)  # (username, uuid) no uuid so pass None

    env = version.install(watcher=DownloadWatcher(app,
                                                  f"{app.translations['downloading_title']}: {version_id}"))
    print("Installation ended")

    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])
    app.launch_button.configure(state="normal")
    Thread(target=run, args=[env]).start()
    SuccessWindow(app)


def launch_forge(launch_parameters, app):
    main_dir = Path(launch_parameters["path"])
    work_dir = Path(main_dir)
    version_id = launch_parameters["version"]
    subversion_id = launch_parameters["subversion"]
    ram_amount = launch_parameters["ram"]
    username = launch_parameters["username"]

    ctx = Context(main_dir, work_dir)

    full_version_id = f"{version_id}-{subversion_id}"
    print(f"Launching : {full_version_id}")

    print("Downloading and installing Forge version")
    app.update_status("working", app.translations["status_working_downloading_forge_version"])
    version = ForgeVersion(full_version_id, context=ctx)

    version.set_auth_offline(username, None)  # (username, uuid) no uuid so pass None

    env = version.install(watcher=DownloadWatcher(app,
                                                  f"{app.translations['downloading_title']}: {full_version_id}"))

    env.username = username
    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])
    app.launch_button.configure(state="normal")
    Thread(target=run, args=[env]).start()
    SuccessWindow(app)


def launch_modpack(launch_parameters, app):
    from git import Repo, InvalidGitRepositoryError, NoSuchPathError
    # path/CalvonettaModpacks/modpackName
    main_dir = launch_parameters["path"] + f"/CalvonettaModpacks/{launch_parameters['modpack']}"
    repo_url = f"https://github.com/CalvonettaModpacks/{launch_parameters['modpack']}.git"
    # Forge version and subversion will be fetched

    # Before we update (and potentially overwrite) it, we keep a copy of the current modlist
    try:
        prev_modlist = load_json(main_dir + "/mods/modlist.json")
    except FileNotFoundError:
        prev_modlist = []

    # this will ensure the repo exists and is up-to-date
    # (In this process, we might have updated the modlist)
    try:
        repo = Repo(main_dir)
        origin = repo.remote()
        origin.pull()
    except (InvalidGitRepositoryError, NoSuchPathError):
        # The repo doesn't exist (first launch), clone it
        Repo.clone_from(repo_url, main_dir)

    """
    Each repo will contain (that are critical to PyMinecraft launcher)
     - mods/modlist.json: dict where {mod_filename: URL}
     - modpack_info.json: Forge version and subversion
    """
    # Reload the info needed to install & launch the modpack
    modlist = load_json(main_dir + "/mods/modlist.json")
    info = load_json(main_dir + "/modpack_info.json")
    version_id = info["version"]
    subversion_id = info["subversion"]

    """
        Launch parameters path should always point to the root of the minecraft installation (kinda like the .minecraft
        folder)
        At the same time, we wan't to launch forge on the installed modpack's directory CalvonettaModpacks/...
        To do this, we just create "disposable" new launch parameters we'll use to launch forge there, but we won't write
        them to disk
    """
    new_parameters = launch_parameters.copy()  # We'll "inject" the new data into the launch parameters
    new_parameters["path"] = main_dir
    new_parameters["version"] = version_id
    new_parameters["subversion"] = subversion_id

    # If we haven't updated the modlist, we skip this step
    # If we have updated the modlist, apply the corresponding changes
    if prev_modlist != modlist:
        # We'll do 2 swipes over the modlis: one to remove unused mods and another one to add the new ones
        current_mods = os.listdir(str(main_dir) + "/mods")

        # Remove unused / deprecated mods:
        # won't remove mods that were added by the user
        for mod in current_mods:
            if mod in prev_modlist and mod not in modlist.keys():
                print(f"Removing deprecated {mod}")
                os.remove(str(main_dir) + f"/mods/{mod}")

        # Download new mods
        download_list = []  # I'll queue them and then download them all together
        for mod in modlist.keys():
            if mod not in current_mods:
                download_list.append(mod)

        progress_bar = ProgressBarWindow(f"{app.translations['downloading_title']}: {launch_parameters['modpack']}")
        progress_bar.set_total(len(download_list))

        for ind, mod in enumerate(download_list):
            # Download the mod with wget
            download(modlist[mod], out=main_dir + f"/mods/{mod}", bar=progress_bar.update_speed_from_wget)
            progress_bar.update_progress(ind, 0)
        progress_bar.finish()

    launch_forge(new_parameters, app)


def is_git_installed():
    """
    Return true if git is installed and false instead
    """

    try:
        call("git --version")
        return True
    except FileNotFoundError:
        return False


def check_git(app, launch_data):
    """
    Checks wether git is installed or not:
     - if git is inastalled, returns true
     - if git is not installed pops up toplevel window to help the user install git
      - If the user doesnt want to install git, returns false
      - If the user wants to install git, it downloads the installer and runs it
    """

    if is_git_installed():
        # In this case, we dont need to do anything else
        return True

    class MessageWindow(ctk.CTkToplevel):
        """
        Reusable window with a message box and 2 buttons
        """
        def __init__(self, title, text, but1, but2, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.grab_set()
            self.title(title)
            self.rowconfigure(3)
            self.columnconfigure(1)

            """ Textbox stuff """
            self.text_frame = ctk.CTkFrame(self)
            self.text_frame.grid(row=0, column=0, sticky="nswe", padx=20, pady=10)
            self.textbox = ctk.CTkTextbox(self.text_frame, width=500, height=100)
            self.textbox.insert("0.0", text)
            self.textbox.configure(state="disabled")
            self.textbox.grid()

            """ The two buttons"""
            # One will return True on press and the other one False, both will close the window
            self.confirm_but = ctk.CTkButton(self, text=but1, width=60, height=30, command=self.confirm)
            self.confirm_but.grid(row=1, column=0, padx=5, pady=(0, 10), sticky="nswe")
            self.refuse_but = ctk.CTkButton(self, text=but2, width=60, height=30, command=self.refuse)
            self.refuse_but.grid(row=2, column=0, padx=5, pady=(0, 10), sticky="nswe")

            self.selection = False  # default value

        def close(self):
            self.grab_release()
            self.destroy()

        def confirm(self):
            self.selection = True
            self.close()

        def refuse(self):
            self.selection = False
            self.close()

        def show(self):
            self.deiconify()
            self.wm_protocol("WM_DELETE_WINDOW", self.close)
            self.wait_window()
            return self.selection

    msg = MessageWindow(app.translations["git_not_found_title"], app.translations["git_not_found_text"],
                        app.translations["git_install_button"], app.translations["git_dont_install_button"])

    install = msg.show()

    if not install:
        # The user has chosen not to install git, this will abort the modpack launch
        app.launch_button.configure(state="normal")  # Release launch button
        return False

    # The user has chosen to install git, download the installer, I'll use a hard-coded release
    # (we don't need the latest and it's more comfortable this way)

    git_link = "https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe"
    download_path = launch_data["path"] + "/git_for_calvonetta.exe"

    print("DOWNLOADING GIT")

    progress_bar = ProgressBarWindow("git")
    progress_bar.set_total(1)

    download(git_link, out=download_path, bar=progress_bar.update_from_wget)
    progress_bar.finish()

    # At this point, we should have git_for_calvonetta.exe downloaded

    os.system(download_path + " /SILENT")  # This will automatically install git automatically :D
    # (will trigger UAC prompt, though)
    os.remove(download_path)  # Remove the executable

    return is_git_installed()  # In case the user stopped the installation


def run(env):
    env.run()


if __name__ == "__main__":
    pass

"""
        launch_parameters = {
            "username": self.input_username_field.get(),
            "version_type": self.version_type.get(),
            "version": self.version_number.get(),
            "subversion": self.subversion_number.get(),
            "ram": self.input_ram_field.get(),
            "path": self.input_installation_path.get(),
            "email": self.input_email_field.get(),
            "premium": False,  # Make it false by default
            "theme": self.appearance_mode.get()
        }
"""