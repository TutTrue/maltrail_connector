import sys
from datetime import datetime
import time
import traceback

from pycti import OpenCTIConnectorHelper
from src.utils.github_client import GithubClient
from src.utils.config_variables import Config
from src.utils.stix_client import STIXConvertor


class ConnectorTemplate:
    """
    ---

    Attributes
        - `config (Config())`:
            Initialize the connector with necessary configuration environment variables

        - `helper (OpenCTIConnectorHelper(config))`:
            This is the helper to use.
            ALL connectors have to instantiate the connector helper with configurations.
            Doing this will do a lot of operations behind the scene.

        - `stix_client (ConnectorConverter(helper))`:
            Provide methods for converting various types of input data into STIX 2.1 objects.

    ---

    """

    def __init__(self):
        """
        Initialize the Connector with necessary configurations
        """

        # Load configuration file and connection helper
        self.config = Config()
        self.helper = OpenCTIConnectorHelper(self.config.load)
        self.client = GithubClient(self.helper, self.config)

    def run(self) -> None:
        """
        Run the main process encapsulated in a scheduler
        It allows you to schedule the process to run at a certain intervals
        This specific scheduler from the pycti connector helper will also check the queue size of a connector
        If `CONNECTOR_QUEUE_THRESHOLD` is set, if the connector's queue size exceeds the queue threshold,
        the connector's main process will not run until the queue is ingested and reduced sufficiently,
        allowing it to restart during the next scheduler check. (default is 500MB)
        It requires the `duration_period` connector variable in ISO-8601 standard format
        Example: `CONNECTOR_DURATION_PERIOD=PT5M` => Will run the process every 5 minutes
        :return: None
        """
        while True:
            try:
                self.process_message()
            except (KeyboardInterrupt, SystemExit):
                self.helper.log_info("Connector stop")
                sys.exit(0)
            except Exception:  # pylint:disable=broad-exception-caught
                self.helper.log_error(traceback.format_exc())

            if self.helper.connect_run_and_terminate:
                self.helper.log_info("Connector stop")
                self.helper.force_ping()
                sys.exit(0)
            # this should sleep it for 2 days before it runs againe
            time.sleep(172800)

    def process_message(self) -> None:
        """
        Connector main process to collect intelligence
        :return: None
        """
        self.helper.connector_logger.info(
            "[CONNECTOR] Starting connector...",
            {"connector_name": self.helper.connect_name},
        )

        try:
            # Get the current state
            now = datetime.now()
            current_timestamp = int(datetime.timestamp(now))
            current_state = self.helper.get_state()

            if current_state is not None and "last_run" in current_state:
                last_run = current_state["last_run"]

                self.helper.connector_logger.info(
                    "[CONNECTOR] Connector last run",
                    {"last_run_datetime": last_run},
                )
            else:
                self.helper.connector_logger.info(
                    "[CONNECTOR] Connector has never run..."
                )

            # Friendly name will be displayed on OpenCTI platform
            friendly_name = "Connector template feed"

            # Initiate a new work
            work_id = self.helper.api.work.initiate_work(
                self.helper.connect_id, friendly_name
            )

            self.helper.connector_logger.info(
                "[CONNECTOR] Running connector...",
                {"connector_name": self.helper.connect_name},
            )

            # Performing the collection of intelligence
            stix_objects = self._collect_intelligence()

            # Note: STIX objects are now sent individually for each file in _collect_intelligence
            # No need to send a bundle here anymore
            
            current_state = self.helper.get_state()
            current_state_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            last_run_datetime = datetime.utcfromtimestamp(current_timestamp).strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if current_state:
                current_state["last_run"] = current_state_datetime
            else:
                current_state = {"last_run": current_state_datetime}
            self.helper.set_state(current_state)

            message = (
                f"{self.helper.connect_name} connector successfully run, storing last_run as "
                + str(last_run_datetime)
            )

            self.helper.api.work.to_processed(work_id, message)
            self.helper.connector_logger.info(message)

        except (KeyboardInterrupt, SystemExit):
            self.helper.connector_logger.info(
                "[CONNECTOR] Connector stopped...",
                {"connector_name": self.helper.connect_name},
            )
            sys.exit(0)
        except Exception as err:
            self.helper.connector_logger.error(str(err))

    def _collect_intelligence(self) -> list:
        """
        Collect intelligence from the source and convert into STIX object
        Send STIX objects for each individual file immediately
        :return: List of STIX objects (empty list since we send individually)
        """
        stix_objects = []
        file_count = 0

        for entity in self.client.get_entities(
            owner="stamparm", repo="maltrail", path="trails/static"
        ):
            self.helper.connector_logger.info(
                f"Processing entity: {entity}"
            )
            
            # Process this entity and send immediately
            file_stix_objects = self._process_entity(entity)
            
            if file_stix_objects:
                # Create and send bundle for this file
                file_bundle = self.helper.stix2_create_bundle(file_stix_objects)
                bundles_sent = self.helper.send_stix2_bundle(file_bundle)
                
                self.helper.connector_logger.info(
                    f"Sent STIX objects for file {file_count + 1}",
                    {"bundles_sent": {str(len(bundles_sent))}, "file_count": file_count + 1}
                )
                
                file_count += 1
                
                # Update state after each file is processed
                self._update_state_after_file(file_count)

        self.helper.connector_logger.info(
            f"Completed processing {file_count} files",
            {"total_files_processed": file_count}
        )
        
        return stix_objects  # Return empty list since we sent individually

    def _process_entity(self, entity: dict) -> list:
        """
        Process a single entity and convert to STIX objects
        :param entity: Entity data containing references and observables
        :return: List of STIX objects for this entity
        """
        stix_convertor = STIXConvertor(self.helper, entity["references"])
        observables = []
        indicators = []
        relationships = []
        
        for value in entity["observables"]:
            if value:
                observable = stix_convertor.create_obs(value)
                indicator = stix_convertor.create_indicator(value)
                indicators.append(indicator)
                if observable:
                    observables.append(observable)
                    relationships.append(
                        stix_convertor.create_relationship(
                            observable["id"], "indicates", indicator["id"]
                        )
                    )
        
        return observables + indicators + relationships

    def _update_state_after_file(self, file_count: int) -> None:
        """
        Update the connector state after processing each file
        :param file_count: Number of files processed so far
        """
        try:
            current_state = self.helper.get_state()
            now = datetime.now()
            current_state_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
            
            if current_state:
                current_state["last_run"] = current_state_datetime
                current_state["files_processed"] = file_count
            else:
                current_state = {
                    "last_run": current_state_datetime,
                    "files_processed": file_count
                }
            
            self.helper.set_state(current_state)
            
            self.helper.connector_logger.info(
                f"Updated state after processing file {file_count}",
                {"files_processed": file_count, "last_update": current_state_datetime}
            )
            
        except Exception as err:
            self.helper.connector_logger.error(f"Error updating state: {err}")
