import json

filename = "config.json"

class ConfigManager:
    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.config = self.loadConfig()

    def loadConfig(self) -> dict:
        with open(self.filename, "r") as file:
            return json.loads(file.read())

    def saveConfig(self) -> None:
        with open(self.filename, "w") as file:
            file.write(json.dumps(config, indent=4))

if __name__ == "__main__":
    manager = ConfigManager(filename)
    config = manager.loadConfig()
    print(config)