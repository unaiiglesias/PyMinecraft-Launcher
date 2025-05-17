from threading import Thread
from src.app_utils.launch_data_manager import LaunchData
from src.launch_managers.vanilla_launcher import build_vanilla_env
from src.launch_managers.forge_launcher import build_forge_env
from src.launch_managers.modpack_launcher import build_modpack_env
from src.custom_toplevels.success_window import SuccessWindow
from portablemc.standard import Environment


def launch(launch_data : LaunchData, app, mode : str):
    """
    Entry point for launch_managers, handles everything regarding the launch.
    Give the parameters,and it will call the corresponding functions / class to launch the game
    Args:
        launch_data:
        app:
        mode: "Vanilla", "Forge", "Modpack"

    Returns:

    """

    env : Environment | None = None # Shut up PyCharm linter!
    if mode == "Vanilla":
        env = build_vanilla_env(launch_data, app)
    elif mode == "Forge":
        env = build_forge_env(launch_data, app)
    elif mode == "Modpack":
        env = build_modpack_env(launch_data, app)

    if env is None:
        # If some kind of error happened, env will be None, error will be displayed by specific method, do nothing
        return

    Thread(target=run, args=[env]).start()
    SuccessWindow(app)

# Auxiliary method for Thread run
def run(env):
    env.run()