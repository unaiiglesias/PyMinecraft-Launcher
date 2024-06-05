import json
from configobj import ConfigObj


def load_ini():
    """
    Reads config.ini file and turns it into a dictionary, saves the dictionary in app.cfg

    The purpouse of this is to ensure that all variables have an expected value (in case an old config.ini file) is
    loaded and to provide a similar interface to that of launch_data.json.

    As of 02/06/2024 it will be assumed that an update will only add stuff to the config.ini
    """
    default = {
        "title": "Calvonetta Launcher",
        "icon": "assets/calvonetta_cut_transparent.ico",
        "theme": "Dark",
        "language": "en",
        "show_terror": False,
        "version": 1.1,
        "cache_day_vanilla": 0,
        "cache_day_forge": 0,
        "cache_day_modpack": 0
    }

    try:
        cfg = ConfigObj("config.ini", raise_errors=True, file_error=True)
        # load config overwriting default values (TODO: Deprecated values will be loaded)
        resul = default.copy()  # We do this so that, if the file is malformed, the default remains unaltered
        for key in cfg["MAIN"]:
            resul[key] = cfg["MAIN"][key]

    except IOError:
        # config.ini was not found, return default
        print("WARNING: config.ini was not found, returning default values")
        return default

    except TypeError:
        # config.ini is malformed
        print("WARNING: config.ini is malformed, returning default values")
        return default

    # Validate resul (taking default as template)
    try:
        resul["show_terror"] = eval(resul["show_terror"])
    except TypeError:
        resul["show_terror"] = False
        print("WARNING: config.ini show_terror malformed, using False")
    try:
        resul["version"] = float(resul["version"])
    except TypeError:
        resul["version"] = 0.0
        print("WARNING: config.ini version malformed, shwoing error")
    try:
        resul["cache_day_vanilla"] = int(resul["cache_day_vanilla"])
    except TypeError:
        resul["cache_day_vanilla"] = 0
        print("WARNING: config.ini cache_day_vanilla malformed, using 0")
    try:
        resul["cache_day_forge"] = int(resul["cache_day_forge"])
    except TypeError:
        resul["cache_day_forge"] = 0
        print("WARNING: config.ini cache_day_forge malformed, using 0")
    try:
        resul["cache_day_modpack"] = int(resul["cache_day_modpack"])
    except TypeError:
        resul["cache_day_modpack"] = 0
        print("WARNING: config.ini cache_day_modpack malformed, using 0")

    return resul


def save_ini(cfg):
    """
    Creates and saves config.ini file.
    Since some of its entries might be changed, it is necessary to save those changes.

    cfg is self.cfg, the config dictionary

    Using load_ini's default as a template
    """
    resul = ConfigObj("config.ini", raise_errors=True, create_empty=True, encoding="UTF8")
    for key in cfg:
        resul["MAIN"][key] = cfg[key]
    resul.write()


def load_launch_data():
    """
    Load launch data from json and returns the dictionary.

    Raises FileNoFoundError if the file is not found (obviously)
    """
    try:
        with open("./launch_data.json", "r") as json_file:
            launch_data = json.load(json_file)
        return launch_data
    except FileNotFoundError:
        print("WARNING: launch_data.json was not found")
        raise FileNotFoundError


def save_launch_data(launch_data):
    """
    Save launch data to json
    """
    with open("./launch_data.json", "w") as json_file:
        json.dump(launch_data, json_file, indent=4)


def load_translations(language):
    """
    Loads translations.json and return it.
    language = full language string (Español, English)
    """
    language_key = None
    if language == "Español":
        language_key = "es"
    else:
        language_key = "en"

    print(f"Loading translations.jsos in {language} code:{language_key}")
    try:
        with open("./assets/translations.json", "r", encoding="utf-8") as file:
            translations_file = json.load(file)
        return translations_file[language_key]
    except FileNotFoundError as e:
        print("ERROR: translations.json not found")
        raise e


def main():
    """
        Function only intended for testing and debugging purpouses
    """
    print(load_ini())


if __name__ == "__main__":
    main()
