"""
KeckDRPF pipeline for launching DEIMOS QL reduction using PypeIt

author: MBrodheim
"""

from keckdrpframework.pipelines.base_pipeline import BasePipeline
from keckdrpframework.models.processing_context import ProcessingContext


class PypeItPipeline(BasePipeline):

    name = 'DeimosQLReductionLauncher'

    event_table = {
        "new_file" :        ("ingest_file",
                             "ingest_file_started",
                             "action_planner"),
        "process_calibs":   ("pypeit_process_calibs",
                             "pypeit_process_calib_started",
                             None),
        "process_science":  ("pypeit_process_science",
                             "pypeit_process_science_started",
                             "AlertRTI"),
        "AlertRTI":         ("SendHTTP",
                             "alerting_rti",
                             None)
    }

    def __init__(self, context: ProcessingContext):
        """
        Constructor
        """
        BasePipeline.__init__(self, context)
        self.cnt = 0
        
        self.num_twiflat = 0
        self.num_bias = 0
        self.num_dark = 0
        self.num_lampflat = 0
        self.num_domeflat = 0
        self.num_arc = 0

    def action_planner(self, action, context):
        try:
            self.logger.info("******* FILE TYPE DETERMINED AS %s" %
                             action.args.imtype)
        except:
            return
        
        calibration_types = ["BIAS", "DARK", "TWIFLAT", "DOMEFLAT", "FLATLAMP",
                                "ARCLAMP"]
        
        if action.args.imtype in calibration_types:
            self._handle_calib(action, context)
        elif action.args.imtype == "OBJECT":
            self._handle_science(action, context)
        else:
            self.logger.error(f"Unexpected IMTYPE: {action.args.imtype}")
        # if the file is a calibration, send it to pypeit process calib routine
        # else, process away

    def _handle_calib(self, action, context):
        imtype = action.args.imtype

        if imtype == "BIAS":
            self.num_bias += 1
        elif imtype == "DARK":
            self.num_dark += 1
        elif imtype == "TWIFLAT":
            self.num_twiflat += 1
        elif imtype == "DOMEFLAT":
            self.num_domeflat += 1
        elif imtype == "FLATLAMP":
            self.num_lampflat += 1
        elif imtype == "ARCLAMP":
            self.num_arc += 1
        else:
            self.logger.error(f"Unexpected calib type: {imtype}")
            return
        if self._minimum_calibrations_met(context):
            self.logger.info("Minimum calibration requirements met")
            context.push_event("process_calib", None)


    def _handle_science(self, action, context):
        if not self._minimum_calibrations_met(context) and context.force == False:
            self.logger.error("Recieved science frame before minimum calibrations!")
        else:
            context.push_event("process_science", action.args)


    def _minimum_calibrations_met(self, context):
        return self.num_bias >= context.config.params.min_bias and \
                self.num_dark >= context.config.params.min_dark and \
                self.num_arc >= context.config.params.min_arc and \
                self.num_twiflat >= context.config.params.min_twi and \
                self.num_domeflat >= context.config.params.min_dome and \
                self.num_lampflat >= context.config.params.min_lamp