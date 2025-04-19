from dotenv import load_dotenv
from configparser import ConfigParser
import tomllib

from src.logging.logger import Logger

logger = Logger()

class ConfigLoader:
    def __init__(self):
        load_dotenv()

class TOMLConfigLoader(ConfigLoader):
    def __init__(self, config_file_path):
        super().__init__()
        self.params = self.__load_configuration(config_file_path)

    @staticmethod
    def __load_configuration(toml_file: str):
        with open(toml_file, "rb") as file:
            config = tomllib.load(file)
        return config

    def get_value(self, section, name):
        section_value= self.params.get(section, {})
        if not section_value:
            logger.warning(f"Unable to find section '{section}' in the TOML file provided")
            return section_value
        name_value = section_value.get(name, {})
        if not name_value:
            logger.warning(f"Unable to find value '{name}' in section '{section}', in the TOML file provided")
        return name_value

class INIConfigLoader:
    def __init__(self, config_file_path):
        super().__init__()
        self.params = self.__load_configuration(config_file_path)

    @staticmethod
    def __load_configuration(ini_file: str):
        config = ConfigParser()
        read_ok = config.read(ini_file)

        if not read_ok:
            raise Exception(f"Configuration data was not properly parsed from target {ini_file} file."
                            " Please check the path and/or file provided.")

        #TODO test config contents for INI version!
        #config_dict = {section: dict(parser.items(section)) for section in parser.sections()}
        return config

    def get_value(self, section, name):
        return self.params.get(section=section, option=name)