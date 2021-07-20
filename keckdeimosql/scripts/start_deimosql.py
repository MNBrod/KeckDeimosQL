"""
Entry point for launching the pipeline. Handles command line input/parsing,
initializing the framework, and launching the action planner.

author: MBrodheim
"""

from keckdrpframework.core.framework import Framework
from keckdrpframework.config.framework_config import ConfigClass
from keckdrpframework.utils.drpf_logger import getLogger

from keckdeimosql.pipelines.pipeline import PypeItPipeline
import logging.config

import argparse
import sys
import traceback
import os
import pkg_resources

def _parse_arguments(in_args: list) -> argparse.Namespace:
    description = "Deimos QL Launcher"

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
    # parser.add_argument('-m', '--monitor', dest="monitor",
    #                     help='Continue monitoring the directory '
    #                          'after the initial ingestion',
    #                     action='store_true', default=False)
    # parser.add_argument("-w", "--wait_for_event", dest="wait_for_event",
    #                     action="store_true", help="Wait for events")
    # parser.add_argument("-W", "--continue", dest="continuous",
    #                     action="store_true",
    #                     help="Continue processing, wait for ever")

    out_args = parser.parse_args(in_args[1:])
    return out_args

def check_directory(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
        print("Directory %s has been created" % directory)

def main():

    args = _parse_arguments(sys.argv)

    # Make the output directory

    pkg = 'keckdeimosql'

    framework_config_file = "../configs/framework.cfg"

    framework_logcfg = 'configs/logger.cfg'
    log_file_path = pkg_resources.resource_filename(pkg, framework_logcfg)

    config_file = 'configs/qldeimos.cfg'
    config_filepath = pkg_resources.resource_filename(pkg, config_file)
    ql_config = ConfigClass(config_filepath, default_section='QL_PARAMS')

    # Add current working directory to config info
    ql_config.cwd = os.getcwd()

    try:
        framework = Framework(PypeItPipeline, framework_config_file)
        logging.config.fileConfig(log_file_path)
        framework.config.params = ql_config
        framework.config.force = args.force
        framework.config.no_clobber = args.no_clobber
    except Exception as e:
        print("Failed to initialize framework, exiting ...", e)
        traceback.print_exc()
        sys.exit(1)
    framework.logger = getLogger(framework_logcfg,
                                 name="DRPF")

    #Check if the directories exist! TODO

    framework.logger.info("Framework initialized")

    if args.dirname is not None:
        directory = args.dirname
    else:
        directory = os.getcwd()

    framework.ingest_data(directory, None, True)

    # framework.start(args.queue_manager_only,
    #                 args.wait_for_event, args.continuous)
    framework.start(qm_only=False, ingest_data_only=False, wait_for_event=True,
                        continuous=True)


if __name__ == "__main__":
    main()
