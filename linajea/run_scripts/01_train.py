"""Training run script

Loads the configuration and starts training.
Uses data specified under [train_data]
Writes logging output to stdout and run.log file
"""
import argparse
import logging
import os
import sys
import time

from linajea.config import (TrackingConfig,
                            maybe_fix_config_paths_to_machine_and_load)
from linajea.utils import print_time
from linajea.training import train

logger = logging.getLogger(__name__)


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--config', type=str,
                        help='path to config file')
    args = parser.parse_args()

    config = maybe_fix_config_paths_to_machine_and_load(args.config)
    config = TrackingConfig(**config)
    logging.basicConfig(
        level=config.general.logging,
        handlers=[
            logging.FileHandler(os.path.join(config.general.setup_dir,
                                             'run.log'),
                                mode='a'),
            logging.StreamHandler(sys.stdout),
        ],
        format='%(asctime)s %(name)s %(levelname)-8s %(message)s')

    start_time = time.time()
    train(config)
    end_time = time.time()
    print_time(end_time - start_time)
