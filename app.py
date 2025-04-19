from os.path import join, dirname
from src.journal_pipeline import JournalPipeline
import argparse
from datetime import datetime

from src.logging.logger import Logger
from src.utils.config_vars import (SUPPORTED_TIMEFRAMES, SUPPORTED_CONFIG_TYPES, TOML_CONFIG_TYPE,
                                   DAILY_TIMEFRAME, CONFIG_FILE_NAME)

logger = Logger()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-tf", "--timeframe", type=str, default=DAILY_TIMEFRAME,
                        help="Timeframe range to be used for the journal. Supported timeframes:\n"
                             f"{'\n'.join(' - '+tf for tf in SUPPORTED_TIMEFRAMES)}")
    parser.add_argument("-dt", "--start_date", type=str,
                        default=datetime.strftime(datetime.now(), "%Y-%m-%d"),
                        help="(Initial) Date or month of the year (if timeframe == 'Monthly') to fetch data from."
                             "Only YYYY-mm-dd and YYYY-mm (if 'Monthly') formats supported.")
    parser.add_argument("-cfg", "--config_type", type=str, default=TOML_CONFIG_TYPE,
                        help="The configuration file type to load the app's configuration details from."
                             " Supported timeframes:\n"
                             f"{'\n'.join(' - '+config for config in SUPPORTED_CONFIG_TYPES)}")

    args = parser.parse_args()
    logger.info(args)

    if args.config_type not in SUPPORTED_CONFIG_TYPES:
        logger.warning(f"Unsupported config type provided. Setting to default config type '{TOML_CONFIG_TYPE}' instead.")
        args.config_type = TOML_CONFIG_TYPE

    args.timeframe = args.timeframe.lower()
    if args.timeframe.lower() not in SUPPORTED_TIMEFRAMES:
        logger.warning(f"Unsupported timeframe provided. Setting to default config type '{DAILY_TIMEFRAME}' instead.")
        args.timeframe = DAILY_TIMEFRAME

    config_file = '.'.join([CONFIG_FILE_NAME, args.config_type])
    config_file_path = join(dirname(__file__), config_file)

    pipeline = JournalPipeline(
        config_file_path,
        args.start_date,
        args.timeframe,
        args.config_type
    )

    pipeline.run()

if __name__ == "__main__":    main()
