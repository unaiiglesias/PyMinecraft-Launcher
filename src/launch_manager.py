from portablemc.standard import Context, Version
from portablemc.forge import ForgeVersion
from pathlib import Path


def launch_vanilla(launch_parameters, app):
    main_dir = Path(launch_parameters["path"])
    work_dir = Path(main_dir)
    version_id = launch_parameters["version"]
    ram_amount = launch_parameters["ram"]
    username = launch_parameters["username"]

    ctx = Context(main_dir, work_dir)
    version = Version(version_id, context=ctx)

    print("Downloading and installing Minecraft version")
    app.update_status("working", app.translations["status_working_downloading_version"])
    version.set_auth_offline(username, None)  # (username, uuid) no uuid so pass None
    env = version.install()

    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])
    env.run()


def launch_forge(launch_parameters, app):
    main_dir = Path(launch_parameters["path"])
    work_dir = Path(main_dir)
    version_id = launch_parameters["version"]
    subversion_id = launch_parameters["subversion"]
    ram_amount = launch_parameters["ram"]
    username = launch_parameters["username"]

    ctx = Context(main_dir, work_dir)

    full_version_id = f"{version_id}-{subversion_id}"
    print(f"Launching : {full_version_id}")

    print("Downloading and installing Forge version")
    app.update_status("working", app.translations["status_working_downloading_forge_version"])
    version = ForgeVersion(full_version_id, context=ctx)

    version.set_auth_offline(username, None)  # (username, uuid) no uuid so pass None

    env = version.install()

    env.username = username
    env.resolution = (1080, 720)
    env.jvm_args.append(f"-Xmx{ram_amount}M")

    print("Launching Minecraft")
    app.update_status("success", app.translations["status_success"])
    env.run()


if __name__ == "__main__":
    launch_forge({"path": "C:\\Users\\unai\\Desktop\\PMC-main_dir", "version": "1.16.3", "subversion": "34.1.42",
                  "ram": 4048, "username": "Xtrike"})

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