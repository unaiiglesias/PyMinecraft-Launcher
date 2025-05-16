from src.app_utils.launch_data_manager import LaunchData
from pathlib import Path
from portablemc.standard import Context, Version
from src.launch_managers.custom_download_watcher import DownloadWatcher

def launch_vanilla(launch_data : LaunchData, app):
    """

    Args:
        launch_data:
        app:

    Returns:
        portablemc env to be run
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

    env = version.install(watcher=DownloadWatcher(app,
                                                  f"{app.translations['downloading_title']}: {version_id}"))
    print("Installation ended")

    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])

    return env