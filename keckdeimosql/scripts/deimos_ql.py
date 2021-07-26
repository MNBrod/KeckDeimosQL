""" Run the QL tests """
import os
import argparse
from pathlib import Path
from re import L

from pypeit.scripts import ql_keck_deimos

from IPython import embed
from astropy.io import fits


def afternoon(raw_path, root, detector, redux_path):
    root = f'--root={root}'
    detector = f'-d={detector}'
    cmds = [raw_path, '--calibs_only',
            root, detector, '--redux_path={}'.format(redux_path)]
    pargs = ql_keck_deimos.parse_args(cmds)
    # Run
    ql_keck_deimos.main(pargs)

def one_slit(raw_path, frame, slit, redux_path):
    slit = f'--slit_spat={slit}'
    frame = f'--science={frame}'
    cmds = [raw_path, frame,  slit,
            '--redux_path={}'.format(redux_path)]
    pargs = ql_keck_deimos.parse_args(cmds)
    # Run
    ql_keck_deimos.main(pargs)

def get_parser():
    parser = argparse.ArgumentParser()

    parser.add_argument('-d', '--directory', dest="directory", default="./",
                        nargs=1, help='Data directory')
    parser.add_argument('-r', '--root', dest='root', default='DE.', nargs=1,
                        help='Filename root, e.g. DE. or d')
    parser.add_argument('--detector', '--det', dest='detector', default=3,
                        help='Detector number', nargs=1)
    parser.add_argument('-c', '--calibs-only', dest="calibs_only",
                        action="store_true", help='Only process calibrations')
    parser.add_argument('-o', '--output', dest='out_path', nargs=1)
    parser.add_argument('-s', '--slit', dest='slit_spat', help='science slit',
                        nargs=1)
    parser.add_argument('-l', default=0, dest='log')
    return parser

class logger():
    def __init__(self, log_level):
        self.level = log_level
    
    def print(self, str):
        if self.level > 0:
            print(str)

# Command line execution
def main():

    raw_path = os.path.join(os.getenv("PYPEIT_DEV"), 'DEIMOS_QL_TST', 'raw')
    redux_path = os.path.join(os.getenv("PYPEIT_DEV"), 'DEIMOS_QL_TST')
    
    parser = get_parser().parse_args()
    log = logger(parser.log)
    
    if 'raw_path' in parser.directory:
        parser.directory = raw_path
        log.print(f'set raw_path to {parser.directory}')

    if parser.out_path is None:
        parser.out_path = redux_path
        log.print(f'set out_path to {parser.out_path}')

    log.print(f'Parsing afternoon with: {parser.directory}, {parser.root}, {parser.detector}, {parser.out_path}')
    afternoon(parser.directory, parser.root, parser.detector, parser.out_path)

    if not parser.calibs_only:
        
        science = []
        for file in Path(parser.directory).glob('*.fits'):
            with fits.open(file) as h:
                if ['arc', 'IntFlat'] not in h.header['OBJECT']:
                    science.append(file)
        log.print(f'Found science files: {science}')
        frame = science[0]
        log.print(f'Using {frame}')
        if parser.slit_spat is None:
            masters_dir = Path(parser.out_path) / 'keck_deimos_A' / 'Masters'
            master_slit = list(masters_dir.glob('MasterSlits'))[0]
            log.print(f'Using slit file {master_slit}')

            with fits.open(master_slit) as h:
                parser.slit_spat = f"{parser.detector}:{h['SLITS'].data[0][0]}"
            log.print(f'slit spat id is {parser.slit_spat}')
        
        log.print(f'running one_slit with {parser.directory}, {frame}, {parser.slit_spat}, {parser.out_path}')
        one_slit(parser.directory, frame, parser.slit_spat, parser.out_path)

        if __name__ == '__main__:
            main()
