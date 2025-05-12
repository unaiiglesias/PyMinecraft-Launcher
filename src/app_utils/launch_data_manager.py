from src.util.utilities import load_json, save_json
from src.util.utilities import get_default_path

class LaunchData:
    """
    Class that will contain all the info necessary to launch the game
    It also handles loading / writing said data to / from the file

    Attributes are to be used directly, with . notation
    """

    def __init__(self, path = "launch_data.json"):

        self.file_path = path

        self.username : str = ""
        self.version_type : str = ""
        self.version : str = ""
        self.subversion : str = ""
        self.modpack : str = ""
        self.ram : int = 0
        self.path : str = ""
        self.premium : bool = False

        self.load_launch_data()

    def _set_default(self):
        self.username = "Default" # String
        self.version_type = "Vanilla" # String
        self.version = "1.12.2" # String
        self.subversion = "" # string
        self.modpack = "" # String
        self.ram = 2048 # Int
        self.path = get_default_path() # String
        self.premium = False

    def save_launch_data(self):
        """
        Wrirte launch data (all data contained in this object) to launch_data file
        """
        data = {
            "username" : self.username,
            "version_type" : self.version_type,
            "version" : self.version,
            "subversion" : self.subversion,
            "modpack" : self.modpack,
            "ram" : self.ram,
            "path" : self.path,
            "premium" : self.premium
        }
        save_json(data, self.path)


    def load_launch_data(self):
        """
        Read launch data form launch_data.json file
        If the file doesn't exist, it generates one with default data and initializes the object accordingly
        """
        try:
            json = load_json(self.file_path)
        except FileNotFoundError:
            # If there is no launch data, create a default one and write it so something exists
            print("WARNING: launch_data.json not found, generating default")
            self._set_default()
            self.save_launch_data()
            return

        # If the load succeeded, just fill the attributes
        self.username = json["username"]
        self.version_type = json["version_type"]
        self.version = json["version"]
        self.subversion = json["subversion"]
        self.modpack = json["modpack"]
        self.ram = int(json["ram"])
        self.path = json["path"]
        self.premium = bool(json["premium"])
