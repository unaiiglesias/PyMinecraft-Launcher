import tkinter.ttk

import customtkinter

import customtkinter as ctk
import portablemc
from PIL import Image
from subprocess import Popen
from pathlib import Path


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.refresh_icon = ctk.CTkImage(light_image=Image.open("./../assets/refresh.png"), size=(20, 20))
        self.check_icon = ctk.CTkImage(light_image=Image.open("./../assets/check.png"), size=(20, 20))
        # light_image = dark_image
        self.version_type_to_get = customtkinter.StringVar(value="base")

        self.title("PyMinecraft Launcher")
        # self.geometry("600x600")

        # Grid configure
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4), weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="PyMinecraft Launcher", font=("calibri", 24))
        self.header.grid(row=0, column=1, rowspan=1, padx=20, pady=(10, 0), sticky="n")

        # Credentials frame
        self.credentials_frame = ctk.CTkFrame(self)
        self.credentials_frame.grid(row=1, column=1, padx=20, pady=10, sticky="nswe")
        self.credentials_frame.rowconfigure(4)

        self.input_username_label = ctk.CTkLabel(self.credentials_frame, text="Username")
        self.input_username_label.grid(row=0, padx=20, pady=(5, 0), sticky="w")

        self.input_username_field = ctk.CTkEntry(self.credentials_frame, width=200, height=20,
                                                 placeholder_text="Username")
        self.input_username_field.grid(row=1, padx=20, pady=5, sticky="w")

        self.input_email_label = ctk.CTkLabel(self.credentials_frame, text="Email (Premium only)")
        self.input_email_label.grid(row=2, padx=20, pady=(0, 5), stick="w")

        self.input_email_field = ctk.CTkEntry(self.credentials_frame, width=160, height=20,
                                              placeholder_text="example@gmail.com")
        self.input_email_field.grid(row=3, padx=(20, 0), pady=(0, 5), sticky="w")

        self.log_in_button = ctk.CTkButton(self.credentials_frame, width=20, height=20, fg_color="white",
                                           command=self.log_in, image=self.refresh_icon, text="")
        self.log_in_button.grid(row=3, padx=(0, 20), pady=(0, 5), sticky="e")

        # Version choice frame
        self.version_frame = ctk.CTkFrame(self)
        self.version_frame.rowconfigure(3)
        self.version_frame.grid(row=2, column=1, padx=20, pady=10, sticky="nswe")

        self.version_label = ctk.CTkLabel(self.version_frame, text="Version to launch")
        self.version_label.grid(row=0, padx=20, pady=0, sticky="w")

        self.version_type = ctk.CTkOptionMenu(self.version_frame, values=["Vanilla", "Forge", "Modpack"])
        self.version_type.grid(row=1, padx=30, pady=10, sticky="w")

        self.version_number = ctk.CTkOptionMenu(self.version_frame, values=self.get_versions())
        self.version_number.grid(row=2, padx=30, pady=10, sticky="w")

        # (Launch) Parameters frame
        self.parameters_frame = ctk.CTkFrame(self)
        self.parameters_frame.rowconfigure(4)
        self.parameters_frame.grid(row=3, column=1, padx=20, pady=10, sticky="nswe")

        self.input_ram_label = ctk.CTkLabel(self.parameters_frame, text="RAM amount")
        self.input_ram_label.grid(padx=20, pady=0, sticky="w", columnspan=2, row=0)

        self.input_ram_field = ctk.CTkEntry(self.parameters_frame, width=60, height=20, placeholder_text="RAM")
        self.input_ram_field.grid(padx=(20, 0), pady=0, sticky="we", column=0, columnspan=1, row=1)

        self.input_ram_unit = ctk.CTkLabel(self.parameters_frame, text="Mb")
        self.input_ram_unit.grid(column=1, columnspan=1, padx=5, row=1, sticky="w")

        self.input_installation_path_label = ctk.CTkLabel(self.parameters_frame, text="Installation path")
        self.input_installation_path_label.grid(row=2, columnspan=2, padx=20, sticky="w")

        self.input_installation_path = ctk.CTkEntry(self.parameters_frame, width=200, height=20,
                                                    placeholder_text=self.get_default_path())
        self.input_installation_path.grid(row=3, columnspan=2, padx=20, pady=10, sticky="w")

        # Side options frame
        self.side_frame = ctk.CTkFrame(self)
        self.side_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nswe")
        self.side_frame.rowconfigure(3)

        self.appearance_mode_label = ctk.CTkLabel(self.side_frame, text="Theme mode")

        self.appearance_mode = ctk.CTkOptionMenu(self.side_frame, values=["Light", "Dark", "System"],
                                                 command=self.change_appearance_mode)
        self.appearance_mode.grid(row=0, padx=20, pady=10)

        self.update_button = ctk.CTkButton(self.side_frame, width=160, height=30, fg_color="green",
                                           command=self.update_launcher, text="Update")
        self.update_button.grid(row=1, padx=20, pady=(10, 0))

        self.version_label = ctk.CTkLabel(self.side_frame, text=self.get_launcher_version())
        self.version_label.grid(row=2, padx=(20, 0), pady=0, sticky="w")

        self.latest_version_label = ctk.CTkLabel(self.side_frame, text=self.get_latest_launcher_version())
        self.latest_version_label.grid(row=2, padx=(0, 20), pady=0, sticky="e")

        # Launch button
        self.launch_button = ctk.CTkButton(self, text="LAUNCH", command=self.launch_game)
        self.launch_button.grid(row=4, column=0, padx=60, pady=20, sticky="ew", columnspan=2)

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def get_versions(self):
        # Actually working for vanilla

        version_type_to_get = self.version_type.get()
        print(version_type_to_get)

        manifest = portablemc.VersionManifest()
        latest = manifest.get_version("release")  # This needs to be called in order for the manifest to be fetched

        versions = []

        for version in manifest.data["versions"]:
            if version["type"] == "release" and version_type_to_get == "Vanilla":
                versions.append(version["id"])
            elif version["type"] == "release" and version_type_to_get == "Forge":
                version.append("forge:" + version["id"])
            else:  # Snapshots, pre-releases...
                pass

        return versions

    def get_default_path(self):
        user_path = str(Path.home())
        installation_path = user_path + "\\AppData\\Roaming\\.minecraft"
        return installation_path

    def log_in(self):
        print("Logging in...")
        if self.log_in_button._image == self.refresh_icon:
            self.log_in_button.configure(image=self.check_icon)
        else:
            self.log_in_button.configure(image=self.refresh_icon)
        return

    def get_launcher_version(self):
        # WIP placeholder
        version = "ver. 0.1"
        return version

    def get_latest_launcher_version(self):
        # WIP placeholder
        latest = "latest: 0.1"
        return latest

    def launch_game(self):
        print("Launching game...")

        username, version_type, version, ram, email, premium, path = get_launch_parameters(app)
        try:
            ram = int(ram)
        except ValueError:
            print("RAM must be a number")
            return

        jvm_args = f"--jvm-args=-Xmx{ram}M -XX:+UnlockExperimentalVMOptions -XX:+UseG1GC -XX:G1NewSizePercent=20" \
                   f" -XX:G1ReservePercent=20 -XX:MaxGCPauseMillis=50 -XX:G1HeapRegionSize=32M"

        if premium is True:
            login = f"-l {email} -m"
        else:
            login = ""

        if version_type in ["Vanilla", "Forge"]:
            print(f"{path}")
            Popen(f"portablemc --main-dir \"{path}\" start {login} \"{jvm_args}\" {version} -u \"{username}\"")

        return

    def update_launcher(self):
        print("Updating launcher")
        return


def get_launch_parameters(app):
    username = app.input_username_field.get()
    version_type = app.version_type.get()
    version = app.version_number.get()
    ram = app.input_ram_field.get()
    inserted_path = app.input_installation_path.get()

    email = app.input_email_field.get()
    if email != "":
        premium = True
    else:  # an email address is given
        premium = False

    if inserted_path == "":
        path = app.get_default_path()
    else:
        path = inserted_path

    return username, version_type, version, ram, email, premium, path


if __name__ == "__main__":
    app = App()
    app.mainloop()
