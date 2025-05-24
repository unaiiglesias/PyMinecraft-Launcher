from src.app_utils.launch_data_manager import LaunchData
from pathlib import Path
from portablemc.forge import ForgeVersion, ForgePostProcessedEvent
from portablemc.standard import Context, Version, Environment, VersionLoadedEvent, JarFoundEvent, \
    LibrariesResolvedEvent, DownloadCompleteEvent, DownloadStartEvent, DownloadProgressEvent
from src.custom_toplevels.popup_download import ProgressBarWindow
from src.custom_toplevels.version_installation_popup import VersionInstallationPopup

class ForgeInstallationPopup(VersionInstallationPopup):

    def __init__(self, app, launch_data : LaunchData, version : Version):
        self.version_name = f"Forge {launch_data.version}-{launch_data.subversion}"

        #task_list = ("Load forge", "Load version", "Load JVM", "Download forge version", "Install forge", "Resolve libraries", "Download vanilla version")
        #task_types = [VersionLoadedEvent, VersionLoadedEvent, JarFoundEvent, DownloadCompleteEvent, ForgePostProcessedEvent, LibrariesResolvedEvent, DownloadCompleteEvent]
        task_list = tuple(app.translations["forge_tasks"]) # Task names translated

        # Aux variables to distinguish regular load and download events from forge events
        self.forge_loaded = False
        self.forge_downloaded = False

        super().__init__(app, self.version_name, task_list, version)

    def handle_event(self):

        while not self.queue.empty():
            event = self.queue.get()
            # Tasks 1 (Forge version loaded) and 2 (Vanilla version loaded)
            if isinstance(event, VersionLoadedEvent):
                if not self.forge_loaded:
                    print("TASK 1 (Load Forge version) DONE")
                    self.tasks[0].select()
                    self.forge_loaded = True
                else:
                    print("TASK 2 load (Vanilla version) DONE")
                    self.tasks[1].select()

            # Task 3 (Load JVM)
            elif isinstance(event, JarFoundEvent):
                print("TASK 3 (load JVM) DONE")
                self.tasks[2].select()

            # Task 4 (Download Forge version)
            elif isinstance(event, DownloadStartEvent) and not self.forge_downloaded: # Download start
                print("Task 4 (download forge) START")
                self.window = ProgressBarWindow(f"Downloading {self.version_name}")
                self.window.set_total(event.entries_count)
            elif isinstance(event, DownloadCompleteEvent) and not self.forge_downloaded: # Download end
                print("Task 4 (download forge) DONE")
                self.tasks[3].select()
                self.window.finish()  # Close progress bar window
                self.forge_downloaded = True # Now forge has been downloaded, mark it. Next download will be vanilla version

            # Task 5 ("compile" and install Forge version)
            elif isinstance(event, ForgePostProcessedEvent):
                print("TASK 5 (Forge compilation and installation) DONE")
                self.tasks[4].select()

            # Task 6 (Library resolution)
            elif isinstance(event, LibrariesResolvedEvent):
                print("TASK 6 (Libraries resolved) DONE")
                self.tasks[5].select()

            elif isinstance(event, DownloadStartEvent): # and self.forge_downloaded
                print("Task 7 (Download Vanilla version) START")
                self.window = ProgressBarWindow(f"Downloading {self.version_name}")
                self.window.set_total(event.entries_count)
            elif isinstance(event, DownloadCompleteEvent): # and self.forge_downloaded
                print("TASK 7 (Download Forge version) DONE")
                self.tasks[6].select()
                self.window.finish()  # Close progress bar window
                self.destroy()  # End
                return

            # General purpose download update event
            elif isinstance(event, DownloadProgressEvent):
                self.window.update_progress(event.count, event.speed)

        self.after(100, self.handle_event)

        # Just in case some step was skipped. if we are done, end the process
        if self.future.done():
            self.destroy()
            return

    def get_env(self) -> Environment | None:
        return self.future.result()


def build_forge_env(launch_data : LaunchData, app) -> Environment | None:
    """
    Builds portablemc env for given launch data (must be version_type "Forge")
    Also handles installation
    Args:
        launch_data:
        app:

    Returns:
        portablemc Environment to be run
    """

    main_dir = Path(launch_data.path)
    work_dir = Path(main_dir)
    version_id = launch_data.version
    subversion_id = launch_data.subversion
    ram_amount = launch_data.ram
    username = launch_data.username

    ctx : Context = Context(main_dir, work_dir)

    full_version_id = f"{version_id}-{subversion_id}"
    print(f"Launching : {full_version_id}")

    print("Downloading and installing Forge version")
    app.update_status("working", app.translations["status_working_downloading_forge_version"])
    version = ForgeVersion(full_version_id, context=ctx)

    version.set_auth_offline(username, None)  # (username, uuid) no uuid so pass None

    env : ForgeInstallationPopup = ForgeInstallationPopup(app, launch_data, version)
    env.wait_window()
    env : Environment = env.get_env()

    env.username = username
    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])
    return env