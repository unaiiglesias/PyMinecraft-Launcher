import datetime
from PIL import Image
import customtkinter as ctk
from threading import Thread
from tkinter import filedialog
from src.launch_manager import launch_vanilla, launch_forge, launch_modpack, ensure_git
from src.util.get_versions import get_vanilla_versions, get_forge_versions, get_modpack_versions
from src.util.config_manager import Configuration
from src.launch_data_manager import LaunchData
from src.util.translation_manager import Translations
from src.util.utilities import get_default_path, check_if_path_is_valid
from src.util.ctk_scrollable_dropdown import  CTkScrollableDropdown

"""
Default font:
Roboto 13
"""


class App(ctk.CTk):

    VERSION_TYPES = ["Vanilla", "Forge", "Modpack"]

    def __init__(self):
        super().__init__()

        print("--- INITIALIZATION BEGINS ---")

        # load config.ini to dictionary
        self.cfg = Configuration()

        # Translations need to be loaded early so that widgets can assign text variables
        self.translations = Translations(self.cfg["MAIN"]["language"])

        # Set app title and icon according to config.ini
        self.title(self.cfg["MAIN"]["title"])
        self.iconbitmap(self.cfg["MAIN"]["icon"])
        # self.geometry("600x600")  # UNUSED

        # App grid configuration
        self.grid_columnconfigure(2, weight=1)
        self.grid_rowconfigure(6, weight=1)

        # Status indicator --> This needs to be "initialised" early or some widgets that try to modify it during load
        # will raise exceptions
        self.status_indicator = ctk.CTkLabel(self,  corner_radius=5, text_color="black")
        self.status_indicator.grid(row=5, column=0, columnspan=2, sticky="ew", padx=60, pady=(0, 10))
        self.update_status("idle")

        # Top title header
        self.header = ctk.CTkLabel(self, text=self.cfg["MAIN"]["title"], font=("calibri", 24))
        self.header.grid(row=0, column=1, rowspan=1, sticky="n", pady=10, padx=20)

        """ Credentials frame """
        self.credentials_frame = ctk.CTkFrame(self)
        self.credentials_frame.grid(row=1, column=1, sticky="nswe", padx=20, pady=10)
        self.credentials_frame.rowconfigure(2)

        self.input_username_label = ctk.CTkLabel(self.credentials_frame, text=self.translations["username_label"])
        self.input_username_label.grid(row=0, column=0, sticky="w", padx=20, pady=(5, 0))

        self.input_username_field = ctk.CTkEntry(self.credentials_frame, width=300, height=20,
                                                 placeholder_text="Steve")
        self.input_username_field.grid(row=1, sticky="w", padx=20, pady=(5, 10))

        """ Version choice frame """
        self.version_frame = ctk.CTkFrame(self)
        self.version_frame.rowconfigure(3)
        self.version_frame.grid(row=2, column=1, sticky="nswe", padx=20, pady=10)

        self.version_to_launch_label = ctk.CTkLabel(self.version_frame, text=self.translations["versions_label"])
        self.version_to_launch_label.grid(row=0, sticky="w", padx=20, pady=(5, 0))

        self.version_type = ctk.CTkOptionMenu(self.version_frame, values=self.VERSION_TYPES,
                                              command=self.update_versions)  # Values are overwritten by translations
        self.version_type.grid(row=1, sticky="w", padx=20, pady=5)

        self.version_number = ctk.CTkOptionMenu(self.version_frame)
        self.version_number_dropdown = CTkScrollableDropdown(self.version_number, values=[""],
                                                                                     command=self.update_subversions)
        self.version_number.set("")  # Default value will be modified by launch_data or in update_versions

        self.subversion_number = ctk.CTkOptionMenu(self.version_frame, values=[""])
        self.subversion_number_dropdown = CTkScrollableDropdown(self.subversion_number, values=[""])
        self.subversion_number.set("")  # Default value will be modified by launch_data or in update_versions

        self.modpack_name = ctk.CTkOptionMenu(self.version_frame, values=[""], width=300)
        self.modpack_name_dropdown = CTkScrollableDropdown(self.modpack_name)
        self.modpack_name.set("")  # Default value will be modified by launch_data or in update_versions

        self.grid_version("Vanilla")  # Enable version and subversion input, needs to be updated from config.ini

        """ (Launch) Parameters frame """
        self.parameters_frame = ctk.CTkFrame(self)
        self.parameters_frame.grid(row=3, column=1, sticky="nswe", padx=20, pady=10)
        self.parameters_frame.rowconfigure(5)
        self.parameters_frame.columnconfigure(2)

        self.input_ram_label = ctk.CTkLabel(self.parameters_frame, text=self.translations["ram_amount_label"])
        self.input_ram_label.grid(row=0, sticky="w", padx=20, pady=5)

        self.input_ram_field = ctk.CTkSlider(self.parameters_frame, width=300, height=20, from_=1, to=16,
                                             number_of_steps=30, command=self.update_ram_slider)
        self.input_ram_field.grid(row=1, column=0, padx=20, pady=0)

        self.input_ram_value_label = ctk.CTkLabel(self.parameters_frame, text="1 GB")
        self.input_ram_value_label.grid(row=1, column=1, sticky="w", padx=(0, 20), pady=0)

        self.input_installation_path_label = ctk.CTkLabel(self.parameters_frame,
                                                          text=self.translations["installation_path_label"])
        self.input_installation_path_label.grid(row=2, sticky="w", padx=20, pady=5)

        self.input_installation_path = ctk.CTkEntry(self.parameters_frame, width=300, height=20)
        self.input_installation_path.insert(0, get_default_path())  # Set entry to default path
        self.input_installation_path.grid(row=3, column=0, sticky="w", padx=(20, 0), pady=(0, 10))

        self.reset_installation_path_button = ctk.CTkButton(self.parameters_frame, width=120, height=20,
                                                            command=self.reset_installation_path,
                                                            text=self.translations["reset_path_button"])
        self.reset_installation_path_button.grid(row=4, column=0, padx=(40, 0), pady=(0, 10), sticky="w")

        self.browse_installation_path_button = ctk.CTkButton(self.parameters_frame, width=120, height=20,
                                                             command=self.browse_installation_path,
                                                             text=self.translations["browse_path_button"])
        self.browse_installation_path_button.grid(row=4, column=0, padx=(0, 40), pady=(0, 10), sticky="e")

        """ Easter Egg frame """
        self.easter_egg_frame = ctk.CTkFrame(self)
        self.easter_egg_frame.grid(row=1, rowspan=2, padx=15, pady=10, sticky="nswe")

        self.terror_easter_egg_image = ctk.CTkImage(Image.open("assets/terrorist.png"), size=(200, 200))
        self.terror_easter_egg = ctk.CTkLabel(self, width=200, height=200, image=self.terror_easter_egg_image,
                                              text="", fg_color="transparent")
        self.terror_easter_egg.grid(row=1, rowspan=2, column=0, padx=15, pady=10, sticky="nswe")
        self.none_image = ctk.CTkImage(Image.new('RGBA', (200, 200), (255, 0, 0, 0)), size=(200, 200))

        """ Side options frame """
        self.side_frame = ctk.CTkFrame(self)
        self.side_frame.grid(row=3, column=0, sticky="nswe", padx=20, pady=10)
        self.side_frame.rowconfigure(4)

        self.side_options_label = ctk.CTkLabel(self.side_frame, text=self.translations["side_options_label"])
        self.side_options_label.grid(row=0, padx=20, pady=(5, 0))

        self.appearance_mode = ctk.CTkOptionMenu(self.side_frame, values=self.translations["theme_choice"],
                                                 command=self.change_appearance_mode)
        self.appearance_mode.grid(row=1, padx=20, pady=10)
        self.appearance_mode.set(self.cfg["MAIN"]["theme"])  # set loaded
        self.change_appearance_mode(self.cfg["MAIN"]["theme"])  # Change to loaded

        self.language_selector = ctk.CTkOptionMenu(self.side_frame, values=["English", "Español"],
                                                   command=self.change_language)
        self.language_selector.set(self.cfg["MAIN"]["language"])
        self.language_selector.grid(row=2, padx=20, pady=10)

        self.version_label = ctk.CTkLabel(self.side_frame, text=f"ver: {self.cfg["MAIN"]['version']}")
        self.version_label.grid(row=3, sticky="sw", padx=(20, 20), pady=0)
        self.bomb_image = ctk.CTkImage(Image.open("assets/bomb.png"), size=(25, 25))
        self.bomb_image_label = ctk.CTkLabel(self.side_frame, image=self.bomb_image, text="",
                                             fg_color="transparent")
        self.bomb_image_label.grid(row=3, padx=(40, 0), pady=0)
        self.enable_terror_easter_egg = ctk.CTkCheckBox(self.side_frame, text="", width=10, height=10,
                                                        command=self.toggle_terror_easter_egg)
        self.enable_terror_easter_egg.grid(row=3, sticky="e", padx=(0, 20), pady=0)
        if self.cfg["MAIN"]["show_terror"] == 1:
            self.enable_terror_easter_egg.select()
        else:
            self.enable_terror_easter_egg.deselect()
        self.toggle_terror_easter_egg()

        # Launch button
        self.launch_button = ctk.CTkButton(self, text=self.translations["launch_button"], command=self.launch_game)
        self.launch_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=60, pady=20)

        # Load launch data
        self.launch_data = LaunchData() # If there exists launch_data.json, loads it. Otherwise, defaults
        self.input_username_field.insert(0, self.launch_data.username)
        self.input_ram_field.set(self.launch_data.ram / 1024)
        self.update_ram_slider(self.launch_data.ram / 1024)

        # To set the value of the path it first needs to be emptied
        self.input_installation_path.delete(0, ctk.END)
        self.input_installation_path.insert(0, self.launch_data.path)

        self.version_type.set(self.launch_data.version_type)
        self.grid_version(self.launch_data.version_type)
        self.version_number.set(self.launch_data.version)
        self.subversion_number.set(self.launch_data.subversion)
        self.modpack_name.set(self.launch_data.modpack)

        self.update_versions(self.version_type.get())  # TODO: cached day will be saved in self.cfg

        print("--- INITIALIZATION FINALIZED ---")

    def change_appearance_mode(self, new_appearance_mode):
        if new_appearance_mode == "Claro":
            new_appearance_mode = "Light"
        elif new_appearance_mode == "Oscuro":
            new_appearance_mode = "Dark"
        elif new_appearance_mode == "Sistema":
            new_appearance_mode = "System"
        ctk.set_appearance_mode(new_appearance_mode)
        self.cfg["MAIN"]["theme"] = new_appearance_mode
        self.cfg.write_ini()

    def toggle_terror_easter_egg(self):
        """
        Read the current value of enable_terror_easter_egg and show or hide the image accordingly
        """

        if self.enable_terror_easter_egg.get() == 0:
            # Disable
            self.terror_easter_egg.configure(image=self.none_image)
            self.terror_easter_egg.image = self.none_image
        else:
            # Enable
            self.terror_easter_egg.configure(image=self.terror_easter_egg_image)
            self.terror_easter_egg.image = self.terror_easter_egg_image

        self.cfg["MAIN"]["show_terror"] = self.enable_terror_easter_egg.get()  # 0 or 1
        self.cfg.write_ini()

    def get_versions(self):
        """
        Read version type to get from version type selector and return version list
         - Vanilla: Simple version number list
         - Forge: dictionary {version number: [subversion list]}
         - Modpack: Simple modpack name list
        """

        version_type_to_get = self.version_type.get()

        versions = []  # Just so PyCharm shuts up
        if version_type_to_get == "Vanilla":
            versions = get_vanilla_versions(".", self)
        elif version_type_to_get == "Forge":
            versions = get_forge_versions(".", self)
        elif version_type_to_get == "Modpack":
            versions = get_modpack_versions(".", self)

        self.update_status("idle")  # Return the launcher status to idle after the versions have been loaded

        return versions

    def update_versions(self, choice):
        # choice must be accepted as a parameter or the function will raise an error

        """
        This function is used by the version_type OptionMenu to update the version and subversion numbers
        """

        print("UPDATING VERSIONS")

        # Choice will always be in ("Vanilla", "Forge", "Modpack)

        # Get version list (numbers) according to selected type

        version_list = self.get_versions()
        today = datetime.datetime.now().day  # get today's number of the month
        self.grid_version(choice)  # Show necessary fields

        if choice == "Vanilla":
            """
            version_list will be a list of versions
            """

            # Set the parent version field values
            self.version_number_dropdown.configure(values=version_list)

            # Update cache date
            self.cfg["MAIN"]["cache_day_vanilla"] = today

            # If no version chosen, choose one
            if not self.version_number.get():
                self.version_number.set(version_list[0])

        elif choice == "Forge":
            """
            version_list will be a dictionary where {parent_version : forge_subversions}
            """

            # Set the parent version field values
            self.version_number_dropdown.configure(values=list(version_list.keys()))

            # Update the subversion field values
            self.update_subversions(self.version_number.get())

            # Update cache date
            self.cfg["MAIN"]["cache_day_forge"] = today

            if not self.version_number.get():
                self.version_number.set(version_list.keys()[0])
                self.subversion_number.set(version_list[version_list.keys()[0]])
            elif not self.subversion_number.get():
                self.subversion_number.set("latest")

        elif choice == "Modpack":
            """
            version_list will be a list of modpack names
            """
            self.modpack_name_dropdown.configure(values=version_list)
            # TODO: Cache date should be updated here

            if not self.modpack_name.get():
                self.modpack_name.set(version_list[0])

        return

    def grid_version(self, choice):
        """
        choice in ("Vanilla", "Forge", "Modpack")
        Show/hide the necessary input menus depending on the choice

        Auxiliary method
        """

        print("Re-griding")

        if choice == "Vanilla":
            self.version_number.grid(row=2, column=0, sticky="w", padx=20, pady=10)
            self.subversion_number.grid(row=2, column=1, sticky="w", padx=20, pady=10)
            self.modpack_name.grid_forget()

            self.subversion_number.configure(state="disabled")

        elif choice == "Forge":
            self.version_number.grid(row=2, column=0, sticky="w", padx=20, pady=10)
            self.subversion_number.grid(row=2, column=1, sticky="w", padx=20, pady=10)
            self.modpack_name.grid_forget()

            self.subversion_number.configure(state="normal")

        elif choice == "Modpack":
            self.version_number.grid_forget()
            self.subversion_number.grid_forget()
            self.modpack_name.grid(row=2, columnspan=2, sticky="w", padx=20, pady=10)

    def update_subversions(self, parent_version):
        """
        This function is used to refresh the subversion numbers.
        choice = parent version number | ex: "1.12.2"

        It is only necessary for forge, and will be called by version number selector
        """

        # This overwrites CTkScrollableDropdown's default command, so we need to do this manually
        self.version_number.set(parent_version)

        if self.version_type.get() == "Vanilla":
            return

        print("UPDATING SUBVERSIONS")
        version_list = self.get_versions()

        subversion_list = version_list[parent_version]  # In this case choice = self.version_number.get()
        self.subversion_number_dropdown.configure(values=subversion_list)
        # Every time the version changes, we default to lastest to prevent the prevoius subversion from being kept
        self.subversion_number.set("latest")

    def update_ram_slider(self, choice):
        self.input_ram_value_label.configure(text=f"{choice} GB")

    def reset_installation_path(self):
        default_path = get_default_path()
        self.input_installation_path.delete(0, ctk.END)  # Clean the entry
        self.input_installation_path.insert(0, default_path)  # Set the entry to the default path
        print("Installation path reseted")
        return

    def browse_installation_path(self):
        path = filedialog.askdirectory()

        if not path:  # If no path was chosen (empty path --> ""), do nothing
            return

        self.input_installation_path.delete(0, ctk.END)  # Delete current path
        self.input_installation_path.insert(0, path)  # add read path

    def change_language(self, choice):
        """
        Updates every button, label, entry's text translation to choice language

        Args:
            choice: "Español" or "English"
        """

        # choice in (English, Español)
        self.translations.load_translations(choice)

        self.input_username_label.configure(text=self.translations["username_label"])
        self.version_to_launch_label.configure(text=self.translations["versions_label"])
        self.input_ram_label.configure(text=self.translations["ram_amount_label"])
        self.input_installation_path_label.configure(text=self.translations["installation_path_label"])
        self.reset_installation_path_button.configure(text=self.translations["reset_path_button"])
        self.browse_installation_path_button.configure(text=self.translations["browse_path_button"])
        self.appearance_mode.configure(values=self.translations["theme_choice"])
        self.side_options_label.configure(text=self.translations["side_options_label"])
        self.launch_button.configure(text=self.translations["launch_button"])
        self.update_status("idle")  # So that the status bar text updates
        self.cfg["MAIN"]["language"] = choice
        self.cfg.write_ini()
        return

    def get_launch_parameters(self):
        """
        Collect all the info neccessary to launch the game from the GUI
        Returns:
            updates self.launch_data according to GUI
        """

        # It makes no sense for the username to be ""
        username = self.input_username_field.get()
        if not username:
            print("ERROR: Empty username selected")
            raise TypeError
        self.launch_data.username = username

        # Get version
        self.launch_data.version_type = self.version_type.get()
        self.launch_data.version = self.version_number.get()
        self.launch_data.subversion = self.subversion_number.get()
        self.launch_data.modpack = self.modpack_name.get()

        # Turn RAM value into an integer
        ram = int(self.input_ram_field.get() * 1024)
        print(f"DEBUG: Launching with ram {ram}") # TODO: Check if this is correct (shouldn't it be 512?)
        self.launch_data.ram = ram

        # This part is only "triggered" if a path is neither provided via GUI nor loaded from the .json file
        # (Shouldn't happen, but just in case)
        inserted_path = self.input_installation_path.get()
        if inserted_path == "":
            inserted_path = get_default_path()
            self.reset_installation_path()
        self.launch_data.path = inserted_path

        # Check that path is valid
        if not check_if_path_is_valid(self.launch_data.path):
            print("ERROR: Invalid Path selected")
            raise PermissionError # This will be caught by launch_game, who will handle it

        # Get premium status
        self.launch_data.premium = False # TODO: Premium functionality, False for now

        return

    def launch_game(self):
        print("Launching game...")

        # Get launch parameters and check if the launch path is valid (we have permission)
        try:
            self.get_launch_parameters()
        except (PermissionError, FileNotFoundError):
            self.update_status("error", self.translations["status_error_invalid_path"])
            return
        except TypeError:
            self.update_status("error", self.translations["status_error_invalid_username"])
            return

        self.launch_data.save_launch_data() # write launch_data.json

        self.update_status("working", self.translations["status_working_launching"])

        # Make separate threads so that the launcher doesn't block
        self.launch_button.configure(state="disabled")
        # I'll enable it in the launch function after the installation is done

        if self.launch_data.version_type == "Vanilla":
            # launch_vanilla(launch_data)  OLD
            Thread(target=launch_vanilla, args=(self.launch_data, self)).start()
        elif self.launch_data.version_type == "Forge":
            # launch_forge(launch_data, self)  OLD
            Thread(target=launch_forge, args=(self.launch_data, self)).start()
        elif self.launch_data.version_type == "Modpack":
            if not ensure_git(self, self.launch_data):
                self.update_status("error", self.translations["status_error_git_not_installed"])
                print("Aborting modpack launch, git not installed")
                return
            launch_modpack(self.launch_data, self)

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
