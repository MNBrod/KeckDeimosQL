"""
author: MBrodheim
"""

from keckdrpframework.primitives.base_primitive import BasePrimitive
from pypeit.scripts import ql_keck_deimos

class process_science(BasePrimitive):
    """
    Calls the process_science function from ql_keck_deimos.py in PypeIt
    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        self.logger = context.pipeline_logger

    def _perform(self):
        raw_path = self.context.config.cwd
        redux_path = self.context.config.redux_path
        file_name = self.action.args.name
        slit_spat = self.context.config.slit_spat

        cmds = [raw_path, f'--science={file_name}',  f'--slit_spat={slit_spat}',
            f'--redux_path={redux_path}']
        pargs = ql_keck_deimos.parse_args(cmds)
        # Run
        ql_keck_deimos.main(pargs)