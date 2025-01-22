import json
from locale import getdefaultlocale
from googletrans import Translator
from os.path import join

MOUSE_TRACKER_FOLDER = r"C:\ProgramData\MouseTracker"
MOUSE_TRACKER_LANGUAGE_FILE = "*.json"

class Language:
    def __init__(self) -> None:
        self.current_language = self.get_system_language()
        self.is_loaded_language_file = self.load_language_file()

    def is_language_loaded(self):
        return self.is_loaded_language_file
    
    def get_system_language(self):
        current_locale = getdefaultlocale()
        if current_locale:
            self.current_language = current_locale[0].split("_")[0]
            return self.current_language
        else:
            return None
    def load_language_file(self):
        try:
            with open(join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_LANGUAGE_FILE.replace("*", self.current_language)), "r", encoding="utf-8") as f:
                self.language_file = json.load(f)
            if self.language_file:
                self.is_loaded_language_file = True
                return True
        except FileNotFoundError:
            pass

        self.is_loaded_language_file = False
        return False
        
    def create_language_file(self, strings):
        language_file = {}

        try:
            translator = Translator()

            for string in strings:
                language_file[string] = translator.translate(string, self.current_language).text
                
            with open(join(MOUSE_TRACKER_FOLDER, MOUSE_TRACKER_LANGUAGE_FILE.replace("*", self.current_language)), "w", encoding="utf-8") as f:
                json.dump(language_file, f, indent=4)

            return True
        except Exception as e:
            print(e)
            return False
        
    def get_string(self, key):
        if self.current_language and self.is_loaded_language_file:
            try:
                return self.language_file[key]
            except KeyError:
                return key
        else:
            return key
    
    def translate(self, text):
        try:
            return Translator().translate(text, self.current_language).text
        except Exception as e:
            print(e)
            return text