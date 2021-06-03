from keckdrpframework.core.framework import Framework
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.utils.drpf_logger import getLogger

from KeckDeimosQL.keckdeimosql.pipelines.pipeline import PypeItPipeline
import logging.config

import argparse
import sys
import traceback
import os

def _parse_arguments(in_args: list) -> argparse.Namespace:
    description = "KCWI pipeline CLI"

    # this is a simple case where we provide a frame and a configuration file
    parser = argparse.ArgumentParser(prog=f"{in_args[0]}",
                                     description=description)
    parser.add_argument('-d', '--directory', dest="dirname", type=str,
                        help="Input directory", nargs='?', default=None)
    parser.add_argument('--force', dest="force", help="Ingest science files"
                                                    "regardless of calib count",
                        action="store_true")
    parser.add_argument('--no-clobber', dest='no_clobber',
                         help="If more than the minimum calibrations are"
                                "provided, don't update the initial processing"
                                "with new files",
                         action="store_true")
    # after ingesting the files,
    # do we want to continue monitoring the directory?
    parser.add_argument('-m', '--monitor', dest="monitor",
                        help='Continue monitoring the directory '
                             'after the initial ingestion',
                        action='store_true', default=False)
    parser.add_argument("-w", "--wait_for_event", dest="wait_for_event",
                        action="store_true", help="Wait for events")
    parser.add_argument("-W", "--continue", dest="continuous",
                        action="store_true",
                        help="Continue processing, wait for ever")
    parser.add_argument("-s", "--start_queue_manager_only",
                        dest="queue_manager_only", action="store_true",
                        help="Starts queue manager only, no processing",)

    out_args = parser.parse_args(in_args[1:])
    return out_args

def main():

    args = _parse_arguments(sys.argv)

    # Make the output directory

    framework_config_file = "../configs/framework.cfg"

    framework_logcfg = '../configs/logger.cfg'

    config_file = '../configs/qldeimos.cfg'
    ql_config = ConfigClass(config_file, default_section='QL_PARAMS')

    # Add current working directory to config info
    ql_config.cwd = os.getcwd()

    try:
        framework = Framework(PypeItPipeline, framework_config_file)
        # add this line ONLY if you are using a local logging config file
        logging.config.fileConfig(framework_logcfg)
        framework.config.params = ql_config
        framework.config.force = args.force
        framework.config.no_clobber = args.no_clobber
    except Exception as e:
        print("Failed to initialize framework, exiting ...", e)
        traceback.print_exc()
        sys.exit(1)
    framework.logger = getLogger(framework_logcfg,
                                 name="DRPF")

    framework.logger.info("Framework initialized")

    framework.start(args.queue_manager_only,
                    args.wait_for_event, args.continuous)


if __name__ == "__main__":
    main()
