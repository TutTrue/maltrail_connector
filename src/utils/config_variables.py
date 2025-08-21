import os
from pathlib import Path

import yaml
from pycti import get_config_variable
from dotenv import load_dotenv


class Config:
    def __init__(self):
        """
        Initialize the connector with necessary configurations
        """

        self.load = self._load_config()
        self._initialize_configurations()

    @staticmethod
    def _load_config() -> dict:
        """
        Load the configuration from the YAML file
        :return: Configuration dictionary
        """
        parent_dir = Path(__file__).parents[2]
        config_file_path = parent_dir.joinpath("config.yml")
        print(f"Loading .env from the following path :::: {parent_dir} ")
        load_dotenv(parent_dir.joinpath(".env"))
        config = (
            yaml.load(open(config_file_path), Loader=yaml.FullLoader)
            if os.path.isfile(config_file_path)
            else {}
        )

        return config

    def _initialize_configurations(self) -> None:
        """
        Connector configuration variables
        :return: None
        """
        # OpenCTI configurations
        self.duration_period = get_config_variable(
            "CONNECTOR_DURATION_PERIOD",
            ["connector", "duration_period"],
            self.load,
        )

        # Connector extra parameters
        self.api_base_url = get_config_variable(
            "GITHUB_API_BASE_URL",
            ["github", "api_base_url"],
            self.load,
        )

        self.github_token = get_config_variable(
            "GITHUB_TOKEN",
            ["github", "github_token"],
            self.load,
        )
