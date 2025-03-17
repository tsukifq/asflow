import json
import os

# ...existing code...
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

with open(CONFIG_FILE, "r") as f:
    CONFIG = json.load(f)
