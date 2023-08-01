from portablemc_forge import request_maven_versions
from portablemc import VersionManifest
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


def get_forge_versions(cache_data_path: str):
    """
    Function that loads the full forge versions list from a cached file. If no file is
    found it instead loads the manifest from the internet and creates the cache file.
    A versions cache file will be considered to be outdated after a day has passed.

    Note: the function is a duplicate of the vanilla versions one except the forge versions
    are saved into a dictionary instead of a list.

    TODO: Find a way of having a single function that handles this instead of 2 that do almost the same

    Args:
        installation_path: Path to the minecraft installation path
    """

    versions_cache_file = f"{cache_data_path}\\cache_forge_version_list.json"
    today = datetime.datetime.now().strftime("%d")  # get today's number of the month

    # If there already exists an updated version cache file, load it and return it
    try:
        with open(versions_cache_file, "r") as versions_file:
            forge_versions = json.load(versions_file)

            if forge_versions["day_of_creation"] != today:
                raise FileNotFoundError  # If the file is outdated (wasn't created today) act as if it didn't exist

            forge_versions.pop("day_of_creation")  # Remove the last key (date)
            return forge_versions
    except FileNotFoundError:
        pass  # Do all the downloading and caching into file stuff

    forge_versions = fetch_forge_versions_from_internet()

    with open(versions_cache_file, "w") as versions_file:
        forge_versions["day_of_creation"] = today  # The last key of the dict will be the day it was created
        json.dump(forge_versions, versions_file)

    forge_versions.pop("day_of_creation")  # Remove the date element from the list before returning

    return forge_versions


def get_vanilla_versions(cache_data_path: str):
    """
    Function that loads the versions list from a cached file. If no file is found it instead loads
    the manifest from the internet and creates the cache file.
    A versions cache file will be considered to be outdated after a day has passed.

    Args:
        installation_path: Path to the minecraft installation path
    """

    versions_cache_file = f"{cache_data_path}\\cache_vanilla_version_list.json"
    today = datetime.datetime.now().strftime("%d")  # get today's number of the month

    # If there already exists an updated version cache file, load it and return it
    try:
        with open(versions_cache_file, "r") as versions_file:
            vanilla_versions = json.load(versions_file)

            if vanilla_versions[-1] != today:
                raise FileNotFoundError  # If the file is outdated (wasn't created today) act as if it didn't exist

            vanilla_versions.pop()  # Remove the last item (date)
            return vanilla_versions
    except FileNotFoundError:
        pass  # Do all the downloading and caching into file stuff

    vanilla_versions = fetch_vanilla_versions_from_internet()

    with open(versions_cache_file, "w") as versions_file:
        vanilla_versions.append(today)  # The last element of the versions list will be the day it was created
        json.dump(vanilla_versions, versions_file)

    vanilla_versions.pop()  # Remove the date element from the list before returning

    return vanilla_versions


if __name__ == "__main__":
    print(get_forge_versions())
