from configparser import ConfigParser

SCHEMA = {
    "MAIN" : {
        "title" : "str",
        "icon" : "str",
        "theme" : "str",
        "language" : ["Español", "English"],
        "show_terror" : "bool",
        "version" : ["1.14"],
        "cache_day_vanilla" : "int",
        "cache_day_forge" : "int",
        "cache_day_modpack" : "int"
    }
}

DEFAULT = {
    "MAIN" : {
        "title" : "Calvonetta Launcher",
        "icon": "assets/calvonetta_cut_transparent.ico",
        "theme": "Dark",
        "language": "English",
        "show_terror": 0,
        "version": "1.14",
        "cache_day_vanilla": 0,
        "cache_day_forge": 0,
        "cache_day_modpack": 0
    }
}

def _validate_cfg(cfg : dict):
    """
    Validates that cfg is correct
    Doesn't return anything. Instead, it corrects errors directly on cfg

    This is generic code to check that the dictionary is ok based on the schema, should not have to be
    modified every time the .ini changes and it should also be able to update outdated versions of the .ini file

    The function will have to iterate twice:
        - Ensure all fields in SCHEMA exist
        - Discard all fields that are in cfg but not in SCHEMA
    """

    changed = False # We'll only have to overwrite current.ini if validation changed something

    # Seems like I cant delete stuff mid-loop, so note down what to delete and do so afterwards
    sections_to_remove = []

    """
        This loop will check 2 main things:
            - Only sections & fields in SCHEMA exist
            - fields have allowed data types
        """
    # Iterate over CFG keys
    schema_sections = SCHEMA.keys()
    for section in cfg.keys():
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
        schema_fields = SCHEMA[section].keys()
        for field in cfg[section].keys():
            # If field shouldn't exist, mark it for removal
            if field not in schema_fields:
                changed = True
                fields_to_remove.append(field)
                continue

            # If field should exist, check data type
            aux = cfg[section][field] # current value of field
            exp_type = SCHEMA[section][field] # Expected value of field
            default = DEFAULT[section][field]
            if type(exp_type) == list: # List indicates that the value must be one of said list
                if not aux in exp_type:
                    cfg[section][field] = default
                    changed = True

            elif exp_type == "int":
                try:
                    cfg[section][field] = int(aux)
                except (TypeError, ValueError):
                    changed = True
                    cfg[section][field] = default

            elif exp_type == "float":
                try:
                    aux = float(aux)
                except (TypeError, ValueError):
                    changed = True
                    cfg[section][field] = default

            elif exp_type == "bool":
                if aux in ("1", "True", "true"):
                    cfg[section][field] = True

                elif aux in ("0", "False", "false"):
                    cfg[section][field] = False

                else:
                    changed = True
                    cfg[section][field] = default
                    continue

            # In this case, whatever is in there will be ok
            elif exp_type == "str":
                pass


        # Remove fields
        for field in fields_to_remove:
            del cfg[section][field]

    # Remove sections
    for section in sections_to_remove:
        del cfg[section]

    """
    This loop will add all sections & fields from SCHEMA that don't exist
    """
    for section in DEFAULT.keys():
        if not section in cfg.keys():
            cfg[section] = DEFAULT[section]
            changed = True
            continue

        for field in DEFAULT[section].keys():
            if not field in cfg[section].keys():
                cfg[section][field] = DEFAULT[section][field]
                changed = True

    if changed:
        save_ini(cfg)


def load_ini():
    """
    Reads config.ini file and return its corresponding dictionary. This is done so that options can be loaded with
    the proper data type. Data type conversion is handled by this script and must be transparent to users

    The purpose of this function is to ensure that all variables have an expected value (in case an old config.ini file
    is loaded) and to provide a similar interface to that of launch_data.json.

    This function also updates outdated .ini. It contains a template of what the .ini file should look like and it
    enforces it to the current .ini file.
    """

    """ Load config.ini file into resul dictionary or return default if config.ini not found """
    try:
        parser = ConfigParser()
        parser.read("config.ini", encoding="UTF-8")
        cfg = {section: dict(parser.items(section)) for section in parser.sections()}
        _validate_cfg(cfg)

    except IOError:
        # config.ini was not found, return default
        print("WARNING: config.ini was not found, returning default values and creating a new one")
        cfg = DEFAULT
        save_ini(cfg)

    except (TypeError, KeyError):
        # config.ini is malformed
        print("WARNING: config.ini is malformed, returning default values")
        cfg = DEFAULT
        save_ini(cfg)

    except UnicodeError:
        # config.ini could be obsolete
        print("WARNING: config.ini has wrong format, returning default values and overwritting")
        cfg = DEFAULT
        save_ini(cfg)

    return cfg


def save_ini(cfg : dict):
    """
    Creates and saves config.ini file with provided cfg dictionary
    """

    print("Writing config.INI file")

    save = ConfigParser()
    save.read_dict(cfg)

    with open("../config.ini", "w") as ini_file:
        save.write(ini_file)


def main():
    """
        Function only intended for testing and debugging purpouses
    """

    cfg = load_ini()
    print(cfg)


if __name__ == "__main__":
    main()
