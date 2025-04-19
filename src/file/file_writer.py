import os
from email.policy import default

from src.utils.config_vars import CONTAINER_MODE
from src.utils.file_vars import WRITE_MODES, DEFAULT_REPORTS_DIR


class FileWriter:
    def __init__(self,
                 journal_dir: str,
                 timeframe_dir: str):

        self.output_path = ""
        if os.environ.get(CONTAINER_MODE, default=False):
            journal_dir = DEFAULT_REPORTS_DIR
        self.set_output_path(journal_dir, timeframe_dir)

    def set_output_path(self, journal_dir, timeframe_dir):
        if not journal_dir or not timeframe_dir:
            missing_data = "journal directory" if not journal_dir else "timeframe directory"
            raise ValueError(f"No {missing_data} was provided to write the file. Please check your parameters")
        if not os.path.isdir(journal_dir):
            raise FileNotFoundError(f"Output path provided '{journal_dir}' does not exist")

        output_path = os.path.join(journal_dir, timeframe_dir)

        if not os.path.isdir(output_path):
            os.makedirs(output_path)

        self.output_path = output_path

    def write_to_file(self, content, file_name, write_mode='w'):

        if not content or not file_name:
            missing_data = "content" if not content else "file_name"
            raise ValueError(f"No {missing_data} was provided to write the file. Please check your parameters")

        if write_mode not in WRITE_MODES.values():
            raise ValueError("Invalid write_mode chosen. Please check your parameters")

        with open(os.path.join(self.output_path, file_name), write_mode) as file:
            file.write(content)

        print(f"File '{file_name}' successfully written to '{self.output_path}'.")
