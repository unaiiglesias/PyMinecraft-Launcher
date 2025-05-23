from src.app_utils.launch_data_manager import LaunchData
from pathlib import Path
from portablemc.standard import Context, Version, Environment, VersionLoadedEvent, JarFoundEvent, \
    LibrariesResolvedEvent, DownloadCompleteEvent, DownloadStartEvent, DownloadProgressEvent

from src.custom_toplevels.popup_download import ProgressBarWindow
from src.launch_managers.version_installation_popup import VersionInstallationPopup

class VanillaInstallationPopup(VersionInstallationPopup):

    def __init__(self, app, launch_data : LaunchData, version : Version):
        self.version_name = f"Vanilla {launch_data.version}"
        task_list = tuple(app.translations["vanilla_tasks"])
        super().__init__(app, self.version_name, task_list, version)

    def handle_event(self):

        while not self.queue.empty():
            event = self.queue.get()
            if isinstance(event, VersionLoadedEvent):
                self.tasks[0].select()
                print("TASK 1 DONE")
            elif isinstance(event, JarFoundEvent):
                self.tasks[1].select()
                print("TASK 2 DONE")
            elif isinstance(event, LibrariesResolvedEvent):
                self.tasks[2].select()
                print("TASK 3 DONE")

            elif isinstance(event, DownloadStartEvent):
                print("Task 4 START (download)")
                self.window = ProgressBarWindow(f"Downloading {self.version_name}")
                self.window.set_total(event.entries_count)
            elif isinstance(event, DownloadProgressEvent):
                self.window.update_progress(event.count, event.speed)
            elif isinstance(event, DownloadCompleteEvent):
                self.tasks[3].select()
                print("TASK 4 DONE, returning...")
                self.window.finish() # Close progress bar window
                self.destroy() # End
                return

            elif self.future.done():
                # Just in case some step was skipped. if we are done, end the window
                self.destroy()
                return

        self.update()
        self.after(100, self.handle_event)

    def get_env(self) -> Environment:
        return self.future.result()


def build_vanilla_env(launch_data : LaunchData, app):
    """
    Builds portablemc env for given launch data (must be version_type "Vanilla")
    Also handles installation
    Args:
        launch_data:
        app:

    Returns:
        portablemc Environment ready to be run
    """

    main_dir = Path(launch_data.path)
    work_dir = Path(main_dir)
    version_id = launch_data.version
    ram_amount = launch_data.ram
    username = launch_data.username

    ctx = Context(main_dir, work_dir)
    version = Version(version_id, context=ctx)

    print("Downloading and installing Minecraft version")
    app.update_status("working", app.translations["status_working_downloading_version"])
    version.set_auth_offline(username, None)  # (username, uuid) no uuid so pass None

    env : VanillaInstallationPopup = VanillaInstallationPopup(app, launch_data, version)
    env.wait_window()
    env : Environment = env.get_env()

    print("Installation ended")

    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])

    return env