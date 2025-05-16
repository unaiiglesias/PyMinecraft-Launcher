from src.app_utils.launch_data_manager import LaunchData
from src.util.utilities import load_json
from src.launch_managers.forge_launcher import launch_forge
from src.custom_windows.popup_download import ProgressBarWindow
import copy
import os
from wget import download
from urllib.error import HTTPError
from json.decoder import JSONDecodeError


def launch_modpack(launch_data : LaunchData, app):
    """

    Args:
        launch_data:
        app:

    Returns:
        portablemc env to be run
    """

    from git import Repo, InvalidGitRepositoryError, NoSuchPathError
    # path/CalvonettaModpacks/modpackName
    main_dir = launch_data.path + f"/CalvonettaModpacks/{launch_data.modpack}"
    repo_url = f"https://github.com/CalvonettaModpacks/{launch_data.modpack}.git"
    # Forge version and subversion will be fetched

    # Before we update (and potentially overwrite) it, we keep a copy of the current modlist
    try:
        prev_modlist = load_json(main_dir + "/mods/modlist.json")
    except (FileNotFoundError, JSONDecodeError) as error:
        # If the modlist is broken, we want to fix it with the remote repo
        if type(error).__name__ == "JSONDecodeError":
            print("WARNING: Modlist read failed. This could mean the modlist was corrupted or had been wrongly modified.")
        prev_modlist = []

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

    """
        Launch parameters path should always point to the root of the minecraft installation (kinda like the .minecraft
        folder)
        At the same time, we wan't to launch forge on the installed modpack's directory CalvonettaModpacks/...
        To do this, we just create "disposable" new launch parameters we'll use to launch forge there, but we won't write
        them to disk
    """
    new_parameters = copy.deepcopy(launch_data) # We'll "inject" the new data into the launch parameters
    new_parameters.path = main_dir
    new_parameters.version = version_id
    new_parameters.subversion = subversion_id

    current_mods = os.listdir(str(main_dir) + "/mods")

    # If we haven't updated the modlist, we skip this step
    # If we have updated the modlist, apply the corresponding changes
    if prev_modlist != modlist or current_mods != modlist:
        # We'll do 2 swipes over the modlis: one to remove unused mods and another one to add the new ones

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

        progress_bar = ProgressBarWindow(f"{app.translations['downloading_title']}: {launch_data.modpack}")
        progress_bar.set_total(len(download_list))

        for ind, mod in enumerate(download_list):
            # Download the mod with wget
            try:
                download(modlist[mod], out=main_dir + f"/mods/{mod}", bar=progress_bar.update_speed_from_wget)
            except HTTPError:
                print("ERROR: Mod download failed! " + mod)
            progress_bar.update_progress(ind, 0)
        progress_bar.finish()

    return launch_forge(new_parameters, app)