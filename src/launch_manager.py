import portablemc.standard
from portablemc.standard import Context, Version, Watcher
from portablemc.forge import ForgeVersion
from pathlib import Path
import customtkinter as ctk
from threading import Thread
from git import Repo, InvalidGitRepositoryError, NoSuchPathError
import os
from src.config_manager import load_json
from wget import download


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


class ProgressBarrWindow(ctk.CTkToplevel):
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
        # I assume this method will be called each time a new item is downloaded
        self.download_counter.configure(text=f"{new_count}/{self.total_count}")  # update current count
        if new_count != self.current_count:
            self.current_count += 1
            self.progress_bar.set(self.current_count / self.total_count)
            self.download_speed.configure(text=f"{round(current_speed/1000000, 2)}Mb/s")
            self.download_speed.update()
            self.download_counter.update()
            self.progress_bar.update()
        self.update()  # So that windows doesn't say that the window stopped working

    def finish(self):
        self.grab_release()
        self.destroy()


class DownloadWatcher(Watcher):
    def __init__(self, app, title):
        self.app = app
        self.title = title
        self.window = None

    def handle(self, event) -> None:
        if isinstance(event, portablemc.standard.DownloadStartEvent):
            self.window = ProgressBarrWindow(self.title)
            self.window.set_total(event.entries_count)
        if isinstance(event, portablemc.standard.DownloadProgressEvent):
            self.window.update_progress(event.count, event.speed)
        if isinstance(event, portablemc.standard.DownloadCompleteEvent):
            self.window.finish()


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
    # path/CalvonettaModpacks/modpackName
    main_dir = launch_parameters["path"] + f"/CalvonettaModpacks/{launch_parameters['modpack']}"
    repo_url = f"https://github.com/CalvonettaModpacks/{launch_parameters['modpack']}.git"
    # Forge version and subversion will be fetched

    # this will ensure the repo exists and is up-to-date
    try:
        repo = Repo(main_dir)
        origin = repo.remote()
        origin.pull()
    except (InvalidGitRepositoryError, NoSuchPathError):
        # The repo doesn't exist (first launch), clone it
        repo = Repo.clone_from(repo_url, main_dir)

    """
    Each repo will contain (that are critical to PyMinecraft launcher)
     - mods/modlist.json: dict where {mod_filename: URL}
     - modpack_info.json: Forge version and subversion
    """
    modlist = load_json(main_dir + "/mods/modlist.json")
    info = load_json(main_dir + "/modpack_info.json")
    version_id = info["version"]
    subversion_id = info["subversion"]

    new_parameters = launch_parameters.copy() # We'll "inject" the new data into the launch parameters
    new_parameters["path"] = main_dir
    new_parameters["version"] = version_id
    new_parameters["subversion"] = subversion_id

    # We'll do 2 swipes over the modlis: one to remove unused mods and another one to add the new ones
    current_mods = os.listdir(str(main_dir) + "/mods")
    # Remove unused / deprecated mods
    for mod in current_mods:
        if mod not in modlist.keys() and mod.split(".")[-1] == "jar":
            print(f"Removing deprecated {mod}")
            os.remove(str(main_dir) + f"/mods/{mod}")

    # Download new mods
    download_list = [] # I'll queue them and then download them all together
    for mod in modlist.keys():
        if mod not in current_mods:
            download_list.append(mod)

    progress_bar = ProgressBarrWindow(f"{app.translations['downloading_title']}: {launch_parameters['modpack']}")
    progress_bar.set_total(len(download_list))

    for ind, mod in enumerate(download_list):
        download(modlist[mod], out=main_dir + f"/mods/{mod}")  # Download the mod with wget
        progress_bar.update_progress(ind, 0)
    progress_bar.finish()

    launch_forge(new_parameters, app)


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