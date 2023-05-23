import customtkinter as ctk
from PIL import Image


def define_window():
    class App(ctk.CTk):
        def __init__(self):
            super().__init__()
            self.refresh_icon = ctk.CTkImage(light_image=Image.open("./../assets/refresh.png"), size=(20, 20))
            self.check_icon = ctk.CTkImage(light_image=Image.open("./../assets/check.png"), size=(20, 20))
            # light_image = dark_image

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

            self.installation_path_label = ctk.CTkLabel(self.parameters_frame, text="Installation path")
            self.installation_path_label.grid(row=2, columnspan=2, padx=20, sticky="w")

            self.installation_path = ctk.CTkEntry(self.parameters_frame, width=200, height=20,
                                            placeholder_text=self.get_installation_path())
            self.installation_path.grid(row=3, columnspan=2, padx=20, pady=10, sticky="w")

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

            self.latest_version_label = ctk.CTkLabel(self.side_frame, text=self.get_latest_version())
            self.latest_version_label.grid(row=2, padx=(0, 20), pady=0, sticky="e")

            # Launch button
            self.launch_button = ctk.CTkButton(self, text="LAUNCH", command=self.launch_game)
            self.launch_button.grid(row=4, column=0, padx=60, pady=20, sticky="ew", columnspan=2)

        def change_appearance_mode(self, new_appearance_mode):
            ctk.set_appearance_mode(new_appearance_mode)

        def get_versions(self):
            # WIP, placeholder
            versions = ["1.18.2", "1.16.5", "1.12.2", "1.8.9"]
            return versions  # Should return a list with the fetched versions WIP

        def log_in(self):
            print("Logging in...")
            if self.log_in_button._image == self.refresh_icon:
                self.log_in_button.configure(image=self.check_icon)
            else:
                self.log_in_button.configure(image=self.refresh_icon)
            return

        def get_installation_path(self):
            # WIP placeholder: default minecraft path
            installation_path = "C:/Users/unai/AppData/Roaming/.minecraft"
            return installation_path

        def launch_game(self):
            print("Launching game...")
            return

        def get_launcher_version(self):
            # WIP placeholder
            version = "ver. 0.1"
            return version

        def get_latest_version(self):
            # WIP placeholder
            latest = "latest: 0.1"
            return latest

        def update_launcher(self):
            print("Updating launcher")
            return

    return App()


def main():
    app = define_window()
    app.mainloop()


if __name__ == "__main__":
    main()
