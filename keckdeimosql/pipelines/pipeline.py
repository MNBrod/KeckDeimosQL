"""
KeckDRPF pipeline for launching DEIMOS QL reduction using PypeIt

author: MBrodheim
"""

from keckdrpframework.pipelines.base_pipeline import BasePipeline
from keckdrpframework.models.processing_context import ProcessingContext

from datetime import datetime

class PypeItPipeline(BasePipeline):
    """
    Defines the flow of the program.

    The pipeline ingests files as they appear, and filters them based on 
    whether they are calibration files, or science files. If a calibration is
    ingested, it is counted against the prescribed minimum number of frames. If
    the minimum threshold is met, the pipeline calls PypeIt's process_calib 
    routine from ql_keck_deimos.py.

    If a science frame is ingested, the pipeline first checks if there are
    enough calibrations (--force overrides this behavior) and then calls the 
    quicklook science reduction step from PypeIt.
    """

    name = 'KeckDeimosQL'

    event_table = {
        "next_file" :        ("IngestFile",
                             "ingest_file_started",
                             "planner"),
        "planner":           ("action_planner",
                              "planning",
                              None),
        "process_calibs":   ("ProcessCalibs",
                             "process_calib_started",
                             None),
        "process_science":  ("ProcessScience",
                             "pypeit_process_science_started",
                             "AlertRTI"),
        "AlertRTI":         ("SendHTTP",
                             "alerting_rti",
                             None)
    }

    # List of all the types of calibrations we will encounter
    cal_types = [
        "flatlamp",
        "arclamp"
    ]

    def __init__(self, context: ProcessingContext):
        """
        Constructor
        """
        BasePipeline.__init__(self, context)
        self.cnt = 0
        
        # Stores the number of each calibration file that have been ingested
        self.cals = {}
        for cal_type in self.cal_types:
            self.cals[cal_type] = 0
        self.minimums = None

        self.minimum_calibrations_met = False

    def set_min_cals(self, context):
        self.minimums = {
            "arclamp": context.config.params.min_arc,
            "flatlamp": context.config.params.min_lamp,
            "bias": context.config.params.min_bias,
            "twiflat": context.config.params.min_twi,
            "dark": context.config.params.min_dark,
            "domeflat": context.config.params.min_dome
        }

    def action_planner(self, action, context):
        """
        Decides what to do with each ingested file
        """
        # If we can't figure out what the frame type is, we're in trouble
        try:
            self.logger.info("******* FILE TYPE DETERMINED AS %s" %
                             action.args.imtype)
        except:
            return
        
        if self.minimums is None:
            self.set_min_cals(context)

        # Record the time of ingestion for RTI metrics
        action.args.ingest_time = datetime.utcnow()
        
        if action.args.imtype in self.cal_types:
            
            return self._handle_calib(action, context)

        elif action.args.imtype == "object":
            
            return self._handle_science(action, context)
        
        else:
        
            self.logger.error(f"Unexpected IMTYPE: {action.args.imtype}")
        
            return True
        
    def _handle_calib(self, action, context):

        # If minimum_calibrations_met is True, that means that process_calib has
        # already been called. In that case, we should only continue if the user
        # is okay with the existing pypeit files being overwritten
        if self.minimum_calibrations_met:
            self.logger.info("Calibration beyond the min requirement ingested")
            if context.config.no_clobber:
                self.logger.info("--no-clobber set to true. Ignoring calib")
                return
            else:
                context.push_event("process_calibs", None)
                return True

        imtype = action.args.imtype

        # Add to the appropriate calib count
        if imtype in self.cal_types:
            self.cals[imtype] += 1
        else:
            self.logger.error(f"Unexpected calib type: {imtype}")
            return False



        # If there are enough calibrations, process them all
        if self._check_minimum_calibrations_met(context):
            self.minimum_calibrations_met = True
            self.logger.info("Minimum calibration requirements met")
            context.push_event("process_calibs", None)
            return True
        else:
            self.logger.info("Waiting for more calibrations:\n")
            self.print_calibration_counts()
            return False


    def _handle_science(self, action, context):
        # If the calibrations have been processed, process this science file
        if not self.minimum_calibrations_met and context.config.force == False:
            self.logger.error("Recieved science frame before minimum calibrations!")
            return False
        else:
            context.push_event("process_science", action.args)
            return True


    def _check_minimum_calibrations_met(self, context):
        """
        Returns True if there are an acceptable number of calibration frames in
        this directory.
        """
        for key in self.cals.keys():
            if self.cals[key] < self.minimums[key]:
                return False
        return True

    def print_calibration_counts(self):
        for key in self.cals.keys():
            self.logger.info(f"\t{key}: {self.cals[key]}")