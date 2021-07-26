"""
author: MBrodheim
"""

from keckdrpframework.models.arguments import Arguments
from keckdrpframework.primitives.base_primitive import BasePrimitive
from astropy.io import fits
from astropy.nddata import CCDData

import os

class IngestFile(BasePrimitive):
    """
    Takes in a filename and loads the argument with information about the frame
    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        self.logger = context.logger
    
    def _pre_condition(self):
        try:
            if os.path.basename(self.action.args.name).startswith(self.context.config.params.root):
                return True
            self.logger.error(f"File does not match DEIMOS name convention: {self.action.args.name}")
            return False
        except TypeError as e:
            self.logger.error("Failed to load filename")
            self.logger.error(e)
            return False

    def _perform(self):
            # if self.context.data_set is None:
            #    self.context.data_set = DataSet(None, self.logger, self.config,
            #    self.context.event_queue)
            # self.context.data_set.append_item(self.action.args.name)
            self.logger.info(
                "------------------- Ingesting file %s -------------------" %
                self.action.args.name)
            self.name = self.action.args.name
            out_args = Arguments()

            self.header = self._fits_header_reader(self.name)

            out_args.name = self.action.args.name
            out_args.imtype = self._get_keyword("KOAIMTYP")
            out_args.koaid = self._get_keyword("KOAID")

            return out_args
    
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