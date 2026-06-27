import json
import os


class FileManager:
    """
    Handles reading and writing JSON files.
    """

    def save_json(self, data, filepath):
        """
        Save data to a JSON file.
        """

        os.makedirs(os.path.dirname(filepath), exist_ok=True)

        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=4, ensure_ascii=False)

    def load_json(self, filepath):
        """
        Load data from a JSON file.
        """

        if not os.path.exists(filepath):
            return None

        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)