from PIL import Image
import customtkinter as ctk
from tkinter import filedialog
from src.launch_managers.generic import launch
from src.util.get_versions import get_vanilla_versions, get_forge_versions, get_modpack_versions
from src.app_utils.config_manager import Configuration
from src.app_utils.launch_data_manager import LaunchData
from src.app_utils.translation_manager import Translations
from src.util.utilities import get_default_path, check_if_path_is_valid
from src.custom_toplevels.ctk_scrollable_dropdown import  CTkScrollableDropdown

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
        self.header.grid(row=0, column=1, sticky="n", pady=10, padx=20)

        # Side menu button
        self.toggle_side_menu_button = ctk.CTkButton(self, text="☰", command=self.toggle_side_menu,
                                                     fg_color="transparent", width=30, height=30)
        self.toggle_side_menu_button.grid(row=0, column=0, sticky="w", padx=(20, 0), pady=10)

        """ Credentials frame """
        self.credentials_frame = ctk.CTkFrame(self)
        self.credentials_frame.grid(row=1, column=1, sticky="nswe", padx=20, pady=10)
        self.credentials_frame.rowconfigure(2)

        self.input_username_label = ctk.CTkLabel(self.credentials_frame, text=self.translations["username_label"])
        self.input_username_label.grid(row=0, column=0, sticky="w", padx=20, pady=(5, 0))

        self.input_username_field = ctk.CTkEntry(self.credentials_frame, width=300, height=20,
                                                 placeholder_text="Steve")
        self.input_username_field.grid(row=1, sticky="w", padx=20, pady=(5, 10))

        """ Version choice frame """ # This section also contains 3 "subframes" each per version type selector
        self.version_frame = ctk.CTkFrame(self)
        self.version_frame.rowconfigure(3)
        self.version_frame.columnconfigure(2)
        self.version_frame.grid(row=2, column=1, sticky="nswe", padx=20, pady=10)

        self.version_to_launch_label = ctk.CTkLabel(self.version_frame, text=self.translations["versions_label"])
        self.version_to_launch_label.grid(row=0, sticky="w", padx=20, pady=(5, 0))

        self.version_type = ctk.CTkOptionMenu(self.version_frame, values=self.VERSION_TYPES,
                                              command=self.update_versions)  # Values are overwritten by translations
        self.version_type.grid(row=1, sticky="w", padx=20, pady=5)

        self.vanilla_frame = ctk.CTkFrame(self.version_frame, fg_color="transparent")
        self.vanilla_frame.rowconfigure(1)
        self.vanilla_version = ctk.CTkOptionMenu(self.vanilla_frame, values=[""], width = 300)
        self.vanilla_version_dropdown = CTkScrollableDropdown(self.vanilla_version,
                                                              values=[""])
        self.vanilla_version.grid(columnspan=2, sticky="w", padx=(20, 0), pady=10)

        self.forge_frame = ctk.CTkFrame(self.version_frame, fg_color="transparent")
        self.forge_frame.rowconfigure(1)
        self.forge_version = ctk.CTkOptionMenu(self.forge_frame, values=[""])
        self.forge_version_dropdown = CTkScrollableDropdown(self.forge_version,
                                                            values=[""],
                                                            command=self.update_subversions)
        self.forge_version.grid(row = 0, column = 0, sticky = "w", padx = 20, pady = 10)
        self.forge_subversion = ctk.CTkOptionMenu(self.forge_frame, values=[""])
        self.forge_subversion_dropdown = CTkScrollableDropdown(self.forge_subversion,
                                                               values=[""])
        self.forge_subversion.grid(row = 0, column = 1, sticky = "w", padx = 20, pady = 10)

        self.modpack_frame =  ctk.CTkFrame(self.version_frame, fg_color="transparent")
        self.modpack_frame.rowconfigure(1)
        self.modpack_name = ctk.CTkOptionMenu(self.modpack_frame, values=[""]
                                              , width = 300)
        self.modpack_name_dropdown = CTkScrollableDropdown(self.modpack_name,
                                                              values=[""])
        self.modpack_name.grid(columnspan = 2, sticky = "w", padx = 20, pady = 10)

        """ (Launch) Parameters frame """
        self.parameters_frame = ctk.CTkFrame(self)
        self.parameters_frame.grid(row=3, column=1, sticky="nswe", padx=20, pady=10)
        self.parameters_frame.rowconfigure(5)

        self.input_ram_label = ctk.CTkLabel(self.parameters_frame, text=self.translations["ram_amount_label"])
        self.input_ram_label.grid(row=0, sticky="w", padx=20, pady=5)

        self.input_ram_field = ctk.CTkSlider(self.parameters_frame, width=250, height=20, from_=1, to=16,
                                             number_of_steps=30, command=self.update_ram_slider)
        self.input_ram_field.grid(row=1, padx=(20, 10), pady=0, sticky="w")

        self.input_ram_value_label = ctk.CTkLabel(self.parameters_frame, text="1 GB", width=50)
        self.input_ram_value_label.grid(row=1, sticky="e", padx=(10, 20), pady=0)

        self.input_installation_path_label = ctk.CTkLabel(self.parameters_frame,
                                                          text=self.translations["installation_path_label"])
        self.input_installation_path_label.grid(row=2, sticky="w", padx=20, pady=5)

        self.input_installation_path = ctk.CTkEntry(self.parameters_frame, width=300, height=20)
        self.input_installation_path.insert(0, get_default_path())  # Set entry to default path
        self.input_installation_path.grid(row=3, sticky="w", padx=20, pady=(0, 10))

        self.reset_installation_path_button = ctk.CTkButton(self.parameters_frame, width=120, height=20,
                                                            command=self.reset_installation_path,
                                                            text=self.translations["reset_path_button"])
        self.reset_installation_path_button.grid(row=4, padx=(30, 10), pady=(0, 10), sticky="w")

        self.browse_installation_path_button = ctk.CTkButton(self.parameters_frame, width=120, height=20,
                                                             command=self.browse_installation_path,
                                                             text=self.translations["browse_path_button"])
        self.browse_installation_path_button.grid(row=4, padx=(10, 30), pady=(0, 10), sticky="e")

        """ Easter Egg """
        self.terror_easter_egg_image = ctk.CTkImage(Image.open("assets/terrorist.png"), size=(200, 200))
        self.terror_easter_egg = ctk.CTkLabel(self, width=200, height=200, image=self.terror_easter_egg_image,
                                              text="", fg_color="transparent")
        self.terror_easter_egg.grid(row=1, rowspan=2, column=0, padx=15, pady=10, sticky="nswe")
        self.none_image = ctk.CTkImage(Image.new('RGBA', (200, 200), (255, 0, 0, 0)), size=(200, 200))

        """ Side options frame """
        self.side_frame = ctk.CTkFrame(self)
        self.side_frame.grid(row=3, column=0, sticky="nswe", padx=20, pady=10)
        self.side_frame.rowconfigure(4)

        light_theme_image = ctk.CTkImage(Image.open("assets/sun.png"), size=(25, 25))
        self.light_theme_selector = ctk.CTkButton(self.side_frame, command=lambda : self.change_appearance_mode("Light"),
                                                  text="", image=light_theme_image, width=25, height=25, fg_color="transparent")
        self.light_theme_selector.grid(row=0, padx=25, pady=(10, 5), sticky="w")

        dark_theme_image = ctk.CTkImage(Image.open("assets/moon.png"), size=(25, 25))
        self.dark_theme_selector = ctk.CTkButton(self.side_frame, command=lambda : self.change_appearance_mode("Dark"),
                                                 text="", image=dark_theme_image, width=25, height=25, fg_color="transparent")
        self.dark_theme_selector.grid(row=0, padx=25, pady=(10, 5), sticky="e")

        self.on_launch_selector = ctk.CTkOptionMenu(self.side_frame, values=[self.translations["on_launch_nothing"],
                                                                             self.translations["on_launch_success_window"],
                                                                             self.translations["on_launch_logger"]],
                                                    command=self.change_on_launch_behaviour)
        self.on_launch_selector.grid(row=1, padx=20, pady=5)

        english_flag_image = ctk.CTkImage(Image.open("assets/english_flag.png"), size=(40, 25))
        self.english_language_selector = ctk.CTkButton(self.side_frame, command=lambda: self.change_language("en"),
                                                       image=english_flag_image, text="", fg_color="transparent",
                                                       width=40, height=25)
        self.english_language_selector.grid(row=2, padx=20, pady=10, sticky="w")

        spanish_flag_image = ctk.CTkImage(Image.open("assets/spanish_flag.png"), size=(40, 25))
        self.spanish_language_selector = ctk.CTkButton(self.side_frame, command = lambda : self.change_language("es"),
                                                       image=spanish_flag_image, text="", fg_color="transparent",
                                                       width=40, height=25)
        self.spanish_language_selector.grid(row=2, padx=20, pady=10, sticky="e")

        self.version_label = ctk.CTkLabel(self.side_frame, text=f"ver: {self.cfg["MAIN"]['version']}")
        self.version_label.grid(row=3, sticky="sw", padx=(20, 20), pady=0)
        self.bomb_image = ctk.CTkImage(Image.open("assets/bomb.png"), size=(25, 25))
        self.bomb_image_label = ctk.CTkLabel(self.side_frame, image=self.bomb_image, text="",
                                             fg_color="transparent")
        self.bomb_image_label.grid(row=3, padx=(40, 0), pady=0)
        self.enable_terror_easter_egg = ctk.CTkCheckBox(self.side_frame, text="", width=10, height=10,
                                                        command=self.toggle_terror_easter_egg)
        self.enable_terror_easter_egg.grid(row=3 , sticky="e", padx=(0, 20), pady=0)
        if self.cfg["MAIN"]["show_terror"] == 1:
            self.enable_terror_easter_egg.select()
        else:
            self.enable_terror_easter_egg.deselect()
        self.toggle_terror_easter_egg(write=False)

        # Launch button
        self.launch_button = ctk.CTkButton(self, text=self.translations["launch_button"], command=self.launch_game)
        self.launch_button.grid(row=4, column=0, columnspan=2, sticky="ew", padx=60, pady=10)

        # Now that everything is initialized:
        self.change_appearance_mode(self.cfg["MAIN"]["theme"], write=False)
        if not self.cfg["MAIN"]["show_side_menu"]:
            # The toggle function flips it, so we pre-flip it to get it back to where we want it to
            self.cfg["MAIN"]["show_side_menu"] = not self.cfg["MAIN"]["show_side_menu"]
            self.toggle_side_menu(write=False)

        # Load launch data
        self.launch_data = LaunchData() # If there exists launch_data.json, loads it. Otherwise, defaults
        self.input_username_field.insert(0, self.launch_data.username)
        self.input_ram_field.set(self.launch_data.ram / 1024)
        self.update_ram_slider(self.launch_data.ram / 1024)

        # To set the value of the path it first needs to be emptied
        self.input_installation_path.delete(0, ctk.END)
        self.input_installation_path.insert(0, self.launch_data.path)

        self.version_type.set(self.launch_data.version_type)
        if self.launch_data.version_type == "Vanilla":
            self.vanilla_version.set(self.launch_data.version)
        elif self.launch_data.version_type == "Forge":
            self.forge_version.set(self.launch_data.version)
            self.forge_subversion.set(self.launch_data.subversion)
        elif self.launch_data.version_type == "Modpack":
            self.modpack_name.set(self.launch_data.modpack)
        self.update_versions(self.launch_data.version_type)

        print("--- INITIALIZATION FINALIZED ---")

    def toggle_side_menu(self, write=True):

        # On button press, flip it
        self.cfg["MAIN"]["show_side_menu"] = not self.cfg["MAIN"]["show_side_menu"]
        if write:
            self.cfg.write_ini()

        # hide
        if not self.cfg["MAIN"]["show_side_menu"]:
            self.side_frame.grid_forget()
            self.terror_easter_egg.grid_forget()
            self.toggle_side_menu_button.configure(fg_color="#1F6AA5")

            self.header.grid(column=0)
            self.credentials_frame.grid(column=0)
            self.version_frame.grid(column=0)
            self.parameters_frame.grid(column=0)

            self.launch_button.grid(column=0, columnspan=1, padx=20)
            self.status_indicator.grid(column=0, columnspan=1, padx=20)

            self.grid_columnconfigure(1, weight=1)

        # display
        else:
            self.side_frame.grid(row=3, column=0, sticky="nswe", padx=20, pady=10)
            self.terror_easter_egg.grid(row=1, rowspan=2, column=0, padx=15, pady=10, sticky="nswe")
            self.toggle_side_menu_button.configure(fg_color="transparent")

            self.header.grid(column=1)
            self.credentials_frame.grid(column=1)
            self.version_frame.grid(column=1)
            self.parameters_frame.grid(column=1)

            self.launch_button.grid(column=0, columnspan=2, padx=60)
            self.status_indicator.grid(column=0, columnspan=2, padx=60)

            self.grid_columnconfigure(2, weight=1)

    def change_appearance_mode(self, new_appearance_mode, write=True):
        self.light_theme_selector.configure(fg_color="transparent")
        self.dark_theme_selector.configure(fg_color="transparent")
        if new_appearance_mode == "Light":
            self.light_theme_selector.configure(fg_color="gray")
        elif new_appearance_mode == "Dark":
            self.dark_theme_selector.configure(fg_color="gray")

        ctk.set_appearance_mode(new_appearance_mode)
        self.cfg["MAIN"]["theme"] = new_appearance_mode
        if write:
            self.cfg.write_ini()

    def change_on_launch_behaviour(self, new_behaviour):
        if new_behaviour == self.translations["on_launch_nothing"]:
            self.cfg["MAIN"]["on_launch"] = "nothing"
        elif new_behaviour == self.translations["on_launch_success_window"]:
            self.cfg["MAIN"]["on_launch"] = "success_window"
        elif new_behaviour == self.translations["on_launch_logger"]:
            self.cfg["MAIN"]["on_launch"] = "logger"
        self.cfg.write_ini()

    def toggle_terror_easter_egg(self, write=True):
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
        if write:
            self.cfg.write_ini()

    def update_versions(self, choice):
        # choice must be accepted as a parameter or the function will raise an error
        """
        Action listener for version type selector
        choice in ("Vanilla", "Forge", "Modpack")

        Show / Hide frames according to choice and update their versions
        """

        print(f"Updating version frame for version type: {choice}")

        self.vanilla_frame.grid_forget()
        self.forge_frame.grid_forget()
        self.modpack_frame.grid_forget()

        # Get version list (numbers) according to selected type

        if choice == "Vanilla":
            # Grid (show) the vanilla frame
            self.vanilla_frame.grid(row=2, columnspan=2, sticky="nswe", padx=0, pady=5)

            #version_list will be a list of versions
            version_list = get_vanilla_versions(".", self)

            # Set the parent version field values
            self.vanilla_version_dropdown.configure(values=version_list)

            # If no version chosen, choose one
            if not self.vanilla_version.get():
                self.vanilla_version.set(version_list[0])

        elif choice == "Forge":
            # Grid (show) the forge frame
            self.forge_frame.grid(row=2, columnspan=2, sticky="nswe", padx=0, pady=5)

            # version_list will be a dictionary where {parent_version : forge_subversions}
            version_list = get_forge_versions(".", self)

            # Set the version field values
            self.forge_version_dropdown.configure(values=list(version_list.keys()))

            # Keep current selection (set said version's subversions
            # Only if version selected and that version has forge
            if self.forge_version.get() and self.forge_version.get() in version_list:
                self.forge_subversion_dropdown.configure(values=version_list[self.forge_version.get()])

            else: # default
                print("DEBUG: Bad or None forge version, going back to default")
                default_forge_version = list(version_list.keys())[0] # First one in dict (latest)
                self.forge_version.set(default_forge_version)
                self.forge_subversion_dropdown.configure(values=version_list[default_forge_version])
                self.forge_subversion.set("latest") # By default, we'll always use latest


        elif choice == "Modpack":
            # Grid (show) the modpack frame
            self.modpack_frame.grid(row=2, columnspan=2, sticky="nswe", padx=0, pady=5)

            # version_list will be a list of modpack names
            version_list = get_modpack_versions(".", self)

            self.modpack_name_dropdown.configure(values=version_list)
            # TODO: Cache date should be updated here

            if not self.modpack_name.get():
                self.modpack_name.set(version_list[0])

        self.update_status("idle")  # Return the launcher status to idle after the versions have been loaded

        return

    def update_subversions(self, parent_version):
        """
        Forge version selector's action listener
        This function is used to refresh the subversion numbers.
        choice = parent version number | ex: "1.12.2"

        It is only necessary for forge, and will be called by version number selector
        """

        print(f"Updating forge subversions for {parent_version}")
        self.forge_version.set(parent_version)
        version_list = get_forge_versions(".", self)

        subversion_list = version_list[parent_version]  # In this case choice = self.version_number.get()
        self.forge_subversion_dropdown.configure(values=subversion_list)
        # Every time the version changes, we default to lastest to prevent the previous subversion from being kept
        self.forge_subversion.set("latest")

        self.update_status("idle")  # Return the launcher status to idle after the versions have been loaded

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
            choice: "es" : Español or "en" : English
        """

        # choice in ("en", "es")
        self.translations.load_translations(choice)

        self.english_language_selector.configure(fg_color="transparent")
        self.spanish_language_selector.configure(fg_color="transparent")
        if choice == "en":
            self.english_language_selector.configure(fg_color="gray")
        elif choice == "es":
            self.spanish_language_selector.configure(fg_color="gray")

        self.input_username_label.configure(text=self.translations["username_label"])
        self.version_to_launch_label.configure(text=self.translations["versions_label"])
        self.input_ram_label.configure(text=self.translations["ram_amount_label"])
        self.input_installation_path_label.configure(text=self.translations["installation_path_label"])
        self.reset_installation_path_button.configure(text=self.translations["reset_path_button"])
        self.browse_installation_path_button.configure(text=self.translations["browse_path_button"])

        self.on_launch_selector.configure(values=[self.translations["on_launch_nothing"],
                                                 self.translations["on_launch_success_window"],
                                                 self.translations["on_launch_logger"]])
        if self.cfg["MAIN"]["on_launch"] == "nothing":
            self.on_launch_selector.set(self.translations["on_launch_nothing"])
        if self.cfg["MAIN"]["on_launch"] == "success_window":
            self.on_launch_selector.set(self.translations["on_launch_success_window"])
        if self.cfg["MAIN"]["on_launch"] == "logger":
            self.on_launch_selector.set(self.translations["on_launch_logger"])

        self.launch_button.configure(text=self.translations["launch_button"])
        self.update_status("idle")  # So that the status bar text updates
        self.cfg["MAIN"]["language"] = choice
        self.cfg.write_ini()
        return

    def _gather_launch_parameters(self):
        """
        Collect all the info necessary to launch the game from the GUI
        updates self.launch_data according to GUI
        Raises:
            TypeError: Empty username
            PermissionError: Invalid path
        """

        # It makes no sense for the username to be ""
        username = self.input_username_field.get()
        if not username:
            print("ERROR: Empty username selected")
            raise TypeError
        self.launch_data.username = username

        # Get version
        version_type = self.version_type.get()
        self.launch_data.version_type = version_type
        if version_type == "Vanilla":
            self.launch_data.version = self.vanilla_version.get()
        elif version_type == "Forge":
            self.launch_data.version = self.forge_version.get()
            self.launch_data.subversion = self.forge_subversion.get()
        elif version_type == "Modpack":
            self.launch_data.modpack = self.modpack_name.get()

        # Turn RAM value into an integer
        ram = int(self.input_ram_field.get() * 1024)
        print(f"DEBUG: Launching with ram {ram}")
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
            self._gather_launch_parameters()
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

        launch(self.launch_data, self, self.launch_data.version_type)

        self.launch_button.configure(state="normal")
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
