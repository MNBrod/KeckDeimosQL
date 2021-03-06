"""
author: MBrodheim
"""

from keckdrpframework.primitives.base_primitive import BasePrimitive
from pypeit.scripts import ql_keck_deimos

class ProcessScience(BasePrimitive):
    """
    Calls the process_science function from ql_keck_deimos.py in PypeIt
    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        self.logger = context.logger

    def _perform(self):
        raw_path = self.context.config.params.cwd
        redux_path = self.context.config.params.redux_path
        file_name = self.action.args.name
        slit_spat = self.context.config.params.slit_spat

        cmds = [raw_path, f'--science={file_name}',  f'--slit_spat={slit_spat}',
            f'--redux_path={redux_path}']
        pargs = ql_keck_deimos.parse_args(cmds)
        # Run
        try:
            ql_keck_deimos.main(pargs)
            return True
        except Exception as e:
            self.logger.error("Exception while trying to process science:")
            self.logger.error(e)
            return False