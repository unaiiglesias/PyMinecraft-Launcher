import customtkinter as ctk


def define_window():

    class App(ctk.CTk):
        def __init__(self):
            super().__init__()

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

            self.input_username_label = ctk.CTkLabel(self.credentials_frame, text="Username")
            self.input_username_label.grid(padx=20, pady=(10, 0), sticky="w")

            self.input_username_field = ctk.CTkEntry(self.credentials_frame, width=200, height=20,
                                                     placeholder_text="Username")
            self.input_username_field.grid(padx=20, pady=10, sticky="ew")

            self.input_password_label = ctk.CTkLabel(self.credentials_frame, text="Password (Premium only)")
            self.input_password_label.grid(padx=20, pady=0, stick="w")

            self.input_password_field = ctk.CTkEntry(self.credentials_frame, width=200, height=20,
                                                     placeholder_text="Password", show="*")
            self.input_password_field.grid(padx=20, pady=10, sticky="ew")

            # Version choice frame
            self.version_frame = ctk.CTkFrame(self)
            self.version_frame.rowconfigure(3)
            self.version_frame.grid(row=2, column=1, padx=20, pady=10, sticky="nswe")

            self.version_label = ctk.CTkLabel(self.version_frame, text="Version to launch")
            self.version_label.grid(row=0, padx=20, pady=0, sticky="ew")

            self.version_type = ctk.CTkOptionMenu(self.version_frame, values=["Vanilla", "Forge", "Modpack"])
            self.version_type.grid(row=1, padx=10, pady=10, sticky="ew")

            self.version_number = ctk.CTkOptionMenu(self.version_frame, values=self.get_versions())
            self.version_number.grid(row=2, padx=10, pady=10, sticky="ew")

            # (Launch) Parameters frame
            self.parameters_frame = ctk.CTkFrame(self)
            self.parameters_frame.rowconfigure(4)
            self.parameters_frame.grid(row=3, column=1, padx=20, pady=10, sticky="nswe")

            self.input_ram_label = ctk.CTkLabel(self.parameters_frame, text="RAM amount")
            self.input_ram_label.grid(padx=20, pady=0, sticky="ew", columnspan=2, row=0)

            self.input_ram_field = ctk.CTkEntry(self.parameters_frame, width=60, height=20, placeholder_text="RAM")
            self.input_ram_field.grid(padx=(20, 0), pady=(0, 10), sticky="ew", column=0, columnspan=1, row=1)

            self.input_ram_unit = ctk.CTkLabel(self.parameters_frame, text="Mb")
            self.input_ram_unit.grid(column=1, columnspan=1, padx=5, row=1, sticky="w")

            self.path_to_jvm_label = ctk.CTkLabel(self.parameters_frame, text="Path to JVM")
            self.path_to_jvm_label.grid(row=2, columnspan=2)

            # Temporary, needs to be improved
            self.path_to_jvm = ctk.CTkEntry(self.parameters_frame, width=200, height=20,
                                            placeholder_text=self.get_path_to_jvm())
            self.path_to_jvm.grid(row=3, columnspan=2, padx=20, pady=10, sticky="ew")

            # Side options frame
            self.side_frame = ctk.CTkFrame(self)
            self.side_frame.grid(row=3, column=0, padx=20, pady=10, sticky="nswe")

            self.appearance_mode_label = ctk.CTkLabel(self.side_frame, text="Theme mode")

            self.appearance_mode = ctk.CTkOptionMenu(self.side_frame, values=["Light", "Dark", "System"],
                                                     command=self.change_appearance_mode)
            self.appearance_mode.grid(column=0, padx=20, pady=10)

            # Launch button
            self.launch_button = ctk.CTkButton(self, text="LAUNCH", command=launch_game)
            self.launch_button.grid(row=4, column=0, padx=60, pady=20, sticky="ew", columnspan=2)

        def change_appearance_mode(self, new_appearance_mode):
            ctk.set_appearance_mode(new_appearance_mode)

        def get_versions(self):
            versions = []
            # WIP, placeholder
            versions = ["1.18.2", "1.16.5", "1.12.2", "1.8.9"]
            return versions # Should return a list with the fetched versions WIP

        def get_path_to_jvm(self):
            path_to_jvm = ""
            # WIP placeholder
            path_to_jvm = "C://some_path"
            return path_to_jvm

        def launch_game(self):
            print("Launching game...")

    return App()


def launch_game():
    print("Game launched")
    pass


def main():
    app = define_window()
    app.mainloop()


if __name__ == "__main__":
    main()
