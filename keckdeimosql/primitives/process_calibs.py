from keckdrpframework.primitives.base_primitive import BasePrimitive
from pypeit.scripts import ql_keck_deimos

class process_calibs(BasePrimitive):
    """
    Calls the process_calibs function from ql_keck_deimos.py in PypeIt

    """

    def __init__(self, action, context):
        BasePrimitive.__init__(self, action, context)
        self.logger = context.pipeline_logger

    def _perform(self):
        raw_path = self.context.config.pypeit.raw_path
        redux_path = self.context.config.pypeit.redux_path
        file_root = self.context.config.pypeit.root
        det_num = self.context.config.params.det_num
        
        cmds = [raw_path, '--calibs_only',
            f'--root={file_root}', f'-d={det_num}', f'--redux_path={redux_path}']
        pargs = ql_keck_deimos.parse_args(cmds)
        # Run
        ql_keck_deimos.main(pargs)