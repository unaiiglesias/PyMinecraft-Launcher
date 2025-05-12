from src.util.utilities import load_json

class Translations:
    """
    Class to manage the translations of the app.
    In order to be used, an object should be created and used as if it where a dictionary
    Keys to translation dictionary can be found in assets/translations.json

    By default, it loads English translations
    """


    def __init__(self, language = "English", path = "assets/translations.json"):

        self.path = path

        self.avaliable_langs = {"Español": "es", "English": "en"}
        self._translations = None # Translations dictionary
        self.load_translations(language) # This writes to self._translations
        self.lang = language # Currently selected lang (Language name, not key)

    def load_translations(self, language):
        """
        Loads translation .json and saves it in the object
        It is also used to change the current language
        Args:
            language: Language name, not key (Español OK, es NOT OK)
        """

        if language not in self.avaliable_langs:
            raise KeyError(f"Selected language ({language}) does not exist")

        language_key = self.avaliable_langs[language]
        print(f"Loading translations.json in {language} code:{language_key}")
        self._translations = load_json(self.path)[language_key]
        self.lang = language

    def get_current_lang(self):
        return self.lang

    def __getitem__(self, key):
        """
        Allows the translations dictionary to be accessed
        Enables the object to be used as if it where said dictionary itself
        """
        return self._translations[key]

    def __repr__(self):
        """
        ToString
        """
        return repr(self._translations)