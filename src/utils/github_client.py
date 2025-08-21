import time
import re
from typing import Generator, Any
from httpx import Client
from src.utils.config_variables import Config
from pycti import OpenCTIConnectorHelper
from urllib.parse import urljoin


class GithubClient:
    """
    Github Client to interact with Github API

    """

    def __init__(self, helper: OpenCTIConnectorHelper, config: Config):
        """
        Initialize the Github client with necessary configurations
        """
        self.helper = helper
        self.config = config
        self.headers = {
            "Authorization": f"Bearer {self.config.github_token}",
            "Agent": "Mozilla/5.0",
        }
        self.cooldown_seconds = 3

    def get_entities(
        self, owner: str, repo: str, path: str
    ) -> Generator[dict[str, list], Any, None]:
        """
        If params is None, retrieve all CVEs in National Vulnerability Database
        :param params: Optional Params to filter what list to return
        :return: A list of dicts of the complete collection of CVE from NVD
        """

        try:
            for url in self.generate_directory_file_urls(
                owner,
                repo,
                path,
                ["__init__.py", "mass_scanner.txt", "mass_scanner_cidr.txt"],
            ):
                with Client() as client:
                    response = client.get(url, headers=self.headers)
                    response.raise_for_status()
                    text = response.text
                    if text:
                        self.helper.connector_logger.info(
                            f"Processing The file with path {path}"
                        )
                        for value in self.process_text(text):
                            yield value
                time.sleep(self.cooldown_seconds)

        except Exception as err:
            self.helper.connector_logger.error(err)

    def generate_directory_file_urls(
        self, owner: str, repo: str, path: str, ignored_files: list[str] = []
    ) -> Generator[Any, Any, str]:
        """
        Get all directories in a Github repository path
        :return: List of file urls in the repository
        """
        try:
            relative_url_path = f"{owner}/{repo}/contents/{path}"
            directory_url = urljoin(self.config.api_base_url, relative_url_path)
            with Client() as client:
                response = client.get(directory_url, headers=self.headers)
                response = response.json()
                for item in response:
                    name: str = item["name"]
                    if (
                        name.startswith(".")
                        or name.startswith("__")
                        or name in ignored_files
                    ):
                        continue
                    if item["type"] == "file":
                        yield item["download_url"]
                    elif item["type"] == "dir":
                        yield from self.generate_directory_file_urls(
                            owner, repo, item["path"], ignored_files
                        )
                    time.sleep(self.cooldown_seconds)
        except Exception as err:
            self.helper.connector_logger.error(err)

    def process_text(
        self,
        text: str,
    ) -> Generator[dict[str, list], Any, None]:
        """
        Process each line in the file
        :param text: text file as string
        :return: None: change based on the repo you process
        """

        reference_pattern = re.compile(
            r"(?P<refs>(^# Reference:.*\n)+)(?P<observables>(^(?!# Reference:|# Generic).*\n)+)?",
            re.MULTILINE,
        )

        generic_pattern = re.compile(
            r"# Generic\s*\n(?P<generic>(?:/.*\n)+)", re.MULTILINE
        )
        matches = reference_pattern.finditer(text)
        generics = generic_pattern.search(text)
        for match in matches:
            observables_dict = {"references": [], "observables": []}
            refs = match.group("refs").strip().splitlines()
            observables = (
                match.group("observables").strip().splitlines()
                if match.group("observables")
                else []
            )

            for line in refs:
                pattern = r"# Reference: (.+)"
                line = line.strip()
                match = re.match(pattern, line)
                if match:
                    line = match.group(1)
                    observables_dict["references"].append(line)

            for line in observables:
                line = line.strip()
                if line == "":
                    continue
                observables_dict["observables"].append(line)

            yield observables_dict

        if generics:
            generics = generics.group("generic").strip().splitlines()
            observables_dict = {"references": [], "observables": []}
            for line in generics:
                line = line.strip()
                if line == "":
                    continue
                observables_dict["observables"].append(line)
            yield observables_dict
