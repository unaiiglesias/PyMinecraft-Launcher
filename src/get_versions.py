from portablemc_forge import request_maven_versions
from portablemc import VersionManifest


def get_vanilla_versions():
    manifest = VersionManifest()
    latest = manifest.get_version("release")  # This needs to be called in order for the manifest to be fetched

    vanilla_versions = []
    for version in manifest.data["versions"]:
        if version["type"] == "release":
            vanilla_versions.append(version["id"])

    return vanilla_versions


def get_forge_versions():
    maven_versions = request_maven_versions()

    # Now lets display them as a dict where --> {parent version : forge subversions} (we'll remove the "-"s)

    forge_versions = {}

    for full_ver in maven_versions:
        splitted_ver = full_ver.split("-")
        parent_version = splitted_ver[0]
        forge_subversion = splitted_ver[1]

        if parent_version not in forge_versions:  # The parent forge version doesn't exist in the dict
            forge_versions[parent_version] = []  # Make it and create the list for the forge subversions

        forge_versions[parent_version].append(forge_subversion)

    return forge_versions


if __name__ == "__main__":
    print(get_forge_versions())
