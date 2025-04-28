from portablemc.forge import request_maven_versions
from portablemc.standard import VersionManifest

from src.config_manager import save_ini
from utilities import load_json, save_json
import datetime
import github # PyGithub


def fetch_vanilla_versions_from_internet():
    """
    Returns a list with all vanilla version numbers
    """

    manifest = VersionManifest()
    manifest.get_version("release")  # This needs to be called in order for the manifest to be fetched

    vanilla_versions = []
    for version in manifest.data["versions"]:
        if version["type"] == "release":
            vanilla_versions.append(version["id"])

    return vanilla_versions


def fetch_forge_versions_from_internet():
    """
    Returns a dict where {version number: [subversion list]}
    """
    maven_versions = request_maven_versions()

    # Now lets display them as a dict where --> {parent version : forge subversions} (we'll remove the "-"s)

    forge_versions = {}

    for full_ver in maven_versions:
        splitted_ver = full_ver.split("-")
        parent_version = splitted_ver[0]
        forge_subversion = splitted_ver[1]

        if parent_version not in forge_versions:  # The parent forge version key doesn't exist in the dict
            forge_versions[parent_version] = []  # Make it and create the list for the forge subversions

        forge_versions[parent_version].append(forge_subversion)    # append the forge subversion to the parent
        # version's value list

    # Add latest and recommended subversions in each forge version
    for version in forge_versions.keys():
        forge_versions[version].insert(0, "recommended")
        forge_versions[version].insert(0, "latest")

    return forge_versions


def fetch_modpack_versions_from_the_internet():
    """
    Returns a list with all modpack names
    """
    g = github.Github()

    resul = []

    for repo in g.get_user("CalvonettaModpacks").get_repos():
        resul.append(repo.name)
    return resul


def get_vanilla_versions(cache_data_path: str, app):
    """
    Function that loads the versions list from a cached file. If no file is found it instead loads
    the manifest from the internet and creates the cache file.
    A versions cache file will be considered to be outdated after a day has passed.

    Args:
        cache_data_path: Path to the minecraft installation path
        app: master app
    """

    versions_cache_file = f"{cache_data_path}\\cache_vanilla_versions.json"

    # If there already exists an updated version cache file, load it and return it
    app.update_status("working", app.translations["status_working_loading_cached_vanilla_versions"])

    today = datetime.datetime.now().day  # get today's number of the month

    if app.cfg["MAIN"]["cache_day_vanilla"] == today:
        # Cache is updated, use cache
        print("Reading vanilla versions from file")
        try:
            return load_json(versions_cache_file)
        except FileNotFoundError:
            print("ERROR: Reported updated cache but file was not found")

    print("Reading vanilla versions from the internet")

    # Load from the internet
    app.update_status("working", app.translations["status_working_fetching_vanilla_versions"])
    vanilla_versions = fetch_vanilla_versions_from_internet()

    # Save cache
    app.update_status("working", app.translations["status_working_caching_vanilla_versions"])
    save_json(vanilla_versions, versions_cache_file)

    app.cfg["MAIN"]["cache_day_vanilla"] = today
    save_ini(app.cfg)

    return vanilla_versions


def get_forge_versions(cache_data_path: str, app):
    """
    Function that loads the full forge versions list from a cached file. If no file is
    found it instead loads the manifest from the internet and creates the cache file.
    A versions cache file will be considered to be outdated after a day has passed.

    Note: the function is a duplicate of the vanilla versions one except the forge versions
    are saved into a dictionary instead of a list.

    TODO: Find a way of having a single function that handles this instead of 2 that do almost the same

    Args:
        cache_data_path: Path to the minecraft installation path
        app: master app
    """

    versions_cache_file = f"{cache_data_path}\\cache_forge_versions.json"
    today = datetime.datetime.now().day  # get today's number of the month

    # If there already exists an updated version cache file, load it and return it
    app.update_status("working", app.translations["status_working_loading_cached_forge_versions"])

    if app.cfg["MAIN"]["cache_day_forge"] == today:
        # Cache is updated, use cache
        try:
            print("Reading forge versions from file")
            return load_json(versions_cache_file)
        except FileNotFoundError:
            print("ERROR: reported updated forge cache but file was not found")

    print("Reading forge versions from the internet")

    # Load from the internet
    app.update_status("working", app.translations["status_working_fetching_forge_versions"])
    forge_versions = fetch_forge_versions_from_internet()

    # Save cache
    app.update_status("working", app.translations["status_working_caching_forge_versions"])
    save_json(forge_versions, versions_cache_file)

    app.cfg["MAIN"]["cache_day_forge"] = today
    save_ini(app.cfg)

    return forge_versions


def get_modpack_versions(cache_data_path: str, app):
    """
    Function that loads all avaliable modpacks and returns a list with their names
    Cache will only contain the modpack names, modlist and files will be handled on launch
    TODO: Figure out a way of having cache
    Args:
        cache_data_path: path to cache_modpack_versions.json (now ".")
        app: master app

    """

    # TODO: should we have cache or just always fetch from the internet
    versions_cache_file = f"{cache_data_path}\\cache_modpack_versions.json"
    today = datetime.datetime.now().day  # get today's number of the month


    app.update_status("working", app.translations["status_working_fetching_modpack_versions"])
    modpack_versions = fetch_modpack_versions_from_the_internet()

    return modpack_versions


if __name__ == "__main__":
    print(fetch_modpack_versions_from_the_internet())
