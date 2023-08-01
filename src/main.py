import customtkinter as ctk
from PIL import Image
from pathlib import Path
import json
from get_versions import get_vanilla_versions, get_forge_versions
from launch_manager import launch_vanilla, launch_forge
from threading import Thread


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.refresh_icon = ctk.CTkImage(light_image=Image.open("./../assets/refresh.png"), size=(20, 20))
        self.check_icon = ctk.CTkImage(light_image=Image.open("./../assets/check.png"), size=(20, 20))
        # light_image = dark_image
        self.version_type_to_get = ctk.StringVar(value="base")

        self.title("PyMinecraft Launcher")
        # self.geometry("600x600")

        # Grid configure
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5), weight=1)

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

        # Choose version type
        self.version_type = ctk.CTkOptionMenu(self.version_frame, values=["Vanilla", "Forge", "Modpack"],
                                              command=self.update_versions)
        self.version_type.grid(row=1, padx=30, pady=10, sticky="w")

        # Choose version number
        self.version_number = ctk.CTkOptionMenu(self.version_frame, values=self.get_versions(),
                                                command=self.update_subversions)
        self.version_number.grid(row=2, column=0, padx=30, pady=10, sticky="w")

        # Choose subversion number
        self.subversion_number = ctk.CTkOptionMenu(self.version_frame, values=self.get_versions())
        self.subversion_number.grid(row=2, column=1, padx=30, pady=10, sticky="w")

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

        self.input_installation_path = ctk.CTkEntry(self.parameters_frame, width=180, height=20)
        self.input_installation_path.insert(0, self.get_default_path())  # Set entry to default path
        self.input_installation_path.grid(row=3, column=0, padx=20, pady=10, sticky="w")

        self.reset_installation_path_button = ctk.CTkButton(self.parameters_frame, width=20, height=20,
                                                            command=self.reset_installation_path, text="Reset")
        self.reset_installation_path_button.grid(row=3, column=1, padx=(0, 20), sticky="e")

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

        # Status indicator
        self.status_indicator = ctk.CTkLabel(self,  corner_radius=5)
        self.status_indicator.grid(row=5, column=0, padx=60, pady=(0, 10), sticky="ew", columnspan=2)
        self.update_status("idle")


        # Load launch data (if any) and update variables
        try:
            launch_data = self.load_launch_data()
            self.input_username_field.insert(0, launch_data["username"])
            self.input_ram_field.insert(0, launch_data["ram"])

            # To set the value of the path it first needs to be emptied
            self.input_installation_path.delete(0, ctk.END)
            self.input_installation_path.insert(0, launch_data["path"])

            self.input_email_field.insert(0, launch_data["email"])
            self.version_type.set(launch_data["version_type"])
            self.version_number.set(launch_data["version"])
            self.subversion_number.set(launch_data["subversion"])
            self.appearance_mode.set(launch_data["theme"])  # set the value
            self.change_appearance_mode(launch_data["theme"])  # Change the theme
        except FileNotFoundError:
            pass

        self.update_versions(self.version_type.get())

    def change_appearance_mode(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

    def get_versions(self):
        # Actually working for vanilla & forge

        version_type_to_get = self.version_type.get()
        if version_type_to_get == "Vanilla":
            print(f"Getting {version_type_to_get} version list...")
        elif version_type_to_get == "Forge":
            print(f"Getting {version_type_to_get} version and subversion dictionary...")

        versions = []
        if version_type_to_get == "Vanilla":
            versions = get_vanilla_versions()
        elif version_type_to_get == "Forge":
            versions = get_forge_versions()
        elif version_type_to_get == "Modpack":
            print("Modpack mode not avaliable yet, WIP")
        else:
            print("Version type not found")

        return versions

    def update_versions(self, choice):
        # choice must be accepted as a parameter or the function will raise an error

        """
        This function is used by the version_type OptionMenu to update the version and subversion numbers
        """

        print("UPDATING VERSIONS")

        # Choice will always be in ("Vanilla", "Forge", "Modpack")

        # Get version list (numbers) according to selected type

        version_list = self.get_versions()

        if choice == "Vanilla":
            """
            version_list will be a list of versions
            """

            # Set the parent version field values
            self.version_number.configure(values=version_list)

            # Disable and empty subversion field
            self.subversion_number.configure(values=[""], state="disabled")
            self.subversion_number.set("")

        elif choice == "Forge":
            """
            version_list will be a dictionary where {parent_version : forge_subversions}
            """

            # Set the parent version field values
            self.version_number.configure(values=list(version_list.keys()))

            # Enable the subversion field
            self.subversion_number.configure(values=[""], state="enabled")

            # Update the subversion field values
            self.update_subversions(self.version_number.get())

        return

    def update_subversions(self, parent_version):
        """
        This function is used to refresh the subversion numbers.
        choice = parent version number | ex: "1.12.2"
        """

        print("UPDATING SUBVERSIONS")
        version_list = self.get_versions()
        version_type = self.version_type.get()

        if version_type == "Vanilla":
            pass  # There are no subversions --- the subversion OptionMenu should be " " and disabled
        elif version_type == "Forge":
            subversion_list = version_list[parent_version]  # In this case choice = self.version_number.get()
            self.subversion_number.configure(values=subversion_list)
            self.subversion_number.set(subversion_list[0])  # Set to latest by default


    def get_default_path(self):
        user_path = str(Path.home())
        installation_path = user_path + "\\AppData\\Roaming\\.minecraft"
        return installation_path

    def reset_installation_path(self):
        default_path = self.get_default_path()
        self.input_installation_path.delete(0, ctk.END)  # Clean the entry
        self.input_installation_path.insert(0, default_path)  # Set the entry to the default path
        print("Path reseted")
        return

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

    def save_launch_data(self, launch_data):
        user_path = str(Path.home())
        launch_data_path = user_path + "\\Documents"

        with open(launch_data_path + "\\launch_data.json", "w") as json_file:
            json.dump(launch_data, json_file)

    def load_launch_data(self):
        user_path = str(Path.home())
        launch_data_path = user_path + "\\Documents"

        try:
            with open(launch_data_path + "/launch_data.json", "r") as json_file:
                launch_data = json.load(json_file)
            return launch_data
        except FileNotFoundError:
            raise FileNotFoundError

    def get_launch_parameters(self):

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

        # Check that ram value is correct
        try:
            launch_parameters["ram"] = int(launch_parameters["ram"])
        except ValueError:
            print("RAM must be a number")
            return

        # If an email is not provided, log in as no-premium
        if launch_parameters["email"] != "":
            launch_parameters["premium"] = True
        else:  # an email address is given
            launch_parameters["premium"] = False

        # This part is only "triggered" if a path neither provided nor loaded from the .json file
        inserted_path = self.input_installation_path.get()
        if inserted_path == "":
            launch_parameters["path"] = self.get_default_path()
        else:
            launch_parameters["path"] = inserted_path

        return launch_parameters

    def launch_game(self):
        print("Launching game...")

        launch_data = self.get_launch_parameters()
        # When using fstrings the dict key must be quoted with '', not ""

        self.save_launch_data(launch_data)
        self.update_status("Launching the game")
        # Make separate threads so that the launcher doesn't block
        if launch_data["version_type"] == "Vanilla":
            #launch_vanilla(launch_data)  # old
            Thread(target=launch_vanilla, args=(launch_data,)).start()
        elif launch_data["version_type"] == "Forge":
            #launch_forge(launch_data, self)  # old
            Thread(target=launch_forge, args=(launch_data, self)).start()

        return

    def update_status(self, code: str, message="undefined"):

        """
        This method updates the message and foreground color of the label under the launch button.
        It is used to indicate what the launcher is doing internally so that the user can know that
        the launcher is actually doing something.

        Params:
        (status) code: idle, working, success, error
        message (not needed in case that code=idle)
        """

        # (light_color, dark_color) foreground color pairs for different status modes
        IDLE_STATUS_COLOR = ("gray", "darkgray")
        WORKING_STATUS_COLOR = ("light_yellow", "yellow")
        SUCCESS_STATUS_COLOR = ("green", "darkgreen")
        ERROR_STATUS_COLOR = ("red", "darkred")

        if code == "idle":
            self.status_indicator.configure(fg_color=IDLE_STATUS_COLOR)
            self.status_indicator.configure(text=f"IDLE: Waiting for launch")

        elif code == "working":
            self.status_indicator.configure(fg_color=WORKING_STATUS_COLOR)
            self.status_indicator.configure(text=f"WORKING: {message}")

        elif code == "success":
            self.status_indicator.configure(fg_color=SUCCESS_STATUS_COLOR)
            self.status_indicator.configure(text=f"SUCCESS: {message}")

        elif code == "error":
            self.status_indicator.configure(fg_color=ERROR_STATUS_COLOR)
            self.status_indicator.configure(text=f"ERROR: {message}")

        else:  # This should never happen, but just in case it will be treated as an error
            self.status_indicator.configure(fg_color=ERROR_STATUS_COLOR)
            self.status_indicator.configure(text=f"ERROR: No status code --> message: {message}")
        return

    def get_latest_launcher_version(self):
        # WIP placeholder
        latest = "latest: 0.1"
        return latest

    def update_launcher(self):
        # WIP placeholder
        print("Updating launcher")
        return


if __name__ == "__main__":
    app = App()
    app.mainloop()
