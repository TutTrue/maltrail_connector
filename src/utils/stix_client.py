import ipaddress
import re
import stix2
import validators
from pycti import Identity, StixCoreRelationship
from pycti import OpenCTIConnectorHelper
import uuid


class STIXConvertor:
    """
    Provides methods for converting various types of input data into STIX 2.1 objects.

    REQUIREMENTS:
    - generate_id() for each entity from OpenCTI pycti library except observables to create
    """

    def __init__(self, helper: OpenCTIConnectorHelper, urls: list[str]):
        self.helper = helper
        self.author = self.create_author()
        self.external_reference = self.create_external_reference(urls)

    @staticmethod
    def create_external_reference(urls: list[str]) -> list:
        """
        Create external reference
        :return: External reference STIX2 list
        """
        references = []
        for url in urls:
            references.append(
                stix2.ExternalReference(
                    source_name="External Source",
                    url=url,
                    description="this is the associated reference for the IOCs fetched from the maltrail github repo",
                )
            )
        return references

    @staticmethod
    def create_author() -> dict:
        """
        Create Author
        :return: Author in Stix2 object
        """
        author = stix2.Identity(
            id=Identity.generate_id(name="Source Name", identity_class="organization"),
            name="maltrail",
            identity_class="organization",
            description="sources added from maltrail github repo owner.",
        )
        return author

    def create_relationship(
        self, source_id: str, relationship_type: str, target_id: str
    ) -> dict:
        """
        Creates Relationship object
        :param source_id: ID of source in string
        :param relationship_type: Relationship type in string
        :param target_id: ID of target in string
        :return: Relationship STIX2 object
        """
        relationship = stix2.Relationship(
            id=StixCoreRelationship.generate_id(
                relationship_type, source_id, target_id
            ),
            relationship_type=relationship_type,
            source_ref=source_id,
            target_ref=target_id,
            created_by_ref=self.author,
            external_references=self.external_reference,
        )
        return relationship

    def create_obs(self, value: str) -> dict:
        """
        Create observable according to value given
        :param value: Value in string
        :return: Stix object for IPV4, IPV6 or Domain
        """
        if self._is_ipv6(value) is True:
            stix_ipv6_address = stix2.IPv6Address(
                value=value,
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_ipv6_address
        elif self._is_ipv4(value) is True:
            stix_ipv4_address = stix2.IPv4Address(
                value=value,
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_ipv4_address
        elif self._is_domain(value) is True:
            stix_domain_name = stix2.DomainName(
                value=value,
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_domain_name
        elif self._is_email(value) is True:
            stix_email_address = stix2.EmailAddress(
                value=value,
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_email_address
        elif self._is_url(value) is True:
            stix_url = stix2.URL(
                value=value,
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_url
        elif self._is_md5(value) is True:
            stix_file_hash = stix2.File(
                name="File",
                hashes={"MD5": value},
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_file_hash
        elif self._is_mac_address(value) is True:
            stix_mac_address = stix2.MACAddress(
                value=value,
                custom_properties={
                    "x_opencti_created_by_ref": self.author["id"],
                    "x_opencti_external_references": self.external_reference,
                },
            )
            return stix_mac_address
        else:
            return None

    def create_indicator(self, value: str) -> dict:
        """
        Create indicator object
        :param value: Value in string
        :return: Indicator STIX2 object
        """

        # Create a proper STIX pattern based on the observable type
        # The pattern needs to reference a specific observable type, not generic 'observable'
        pattern = self._create_pattern(value)

        indicator = stix2.Indicator(
            id=f"indicator--{uuid.uuid5(uuid.NAMESPACE_URL, value)}",
            pattern_type="stix",
            pattern=pattern,
            created_by_ref=self.author,
            labels=["malicious-activity"],
            external_references=self.external_reference,
            custom_properties={
                "x_opencti_created_by_ref": self.author["id"],
                "x_opencti_external_references": self.external_reference,
            },
        )
        return indicator

    @staticmethod
    def _is_ipv6(value: str) -> bool:
        """
        Determine whether the provided IP string is IPv6
        :param value: Value in string
        :return: A boolean
        """
        try:
            ipaddress.IPv6Address(value)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def _is_ipv4(value: str) -> bool:
        """
        Determine whether the provided IP string is IPv4
        :param value: Value in string
        :return: A boolean
        """
        try:
            ipaddress.IPv4Address(value)
            return True
        except ipaddress.AddressValueError:
            return False

    @staticmethod
    def _is_domain(value: str) -> bool:
        """
        Valid domain name regex including internationalized domain name
        :param value: Value in string
        :return: A boolean
        """
        is_valid_domain = validators.domain(value)

        if is_valid_domain:
            return True
        else:
            return False

    @staticmethod
    def _is_url(value: str) -> bool:
        """
        Determine whether the provided string is URL
        :param value: Value in string
        :return: A boolean
        """
        is_valid_url = validators.url(value)

        if is_valid_url:
            return True
        else:
            return False

    @staticmethod
    def _is_email(value: str) -> bool:
        """
        Determine whether the provided string is email
        :param value: Value in string
        :return: A boolean
        """
        is_valid_email = validators.email(value)

        if is_valid_email:
            return True
        else:
            return False

    @staticmethod
    def _is_md5(value: str) -> bool:
        """
        Determine whether the provided string is MD5 hash
        :param value: Value in string
        :return: A boolean
        """
        is_valid_md5 = validators.md5(value)

        if is_valid_md5:
            return True
        else:
            return False

    @staticmethod
    def _is_mac_address(value: str) -> bool:
        """
        Determine whether the provided string is MAC address
        :param value: Value in string
        :return: A boolean
        """
        is_valid_mac_address = validators.mac_address(value)
        if is_valid_mac_address:
            return True
        else:
            return False

    @staticmethod
    def _is_file_path(value: str) -> bool:
        """
        Determine whether the provided string is file path
        :param value: Value in string
        :return: A boolean
        """
        file_path_pattern = (
            r'^(?:[a-zA-Z]:\\(?:[^<>:"/\\|?*\n\r]+\\?)*|\/(?:[^\/\n]+\/?)*)$'
        )
        return bool(re.match(file_path_pattern, value))

    def _create_pattern(self, value: str) -> str:
        """
        Create a proper STIX pattern based on the observable type
        :param value: Value in string
        :return: STIX pattern
        """
        # Escape special characters in the value to prevent STIX pattern syntax errors
        # First escape backslashes, then escape single quotes
        escaped_value = value.replace("\\", "\\\\").replace("'", "\\'")
        pattern = ""
        if self._is_ipv6(value):
            pattern = f"[ipv6-addr:value = '{escaped_value}']"
        elif self._is_ipv4(value):
            pattern = f"[ipv4-addr:value = '{escaped_value}']"
        elif self._is_domain(value):
            pattern = f"[domain-name:value = '{escaped_value}']"
        elif self._is_email(value):
            pattern = f"[email-addr:value = '{escaped_value}']"
        elif self._is_url(value):
            pattern = f"[url:value = '{escaped_value}']"
        elif self._is_md5(value):
            pattern = f"[file:hashes.MD5 = '{escaped_value}']"
        elif self._is_mac_address(value):
            pattern = f"[mac-addr:value = '{escaped_value}']"
        else:
            # For unknown types (like regex patterns), use artifact object
            pattern = f"[artifact:payload_bin = '{escaped_value}']"
        return pattern
