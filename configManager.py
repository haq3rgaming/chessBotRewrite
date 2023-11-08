import json

filename = "config.json"

def loadConfig() -> dict:
    global config
    with open(filename, "r") as file:
        return json.loads(file.read())

def saveConfig(config) -> None:
    with open(filename, "w") as file:
        file.write(json.dumps(config, indent=4))

if __name__ == "__main__":
    print(loadConfig())