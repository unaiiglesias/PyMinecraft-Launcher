from portablemc.forge import request_maven_versions
from portablemc.standard import VersionManifest
import json
import datetime


def fetch_vanilla_versions_from_internet():

    manifest = VersionManifest()
    manifest.get_version("release")  # This needs to be called in order for the manifest to be fetched

    vanilla_versions = []
    for version in manifest.data["versions"]:
        if version["type"] == "release":
            vanilla_versions.append(version["id"])

    return vanilla_versions


def fetch_forge_versions_from_internet():
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

    return forge_versions


def get_vanilla_versions(cache_data_path: str, app):
    """
    Function that loads the versions list from a cached file. If no file is found it instead loads
    the manifest from the internet and creates the cache file.
    A versions cache file will be considered to be outdated after a day has passed.

    Args:
        cache_data_path: Path to the minecraft installation path
    """

    versions_cache_file = f"{cache_data_path}\\cache_vanilla_versions.json"

    # If there already exists an updated version cache file, load it and return it
    app.update_status("working", app.translations["status_working_loading_cached_vanilla_versions"])

    today = datetime.datetime.now().day  # get today's number of the month

    if app.cfg["cache_day_vanilla"] == today:
        # Cache is updated, use cache
        print("Reading vanilla versions from file")
        try:
            with open(versions_cache_file, "r") as versions_file:
                vanilla_versions = json.load(versions_file)
                return vanilla_versions
        except FileNotFoundError:
            print("ERROR: Reported updated cache but file was not found")

    print("Reading vanilla versions from the internet")

    # Load from the internet
    app.update_status("working", app.translations["status_working_fetching_vanilla_versions"])

    vanilla_versions = fetch_vanilla_versions_from_internet()

    app.update_status("working", app.translations["status_working_caching_vanilla_versions"])

    with open(versions_cache_file, "w") as versions_file:
        json.dump(vanilla_versions, versions_file)

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
    """

    versions_cache_file = f"{cache_data_path}\\cache_forge_versions.json"
    today = datetime.datetime.now().day  # get today's number of the month

    # If there already exists an updated version cache file, load it and return it
    app.update_status("working", app.translations["status_working_loading_cached_forge_versions"])

    if app.cfg["cache_day_forge"] == today:
        # Cache is updated, use cache
        try:
            print("Reading forge versions from file")
            with open(versions_cache_file, "r") as versions_file:

                forge_versions = json.load(versions_file)
                return forge_versions

        except FileNotFoundError:
            print("ERROR: reported updated forge cache but file was not found")

    print("Reading forge versions from the internet")

    app.update_status("working", app.translations["status_working_fetching_forge_versions"])

    forge_versions = fetch_forge_versions_from_internet()

    # Add latest and recommended subversions in each forge version
    for version in forge_versions.keys():
        forge_versions[version].insert(0, "recommended")
        forge_versions[version].insert(0, "latest")

    app.update_status("working", app.translations["status_working_caching_forge_versions"])
    with open(versions_cache_file, "w") as versions_file:
        json.dump(forge_versions, versions_file)

    return forge_versions




if __name__ == "__main__":
    print(get_forge_versions())
