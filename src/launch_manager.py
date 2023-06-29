from time import sleep
from portablemc import Context, Version, StartOptions, Start
from portablemc_forge import ForgeVersionInstaller, ForgeVersion
import json
from os import path, popen, remove
import requests_html as rq
import wget
import keyboard
from pyperclip import copy
import customtkinter as ctk
import pyautogui as pag


def launch_vanilla(launch_parameters):
    main_dir = launch_parameters["path"]
    work_dir = main_dir
    version_id = launch_parameters["version"]
    ram_amount = launch_parameters["ram"]
    username = launch_parameters["username"]

    ctx = Context(main_dir, work_dir)
    version = Version(ctx, version_id)

    version.install(jvm=True)

    start_opts = StartOptions()
    start_opts.username = username
    start_opts.resolution = (1080, 720)

    start = Start(version)
    start.prepare(start_opts)
    start.jvm_args.append(f"-Xmx{ram_amount}M")
    start.start()


def make_launcher_profiles_json(main_dir):
    LAUNCHER_PROFILES_BASE = {"profiles": {"(Default)": {"created": "1970-01-01T00:00:00.0000000Z", "javaArgs": "-Xmx5G -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent\u003d20 -XX:G1ReservePercent\u003d20 -XX:MaxGCPauseMillis\u003d50 -XX:G1HeapRegionSize\u003d32M", "lastUsed": "1970-01-01T00:00:00.0000000Z", "lastVersionId": "latest-release", "name": "", "type": "custom"}}, "settings": {"crashAssistance": True, "enableAdvanced": True, "enableAnalytics": True, "enableHistorical": False, "enableReleases": True, "enableSnapshots": False, "keepLauncherOpen": False, "profileSorting": "ByLastPlayed", "showGameLog": False, "showMenu": False, "soundOn": False}}

    with open(main_dir + "\\launcher_profiles.json", "w") as json_file:
        json.dump(LAUNCHER_PROFILES_BASE, json_file)

    return


def download_forge_installer(version, subversion, main_dir):

    # TODO: Instead of making a request to fetch the link, just "guess" it formatting a string
    # ex: https://maven.minecraftforge.net/net/minecraftforge/forge/1.16.2-33.0.58/forge-1.16.2-33.0.58-installer.jar

    url = f"https://files.minecraftforge.net/net/minecraftforge/forge/index_{version}.html"
    full_version = f"{version}-{subversion}"

    # This will get the forge page for the selected game version an fetch all the links in the page
    session = rq.HTMLSession()
    r = session.get(url)
    all_links = r.html.absolute_links

    # Now, the download link for the specific subversion will be collected
    needed_url = None
    for link in all_links:
        if full_version in link and "installer" in link and "adfoc" not in link:
            needed_url = link
            break

    print(needed_url)

    # Download the installer into the main_dir (it will be named installer.jar)
    wget.download(needed_url, f"{main_dir}\\installer.jar")


def automatically_launch_forge_installer(installer_path, main_dir, version, screen_resolution):
    sleep(1)
    popen(installer_path, "r", 1)  # Open the forge installer
    sleep(6)  # Wait until the forge installer has opened

    # In order to ensure that the forge installer is focused, the window of the installer (which spawns at the center
    # of the screen) will be clicked
    print(screen_resolution)
    pag.moveTo(screen_resolution[0] / 2, screen_resolution[1] / 2 - 150)
    pag.click()

    copy(main_dir)
    print("main_dir copied")

    if version in ("1.7.2", "1.7.10", "1.8","1.8.", "1.8.9", "1.9", "1.9.4", "1.10", "1.10.2", "1.11.2", "1.14.2", "1.14.3", "1.15", "1.15.1", "1.16.1", "1.16.2", "1.16.3", "1.16.4", "1.16.5", "1.17.1", "1.18", "1.18.1", "1.18.2", "1.19", "1.19.1", "1.19.2", "1.19.3", "1.19.4", "1.20", "1.20.1"):  # These ones need an extra tab
        keyboard.send("tab")
        sleep(0.1)
    elif version in ("1.11", "1.12", "1.12.1"):  # These ones need 2 extra tabs
        keyboard.send("tab")
        sleep(0.1)
        keyboard.send("tab")
        sleep(0.1)
    elif version in ("1.12.2", "1.13.2", "1.14.4", "1.15.2"):  # These ones don't need extra tabs
        pass
    else: # Looks like most versions need an extra tab, so....
        keyboard.send("tab")
        sleep(0.1)

    keyboard.send("tab")
    sleep(0.1)
    keyboard.send("tab")
    sleep(0.1)
    keyboard.send("tab")
    sleep(0.1)
    keyboard.send("tab")
    sleep(0.1)

    keyboard.send("enter")
    sleep(0.3)
    keyboard.send("control+v")
    sleep(0.3)
    keyboard.send("enter")
    sleep(0.3)
    keyboard.send("tab")
    sleep(0.1)
    keyboard.send("enter")
    print("DONE")



def ask_if_forge_installation_has_finished(installer_path, master):
    """
    Since it would be hard to check whether the forge installation has finished,
    this function will pop up a window to ask the user before continuing with the forge installation. 
    """

    class AskIfForgeHasFinishedPopUp(ctk.CTkToplevel):
        def __init__(self, master):
            super().__init__()
            self.title("Ha acabado de instalarse Forge?")
            self.geometry("600x200")

            self.text = ctk.CTkTextbox(self, width=560, height=80)
            self.text.insert("1.0", "Espera hasta que forge termine de instalarse.\n")
            self.text.insert("2.0", "Una vez termine, pulsa OK para que se cierre la ventana de instalación.\n")
            self.text.insert("3.0", "Entonces, presiona el botón de abajo.")
            self.text.pack(padx=20, pady=10)

            self.button = ctk.CTkButton(self, text="Forge ha acabado de instalarse", command=self.destroy, width=300,
                                        height=60)
            self.button.pack(padx=50, pady=10)

            self.transient(master)  # The pop-up will stay on top of the launcher window
            self.grab_set()  # Hijack the launcher window so that it can't be clicked
            master.wait_window(self)  # Tell the launcher window to wait (block itself)

    pop_up = AskIfForgeHasFinishedPopUp(master)
    sleep(1)  # Give the forge installer some time to completely close, in case the user clicks too fast
    remove(installer_path)  # Remove installer as it is no longer needed


def launch_forge(launch_parameters, app):
    main_dir = launch_parameters["path"]
    work_dir = main_dir
    version_id = launch_parameters["version"]
    subversion_id = launch_parameters["subversion"]
    ram_amount = launch_parameters["ram"]
    username = launch_parameters["username"]

    screen_resolution = (app.winfo_screenwidth(), app.winfo_screenheight())

    if not path.isfile(main_dir + "\\launcher_profiles.json"):
        make_launcher_profiles_json(main_dir)
    #  If there is no launcher_profiles json, make one. The forge installer will need it to run.

    ctx = Context(main_dir, work_dir)

    full_version_id = f"{version_id}-{subversion_id}"
    print(f"Launching : {full_version_id}")

    installer = ForgeVersionInstaller(ctx, full_version_id)

    if installer.needed():  # The version needs to be installed

        # Download and use forge manual version installer
        download_forge_installer(version_id, subversion_id, main_dir)

        installer_path = f"{main_dir}\\installer.jar"
        automatically_launch_forge_installer(installer_path, main_dir, version_id, screen_resolution)
        ask_if_forge_installation_has_finished(installer_path, app)

        installer.prepare()
        installer.download()
        installer.install()

    version = ForgeVersion(ctx, full_version_id)
    version.install(jvm=True)

    start_opts = StartOptions()
    start_opts.username = username
    start_opts.disable_multiplayer = False
    start_opts.resolution = (1080, 720)

    start = Start(version)
    start.prepare(start_opts)
    start.jvm_args.append(f"-Xmx{ram_amount}M")
    start.start()


if __name__ == "__main__":
    launch_forge({"path" : "C:\\Users\\unai\\Desktop\\PMC-main_dir", "version" : "1.16.3", "subversion" : "34.1.42", "ram": 4048, "username" : "Xtrike"})

"""
        launch_parameters = {
            "username": self.input_username_field.get(),
            "version_type": self.version_type.get(),
            "version": self.version_number.get(),
            "subversion": self.subversion_number.get(),
            "ram": self.input_ram_field.get(),
            "path": self.input_installation_path.get(),
            "email": self.input_email_field.get(),
            "premium": False,  # Make it false by default
            "theme": self.appearance_mode.get()
        }
"""