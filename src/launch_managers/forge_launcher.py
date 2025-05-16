from src.app_utils.launch_data_manager import LaunchData
from src.launch_managers.custom_download_watcher import DownloadWatcher
from pathlib import Path
from portablemc.standard import Context
from portablemc.forge import ForgeVersion


def launch_forge(launch_data : LaunchData, app):
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
    subversion_id = launch_data.subversion
    ram_amount = launch_data.ram
    username = launch_data.username

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
    return env