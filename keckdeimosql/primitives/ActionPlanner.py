"""
author: MBrodheim
"""

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from astropy.io import fits
from astropy.nddata import CCDData
from datetime import datetime

import os

class ActionPlanner(BasePrimitive):
    """
    Takes in a filename and loads the argument with information about the frame
    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        self.logger = context.logger
        print(self.context.config.params)
        self.minimums = {
            "arclamp": context.config.min_arc,
            "flatlamp": context.config.min_lamp,
            "bias": context.config.min_bias,
            "twiflat": context.config.min_twi,
            "dark": context.config.min_dark,
            "domeflat": context.config.min_dome
        }

    def _perform(self):
        self.action_planner(self, self.action, self.context)
        pass

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
        
        # Record the time of ingestion for RTI metrics
        action.args.ingest_time = datetime.utcnow()
        
        if action.args.imtype in self.cal_types:
            
            self._handle_calib(action, context)

        elif action.args.imtype == "object":
            
            self._handle_science(action, context)
        
        else:
        
            self.logger.error(f"Unexpected IMTYPE: {action.args.imtype}")
        
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
                context.push_event("process_calib", None)
                return

        imtype = action.args.imtype

        # Add to the appropriate calib count
        if imtype in self.cal_types:
            self.cals[imtype] += 1
        else:
            self.logger.error(f"Unexpected calib type: {imtype}")
            return



        # If there are enough calibrations, process them all
        if self._check_minimum_calibrations_met(context):
            self.minimum_calibrations_met = True
            self.logger.info("Minimum calibration requirements met")
            context.push_event("process_calib", None)
        else:
            self.logger.info("Waiting for more calibrations:\n")
            self.print_calibration_counts()


    def _handle_science(self, action, context):
        # If the calibrations have been processed, process this science file
        if not self.minimum_calibrations_met and context.config.force == False:
            self.logger.error("Recieved science frame before minimum calibrations!")
        else:
            context.push_event("process_science", action.args)


    def _check_minimum_calibrations_met(self, context):
        """
        Returns True if there are an acceptable number of calibration frames in
        this directory.
        """
        for key in self.cals.keys():
            # print(f"Key: {key}")
            # print(self.minimums)
            if self.cals[key] < self.minimums[key]:
                return False
        return True

    def print_calibration_counts(self):
        for key in self.cals.keys():
            self.logger.info(f"\t{key}: {self.cals[key]}")
    
    def _fits_header_reader(self, filename):
        try:
            hdul = fits.open(filename)
        except (FileNotFoundError, OSError) as e:
            print(e)
            raise e
        
        header = hdul[0].header
        hdul.close()
        return header
    
    def _get_keyword(self, key):
        try:
            keyval = self.header[key]
        except KeyError:
            keyval = None
        return keyval