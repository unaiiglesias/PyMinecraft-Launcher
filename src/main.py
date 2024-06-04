import datetime
import os
from PIL import Image
import customtkinter as ctk
from pathlib import Path
from get_versions import get_vanilla_versions, get_forge_versions
from launch_manager import launch_vanilla, launch_forge
import config_manager
from threading import Thread
from tkinter import filedialog

"""
Default font:
Roboto 13
"""


class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        # load config.ini dictionary
        self.cfg = config_manager.load_ini()

        # "Global" app variables
        self.launcher_version = self.cfg["version"]
        self.translations = config_manager.load_translations(self.cfg["language"])

        self.title(self.cfg["title"])
        self.iconbitmap(self.cfg["icon"])
        # self.geometry("600x600")

        # App grid configuration
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Status indicator --> This needs to be "initialised" early or some widgets that try to modify it during load
        # will raise exceptions
        self.status_indicator = ctk.CTkLabel(self,  corner_radius=5, text_color="black")
        self.status_indicator.grid(row=5, column=0, columnspan=2, sticky="ew", padx=60, pady=(0, 10))
        self.update_status("idle")

        # Header
        self.header = ctk.CTkLabel(self, text=self.cfg["title"], font=("calibri", 24))
        self.header.grid(row=0, column=1, rowspan=1, sticky="n", pady=10, padx=20)

        # Credentials frame
        self.credentials_frame = ctk.CTkFrame(self)
        self.credentials_frame.grid(row=1, column=1, sticky="nswe", padx=20, pady=10)
        self.credentials_frame.rowconfigure(2)

        self.input_username_label = ctk.CTkLabel(self.credentials_frame, text="Username")
        self.input_username_label.grid(row=0, column=0, sticky="w", padx=20, pady=(5, 0))

        self.input_username_field = ctk.CTkEntry(self.credentials_frame, width=300, height=20,
                                                 placeholder_text="Steve")
        self.input_username_field.grid(row=1, sticky="w", padx=20, pady=(5, 10))

        # Version choice frame
        self.version_frame = ctk.CTkFrame(self)
        self.version_frame.rowconfigure(3)
        self.version_frame.grid(row=2, column=1, sticky="nswe", padx=20, pady=10)

        self.version_to_launch_label = ctk.CTkLabel(self.version_frame, text="Version to launch")
        self.version_to_launch_label.grid(row=0, sticky="w", padx=20, pady=(5, 0))

        self.version_type = ctk.CTkOptionMenu(self.version_frame, values=["Vanilla", "Forge"],
                                              command=self.update_versions)
        self.version_type.grid(row=1, sticky="w", padx=20, pady=5)

        self.version_number = ctk.CTkOptionMenu(self.version_frame, values=self.get_versions(),
                                                command=self.update_subversions)
        self.version_number.grid(row=2, column=0, sticky="w", padx=20, pady=10)

        self.subversion_number = ctk.CTkOptionMenu(self.version_frame, values=self.get_versions())
        self.subversion_number.grid(row=2, column=1, sticky="w", padx=20, pady=10)

        # (Launch) Parameters frame
        self.parameters_frame = ctk.CTkFrame(self)
        self.parameters_frame.grid(row=3, column=1, sticky="nswe", padx=20, pady=10)
        self.parameters_frame.rowconfigure(5)
        self.parameters_frame.columnconfigure(2)

        self.input_ram_label = ctk.CTkLabel(self.parameters_frame, text="RAM amount")
        self.input_ram_label.grid(row=0, sticky="w", padx=20, pady=5)

        self.input_ram_field = ctk.CTkSlider(self.parameters_frame, width=300, height=20, from_=1, to=16,
                                             number_of_steps=15, command=self.update_ram_slider)
        self.input_ram_field.grid(row=1, column=0, padx=20, pady=0)

        self.input_ram_value = ctk.CTkLabel(self.parameters_frame, text="1 GB")
        self.input_ram_value.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=0)

        self.input_installation_path_label = ctk.CTkLabel(self.parameters_frame, text="Installation path")
        self.input_installation_path_label.grid(row=2, sticky="w", padx=20, pady=5)

        self.input_installation_path = ctk.CTkEntry(self.parameters_frame, width=300, height=20)
        self.input_installation_path.insert(0, self.get_default_path())  # Set entry to default path
        self.input_installation_path.grid(row=3, column=0, sticky="w", padx=(20, 0), pady=(0, 10))

        self.reset_installation_path_button = ctk.CTkButton(self.parameters_frame, width=120, height=20,
                                                            command=self.reset_installation_path, text="Reset")
        self.reset_installation_path_button.grid(row=4, column=0, padx=(40, 0), pady=(0, 10), sticky="w")

        self.browse_installation_path_button = ctk.CTkButton(self.parameters_frame, width=120, height=20,
                                                             command=self.browse_installation_path, text="Browse")
        self.browse_installation_path_button.grid(row=4, column=0, padx=(0, 40), pady=(0, 10), sticky="e")

        # Easter Egg frame
        self.easter_egg_frame = ctk.CTkFrame(self)
        self.easter_egg_frame.grid(row=1, rowspan=2, padx=15, pady=10, sticky="nswe")

        self.terror_easter_egg_image = ctk.CTkImage(Image.open("assets/terrorist.png"), size=(200, 200))
        self.terror_easter_egg = ctk.CTkLabel(self, width=200, height=200, image=self.terror_easter_egg_image,
                                              text="", fg_color="transparent")
        self.terror_easter_egg.grid(row=1, rowspan=2, column=0, padx=15, pady=10, sticky="nswe")
        self.none_image = ctk.CTkImage(Image.new('RGBA', (200, 200), (255, 0, 0, 0)), size=(200, 200))

        # Side options frame
        self.side_frame = ctk.CTkFrame(self)
        self.side_frame.grid(row=3, column=0, sticky="nswe", padx=20, pady=10)
        self.side_frame.rowconfigure(4)

        self.side_options_label = ctk.CTkLabel(self.side_frame, text="Launcher settings")
        self.side_options_label.grid(row=0, padx=20, pady=(5, 0))

        self.appearance_mode = ctk.CTkOptionMenu(self.side_frame, values=["Light", "Dark", "System"],
                                                 command=self.change_appearance_mode)
        self.appearance_mode.grid(row=1, padx=20, pady=10)
        self.appearance_mode.set(self.cfg["theme"])  # set loaded
        self.change_appearance_mode(self.cfg["theme"])  # Change to loaded

        self.language_selector = ctk.CTkOptionMenu(self.side_frame, values=["English", "Español"],
                                                   command=self.change_language)
        self.language_selector.set(self.cfg["language"])
        self.language_selector.grid(row=2, padx=20, pady=10)

        self.version_label = ctk.CTkLabel(self.side_frame, text=f"ver: {self.launcher_version}")
        self.version_label.grid(row=3, sticky="sw", padx=(20, 20), pady=0)
        self.bomb_image = ctk.CTkImage(Image.open("assets/bomb.png"), size=(25, 25))
        self.bomb_image_label = ctk.CTkLabel(self.side_frame, image=self.bomb_image, text="",
                                             fg_color="transparent")
        self.bomb_image_label.grid(row=3, padx=(40, 0), pady=0)
        self.enable_terror_easter_egg = ctk.CTkCheckBox(self.side_frame, text="", width=10, height=10,
                                                        command=self.toggle_terror_easter_egg)
        self.enable_terror_easter_egg.grid(row=3, sticky="e", padx=(0, 20), pady=0)
        if self.cfg["show_terror"]:
            self.enable_terror_easter_egg.select()
        else:
            self.enable_terror_easter_egg.deselect()
        self.toggle_terror_easter_egg()

        # Launch button
        self.launch_button = ctk.CTkButton(self, text="LAUNCH", command=self.launch_game)
        self.launch_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=60, pady=20)

        self.change_language(self.cfg["language"])  # This requires all widgets to be initialised
        # Load launch data (if any) and update variables
        try:
            launch_data = config_manager.load_launch_data()
            self.input_username_field.insert(0, launch_data["username"])
            self.input_ram_field.set(launch_data["ram"] / 1024)
            self.update_ram_slider(launch_data["ram"] / 1024)

            # To set the value of the path it first needs to be emptied
            self.input_installation_path.delete(0, ctk.END)
            self.input_installation_path.insert(0, launch_data["path"])

            self.version_type.set(launch_data["version_type"])
            self.version_number.set(launch_data["version"])
            self.subversion_number.set(launch_data["subversion"])

        except FileNotFoundError:
            pass

        except KeyError:
            print("Outdated Launch data")
            pass

        self.update_versions(self.version_type.get())  # TODO: cached day will be saved in self.cfg

    def change_appearance_mode(self, new_appearance_mode):
        if new_appearance_mode == "Claro":
            new_appearance_mode = "Light"
        elif new_appearance_mode == "Oscuro":
            new_appearance_mode = "Dark"
        elif new_appearance_mode == "Sistema":
            new_appearance_mode = "System"
        ctk.set_appearance_mode(new_appearance_mode)

    def toggle_terror_easter_egg(self):
        if self.enable_terror_easter_egg.get() == 0:
            self.terror_easter_egg.configure(image=self.none_image)
            self.terror_easter_egg.image = self.none_image
        else:
            self.terror_easter_egg.configure(image=self.terror_easter_egg_image)
            self.terror_easter_egg.image = self.terror_easter_egg_image
        self.cfg["show_terror"] = self.enable_terror_easter_egg.get()

    def get_versions(self):
        # Actually working for vanilla & forge

        version_type_to_get = self.version_type.get()
        if version_type_to_get == "Vanilla":
            print(f"Getting {version_type_to_get} version list...")
        elif version_type_to_get == "Forge":
            print(f"Getting {version_type_to_get} version and subversion dictionary...")

        versions = []
        if version_type_to_get == "Vanilla":
            versions = get_vanilla_versions(".", self)
        elif version_type_to_get == "Forge":
            versions = get_forge_versions(".", self)

        self.update_status("idle")  # Return the launcher status to idle after the versions have been loaded

        return versions

    def update_versions(self, choice):
        # choice must be accepted as a parameter or the function will raise an error

        """
        This function is used by the version_type OptionMenu to update the version and subversion numbers
        """

        print("UPDATING VERSIONS")

        # Choice will always be in ("Vanilla", "Forge")

        # Get version list (numbers) according to selected type

        version_list = self.get_versions()
        today = datetime.datetime.now().day  # get today's number of the month

        if choice == "Vanilla":
            """
            version_list will be a list of versions
            """

            # Set the parent version field values
            self.version_number.configure(values=version_list)

            # Disable and empty subversion field
            self.subversion_number.configure(values=[""], state="disabled")
            self.subversion_number.set("")
            # Update cache date
            self.cfg["cache_day_vanilla"] = today

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

            # Update cache date
            self.cfg["cache_day_forge"] = today

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

    def update_ram_slider(self, choice):
        self.input_ram_value.configure(text=f"{choice} GB")

    def get_default_path(self):
        user_path = str(Path.home())
        installation_path = user_path + "\\AppData\\Roaming\\.minecraft"
        return installation_path

    def reset_installation_path(self):
        default_path = self.get_default_path()
        self.input_installation_path.delete(0, ctk.END)  # Clean the entry
        self.input_installation_path.insert(0, default_path)  # Set the entry to the default path
        print("Installation path reseted")
        return

    def browse_installation_path(self):
        path = filedialog.askdirectory()

        if not path:  # If no path was chosen (empty path --> ""), do nothing
            return

        self.input_installation_path.delete(0, ctk.END)
        self.input_installation_path.insert(0, path)

    def change_language(self, choice):
        # choice in (English, Español)
        if choice == "English":
            self.translations = config_manager.load_translations("en")
        elif choice == "Español":
            self.translations = config_manager.load_translations("es")

        self.input_username_label.configure(text=self.translations["username_label"])
        self.version_to_launch_label.configure(text=self.translations["versions_label"])
        self.version_type.configure(values=self.translations["version_types"])
        self.input_ram_label.configure(text=self.translations["ram_amount_label"])
        self.input_installation_path_label.configure(text=self.translations["installation_path_label"])
        self.reset_installation_path_button.configure(text=self.translations["reset_path_button"])
        self.browse_installation_path_button.configure(text=self.translations["browse_path_button"])
        self.appearance_mode.configure(values=self.translations["theme_choice"])
        self.side_options_label.configure(text=self.translations["side_options_label"])
        self.launch_button.configure(text=self.translations["launch_button"])
        self.update_status("idle")  # So that the status bar text updates
        return

    def get_launch_parameters(self):

        launch_parameters = {
            "username": self.input_username_field.get(),
            "version_type": self.version_type.get(),
            "version": self.version_number.get(),
            "subversion": self.subversion_number.get(),
            "ram": self.input_ram_field.get() * 1024,  # RAM is got in GB
            "path": self.input_installation_path.get(),
            "premium": False,  # Make it false by default
        }

        # Check that a username was introduced, if not, set Steve as username
        if not launch_parameters["username"]:
            launch_parameters["username"] = "Steve"
            self.input_username_field.insert(0, "Steve")

        # Turn RAM value into an integer
        launch_parameters["ram"] = int(launch_parameters["ram"])

        # This part is only "triggered" if a path is neither provided via GUI nor loaded from the .json file
        inserted_path = self.input_installation_path.get()
        if inserted_path == "":
            launch_parameters["path"] = self.get_default_path()
        else:
            launch_parameters["path"] = inserted_path

        # Check that path is valid (= It doesn't throw PermissionError)
        try:
            test_file_path = launch_parameters["path"] + "\\test.txt"
            with open(test_file_path, "w") as test_file:
                test_file.write("Do we got permission?")
            os.remove(test_file_path)
        except PermissionError:
            print("Invalid Path")
            raise PermissionError

        return launch_parameters

    def update_cfg(self):
        """
        Updates self.cfg so that if any changes have been made, it contains the new values
        Just in case I missed something
        """
        self.cfg["theme"] = self.appearance_mode.get()
        if self.language_selector == "Español":
            self.cfg["language"] = "es"
        elif self.language_selector == "English":
            self.cfg["language"] = "en"

        if self.enable_terror_easter_egg.get() == 0:
            self.cfg["show_terror"] = False
        else:
            self.cfg["show_terror"] = True

        # TODO: Cache days (should probably not be updated here, but anyway)

    def launch_game(self):
        print("Launching game...")

        try:
            launch_data = self.get_launch_parameters()
        except PermissionError:
            self.update_status("error", self.translations["status_error_invalid_path"])
            return
        self.update_cfg()

        # When using fstrings the dict key must be quoted with '', not ""

        config_manager.save_launch_data(launch_data)
        config_manager.save_ini(self.cfg)
        self.update_status("working", self.translations["status_working_launching"])
        # Make separate threads so that the launcher doesn't block
        if launch_data["version_type"] == "Vanilla":
            # launch_vanilla(launch_data)  OLD
            Thread(target=launch_vanilla, args=(launch_data, self)).start()
        elif launch_data["version_type"] == "Forge":
            # launch_forge(launch_data, self)  OLD
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
        IDLE_STATUS_COLOR = "#2DCCFF"
        WORKING_STATUS_COLOR = "#FCE83A"
        SUCCESS_STATUS_COLOR = "#56F000"
        ERROR_STATUS_COLOR = "#FF3838"

        if code == "idle":
            self.status_indicator.configure(fg_color=IDLE_STATUS_COLOR)
            self.status_indicator.configure(text="IDLE: {}".format(self.translations["status_idle"]))

        elif code == "working":
            self.status_indicator.configure(fg_color=WORKING_STATUS_COLOR)
            self.status_indicator.configure(text=f"WORKING: {message}")

        elif code == "success":
            self.status_indicator.configure(fg_color=SUCCESS_STATUS_COLOR)
            self.status_indicator.configure(text=f"SUCCESS: {message}")

        elif code == "error":
            self.status_indicator.configure(fg_color=ERROR_STATUS_COLOR)
            self.status_indicator.configure(text=f"ERROR: {message}")

        else:  # This should never  (except crash / exception raise), but just in case it will be treated as an error
            self.status_indicator.configure(fg_color=ERROR_STATUS_COLOR)
            self.status_indicator.configure(text=f"ERROR: No status code --> message: {message}")

        self.status_indicator.update()  # Just in case
        return


if __name__ == "__main__":
    app = App()
    app.mainloop()
