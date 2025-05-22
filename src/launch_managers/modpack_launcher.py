from src.app_utils.launch_data_manager import LaunchData
from src.custom_toplevels.modpack_download_error_window import ModpackDownloadError
from src.util.ensure_git import ensure_git
from src.util.utilities import load_json
from src.launch_managers.forge_launcher import build_forge_env
from src.custom_toplevels.popup_download import download_stuff
import os
from json.decoder import JSONDecodeError


def build_modpack_env(launch_data : LaunchData, app):
    """
    Handles everything regarding modpack launch:
        - Ensures git is installed
        - Installs / Updates modpack
        - Creates forge env
    Builds portablemc Environment for modpacks Forge version
    Args:
        launch_data:
        app:

    Returns:
        portablemc env to be run
    """

    print(f"Launching : {launch_data.modpack}")

    # Only continue if git is installed (Delegate that task on util.ensure_git)
    if not ensure_git(app, launch_data):
        app.update_status("error", app.translations["status_error_git_not_installed"])
        print("Aborting modpack launch, git not installed")
        return None

    """
    Explanation on what we'll do going forward:
        We will want to pull the repo and update the previous mods according to the new modlist. However, we don't want
        to touch mods installed by the user, so we must be careful with what we remove.
        At the same time, we can't trust tha the mods in the modlist are actually installed, so we need to double
        check with the actual mods folder.
        
        In order to achieve this, we'll follow the next order:
        1. Read the current modlist (what mods should currently be installed)
        2. Read the current mods folder (what mods are currently installed)
        3. Update the repo and read the new modlist (what mods will have to be currently installed)
        4. Deduct which mods need to be removed and which ones installed
        5. Remove and install said mods
    """

    from git import Repo, InvalidGitRepositoryError, NoSuchPathError
    # path/CalvonettaModpacks/modpackName
    main_dir = launch_data.path + f"/CalvonettaModpacks/{launch_data.modpack}"
    repo_url = f"https://github.com/CalvonettaModpacks/{launch_data.modpack}.git"
    # Forge version and subversion will be fetched

    # 1. Read the current modlist
    try:
        prev_modlist = load_json(main_dir + "/mods/modlist.json")
    except (FileNotFoundError, JSONDecodeError) as error:
        # If the modlist is not found, it probably means this is the first time we're launching this modpack, so,
        # it's normal. We'll download it when cloning the repo

        # If the modlist is broken, we'll also fix it with the repo, but we shall print a debug message just in case
        if type(error).__name__ == "JSONDecodeError":
            print("WARNING: Modlist read failed. this could mean that the modlist was corrupted or has been wrongly modified.")
        prev_modlist = {} # In both cases, default to empty prev_modlist

    # 2. Get the currently installed mods
    try:
        prev_mods = os.listdir(str(main_dir) + "/mods")
    except FileNotFoundError:
        # First launch, installation
        prev_mods = []


    # 3. Update the repo
    # this will ensure the repo exists and is up-to-date
    # (In this process, we might have updated the modlist)
    try:
        repo = Repo(main_dir)
        origin = repo.remote()
        origin.fetch()
        repo.git.reset("--hard")
        repo.git.merge("origin/master")
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

    # 4. Deduct which mods need to be removed and which installed
    # Sets are a great tool to find differences between lists
    prev_modlist = set(prev_modlist.keys())
    prev_mods = set(prev_mods)
    new_modlist = set(modlist.keys())

    # Remove: Mods that were both in the prev_modlist and installed but that are not in the new_modlist
    mods_to_remove = (prev_modlist & prev_mods) - new_modlist
    # Download: Mods that are not installed but are in the new modlist
    mods_to_download = new_modlist - prev_mods

    # Remove mods
    for mod in mods_to_remove:
        print(f"Removing deprecated {mod}")
        os.remove(str(main_dir) + f"/mods/{mod}")

    # Download mods
    # (first get the URLS of the mods to download and build a proper dict for download_stuff)
    download_dict = dict()
    for mod in mods_to_download:
        download_dict[mod] = modlist[mod]
    failed_downloads = download_stuff(str(main_dir) + "/mods", download_dict, f"{app.translations['downloading_title']}: {launch_data.modpack}")

    if failed_downloads:
        for mod in failed_downloads:
            print(f"ERROR: {mod} mod download failed")

        error_popup = ModpackDownloadError(app, launch_data, failed_downloads)
        error_popup.wait_window()  # Wait until the popup closes (choice made)
        choice = error_popup.get_choice()

        # Continue
        if choice is True:
            pass

        # Retry
        if choice is False:
            return build_modpack_env(launch_data, app)

        # Abort
        if choice is None:
            # Display error
            app.update_status("error", app.translations["modpack_error_abort"])
            return None

    """
        Launch parameters path should always point to the root of the minecraft installation (kinda like the .minecraft
        folder)
        At the same time, we want to launch forge on the installed modpack's directory CalvonettaModpacks/...
        To do this, we inject the new path into the launch parameters, use it to build the env and then restore the
        "root" path
    """
    root_path = launch_data.path
    launch_data.path = main_dir
    launch_data.version = version_id
    launch_data.subversion = subversion_id

    env =  build_forge_env(launch_data, app)
    # Restore the path before returning
    launch_data.path = root_path
    return env
