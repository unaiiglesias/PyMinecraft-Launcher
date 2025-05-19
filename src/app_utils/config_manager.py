from configparser import ConfigParser
from datetime import datetime, timedelta


class Configuration:

    """
        The launcher uses a config.ini file to save some configuration data. This class provides a comfortable interface
        for the launcher to access this config file.

        Configuration is stored as a dictionary and exposed by the object. Therefore, configuration values can be accessed
        directly as if the configuration object where the dictionary itself.

        This class  also handles config.ini file verification according to the SCHEMA and DEFAULT values.

        config file / file = config.ini
    """

    # Defines the structure tha the config file should follow (values indicate type of the stored info)
    SCHEMA = {
        "MAIN": {
            "title": "str",
            "icon": "str",
            "theme": "str",
            "language": ["Español", "English"],
            "show_terror": "bool",
            "version": ["1.14"],
            "cache_day_vanilla": "int",
            "cache_day_forge": "int",
            "cache_day_modpack": "int",
            "cache_date_vanilla" : "datetime", # All dates are stored as str, but loaded as datetime.datetime
            "cache_date_forge": "datetime",
            "cache_date_modpack": "datetime"
        }
    }

    # Default values for each field (MUST match schema)
    DEFAULT = {
        "MAIN": {
            "title": "Calvonetta Launcher",
            "icon": "assets/calvonetta_cut_transparent.ico",
            "theme": "Dark",
            "language": "English",
            "show_terror": 0,
            "version": "1.14",
            "cache_day_vanilla": 0,
            "cache_day_forge": 0,
            "cache_day_modpack": 0,
            "cache_date_vanilla": datetime.now() - timedelta(days=1), # Default time is yesterday (so that cache is forced to update)
            "cache_date_forge": datetime.now() - timedelta(days=1),
            "cache_date_modpack": datetime.now() - timedelta(days=1)
        }
    }

    def __init__(self, path = "config.ini"):
        # When config_manager is used by main.py, the default path is correct, but when it is used by
        # other scripts it might change i.e. config_manager.py/main --> ../config.ini
        self.path = path
        self._cfg = {}
        self.load_ini()


    def load_ini(self):
        """
        Reads config.ini file and sets self._cfg dictionary. This is done so that options can be loaded with
        the proper data type. Data type conversion is handled by this script and must be transparent to users

        The purpose of this function is to ensure that all variables have an expected value (in case an old config.ini file
        is loaded) and to provide a similar interface to that of launch_data.json.
        """

        """ Load config.ini file into resul dictionary or return default if config.ini not found """
        try:
            parser = ConfigParser()
            parser.read(self.path, encoding="UTF-8")
            self._cfg = {section: dict(parser.items(section)) for section in parser.sections()}
            self._validate_cfg()

        except IOError:
            # config.ini was not found, return default
            print("WARNING: config.ini was not found, returning default values and creating a new one")
            self._cfg = self.DEFAULT
            self.write_ini()

        except (TypeError, KeyError):
            # config.ini is malformed
            print("WARNING: config.ini is malformed, returning default values")
            self._cfg = self.DEFAULT
            self.write_ini()

        except UnicodeError:
            # config.ini could be obsolete
            print("WARNING: config.ini has wrong format, returning default values and overwriting")
            self._cfg = self.DEFAULT
            self.write_ini()


    def write_ini(self):
        """
        Creates and saves config.ini file with provided cfg dictionary
        """
        print("Writing config.INI file")

        save = ConfigParser()
        save.read_dict(self._cfg)

        with open("config.ini", "w") as ini_file:
            save.write(ini_file)

    def _validate_cfg(self):
        """
        Validates that cfg is correct
        Doesn't return anything. Instead, it corrects errors directly on cfg

        This is generic code to check that the dictionary is ok based on the schema, and thus should not have to be
        updated every time the schema changes.
        This function also updates outdated versions of the .ini file.

        The function will have to iterate twice:
            - Ensure all fields in SCHEMA exist
            - Discard all fields that are in cfg but not in SCHEMA

        Params:
            cfg: Current read configuration dictionary from existing config.ini file
        """

        changed = False # We'll only have to overwrite current.ini if validation changed something

        # Seems like I cant delete stuff mid-loop, so note down what to delete and do so afterwards
        sections_to_remove = []

        """
            This loop will check 2 main things:
                - Only sections & fields in SCHEMA exist (mark for removal sections & fields that aren't in schema)
                - fields have allowed data types
        """
        # Iterate over CFG keys
        schema_sections = self.SCHEMA.keys()
        for section in self._cfg.keys():
            # Skip default section
            if section == "DEFAULT":
                continue

            # If section doesn't exist, mark it for removal
            if section not in schema_sections:
                changed = True
                sections_to_remove.append(section)
                continue

            fields_to_remove = []

            # Iterate over fields of this section in CFG
            schema_fields = self.SCHEMA[section].keys()
            for field in self._cfg[section].keys():
                # If field shouldn't exist, mark it for removal
                if field not in schema_fields:
                    changed = True
                    fields_to_remove.append(field)
                    continue

                # If field should exist, check data type
                aux = self._cfg[section][field] # current value of field
                exp_type = self.SCHEMA[section][field] # Expected value of field
                default = self.DEFAULT[section][field]
                if type(exp_type) == list: # List indicates that the value must be one of said list
                    if not aux in exp_type:
                        self._cfg[section][field] = default
                        changed = True

                elif exp_type == "int":
                    try:
                        self._cfg[section][field] = int(aux)
                    except (TypeError, ValueError):
                        changed = True
                        self._cfg[section][field] = default

                elif exp_type == "float":
                    try:
                        self._cfg[section][field] = float(aux)
                    except (TypeError, ValueError):
                        changed = True
                        self._cfg[section][field] = default

                elif exp_type == "bool":
                    if aux in ("1", "True", "true"):
                        self._cfg[section][field] = True

                    elif aux in ("0", "False", "false"):
                        self._cfg[section][field] = False

                    else:
                        changed = True
                        self._cfg[section][field] = default

                elif exp_type == "datetime":
                    try:
                        self._cfg[section][field] = datetime.strptime(aux, "%Y-%m-%d %H:%M:%S.%f")
                    except ValueError:
                        self._cfg[section][field] = default

                # In this case, whatever is in there will be ok
                elif exp_type == "str":
                    pass


            # Remove fields
            for field in fields_to_remove:
                del self._cfg[section][field]

        # Remove sections
        for section in sections_to_remove:
            del self._cfg[section]

        """
        This loop will add all sections & fields from SCHEMA that don't exist
        """
        for section in self.DEFAULT.keys():
            if not section in self._cfg.keys():
                self._cfg[section] = self.DEFAULT[section]
                changed = True
                continue

            for field in self.DEFAULT[section].keys():
                if not field in self._cfg[section].keys():
                    self._cfg[section][field] = self.DEFAULT[section][field]
                    changed = True

        if changed:
            self.write_ini()

    def __getitem__(self, key):
        """
        Allows the config dictionary to be accessed
        Enables the object to be used as if it where said dictionary itself
        """
        return self._cfg[key]

    def __repr__(self):
        """
        ToString
        """
        return repr(self._cfg)


def main():
    """
        Function only intended for testing and debugging purpouses
    """

    cfg = Configuration(path ="../config.ini")
    print(cfg)


if __name__ == "__main__":
    main()
