"""Parser for YAML-based app configuration."""

import logging
from logging.config import dictConfig
from typing import (Dict, Optional)

from addict import Dict as Addict
import yaml

from foca.models.config import (Config, LogConfig)

logger = logging.getLogger(__name__)


class ConfigParser():
    """Parser for FOCA config files.
    """

    def __init__(
        self,
        config_file: Optional[str] = None,
        format_logs: bool = True
    ) -> None:
        """Initialiser method for `ConfigParser` class.

        Args:
            config_file (Optional[str], optional): Path to config file in YAML
                format. Defaults to None.
            format_logs (bool, optional): Whether log formatting should be
                configured. Defaults to True.
        """
        if config_file:
            self.config = Config(**self.parse_yaml(config_file))
        else:
            self.config = Config()
        if format_logs:
            self.configure_logging()
        logger.debug(f"Parsed config: {self.config.dict(by_alias=True)}")

    def configure_logging(self) -> None:
        """Configure logging."""
        try:
            dictConfig(self.config.log.dict(by_alias=True))
        except Exception as e:
            dictConfig(LogConfig().dict(by_alias=True))
            logger.warning(
                f"Failed to configure logging. Falling back to default "
                f"settings. Original error: {type(e).__name__}: {e}"
            )

    @staticmethod
    def parse_yaml(conf: str) -> Dict:
        """Load YAML file.

        Args:
            conf (str): Path to YAML file.

        Raises:
            yaml.YAMLError: File cannot be accessed.
            OSError: File cannot be parsed.

        Returns:
            Dict: Dictionary of YAML file contents.
        """
        try:
            with open(conf) as config_file:
                try:
                    return yaml.safe_load(config_file)
                except yaml.YAMLError:
                    raise yaml.YAMLError(
                        f"file '{conf}' is not valid YAML"
                    )
        except OSError as e:
            raise OSError(
                f"file '{conf}' could not be read"
            ) from e

    @staticmethod
    def merge_yaml(*args: str) -> Optional[Dict]:
        """Parse and merge a set of YAML files.

        Note:
            Merging is done iteratively, from the first, second to the nth
            argument. Dict items are updated, not overwritten. For exact
            behavior cf. https://github.com/mewwts/addict.

        Args:
            *args: One or more paths to YAML files.

        Returns:
            Optional[Dict]: Dictionary of merged YAML file contents, or None
            if no arguments have been supplied; if only a single YAML file
            path is provided, no merging is done.
        """
        args_list = list(args)
        if not args_list:
            return None
        yaml_dict = Addict(ConfigParser.parse_yaml(args_list.pop(0)))

        for arg in args_list:
            yaml_dict.update(Addict(ConfigParser.parse_yaml(arg)))

        return yaml_dict.to_dict()
