from pathlib import Path

PATH_TO_BASE_FOLDER = Path(__file__).resolve().parents[1]


class EnvFileLocation:
    LOCATION = f"{PATH_TO_BASE_FOLDER}/.env"
